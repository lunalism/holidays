"""독일·슐레스비히홀슈타인 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über Sonn- und Feiertage (SFTG) vom 28. Juni 2004 (GVOBl.
Schl.-H. S. 213) § 2 Abs. 1 Nr. 1~10 이다. 조사 기록은 /tmp/report_sh_gesetz_chain.md
(개정 체인 양방향 마감).

공포본 두 벌을 직접 읽었다 — 제정 공포본 GVOBl. Schl.-H. 2004 Nr. 8 (15.07.2004)
S. 213 과 유일한 § 2 개정 공포본 2018 Nr. 6 (29.03.2018) S. 69. 둘 다
Verkündungsportal Schleswig-Holstein 의 연도판 PDF 이고 sha256 을 각 항목 source 에
남겼다. 그래서 10 건 전부 verified: true 다 — 이 레포의 첫 전건 true 주 피드.
개정 체인: 2004 제정 → 2005-02-01 Art. 11(§ 9 자구) → 2016-02-15(§ 6 Abs. 1) →
2018-03-21(§ 2 Abs. 1 Nr. 8 삽입·재번호) → 2026/81 까지 무개정. § 2 를 건드린
개정은 2018 하나뿐이다.

연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건이다. 전국 공통 9 건에 Nr. 8
"31. Oktober - Reformationstag -" 하나가 더해진다. token 은 전부 기존 확립값
(공통 9 종 + de_hh 의 reformationstag) — 신규 명명 0. § 2 Abs. 2 는 Landesregierung
이 명령으로 일회성 공휴일을 정할 수 있는 수권인데 2019~2026 공포본에 그런 명령이
없어 일회성 표는 두지 않는다. 대체공휴일(이동) 규칙도 없다.

SUMMARY 는 조문 표기에서 날짜부와 대시를 뺀 것이다(de.ics 의 전례). Nr. 7 → "Tag
der Deutschen Einheit", Nr. 8 → "Reformationstag". HH 의 Nr. 8 이 "31. Oktober" 인
것과 다른 이유는 SH 조문에 통칭이 들어 있어서다 — 각 피드는 자기 조문의 표기를
쓴다. 원문은 source 에 그대로 남긴다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 SH 에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_sh_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(여섯 주)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 4 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_sh/feed.py).
"""
