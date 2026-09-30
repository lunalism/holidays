# Saarland (SL): 공휴일 법령 조사

- 조사일: 2026-09-30 (접근 시각 UTC는 `state_SL_fetch.log` 참조)
- 요청 수: 19회 (상한 25회). 403/429 응답은 없었다. landtag-saar.de 1회는 연결 실패(000)였고 재시도하지 않았다.
- 표기: 태그가 없는 문장은 직접 관측한 내용이다. **[추론]**은 관측 결과에서 도출했거나 배경지식에 기댄 내용이다.

---

## A. 법령

**정식 명칭 (관측, 1976년 관보 원문)**
- 관보 표제는 „Gesetz Nr. 1040 über die Sonn- und Feiertage (Feiertagsgesetz – SFG)“이며 날짜는 „Vom 18. Februar 1976“이다.
- 출처는 Amtsblatt des Saarlandes 1976 Nr. 13(1976년 3월 23일), S. 213이다. 2010년 법안 Drucksache 14/266과 2015년 Gesetz Nr. 1868도 이 법을 „Feiertagsgesetz vom 18. Februar 1976 (Amtsbl. S. 213)“으로 인용한다.

**공식 법령 포털의 현행 통합본: 확보 실패 (JS 셸)**
- 포털 URL은 `https://recht.saarland.de/`이며 `/bssl/`로 리다이렉트된다. 접근일은 2026-09-30이다.
- 정적 HTML은 5,784 bytes이고 본문 대신 다음 문구만 들어 있다: „Wenn Sie diese Meldung sehen, haben Sie in Ihrem Browser kein JavaScript aktiviert.“
- 문서 딥링크 `https://recht.saarland.de/bssl/document/jlr-FeiertGSLrahmen`도 루트와 **바이트 단위로 같은** 5,784 bytes 셸을 반환했다(cmp로 확인). 정적 HTML에 „feiertag“는 0회 나온다. 딥링크 경로명은 juris 관례를 따라 추정한 것이다 **[추론]**.
- 규칙에 따라 이 경로는 **여기서 중단했다.** 헤드리스 브라우저나 API 추적은 하지 않았다.
- 참고로 통합본(konsolidierte Fassung)은 공식 포털에 있더라도 이 레포에서는 **2차 출처**다. 정본 근거는 관보(Amtsblatt)에 공포된 법률 원문이다.

**관측으로 확인한 개정 연결고리 (체인 전수 검증 아님)**
| 개정법 | 관보 | 내용 (관측 범위) |
|---|---|---|
| Gesetz vom 21. November 2007 (Nichtraucherschutz u. Änderung des Feiertagsrechts) | Amtsbl. 2008 S. 75 | 2010년 법안에 „zuletzt geändert durch“로 인용됨. 내용은 미확인 |
| Gesetz Nr. 1726 vom 18. November 2010 | Amtsbl. I S. 2587 (2015년 법이 인용) | Drucksache 14/266(PDF 확인): §2 Abs. 2·§12의 부처명 변경, §14 과태료 조항 보완, 법률 전체에 시한 부여 |
| Gesetz Nr. 1868 vom 13. Oktober 2015 | Amtsbl. I 2015 Nr. 33, S. 790 | Art. 2 Nr. 3: §16을 „Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.“로 교체해 시한을 삭제 |

- 2010년·2015년 개정은 공휴일 목록(§2 Abs. 1)을 건드리지 않았다(관측한 조문 범위 기준).
- 2010년 개정으로 SFG에 시한이 붙었고 2015년 개정이 이를 없앴다. 이 사이에 법률 자체가 실효된 공백은 없었던 것으로 보인다 **[추론]**. 어느 쪽이든 2020년 이후 효력에는 영향이 없다 **[추론]**.

---

## B. 공휴일 목록

**주의:** 현행 조문은 확보하지 못했다(A절 참조). 아래 인용은 **1976년 공포 원문 §2 Abs. 1**이다(Amtsbl. 1976 S. 214, 스캔 PDF를 렌더링해 판독). 현행 조문과 다를 수 있다.

