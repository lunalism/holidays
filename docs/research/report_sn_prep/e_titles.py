# ruff: noqa
"""호별 상품 화면(recht-sachsen.de)의 「Beschreibung」 에서 그 호의 목차(Inhaltsverzeichnis) 제목을 뽑는다.

사용: python3 e_titles.py <products-dir> > e_titles.tsv
열: 연도, 호, 꼴, 공개일(「Veröffentlicht am」), 순번, 제목. 상품 화면 파일 이름은 <연도>_<호>_<꼴>.html(e_fetch_products.sh).
목차는 「Beschreibung」 다음의 「Inhaltsverzeichnis | …」 줄부터, 같은 화면의 「Jahresinhaltsverzeichnis」 링크 묶음이나
「Titelangaben」·「Zusatzinformation」 앞까지의 줄이다. 제목이 하나도 없으면 「(목차 없음)」 한 줄을 남긴다.
"""
import html
import os
import re
import sys

d = sys.argv[1]
print("year\tissue\tkind\tpublished\tn\ttitle")
for name in sorted(os.listdir(d)):
    if not name.endswith(".html"):
        continue
    year, issue, kind = name[:-5].split("_", 2)
    h = open(os.path.join(d, name), encoding="utf-8", errors="replace").read()
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    h = re.sub(r"<br\s*/?>|</p>|</li>|</div>", "\n", h)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in html.unescape(re.sub(r"<[^>]+>", "\n", h)).splitlines()]
    lines = [ln for ln in lines if ln]
    k = next((n for n, ln in enumerate(lines) if ln == "Veröffentlicht am"), None)
    published = lines[k + 1][:10] if k is not None and k + 1 < len(lines) else ""
    try:
        i = next(n for n, ln in enumerate(lines) if ln.startswith("Inhaltsverzeichnis |"))
    except StopIteration:
        print(f"{year}\t{issue}\t{kind}\t{published}\t0\t(목차 없음)")
        continue
    titles = []
    for ln in lines[i + 1:]:
        if ln.startswith(("Sächsisches Gesetz- und Verordnungsblatt (SächsGVBl.)", "Zusatzinformation", "Titelangaben",
                          "Mehr Informationen", "Bewertungen")) or "Jahresinhaltsverzeichnis" in ln:
            break
        titles.append(ln)
    if not titles:
        print(f"{year}\t{issue}\t{kind}\t{published}\t0\t(목차 없음)")
    for n, t in enumerate(titles, 1):
        print(f"{year}\t{issue}\t{kind}\t{published}\t{n}\t{t}")
