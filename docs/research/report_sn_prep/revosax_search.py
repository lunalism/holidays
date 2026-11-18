# ruff: noqa
"""REVOSax 의 빠른 검색(quicksearch, sachsen.de 첫 화면의 GET 폼과 같은 주소)을 렌더하고, 결과 목록의
「nächste」 를 끝까지 눌러 모든 적중을 적는다.

사용: uv run python revosax_search.py <검색어> <out-prefix> <fetch.log>
  <out-prefix>.tsv      적중마다: 쪽, 순번, 문서 링크, 링크 글자, 본문 줄(정식 제목·관보·유형·Erlassdatum·Fassung gültig ab)
  <out-prefix>.net.tsv  요청 전부(시각, 메서드, URL, 상태)
fetch.log 에는 검색 URL 한 줄만 더한다(쪽 수를 #pages= 로 붙인다). 쪽 넘김은 브라우저가 같은 세션에서 낸다.
화면의 숨은 필드 search_request[valid_day](오늘 날짜)가 보이듯, 이 검색은 그날 유효한 문서를 본다 — 효력이 끝난
문서가 드는지는 이 스크립트로 알 수 없다(보고에 적는다).
"""
import datetime as dt
import sys
import urllib.parse

from playwright.sync_api import sync_playwright

UA = "holidays.lunalism.com research (contact: repo issues)"
query, prefix, log = sys.argv[1:4]
url = "https://revosax.sachsen.de/quicksearch?" + urllib.parse.urlencode({"text": query})
rows, net = [], []


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(user_agent=UA)
    page.on("response", lambda r: net.append((now(), r.request.method, r.url, r.status)))
    t0 = now()
    resp = page.goto(url, wait_until="networkidle", timeout=90000)
    status = resp.status if resp else ""
    pages = 0
    while True:
        pages += 1
        hits = page.eval_on_selector_all(
            ".result_hit",
            """els => els.map(e => {
                const a = e.querySelector('p a');
                const ps = e.querySelectorAll(':scope > p');
                return [a ? a.getAttribute('href') : '', a ? a.innerText.trim() : '',
                        ps.length > 1 ? ps[1].innerText.replace(/\\s*\\n\\s*/g, ' | ').trim() : ''];
            })""",
        )
        for n, (href, text, body) in enumerate(hits, 1):
            rows.append((pages, n, href, text, body))
        nxt = page.locator("a", has_text="nächste").first
        if pages >= 40 or nxt.count() == 0 or not nxt.is_visible():
            break
        before = page.url
        nxt.click()
        page.wait_for_load_state("networkidle", timeout=90000)
        page.wait_for_timeout(3000)
        if page.url == before:
            break
    browser.close()

with open(prefix + ".tsv", "w", encoding="utf-8") as f:
    f.write("page\tn\thref\tlink_text\tbody\n")
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
with open(prefix + ".net.tsv", "w", encoding="utf-8") as f:
    f.write("time\tmethod\turl\tstatus\n")
    for r in net:
        f.write("\t".join(map(str, r)) + "\n")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{t0}\t{url}#pages={pages}\t{status}\ttext/html\t{len(rows)}\t{url}\n")
print(f"{t0}\tq={query!r}\tpages={pages}\thits={len(rows)}")
