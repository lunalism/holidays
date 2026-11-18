# ruff: noqa
"""PDF 의 지정 쪽을 PNG 로 렌더한다(텍스트층이 없는 쪽의 시각 판독용). 렌더는 scratch 에만 둔다.

사용: uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python render_pages.py <pdf> <dpi> <out-prefix> <쪽…(1부터)>
"""
import sys

import pypdfium2 as pdfium

src, dpi, prefix, *pages = sys.argv[1:]
doc = pdfium.PdfDocument(src)
for p in pages:
    img = doc[int(p) - 1].render(scale=int(dpi) / 72).to_pil()
    img.save(f"{prefix}_p{p}.png")
    print(f"{prefix}_p{p}.png", img.size)
