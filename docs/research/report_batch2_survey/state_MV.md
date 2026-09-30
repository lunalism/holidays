# Mecklenburg-Vorpommern (MV) — Feiertagsgesetz 조사

- 조사일(접근일): 2026-09-30 (UTC 09:25–09:31)
- 요청 로그: `state_MV_fetch.log` (MV 관련 요청 10건, 전부 기록)
- 표기: [추론] = 직접 관찰이 아니라 유도한 문장. 태그 없는 문장 = 이번 조사에서 직접 관찰한 것.
- 인용문은 독일어 원문 그대로, 15단어 이하.

---

## A. 법령

- 정식 명칭(관보 색인·개정법 원문에서 관찰): „Gesetz über Sonn- und Feiertage (Feiertagsgesetz Mecklenburg-Vorpommern – FTG M-V)"
  - 현행 기준본: Neufassung(재공포) „in der Fassung der Bekanntmachung vom 8. März 2002 (GVOBl. M-V S. 145)"
  - 정리번호: GS Meckl.-Vorp. Gl.-Nr. 1136-1
- 공식 주 법령 포털: `https://www.landesrecht-mv.de/bsmv/document/jlr-FeiertGMVrahmen`
  - HTTP 200, text/html, 5,559 bytes. 그런데 정적 HTML에는 법령 본문이 없는 **JS 셸**이다. 본문 대신 „Aktivieren Sie bitte JavaScript, um den Bürgerservice zu nutzen." 문구만 있고, HTML 안에 'Feiertag' 문자열은 0회다.
  - 규칙에 따라 **공식 통합본(consolidated text) 확보는 여기서 중단**했다. 헤드리스 브라우저나 API 역공학은 시도하지 않았다.
- 참고로, 통합본은 이 레포에서 **2차 자료**다. 정본 근거는 관보(GVOBl. M-V)에 공포된 개정법 원문이다.
- 비공식 대체 출처 확인 결과:
  - `gesetze.co/MV/FTG_M-V` 는 MV 법령 목록(`/alle/MV`)으로 리다이렉트됐다. 이 목록(50개 링크)에 FTG M-V 는 없다. → 비공식 통합본도 확보하지 못했다.
  - 같은 폴더의 `fapi_2026_MV.json`(feiertage-api 계열, 이번 조사 이전에 이미 받아 둔 파일, **비공식**)에는 2026년 MV 공휴일 11개가 있다. 공식 근거로 쓰지 않는다. B절에서 명칭을 대조하는 용도로만 썼다.
- 공식 대체 근거(1차 자료, 직접 관찰):
  - 법무부 관보 페이지의 **Fundstellennachweis „1-System Übersicht Stand 9_2026.pdf"**(관보 체계 색인). 여기에 FTG M-V 개정 이력 전체가 실려 있다.
  - 최신 개정법의 **관보 원문 PDF**(GVOBl. M-V 2022 Nr. 31).

### 관보 색인(Stand 9/2026)에 기재된 FTG M-V 개정 이력 (포털 기재)
| 항목 | GVOBl. 면 | 호/연도 | 일자 |
|---|---|---|---|
| 원법 | 342 | 17/92 | 18.6.1992 |
| § 8 neu gefasst d. Art. 8 d. G | 566 | 12/94 | 5.5.1994 |
| geänd. §§ 2, 5, 6 d. G | 1055 | 26/94 | 20.12.1994 |
| geänd. d. G | 405 | 13/01 | 24.10.2001 |
| Bek. d. NF (재공포) | 145 | 4/02 | 8.3.2002 |
| geänd. d. G | 390 | 15/04 | 20.7.2004 |
| geänd. d. Art. 3 d. G | 502 | 19/12 | 15.11.2012 |
| geänd. d. Art. 2 d. G | 1010 | 43/21 | 21.6.2021 |
| geänd. d. G | 427 | 31/22 | 7.7.2022 |

