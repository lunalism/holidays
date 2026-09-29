"""독일·노르트라인베스트팔렌 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Gesetz über die Sonn- und Feiertage (Feiertagsgesetz NW) in der Fassung
der Bekanntmachung vom 23. April 1989 (GV. NW. S. 222) § 2 Abs. 1 Nr. 1~11 이다.
조사 기록은 docs/research/report_nw_feiertagsgesetz_chain.md.

조문은 공포본 세 호로 읽었다 — 1989 Neufassung(GV. NW. 1989 Nr. 19 S. 222), 1991
개정(1991 Nr. 19 S. 200, Nr. 8 을 3. Oktober 로), 1994 개정(1994 Nr. 88 S. 1114,
Nr. 10 Buß- und Bettag 삭제·재번호). 세 PDF 는 recht.nrw.de 의 GV_Archiv 스캔본이고
결정적이라(재수령 sha256 동일) 파일 sha256 으로 고정했다. 1989·1991 판은 JBIG2
이미지에 OCR 텍스트층이 있고 1994 판은 CCITT G4 에 텍스트층이 없다 — 판독 근거는
세 판 모두 면 이미지이고 OCR 은 교차 확인에만 썼다. 11 건 전부 verified: true 다.
서지·체인의 닫힘·비공식 현행판(lexmea·IHK Köln)과의 자구 차이는
solar_holidays.yaml 머리 주석에 있다.

연 단위 구성은 고정 6 + 부활절 이동 5 = 11 건이다. 전국 공통 9 건에 Nr. 7
Fronleichnamstag 와 Nr. 9 Allerheiligentag 가 더해진다. token 은 전부 기존 확립값
(공통 9 종 + fronleichnam + allerheiligen) — 신규 명명 0. § 2 에 지자체·집단 한정
항목이 없다. 일회성은 2017-10-31(GV. NRW. 2015 S. 496) 하나가 있었으나 피드 범위
(2020~) 밖이다. 대체공휴일(이동) 규칙도 없다.

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
