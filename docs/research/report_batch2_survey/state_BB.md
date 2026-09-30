# Brandenburg (BB) — 공휴일 법령 조사

- 조사일: 2026-09-30 (UTC 09:25–09:28)
- 요청 로그: `~/holidays-reports/report_batch2_survey/state_BB_fetch.log` (총 16건, 403/429 없음)
- 태그 규약: 직접 관측한 내용은 태그 없음, 도출·추정한 문장은 [추론].

---

## A. 법령

- 공식 명칭: „Gesetz über die Sonn- und Feiertage (Feiertagsgesetz - FTG)“
- 원 공포: „vom 21. März 1991 (GVBl.I/91, [Nr. 06], S.44)“
- 포털 표기 최종 개정: „zuletzt geändert durch Gesetz vom 30. April 2015 ( GVBl.I/15, [Nr. 13] )“
- 공식 주법 포털: BRAVORS (Brandenburgisches Vorschriftensystem)
  - 현행 통합본: https://bravors.brandenburg.de/gesetze/ftg_2015 (HTTP 200, 정적 HTML에 전문 포함, 접근일 2026-09-30)
  - 개정 이력: https://bravors.brandenburg.de/gesetze/ftg_2015/list
  - 참고: `/gesetze/ftg`, `/gesetze/feiertagsg` 는 302 → `http://bravors.brandenburg.de:443` (존재하지 않는 경로를 홈으로 돌리는 것으로 보임 [추론]). 올바른 경로는 포털의 빠른검색(POST 폼, 세션 쿠키 필요)으로 찾았다.
- **주의: 이 통합본(Lesefassung)은 이 레포에서 2차 출처다.** 정본은 GVBl. 공포문이다. 아래 B·C 의 내용은 모두 통합본/포털 기재에 근거한다.

## B. 현행 통합본의 공휴일 목록 (§ 2)

§ 2 Abs. 1 도입문: „Gesetzlich anerkannte Feiertage sind:“ — 주 전체에 적용되며, 지역·집단 한정 조항은 없다.

| # | 법문 표현 (인용) | 적용 범위 |
|---|---|---|
| 1 | „der Neujahrstag (1. Januar)“ | 주 전역 |
| 2 | „der Karfreitag“ | 주 전역 |
| 3 | „der Ostersonntag“ | 주 전역 |
| 4 | „der Ostermontag“ | 주 전역 |
| 5 | „der 1. Mai (Tag der Arbeit)“ | 주 전역 |
| 6 | „der Christi Himmelfahrtstag“ | 주 전역 |
| 7 | „der Pfingstsonntag“ | 주 전역 |
| 8 | „der Pfingstmontag“ | 주 전역 |
| 9 | „der Tag der deutschen Einheit (3. Oktober)“ | 주 전역 |
| 10 | „das Reformationsfest (31. Oktober)“ | 주 전역 |
| 11 | „der 1. Weihnachtsfeiertag (25. Dezember)“ | 주 전역 |
| 12 | „der 2. Weihnachtsfeiertag (26. Dezember)“ | 주 전역 |

- 지역/지자체/집단 한정 공휴일: **없음** (범위 밖 항목 0건).
- 공휴일이 아닌 관련 조항 (기록용, 피드 대상 아님):
  - § 2 Abs. 2 „Gedenk- und Trauertage sind:“ — Volkstrauertag, Totensonntag, „der 8. Mai als Tag der Befreiung vom Nationalsozialismus …“. 이들은 „gesetzlich anerkannte Feiertage“ 목록(Abs. 1)에 속하지 않으므로 공휴일이 아니다 [추론: 조문 구조상 Abs. 1 과 Abs. 2 가 별개 범주]. Volkstrauertag·Totensonntag 는 어차피 일요일.
  - § 2 Abs. 3: 주정부가 „durch Rechtsverordnung Werktage zu einmaligen Feier-, Gedenk- oder Trauertagen“ 지정 가능 (1회성 공휴일 수권 조항).
  - § 2 Abs. 4: 종교 축일(religiöse Feiertage) — 근로자에게 예배 참석 기회 보장(§ 7)일 뿐 일반 공휴일 아님 → 범위 밖.

## C. 2020-01-01 이후 효력이 있는 변경 / 1990년 이후 도입 항목 / 2020+ 1회성 공휴일

포털 „Änderungshistorie“ 기재(포털 기재, 개정 연쇄 검증 없음):

