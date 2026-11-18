# ruff: noqa
"""렌더 innerText(<prefix>.txt)에서 § 2 와 문서 머리 줄을 뽑는다.

사용: python3 extract_para2.py <render.txt> <out.txt>
- 머리: 「Dokumentkopf」 와 「Dokumentreiter」 사이의 줄(Fassung vom·Gültig ab 등).
- § 2: 「§ 2」 한 줄부터 「Redaktionelle Hinweise」 앞까지.
- 정규화: 줄마다 앞뒤 공백을 지우고 안의 공백(탭 포함)을 한 칸으로 줄인 뒤 빈 줄을 뺀다. 줄바꿈은 \n, 끝에 \n 하나.
sha256 은 정규화한 § 2 텍스트(머리 제외)의 UTF-8 바이트로 잰다 — 렌더 HTML 은 바이트 안정이 아니다
(report_mv_prep A1).
"""
import hashlib
import re
import sys

src, out = sys.argv[1:3]
lines = [re.sub(r"\s+", " ", ln).strip() for ln in open(src, encoding="utf-8").read().splitlines()]
lines = [ln for ln in lines if ln]
head = lines[lines.index("Dokumentkopf") + 1: lines.index("Dokumentreiter")]
start = lines.index("§ 2")
end = lines.index("Redaktionelle Hinweise", start)
para = "\n".join(lines[start:end]) + "\n"
digest = hashlib.sha256(para.encode("utf-8")).hexdigest()
with open(out, "w", encoding="utf-8") as f:
    f.write("# 머리(Dokumentkopf)\n" + "\n".join(head) + "\n\n# § 2 (정규화)\n" + para)
    f.write(f"\n# sha256(§ 2 정규화 텍스트) = {digest}\n")
print(digest, len(para.encode("utf-8")), "bytes", src)
