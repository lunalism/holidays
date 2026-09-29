# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import re, sys
from playwright.sync_api import sync_playwright
S = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(user_agent='holidays-lunalism-research/1.0 (+https://holidays.lunalism.com/; one-off gazette survey, low rate)')
    pg.goto("https://pardok.parlament-berlin.de/portala/browse.tt.html?type=generic1", timeout=90000); pg.wait_for_timeout(6000)
    pg.fill("[name='searchgeneric1-text']", "Feiertag"); pg.select_option("[name='searchgeneric1-wp']", "19")
    pg.press("[name='searchgeneric1-text']", "Enter"); pg.wait_for_timeout(12000)
    pg.select_option("#efxDisplayFormat", label="Vollanzeige"); pg.wait_for_timeout(8000)
    for s_ in pg.query_selector_all("select"):
        if "Alle auf einer Seite" in s_.eval_on_selector_all("option", "os => os.map(o => o.textContent.trim())"):
            s_.select_option(label="Alle auf einer Seite"); pg.wait_for_timeout(25000); break
    open(f"{S}/pw_feiertag_full.txt", "w").write(pg.inner_text("body")); b.close()
t = open(f"{S}/pw_feiertag_full.txt").read()
print(re.search(r"Treffer: \d+ bis \d+ von \d+", t).group(0))
entries = re.split(r"\nDetails\nAuswählen\n", t)
for e in entries:
    if re.search(r"Gesetzentwurf", e):
        title = [l for l in e.strip().split("\n") if l.strip()][-6:]
        status = re.findall(r"(Angenommen|Abgelehnt|Zurückgezogen|Erledigt|Beratung ist \(noch\) nicht erfolgt|Gesetz vom \d{2}\.\d{2}\.\d{4})", e)
        dr = re.findall(r"Drucksache 19/\d+ vom \d{2}\.\d{2}\.\d{4}", e)
        print("*", dr[:1], sorted(set(status)), "|", re.sub(r"\s+"," ", e)[:160])
