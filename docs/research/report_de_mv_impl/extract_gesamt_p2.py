# ruff: noqa
"""Gesamtausgabe 렌더 innerText 에서 Stand 줄과 § 2 를 뽑는다(report_mv_retry/extract_para2.py 와 같은 정규화).

사용: python3 extract_gesamt_p2.py <render.txt> <out.txt>
- Stand: 「Stand:」 로 시작하는 첫 줄과 그 앞의 「… aktuellste verfügbare Fassung der Gesamtausgabe」 줄.
- § 2: 본문의 「§ 2」 한 줄(목차의 「§ 2 - …」 가 아니라 정확히 「§ 2」)부터 「zur Einzelansicht § 2」 또는
  「Fußnoten」 앞까지 — Gesamtausgabe 에는 조문마다 「zur Einzelansicht § N」 이 붙는다.
- 정규화: 줄마다 앞뒤 공백을 지우고 안의 공백(탭 포함)을 한 칸으로 줄인 뒤 빈 줄을 뺀다. 줄바꿈 \n, 끝에 \n 하나.
sha256 은 정규화한 § 2 텍스트의 UTF-8 바이트로 잰다 — report_mv_retry 의 조문 단위 id 추출과 같은 정의다.
"""
import hashlib
import re
import sys

src, out = sys.argv[1:3]
lines = [re.sub(r"\s+", " ", ln).strip() for ln in open(src, encoding="utf-8").read().splitlines()]
lines = [ln for ln in lines if ln]
stand = [ln for ln in lines if ln.startswith("Stand:") or "aktuellste verfügbare Fassung" in ln][:2]
start = lines.index("§ 2")
end = next(i for i in range(start + 1, len(lines)) if lines[i] in ("zur Einzelansicht § 2", "Fußnoten"))
para = "\n".join(lines[start:end]) + "\n"
digest = hashlib.sha256(para.encode("utf-8")).hexdigest()
with open(out, "w", encoding="utf-8") as f:
    f.write("# Stand\n" + "\n".join(stand) + "\n\n# § 2 (정규화)\n" + para)
    f.write(f"\n# sha256(§ 2 정규화 텍스트) = {digest}\n")
print(digest, len(para.encode("utf-8")), "bytes", "end-marker:", lines[end])
