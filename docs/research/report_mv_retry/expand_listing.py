# ruff: noqa
"""land-mv.de 의 「Gesetz- und Verordnungsblätter」 화면을 렌더하고 「Mehr anzeigen」 을 더 없을 때까지 누른 뒤
PDF 링크를 모은다(Part C 의 코퍼스 완결성 — 이 화면이 담는 호 번호).

사용: uv run python expand_listing.py <url> <out-prefix> <fetch.log>
  <out-prefix>.txt        펼친 뒤 body innerText
  <out-prefix>.pdfs.tsv   PDF 링크 전부(href, 링크 글자)
  <out-prefix>.net.tsv    요청 전부
fetch.log 에는 화면 URL 한 줄만 더한다(#expand 표시). 「Mehr anzeigen」 은 최대 30 번 누른다.
"""
import datetime as dt
import sys

from playwright.sync_api import sync_playwright

UA = "holidays.lunalism.com research (contact: repo issues)"
url, prefix, log = sys.argv[1:4]
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


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(user_agent=UA)
    page.on("request", on_request)
    page.on("response", on_response)
    t0 = now()
    resp = page.goto(url, wait_until="networkidle", timeout=90000)
    status = resp.status if resp else ""
    ctype = resp.headers.get("content-type", "") if resp else ""
    clicks = 0
    for _ in range(30):
        more = page.get_by_text("Mehr anzeigen", exact=True)
        if more.count() == 0 or not more.first.is_visible():
            break
        more.first.click()
        clicks += 1
        page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle", timeout=90000)
    html = page.content()
    text = page.inner_text("body")
    pdfs = page.eval_on_selector_all(
        "a[href*='.pdf' i]", "els => els.map(e => [e.href, (e.innerText || '').trim()])"
    )
    browser.close()

open(prefix + ".html", "w", encoding="utf-8").write(html)
open(prefix + ".txt", "w", encoding="utf-8").write(text)
with open(prefix + ".pdfs.tsv", "w", encoding="utf-8") as f:
    f.write("href\ttext\n")
    for href, t in pdfs:
        f.write(f"{href}\t{' '.join(t.split())}\n")
with open(prefix + ".net.tsv", "w", encoding="utf-8") as f:
    f.write("time\tmethod\turl\tstatus\tcontent_type\n")
    for k in order:
        f.write("\t".join(map(str, rows[k])) + "\n")
with open(log, "a", encoding="utf-8") as f:
    f.write(f"{t0}\t{url}#expand\t{status}\t{ctype}\t{len(html.encode('utf-8'))}\t{url}\n")
print(f"{t0}\tclicks={clicks}\tpdfs={len(pdfs)}")
