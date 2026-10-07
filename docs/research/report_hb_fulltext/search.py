# ruff: noqa
"""쪽별 텍스트(extract.py 출력)를 정규화하고 패턴을 찾는다.

사용: python -I search.py <txt-dir 또는 txt 파일…> > hits.tsv
정규화(쪽 단위, 이 순서):
  1. 줄 끝(뒤 공백 무시)이 "-" 이고 다음 줄(앞 공백 무시)이 소문자로 시작하면 "-" 와 줄바꿈을 지우고 잇는다.
     다음 줄이 소문자로 시작하지 않으면 그대로 둔다("Sonn-, Gedenk-" 같은 하이픈 보존).
  2. 공백 연속을 공백 하나로.
  3. casefold.
패턴(정규화 텍스트의 부분 문자열): feiertag, gedenk, 113-c, reformationstag, einmalig
열: file, page, pattern, offset, context(적중 앞뒤 약 300 자, 적중 부분은 [[ ]] 로 감쌈)
쪽 경계를 넘는 낱말은 잇지 않는다 — 쪽마다 따로 찾는다.
"""
import pathlib
import re
import sys

PATTERNS = ["feiertag", "gedenk", "113-c", "reformationstag", "einmalig"]
CTX = 300
PAGE = re.compile(r"\f=== page (\d+) ===\n")


def normalise(text):
    lines = text.split("\n")
    out = []
    for line in lines:
        if out and out[-1].rstrip().endswith("-"):
            nxt = line.lstrip()
            if nxt[:1].islower():
                out[-1] = out[-1].rstrip()[:-1] + nxt
                continue
        out.append(line)
    return " ".join(" ".join(out).split()).casefold()


def pages(path):
    parts = PAGE.split(path.read_text(encoding="utf-8"))
    for i in range(1, len(parts), 2):
        yield int(parts[i]), parts[i + 1]


args = [pathlib.Path(a) for a in sys.argv[1:]]
files = []
for a in args:
    files += sorted(a.glob("*.txt")) if a.is_dir() else [a]

print("file\tpage\tpattern\toffset\tcontext")
for f in files:
    for no, text in pages(f):
        norm = normalise(text)
        for pat in PATTERNS:
            start = 0
            while (i := norm.find(pat, start)) >= 0:
                ctx = norm[max(0, i - CTX):i] + "[[" + norm[i:i + len(pat)] + "]]" + norm[i + len(pat):i + len(pat) + CTX]
                print(f"{f.stem}\t{no}\t{pat}\t{i}\t{ctx}")
                start = i + 1
