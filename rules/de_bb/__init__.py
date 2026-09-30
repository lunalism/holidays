"""독일·브란덴부르크 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über die Sonn- und Feiertage (Feiertagsgesetz - FTG) vom 21. März 1991
(GVBl. I S. 44) § 2 Abs. 1 이다 — 번호 없는 열거 12 건. 현행 자구는 BRAVORS 통합본
(zuletzt geändert durch Gesetz vom 30. April 2015)으로 읽었다. 통합본은 2차 출처다.

verified 는 12 건 전건 false 다. § 2 Abs. 1 자구는 1991 원법과 1994-12-19 개정
(GVBl. I S. 514, 포털 기재 대상 §§ 1, 2, 4, 5, 7-12)에 의존하는데, 두 호 모두 온라인
공포본을 찾지 못했다 — BRAVORS 의 관보 목록은 1994 년에 Teil I Nr. 12·26 만 PDF 로 두고
1991 년 목록은 없다(2026-09-30). 2015 개정(GVBl. I/15 Nr. 13)은 § 2 Abs. 2(8. Mai
기념일)만 바꿨다. source_todo 가 그 경계와 잔존 경로를 적는다(HH·NI·RP 전례).

연 단위 구성은 고정 6 + 부활절 이동 6 = 12 건이다. 전국 공통 9 건에 Ostersonntag(+0)·
Pfingstsonntag(+49)·Reformationsfest(10. 31.)가 더해진다. 두 일요일의 key(ostersonntag·
pfingstsonntag)는 이 피드에서 처음 쓰는 것이고 사람이 승인했다. Reformationsfest 는 기존
key reformationstag 를 쓴다(token 은 개념 식별자, SUMMARY 가 조문 표기를 든다). § 2 Abs. 2
의 Gedenk- und Trauertage 와 Abs. 4 의 종교 축일은 공휴일이 아니라 싣지 않는다. Abs. 3 의
일회성 지정 수권은 있으나 발행 범위 안의 지정 명령을 찾지 못했다(solar_holidays.yaml 머리
주석). 대체공휴일(이동) 규칙은 없다.

§ 2 Abs. 1 에 번호가 없어 조문 인용은 "§ 2 Abs. 1, 열거 n번째 '자구'" 로 지시한다(BW
전례). SUMMARY 는 관사와 괄호만 뺀 조문 표기이고 원문은 source 에 남긴다.

rules/de/ 의 표를 물려받지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 BB 에서도 유효하다는
것은 이 표가 그 사실을 담고 있어서다. 두 표가 갈리면 tests/test_de_bb_feed.py 의 상위집합
테스트가 잡고, 주 피드끼리 갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트
(rules/ 스캔)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 6 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_bb/feed.py).
"""
