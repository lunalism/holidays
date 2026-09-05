"""독일·베를린 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über die Sonn- und Feiertage (Berlin) vom 28. Oktober 1954
(GVBl. S. 615) § 1 Abs. 1 이다. 조사 기록은 /tmp/report_de_laender.md 의 BE 절.

연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건이고, 조문에 연도가 박힌 일회성
항목이 해마다 더해진다(designated_holidays.yaml). 지자체·학교 한정 항목은
법령에 없다. 대체공휴일(이동) 규칙도 없다 — § 1 에 이동 조항이 없고,
feiertage-api 2026(03-08 일요일) 실측에서 보상 휴일 0 건이다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 베를린에서도
유효하다는 것은 이 표의 내용이 그 사실을 담고 있어서이지, de 의 표를 물려받아서가
아니다. 두 표가 갈리면 tests/test_de_be_feed.py 의 상위집합 테스트가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 4 건
    designated_holidays.yaml  일회성(연도 박힘) 3 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_be/feed.py).
"""
