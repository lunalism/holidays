# ruff: noqa
"""D — HmbGVBl. 2018 Nr. 9 PDF 의 쪽수·텍스트층·해당 조문 위치.
사용: uv run --no-project --with pymupdf==1.26.5 python hh_pdf_text.py <pdf>"""
import re
import sys

import fitz

doc = fitz.open(sys.argv[1])
print("pages", doc.page_count, "metadata", {k: v for k, v in doc.metadata.items() if v})
for i, page in enumerate(doc):
    t = page.get_text()
    head = " ".join(t.split())[:160]
    print(f"--- pdf p.{i + 1} chars={len(t)} head: {head}")
    for pat in (r"Fünftes Gesetz", r"Feiertagsgesetz", r"Hinter Nummer 7", r"31\. Oktober", r"Nummern 8 und 9", r"Vom 12\. März 2018", r"12\. März 2018"):
        for m in re.finditer(pat, t):
            ctx = " ".join(t[max(0, m.start() - 80): m.end() + 120].split())
            print(f"   [{pat}] {ctx}")
