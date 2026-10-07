# ruff: noqa
"""읽기 집합(read_set.tsv)의 쪽을 렌더한다.

사용: uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I render.py <read_set.tsv> <pdf-dir> <png-dir> <dpi> [file:page ...]
  file:page 를 주면 그 쪽만(300 dpi 재렌더용). 파일명: <file>_p<page>_<dpi>.png
"""
import csv
import sys

import pypdfium2 as pdfium

rs, pdfdir, out, dpi = sys.argv[1:5]
only = {tuple(x.split(":")) for x in sys.argv[5:]}
for r in csv.DictReader(open(rs, encoding="utf-8"), delimiter="\t"):
    if only and (r["file"], r["page"]) not in only:
        continue
    doc = pdfium.PdfDocument(f"{pdfdir}/{r['file']}")
    img = doc[int(r["page"]) - 1].render(scale=int(dpi) / 72).to_pil()
    name = f"{r['file'][:-4]}_p{r['page']}_{dpi}.png"
    img.save(f"{out}/{name}")
    doc.close()
    print(name, img.size[0], img.size[1])
