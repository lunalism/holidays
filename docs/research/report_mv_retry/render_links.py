# ruff: noqa
"""land-mv.de(관보 사이트가 옮겨 간 곳)의 화면 하나를 렌더하고 링크를 모은다. 선택적으로 사이트 검색어를 넣는다.

사용: uv run python render_links.py <url> <out-prefix> <fetch.log> [<검색어>]
  <out-prefix>.txt        body innerText
  <out-prefix>.links.tsv  렌더 뒤 a[href] 전부(href, 글자)
  <out-prefix>.net.tsv    요청 전부(시각, 메서드, URL, 상태, content-type)
검색어를 주면 화면의 첫 search 입력(input[type=search] 또는 name/placeholder 에 'such')에 넣고 Enter 를 누른다.
fetch.log 에는 사람이 여는 URL 한 줄(검색어가 있으면 '#q=<검색어>')만 fetch.sh 형식으로 더한다.
URL 을 만들지 않는다 — 화면의 링크를 따라갈 때만 이 스크립트에 그 href 를 준다.
"""
import datetime as dt
import sys

from playwright.sync_api import sync_playwright

UA = "holidays.lunalism.com research (contact: repo issues)"
url, prefix, log = sys.argv[1:4]
query = sys.argv[4] if len(sys.argv) > 4 else None
rows, order = {}, []


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
    status = resp.status if resp else ""
    ctype = resp.headers.get("content-type", "") if resp else ""
    if query:
        box = page.locator(
            "input[type=search], input[name*=such i], input[placeholder*=such i], input[aria-label*=such i]"
        ).first
        box.fill(query)
        box.press("Enter")
        page.wait_for_load_state("networkidle", timeout=90000)
    page.wait_for_timeout(3000)
    html = page.content()
    text = page.inner_text("body")
    links = page.eval_on_selector_all(
        "a[href]", "els => els.map(e => [e.href, (e.innerText || e.getAttribute('aria-label') || '').trim()])"
    )
    final = page.url
    browser.close()

open(prefix + ".html", "w", encoding="utf-8").write(html)
open(prefix + ".txt", "w", encoding="utf-8").write(text)
with open(prefix + ".links.tsv", "w", encoding="utf-8") as f:
    f.write("href\ttext\n")
    for href, t in links:
        f.write(f"{href}\t{' '.join(t.split())}\n")
with open(prefix + ".net.tsv", "w", encoding="utf-8") as f:
    f.write("time\tmethod\turl\tstatus\tcontent_type\n")
    for k in order:
        f.write("\t".join(map(str, rows[k])) + "\n")
shown = url + (f"#q={query}" if query else "")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{t0}\t{shown}\t{status}\t{ctype}\t{len(html.encode('utf-8'))}\t{final}\n")
print(f"{t0}\t{shown}\t{status}\tlinks={len(links)}\tfinal={final}")
