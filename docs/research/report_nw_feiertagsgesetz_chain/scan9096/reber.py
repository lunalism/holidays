# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import fitz, re, subprocess, os
rows = [l.rstrip("\n").split("\t") for l in open("scan9096/result.tsv")]
out = open("scan9096/berichtigung_ctx.tsv", "w")
for r in rows:
    y, n, mode, cnt = r[:4]
    if not cnt or cnt == "0": continue
    if len(r) >= 6:
        ctx = r[5]
    else:
        d = fitz.open(f"scan9096/{y}-{n}.pdf")
        if mode == "textlayer":
            text = "\n".join(p.get_text() for p in d)
        else:
            png = f"scan9096/{y}-{n}_p1.png"; d[0].get_pixmap(dpi=200).save(png)
            text = subprocess.run(["./ocrbin", png], capture_output=True, text=True).stdout; os.remove(png)
        ctx = " || ".join(text[max(0,m.start()-150):m.start()+200].replace("\n"," ").replace("\t"," ") for m in re.finditer(r"(?i)berichtigung", text))
    out.write(f"{y}\t{n}\t{mode}\t{cnt}\t{ctx}\n")
print("ok")
