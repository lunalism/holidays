"""bgbl.de 링크 두 형태 — 쿠키 없는 새 컨텍스트에서 문서가 뜨는지(pdf.js 상태로 판정).

사용: uv run python bgbl_final_check.py   (레포 dev 의존성 playwright 사용, 헤드리스 Chromium)
"""

import urllib.parse

from playwright.sync_api import sync_playwright

URLS = {
    "[1] jumpTo": "https://www.bgbl.de/xaver/bgbl/start.xav?startbk=Bundesanzeiger_BGBl&jumpTo=bgbl290s0885.pdf",
    "[2] start=attr_id": "https://www.bgbl.de/xaver/bgbl/start.xav?start=%2F%2F*%5B%40attr_id%3D%27bgbl290s0885.pdf%27%5D",
}
BREADCRUMB_SELECTOR = "#pathContainer a, .xaverPath a, [class*=ath] a"
LINK_DIALOG_INPUTS = "#bgblLinkadresse input, #bgblLinkadresse textarea"


def check(browser, label, url):
    ctx = browser.new_context()
    page = ctx.new_page()
    errs = []
    page.on("console", lambda m: errs.append(m.text[:200]) if m.type == "error" else None)
    page.on("pageerror", lambda e: errs.append("pageerror " + str(e)[:200]))
    page.goto(url, wait_until="load", timeout=60000)
    page.wait_for_selector("iframe[src*='pdfjs']", timeout=45000)
    # 뷰어 iframe 은 한 번 교체된다 — 식별자가 든 것이 뜰 때까지 기다린다.
    for _ in range(60):
        if any("pdfjs" in f.url and "bgbl290s0885" in f.url for f in page.frames):
            break
        page.wait_for_timeout(1000)
    page.wait_for_timeout(2000)
    viewer = [f for f in page.frames if "pdfjs" in f.url][-1]
    viewer.wait_for_function(
        "() => window.PDFViewerApplication && window.PDFViewerApplication.pdfDocument",
        timeout=90000,
    )
    state = viewer.evaluate(
        "() => ({pagesCount: PDFViewerApplication.pagesCount, url: PDFViewerApplication.url})"
    )
    crumbs = page.evaluate(
        f"() => [...document.querySelectorAll('{BREADCRUMB_SELECTOR}')]"
        ".map(a=>a.innerText.trim()).filter(Boolean)"
    )
    page.locator("[title='Linkadresse anzeigen']").first.click(timeout=5000)
    page.wait_for_timeout(1500)
    link = page.evaluate(
        f"() => [...document.querySelectorAll('{LINK_DIALOG_INPUTS}')].map(i=>i.value)"
    )
    viewer_url = urllib.parse.unquote(state["url"])
    print(f"=== {label}\n    {url}")
    print("    pdf.js pagesCount:", state["pagesCount"])
    print(
        "    pdf.js url 에 bgbl290s0885.pdf 포함:",
        "bgbl290s0885.pdf" in viewer_url,
        "| 파일명:",
        viewer_url.split("media.xav/")[1].split("?")[0],
    )
    print("    경로 표시:", crumbs)
    print("    'Linkadresse anzeigen' 이 내는 값:", link)
    print("    console errors:", errs)
    ctx.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for label, url in URLS.items():
            check(browser, label, url)
        browser.close()


if __name__ == "__main__":
    main()