| 개정 | 포털 기재 대상 | 포털 기재 출처 |
|---|---|---|
| Ursprüngliche Fassung vom 21. März 1991 | 전체 | GVBl.I/91, [Nr. 06], S.44 |
| Gesetz vom 19. Dezember 1994 | „§§ 1, 2, 4, 5, 7-12“ | GVBl.I/94, S.514 |
| Gesetz vom 7. April 1997 | §§ 3-6, 8 | GVBl.I/97, S.32 |
| Gesetz vom 6. Juli 1998 | § 4 | GVBl.I/98, [Nr. 12], S.167, 170 |
| Gesetz vom 20. November 2003 | § 4 | GVBl.I/03, [Nr. 15], S.287 |
| Gesetz vom 30. April 2015 | § 2 | GVBl.I/15, [Nr. 13] |

- **2020-01-01 이후 효력 발생한 공휴일 목록 변경: 없음** (포털 기재). 포털상 최종 개정은 2015년이다.
- 2015년 개정 (포털 기재; 공포 PDF 로 내용 확인): „Viertes Gesetz zur Änderung des Feiertagsgesetzes Vom 30. April 2015“ — § 2 Abs. 2 에 Nummer 3(8. Mai 기념일) 추가. **Gedenktag 이며 공휴일 아님** → 공휴일 목록에는 영향 없음.
- 1990년 이후 도입 항목 중 2020+ 에 영향: 법 자체가 1991년 제정이므로 12개 항목 전부가 형식상 "1990년 이후 도입"이다. 이 중 Reformationsfest(10/31)은 BB 에서 1991년 이래 공휴일로 되어 있다고 알려져 있으나, 1994년 § 2 개정에서 목록이 어떻게 바뀌었는지는 이번에 해당 판을 열람하지 않아 확인하지 않았다 [추론]. 어느 경우든 2020년 이전부터 효력 → 레포 관점에서 기간 경계 없음 [추론].
- 2020+ 1회성 공휴일 (§ 2 Abs. 3 Verordnung): BRAVORS 빠른검색("Feiertagsgesetz") 결과 1쪽에서 해당 Verordnung 은 보이지 않았다 (보인 Verordnung 은 FTGZüV·Bedarfsgewerbe-VO 뿐). 1쪽만 확인했으므로 "없음"은 [추론].
  - 레포의 `achter_mai_2020`·`achter_mai_2025` 는 de_be(Berlin) 1회성이며 BB 와 무관하다 [추론].
- 참고: 포털은 모든 판의 „Gültigkeitsdauer“ 를 „gültig von 11.05.1991“ 로 동일하게 표기 — 판별 시행일로 쓸 수 없다.

## D. 항목별 필요 규칙 유형

| 항목 | 규칙 | 레포 지원 |
|---|---|---|
| Neujahrstag | 고정 01-01 | (1) 기존 |
| Karfreitag | 부활절 −2 | (2) 기존 |
| Ostersonntag | 부활절 +0 | (2) 기존 (offset 0 허용) |
| Ostermontag | 부활절 +1 | (2) 기존 |
| 1. Mai | 고정 05-01 | (1) 기존 |
| Christi Himmelfahrtstag | 부활절 +39 | (2) 기존 |
| Pfingstsonntag | 부활절 +49 | (2) 기존 (offset 49 허용) |
| Pfingstmontag | 부활절 +50 | (2) 기존 |
| Tag der deutschen Einheit | 고정 10-03 | (1) 기존 |
| Reformationsfest | 고정 10-31 | (1) 기존 |
| 1. Weihnachtsfeiertag | 고정 12-25 | (1) 기존 |
| 2. Weihnachtsfeiertag | 고정 12-26 | (1) 기존 |

- **NEW 규칙 유형: 없음.** 요일 기반 규칙·기간 한정(valid-from/until) 모두 불필요 (2020+ 변경 없음, 포털 기재 기준).
- 1회성 테이블: BB 에는 2020+ 1회성 항목이 확인되지 않아 불필요 [추론].

## E. 키 매핑

| 항목 | 키 |
|---|---|
| Neujahrstag | `neujahr` 재사용 |
| Karfreitag | `karfreitag` 재사용 |
| **Ostersonntag** | **NEW** |
| Ostermontag | `ostermontag` 재사용 |
| 1. Mai (Tag der Arbeit) | `erster_mai` 재사용 |
| Christi Himmelfahrtstag | `christi_himmelfahrt` 재사용 |
| **Pfingstsonntag** | **NEW** |
| Pfingstmontag | `pfingstmontag` 재사용 |
| Tag der deutschen Einheit | `tag_der_deutschen_einheit` 재사용 |
| Reformationsfest | `reformationstag` 재사용 (법문 명칭은 „Reformationsfest“ — 표시명 차이만 있고 날짜 동일) |
| 1. Weihnachtsfeiertag | `erster_weihnachtstag` 재사용 |
| 2. Weihnachtsfeiertag | `zweiter_weihnachtstag` 재사용 |

