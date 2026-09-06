"""독일·함부르크 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über Sonntage, Feiertage, Gedenktage und Trauertage
(Feiertagsgesetz) vom 16. Oktober 1953 § 1 Nr. 1~10 이다. 조사 기록은
/tmp/report_de_laender.md 의 HH 절.

공식 포털(landesrecht-hamburg.de)은 JS 셸만 돌아와 열람하지 못했다. 조문 원문은
비공식 현행판(umwelt-online, Stand 28.08.2023)으로 읽었고, 2018 개정분(Nr. 8
"31. Oktober" 삽입)만 의회 문서 Drucksache 21/12153 로 봤다 — 의결 전 안이라
공포 관보(HmbGVBl. 2018 S. 63)는 미열람. 그래서 10 건 전부 verified: false 다
(BE 기저 9 건과 같은 관례, source_todo 에 공식 경로).

연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건이다. 전국 공통 9 건에 Nr. 8
"31. Oktober" 하나가 더해진다 — 조문에는 이름 없이 날짜만 있다. SUMMARY 는 그
표기 그대로 싣고, token 은 통칭 reformationstag 를 쓴다(key charset 이 날짜형을
허용하지 않아 통칭을 식별자로 채택, 승인 완료). 이 피드의 신규 명명은 이 하나다.
§ 2 Abs. 1 Nr. 1 은 Senat 이 명령으로 일회성 Sonderfeiertag 을 정할 수 있는
수권인데 조사에서 확인된 명령이 없어 일회성 표는 두지 않는다. 대체공휴일(이동)
규칙도 없다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 함부르크에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_hh_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(BE∩BY∩HE∩HH)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 4 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_hh/feed.py).
"""
