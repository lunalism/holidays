# ruff: noqa
"""플래그 쪽 741 개를 클립 제외 규칙(D1)으로 다시 재고 다시 분류한다.

사용: uv run --no-project --with 'pypdf==5.4.0' python -I reclassify.py \
        <report_hb_flagged/pages_measured.tsv> <pdf-dir> > pages_reclassified.tsv

규칙 변경(실행 전에 고정): 경로 구성 연산자(m l c v y h re) 뒤에 W 또는 W* 가 오고 이어 n 으로 끝나는
경로(클립만, 칠하지 않음)는 그 구성 연산자와 n 을 경로 연산자 합계에서 뺀다.
  - 구성 연산자는 끝맺음 연산자가 올 때까지 쌓아 둔다.
  - 칠하기(S s f F f* B B* b b*)로 끝나면 쌓인 구성 연산자 + 칠하기 1 을 센다(W 가 있어도 — 칠했으므로).
  - n 으로 끝나고 그 경로에 W/W* 가 있었으면 하나도 세지 않는다. W/W* 가 없었으면 구성 + n 1 을 센다.
  - 스트림 끝까지 끝맺음이 없으면 쌓인 구성 연산자를 센다.
그 밖의 측정(이미지 XObject·면적·텍스트 연산자)과 분류 규칙·임계는 report_hb_flagged/measure.py 그대로다.
  IMAGE  : 표시 면적 ≥ 25% 인 이미지 XObject(면적 unknown 이면 ≥ 500×500 px)
  VECTOR : IMAGE 아님, 경로 연산자 ≥ 500
  BLANK  : 이미지 XObject 없음, 경로 연산자 < 50
  OTHER  : 나머지
열: file, page, old_class, old_path_ops, new_path_ops, clip_paths, img_count, max_area_frac, new_class
"""
import csv
import sys

import pypdf
from pypdf.generic import ContentStream

CONSTRUCT = {b"m", b"l", b"c", b"v", b"y", b"h", b"re"}
PAINT = {b"S", b"s", b"f", b"F", b"f*", b"B", b"B*", b"b", b"b*"}


def mul(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + b * c2, a * b2 + b * d2, c * a2 + d * c2, c * b2 + d * d2,
            e * a2 + f * c2 + e2, e * b2 + f * d2 + f2)


class Walker:
    def __init__(self, reader):
        self.reader = reader
        self.images = []
        self.paths = 0
        self.clips = 0

    def walk(self, stream, resources, ctm, depth=0, seen=()):
        if depth > 20:
            return
        try:
            cs = ContentStream(stream, self.reader)
        except Exception:
            return
        try:
            xo = resources.get("/XObject") if resources else None
            xobjs = xo.get_object() if xo is not None else {}
        except Exception:
            xobjs = {}
        stack, cur = [], ctm
        pending, clip = 0, False
        for operands, op in cs.operations:
            if op in CONSTRUCT:
                pending += 1
            elif op in (b"W", b"W*"):
                clip = True
            elif op in PAINT:
                self.paths += pending + 1
                pending, clip = 0, False
            elif op == b"n":
                if clip:
                    self.clips += 1
                else:
                    self.paths += pending + 1
                pending, clip = 0, False
            elif op == b"q":
                stack.append(cur)
            elif op == b"Q":
                cur = stack.pop() if stack else cur
            elif op == b"cm":
                try:
                    m = tuple(float(x) for x in operands)
                    cur = mul(m, cur) if cur is not None and len(m) == 6 else None
                except Exception:
                    cur = None
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
        self.paths += pending


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


rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
pdfdir = sys.argv[2]
readers = {}
print("\t".join(["file", "page", "old_class", "old_path_ops", "new_path_ops", "clip_paths",
                 "img_count", "max_area_frac", "new_class"]))
for r in rows:
    rd = readers.setdefault(r["file"], pypdf.PdfReader(f"{pdfdir}/{r['file']}"))
    page = rd.pages[int(r["page"]) - 1]
    mb = page.mediabox
    area_page = float(mb.width) * float(mb.height)
    wk = Walker(rd)
    res = page.get("/Resources")
    wk.walk(page.get_contents(), res.get_object() if res is not None else None, (1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
    imgs = [(w, h, None if a is None else a / area_page) for w, h, a in wk.images]
    known = [f for _, _, f in imgs if f is not None]
    print("\t".join([r["file"], r["page"], r["class"], r["path_ops"], str(wk.paths), str(wk.clips),
                     str(len(imgs)), f"{max(known):.4f}" if known else "", classify(imgs, wk.paths)]))