- 색인 1136(Feiertage) 절에는 1136-1(FTG M-V) 하나만 있다. 별도의 일회성 공휴일 법률은 등재돼 있지 않다.

---

## B. 현행 공휴일 목록 (§ 2 Abs. 1)

직접 관찰한 사실 (2022년 개정법 원문, GVOBl. M-V 2022 S. 427):
- 개정 조문: „§ 2 Absatz 1 wird wie folgt geändert:"
- 삽입 조문: „Nach Nummer 1 wird folgende Nummer 2 eingefügt: „2. der Frauentag (8. März),""
- 번호 이동: „Die bisherigen Nummern 2 bis 10 werden die Nummern 3 bis 11."

이로부터 § 2 Abs. 1 에는 현재 **11개 번호 항목**이 있다는 것이 확인된다.

**조문 문구 관찰 한계:** 공식 통합본이 JS 셸이다. 2002년 재공포 관보(4/02)도 온라인 관보 목록 밖이다(온라인은 2014년 이후분만 있음). 그래서 **Frauentag 외 10개 항목의 조문 문구는 직접 관찰하지 못했다.** 아래 명칭은 비공식 `fapi_2026_MV.json` 에서 가져왔다. 번호 순서는 [추론]이다.

| § 2 Abs. 1 Nr. | 항목 | 조문 문구(인용) | 범위 |
|---|---|---|---|
| 1 | Neujahr [추론: Nr. 1 = 1월 1일] | 미관찰 | 주 전역 [추론] |
| 2 | Frauentag | „der Frauentag (8. März)," (GVOBl. 2022 S. 427) | 주 전역 (§ 2 Abs. 1 에 들어 있음) |
| 3–11 | Karfreitag, Ostermontag, Tag der Arbeit (1. Mai), Christi Himmelfahrt, Pfingstmontag, Tag der Deutschen Einheit (3. Oktober), Reformationstag (31. Oktober), 1. Weihnachtstag, 2. Weihnachtstag | 미관찰 (명칭은 비공식 fapi 기준) | 주 전역 [추론] |

- 9개 명칭(Nr. 3–11)과 개정 전 번호 2–10의 개수(9개)가 일치한다. 따라서 비공식 목록 11개가 § 2 Abs. 1 의 11개 번호와 대응한다고 본다. [추론]
- **범위 한정 항목(지역·종교 집단 한정):** 조문을 보지 못했으므로 **확인 불가**다.
  - 비공식 fapi 목록에는 `hinweis`(지역 한정 주석)가 붙은 항목이 없다.
  - MV 에 Fronleichnam 등 지역 한정 공휴일이 법정돼 있다는 근거는 이번 조사에서 발견하지 못했다. [추론: MV 에는 "범위 밖" 항목이 없거나, 있더라도 § 2 Abs. 1 밖의 종교 보호 규정일 가능성]
  - 이 점은 조문을 직접 확인해야 확정된다.

---

## C. 2020-01-01 이후 변경 / 1990년 이후 도입 항목 / 일회성 공휴일

1. **Frauentag (3월 8일) 신설** — 포털 기재 + 관보 원문 관찰
   - 근거: „Viertes Gesetz zur Änderung des Feiertagsgesetzes Mecklenburg-Vorpommern" vom 7. Juli 2022, GVOBl. M-V 2022 Nr. 31 (ausgegeben 12. Juli 2022), S. 427
   - 시행: „Dieses Gesetz tritt am Tag nach der Verkündung in Kraft."
   - 따라서 시행일은 2022-07-13 이다. [추론] 그 해 3월 8일은 이미 지났으므로 **첫 적용 연도는 2023**이다. [추론]
   - 같은 법으로 § 5 Abs. 1 에 „des 8. März," 가 추가됐다. 이는 공휴일 보호(조용한 날) 관련 조항이며 목록 변경은 아니다.
