# ruff: noqa
"""300 dpi 렌더를 2×2 타일(가장자리 5% 겹침)로 자른다 — 작은 지도 글자를 읽기 위해서.

사용: uv run --no-project --with 'pillow==11.3.0' python -I tile.py <png-dir>
입력 *_300.png 마다 *_300_t{1..4}.png 를 같은 폴더에 쓴다(왼쪽 위, 오른쪽 위, 왼쪽 아래, 오른쪽 아래).
"""
import pathlib
import sys

from PIL import Image

for p in sorted(pathlib.Path(sys.argv[1]).glob("*_300.png")):
    im = Image.open(p)
    w, h = im.size
    ox, oy = int(w * 0.05), int(h * 0.05)
    boxes = [(0, 0, w // 2 + ox, h // 2 + oy), (w // 2 - ox, 0, w, h // 2 + oy),
             (0, h // 2 - oy, w // 2 + ox, h), (w // 2 - ox, h // 2 - oy, w, h)]
    for i, b in enumerate(boxes, 1):
        im.crop(b).save(p.with_name(f"{p.stem}_t{i}.png"))
    print(p.name)
