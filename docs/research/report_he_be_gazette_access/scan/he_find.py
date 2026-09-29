# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import fitz, subprocess, os, re, sys
f = sys.argv[1]; d = fitz.open(f)
for i, p in enumerate(d):
    t = p.get_text()
    src = "text"
    if len(t) < 100:
        p.get_pixmap(dpi=200).save("tmp.png"); t = subprocess.run(["./ocrbin", "tmp.png"], capture_output=True, text=True).stdout; src = "ocr"
    for m in re.finditer(r"(?i)Feiertagsgesetz|Feiertags-\s*gesetz|Sonn- und Feiertage", t):
        print(f"{os.path.basename(f)} p{i+1} [{src}] …", t[max(0, m.start()-200):m.start()+900].replace("\n", " | ")); break
