# ruff: noqa
"""판독 메모(file, page, 내용, finding, 재렌더 dpi)와 부분 판독 불가 목록을 합쳐 r_reading.tsv 를 만든다.
판독 자체는 조사자가 렌더 이미지를 보고 한 것이다(시각 판독). 이 스크립트는 기록을 표로 옮길 뿐이다.

사용: python -I build_reading.py <read_set.tsv> <notes.tsv> > r_reading.tsv
"""
import csv
import sys

PARTLY = {
    ("2020_160.pdf", "8"): "지도 안의 거리 이름 글자(회색 바탕의 작은 세로·가로 라벨) — 300 dpi 에서도 읽히지 않음",
    ("2021_045.pdf", "2"): "바탕 지형도의 작은 라벨(공원 안 길 이름, 세로 하천 이름 일부) — 300 dpi 에서도 일부 읽히지 않음",
    ("2022_092.pdf", "13"): "바탕 지형도의 작은 지명·도로 라벨 — 300 dpi 에서도 읽히지 않음",
    ("2024_039.pdf", "2"): "옛 시가도 래스터의 작은 라벨(빗금 구역 안 건물·거리 이름) — 300 dpi 에서도 일부 읽히지 않음",
    ("2024_043.pdf", "2"): "2024 Nr. 39 p2 와 같은 래스터(이미지 sha256 앞 12 자 0efb97eccbc3) — 같은 영역 읽히지 않음",
    ("2026_009.pdf", "6"): "옛 시가도 래스터의 작은 라벨(빗금 구역 안) — 300 dpi 에서도 일부 읽히지 않음",
    ("2024_097.pdf", "2"): "평면도 안의 아주 작은 필지 목록(범례 옆 표)과 측량사 도장 칸 — 300 dpi 에서도 읽히지 않음",
}
SAME_RASTER = {
    ("2024_043.pdf", "3"): "래스터는 2024 Nr. 39 p3 와 같음(96143f45186b) — 그 쪽 300 dpi 타일 넷을 읽었고, 이 쪽은 오른쪽 아래 타일(서명 「Ordnungsamt Bremen」)을 따로 봄",
    ("2026_009.pdf", "7"): "래스터는 2024 Nr. 39 p3 와 같음(96143f45186b) — 그 쪽 300 dpi 타일 넷을 읽었고, 이 쪽은 오른쪽 아래 타일을 따로 봄",
}

rs = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
notes = {}
for line in open(sys.argv[2], encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    notes[(f[0], f[1])] = f
w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["file", "page", "read_reason", "dpi", "status", "unreadable_region", "visible_content",
            "finding", "transcription", "class", "basis"])
for r in rs:
    k = (r["file"], r["page"])
    n = notes[k]
    dpi = "150+300" if n[4] == "300" else "150"
    status = "partly unreadable" if k in PARTLY else "read"
    content = n[2] + ((" ; " + SAME_RASTER[k]) if k in SAME_RASTER else "")
    w.writerow([r["file"], r["page"], r["reason"], dpi, status, PARTLY.get(k, ""), content,
                "none" if n[3] == "no" else n[3], "", "", "visual reading"])
