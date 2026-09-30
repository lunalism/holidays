"""F — headless Chromium 에서 body 의 <noscript>(피드 목록) 가 어떻게 서는지 본다.

JS 켬: noscript 요소의 childElementCount·textContent 길이·첫 80 자, 스크립트가 세운 행 수.
JS 끔: 문서 전체 .feed-row 수, noscript 안 .feed-row 수, #feed-groups 안 행 수.
대상은 인자 디렉터리(발행 배치 그대로: index.html, en/, ja/, status.json)를 http 로 서빙한 것.
사용: uv run python noscript_dom.py <site_dir>
"""
import functools
import http.server
import sys
import threading

from playwright.sync_api import sync_playwright

site = sys.argv[1]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=site)
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{httpd.server_address[1]}/"

PROBE = """() => {
  const ns = [...document.querySelectorAll('noscript')];
  const list = ns.find(n => n.closest('section')) || null;
  return {
    noscript_total: ns.length,
    list_childElementCount: list ? list.childElementCount : null,
    list_textContent_len: list ? list.textContent.length : null,
    list_textContent_head: list ? list.textContent.trim().slice(0, 80) : null,
    list_innerHTML_len: list ? list.innerHTML.length : null,
    rows_all: document.querySelectorAll('.feed-row').length,
    rows_in_noscript: list ? list.querySelectorAll('.feed-row').length : null,
    rows_script: document.querySelectorAll('#feed-groups .feed-row').length,
    details_in_noscript: list ? list.querySelectorAll('details').length : null,
  };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for js in (True, False):
        ctx = b.new_context(java_script_enabled=js)
        page = ctx.new_page()
        for path in ("", "en/", "ja/"):
            page.goto(base + path, wait_until="load")
            print(f"js={js}\t/{path}\t{page.evaluate(PROBE)}")
        ctx.close()
    print("chromium", b.version)
    b.close()
httpd.shutdown()
