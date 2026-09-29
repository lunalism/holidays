# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import re, sys
from playwright.sync_api import sync_playwright
S = sys.argv[1]; terms = sys.argv[2:]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(user_agent='holidays-lunalism-research/1.0 (+https://holidays.lunalism.com/; one-off gazette survey, low rate)')
    for n, term in enumerate(terms):
        pg.goto("https://pardok.parlament-berlin.de/portala/browse.tt.html?type=generic1", timeout=90000); pg.wait_for_timeout(6000)
        pg.fill("[name='searchgeneric1-text']", term)
        try: pg.select_option("[name='searchgeneric1-wp']", "19")
        except Exception as e: print("wp select:", e)
        pg.press("[name='searchgeneric1-text']", "Enter"); pg.wait_for_timeout(12000)
        txt = pg.inner_text("body")
        parsed = pg.eval_on_selector("[name='searchgeneric1-parsed']", "e => e.value") if pg.query_selector("[name='searchgeneric1-parsed']") else None
        open(f"{S}/pw_form{n}.txt", "w").write(f"TERM: {term}\nURL: {pg.url}\nPARSED: {parsed}\n\n" + txt)
        m = re.search(r"Treffer: \d+ bis \d+ von (\d+)", txt)
        print(f"f{n} | {term} | hits: {m.group(1) if m else ('0' if 'keine Treffer' in txt else '?')} | parsed: {parsed}")
    b.close()
