# ruff: noqa
"""report_mv_retry/render_doc.py 와 같은 렌더에, 문서 탭 하나(기본 「Aktuelle Gesamtausgabe」)를 누르는 단계를 더했다.

사용: uv run python render_tab.py <url> <out-prefix> <fetch.log> [<탭 글자>]
  <out-prefix>.html      렌더된 DOM(page.content()) — 사이트 응답 덤프라 scratch 에만 둔다
  <out-prefix>.txt       body 의 innerText
  <out-prefix>.net.tsv   이 렌더 동안 브라우저가 낸 요청 전부: 시각, 메서드, URL, 상태(응답 없으면 FAILED:<사유>), content-type
fetch.log 에는 사람이 여는 문서 URL 한 줄만 fetch.sh 형식으로 더한다(시각, URL, 상태, content-type,
바이트(렌더 HTML 의 UTF-8 바이트), 최종 URL). 하위 요청은 브라우저가 스스로 내므로 3 초 간격을 줄 수 없다.
"""
import datetime as dt
import sys

from playwright.sync_api import sync_playwright

UA = "holidays.lunalism.com research (contact: repo issues)"
url, prefix, log = sys.argv[1:4]
tab = sys.argv[4] if len(sys.argv) > 4 else "Aktuelle Gesamtausgabe"
rows = {}
order = []


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def on_request(r):
    rows[id(r)] = [now(), r.method, r.url, "", ""]
    order.append(id(r))


def on_response(resp):
    row = rows.get(id(resp.request))
    if row is not None:
        row[3] = resp.status
        row[4] = resp.headers.get("content-type", "")


def on_failed(r):
    row = rows.get(id(r))
    if row is not None:
        row[3] = f"FAILED:{r.failure}"


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(user_agent=UA)
    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_failed)
    t0 = now()
    resp = page.goto(url, wait_until="networkidle", timeout=90000)
    try:
        page.wait_for_function(
            "document.body && /Feiertag|fehlgeschlagen/.test(document.body.innerText)", timeout=60000
        )
    except Exception as e:  # 본문도 오류 문구도 끝내 안 오면 그대로 기록한다
        print("wait_for_function:", type(e).__name__)
    page.wait_for_timeout(3000)
    page.get_by_text(tab, exact=True).first.click()
    try:
        page.wait_for_function("document.body && document.body.innerText.includes('§ 12')", timeout=60000)
    except Exception as e:  # 탭 본문이 끝내 안 오면 그대로 기록한다
        print("wait_for_function(tab):", type(e).__name__)
    page.wait_for_load_state("networkidle", timeout=90000)
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
    f.write("time\tmethod\turl\tstatus\tcontent_type\n")
    for k in order:
        f.write("\t".join(map(str, rows[k])) + "\n")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{t0}\t{url}#tab={tab}\t{status}\t{ctype}\t{len(html.encode('utf-8'))}\t{final}\n")
print(f"{t0}\t{url}\t{status}\t{len(html)}\trequests={len(order)}\ttext_chars={len(text)}")
