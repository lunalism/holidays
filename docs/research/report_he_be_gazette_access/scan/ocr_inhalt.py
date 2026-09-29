# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import fitz, glob, subprocess, os, re
out = open("he/inhalt_ocr.tsv", "a")
done = {l.split("\t")[0] for l in open("he/inhalt_ocr.tsv")} if os.path.exists("he/inhalt_ocr.tsv") else set()
for f in sorted(glob.glob("he/inhalt/*.pdf")):
    y = os.path.basename(f)[:4]
    d = fitz.open(f)
    for i, p in enumerate(d):
        key = f"{y}:{i+1}"
        if key in done: continue
        png = f"he/tmp_{y}_{i}.png"
        p.get_pixmap(dpi=200).save(png)
        t = subprocess.run(["./ocrbin", png], capture_output=True, text=True).stdout
        os.remove(png)
        open(f"he/inhalt_txt_{y}_{i+1:02d}.txt", "w").write(t)
        hits = [t[max(0, m.start()-150):m.start()+200].replace("\n", " ").replace("\t", " ") for m in re.finditer(r"(?i)feiertag", t)]
        out.write(f"{key}\t{len(t)}\t{' || '.join(hits)}\n"); out.flush()
print("done")
