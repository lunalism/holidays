"""독일·노르트라인베스트팔렌 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über die Sonn- und Feiertage (Feiertagsgesetz NW) in der Fassung
der Bekanntmachung vom 23. April 1989 (GV. NW. S. 222) § 2 Abs. 1 Nr. 1~11 이다.
조사 기록은 /tmp/report_de_laender.md 의 NW 절.

공식 경로는 전멸이다 — recht.nrw.de 는 검색 SPA 로 딥링크를 무시하고, 관보 PDF
(GV_Archiv 4122-xmmgvb8919.pdf)는 JBIG2 스캔이라 텍스트가 없다. 조문은 비공식 둘로
읽었다: lexmea(전문, "Imported 21.10.2025") ↔ IHK Köln(요약 열거). 기준 텍스트는
lexmea 이고, 자구가 다른 호(Nr. 7 괄호, Nr. 8 어순, Nr. 10/11 괄호 날짜)는 해당
항목 source 에 차이를 기록했다. 그래서 11 건 전부 verified: false 다(BE 기저 9 건과
같은 관례, source_todo 에 공식 경로).

연 단위 구성은 고정 6 + 부활절 이동 5 = 11 건이다. 전국 공통 9 건에 Nr. 7
Fronleichnamstag 와 Nr. 9 Allerheiligentag 가 더해진다. token 은 전부 기존 확립값
(공통 9 종 + fronleichnam + allerheiligen) — 신규 명명 0. § 2 에 지자체·집단 한정
항목이 없고 일회성도 없다. 대체공휴일(이동) 규칙도 없다.

SUMMARY 는 조문 표기에서 정관사·서술부·괄호를 뺀 것이다(de.ics 의 전례). Nr. 4 의
"als Tag des Bekenntnisses …", Nr. 7·9 의 괄호 정의, Nr. 8 의 "der 3. Oktober als"
가 빠진다 — 원문은 source 에 그대로 남긴다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 NW 에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_nw_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(다섯 주)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 5 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_nw/feed.py).
"""
