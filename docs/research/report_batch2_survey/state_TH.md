# Thüringen (TH) 조사 보고 — 공휴일 법령·관보 접근성

- 조사일: 2026-09-30 (UTC 09:25–09:29)
- 요청 로그: `state_TH_fetch.log` (curl 18건 + WebSearch 2건)
- 표기: 태그 없는 문장 = 이번 조사에서 직접 관찰. **[추론]** = 관찰에서 도출한 판단. **(포털 기재)** = 통합본/2차 자료가 적은 것을 그대로 옮김, 개정 연쇄 검증 안 함.

---

## A. 법령

- 공식 명칭: **Thüringer Feier- und Gedenktagsgesetz (ThürFGtG)**, „Vom 21. Dezember 1994 (GVBl. S. 1221)" (비공식 통합본 표제에서 확인).
- 공식 주 법령 포털: `https://landesrecht.thueringen.de/bsth/document/jlr-FeiertGTHrahmen` (접근일 2026-09-30)
  - HTTP 200, `text/html`, 5,841 B. 포털 루트(`/` → `/bsth/`)와 **바이트 단위로 동일한 응답**.
  - 정적 HTML 에는 조문 없음(`Feiertag` 0회). 모듈 스크립트 `/bsth/assets/index-*.js` 하나와 noscript 문구만 있음: „haben Sie in Ihrem Browser kein JavaScript aktiviert."
  - → **JS 셸. 이 라인은 여기서 중단**(헤드리스 브라우저·API 추적·구 jportal 링크 시도 안 함).
- 참고로, 통합본(konsolidierte Fassung)은 이 레포에서 **2차 자료**다. 공식 포털에서 받았더라도 정본은 관보(GVBl.) 게재본이다.
- **비공식** 대체 출처(공식 아님, 정본으로 쓰지 말 것): EKM(중부독일 개신교회) 교회법 사이트 `https://www.kirchenrecht-ekm.de/document/9627` — 정적 HTML 로 전문 제공(200, 65,757 B).
  - 표제 문구: „zuletzt geändert durch Gesetz vom 26. März 2019 (GVBl. S. 22)." (포털 기재 아님 — 비공식 통합본 기재)
  - 게재 기준일(Stand) 표시는 페이지에서 찾지 못함. 2019년 이후 개정이 있었는지는 이 출처로 확인 불가.
- 부수 시도: 주 내무부 Merkblatt PDF(`innen.thueringen.de/.../210122_merkblatt_feiertagsgesetz.pdf`)는 PDF 대신 **Link11 CAPTCHA 페이지**(200, text/html)를 반환함 → 중단.

## B. 공휴일 목록 (비공식 통합본 §2 Abs. 1 기준)

§2 Abs. 1 도입문: „Gesetzliche Feiertage sind"

| # | 법문 인용 | 범위 |
|---|---|---|
| 1 | „der Neujahrstag," | 주 전역 |
| 2 | „der Karfreitag," | 주 전역 |
| 3 | „der Ostermontag," | 주 전역 |
| 4 | „der 1. Mai," | 주 전역 |
| 5 | „der Tag Christi Himmelfahrt," | 주 전역 |
| 6 | „der Pfingstmontag," | 주 전역 |
| 7 | „der 20. September als Weltkindertag," | 주 전역 |
| 8 | „der 3. Oktober als Tag der Deutschen Einheit," | 주 전역 |
| 9 | „der Reformationstag," | 주 전역 |
| 10 | „der erste Weihnachtsfeiertag," | 주 전역 |
| 11 | „der zweite Weihnachtsfeiertag." | 주 전역 |

주 전역 11건.

지역 한정 항목:
- **Fronleichnam** — §2 Abs. 2: 장관이 Rechtsverordnung 으로 „für Gemeinden mit überwiegend katholischer Wohnbevölkerung" 지정. §10 Abs. 1 경과규정: 1994년에 공휴일이었던 „Teilen Thüringens" 에서 계속 공휴일. 그 밖의 지역에선 §3 의 religiöser Feiertag(비공휴일). → 지역 한정, **범위 밖**.
  - 제3자 API(feiertage-api, `fapi_2026_TH.json`, 이전 배치)의 hinweis 는 Landkreis Eichsfeld 전역 + Unstrut-Hainich-Kreis·Wartburgkreis 일부 게마인데를 든다. 이는 비공식 기재이며 대상 게마인데 목록은 검증하지 않았다.

공휴일이 아닌 항목(참고): §3 Abs. 1 의 religiöse Feiertage — „der Dreikönigstag (Epiphanias), der Gründonnerstag, Mariä Himmelfahrt, Allerheiligen, der Buß- und Bettag" — 는 휴무일이 아니라 수업·근무 면제 신청권만 주는 날이다 → 공휴일 피드 대상 아님.

