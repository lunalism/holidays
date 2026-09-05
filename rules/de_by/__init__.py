"""독일·바이에른 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über den Schutz der Sonn- und Feiertage (Feiertagsgesetz – FTG,
BayFTG) vom 21. Mai 1980 (BayRS II S. 172, BayRS 1131-3-I) Art. 1 Abs. 1 Nr. 1 이다.
공식 포털 gesetze-bayern.de(BAYERN.RECHT) 가 정적 HTML 로 원문을 그대로 돌려주어
2026-09-06 에 열람했다 — 4 주 조사에서 유일하게 공식 경로가 열린 주다.

연 단위 구성은 고정 7 + 부활절 이동 5 = 12 건이다. "im ganzen Staatsgebiet" 열거
12 건만 싣는다. 같은 조의 나머지 — Abs. 1 Nr. 2 Mariä Himmelfahrt(가톨릭 다수
지자체), Abs. 2 Friedensfest(아우크스부르크 시), Art. 4 의 Buß- und Bettag(휴교일,
공휴일 아님) — 은 주 전역이 아니라 범위 밖이다(docs/holiday_12.md §0).
일회성(designated) 항목은 아직 없다 — 사례가 확보되면 별도 PR 로 표를 더한다.
대체공휴일(이동) 규칙도 없다 — Art. 1~9 에 이동 조항이 없고, feiertage-api BY
2020–2031 실측의 일요일 겹침 연도 7 개에서 보상 휴일 0 건이다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 바이에른에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_by_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트가 잡는다.

    solar_holidays.yaml       고정 날짜 7 건
    easter_holidays.yaml      부활절 기준 오프셋 5 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_by/feed.py).
"""