1976년 원문 §2 Abs. 1은 „Gesetzliche Feiertage sind“로 시작한다.

| # | 원문 (1976) | 적용 범위 (1976 문언) | 현행 여부 |
|---|---|---|---|
| 1 | „der Neujahrstag“ | 주 전역 | 유지 [추론] |
| 2 | „der Karfreitag“ | 주 전역 | 유지 [추론] |
| 3 | „der Ostermontag“ | 주 전역 | 유지 [추론] |
| 4 | „der 1. Mai“ | 주 전역 | 유지 [추론] |
| 5 | „der Tag Christi Himmelfahrt“ | 주 전역 | 유지 [추론] |
| 6 | „der Pfingstmontag“ | 주 전역 | 유지 [추론] |
| 7 | „der Fronleichnamstag“ | 주 전역 | 유지 [추론] |
| 8 | „der Tag der Deutschen Einheit (17. Juni)“ | 주 전역 | **날짜가 바뀌었음.** 현재는 10월 3일로 판단한다 [추론, 배경지식: 1990년 통일조약. SL 조문에서 미관측] |
| 9 | „der Mariä Himmelfahrtstag (15. August)“ | 주 전역 (지역 한정 문언 없음) | 유지 [추론] |
| 10 | „der Allerheiligentag (1. November)“ | 주 전역 | 유지 [추론] |
| 11 | „der Buß- und Bettag“ | 주 전역 | **폐지된 것으로 판단** [추론, 배경지식: 1995년 장기요양보험(Pflegeversicherung) 재원 마련을 위해 작센 외 모든 주에서 폐지. SL 개정법은 미관측] |
| 12 | „der 1. Weihnachtstag (25. Dezember)“ | 주 전역 | 유지 [추론] |
| 13 | „der 2. Weihnachtstag (26. Dezember)“ | 주 전역 | 유지 [추론] |

- **지역·집단 한정 항목:** 1976년 §2 Abs. 1에는 기초자치단체·지역·집단으로 한정하는 문언이 없다. 따라서 „범위 밖“으로 제외할 항목은 **0건**이다(1976 원문 기준). 현행 조문에서 한정 항목이 추가됐는지는 확인하지 못했다.
- **§2 Abs. 2 (1976):** 내무장관은 „Werktage einmalig zu Feiertagen zu erklären“, 즉 평일을 **법규명령(Rechtsverordnung)으로 1회성 공휴일로 지정**할 수 있다. 이 권한은 2010년 법안에서도 „§ 2 Absatz 2 … Ministerium“으로 존속이 확인된다. 따라서 SL에서 1회성 공휴일은 법률 개정 없이 명령만으로 생길 수 있다. C절 검색은 이 점을 고려해 해석해야 한다.

---

## C. 2020-01-01 이후 변경 및 1회성 공휴일

- **포털 기재 사항: 확보 불가.** 공식 포털이 JS 셸이라 „포털 기재“ 형식의 개정 이력을 얻을 수 없었다.
- **관보 전문검색 (Verkündungsportal, 관측):**
  - „Feiertagsgesetz“ 검색은 20건이다. 가장 최근 항목은 Drucksache 15/1464(2015-07-09)와 Amtsblatt I 2015 Nr. 33(2015-11-19)이다. **2016년 이후 결과는 0건**이다.
  - „Feiertagsgesetzes“ 검색도 결과가 20건으로 같다.
  - „Feiertag“ 검색은 423건이다. 상위 25건(2017~2025년 Drucksachen/Protokolle)의 제목에는 공휴일 추가·1회성 지정이 없다. 다만 Amtsblatt 항목은 상위 25건에 나오지 않아, 423건 전체는 **검토하지 못했다**.
