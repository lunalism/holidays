# ruff: noqa
"""옵션 2 의 전제 확인 — 구현이 아니다. JS 켠 페이지에서 noscript 의 textContent 를
DOMParser·<template> 로 다시 파싱하면 행·그룹·아코디언이 몇 개 서는지만 센다."""
import functools, http.server, sys, threading
from playwright.sync_api import sync_playwright
site = sys.argv[1]
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=site)
s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
threading.Thread(target=s.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{s.server_address[1]}/"
PROBE = """() => {
  const ns = [...document.querySelectorAll('noscript')].find(n => n.closest('section'));
  const doc = new DOMParser().parseFromString(ns.textContent, 'text/html');
  const t = document.createElement('template'); t.innerHTML = ns.textContent;
  const f = t.content;
  const fields = [...doc.querySelectorAll('.feed-row')].map(r => ({
    label: r.querySelector('.feed-label').textContent,
    url: r.querySelector('code.url').textContent,
  }));
  return {
    domparser_rows: doc.querySelectorAll('.feed-row').length,
    domparser_groups: doc.querySelectorAll('.feed-group').length,
    domparser_accordion_rows: doc.querySelectorAll('details .feed-row').length,
    template_rows: f.querySelectorAll('.feed-row').length,
    first: fields[0], last: fields[fields.length - 1],
  };
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for path in ("", "en/", "ja/"):
        pg.goto(base + path, wait_until="load"); print(f"/{path}\t{pg.evaluate(PROBE)}")
    b.close()
s.shutdown()
