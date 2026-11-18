"""REVOSax 통합본 PDF 의 텍스트층에서 머리·§ 1·§ 2 를 뽑고 각 정규화 텍스트의 sha256 을 잰다.

사용: uv run --no-project --with 'pypdf==5.4.0' python extract_revosax.py <pdf> <out.txt>
- 전문: 쪽마다 pypdf extract_text() 를 이어 붙인다.
- 정규화: 줄마다 앞뒤 공백 제거·안의 공백 축약·빈 줄 제거, 줄바꿈 \n, 끝에 \n 하나.
- § 1: 「§ 1」 로 시작하는 줄부터 「§ 2」 로 시작하는 줄 앞까지. § 2: 「§ 2」 부터 「§ 2a」 앞까지.
  (쪽 머리·꼬리 줄이 끼면 그대로 둔다 — 두 파일을 같은 규칙으로 비교하는 것이 목적이다.)
"""
import hashlib
import re
import sys

from pypdf import PdfReader

src, out = sys.argv[1:3]
reader = PdfReader(src)
raw = "\n".join(page.extract_text() or "" for page in reader.pages)
lines = [re.sub(r"\s+", " ", ln).strip() for ln in raw.splitlines()]
lines = [ln for ln in lines if ln]


def section(start_re, end_re):
    i = next(n for n, ln in enumerate(lines) if re.match(start_re, ln))
    j = next(n for n in range(i + 1, len(lines)) if re.match(end_re, lines[n]))
    return "\n".join(lines[i:j]) + "\n"


full = "\n".join(lines) + "\n"
p1 = section(r"^§ 1\b", r"^§ 2\b")
p2 = section(r"^§ 2\b(?!a)", r"^§ 2a\b")
h = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in (("full", full), ("p1", p1), ("p2", p2))}
with open(out, "w", encoding="utf-8") as f:
    f.write(f"# pages={len(reader.pages)}\n# sha256 full={h['full']}\n# sha256 §1={h['p1']}\n"
            f"# sha256 §2={h['p2']}\n\n# --- 전문(정규화) ---\n{full}")
print(len(reader.pages), "pages", h)