- **판단 [추론]:** 2020년 이후 SFG §2 Abs. 1의 목록 개정은 **확인되지 않았다.** 이 검색은 법안 본문까지 색인한다(예: 2012년 도박법 법안이 본문 언급만으로 검색됨). 그러므로 개정법이 있었다면 „Feiertagsgesetz(es)“로 걸렸을 가능성이 높다. 단, 색인 범위는 검증하지 않았다.
- **2020년 이후 1회성 공휴일:** 발견하지 못했다. §2 Abs. 2에 따른 명령(Verordnung)은 법률명을 포함하지 않을 수 있으므로 **부재를 입증한 것은 아니다** [추론].

---

## D. 주 전역 항목별 규칙 유형

현행 12개 항목을 가정했다 [추론: 1976 목록에서 17. Juni를 10월 3일로 바꾸고 Buß- und Bettag를 제외].

| 항목 | 규칙 | 레포 지원 |
|---|---|---|
| Neujahr | (1) 고정 01-01 | 지원 |
| Karfreitag | (2) 부활절 −2 | 지원 |
| Ostermontag | (2) 부활절 +1 | 지원 |
| 1. Mai | (1) 고정 05-01 | 지원 |
| Christi Himmelfahrt | (2) 부활절 +39 | 지원 |
| Pfingstmontag | (2) 부활절 +50 | 지원 |
| Fronleichnam | (2) 부활절 +60 | 지원 |
| Mariä Himmelfahrt | (1) 고정 08-15 | 지원 |
| Tag der Deutschen Einheit | (1) 고정 10-03 | 지원 |
| Allerheiligen | (1) 고정 11-01 | 지원 |
| 1. Weihnachtstag | (1) 고정 12-25 | 지원 |
| 2. Weihnachtstag | (1) 고정 12-26 | 지원 |

- **NEW 규칙 유형: 없음** [추론].
- 2020년 이후에 효력이 시작되거나 끝나는 항목도 발견되지 않았다.
- 참고: 1976 원문의 Buß- und Bettag(11월 23일 이전 마지막 수요일, 요일 기반 규칙)가 SL에서 아직 유효하다면 NEW 유형이 된다. 폐지 개정법은 관측하지 못했다. 이 항목을 레포에 넣지 않는 판단은 [추론]에 기반한다.

---

## E. 키 매핑

| 항목 | 키 | 구분 |
|---|---|---|
| Neujahr | neujahr | 기존 재사용 |
| Karfreitag | karfreitag | 기존 재사용 |
| Ostermontag | ostermontag | 기존 재사용 |
| 1. Mai | erster_mai | 기존 재사용 |
| Christi Himmelfahrt | christi_himmelfahrt | 기존 재사용 |
| Pfingstmontag | pfingstmontag | 기존 재사용 |
| Fronleichnam | fronleichnam | 기존 재사용 |
| Mariä Himmelfahrt | mariae_himmelfahrt | **예고됨 (첫 사용)** |
| Tag der Deutschen Einheit | tag_der_deutschen_einheit | 기존 재사용 |
| Allerheiligen | allerheiligen | 기존 재사용 |
| 1. Weihnachtstag | erster_weihnachtstag | 기존 재사용 |
| 2. Weihnachtstag | zweiter_weihnachtstag | 기존 재사용 |

- **NEW 키: 없음.**
- buss_und_bettag는 SL에 해당하지 않는 것으로 판단한다 [추론, B절 11번 참조].

---

## F. 관보 접근성

**1) Verkündungsportal des Saarlandes: `https://www.amtsblatt.saarland.de/` (juris jportal)**
- 형태: 서버에서 렌더링한 정적 HTML이며 JS 셸이 아니다. 검색 폼은 GET 방식이라 표준 폼 제출로 결과 목록을 받았다.
- 수록 범위 (포털 문구):
  - Teil I: „ab der Ausgabe 48 vom 3. Dezember 2009“(서명본, 공적 효력)
  - 1999~2009년판
  - Teil II: 2009년 48호부터(참고용, 정본은 인쇄본)
  - 이용 조건: „kostenfrei“
