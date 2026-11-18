# ruff: noqa
"""미리보기 PDF 1 쪽(호의 목차, 텍스트층)에서 제목을 뽑는다 — 2021–2023 호(상품 화면에 목차가 없는 해).

사용: uv run --no-project --with 'pypdf==5.4.0' --with 'cryptography==44.0.2' python e_toc.py <previews-dir> > e_toc.tsv
열: 연도, 호, 꼴, 1 쪽 머리의 날짜, 순번, 제목. 미리보기는 빈 비밀번호의 AES 암호화라 cryptography 가 필요하다.
1 쪽의 「Inhaltsverzeichnis」 뒤를 줄로 잇고, 점선(…)과 쪽 번호로 끝나는 곳에서 제목을 끊는다. 줄 끝 하이픈은 잇는다.
쪽 번호 없이 끝나는 마지막 덩어리(예: 「Inhaltsverzeichnis … Jahrgang 2021」)도 제목으로 남긴다.
"""
import os
import re
import sys

from pypdf import PdfReader

d = sys.argv[1]
print("year\tissue\tkind\tdate\tn\ttitle")
for name in sorted(os.listdir(d)):
    if not name.endswith(".pdf"):
        continue
    year, issue, kind = name[:-4].split("_", 2)
    text = PdfReader(os.path.join(d, name)).pages[0].extract_text() or ""
    m = re.search(r"Nr\.\s*\S+\s+(\d{1,2}\.\s*\w+\s+\d{4})", text)
    date = re.sub(r"\s+", " ", m.group(1)) if m else ""
    body = text.split("Inhaltsverzeichnis", 1)[1] if "Inhaltsverzeichnis" in text else ""
    body = re.sub(r"-\s*\n\s*(?=[a-zäöüß])", "", body)
    body = re.sub(r"\s+", " ", body)
    parts = [p.strip() for p in re.split(r"[…\.]{2,}\s*\d+", body) if p.strip()]
    if not parts:
        print(f"{year}\t{issue}\t{kind}\t{date}\t0\t(목차 없음)")
    for n, t in enumerate(parts, 1):
        print(f"{year}\t{issue}\t{kind}\t{date}\t{n}\t{t}")
