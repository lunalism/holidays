"""p3_results.tsv 의 「Feiertag」(분류 Gesetze/Verordnungen) 87 건 전부에 기간·판정·근거를 붙인다.

사용: python3 p3_classify.py p3_results.tsv > p3_classified.tsv
판정은 조사자(CC)가 각 결과의 제목(titleList)과 부제(subtitleList)만 읽고 정한 것이다.
문서 본문은 열지 않았다.
열: n, doc_id, date, 기간(2020 이후 / 날짜 없음 / 2020 전), 제목, 부제, 판정, 판정 근거.
판정 「일회성 선언 아님」 은 그 제목·부제가 주 전역 일회성 공휴일이나 Arbeitsruhe 날을 선언하는
규범의 것이 아니라는 뜻이다. 2020 전 날짜의 결과도 판정한다 — 결과 날짜는 판(Fassung)의
날짜라, 2020 의 날을 2019 에 선언한 규범이 있다면 2019 로 나온다.
"""
import datetime as dt
import sys

SKIP = ("-", "gültig ab", "Textnachweis")
rows = [ln.rstrip("\n").split("\t") for ln in open(sys.argv[1], encoding="utf-8")][1:]
print("n\tdoc_id\tdate\tperiod\ttitle\tsubtitle\tverdict\tbasis")
for r in rows:
    query, _label, _rep, n, doc_id, date, _cat, title, subtitle = r
    if query != "Feiertag":
        continue
    try:
        d = dt.datetime.strptime(date, "%d.%m.%Y").date()
        period = "2020 이후" if d >= dt.date(2020, 1, 1) else "2020 전"
    except ValueError:
        period = "날짜 없음"
    parts = [p.strip() for p in subtitle.split("|")]
    parts = [p for p in parts if p and p != "Landesnorm Mecklenburg-Vorpommern"]
    norm = next((p for p in parts if not p.startswith(SKIP)), title)
    if "FFN" in title:
        basis = (f"제목·부제만 읽음: 「{title}」 — Fundstellennachweis(법령 색인)의 절 "
                 f"「{norm}」 이다. 선언 규범이 아니다")
    else:
        basis = (f"제목·부제만 읽음: 「{title}」 은 「{norm}」 의 조문·부속이다 — 제목이 주 전역 "
                 "일회성 공휴일·Arbeitsruhe 날의 선언이 아니다")
    print("\t".join([n, doc_id, date, period, title, subtitle, "일회성 선언 아님", basis]))
