# ruff: noqa
"""관보 목록 HTML(skip*.html)에서 호별 항목을 뽑는다.

사용: python -I parse_listing.py <html-dir> > listing.tsv
열: year, year_src, nr, date(ISO), href(목록에 적힌 그대로), link_count, title, hinweis, pages, src_file
한 항목(<li class="search-result-item">)에 링크(<a>, href 빈 것 포함)가 둘 이상이면 링크마다 한 줄을 내고 link_count 에 그 수를 적는다.
"""
import html
import pathlib
import re
import sys

ITEM = re.compile(r'<li class="search-result-item">(.*?)</li>', re.S)
LINK = re.compile(r"<a[^>]*href=['\"]([^'\"]*)['\"][^>]*>([^<]*)</a>", re.I)
DATE = re.compile(r"Veröffentlichungsdatum:</strong>\s*(\d\d)\.(\d\d)\.(\d{4})")
HINW = re.compile(r"Hinweistext:</strong>\s*(.*?)(?:<br\s*/?>|$)", re.S)
PAGES = re.compile(r"\((S\.[^)]*)\)")
# 표기가 고르지 않다: "Gesetzblatt 2025 Nr. 13", "Gesetzblatt Nr. 5"(연도 없음), "Gesetzblatt 2020 Nr: 171".
# 연도가 없으면 공개일의 연도를 쓰고 year_src 열에 "date" 라고 적는다.
TITLE = re.compile(r"Gesetzblatt\s+(?:(\d{4})\s+)?Nr[.:]\s*(\d+)(.*)")

out = []
for f in sorted(pathlib.Path(sys.argv[1]).glob("skip*.html")):
    text = f.read_text(encoding="utf-8")
    for block in ITEM.findall(text):
        links = LINK.findall(block)
        d = DATE.search(block)
        h = HINW.search(block)
        p = PAGES.search(block)
        date = f"{d.group(3)}-{d.group(2)}-{d.group(1)}" if d else ""
        hinw = " ".join(html.unescape(h.group(1)).split()) if h else ""
        pages = p.group(1) if p else ""
        for href, label in links:
            label = " ".join(html.unescape(label).split())
            m = TITLE.match(label)
            if m and m.group(1):
                year, ysrc = m.group(1), "title"
            else:
                year, ysrc = date[:4], "date"
            nr = m.group(2) if m else ""
            out.append([year, ysrc, nr, date, href, str(len(links)), label, hinw, pages, f.name])
        if not links:
            out.append([date[:4], "date", "", date, "", "0", "", hinw, pages, f.name])

print("year\tyear_src\tnr\tdate\thref\tlink_count\ttitle\thinweis\tpages\tsrc_file")
for row in out:
    print("\t".join(c.replace("\t", " ") for c in row))