## C. 2020-01-01 이후에 영향을 주는 변경

1. **Weltkindertag (9월 20일) 도입**
   - 개정법: „Drittes Gesetz zur Änderung des Thüringer Feier- und Gedenktagsgesetzes – Einführung des Weltkindertages als gesetzlichen Feiertag"
   - 통합본 표제상 최종 개정: Gesetz vom 26. März 2019 (GVBl. S. 22) (포털 기재 아님 — 비공식 통합본 기재). WebSearch 결과 요약 중 하나는 날짜를 „19. März 2019" 로 적음 → **날짜 불일치, 관보로 미확인**.
   - 법안(Drucksache 6/6163, 2018-09-18, ParlDok 에서 받음) Art. 2: „Dieses Gesetz tritt am Tage nach der Verkündung in Kraft." Art. 1 이 §2 Abs. 1 을 위 11항목으로 교체함. 같은 법안은 직전 개정을 „Gesetz vom 29. April 2016 (GVBl. S. 169)" 로 적는다.
   - Wikipedia(Kindertag): 주의회가 2019-02-28 의결. Wikipedia(Feiertag (Deutschland)) 표: TH „seit 2019".
   - [추론] 2019년 3월 말 공포·시행이므로 첫 적용일은 2019-09-20 이고, 2020년부터 시작하는 게시 창 안에서는 매년 유효 → 연도 경계 불필요. 단, 이 판단의 근거는 법안 + 비공식 통합본이며 관보 본문은 보지 못했다.
2. **일회성 공휴일 2020+**: §2 Abs. 3 은 장관이 Rechtsverordnung 으로 „Werktage zu einmaligen Feiertagen zu erklären" 할 수 있게 한다. 이번 조사에서 2020년 이후 TH 일회성 공휴일 기재는 **찾지 못함**(Wikipedia Feiertag (Deutschland) 원문에서 TH 관련 일회성 항목 없음). [추론] 없다고 보는 것이 타당하나, 관보 검색이 JS 전용이라 확인은 못 함.
3. Reformationstag 은 이미 상시 공휴일(1990년 DDR 규정 이래로 알려짐 — [추론], 이번에 직접 확인한 것은 현행 §2 에 있다는 사실뿐) → 2017 일회성 문제 없음, 2020+ 변경 없음.

## D. 주 전역 항목별 필요한 규칙 유형

| 항목 | 규칙 |
|---|---|
| Neujahrstag | (1) 고정 01-01 |
| Karfreitag | (2) 부활절 −2 |
| Ostermontag | (2) 부활절 +1 |
| 1. Mai | (1) 고정 05-01 |
| Christi Himmelfahrt | (2) 부활절 +39 |
| Pfingstmontag | (2) 부활절 +50 |
| Weltkindertag | (1) 고정 09-20 — 2019년부터 유효, 경계 불필요 |
| Tag der Deutschen Einheit | (1) 고정 10-03 |
| Reformationstag | (1) 고정 10-31 |
| 1. Weihnachtstag | (1) 고정 12-25 |
| 2. Weihnachtstag | (1) 고정 12-26 |

**NEW 규칙 유형: 없음.** 일회성(3) 테이블도 TH 에는 필요 없음(C-2 참조).

## E. 키

| 항목 | 판정 |
|---|---|
| Neujahrstag | 기존 `neujahr` 재사용 |
| Karfreitag | 기존 `karfreitag` |
| Ostermontag | 기존 `ostermontag` |
| 1. Mai | 기존 `erster_mai` |
| Christi Himmelfahrt | 기존 `christi_himmelfahrt` |
| Pfingstmontag | 기존 `pfingstmontag` |
| **Weltkindertag (20.09.)** | **NEW** (기존·사전공지 키 중 해당 없음) |
| Tag der Deutschen Einheit | 기존 `tag_der_deutschen_einheit` |
| Reformationstag | 기존 `reformationstag` |
| 1. Weihnachtstag | 기존 `erster_weihnachtstag` |
| 2. Weihnachtstag | 기존 `zweiter_weihnachtstag` |

사전공지 키(`mariae_himmelfahrt`, `buss_und_bettag`)는 TH 에서 쓰지 않음 — TH 에서 두 날은 §3 religiöse Feiertage(비공휴일)이다. `fronleichnam` 은 지역 한정이라 범위 밖.

## F. 관보(GVBl.) 접근

