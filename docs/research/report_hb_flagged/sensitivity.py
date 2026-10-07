# ruff: noqa
"""임계 ±20% 민감도: 임계를 하나씩 ±20% 옮겼을 때 분류가 바뀌는 쪽을 센다. 분류 자체는 바꾸지 않는다(보고용).

사용: python -I sensitivity.py pages_measured.tsv
"""
import csv
import sys

R = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))


def cls(r, area=0.25, px=500, vec=500, blank=50):
    fr = [None if x == "unknown" else float(x) for x in r["img_area_frac"].split(",") if x]
    dims = [tuple(map(int, d.split("x"))) for d in r["img_px"].split(",") if d]
    p = int(r["path_ops"])
    for (w, h), f in zip(dims, fr):
        if f is not None and f >= area:
            return "IMAGE"
        if f is None and w >= px and h >= px:
            return "IMAGE"
    if p >= vec:
        return "VECTOR"
    if not dims and p < blank:
        return "BLANK"
    return "OTHER"


base = {(r["file"], r["page"]): r["class"] for r in R}
assert all(cls(r) == base[(r["file"], r["page"])] for r in R)
for name, kw in [("area 0.20", dict(area=0.20)), ("area 0.30", dict(area=0.30)),
                 ("px 400", dict(px=400)), ("px 600", dict(px=600)),
                 ("vector 400", dict(vec=400)), ("vector 600", dict(vec=600)),
                 ("blank 40", dict(blank=40)), ("blank 60", dict(blank=60))]:
    ch = [(r["file"], r["page"], base[(r["file"], r["page"])], cls(r, **kw)) for r in R
          if cls(r, **kw) != base[(r["file"], r["page"])]]
    print(f"{name}\t{len(ch)}\t" + " ".join(f"{f}:p{p}:{a}->{b}" for f, p, a, b in ch))
