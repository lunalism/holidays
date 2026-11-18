# ruff: noqa
"""Part E — 2021 Nr. 15 – 2026 의 SächsGVBl. 호 목차 제목에서 검색어를 찾는다.

사용: python3 e_search.py e_titles.tsv e_toc.tsv > e_hits.tsv
- 입력: e_titles.tsv(상품 화면 목차, 2024–2026)와 e_toc.tsv(미리보기 1 쪽 목차, 2021 Nr. 15 – 2023).
  두 표가 겹치는 호(2024 이후 미리보기는 받지 않았다)는 없다.
- 검색어(de_bb·de_mv 와 같은 꼴에 SN 몫을 더함): feiertag, gedenktag, einmalig, bettag, arbeitsruhe, sächssfg.
- 비교는 casefold 한 제목과, 거기서 공백을 모두 뺀 제목(줄바꿈 하이픈이 「Glücks spielwesens」 처럼 공백으로 남는 일 때문)
  둘에서 한다.
"""
import sys

TERMS = ("feiertag", "gedenktag", "einmalig", "bettag", "arbeitsruhe", "sächssfg")
print("year\tissue\tkind\tdate\tn\tterms\ttitle")
for path in sys.argv[1:]:
    for ln in open(path, encoding="utf-8").read().splitlines()[1:]:
        year, issue, kind, date, n, title = ln.split("\t")
        folded = title.casefold()
        squeezed = folded.replace(" ", "")
        hits = [t for t in TERMS if t in folded or t in squeezed]
        if hits:
            print(f"{year}\t{issue}\t{kind}\t{date}\t{n}\t{','.join(hits)}\t{title}")
