# ruff: noqa
"""A — sources.tsv 의 source 문면에 범주 패턴을 대고 적중을 낸다. 대소문자 구분·무시 두 번 돌려 차이를 센다.
사용: python classify.py sources.tsv > hits.tsv"""
import csv
import re
import sys

PATTERNS = {
    "C1": [r"rules/", r"docs/", r"tests/", r"\.py\b", r"\.yaml\b", r"\.md\b"],
    "C2": [r"머리 주석", r"이 파일", r"이 표", r"주석"],
    "C3": [r"de\.ics", r"\.ics\b", r"전례", r"미러", r"\bde_[a-z]{2}\b(?! 와 같은)", r"\bBW 의\b", r"\bde_bw 의\b"],
    "C4": [r"\btoken\b", r"\bkey\b", r"토큰", r"\bUID\b"],
    "C5": [r"무개정", r"변경 없음", r"개정 없음", r"개정이 없", r"유효", r"변동 없", r"unverändert", r"keine Änderung", r"gilt fort", r"그대로"],
    "C6": [r"SUMMARY", r"\b(erster|zweiter)_weihnachtstag\b", r"source_todo", r"verified", r"#\d+", r"[Hh]oliday_\d", r"참조", r"조사 보고", r"README", r"레포", r"세션"],
}

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["file", "key", "verified", "cat", "pattern", "cs_hits", "ci_hits", "context"])
for r in rows:
    s = r["source"]
    for cat, pats in PATTERNS.items():
        for p in pats:
            cs = [m.start() for m in re.finditer(p, s)]
            ci = [m.start() for m in re.finditer(p, s, re.I)]
            if cs or ci:
                i = (cs or ci)[0]
                w.writerow([r["file"], r["key"], r["verified"], cat, p, len(cs), len(ci), s[max(0, i - 40): i + 60]])
