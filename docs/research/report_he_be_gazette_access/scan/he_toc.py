# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import fitz, subprocess, os, re, sys, urllib.request, time
cands = []
for spec in sys.argv[1:]:
    y, a, b = spec.split(":"); cands += [(y, n) for n in range(int(a), int(b)+1)]
for y, n in cands:
    f = f"he/chain/{y}-{n:05d}.pdf"
    if not os.path.exists(f):
        time.sleep(0.5)
        try: urllib.request.urlretrieve(f"https://starweb.hessen.de/cache/GVBL/{y}/{n:05d}.pdf", f)
        except Exception as e: print(y, n, "FAIL", e); continue
    d = fitz.open(f); p = d[0]
    t = p.get_text()
    if len(t) < 100:
        r = p.rect; p.get_pixmap(clip=fitz.Rect(0, 0, r.width, r.height*0.6), dpi=200).save("tmp.png")
        t = subprocess.run(["./ocrbin", "tmp.png"], capture_output=True, text=True).stdout
    date = re.search(r"Ausgegeben zu Wiesbaden am ([^\n|]+)", t)
    pages = re.findall(r"\b(\d{2,4})\b", t[:300])[:3]
    hit = [t[max(0, m.start()-120):m.start()+160].replace("\n", " ") for m in re.finditer(r"(?i)feier\s*-?\s*tag", t)]
    print(y, n, d.page_count, date.group(1).strip() if date else "?", pages, "| HIT: " + " || ".join(hit) if hit else "")
