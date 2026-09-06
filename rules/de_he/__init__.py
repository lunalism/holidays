"""독일·헤센 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Hessisches Feiertagsgesetz (HFeiertagsG) vom 17. September 1952
(GVBl. S. 145), Neufassung vom 29. Dezember 1971 (GVBl. I S. 344) § 1 Abs. 1 이다.
조사 기록은 /tmp/report_de_laender.md 의 HE 절.

공식 포털(rv.hessenrecht.hessen.de)은 JS 셸만 돌아와 열람하지 못했다(curl·headless
180초·WebFetch 모두 실패). 조문 원문은 비공식 현행판(umwelt-online, Stand
28.08.2023)과 Bistum Fulda PDF 로 읽었고, 날짜는 준공식 innen.hessen.de 2026 목록과
feiertage-api 2026 HE 로 대조했다(10/10). 그래서 10 건 전부 verified: false 다 —
BE 기저 9 건과 같은 관례(source_todo 에 공식 경로를 남긴다).

연 단위 구성은 고정 5 + 부활절 이동 5 = 10 건이다. § 1 Abs. 1 Nr. 1~9 의 열거에서
Nr. 9 "der 1. und 2. Weihnachtstag" 가 한 호에 이틀이라 항목은 열이다. 전국 공통
9 건에 Fronleichnamstag(Nr. 7) 하나가 더해진다. 지자체·학교 한정 항목은 § 1 에
없다(시행규칙의 학생 수업 면제일은 공휴일이 아니다). § 2 는 주 정부가 명령으로
일회성 공휴일을 정할 수 있는 수권인데 조사에서 확인된 명령이 없어 일회성 표는
두지 않는다. 대체공휴일(이동) 규칙도 없다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 헤센에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_he_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(BE∩BY∩HE)가 잡는다.

    solar_holidays.yaml       고정 날짜 5 건
    easter_holidays.yaml      부활절 기준 오프셋 5 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_he/feed.py).
"""
