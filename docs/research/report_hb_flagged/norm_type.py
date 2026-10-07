# ruff: noqa
"""플래그 파일 167 개에 목록 제목(Hinweistext)을 붙이고, 제목 문면만으로 규범 유형을 정한다.

사용: python -I norm_type.py <report_hb_fulltext/flagged_files.tsv> > norm_types.tsv
열: file, year, nr, norm_type, rule, title
규칙(위에서부터 처음 맞는 것, 제목 문면만 본다 — 본문은 보지 않는다):
  R1 제목이 "Berichtigung" 으로 시작                              → Berichtigung
  R2 제목이 "Bekanntmachung" 으로 시작                            → Bekanntmachung
  R3 제목이 "Entwurf" 로 시작                                     → unclear
  R4 첫 세 낱말 안에 "Ortsgesetz"                                  → other(Ortsgesetz)
  R5 첫 세 낱말 안에 "-gesetz" 낱말 + 제목에 "staatsvertrag"(대소문자 무시) → Zustimmungsgesetz zu Staatsvertrag
  R6 첫 세 낱말 안에 "-gesetz" 낱말 + 제목에 "Vertrag"/"Abkommen" (Staatsvertrag 아님) → unclear
  R7 첫 세 낱말 안에 "-gesetz" 낱말                                → Gesetz
  R8 첫 세 낱말 안에 "-verordnung" 낱말                            → Verordnung
  R9 첫 세 낱말 안에 "Satzung"                                     → Satzung
  R10 제목이 "Vertrag" 로 시작                                      → other(Vertrag)
  R11 나머지                                                        → unclear
"""
import csv
import re
import sys

csv.field_size_limit(10**7)


def norm_type(t):
    head = t.split()[:3]
    hl = [w.casefold() for w in head]
    tl = t.casefold()
    if t.startswith("Berichtigung"):
        return "Berichtigung", "R1"
    if t.startswith("Bekanntmachung"):
        return "Bekanntmachung", "R2"
    if t.startswith("Entwurf"):
        return "unclear", "R3"
    if any(w.startswith("ortsgesetz") for w in hl):
        return "other(Ortsgesetz)", "R4"
    if any(re.search(r"gesetz$", w) for w in hl):
        if "staatsvertrag" in tl:
            return "Zustimmungsgesetz zu Staatsvertrag", "R5"
        if re.search(r"\bvertrag\b|\babkommen\b", tl):
            return "unclear", "R6"
        return "Gesetz", "R7"
    if any(re.search(r"verordnung$", w) for w in hl):
        return "Verordnung", "R8"
    if any("satzung" in w for w in hl):
        return "Satzung", "R9"
    if t.startswith("Vertrag"):
        return "other(Vertrag)", "R10"
    return "unclear", "R11"


w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["file", "year", "nr", "norm_type", "rule", "title"])
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"):
    f = r["file"]
    y, n = f[:4], int(f[5:8])
    nt, rule = norm_type(r["hinweis"])
    w.writerow([f, y, n, nt, rule, r["hinweis"]])
