"""독일·라인란트팔츠 주 공휴일 규칙 — 주 전역 법정 공휴일.

근거 법령은 Landesgesetz über den Schutz der Sonn- und Feiertage (Feiertagsgesetz –
LFtG) vom 15. Juli 1970 (GVBl. S. 225, BS 113-10) § 2 Abs. 1 Nr. 1~10 이다 — 번호
열거 10 호. Nr. 10 "der 1. und 2. Weihnachtstag (25. und 26. Dezember)" 은 이름 있는
두 공휴일을 한 번호에 병렬로 묶은 것이라 항목은 11 건이다. 조사 기록은
/tmp/report_rp_gesetz_chain.md (관문 구조: 접근 경로 실측 → 개정 체인 마감).

verified 는 11 건 전건 false 다 — true 항목이 없는 첫 주 피드. 현행 § 2 Abs. 1 자구는
1970 원법에 1990-10-05(GVBl. S. 289)·1993-06-08(S. 314)·1994-12-20(S. 474) 개정이 얹힌
것인데, GVBl. Rheinland-Pfalz 의 디지털 공개는 2004 년부터(gvbl.rlp.de 온라인 아카이브,
2026-07-01 부터 verkuendung.rlp.de)라 넷 다 공포본을 읽지 못했다. 2004~2026 전 호
스캔(아카이브 579 + 플랫폼 11 PDF)으로 확인된 LFtG 개정은 2009-10-27(GVBl. S. 358 Art. 2)
하나뿐이고 § 10 만 바꿔 어떤 항목의 자구도 세우지 못한다. 현행 자구는 2차 소스 넷
(datumsrechner.de·Bistum Speyer OVB 2007/08 Beilage·kirchenrecht-ekhn.de·
kirchenrecht-evpfalz.de)의 글자 단위 일치에 의존하고, source_todo 가 공포본으로 닫힌
구간과 [2차] 로만 닫힌 것을 나눠 적는다.

연 단위 구성은 고정 6 + 부활절 이동 5 = 11 건이다. 3. Oktober 는 조문 열거 안에
있다(Nr. 8) — BW 처럼 rules/de 를 미러하지 않고 조문이 주근거이며 Einigungsvertrag
Art. 2 Abs. 2 는 DESCRIPTION 부기다. land 항목은 Nr. 7 Fronleichnamstag·Nr. 9
Allerheiligentag 둘. token 은 전부 기존 확립값(공통 9 종 + de_bw·de_by·de_nw 의
fronleichnam·allerheiligen) — 신규 명명 0. § 2 Abs. 2 의 일회성 수권은 있으나 수록
항목은 없다(유일한 발동 2015 LVO 는 2017-10-31, 발행 하한 밖). 대체공휴일(이동) 규칙
없음.

조문 인용은 "§ 2 Abs. 1 Nr. n '자구'" 형식이다. SUMMARY 는 관사 "der" 와 괄호 날짜만
정리한 것(Fronleichnamstag·Allerheiligentag·Tag Christi Himmelfahrt — BW 표기와 갈리는
것은 의도)이고 원문은 source 에 남긴다.

rules/de/ 를 import 하지 않는다. 표를 따로 둔다 — 전국 공통 9 건이 RP 에서도
유효하다는 것은 이 표가 그 사실을 담고 있어서이지 de 의 표를 물려받아서가 아니다.
두 표가 갈리면 tests/test_de_rp_feed.py 의 상위집합 테스트가 잡고, 주 피드끼리
갈리면 tests/test_de_be_feed.py 의 교집합 == de.ics 테스트(아홉 주)가 잡는다.

    solar_holidays.yaml       고정 날짜 6 건
    easter_holidays.yaml      부활절 기준 오프셋 5 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de_rp/feed.py).
"""
