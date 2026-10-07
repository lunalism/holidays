# ruff: noqa
"""진단용: BLANK·OTHER 쪽의 경로 연산자를 종류별로 센다(Form XObject 재귀 포함). 분류는 바꾸지 않는다.

사용: uv run --no-project --with 'pypdf==5.4.0' python -I op_breakdown.py <pages_measured.tsv> <pdf-dir> > op_breakdown.tsv
열: file, page, class, path_ops, 그리고 연산자별 수(m l c v y h re S s f F f* B B* b b* n), W(클립), W*(클립)
"""
import collections
import csv
import sys

import pypdf
from pypdf.generic import ContentStream

OPS = ["m", "l", "c", "v", "y", "h", "re", "S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n", "W", "W*"]


def walk(reader, stream, res, cnt, depth=0):
    if depth > 20:
        return
    try:
        cs = ContentStream(stream, reader)
    except Exception:
        return
    try:
        xo = res.get("/XObject").get_object() if res and res.get("/XObject") is not None else {}
    except Exception:
        xo = {}
    for operands, op in cs.operations:
        o = op.decode("latin-1")
        if o in OPS:
            cnt[o] += 1
        elif o == "Do" and operands:
            try:
                x = xo[operands[0]].get_object()
            except Exception:
                continue
            if x.get("/Subtype") == "/Form":
                r2 = x.get("/Resources")
                walk(reader, x, r2.get_object() if r2 is not None else res, cnt, depth + 1)


rows = [r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t") if r["class"] in ("BLANK", "OTHER")]
readers = {}
print("\t".join(["file", "page", "class", "path_ops"] + OPS))
for r in rows:
    rd = readers.setdefault(r["file"], pypdf.PdfReader(f"{sys.argv[2]}/{r['file']}"))
    pg = rd.pages[int(r["page"]) - 1]
    cnt = collections.Counter()
    res = pg.get("/Resources")
    walk(rd, pg.get_contents(), res.get_object() if res is not None else None, cnt)
    print("\t".join([r["file"], r["page"], r["class"], r["path_ops"]] + [str(cnt[o]) for o in OPS]))
