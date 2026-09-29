"""독일·헤센 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Hessisches Feiertagsgesetz (HFeiertagsG) vom 17. September 1952
(GVBl. S. 145), Neufassung vom 29. Dezember 1971 (GVBl. I S. 344) § 1 Abs. 1 이다.
조사 기록은 docs/research/report_he_be_gazette_access.md.

조문은 공포본 두 호로 읽었다 — 1971 Neufassung(GVBl. 1971 I Nr. 36 S. 343, § 1 은
S. 344)과 1994 Fünftes Änderungsgesetz(GVBl. 1994 I Nr. 25 S. 596, Nr. 8 새 문언·
Nr. 9·10 을 새 Nr. 9 로). 두 PDF 는 헤센 주의회 서버(starweb.hessen.de)의 스캔본이고
결정적이라(재수령 sha256 동일) 파일 sha256 으로 고정했다. 공식 통합본 포털
(rv.hessenrecht.hessen.de)은 2026-09-29 에도 JS 셸만 돌려주고 그 API 는 인증을
요구한다 — 근거로 쓰지 않았다. 10 건 전부 verified: true 다. 서지·체인의 닫힘·
비공식 사본과의 차이는 solar_holidays.yaml 머리 주석에 있다.

연 단위 구성은 고정 5 + 부활절 이동 5 = 10 건이다. § 1 Abs. 1 Nr. 1~9 의 열거에서
Nr. 9 "der 1. und 2. Weihnachtstag" 가 한 호에 이틀이라 항목은 열이다. 전국 공통
9 건에 Fronleichnamstag(Nr. 7) 하나가 더해진다. 지자체·학교 한정 항목은 § 1 에
없다(시행규칙의 학생 수업 면제일은 공휴일이 아니다). § 2 는 주 정부가 명령으로
일회성 공휴일을 정할 수 있는 수권이다 — 그 명령으로 2017-10-31(GVBl. 2013 S. 566)이
있었으나 피드 범위(2020~) 밖이라 일회성 표는 두지 않는다. 대체공휴일(이동) 규칙도
없다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 헤센에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_he_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(BE∩BY∩HE)가 잡는다.

    solar_holidays.yaml       고정 날짜 5 건
    easter_holidays.yaml      부활절 기준 오프셋 5 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_he/feed.py).
"""