2. **2021년 개정 (Art. 2 d. G v. 21.6.2021, GVOBl. S. 1010, 1016)** — 관보 원문 관찰
   - § 6 Abs. 2 에 „4. der Betrieb von Wettvermittlungsstellen." 를 추가했다(금지 행위 목록).
   - **공휴일 목록 변경은 없다.**
3. **2012년 개정 (Art. 3 d. G v. 15.11.2012)** — 2020 이전이라 대상 밖이다.
   - 법률 제목은 AG-SGB II·StiftG 개정과 묶여 있다. 목록 변경은 아닐 것이다. [추론, 원문 미확인 — 2012년 관보는 온라인 목록에 없음]
4. **Reformationstag** — 1990년대부터 MV 공휴일이다. 2020 이전부터 존재하므로 2020+ 유효기간 문제는 없다. [추론, 원문 미확인]
5. **일회성 공휴일 (2020+)**
   - 관보 색인 Stand 9/2026 에서 1136 절에는 1136-1 하나뿐이다. 2022년 이후 FTG 개정도 없다(포털 기재).
   - 따라서 **2020-05-08, 2025-05-08 모두 MV 에서는 일회성 공휴일이 아니었다.** [추론 — 색인에 해당 법률이 없음을 근거로 함]
   - 참고로 fapi 비공식 2026 목록에도 일회성 항목은 없다.

---

## D. 항목별 필요한 규칙 유형

| 항목 | 규칙 | 판정 |
|---|---|---|
| Neujahr | (1) 고정 01-01 | 지원됨 |
| Frauentag | 고정 03-08 이지만 **2023년부터만** 존재 (2020–2022 에는 없음) | **NEW** — 유효 시작 연도(valid-from 2023)가 필요하다. 현 레포는 연도 범위 유효성을 지원하지 않는다. (1)로 넣으면 2020–2022 에 잘못된 공휴일이 생긴다. |
| Karfreitag | (2) 부활절 −2 | 지원됨 |
| Ostermontag | (2) 부활절 +1 | 지원됨 |
| Tag der Arbeit | (1) 고정 05-01 | 지원됨 |
| Christi Himmelfahrt | (2) 부활절 +39 | 지원됨 |
| Pfingstmontag | (2) 부활절 +50 | 지원됨 |
| Tag der Deutschen Einheit | (1) 고정 10-03 | 지원됨 |
| Reformationstag | (1) 고정 10-31 | 지원됨 |
| 1. Weihnachtstag | (1) 고정 12-25 | 지원됨 |
| 2. Weihnachtstag | (1) 고정 12-26 | 지원됨 |

- 대안이 하나 있다. Frauentag 를 (3) 일회성 항목 `_YYYY` 로 해마다 나열하는 방식이다. 하지만 끝이 없는 반복을 일회성 표로 처리하게 된다. 설계상 부적합하다는 점만 적어 둔다. [추론]

---

## E. 키 재사용 여부

| 항목 | 키 |
|---|---|
| Neujahr | 기존 `neujahr` 재사용 |
| Frauentag | 키는 기존 `frauentag` 재사용 가능. 단 **규칙은 NEW**(valid-from 2023) — D 참조 |
| Karfreitag | 기존 `karfreitag` |
| Ostermontag | 기존 `ostermontag` |
| Tag der Arbeit | 기존 `erster_mai` |
| Christi Himmelfahrt | 기존 `christi_himmelfahrt` |
| Pfingstmontag | 기존 `pfingstmontag` |
| Tag der Deutschen Einheit | 기존 `tag_der_deutschen_einheit` |
| Reformationstag | 기존 `reformationstag` |
| 1. Weihnachtstag | 기존 `erster_weihnachtstag` |
| 2. Weihnachtstag | 기존 `zweiter_weihnachtstag` |

- NEW 키: 없음.

---

## F. 관보(GVOBl. M-V) 접근성

