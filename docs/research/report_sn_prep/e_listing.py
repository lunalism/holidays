# ruff: noqa
"""recht-sachsen.de 의 SächsGVBl. 목록 화면(25 건씩)에서 호별 상품 화면 주소를 모은다.

사용: python3 e_listing.py <listing.html...> > e_listing.tsv
열: 연도, 호(16a 같은 a 호 포함), 꼴(regular / a / Anlageband), 상품 이름, 상품 화면 URL — 목록 화면의 링크 그대로.
구독 상품(Abonnement·Gemeindelizenz)은 호가 아니라 뺀다.
"""
import re
import sys

rows = {}
for path in sys.argv[1:]:
    h = open(path, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'title="(Sächsisches Gesetz- und Verordnungsblatt Heft (\d+)(a?)/(\d{4})([^"]*))"\s+href="([^"]+)"', h):
        name, num, a, year, rest, url = m.groups()
        kind = "Anlageband" if "Anlageband" in rest else ("a" if a else "regular")
        rows.setdefault(name, (int(year), int(num), a, kind, name, url))
print("year\tissue\tkind\tname\turl")
for year, num, a, kind, name, url in sorted(rows.values()):
    print(f"{year}\t{num}{a}\t{kind}\t{name}\t{url}")
