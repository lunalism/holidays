"""독일·메클렌부르크포어포메른 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über Sonn- und Feiertage (Feiertagsgesetz Mecklenburg-Vorpommern - FTG M-V -)
in der Fassung der Bekanntmachung vom 8. März 2002 (GVOBl. M-V 2002, 145) § 2 Abs. 1 이다 —
Nr. 1–11 의 11 건. 현행 자구는 공식 법령 포털 Landesrecht M-V 의 § 2 조문 단위 문서
(jlr-NNLMV00007A2FNN00000000003, 「Fassung vom: 07.07.2022 / Gültig ab: 13.07.2022」)로 읽었다.
그것을 전 항목 자구의 공식 현행 조문으로 삼은 것은 사람의 결정이다(M1).

Frauentag(Nr. 2)는 effective_from: 2022-07-13 부터다 — 포털의 「Gültig ab: 13.07.2022」 문면
그대로(M2). 그래서 2020–2022 는 10 건, 2023 부터 11 건이다. effective_from 은 kr 의 항목별
effective_from 과 같은 뜻(날짜, 포함 경계)이고, 이 주의 로더만 그것을 받으며 모르는 필드를
거부한다(rules/de_mv/feed.py, M6).

verified 는 11 건 전부 false 다 — 공포본(2002 재공포본, 개정법 GVOBl. M-V 2022 Nr. 31)을 해시와
함께 받지 못했다. GVOBl. M-V 2014–2025 는 이제 온라인에 없고 관보 화면은 E-Mail 요청을 안내한다
(M3). E-Mail 요청은 하지 않는다(M4). § 2 Abs. 3 의 일회성 지정은 포털 검색으로만 확인했다 —
범위는 solar_holidays.yaml 머리 주석.

연 단위 구성은 고정 7 + 부활절 이동 4 = 11 건이다. 전국 공통 9 건에 Frauentag(3. 8.)와
Reformationstag(10. 31.)가 더해진다. key 는 전부 기존 확립값이다. § 2 Abs. 2 의 Gedenk- und
Trauertage(8. Mai 포함)와 § 7 의 kirchliche Feiertage 는 공휴일이 아니라 싣지 않는다. 대체공휴일
(이동) 규칙은 없다.

rules/de/ 의 표를 물려받지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 MV 에서도 유효하다는
것은 이 표가 그 사실을 담고 있어서다. 두 표가 갈리면 tests/test_de_mv_feed.py 의 상위집합
테스트가 잡고, 주 피드끼리 갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트
(rules/ 스캔)가 잡는다.

    solar_holidays.yaml       고정 날짜 7 건(그중 frauentag 에 effective_from)
    easter_holidays.yaml      부활절 기준 오프셋 4 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_mv/feed.py).
"""