- **관보 포털 (법무부, 정적 HTML, 딥링크 가능):** `https://www.regierung-mv.de/Landesregierung/jm/service_justizministerium/verkuendungsblaetter/gesetz-verordnungsblaetter/`
  - HTTP 200, text/html, 524,995 bytes.
  - 정적 HTML 에 PDF 직링크가 448개 있다. JS 셸이 아니다.
  - 연도 섹션: **2014–2026** („Gesetz- und Verordnungsblätter M-V 2014" … „2026").
  - 2026년분은 Nr. 28 v. 28.9.2026 까지 있다.
  - 2013년 이전 호수는 이 페이지에 없다. 1992·2002 원법·재공포본은 온라인에서 확인 불가다.
  - 같은 페이지에 Fundstellennachweis(„1-System Übersicht Stand 9_2026.pdf", 304쪽)와 Stichwortverzeichnis PDF 가 있다.
- PDF URL 은 `/static/Regierungsportal/Justizministerium/Inhalte/Rechtliches/GVOBI.M-V/...` 형태다. 파일명 규칙은 제각각이다(`GVOBl. Nr. 31 v. 12.7.2022.pdf`, `Dateien/2021/letzte AK_GVO_43_21.pdf` 등). 그래서 호수만으로 URL 을 추정할 수는 없고 목록 페이지에서 찾아야 한다.
- **실제 요청 결과:**
  - 관보 색인 PDF → 200, application/pdf, 1,881,891 bytes
  - **최신 목록 개정 관보 GVOBl. 2022 Nr. 31** `…/GVOBI.M-V/GVOBl.%20Nr.%2031%20v.%2012.7.2022.pdf` → **200, application/pdf, 263,235 bytes** (8쪽, S. 427 에 개정 원문이 있음)
  - GVOBl. 2021 Nr. 43 `…/Dateien/2021/letzte%20AK_GVO_43_21.pdf` → 200, application/pdf, 676,228 bytes
  - 추측으로 넣은 URL `…/jm/Service/Gesetz--und-Verordnungsblatt/` → 404 (정상 404 페이지)
  - `regierung-mv.de/Suche/?query=Feiertagsgesetz` → 200 이지만 검색 결과가 없다. 파라미터 형식이 맞지 않은 것으로 보여 추가 시도하지 않았다.
  - 인증 요구, 403/429, 속도 제한 징후는 관찰되지 않았다. 동일 호스트 요청 간격은 3초 이상을 지켰다.
- **공식 법령 포털 landesrecht-mv.de:** JS 셸이다 (A 참조). 차단은 아니지만 정적 본문이 없다.
- **Landtag MV Parlamentsdokumentation:** `https://www.dokumentation.landtag-mv.de/parldok/`
  - 200, text/html, 42,233 bytes. 정적 HTML 에 „Für diese Anwendung ist JavaScript erforderlich." 문구가 있다.
  - 검색 기능은 JS 기반이다. 정적 링크는 lizenz·rss·impressum 정도다.
  - 관보 사본이나 2022년 Drucksache 에 정적으로 접근할 경로는 확인하지 못했다. 규칙에 따라 여기서 중단했다.

---

## 요약 (5줄)
1. 주 전역 공휴일 11개 (§ 2 Abs. 1 Nr. 1–11; 개수와 Frauentag 문구는 관보 원문, 나머지 명칭은 비공식 목록 기준)
2. 범위 한정 제외 항목: 0 확인 (조문 미관찰로 지역·종교 한정 항목 존재 여부는 미확정)
3. NEW 규칙 유형: 1 — Frauentag(03-08)의 유효 시작 연도 2023 (2022-07-13 시행, 2022 Nr. 31 S. 427)
4. NEW 키: 0 (`frauentag` 포함 전부 기존 키 재사용 가능). 2020·2025 5월 8일 일회성 공휴일 없음 [추론]
5. 관보 접근: partial — regierung-mv.de 에서 2014–2026 PDF 공개(정적·딥링크·무인증). 법령 포털 landesrecht-mv.de 와 Landtag ParlDok 은 JS 셸
