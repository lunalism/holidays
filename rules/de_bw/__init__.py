"""독일·바덴뷔르템베르크 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über die Sonntage und Feiertage (Feiertagsgesetz – FTG) in der
Fassung vom 8. Mai 1995 (GBl. S. 450) § 1 이다 — 호 번호 없는 열거 11 건. 조사 기록은
/tmp/report_bw_gesetz_chain.md (개정 체인 양방향 마감).

공포본을 직접 읽었다 — 현행 § 1 자구의 인쇄본인 Neufassung(GBl. 1995 Nr. 17,
30.06.1995, S. 450)과 그 입법 뿌리 세 벌(1970 Neufassung GBl. 1971 S. 1 / 1994-12-12
개정 GBl. S. 631 / 1995-03-23 개정 GBl. S. 293). 전부 Landtag Baden-Württemberg 의
호별 PDF 이고 sha256 은 YAML 머리 주석에 있다. § 1 은 1995 이후 무개정(2014 § 1a
한시, 2015 §§ 8·10·11·13 만; 1995~2013 전 호·2016~2023 전 호·2024~ 전자 관보 GBl.
2026 Nr. 79 까지 실측). 그래서 § 1 의 11 건은 verified: true 다.

연 단위 구성은 고정 7 + 부활절 이동 5 = 12 건이다. § 1 의 11 건에 § 1 밖의
3. Oktober 를 더한다 — BW 조문은 3. Oktober 를 열거하지 않고 § 7 Abs. 2 등에서
전제만 하며, 근거는 Einigungsvertrag Art. 2 Abs. 2(연방법)다. 그 항목은 rules/de 의
같은 항목을 미러한다(verified true). 전국 공통 9 건에 Erscheinungsfest(1. 6.)·
Fronleichnam(+60)·Allerheiligen(1. 11.)이 더해진다. token 은 전부 기존 확립값(공통
9 종 + de_by 의 heilige_drei_koenige·fronleichnam·allerheiligen) — 신규 명명 0.
§ 1a(Reformationsfest 2017 한시)는 실효해 싣지 않는다. 대체공휴일(이동) 규칙도 없다.

§ 1 에 호 번호가 없어 조문 인용은 "§ 1, 열거 n번째" 로 지시한다(de_by 전례). SUMMARY
는 조문 표기에서 괄호 날짜만 뺀 것이다 — "Erscheinungsfest (6. Januar)" →
"Erscheinungsfest", "Allerheiligen (1. November)" → "Allerheiligen". 원문은 source 에
그대로 남긴다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 BW 에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_bw_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(일곱 주)가 잡는다.
3. Oktober 를 빼면 tests/test_de_scope.py 의 교차 검증(bundesweit key 집합 == de 9 key)
이 먼저 깨진다 — 의도된 안전망이다.

    solar_holidays.yaml       고정 날짜 7 건
    easter_holidays.yaml      부활절 기준 오프셋 5 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_bw/feed.py).
"""
