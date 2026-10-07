# ruff: noqa
"""플래그 쪽마다 내용 스트림을 걸어 이미지·경로·텍스트 연산자를 센다. Form XObject 안으로 재귀한다.

사용: uv run --no-project --with 'pypdf==5.4.0' python -I measure.py <flagged_pages.txt> <pdf-dir> > pages_measured.tsv

측정(쪽마다):
  - 이미지 XObject: 개수, 픽셀 W×H, 표시 면적 / MediaBox 면적. 면적은 Do 시점 CTM 의 |a·d − b·c|
    (이미지는 단위 정사각형을 CTM 으로 그린다). CTM 을 풀지 못하면 "unknown".
  - 경로 연산자: m l c v y h re S s f F f* B B* b b* n
  - 텍스트 표시 연산자: Tj TJ ' "
  - 참고(분류에 쓰지 않음): 인라인 이미지(BI…EI) 수, Form XObject 수
분류(실행 전에 고정):
  IMAGE  : 표시 면적 ≥ 25% 인 이미지 XObject 가 있다. 면적 unknown 인 이미지는 ≥ 500×500 px 이면.
  VECTOR : IMAGE 아님, 경로 연산자 ≥ 500
  BLANK  : 이미지 XObject 없음, 경로 연산자 < 50
  OTHER  : 나머지
"""
import sys

import pypdf
from pypdf.generic import ContentStream

PATH_OPS = {b"m", b"l", b"c", b"v", b"y", b"h", b"re", b"S", b"s", b"f", b"F", b"f*",
            b"B", b"B*", b"b", b"b*", b"n"}
TEXT_OPS = {b"Tj", b"TJ", b"'", b'"'}


def mul(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + b * c2, a * b2 + b * d2, c * a2 + d * c2, c * b2 + d * d2,
            e * a2 + f * c2 + e2, e * b2 + f * d2 + f2)


class Walker:
    def __init__(self, reader):
        self.reader = reader
        self.images = []  # (w, h, area or None)
        self.paths = self.texts = self.inline = self.forms = 0

    def walk(self, stream, resources, ctm, depth=0, seen=()):
        if depth > 20:
            return
        try:
            cs = ContentStream(stream, self.reader)
        except Exception:
            return
        xobjs = {}
        try:
            xo = resources.get("/XObject") if resources else None
            xobjs = xo.get_object() if xo is not None else {}
        except Exception:
            xobjs = {}
        stack, cur = [], ctm
        for operands, op in cs.operations:
            if op == b"q":
                stack.append(cur)
            elif op == b"Q":
                cur = stack.pop() if stack else cur
            elif op == b"cm":
                try:
                    m = tuple(float(x) for x in operands)
                    cur = mul(m, cur) if cur is not None and len(m) == 6 else None
                except Exception:
                    cur = None
            elif op in PATH_OPS:
                self.paths += 1
            elif op in TEXT_OPS:
                self.texts += 1
            elif op == b"INLINE IMAGE":
                self.inline += 1
            elif op == b"Do":
                name = operands[0] if operands else None
                try:
                    ref = xobjs[name]
                    x = ref.get_object()
                except Exception:
                    continue
                sub = x.get("/Subtype")
                if sub == "/Image":
                    w, h = int(x.get("/Width", 0)), int(x.get("/Height", 0))
                    area = abs(cur[0] * cur[3] - cur[1] * cur[2]) if cur is not None else None
                    self.images.append((w, h, area))
                elif sub == "/Form":
                    self.forms += 1
                    key = getattr(ref, "idnum", id(x))
                    if key in seen:
                        continue
                    try:
                        fm = tuple(float(v) for v in x.get("/Matrix", [1, 0, 0, 1, 0, 0]))
                        fctm = mul(fm, cur) if cur is not None else None
                    except Exception:
                        fctm = None
                    res = x.get("/Resources")
                    res = res.get_object() if res is not None else resources
                    self.walk(x, res, fctm, depth + 1, seen + (key,))


def classify(images, paths):
    for w, h, frac in images:
        if frac is not None and frac >= 0.25:
            return "IMAGE"
        if frac is None and w >= 500 and h >= 500:
            return "IMAGE"
    if paths >= 500:
        return "VECTOR"
    if not images and paths < 50:
        return "BLANK"
    return "OTHER"


flagged = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="utf-8")][1:]
pdfdir = sys.argv[2]
readers = {}
print("\t".join(["file", "page", "mediabox_w", "mediabox_h", "img_count", "img_px", "img_area_frac",
                 "max_area_frac", "area_unknown", "path_ops", "text_ops", "inline_img", "form_xobj", "class"]))
for f, p, _n in flagged:
    r = readers.setdefault(f, pypdf.PdfReader(f"{pdfdir}/{f}"))
    page = r.pages[int(p) - 1]
    mb = page.mediabox
    mw, mh = float(mb.width), float(mb.height)
    wk = Walker(r)
    wk.walk(page.get_contents(), page.get("/Resources").get_object() if page.get("/Resources") else None,
            (1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
    fracs = [None if a is None else a / (mw * mh) for _, _, a in wk.images]
    known = [x for x in fracs if x is not None]
    imgs = [(w, h, fr) for (w, h, _), fr in zip(wk.images, fracs)]
    print("\t".join([f, p, f"{mw:g}", f"{mh:g}", str(len(imgs)),
                     ",".join(f"{w}x{h}" for w, h, _ in imgs),
                     ",".join("unknown" if x is None else f"{x:.4f}" for x in fracs),
                     f"{max(known):.4f}" if known else "",
                     str(sum(1 for x in fracs if x is None)),
                     str(wk.paths), str(wk.texts), str(wk.inline), str(wk.forms),
                     classify(imgs, wk.paths)]))