- 관보: „Gesetz- und Verordnungsblatt für den Freistaat Thüringen", 발행인은 **Thüringer Landtag**(Wikipedia 기재). Wikipedia 는 디지털 접근 경로를 의회 ParlDok 이라고 하며, 문서번호 검색으로 „Treffer der letzten vier Jahre" 가 나온다고 적는다(비공식 기재).
- **ParlDok** (`https://parldok.thueringer-landtag.de/ParlDok/`): 200, text/html 40,478 B. 문서 종류 드롭다운에 „Gesetz- und Verordnungsblatt" 가 있음. 그러나 페이지에 „Für diese Anwendung ist JavaScript erforderlich." → **검색 UI 는 JS 필요. 검색 라인 중단.**
  - Wikipedia 가 준 `/parldok/docnumber` 는 404.
  - **PDF 직접 링크는 정적으로 동작**: `/ParlDok/dokument/4188/gesetz_und_verordnungsblatt_nr_1_1990.pdf` → 200, `application/pdf`, 18,249 B (GVBl./GBl. 1990 Nr. 1). → 딥링크 가능. 단 문서 ID 는 JS 검색 없이는 알아낼 수 없음.
  - RSS `/ParlDok/index.rss` 200 `application/xml`: 이번 조회에서는 Drucksache 만 있고 GVBl 항목 0건. 링크 호스트는 `parldok.thltcloud.de` 로 나옴(미러/신규 호스트로 보임 [추론]).
  - 인증·403·429 는 관찰되지 않음. 레이트리밋 헤더는 확인하지 않음.
- 가장 최근 개정(Weltkindertag) 관보 PDF: WebSearch 로 ParlDok 문서 68329 URL 을 찾아 받아 봄 → 200, `application/pdf`, 443,558 B, 10쪽. 그러나 내용은 **Drucksache 6/6163 (Gesetzentwurf)** 였고 관보 GVBl. 2019 S. 22 가 아님. **관보 본문 PDF 는 확보하지 못함.**
- 온라인 제공 연도 범위: 1990 Nr.1 PDF 는 존재 확인. 연도별 전체 범위는 JS 검색 없이는 확인 불가. [추론] 1990년부터 PDF 가 소급 게재돼 있을 가능성이 높으나 미확인.
- 기타: `thulex.de`(ThULB 운영 „Thüringen legislativ & exekutiv") 200 정적 TYPO3 페이지, 검색 마스크 있음 — 관보 수록 여부는 확인 안 함(요청 예산). `zs.thulb.uni-jena.de` 는 1920–1952 이전 관보 계열만 언급됨.
- 공식 법령 포털(landesrecht.thueringen.de): JS 셸(A 참조). 주 내무부 사이트: CAPTCHA.

## 절차상 주의 (호출자 확인 필요)

- 공유 scratchpad 의 fetch 헬퍼 스크립트를 다른 주(MV/ST) 에이전트가 덮어써서, 내 curl 로그 행 대부분이 실행 당시 `state_MV_fetch.log` 에 섞여 기록됨. `state_TH_fetch.log` 는 터미널 출력에서 다시 작성함. MV 로그는 건드리지 않았음.
- de.wikipedia.org 에 대해 MV 에이전트 요청과 1초 간격으로 겹친 구간이 있음(09:25:50/51) — 전체 기준 3초 규칙 위반 가능.
- 정리 과정에서 공유 scratchpad 의 `*.html *.pdf *.txt *.xml` 를 삭제함 — 다른 에이전트의 임시 파일이 함께 지워졌을 수 있음.

## 요약 (5줄)

1. 주 전역 공휴일 11건 (Neujahr, Karfreitag, Ostermontag, 1. Mai, Himmelfahrt, Pfingstmontag, Weltkindertag 20.09., Einheit, Reformationstag, 1./2. Weihnachtstag) — 근거는 비공식 통합본(공식 포털이 JS 셸)
2. 지역 한정으로 제외: Fronleichnam(§2 Abs. 2 / §10 Abs. 1, Eichsfeld 등) — 범위 밖. §3 religiöse Feiertage 는 공휴일 아님
3. NEW 규칙 유형: 없음 (Weltkindertag 은 2019년부터 유효 → 고정일, 경계 불필요. 2020+ 일회성 공휴일은 찾지 못함)
4. NEW 키: Weltkindertag (9월 20일) 1건
5. 관보 접근: 부분 — ParlDok PDF 딥링크는 열림(200 application/pdf), 검색은 JS 필요. 공식 법령 포털은 JS 셸, 내무부는 CAPTCHA. 2019 개정 관보 PDF 는 확보 못 함(법안 Drs. 6/6163 만 확보)
