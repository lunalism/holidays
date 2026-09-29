# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import re, html, sys
from playwright.sync_api import sync_playwright
S = sys.argv[1]
tmpl = open(f"{S}/browse.html", encoding="utf-8", errors="replace").read()
link = html.unescape(re.findall(r'href="(browse\.tt\.html\?type=generic1&(?:amp;)?action=link[^"]*gesetzentwurf[^"]*)"', tmpl)[0])
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(user_agent='holidays-lunalism-research/1.0 (+https://holidays.lunalism.com/; one-off gazette survey, low rate)')
    pg.goto("https://pardok.parlament-berlin.de/portala/" + link, timeout=90000); pg.wait_for_timeout(12000)
    try: pg.select_option("#efxDisplayFormat", label="Vollanzeige"); pg.wait_for_timeout(8000)
    except Exception as e: print("fmt", e)
    sel = pg.query_selector_all("select")
    done = False
    for s_ in sel:
        opts = s_.eval_on_selector_all("option", "os => os.map(o => o.textContent.trim())")
        if "Alle auf einer Seite" in opts:
            s_.select_option(label="Alle auf einer Seite"); pg.wait_for_timeout(25000); done = True; break
    print("all-on-one-page:", done)
    txt = pg.inner_text("body"); open(f"{S}/pw_adopted_full.txt", "w").write(txt)
    b.close()
t = open(f"{S}/pw_adopted_full.txt").read()
m = re.search(r"Treffer: (\d+) bis (\d+) von (\d+)", t); print("range", m.groups() if m else None)
print("Drucksache entries:", len(re.findall(r"Drucksache 19/\d+ vom", t)))
for mm in re.finditer(r"(?i)feiertag|sonn- und", t):
    print("…", re.sub(r"\s+", " ", t[max(0, mm.start()-300):mm.start()+200]))
