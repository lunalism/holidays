# ruff: noqa
"""corpus.tsv 와 flagged_pages.txt 를 만든다.

사용: python -I corpus.py <listing.tsv> <fetch.log> <pdf-dir> <extract_stats.tsv> <corpus.tsv> <flagged_pages.txt>
corpus.tsv 열: year, nr, date, url, http_status, bytes, sha256, pages, chars
  - year >= 2020 인 목록 항목 전부. PDF 링크가 없는 항목(철회·폐지)도 한 줄을 두고 url 이하를 비운다.
  - http_status·bytes 는 fetch.log 에서 그 URL 의 마지막 줄.
flagged_pages.txt: 비공백 문자가 200 개 미만인 쪽 — file, page, 비공백 문자 수.
"""
import csv
import hashlib
import pathlib
import sys

BASE = "https://www.gesetzblatt.bremen.de"
listing, log, pdfdir, stats, out_corpus, out_flag = sys.argv[1:7]
pdfdir = pathlib.Path(pdfdir)

last = {}
for line in open(log, encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) == 6:
        last[f[1]] = f

st = {r["file"]: r for r in csv.DictReader(open(stats, encoding="utf-8"), delimiter="\t")}

rows, flagged = [], []
for r in csv.DictReader(open(listing, encoding="utf-8"), delimiter="\t"):
    if r["year"] < "2020":
        continue
    nr = int(r["nr"])
    if not r["href"].endswith(".pdf"):
        rows.append([r["year"], str(nr), r["date"], "", "", "", "", "", "", r["title"]])
        continue
    url = BASE + r["href"]
    name = f"{r['year']}_{nr:03d}.pdf"
    p = pdfdir / name
    sha = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else ""
    lg = last.get(url, [""] * 6)
    s = st.get(name, {})
    rows.append([r["year"], str(nr), r["date"], url, lg[2], lg[4], sha,
                 s.get("pages", ""), s.get("chars", ""), s.get("error", "")])
    for i, n in enumerate((s.get("nonws_per_page") or "").split(","), 1):
        if n != "" and int(n) < 200:
            flagged.append(f"{name}\t{i}\t{n}")

rows.sort(key=lambda x: (x[0], int(x[1])))
with open(out_corpus, "w", encoding="utf-8") as f:
    f.write("year\tnr\tdate\turl\thttp_status\tbytes\tsha256\tpages\tchars\tnote\n")
    for x in rows:
        f.write("\t".join(x) + "\n")
with open(out_flag, "w", encoding="utf-8") as f:
    f.write("file\tpage\tnonws_chars\n")
    for x in flagged:
        f.write(x + "\n")
print(f"rows {len(rows)} flagged {len(flagged)}")
