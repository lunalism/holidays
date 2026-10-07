"""독일·브레멘 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über die Sonn-, Gedenk- und Feiertage vom 12. November 1954
(Brem.GBl. S. 115) § 2 Abs. 1 이다 — Buchst. a)–j) 10 건. 현행 자구는 Transparenzportal
Bremen 통합본(Inkrafttreten 14.03.2020 판, gsid 145882)으로 읽었다. 통합본은 2차 출처다.
현행 통합본(gsid 296390)은 PDF 요청이 HTTP 500 이라 받지 못했다.

2020-03-14 판이 지금도 현행이라는 근거는 Brem.GBl. 2020 Nr. 1 – 2026 Nr. 102 의 텍스트층
전문 검색(§ 2 Abs. 1 개정 0 건)과 텍스트층이 부족한 쪽 741 개의 계정(미계정 0, 그중 557 쪽은
구조 검사로만 닫은 [추론])이다. 미리 정한 판정 기준 2(검색 불가 쪽 0)는 미충족이고, 계정으로
대신한 것은 사람의 결정이다. 조사 기록은 docs/research/report_hb_fulltext.md·
report_hb_flagged.md·report_hb_structure.md·report_hb_read.md 와 같은 이름의 폴더.

verified 는 reformationstag 1 건만 true 다 — Buchst. j 의 현행 문언을 Brem.GBl. 2018 Nr. 63
S. 302 공포본으로 읽었다. a–i 9 건은 1954 원법과 2013 이전 개정에 의존하는데 브레멘 관보
포털의 공개가 2013 년부터라 공포본을 찾지 못했다 — false + source_todo(HH·NI·RP·BB 전례).

연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건이다. 전국 공통 9 건에 Reformationstag(10. 31.)
가 더해진다. key 는 전부 기존 확립값이다. § 7a 의 8. Mai(Gedenktag)와 § 8 의 종교 축일은
공휴일이 아니라 싣지 않는다. 대체공휴일(이동) 규칙은 없다.

rules/de/ 의 표를 물려받지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 HB 에서도 유효하다는
것은 이 표가 그 사실을 담고 있어서다. 두 표가 갈리면 tests/test_de_hb_feed.py 의 상위집합
테스트가 잡고, 주 피드끼리 갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트
(rules/ 스캔)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 4 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_hb/feed.py).
"""
