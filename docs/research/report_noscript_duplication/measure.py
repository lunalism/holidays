# ruff: noqa
"""B·C 측정 — 페이지에서 블록 셋을 정확한 앵커로 떼어 크기를 잰다.

앵커 (landing/render.py·template.html 에서 확인한 구조):
    json      <script type="application/json" id="feed-data"> … </script>   (template.html 706–708)
    list      body 의 <noscript> — 속성 없는 여는 태그 중 head style 이 아닌 것 하나
              (render.py::_noscript 가 "<noscript>" 로 시작해 "</noscript>" 로 끝낸다)
    head      <noscript><style> … </style></noscript>                      (template.html 29–31)
각 앵커가 정확히 1 개가 아니면 멈춘다. 떼는 단위는 줄 — 블록 첫 줄의 줄머리(들여쓰기)부터
마지막 줄의 줄바꿈까지. 블록이 줄 중간에서 시작·끝나지 않는지도 검사한다.

사용: python measure.py <label> <page.html> [...]   → TSV 를 stdout 으로.
gzip 은 Python gzip.compress(mtime=0) — 헤더 10 B + 트레일러 8 B, 파일명 없음.
레벨 5 는 Pages 가 보낸 바이트 수와 세 면 모두 정확히 같은 레벨이다(gzip_levels.txt).
"""

from __future__ import annotations

import gzip
import sys

JSON_OPEN = '<script type="application/json" id="feed-data">'
HEAD_OPEN = "<noscript><style>"
HEAD_CLOSE = "</style></noscript>"


def _line_span(page: str, start: int, end: int) -> tuple[int, int]:
    ls = page.rfind("\n", 0, start) + 1
    if page[ls:start].strip():
        raise SystemExit(f"블록이 줄 중간에서 시작한다: {page[ls:start]!r}")
    le = page.index("\n", end)
    if page[end:le].strip():
        raise SystemExit(f"블록 뒤에 같은 줄 내용이 있다: {page[end:le]!r}")
    return ls, le + 1


def spans(page: str) -> dict[str, tuple[int, int]]:
    out = {}
    assert page.count(JSON_OPEN) == 1, "feed-data 블록이 1 개가 아니다"
    s = page.index(JSON_OPEN)
    e = page.index("</script>", s) + len("</script>")
    out["json"] = _line_span(page, s, e)

    assert page.count(HEAD_OPEN) == 1 and page.count(HEAD_CLOSE) == 1, "head noscript style"
    s = page.index(HEAD_OPEN)
    e = page.index(HEAD_CLOSE, s) + len(HEAD_CLOSE)
    out["head"] = _line_span(page, s, e)

    plain = [i for i in range(len(page)) if page.startswith("<noscript>", i)]
    body = [i for i in plain if not page.startswith(HEAD_OPEN, i)]
    assert len(plain) == 2 and len(body) == 1, f"<noscript> 여는 태그 {len(plain)} 개"
    s = body[0]
    assert page.count("</noscript>") == 2
    e = page.index("</noscript>", s) + len("</noscript>")
    assert '<div class="feed-group">' in page[s:e]
    out["list"] = _line_span(page, s, e)
    return out


def cut(page: str, parts: dict[str, tuple[int, int]], names: list[str]) -> str:
    for a, b in sorted((parts[n] for n in names), reverse=True):
        page = page[:a] + page[b:]
    return page


def gz(text: str, level: int) -> int:
    return len(gzip.compress(text.encode("utf-8"), compresslevel=level, mtime=0))


VARIANTS = [
    ("full", []),
    ("-json", ["json"]),
    ("-list", ["list"]),
    ("-head", ["head"]),
    ("-json-list", ["json", "list"]),
]


def main(argv: list[str]) -> None:
    label = argv[0]
    print("set\tpage\tvariant\traw\tgzip5\tgzip9\td_raw\td_gzip5\td_gzip9")
    for path in argv[1:]:
        page = open(path, encoding="utf-8").read()
        parts = spans(page)
        base = None
        for name, names in VARIANTS:
            p = cut(page, parts, names)
            row = (len(p.encode()), gz(p, 5), gz(p, 9))
            base = base or row
            d = tuple(b - r for b, r in zip(base, row))
            print(label, path, name, *row, *d, sep="\t")
        for n, (a, b) in parts.items():
            print(f"# {label}\t{path}\t{n}\tchars {a}..{b}\tlines "
                  f"{page.count(chr(10), 0, a) + 1}..{page.count(chr(10), 0, b)}")


if __name__ == "__main__":
    main(sys.argv[1:])
