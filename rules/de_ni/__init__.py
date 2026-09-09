"""독일·니더작센 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Niedersächsisches Gesetz über die Feiertage (NFeiertagsG) in der Fassung
vom 7. März 1995 (Nds. GVBl. S. 50) § 2 Abs. 1 Buchst. a)~j) 이다 — 알파벳 호 열거
10 건. 조사 기록은 /tmp/report_ni_gesetz_chain.md (관문 구조: 접근 경로 실측 →
개정 체인 마감).

verified 는 혼합이다(HH 구도). Nds. GVBl. 의 디지털 공개는 2004 년부터(니더작센 포털
호별 PDF)이고 2024 년부터는 verkuendung-niedersachsen.de 가 정본이다. § 2 를 건드린
개정은 2013 S. 131(2017 한시 Satz 2, 실효)과 2018 Nr. 7 S. 122(Buchst. h 삽입,
h·i → i·j, Satz 2 삭제)뿐이고 둘 다 공포본으로 읽었다 — 2004~2023 전 호 671 건과
2024~2026 Nr. 76 까지의 플랫폼 목록·전문검색으로 순방향도 닫았다. 그래서 Buchst. h
(Reformationstag)만 true 다. 나머지 아홉의 자구는 1995 Neufassung(S. 50)에 의존하고
그 공포본과 2002 개정(S. 17)은 디지털 부재라 false + source_todo(실측 경계 서술).

연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건이다. 3. Oktober 는 조문 열거 안에
있다(Buchst. g) — BW 처럼 rules/de 를 미러하지 않고 조문이 주근거이며 Einigungsvertrag
Art. 2 Abs. 2 는 DESCRIPTION 부기다. token 은 전부 기존 확립값(공통 9 종 + de_hh·de_sh
의 reformationstag) — 신규 명명 0. 일회성 없음, 대체공휴일(이동) 규칙 없음.

조문 인용은 "§ 2 Abs. 1 Buchst. x '자구'" 형식이다(공포본도 "Buchstabe h" 로 지시).
재번호 항목 i·j 는 자구(1995)와 번호(2018)를 나눠 적는다. SUMMARY 는 "der …, als …"
서술부를 정리한 것이고 원문은 source 에 남긴다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 NI 에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_ni_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(여덟 주)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 4 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_ni/feed.py).
"""
