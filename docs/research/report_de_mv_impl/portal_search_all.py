# ruff: noqa
"""report_mv_retry/portal_search.py 와 같은 검색에 두 단계를 더했다: (선택) 분류 하나로 좁히기, 그리고 결과
목록의 「다음 쪽」 을 끝까지(최대 MAX_PAGES 쪽) 넘기기. 브라우저가 받은 RESULT_LIST 응답이 쪽마다 쌓인다.

사용: uv run python portal_search_all.py <query> <out-prefix> <fetch.log> [<분류 id, 예: Gesetze_Verordnungen>]
  <out-prefix>.txt          검색 뒤 body innerText
  <out-prefix>.links.tsv    결과 화면의 /document/ 링크(문서 id, 링크 글자)
  <out-prefix>.search.json  브라우저가 받은 recherche3/search 응답 본문 전부(JSON 배열) — scratch 에만
  <out-prefix>.net.tsv      요청 전부(시각, 메서드, URL, 상태, content-type)
fetch.log 에는 「시작 화면 URL #q=<검색어>」 한 줄을 fetch.sh 형식으로 더한다(바이트는 검색 뒤 렌더 HTML).
"""
import datetime as dt
import json
import re
import sys

from playwright.sync_api import sync_playwright

UA = "holidays.lunalism.com research (contact: repo issues)"
START = "https://www.landesrecht-mv.de/bsmv/"
query, prefix, log = sys.argv[1:4]
category = sys.argv[4] if len(sys.argv) > 4 else None
MAX_PAGES = 20
pages = 1
rows, order, bodies = {}, [], []


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
    if resp.url.endswith("/recherche3/search"):
        try:
            bodies.append({"status": resp.status, "request": resp.request.post_data, "body": resp.json()})
        except Exception as e:
            bodies.append({"status": resp.status, "error": repr(e)})


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
    resp = page.goto(START, wait_until="networkidle", timeout=90000)
    status = resp.status if resp else ""
    ctype = resp.headers.get("content-type", "") if resp else ""
    n_before = len(bodies)
    editor = page.locator('[data-testid="ID_FAST_SEARCH_BAR_EDITOR"]')
    editor.click()
    page.keyboard.type(query, delay=40)
    page.wait_for_timeout(800)
    page.keyboard.press("Escape")  # 자동 완성 목록을 닫는다
    page.locator("#ID_FAST_SEARCH_BAR_SEARCH_BUTTON").click()
    page.wait_for_load_state("networkidle", timeout=90000)
    page.wait_for_timeout(4000)
    if category:
        page.locator(f"#categories_select_{category}").click()
        page.wait_for_load_state("networkidle", timeout=90000)
        page.wait_for_timeout(4000)
    while pages < MAX_PAGES:
        nxt = page.locator("a.pager__to-page--next")
        if nxt.count() == 0 or not nxt.first.is_visible():
            break
        nxt.first.click()
        pages += 1
        page.wait_for_load_state("networkidle", timeout=90000)
        page.wait_for_timeout(3000)
    html = page.content()
    text = page.inner_text("body")
    links = page.eval_on_selector_all(
        "a[href*='/document/']", "els => els.map(e => [e.getAttribute('href'), e.innerText.trim()])"
    )
    final = page.url
    browser.close()

open(prefix + ".txt", "w", encoding="utf-8").write(text)
open(prefix + ".html", "w", encoding="utf-8").write(html)
json.dump(bodies, open(prefix + ".search.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(prefix + ".links.tsv", "w", encoding="utf-8") as f:
    f.write("doc_id\thref\tlink_text\n")
    for href, t in links:
        m = re.search(r"/document/([^/?#]+)", href or "")
        f.write(f"{m.group(1) if m else ''}\t{href}\t{' '.join(t.split())}\n")
with open(prefix + ".net.tsv", "w", encoding="utf-8") as f:
    f.write("time\tmethod\turl\tstatus\tcontent_type\n")
    for k in order:
        f.write("\t".join(map(str, rows[k])) + "\n")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{t0}\t{START}#q={query}{f'&category={category}' if category else ''}&pages={pages}\t{status}\t{ctype}\t{len(html.encode('utf-8'))}\t{final}\n")
print(f"{t0}\tq={query!r}\tcategory={category}\tpages={pages}\tsearch_responses={len(bodies) - n_before}/{len(bodies)}\tlinks={len(links)}\tfinal={final}")