- 최신호: 2026년 Nr. 37(2026-09-24)이 게시되어 있다.
- 인증: 로그인 폼(„Zugang mit Kennung“)이 있지만, 무료 영역의 검색·문서·PDF는 로그인 없이 받았다.
- 딥링크:
  - 문서 permalink `…/jportal/?quelle=jlink&docid=VB-SL-ABlI2015789-G&psml=bsverkslprod.psml&max=true`는 세션 없이 200을 반환했고, 새 세션이 붙은 PDF 링크를 포함했다.
  - PDF 직링크는 **세션 의존**이다. `Gs14_0266.pdf`는 jsessionid 없이 **404**(0 bytes), 세션 포함 시 **200**(application/pdf, 55,622 bytes)이었다.
  - 따라서 PDF URL은 영구 링크로 쓸 수 없다. 영구 링크는 jlink 형식으로 남겨야 한다 [추론].
- 속도 제한: 약 3~20초 간격으로 요청한 12회 동안 403/429나 지연은 관측하지 못했다.
- 의회 문서: 같은 포털에 Landtagsdrucksachen과 Plenarprotokolle가 함께 들어 있다(표시 건수: Landtagsdrucksachen 2,401, 전체 5,565). 법안 PDF를 받을 수 있다.
- **최근 SFG 개정 관보 PDF 시도:**
  - 대상: Amtsblatt I 2015 Nr. 33(Gesetz Nr. 1868 수록)
  - URL: `…/jportal/docs/anlage/sl/pdf/VerkBl/ABl/ads_33-2015_teil_I_signed.pdf;jsessionid=…`
  - 결과: **200, application/pdf, 19,096,599 bytes**, 62쪽. 텍스트 레이어가 있다.
  - 한계: 이 개정은 목록 개정이 아니라 시한 삭제다. 목록을 마지막으로 바꾼 개정(10월 3일, Buß- und Bettag 관련, 1990년대로 추정 **[추론]**)의 관보는 찾지 못했다.

**2) 역사 관보 아카이브: `https://www.amtsblatt.uni-saarland.de/` (1920~1998, 자를란트대 Gröpl 교수와 Staatskanzlei 공동)**
- 형태: 정적 HTML이다. 연도별 목록 `jahrghtml/1976.html`에서 호별 PDF `hefte/1976/1976-013.pdf`로 **딥링크가 가능**하다. 해당 PDF는 200, application/pdf, 180,842 bytes였다.
- PDF는 JBIG2 스캔 이미지이고 **텍스트 레이어가 없다.** 판독하려면 렌더링이 필요하다.
- 검색(`suche/search.php`, 목차만 색인)은 „Feiertagsgesetz“ 0건, „Feiertage“ 19건이었다. 1976년 목차는 결과에 나오지 않아 검색의 신뢰도가 낮다.

**3) Landtag des Saarlandes: `https://www.landtag-saar.de/`**
- 연결 실패(curl 000)했고 재시도하지 않았다. 원인은 확인하지 못했다.

**종합:** 관보 접근은 **open**이다(1999년 이후와 1920~1998년 모두 무료, 로그인 불필요). 단, 현행 통합본 포털은 **blocked (JS 셸)**이다.

---

## 요약 (5줄)
1. 주 전역: 12개 [추론]. 현행 조문 미확보, 1976 원문 13개에서 17. Juni→10월 3일, Buß- und Bettag 폐지로 판단.
2. 지역 한정 제외: 0건 (1976 원문 §2 Abs. 1 기준).
3. NEW 규칙 유형: 없음 (모두 고정일 또는 부활절 오프셋. 2020년 이후 변경·1회성 공휴일 발견 안 됨, 단 명령에 의한 1회성 지정의 부재는 입증 못 함).
4. NEW 키: 없음 (mariae_himmelfahrt 첫 사용, 나머지 11개는 기존 키).
5. 관보 접근: open (Verkündungsportal 1999~, uni-saarland 1920~1998, PDF 세션 의존). 통합본 포털 recht.saarland.de는 JS 셸로 blocked.
