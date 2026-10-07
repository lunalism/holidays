# ruff: noqa
"""분류기 검증용 표본: 분류마다 최대 10 쪽을 시드 고정 무작위로 뽑아 100 dpi 로 렌더한다.

사용: uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I sample_render.py \
        <pages_reclassified.tsv> <pdf-dir> <png-out-dir> > sample_list.tsv
시드: 20261007. 뽑기: 분류별로 (file, page) 를 정렬한 뒤 random.Random(SEED).sample.
렌더 이미지는 scratch 에만 둔다. 이 목록(sample_list.tsv)만 보고 폴더에 남긴다.
"""
import csv
import random
import sys

import pypdfium2 as pdfium

SEED = 20261007
N = 10
DPI = 100

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
pdfdir, out = sys.argv[2], sys.argv[3]
by = {}
for r in rows:
    by.setdefault(r["new_class"], []).append((r["file"], int(r["page"])))
print("class\tfile\tpage\tpng")
for cls in sorted(by):
    pool = sorted(by[cls])
    pick = random.Random(SEED).sample(pool, min(N, len(pool)))
    for f, p in pick:
        doc = pdfium.PdfDocument(f"{pdfdir}/{f}")
        img = doc[p - 1].render(scale=DPI / 72).to_pil()
        name = f"{cls}_{f[:-4]}_p{p}.png"
        img.save(f"{out}/{name}")
        doc.close()
        print(f"{cls}\t{f}\t{p}\t{name}")
