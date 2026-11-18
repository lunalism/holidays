# ruff: noqa
"""Part E 의 적중 분류표.

사용: python3 e_classify.py e_hits.tsv e_revosax_feiertag.tsv > e_classified.tsv
분류(지시의 셋): A = SächsSFG § 1 개정 / C = 주 전역 일회성 공휴일 지정 / D = 언급뿐.
- 관보 목차 적중(e_hits.tsv)은 둘이고 판정은 아래 NOTES 에 손으로 적었다(제목을 읽은 결과).
- REVOSax 「Feiertag」 적중은 Erlassdatum 이 2020-01-01 이후인 것만 분류한다. 판정은 결과 목록의 정식 제목·관보·유형을 읽은 것이고,
  문서 본문은 열지 않았다. 27 건 모두 제목이 근무·급여·절차·방송·교정 등 다른 법의 것이라 D 다.
"""
import datetime as dt
import re
import sys

M = {m: i for i, m in enumerate(
    "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split(), 1)}
NOTES = {
    ("2025", "6"): ("D", "SächsSFG § 2(Gedenk- und Trauertage, 8. Mai 추가)와 § 6 을 바꾼다. § 1 은 건드리지 않는다"
                         "(관보 S. 146 렌더 판독). 공휴일 지정 아님"),
    ("2022", "25"): ("D", "「einmaligen Heizkostenzuschusses」 — 일회성 난방비 보조금. 공휴일과 무관"),
}
print("source\tid\tdate\tclass\tbasis\ttitle")
hits, revosax = sys.argv[1:3]
for ln in open(hits, encoding="utf-8").read().splitlines()[1:]:
    year, issue, kind, date, n, terms, title = ln.split("\t")
    cls, basis = NOTES[(year, issue)]
    print(f"SächsGVBl. 목차\t{year} Nr. {issue}\t{date}\t{cls}\t{basis} (검색어 {terms})\t{title}")
for ln in open(revosax, encoding="utf-8").read().splitlines()[1:]:
    page, n, href, text, body = ln.split("\t")
    m = re.search(r"Erlassdatum: (\d+)\. (\w+) (\d{4})", body)
    if not m:
        continue
    d = dt.date(int(m.group(3)), M[m.group(2)], int(m.group(1)))
    if d < dt.date(2020, 1, 1):
        continue
    title = body.split(" | ")[0]
    print(f"REVOSax\t{href}\t{d}\tD\t정식 제목상 다른 법(근무·급여·절차 등)의 조문이 Feiertag 를 언급한다 — 본문은 열지 않았다\t{title}")
