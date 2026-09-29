"""판독한 두 면의 PNG 를 PDF 에서 다시 만든다(재현 기록, CI 는 돌리지 않는다).

PDF 는 레포에 두지 않는다. 먼저 받아서 sha256 을 맞춘 뒤 이 스크립트를 돌린다.

    curl -sS -L -o 1971-00036.pdf https://starweb.hessen.de/cache/GVBL/1971/00036.pdf
    curl -sS -L -o 1994-00025.pdf https://starweb.hessen.de/cache/GVBL/1994/00025.pdf
    shasum -a 256 1971-00036.pdf 1994-00025.pdf
    uv run --no-project --with pymupdf==1.26.5 python render_pngs.py

sha256 은 rules/de_he/solar_holidays.yaml 머리 주석과 같아야 한다. 출력은 png/ 아래,
파일 이름은 전사본 머리의 판독 대상 경로와 같다.
"""

import os

import fitz  # PyMuPDF 1.26.5

os.makedirs("png", exist_ok=True)


def page(path, index):
    """렌더마다 문서를 새로 열고 MuPDF 의 이미지 저장소를 비운다 — 저장소에 남은 다른
    해상도의 디코드가 쓰이면 픽셀이 달라진다(NW 조사 폴더 render_pngs.py 참조)."""
    fitz.TOOLS.store_shrink(100)
    return fitz.open(path)[index]


def clip(p, x0, y0, x1, y1):
    r = p.rect
    return fitz.Rect(r.width * x0, r.height * y0, r.width * x1, r.height * y1)


# 1971 I Nr. 36, PDF 2 쪽 = S. 344. § 1 Abs. 1(좌단).
p = page("1971-00036.pdf", 1)
p.get_pixmap(clip=clip(p, 0.1, 0.1, 0.52, 0.5), dpi=300).save("png/1971_S344_par1.png")

# 1994 I Nr. 25, PDF 22 쪽 = S. 596. Art. 1(좌단).
p = page("1994-00025.pdf", 21)
p.get_pixmap(clip=clip(p, 0.05, 0.05, 0.52, 0.55), dpi=250).save("png/1994_S596_artI.png")