- NEW 키 필요 항목: Ostersonntag, Pfingstsonntag (둘 다 일요일이라 휴무 효과는 없지만 법정 공휴일로 명시됨). 토큰명은 제안하지 않음.
- 예고 키 `mariae_himmelfahrt`, `buss_und_bettag` 는 BB 에서 쓰이지 않음.

## F. 관보(GVBl.) 접근성

- 관보 포털: BRAVORS „Veröffentlichungsblätter“
  - 연도별 목록: https://bravors.brandenburg.de/de/veroeffentlichungsblaetter_chronologisch — 링크된 연도 **1994–2026** (1990–1993 연도 링크는 목록에 없음).
  - 2026 연도 페이지(`…/chronologisch/2026`, 200, 55,727 B): 정적 HTML 에 PDF 직링크 포함. GVBl. 링크 96개 (Teil I 39, Teil II 57) 외 Amtsblatt 등.
  - PDF URL 패턴 (관측): `/fm/76/GVBl_I_<Nr>_<Jahr>.pdf` (예: `GVBl_I_01_2026.pdf`, `GVBl_I_13_2015.pdf`).
  - 전문검색 폼(`veroeffentlichungsblaetter_einfache_suche`)은 POST 폼 — 이번에 사용하지 않음.
- 딥링크: 가능. JS 셸 아님 (포털 페이지 모두 정적 HTML 에 본문·링크 존재).
- 인증/속도 제한: 관측되지 않음 (전 요청 200 또는 302, 3초 간격). 단, 법령 빠른검색 POST 는 세션 쿠키(`sixcms_project`) 없이 보내면 검색 결과 대신 빈 폼이 돌아왔다 (쿠키 포함 시 200, 결과 페이지로 이동).
- 최근 개정 공포 PDF 시도:
  - https://bravors.brandenburg.de/fm/76/GVBl_I_13_2015.pdf → **200, application/pdf, 128,605 B**, 1쪽. 내용: „Viertes Gesetz zur Änderung des Feiertagsgesetzes“ (§ 2 Abs. 2 Nr. 3 추가).
  - 이력 페이지에는 2003 개정 PDF(`/fm/76/GVBl_I_15_2003.pdf`) 링크도 있음 (미요청). 1991·1994·1997·1998 판에는 PDF 링크 없음.
- 의회 문서 서버 (Landtag Brandenburg Parlamentsdokumentation):
  - `https://www.parlamentsdokumentation.brandenburg.de/` → 200, 782 B, 웹서버 기본 테스트 페이지.
  - `/starweb/LBB/ELVIS/index.html` → 200, 283 B, 본문 없이 JS `location.href` 로 `/portal/browse.tt.html` 이동.
  - `/portal/browse.tt.html` → 200, 346,264 B, 정적 HTML 에 본문 있음 (Wahlperiode 1–8 검색 UI, „Anmelden“ 링크 있으나 열람에 로그인 필요 여부는 미확인).
  - GVBl. 사본 보관 여부: 이 페이지에서 GVBl./Verordnungsblatt 언급 없음. Drucksachen·Plenarprotokolle 중심으로 보이며 관보 사본은 없는 것으로 추정 [추론]. 검색 폼은 사용하지 않음.

---

## 요약 (5줄)

1. 주 전역 공휴일: 12개 (FTG § 2 Abs. 1; 포털 통합본 2015 개정판, 2020+ 목록 변경 없음 — 포털 기재)
2. 한정 공휴일(범위 밖) 제외: 0개 (8. Mai 등 § 2 Abs. 2 Gedenktage 는 공휴일 아님)
3. NEW 규칙 유형: 없음 (고정일 + 부활절 오프셋 0/−2/+1/+39/+49/+50 으로 충족)
4. NEW 키: 2개 — Ostersonntag, Pfingstsonntag
5. 관보 접근성: 개방 (BRAVORS 1994–2026 연도별 PDF 직링크, 정적 HTML, 인증·속도제한 미관측; 2015 개정 PDF 200/128,605 B)
