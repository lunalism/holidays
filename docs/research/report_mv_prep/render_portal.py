# ruff: noqa
"""landesrecht-mv.de 의 FTG M-V 문서를 헤드리스 chromium 으로 한 번 렌더한다.

사용: uv run python render_portal.py <url> <out-prefix> <fetch.log>
  <out-prefix>.html      렌더된 DOM(page.content())
  <out-prefix>.txt       body 의 innerText
  <out-prefix>.net.tsv   이 렌더 동안 브라우저가 받은 모든 응답(시각, URL, 상태, content-type)
fetch.log 에는 사용자가 보는 문서 URL 한 줄만 fetch.sh 형식으로 더한다(시각, URL, 상태, content-type,
바이트(렌더 HTML 의 UTF-8 바이트), 최종 URL). 하위 요청은 브라우저가 스스로 내므로 3 초 간격을 줄 수 없다 —
.net.tsv 에 전부 적는다.
"""
import datetime as dt
import sys

from playwright.sync_api import sync_playwright

UA = "holidays.lunalism.com research (contact: repo issues)"
url, prefix, log = sys.argv[1:4]
net = []


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(user_agent=UA)
    page.on("response", lambda r: net.append((now(), r.url, r.status, r.headers.get("content-type", ""))))
    t0 = now()
    resp = page.goto(url, wait_until="networkidle", timeout=90000)
    try:
        page.wait_for_function("document.body && document.body.innerText.includes('Feiertag')", timeout=60000)
    except Exception as e:  # 본문이 끝내 안 오면 그대로 기록한다
        print("wait_for_function:", type(e).__name__)
    page.wait_for_timeout(3000)
    html = page.content()
    text = page.inner_text("body")
    final = page.url
    status = resp.status if resp else ""
    ctype = resp.headers.get("content-type", "") if resp else ""
    browser.close()

open(prefix + ".html", "w", encoding="utf-8").write(html)
open(prefix + ".txt", "w", encoding="utf-8").write(text)
with open(prefix + ".net.tsv", "w", encoding="utf-8") as f:
    f.write("time\turl\tstatus\tcontent_type\n")
    for row in net:
        f.write("\t".join(map(str, row)) + "\n")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{t0}\t{url}\t{status}\t{ctype}\t{len(html.encode('utf-8'))}\t{final}\n")
print(f"{t0}\t{url}\t{status}\t{len(html)}\tresponses={len(net)}\ttext_chars={len(text)}")
