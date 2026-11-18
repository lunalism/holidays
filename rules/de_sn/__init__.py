"""독일·작센 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über Sonn- und Feiertage im Freistaat Sachsen (SächsSFG) vom 10. November 1992
(SächsGVBl. 1992 Nr. 35 S. 536) § 1 Abs. 1 이다 — 번호 없는 열거 12 건 중 지정 지역만의
Fronleichnam(7번째)을 뺀 11 건. 현행 자구는 REVOSax 통합본(「Fassung gültig ab: 7. Mai 2025」)으로
읽었다. 통합본은 2차 출처다.

Buß- und Bettag(10번째)는 조문이 이름만 든다. 날짜는 Totensonntag − 4 일이다 — Totensonntag 는
같은 법 § 2 의 「letzter Sonntag vor dem 1. Advent」 이고, 「am letzten Mittwoch vor dem
Totensonntag」 은 작센 주의회 청원위원회 보고서 2023 의 문장이다(S2·S3). 오프셋 필드
totensonntag_offset 은 이 주의 로더만 받는다(rules/de_sn/feed.py). key buss_und_bettag 는 사람이
승인했다(2026-11-18, S1).

verified 는 11 건 전부 false 다 — 1992 원법은 온라인에 없고, § 1 Abs. 1 을 바꾼 2002 개정(SächsGVBl.
2002 Nr. 9)은 관보 발행사의 유료 보관 상품 안에만 있다(S4). 일회성 지정을 수권하는 조항은 없고,
2020 이후 지정 확인의 범위와 공백은 solar_holidays.yaml 머리 주석에 있다(S5).

연 단위 구성은 고정 6 + 부활절 이동 4 + Totensonntag 기준 1 = 11 건이다. 전국 공통 9 건에
Reformationsfest(10. 31.)와 Buß- und Bettag 가 더해진다. Fronleichnam·§ 2 Gedenk- und Trauertage
(8. Mai 포함)·§ 2a örtlicher Gedenktag·§ 3 religiöse Feiertage 는 싣지 않는다(S7). 대체공휴일(이동)
규칙은 없다.

rules/de/ 의 표를 물려받지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 SN 에서도 유효하다는
것은 이 표가 그 사실을 담고 있어서다. 두 표가 갈리면 tests/test_de_sn_feed.py 의 상위집합
테스트가 잡고, 주 피드끼리 갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트
(rules/ 스캔)가 잡는다.

    solar_holidays.yaml          고정 날짜 6 건
    easter_holidays.yaml         부활절 기준 오프셋 4 건
    totensonntag_holidays.yaml   Totensonntag 기준 오프셋 1 건
부활절은 python-dateutil 의 easter() 가, Totensonntag 는 rules/de_sn/feed.py 가 계산한다.
"""
