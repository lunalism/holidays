"""조사 보고가 판독한 PNG 를 PDF 에서 다시 만든다(재현 기록, CI 는 돌리지 않는다).

PDF 는 레포에 두지 않는다. 먼저 받아서 sha256 을 맞춘 뒤 이 스크립트를 돌린다.

    curl -sS -o 1989-19.pdf https://recht.nrw.de/system/files/GV_Archiv/4122-xmmgvb8919.pdf
    curl -sS -o 1991-19.pdf https://recht.nrw.de/system/files/GV_Archiv/3762-xmmgvb9119.pdf
    curl -sS -o 1994-88.pdf https://recht.nrw.de/system/files/GV_Archiv/4383-xmmgvb9488.pdf
    shasum -a 256 1989-19.pdf 1991-19.pdf 1994-88.pdf
    uv run --no-project --with pymupdf==1.26.5 python render_pngs.py

sha256 은 rules/de_nw/solar_holidays.yaml 머리 주석과 같아야 한다. 출력은 png/ 아래,
파일 이름은 조사 보고의 $S/png/ 경로와 같다. 크기(픽셀 수)는 조사 때의 PNG 와 같지만
바이트 동일은 보장하지 않는다 — 조사 때는 같은 면을 여러 해상도로 그리는 순서가 크롭마다
달라 MuPDF 저장소 상태가 달랐다(11 장 중 7 장만 바이트 동일, 2026-09-29 대조). 판독
대조에는 지장이 없다.
"""

import os

import fitz  # PyMuPDF 1.26.5

os.makedirs("png", exist_ok=True)


def clip(page, x0, y0, x1, y1):
    """면 크기에 대한 비율로 자른다."""
    r = page.rect
    return fitz.Rect(r.width * x0, r.height * y0, r.width * x1, r.height * y1)


def page(path, index):
    """렌더마다 문서를 새로 열고 MuPDF 의 이미지 저장소를 비운다. 저장소에 같은 면의
    다른 해상도 디코드가 남아 있으면 그것이 쓰여 픽셀이 달라진다 — 비워 두면 이
    스크립트의 출력은 렌더 순서와 무관하게 같다."""
    fitz.TOOLS.store_shrink(100)
    return fitz.open(path)[index]


# 1989 Nr. 19, PDF 2 쪽 = S. 222. § 2 Abs. 1 전체(좌단).
p = page("1989-19.pdf", 1)
fitz.Pixmap(p.parent, p.get_images(full=True)[0][0]).save("png/1989_S222_full.png")
p = page("1989-19.pdf", 1)
p.get_pixmap(clip=fitz.Rect(70, 460, 305, 685), dpi=300).save("png/1989_S222_par2abs1.png")

# 1991 Nr. 19, PDF 4 쪽 = S. 200. Art. I–II(좌단).
p = page("1991-19.pdf", 3)
fitz.Pixmap(p.parent, p.get_images(full=True)[0][0]).save("png/1991_S200_full.png")
p = page("1991-19.pdf", 3)
p.get_pixmap(clip=clip(p, 0, 0, 1, 0.5), dpi=150).save("png/1991_S200_top.png")
p = page("1991-19.pdf", 3)
p.get_pixmap(clip=clip(p, 0, 0.05, 0.5, 0.35), dpi=400).save("png/1991_S200_artI.png")

# 1994 Nr. 88, PDF 1 쪽 = 목차, PDF 4 쪽 = S. 1114(표제는 좌단 하단, Art. I 은 우단 상단).
p = page("1994-88.pdf", 0)
p.get_pixmap(clip=clip(p, 0, 0, 1, 0.5), dpi=150).save("png/1994_nr88_p1_top.png")
p = page("1994-88.pdf", 3)
fitz.Pixmap(p.parent, p.get_images(full=True)[0][0]).save("png/1994_nr88_p4_full.png")
p = page("1994-88.pdf", 3)
p.get_pixmap(clip=clip(p, 0, 0, 1, 0.5), dpi=150).save("png/1994_nr88_p4_top.png")
p = page("1994-88.pdf", 3)
p.get_pixmap(clip=clip(p, 0, 0.5, 1, 1), dpi=150).save("png/1994_nr88_p4_bottom.png")
p = page("1994-88.pdf", 3)
p.get_pixmap(clip=clip(p, 0.5, 0.07, 1, 0.22), dpi=400).save("png/1994_S1114_artI.png")
p = page("1994-88.pdf", 3)
p.get_pixmap(clip=clip(p, 0, 0.78, 0.5, 0.95), dpi=400).save("png/1994_S1114_title.png")
