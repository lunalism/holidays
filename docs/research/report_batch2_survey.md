# 2차 배치 7 주(BB·HB·MV·SL·SN·ST·TH) 얕은 조사 — 배치 분할 판단용

- 측정 시점: 2026-09-30. `origin/main` = `be1c45fa8667fa60e71678a2e95dc3687ddf1388` (#119 머지).
- `git fetch --prune` 의 prune 은 `origin/data/de-source-selfcontain` 하나다(#119 머지 브랜치).
- 범위: 조사만 했다. 레포 변경·브랜치·PR 없음.
- 깊이: 현행 조문과 접근성까지다. 개정 체인과 verified 판정은 하지 않았다.
- 표기: 명령 출력·원문에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다. 「포털 기재」 는 통합본·포털이 적은 것을 체인 검증 없이 옮긴 것이다.
- 통합본(konsolidierte Fassung)은 이 레포에서 **2차 출처**다. 근거의 정본이 되려면 공포 관보가 필요하다.
- 재현 기록은 `~/holidays-reports/report_batch2_survey/` 에 있다.
  - 주별 원보고 `state_XX.md` 와 요청 로그 `state_XX_fetch.log`
  - G 의 `fapi_2026*`
  - 내가 한 교차 확인 `spotcheck.log`

## 방법과 한계
- 주별 A–F 는 병렬 에이전트 일곱이 조사했다(주당 하나, curl + 식별 UA + 호스트당 3 초 간격, 요청 약 25 회 상한, 403/429/인증/JS 셸에서 중단).
- 아래 주별 절은 각 `state_XX.md` 를 제목 단계만 한 칸 내려 그대로 옮긴 것이다.
- G(feiertage-api 2026)는 내가 일곱 주를 한 스크립트로 받았다(`fapi_2026.sh`).
- **내가 공식 출처로 직접 다시 확인한 것**(`spotcheck.log`, 2026-09-30):
  - BB BRAVORS `ftg_2015` § 2 에 「der Ostersonntag」 「der Pfingstsonntag」 「das Reformationsfest (31. Oktober)」 이 있다.
  - SN REVOSax `3997-SaechsSFG` 에 「Buß- und Bettag」(날짜 정의 없이 이름만)와 「Fronleichnam (nur in den vom Staatsministerium des Innern …)」 이 있다.
  - MV GVOBl. 2022 Nr. 31(263,235 B)에 「Nach Nummer 1 wird folgende Nummer 2 eingefügt: „2. der Frauentag (8. März),“」 가 있다.
  - HB Brem.GBl. 2018 Nr. 63(241,672 B)에 「§ 2 Absatz 1j wird wie folgt neu gefasst: der Reformationstag.」 가 있다.
  - 넷 다 에이전트 보고와 일치한다.
- **요청 로그의 한계**
  - 에이전트들이 세션 scratchpad 를 공유해, 한 에이전트의 fetch 도우미 스크립트를 다른 에이전트가 덮어썼다.
  - 그 결과 요청 일부가 남의 로그에 기록됐고, 일부 행은 지워졌다(MV 에이전트가 자기 로그에서 타 주 행 약 45 건을 삭제). 여러 로그는 터미널 출력에서 복원됐다(각 로그 머리말에 적혀 있다).
  - **따라서 `state_XX_fetch.log` 는 요청 전수가 아닐 수 있다.**
  - 에이전트 합산으로는 같은 호스트(Wikipedia) 간격 3 초가 한 번 지켜지지 않았다(TH 보고).
  - [추론] 다음 배치에서는 에이전트마다 scratch 디렉터리를 따로 둔다.
- 일부 에이전트는 URL 을 찾으려고 Wikipedia·검색엔진을 썼다. 내용 판독은 각 보고가 밝힌 출처에서 했다.
- 비공식 통합본은 TH 가 kirchenrecht-ekm.de, ST 가 gesetze.co 를 썼다. 각 보고에 「비공식」 으로 표시돼 있다.

## 사전 확인

### 규칙 유형 — 지금 있는 것(잣대)
규칙 유형은 공용 core 가 아니라 **주마다 `rules/de_*/feed.py`** 가 구현한다. 전부 같은 꼴이다.

| 유형 | 자리 |
|---|---|
| 고정 월·일 | `_load(SOLAR_PATH, "month", "day")` → `date(year, month, day)` (예: `rules/de_he/feed.py:131, 153`) |
| 부활절 오프셋(일) | `_load(EASTER_PATH, "easter_offset")` → `easter + timedelta(days=offset)` (예: `rules/de_he/feed.py:135, 155`) |
| 일회성(연도 접미사 key) | `rules/de_be/feed.py:137–148`(`_designated`, key 가 `_{year}` 로 끝나야 함) · `:169`. de_be 에만 있다 |

- **없는 것**: 연도 경계(유효 시작·끝)와 요일 기반 계산.
  - `valid_from`·`until` 류 필드가 `rules/de*/feed.py` 에 없다(grep).
  - key 규약은 `rules/de/feed.py:106` `[a-z][a-z_]*`, `rules/de_be/feed.py:88` `[a-z][a-z_]*(?:_\d{4})?`.
- [추론] 「NEW 규칙 유형」 은 core 가 아니라 해당 주 `feed.py` 로더·계산과 그 테스트를 새로 쓰는 일이다. 세 번째로 쓰이면 공용화 판단이 붙는다.

### 쓰이는 key(rules/de*/)와 예고된 key
- 공통 9: neujahr, karfreitag, ostermontag, christi_himmelfahrt, pfingstmontag, erster_mai, tag_der_deutschen_einheit, erster_weihnachtstag, zweiter_weihnachtstag
- 주 고유: heilige_drei_koenige(bw·by), fronleichnam(bw·by·he·nw·rp), allerheiligen(bw·by·nw·rp), reformationstag(hh·ni·sh), frauentag(be), achter_mai_2020·achter_mai_2025·siebzehnter_juni_2028(be)
- 예고: `rules/de/solar_holidays.yaml:23–24` 「주별 피드에서 Mariä Himmelfahrt(→ mariae_himmelfahrt), Buß- und Bettag (→ buss_und_bettag) 이 처음 쓰게 된다.」

---

## 요약 표

| 주 | 현행 조문 출처 | 주 전역 | 한정(제외) | NEW 규칙 유형 | NEW key | 2020 이후 변경(포털 기재) | 관보 접근 |
|---|---|---|---|---|---|---|---|
| BB | 공식(BRAVORS 통합본) | 12 | 0 | 없음 | **2**: Ostersonntag, Pfingstsonntag | 목록 변경 없음(마지막 2015) | open — BRAVORS 1994–2026 호별 PDF 딥링크 |
| HB | 공식 포털이나 **현행판(2025-06-30~) 500**, 2020-03-14 판으로 봄 | 10 | 0 (§ 8 종교 축일·§ 7a 8. Mai Gedenktag 는 공휴일 아님) | 없음 | 0 | 목록 변경 없음(Reformationstag 는 2018) | open — gesetzblatt.bremen.de 2013–2026 PDF |
| MV | 공식 통합본 **못 받음**(JS 셸). 관보 원문 + 공식 색인 | 11 | 0(미확정) | **1**: 연도 경계 — Frauentag 2023 부터 | 0 (frauentag 재사용) | Frauentag 신설, GVOBl. 2022 Nr. 31 S. 427 | partial — 관보 2014–2026 PDF open, 법령 포털·ParlDok JS |
| SL | **공식 출처 없음**(JS 셸). 1976 원법 스캔에서 [추론] | 12 [추론] | 0 | 없음 [추론] | 0 (예고 key mariae_himmelfahrt 첫 사용) | 찾지 못함(관보 전문검색) | open — 관보 1999+ · 대학 아카이브 1920–1998, PDF 링크는 세션 필요 |
| SN | 공식(REVOSax) | 11 | 1: Fronleichnam(지정 지역) | **1**: 요일 기반 — Buß- und Bettag | 0 (예고 key buss_und_bettag 첫 사용) | 목록 변경 없음(마지막 2002). 8. Mai 는 2025 부터 Gedenktag | partial — REVOSax open, 관보는 유료 판매(미리보기 PDF 는 무료) |
| ST | **공식 출처 없음**(JS 셸). 비공식 gesetze.co | 11 | 0 (§ 2a 8. Mai·17. Juni Gedenktage 는 공휴일 아님, 2026 신설) | 없음 | 0 | 목록 변경 없음 | blocked/partial — 관보는 등록·유료 출판사, 사이트 접속 실패, PADOKA JS |
| TH | **공식 출처 없음**(JS 셸). 비공식 kirchenrecht-ekm.de | 11 | 1: Fronleichnam(Eichsfeld 등) | 없음 (Weltkindertag 2019~ 라 발행 하한 2020 에서 경계 불필요) | **1**: Weltkindertag(9. 20.) | 발행 범위 안 변경 없음(Weltkindertag 2019) | partial — ParlDok PDF 직링크 200, 검색은 JS, 법령 포털 JS |

- 조사한 주는 7 이다.
- **현행 조문을 공식 출처에서 못 얻은 주는 SL·ST·TH 3 이다.**
- 부분으로 얻은 주는 둘이다: HB(구판), MV(관보 원문·색인만).

G(feiertage-api 2026 대조, `fapi_2026_summary.txt`):
- 일곱 주 모두 주 전역 목록과 API 의 hinweis 공란 항목이 **일치**한다.
- API 의 hinweis 항목(SN·TH 의 Fronleichnam)은 각 보고의 「한정·제외」 와 일치한다.
- 차이 0.
- SL 은 보고 목록이 [추론] 이라, 이 일치는 추론을 받치는 2차 대조일 뿐이다.

**key 혼동 주의**: 8. Mai·17. Juni 가 HB(§ 7a)·SN(2025~)·ST(§ 2a, 2026~)에서 **기념일(Gedenktag)**로 들어왔다. 공휴일이 아니다. de_be 의 `achter_mai_2020`·`siebzehnter_juni_2028`(공휴일, 일회성)과 이름이 겹친다.

## 묶음 제안 [추론] — 사람이 정한다

비용 순(새 규칙 유형 > 새 key > 기존만)으로 나누고, 그 안에서 관보 접근 순으로 줄 세웠다.

| 묶음 | 주 | 까닭 |
|---|---|---|
| 1. 기존 유형·기존 key 만 | **HB** → SL → ST | HB 는 관보 open, 현행판 재확인만 필요하다. SL 은 관보 open 이나 현행 조문 출처가 없어 체인을 1976 원법부터 관보로 이어야 한다. ST 는 조문·관보 둘 다 막혀 가장 비싸다 |
| 2. 새 key(유형은 기존) | **BB** → TH | BB 는 관보·통합본 둘 다 open, key 2 개 승인이 필요하다(부활절 오프셋 0·49 는 기존 유형). TH 는 key 1 개, 조문 출처가 비공식이고 관보 partial |
| 3. 새 규칙 유형(feed.py 로더·계산 신설) | MV, SN | MV 는 연도 경계(Frauentag 2023~, 관보 확인), SN 은 요일 계산(Buß- und Bettag, 조문에 날짜 정의 없음). 각자 안전망 먼저 |

- 관보 접근만 보면 다르게 묶을 수 있다: open 인 BB·HB(·SL 관보)를 먼저 하고, 막힌 ST·TH 는 접근 경로를 찾을 때까지 미룬다.
- MV 는 새 유형이지만 필요한 관보(2022 Nr. 31)가 이미 확보돼 있다. 유형 설계만 정하면 비용이 작다.

---

# 주별 절

## Brandenburg (BB) — 공휴일 법령 조사

- 조사일: 2026-09-30 (UTC 09:25–09:28)
- 요청 로그: `~/holidays-reports/report_batch2_survey/state_BB_fetch.log` (총 16건, 403/429 없음)
- 태그 규약: 직접 관측한 내용은 태그 없음, 도출·추정한 문장은 [추론].

---

### A. 법령

- 공식 명칭: „Gesetz über die Sonn- und Feiertage (Feiertagsgesetz - FTG)“
- 원 공포: „vom 21. März 1991 (GVBl.I/91, [Nr. 06], S.44)“
- 포털 표기 최종 개정: „zuletzt geändert durch Gesetz vom 30. April 2015 ( GVBl.I/15, [Nr. 13] )“
- 공식 주법 포털: BRAVORS (Brandenburgisches Vorschriftensystem)
  - 현행 통합본: https://bravors.brandenburg.de/gesetze/ftg_2015 (HTTP 200, 정적 HTML에 전문 포함, 접근일 2026-09-30)
  - 개정 이력: https://bravors.brandenburg.de/gesetze/ftg_2015/list
  - 참고: `/gesetze/ftg`, `/gesetze/feiertagsg` 는 302 → `http://bravors.brandenburg.de:443` (존재하지 않는 경로를 홈으로 돌리는 것으로 보임 [추론]). 올바른 경로는 포털의 빠른검색(POST 폼, 세션 쿠키 필요)으로 찾았다.
- **주의: 이 통합본(Lesefassung)은 이 레포에서 2차 출처다.** 정본은 GVBl. 공포문이다. 아래 B·C 의 내용은 모두 통합본/포털 기재에 근거한다.

### B. 현행 통합본의 공휴일 목록 (§ 2)

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

### C. 2020-01-01 이후 효력이 있는 변경 / 1990년 이후 도입 항목 / 2020+ 1회성 공휴일

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

### D. 항목별 필요 규칙 유형

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

### E. 키 매핑

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

### F. 관보(GVBl.) 접근성

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

### 요약 (5줄)

1. 주 전역 공휴일: 12개 (FTG § 2 Abs. 1; 포털 통합본 2015 개정판, 2020+ 목록 변경 없음 — 포털 기재)
2. 한정 공휴일(범위 밖) 제외: 0개 (8. Mai 등 § 2 Abs. 2 Gedenktage 는 공휴일 아님)
3. NEW 규칙 유형: 없음 (고정일 + 부활절 오프셋 0/−2/+1/+39/+49/+50 으로 충족)
4. NEW 키: 2개 — Ostersonntag, Pfingstsonntag
5. 관보 접근성: 개방 (BRAVORS 1994–2026 연도별 PDF 직링크, 정적 HTML, 인증·속도제한 미관측; 2015 개정 PDF 200/128,605 B)

### G. feiertage-api 2026 대조
일치 — API 12(Ostersonntag·Pfingstsonntag 포함), 전부 hinweis 공란.

---

## Bremen (HB) — 공휴일 법령 조사 (batch 2 survey)

- 조사일: 2026-09-30 (UTC 09:25–09:32)
- 요청 로그: `state_HB_fetch.log` (총 20회 HTTP 요청, 그 외 문서 ID 검색용 WebSearch 3회)
- 표기: [추론] = 직접 관찰하지 않고 도출한 문장. 태그가 없는 문장은 이번 세션에서 받은 응답을 직접 확인한 내용이다.

### A. 법령

- 정식 명칭(포털 표기): „Gesetz über die Sonn-, Gedenk- und Feiertage“ vom 12. November 1954. 공식 약칭은 문서에서 확인하지 못함.
  - 2018년 개정 관보(아래 C)는 „Gesetz über die Sonn- und Feiertage“라는 옛 이름을 씀. 이름에 „Gedenk-“가 붙은 것은 2020-03-14 판부터 [추론: 2020 판 표제가 „Die Sonntage und die staatlich anerkannten Gedenk- und Feiertage“로 바뀌고 § 7a가 들어간 것을 보고 판단].
- 공식 법령 포털: Transparenzportal Bremen (`www.transparenz.bremen.de`), Fundstelle „SaBremR 113-c-1“
- 포털에서 확인한 통합본(consolidated) 판:

| 문서 ID | PDF URL (template=00_html_to_pdf_d) | „Inkrafttreten“ 기재 | 결과 |
|---|---|---|---|
| 74780 | `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.74780.de&template=00_html_to_pdf_d` | 04.06.2013 | 200 PDF, 쪽마다 „außer Kraft“ |
| 87915 | `…gsid=bremen2014_tp.c.87915.de&template=00_html_to_pdf_d` | 28.07.2015 | 200 PDF, 쪽마다 „außer Kraft“ |
| 145882 | `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.145882.de&template=00_html_to_pdf_d` | 14.03.2020 | 200 PDF (8쪽), 쪽마다 „außer Kraft“ |
| 296390 | `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.296390.de&template=00_html_to_pdf_d` | (확인 못 함) | **500 „db-connection failed“, 재시도해도 500** |

- **현행판은 받지 못했다.** 검색엔진 스니펫에 따르면 145882 판은 „14.03.2020 bis 29.06.2025“ 동안 유효했고, 296390 판은 Inkrafttreten 30.06.2025이다. 이 날짜들은 포털을 직접 보고 확인한 것이 아니라 스니펫에서 가져왔다. 145882 PDF 쪽마다 „außer Kraft“ 표시가 있는 것은 직접 확인했다.
  - 그래서 아래 B는 **2020-03-14 판(145882, 이미 효력 상실)** 기준이다. 2025-06-30 판에서 § 2 목록이 바뀌었는지는 확인하지 못했다.
  - 2025년 관보를 제목어 „Feiertage“·„Gedenk“로 검색했더니 0건이었다(로그 #17, #18). [추론] 2025-06 개정은 제목에 Feiertag가 들어가지 않는 개정법(Artikelgesetz), 예를 들어 소관·관할 정비일 수 있다. § 2 목록이 바뀌었을 가능성은 낮지만 검증되지 않았다.
  - 모든 판의 머리글에 „Zuletzt geändert durch … Geschäftsverteilung des Senats vom 02.09.2025 (Brem.GBl. S. 674)“가 똑같이 찍혀 있다. [추론] 이 줄은 해당 판이 아니라 포털 메타데이터를 보여 주는 것으로 보인다.
- 접근일: 2026-09-30
- **통합본은 이 레포에서 2차 출처다.** 법적 효력이 있는 것은 Brem.GBl. 공포본이다. 이 레포 YAML `source`에는 가능하면 관보 판면을 인용해야 한다.
- 메타정보 페이지(`/metainformationen/…-87915`, `…-145882`)는 둘 다 500 „db-connection failed“였다. 포털 자체 검색도 503 „Die Suche ist leider momentan nicht erreichbar.“였다. [추론] 서버 쪽 일시 장애로 보이며 차단 신호(403/429)는 아니다. 그래도 규칙에 따라 해당 경로는 더 시도하지 않았다.

### B. 공휴일 목록 (2020-03-14 판, § 2 Abs. 1 „Staatlich anerkannte Feiertage sind:“)

| # | 법문 표현 | 범위 |
|---|---|---|
| a | „der Neujahrstag,“ | 주 전역 |
| b | „der Karfreitag,“ | 주 전역 |
| c | „der Ostermontag,“ | 주 전역 |
| d | „der 1. Mai,“ | 주 전역 |
| e | „der Himmelfahrtstag,“ | 주 전역 |
| f | „der Pfingstmontag,“ | 주 전역 |
| g | „der 3. Oktober - Tag der deutschen Einheit -,“ | 주 전역 |
| h | „der 1. Weihnachtstag,“ | 주 전역 |
| i | „der 2. Weihnachtstag,“ | 주 전역 |
| j | „der Reformationstag.“ | 주 전역 |

- 주 전역 공휴일: 10개. 지방자치단체나 지역으로 한정된 공휴일은 § 2에 없다.
- § 2가 아닌 다른 조항에 나오는 날(모두 **범위 밖**):
  - § 7a Abs. 1 „Der 8. Mai als Tag der Befreiung vom Nationalsozialismus …“ „… ist staatlich anerkannter Gedenktag.“ 이것은 공휴일이 아니라 **기념일(Gedenktag)**이다. 근로자에게는 „soweit betriebliche Notwendigkeiten nicht entgegenstehen“ 조건으로 기념행사 참석 기회를 줄 뿐이다. → 범위 밖(공휴일 아님)
  - § 8 Abs. 1 religiöse Feiertage는 해당 교파 신자에게만 적용되고, 예배 장소 인근 소음 금지와 § 9/§ 10 예배 참석·수업 면제가 효과다. → **범위 밖(집단 한정)**
    - „Am 31. Oktober - Reformationsfest - (evangelischer Feiertag)“ (§ 2 j와 같은 날이며, 그쪽이 주 전역 공휴일이다)
    - „am Buß- und Bettag - (evangelischer Feiertag)“
    - „am Donnerstag nach Trinitatis - Fronleichnam - (katholischer Feiertag)“
    - „am 1. November - Allerheiligen - (katholischer Feiertag)“
    - 유대교 축일: Rosch Haschana, Jom Kippur, Sukkoth, Schemini Azereth, Simchat Thora, Pessach, Schawuoth
  - § 8 Abs. 2 이슬람 축일(Opferfest, Ramadanfest, Aschura)과 Abs. 3 알레비 축일(Aşure-Tag, Hızır-Lokması, Nevruz) → 범위 밖(집단 한정)
  - § 6/§ 7 Volkstrauertag, Totensonntag, 24.12.는 행사·도박 금지일일 뿐 공휴일이 아니다. → 범위 밖
- 참고: 2026년 공휴일 API 캡처(`fapi_2026_HB.json`)도 같은 10개를 나열한다(2차 출처 비교용).

### C. 2020-01-01 이후 영향을 주는 변경

1. **Reformationstag(10/31) 상설 공휴일화**. 1990년 이후 도입되어 2020년 이후에도 효력이 있다.
   - 내용: § 2 Abs. 1 j를 „der Reformationstag.“로 새로 씀. 이전 판(2015-07-28 판)의 j는 „der 31. Oktober 2017 (500. Jahrestag der Reformation).“로, 2017년 한 번만 쉬는 날이었다.
   - 적용 연도: 2018년부터. 관보 원문에 „Das Gesetz tritt am Tag nach seiner Verkündung in Kraft.“, 공포일 „Verkündet am 28. Juni 2018“로 되어 있다. 따라서 발효일은 2018-06-29이다 [추론: 공포일+1일로 계산]. 2020년 이후 모든 연도에 적용된다.
   - 개정법: „Gesetz zur Änderung des Gesetzes über die Sonn- und Feiertage Vom 26. Juni 2018“, Brem.GBl. 2018 Nr. 63, S. 302.
   - 출처 등급: 포털 통합본 각주에 „Gesetzes vom 26.06.2018 (Brem.GBl. S. 302)“로 적혀 있다(**포털 기재**). 관보 PDF 원문에서도 같은 내용을 직접 확인했다(아래 F). 이 한 건은 관보로 확인했지만 개정 이력 전체를 추적하지는 않았다.
2. **§ 7a 8. Mai Gedenktag 신설**(2020-03-14 판)
   - 내용: 공휴일이 아닌 기념일이다. 공휴일 목록은 바뀌지 않는다.
   - 개정법: 이번에 받은 통합본 PDF에는 개정법 인용이 없어 확인하지 못했다. 발효일은 **포털 기재** „Inkrafttreten: 14.03.2020“이다.
   - 이 레포의 `achter_mai_2020`(de_be 일회성 공휴일)와는 성격이 다르다. Bremen 2020년 5월 8일은 휴일이 아니다 [추론: § 2 목록에 없고 § 7a는 휴무를 부여하지 않는 조문이라 판단].
3. **2025-06-30 판**(ID 296390): 무엇이 바뀌었는지 모른다(A 참고). 미확인.
4. 2020년 이후 일회성 공휴일: 2020-03-14 판 § 2에는 없다. 2025-06-30 이후 판은 확인하지 못했다.
   - § 12 Nr. 2에 따라 Senat는 „aus besonderem Anlaß im Einzelfall“ 이 법의 규정을 다른 날에도 적용한다고 선언할 수 있다. [추론] 이 수권은 § 3 보호(휴식일) 규정을 적용하는 것이지 § 2 공휴일을 추가하는 것이 아니다. 이 방식의 공휴일 사례가 있는지는 조사하지 않았다.

### D. 필요한 규칙 유형 (주 전역 10개)

| 항목 | 규칙 | 레포 지원 |
|---|---|---|
| Neujahrstag | 고정 01-01 | (1) 있음 |
| Karfreitag | 부활절 −2 | (2) 있음 |
| Ostermontag | 부활절 +1 | (2) 있음 |
| 1. Mai | 고정 05-01 | (1) 있음 |
| Himmelfahrtstag | 부활절 +39 | (2) 있음 |
| Pfingstmontag | 부활절 +50 | (2) 있음 |
| 3. Oktober | 고정 10-03 | (1) 있음 |
| 1. Weihnachtstag | 고정 12-25 | (1) 있음 |
| 2. Weihnachtstag | 고정 12-26 | (1) 있음 |
| Reformationstag | 고정 10-31 | (1) 있음 |

- 새로운 규칙 유형: **없음**.
  - Reformationstag는 2018년 발효라서 2020년 이후 구간 안에 시작일이나 종료일이 없다. 유효기간 규칙이 필요 없다.
  - 요일 기반 계산이 필요한 항목(Buß- und Bettag 등)은 § 8 한정 항목뿐이고 모두 범위 밖이다.
- 단서: 2025-06-30 판에서 목록이 바뀌었다면 이 결론은 달라질 수 있다(미확인).

### E. 키 매핑

| 항목 | 키 | 판정 |
|---|---|---|
| Neujahrstag | `neujahr` | 기존 재사용 |
| Karfreitag | `karfreitag` | 기존 재사용 |
| Ostermontag | `ostermontag` | 기존 재사용 |
| 1. Mai | `erster_mai` | 기존 재사용 |
| Himmelfahrtstag | `christi_himmelfahrt` | 기존 재사용 (법문은 „Himmelfahrtstag“, 같은 날) |
| Pfingstmontag | `pfingstmontag` | 기존 재사용 |
| 3. Oktober | `tag_der_deutschen_einheit` | 기존 재사용 |
| 1. Weihnachtstag | `erster_weihnachtstag` | 기존 재사용 |
| 2. Weihnachtstag | `zweiter_weihnachtstag` | 기존 재사용 |
| Reformationstag | `reformationstag` | 기존 재사용 |

- NEW 키: **없음**. 미리 알려 둔 `buss_und_bettag`는 HB에서는 § 8 집단 한정이라 쓰지 않는다.

### F. 관보(Brem.GBl.) 접근성

- 포털: `https://www.gesetzblatt.bremen.de/` (200, 정적 HTML). 페이지에 „Es wird in elektronischer Form geführt …“라고 적혀 있다.
  - 호별 PDF는 `/fastmedia/218/YYYY_MM_DD_GBl_Nr_NNNN_signed.pdf` 형식의 **직접 링크**로, 정적 HTML에 그대로 있다. JS 셸이 아니다.
  - 연도별 합본 PDF 링크는 2013–2025년치가 정적 HTML에 있다. 예: `/fastmedia/220/2018_gesetzblatt.pdf`, `/fastmedia/220/Gesetzblatt_Bremen_2025.pdf`. 링크만 보았고 내려받지는 않았다.
  - 연도 선택 목록은 2013–2026년이다. 2012년 이전 관보는 이 포털에서 보지 못했다. [추론] 2012년 이전은 다른 경로가 필요하다.
  - 제목어 검색은 GET 파라미터(`sv[suchbegriff]`, `sv[suchbegriff_jahr][0]`)로 동작하고 결과 URL을 그대로 딥링크할 수 있다. 연도 파라미터를 여러 개 주면 첫 연도만 적용됐다(로그 #13).
- **개정 PDF 1건 받음** (holiday 목록의 가장 최근 확인된 개정)
  - `https://www.gesetzblatt.bremen.de/fastmedia/218/2018_06_28_GBl_Nr_0063_signed.pdf` → **200, application/pdf, 241,672 bytes**, 1쪽, 판면 S. 302
  - 원문 발췌: „1. § 2 Absatz 1j wird wie folgt neu gefasst: der Reformationstag.“
- 인증이나 rate-limit: gesetzblatt.bremen.de에 3초 간격으로 9회 요청했고 모두 200이었다. 403/429나 로그인 요구는 없었다.
- transparenz.bremen.de(법령 포털) 관찰 결과:
  - 404: 추측한 `/suche` 경로
  - 503: 사이트 검색
  - 500 „db-connection failed“: 메타정보 페이지 2건, 현행판 PDF 2회
  - 200: 구판 PDF 3건
  - 403/429는 없었다. 장애성 오류에 해당하므로 규칙대로 재시도를 최소화하고 중단했다.
- 의회 문서 서버: `https://www.bremische-buergerschaft.de/drs_abo/Drs-18-896_3d1.pdf` → 200, application/pdf, 109,730 bytes
  - 2013년 개정안 „Mitteilung des Senats vom 7. Mai 2013“(Drucksache 18/896)이다. 법안 원문은 의회 서버에서도 받을 수 있다.
  - 관보 사본 자체를 이 서버가 싣고 있는지는 확인하지 않았다.

### 운영 메모
- scratchpad 공유 문제: 공유 scratchpad의 fetch 스크립트(`f.sh`)가 다른 병렬 에이전트에 의해 덮어써졌다. 그 때문에 초기 로그 파일이 유실됐고, 요청 2건(#16, #17)은 다른 에이전트의 `scratchpad/st.log`에 기록됐다. `state_HB_fetch.log`는 세션 출력(curl `-w` 결과)으로 다시 만들었으며, 그 사실을 파일 머리말에 적어 두었다.
- 작업용 PDF와 텍스트는 scratchpad/hb_only에만 두었다. 보고서 폴더에는 원문을 덤프하지 않았다.

### 요약 (5줄)
1. 주 전역 공휴일 10개 (2020-03-14 통합본 § 2 기준. 2025-06-30 현행판은 포털 500으로 받지 못해 미확인)
2. 한정 항목 제외: § 8 종교 축일(Buß- und Bettag, Fronleichnam, Allerheiligen, 유대교·이슬람·알레비 축일)과 § 7a 8. Mai Gedenktag(공휴일 아님)은 모두 범위 밖
3. 새로운 규칙 유형: 없음 (고정일과 부활절 오프셋만 필요. Reformationstag는 2018년 발효라 2020년 이후 구간에 유효기간 경계 없음)
4. NEW 키: 없음 (10개 모두 기존 키로 재사용)
5. 관보 접근: 열림. gesetzblatt.bremen.de의 정적 HTML과 직접 PDF 링크로 2013년부터 볼 수 있고, 2018 Nr. 63 S. 302를 200으로 받음. 법령 포털(통합본)은 부분 접근: 구판은 받았고 현행판·메타정보·검색은 500/503.

### G. feiertage-api 2026 대조
일치 — API 10, 전부 hinweis 공란. (보고 목록은 2020-03-14 판 기준)

---

## Mecklenburg-Vorpommern (MV) — Feiertagsgesetz 조사

- 조사일(접근일): 2026-09-30 (UTC 09:25–09:31)
- 요청 로그: `state_MV_fetch.log` (MV 관련 요청 10건, 전부 기록)
- 표기: [추론] = 직접 관찰이 아니라 유도한 문장. 태그 없는 문장 = 이번 조사에서 직접 관찰한 것.
- 인용문은 독일어 원문 그대로, 15단어 이하.

---

### A. 법령

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

#### 관보 색인(Stand 9/2026)에 기재된 FTG M-V 개정 이력 (포털 기재)
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

### B. 현행 공휴일 목록 (§ 2 Abs. 1)

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

### C. 2020-01-01 이후 변경 / 1990년 이후 도입 항목 / 일회성 공휴일

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

### D. 항목별 필요한 규칙 유형

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

### E. 키 재사용 여부

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

### F. 관보(GVOBl. M-V) 접근성

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

### 요약 (5줄)
1. 주 전역 공휴일 11개 (§ 2 Abs. 1 Nr. 1–11; 개수와 Frauentag 문구는 관보 원문, 나머지 명칭은 비공식 목록 기준)
2. 범위 한정 제외 항목: 0 확인 (조문 미관찰로 지역·종교 한정 항목 존재 여부는 미확정)
3. NEW 규칙 유형: 1 — Frauentag(03-08)의 유효 시작 연도 2023 (2022-07-13 시행, 2022 Nr. 31 S. 427)
4. NEW 키: 0 (`frauentag` 포함 전부 기존 키 재사용 가능). 2020·2025 5월 8일 일회성 공휴일 없음 [추론]
5. 관보 접근: partial — regierung-mv.de 에서 2014–2026 PDF 공개(정적·딥링크·무인증). 법령 포털 landesrecht-mv.de 와 Landtag ParlDok 은 JS 셸

### G. feiertage-api 2026 대조
일치 — API 11(Frauentag 03-08 포함), 전부 hinweis 공란.

---

## Saarland (SL): 공휴일 법령 조사

- 조사일: 2026-09-30 (접근 시각 UTC는 `state_SL_fetch.log` 참조)
- 요청 수: 19회 (상한 25회). 403/429 응답은 없었다. landtag-saar.de 1회는 연결 실패(000)였고 재시도하지 않았다.
- 표기: 태그가 없는 문장은 직접 관측한 내용이다. **[추론]**은 관측 결과에서 도출했거나 배경지식에 기댄 내용이다.

---

### A. 법령

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

### B. 공휴일 목록

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

### C. 2020-01-01 이후 변경 및 1회성 공휴일

- **포털 기재 사항: 확보 불가.** 공식 포털이 JS 셸이라 „포털 기재“ 형식의 개정 이력을 얻을 수 없었다.
- **관보 전문검색 (Verkündungsportal, 관측):**
  - „Feiertagsgesetz“ 검색은 20건이다. 가장 최근 항목은 Drucksache 15/1464(2015-07-09)와 Amtsblatt I 2015 Nr. 33(2015-11-19)이다. **2016년 이후 결과는 0건**이다.
  - „Feiertagsgesetzes“ 검색도 결과가 20건으로 같다.
  - „Feiertag“ 검색은 423건이다. 상위 25건(2017~2025년 Drucksachen/Protokolle)의 제목에는 공휴일 추가·1회성 지정이 없다. 다만 Amtsblatt 항목은 상위 25건에 나오지 않아, 423건 전체는 **검토하지 못했다**.
- **판단 [추론]:** 2020년 이후 SFG §2 Abs. 1의 목록 개정은 **확인되지 않았다.** 이 검색은 법안 본문까지 색인한다(예: 2012년 도박법 법안이 본문 언급만으로 검색됨). 그러므로 개정법이 있었다면 „Feiertagsgesetz(es)“로 걸렸을 가능성이 높다. 단, 색인 범위는 검증하지 않았다.
- **2020년 이후 1회성 공휴일:** 발견하지 못했다. §2 Abs. 2에 따른 명령(Verordnung)은 법률명을 포함하지 않을 수 있으므로 **부재를 입증한 것은 아니다** [추론].

---

### D. 주 전역 항목별 규칙 유형

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

### E. 키 매핑

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

### F. 관보 접근성

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

### 요약 (5줄)
1. 주 전역: 12개 [추론]. 현행 조문 미확보, 1976 원문 13개에서 17. Juni→10월 3일, Buß- und Bettag 폐지로 판단.
2. 지역 한정 제외: 0건 (1976 원문 §2 Abs. 1 기준).
3. NEW 규칙 유형: 없음 (모두 고정일 또는 부활절 오프셋. 2020년 이후 변경·1회성 공휴일 발견 안 됨, 단 명령에 의한 1회성 지정의 부재는 입증 못 함).
4. NEW 키: 없음 (mariae_himmelfahrt 첫 사용, 나머지 11개는 기존 키).
5. 관보 접근: open (Verkündungsportal 1999~, uni-saarland 1920~1998, PDF 세션 의존). 통합본 포털 recht.saarland.de는 JS 셸로 blocked.

### G. feiertage-api 2026 대조
일치 — API 12(Fronleichnam·Mariä Himmelfahrt·Allerheiligen 포함), 전부 hinweis 공란. 보고 목록이 [추론] 이라 이 대조는 추론을 받치는 2차 대조다.

---

## Sachsen (SN) — 공휴일 법령 조사 (batch2 survey)

- 조사일: 2026-09-30 (요청 시각은 `state_SN_fetch.log` 참조, UTC)
- 범위: 조사만. 레포(/Volumes/Data/dev/holidays)는 수정하지 않음.
- 표기: 직접 관측한 내용은 태그 없이, 관측에서 끌어낸 판단은 **[추론]** 으로 표시.
- 로그 관련 주의: 공유 scratchpad 충돌로 최초 로그 파일이 유실되어, 09:29Z 이전 항목은 각 요청 직후 터미널에 찍힌 같은 행으로 재구성함(로그 머리말에 명시).

---

### A. 법령 (Statute)

- 공식 명칭(포털 표기): „Gesetz über Sonn- und Feiertage im Freistaat Sachsen (SächsSFG)“, „Vom 10. November 1992“.
  - 과제 설명의 „Sächsisches Sonn- und Feiertagsgesetz“는 통칭이고, REVOSax 표제는 위와 같음.
- 원 공포 출처(포털 기재): „SächsGVBl. 1992 Nr. 35, S. 536“, Fsn-Nr. 114-2.
- 현행 통합본(consolidated): REVOSax (Recht und Vorschriftenverwaltung Sachsen, 발행 Sächsische Staatskanzlei)
  - URL: https://www.revosax.sachsen.de/vorschrift/3997-SaechsSFG (HTTP 200, 2026-09-30 접속)
  - PDF 판: https://www.revosax.sachsen.de/vorschrift_gesamt/3997/48138.pdf (HTTP 200, application/pdf, 53,502 B, 4쪽)
  - 페이지 표기: „Rechtsbereinigt mit Stand vom 7. Mai 2025“, „Fassung gültig ab: 7. Mai 2025“
  - Vollzitat: „…zuletzt durch das Gesetz vom 23. April 2025 (SächsGVBl. S. 146) geändert…“
  - 역사적 판(Historische Fassungen) 목록: 21.11.1992–02.07.2002 / 03.07.2002–26.04.2008 / 27.04.2008–20.12.2010 / 21.12.2010–09.02.2013 / 10.02.2013–06.05.2025 / 07.05.2025–.
- **이 레포 기준에서 통합본은 2차 출처다.** REVOSax 통합본은 편집된 현행 텍스트이며, 법적 정본은 SächsGVBl.에 공포된 원 법률·개정법이다. 아래 B–E는 전부 통합본에서 읽은 것이다.
- 참고(발견 경로): REVOSax 검색은 POST 폼(CSRF 토큰 포함)이라 사용하지 않았음(로컬 권한 정책으로 전송 전 차단). 첫 시도한 ID 추측 URL(`/vorschrift/3853-…`)은 무관한 문서로 연결됨. 정확한 REVOSax URL은 de.wikipedia „Gesetzliche Feiertage in Deutschland“ 문서의 참고 링크에서 얻었고, 내용은 모두 REVOSax에서 직접 확인함(위키 내용은 근거로 쓰지 않음).

### B. 공휴일 목록 (현행 § 1 Abs. 1)

§ 1 Abs. 1 도입부: „Gesetzliche Feiertage sind:“ (전체 12개 항목)

| # | 법문 표현(인용) | 적용 범위 | 비고 |
|---|---|---|---|
| 1 | „Neujahr (1. Januar)“ | 주 전역 | |
| 2 | „Karfreitag“ | 주 전역 | |
| 3 | „Ostermontag“ | 주 전역 | |
| 4 | „Tag der Arbeit (1. Mai)“ | 주 전역 | |
| 5 | „Christi Himmelfahrt“ | 주 전역 | |
| 6 | „Pfingstmontag“ | 주 전역 | |
| 7 | „Fronleichnam (nur in den … durch Rechtsverordnung bestimmten Regionen)“ (생략부: 내무부 Staatsministerium des Innern) | **지역 한정** | **범위 밖** |
| 8 | „Tag der Deutschen Einheit (3. Oktober)“ | 주 전역 | |
| 9 | „Reformationsfest (31. Oktober)“ | 주 전역 | 법문 명칭은 Reformationstag 가 아니라 Reformationsfest |
| 10 | „Buß- und Bettag“ | 주 전역 | 법문에 날짜 정의 없음 (D 참조) |
| 11 | „1. Weihnachtstag (25. Dezember)“ | 주 전역 | |
| 12 | „2. Weihnachtstag (26. Dezember)“ | 주 전역 | |

- 주 전역 11개, 지역 한정 1개(Fronleichnam).
- Fronleichnam 대상 지역을 정하는 법규명령(Rechtsverordnung) 자체는 이번에 열람하지 않았음. 소르브 지역(Landkreis Bautzen)의 일부 지자체라는 통상 설명은 이번 조사에서 공식 출처로 확인하지 않음 **[추론/미확인]**. 범위 밖이므로 추가 확인하지 않음.
- 공휴일이 아닌 항목(참고, 모두 범위 밖):
  - § 2 Gedenk- und Trauertage: Volkstrauertag, Totensonntag, „der 8. Mai als Tag der Befreiung vom Nationalsozialismus…“ — 기념일이며 § 1의 gesetzliche Feiertage 가 아님.
  - § 2a: 지자체가 조례(Satzung)로 정할 수 있는 1989 평화혁명 „örtlicher Gedenktag“.
  - § 3 Religiöse Feiertage (Erscheinungsfest 6.1., Frühjahrsbußtag, Gründonnerstag, 공휴일이 아닌 곳의 Fronleichnam, Johannestag, Peter und Paul, Mariä Himmelfahrt, Allerheiligen, Mariä Empfängnis): 예배 참석을 위한 결석·결근권만 부여하며 공휴일이 아님.

### C. 2020-01-01 이후 변경 / 1990년 이후 도입분 / 2020+ 일회성 공휴일

모두 **포털 기재** 사항이며 개정 연쇄를 검증하지는 않았다.

1. **§ 1 Abs. 1 (공휴일 목록)** — 포털 각주: „§ 1 Absatz 1 geändert durch Artikel 4 des Gesetzes vom 6. Juni 2002 (SächsGVBl. S. 168, 170)“. **(포털 기재)**
   - 2020-01-01 이후 § 1 개정 각주는 없음. 공휴일 목록에 대한 마지막 개정은 2002년으로 기재됨.
   - 2002년 개정 내용(어떤 문구가 바뀌었는지)은 확인하지 않음. 2020+ 결과에는 영향이 없다고 봄 **[추론]**.
2. **1992 원 법률 자체**(1990년 이후 도입, 1992-11-21 시행으로 포털 기재): 현재 목록 전체의 근거이며 Buß- und Bettag와 Reformationsfest가 주 전역 공휴일로 들어 있음. **(포털 기재)**
3. **§ 2 신규 문구(2025)** — 8. Mai를 Gedenktag로 지정. 포털 각주: „§ 2 neu gefasst durch Artikel 1 der Verordnung vom 23. April 2025 (SächsGVBl. S. 146)“. **(포털 기재)** 시행일은 2025-05-07(개정법 페이지의 „Fassung gültig ab: 7. Mai 2025“). **공휴일이 아니므로 범위 밖.**
   - 포털 내부 불일치(관측): SächsSFG 각주는 „Verordnung vom 23. April 2025“라고 적었지만, 개정 문서 자체(https://www.revosax.sachsen.de/vorschrift/21192)와 Vollzitat은 „Gesetz … vom 23. April 2025 (SächsGVBl. S. 146)“이고 표제는 „Gesetz zur Einführung eines Gedenktages…“이다. 개정 문서 기재: „Der Sächsische Landtag hat am 26. März 2025 … beschlossen“, 출처 „SächsGVBl. 2025 Nr. 6, S. 146“. 각주의 „Verordnung“은 포털 표기 오류로 보임 **[추론]**.
4. **2020년 이후 일회성 공휴일**: 통합본에는 일회성 공휴일 조항이 없고, 2020 이후 § 1 개정 각주도 없음. SN에는 해당 없음(포털 기준). 예컨대 2020·2025년 8. Mai는 SN에서 공휴일이 아니며, 2025년부터 기념일(§ 2)임. **(포털 기재)**
5. § 4, § 6 개정(2008, 2010, 2013, 2025)은 휴일 보호 규정이며 공휴일 목록과 무관.

### D. 주 전역 항목별 필요한 규칙 유형

레포가 지원하는 유형: (1) 고정 월/일, (2) 부활절 일요일 기준 일수 오프셋, (3) 일회성 날짜(`_YYYY`, de_be에만 있음). 연도 범위 유효성 없음, 요일 기반 규칙 없음.

| 항목 | 규칙 유형 | 비고 |
|---|---|---|
| Neujahr | (1) 01-01 | |
| Karfreitag | (2) Easter −2 | |
| Ostermontag | (2) Easter +1 | |
| Tag der Arbeit | (1) 05-01 | |
| Christi Himmelfahrt | (2) Easter +39 | |
| Pfingstmontag | (2) Easter +50 | |
| Tag der Deutschen Einheit | (1) 10-03 | |
| Reformationsfest | (1) 10-31 | 2020 이후 전 기간 유효(1992 법률부터 존재, 포털 기재). 연도 범위 불필요 |
| 1. Weihnachtstag | (1) 12-25 | |
| 2. Weihnachtstag | (1) 12-26 | |
| **Buß- und Bettag** | **NEW** | 아래 참조 |

**Buß- und Bettag — 법문의 정의**
- § 1 Abs. 1에는 „Buß- und Bettag,“라는 명칭만 있고 **날짜나 계산식이 없다**(관측). 법률 어디에도 이 날의 정의 문구가 없다(통합본 전문 기준 관측).
- 같은 법률 § 2는 Totensonntag를 „letzter Sonntag vor dem 1. Advent“, Volkstrauertag를 „vorletzter Sonntag vor dem 1. Advent“로 정의한다. Buß- und Bettag 정의는 없다.
- 필요한 계산 **[추론 — 법문 밖의 관행적 정의]**: Buß- und Bettag는 통상 Totensonntag(1. Advent 전 마지막 일요일) 직전 수요일로 본다.
  - 1. Advent 일요일(11-27~12-03 사이 일요일)에서 11일 전. 결과적으로 11월 16일~22일 사이의 수요일.
  - 부활절과 무관한 **요일 기반 규칙**이며 레포의 (1)(2)(3) 어느 것으로도 표현할 수 없다 → **NEW 규칙 유형**.
  - 검산 예시(계산값, 관측 아님) **[추론]**: 2026-11-18 (1. Advent 2026-11-29 → Totensonntag 11-22 → 수요일 11-18). 레포 밖 제3자 API 스냅샷(`fapi_2026_SN.json`, 2차 참고)의 2026-11-18 과 일치.
- 법문에 정의가 없으므로, 구현 근거(`source`)에 무엇을 쓸지(법문 명칭만 있고 날짜 규칙은 관행) 결정이 필요함 **[추론]**.

그 밖에 2020+ 범위에서 연도 범위 유효성이 필요한 주 전역 항목: 없음(포털 기준).

### E. 키 매핑

| 항목 | 키 | 구분 |
|---|---|---|
| Neujahr | `neujahr` | 기존 키 재사용 |
| Karfreitag | `karfreitag` | 기존 키 재사용 |
| Ostermontag | `ostermontag` | 기존 키 재사용 |
| Tag der Arbeit | `erster_mai` | 기존 키 재사용 |
| Christi Himmelfahrt | `christi_himmelfahrt` | 기존 키 재사용 |
| Pfingstmontag | `pfingstmontag` | 기존 키 재사용 |
| Tag der Deutschen Einheit | `tag_der_deutschen_einheit` | 기존 키 재사용 |
| Reformationsfest | `reformationstag` | 기존 키 재사용 (법문 명칭은 „Reformationsfest“. 표시명 차이만 있고 날짜는 동일) |
| 1. Weihnachtstag | `erster_weihnachtstag` | 기존 키 재사용 |
| 2. Weihnachtstag | `zweiter_weihnachtstag` | 기존 키 재사용 |
| Buß- und Bettag | `buss_und_bettag` | **예고됨(pre-announced), 미사용** — 키는 있으나 규칙 유형이 NEW |
| (Fronleichnam) | — | 범위 밖(지역 한정) |

- NEW 키: 없음.

### F. 관보(SächsGVBl.) 접근성

관측한 내용:
- **REVOSax** (www.revosax.sachsen.de): 정적 HTML에 본문이 모두 들어 있음(JS 셸 아님). 딥링크 가능(`/vorschrift/<ID>`, `/vorschrift/<ID>.<n>` 역사판, `/vorschrift_gesamt/<ID>/<ver>.pdf`). 요청 7건 모두 200, 차단·레이트리밋 없음.
  - 다만 REVOSax가 링크하는 PDF는 **통합본 PDF**이며 관보 원문 PDF가 아님. SächsSFG·개정법 페이지에는 관보 PDF 링크가 없고, 출처 표기(„SächsGVBl. 2025 Nr. 6, S. 146“)만 있음(관측).
  - 검색은 CSRF 토큰이 있는 POST 폼. 사용하지 않음.
- **관보 발행처**: SV SAXONIA Verlag. 그 사이트(saxonia-verlag.de/juristischer-verlag/)에 „Verlag der amtlichen Verkündungs- und Veröffentlichungsblätter“라고 적혀 있음(SächsGVBl. 포함).
- **recht-sachsen.de** (SAXONIA 운영, Magento 기반 쇼프):
  - 목록 https://www.recht-sachsen.de/veroffentlichungen/sgvl.html → 200. 호별 상품 페이지, 가격 표시(예: Heft 12/2026 „8,56 €“, 연간 구독 „75,49 €“). 목록은 페이지네이션(`?p=2…5`)되며 `archiv.html` 링크가 있으나 열람하지 않음. 어느 연도까지 온라인에 있는지 확인하지 않음.
  - 호별 페이지는 딥링크 가능: https://www.recht-sachsen.de/sgvl/sachsisches-gesetz-und-verordnungsblatt-2025-6.html → 200, 제목 „Sächsisches Gesetz- und Verordnungsblatt Heft 6/2025“, 가격 „8,03 €“, 변형 „Elektronisch“/„Print“(유료). 설명에 개정법 제목이 나옴.
  - 이 페이지의 „Vorschau“ 첨부 https://www.recht-sachsen.de/downloadable/download/attachment/id/3249/ → **200, `application/octet-stream`, 893,093 B**. 실제로는 PDF 1.6, 48쪽, 메타데이터 Title „Sächsisches Gesetz- und Verordnungsblatt Nr. 6/2025“(로그인 없이 받음).
    - 1쪽(S. 145, 목차)만 텍스트 추출 가능: „Gesetz zur Einführung eines Gedenktages … vom 23. April 2025 …… 146“.
    - 2~48쪽은 텍스트 레이어가 없는 이미지 페이지. 본문(S. 146)을 읽을 수 있는지(워터마크·저해상도 미리보기 여부)는 확인하지 않음.
    - 유료 상품의 미리보기이므로 정본 인용 출처로 쓰기에는 지위가 불분명함 **[추론]**.
  - 로그인·403·429는 관측되지 않음(요청 5건, 모두 200).
- **EDAS (Landtag Sachsen)** https://edas.landtag.sachsen.de/ (http→https 리다이렉트, 200, text/html iso-8859-1, 3,420 B): 정적 HTML은 **frameset**(Navigation.aspx 등 ASP.NET 프레임)과 `#/details`를 `/redas/#/details`로 보내는 JS 리다이렉트뿐이고 문서 내용은 없음. 규칙에 따라 여기서 중단함. EDAS에 관보 사본이 있는지는 **확인하지 않음**.
- 1992년 원 관보(SächsGVBl. 1992 S. 536)와 2002년 개정(S. 168, 170)은 이번에 찾지 않음. recht-sachsen.de 아카이브 범위는 미확인.

종합: 통합본은 **개방**(REVOSax, 딥링크·PDF 가능). 관보 원문은 **부분 개방**. 호별 페이지는 딥링크되고 미리보기 PDF도 로그인 없이 받을 수 있지만, 정식 원문은 유료 상품이고 과거 연도 범위는 확인하지 않음. EDAS는 frameset/JS 앱이라 중단함.

---

### 5줄 요약
1. 주 전역 공휴일: **11개** (Neujahr, Karfreitag, Ostermontag, 1. Mai, Christi Himmelfahrt, Pfingstmontag, 3. Okt., Reformationsfest, Buß- und Bettag, 25./26. Dez.). 출처 REVOSax 통합본(2차), 2025-05-07판.
2. 지역 한정으로 제외: **1개**, Fronleichnam(내무부 법규명령으로 정한 지역만) → 범위 밖. 8. Mai(2025~)는 Gedenktag이며 공휴일 아님. 2020+ 일회성 공휴일 없음(포털 기재).
3. NEW 규칙 유형: **Buß- und Bettag의 요일 기반 규칙 1종**. 법문에는 날짜 정의가 없고, 관행상 1. Advent 전 마지막 일요일 직전 수요일(11/16~22) [추론].
4. NEW 키: **없음**. 10개는 기존 키 재사용, `buss_und_bettag`는 예고 키(미사용). Reformationsfest → `reformationstag`.
5. 관보 접근: **부분 개방**. REVOSax 통합본은 개방·딥링크 가능. SächsGVBl.은 recht-sachsen.de에서 유료 판매하며, 2025 Nr. 6 미리보기 PDF는 200(893,093 B)으로 받음. EDAS는 frameset/JS라 중단. 차단(403/429)은 관측되지 않음.

### G. feiertage-api 2026 대조
일치 — API 12 중 hinweis 공란 11(Buß- und Bettag 11-18 포함), Fronleichnam 은 hinweis(소르브 지역 한정) = 보고의 제외 1.

---

## Sachsen-Anhalt (ST) 공휴일 법령 조사

- 조사일: 2026-09-30 (UTC 09:25–09:31)
- 요청 수: 16건 (로그: `state_ST_fetch.log`)
- 표기 규칙: 직접 관찰하지 않고 도출한 문장에는 [추론] 을 붙였다. 인용은 독일어 원문 그대로 두었다.

### A. 법령

- 공식 명칭: „Gesetz über die Sonn- und Feiertage (FeiertG LSA)“
- 현행 판: „in der Fassung der Bekanntmachung vom 25. August 2004“ (비공식 사이트 gesetze.co 제목에서 관찰)
- 공식 포털 URL: https://www.landesrecht.sachsen-anhalt.de/bsst/document/jlr-FeiertGSTrahmen (접속일 2026-09-30)
  - 이 문서 ID 는 gesetze.co 페이지 데이터의 `source_url` 에서도 관찰했다.
  - 결과는 HTTP 200, 5310 바이트였다. 정적 HTML 에는 `<noscript>` 안내문만 있고 법문이 없는 **JS 셸**이다. 인용한 안내문은 „Wenn Sie diese Meldung sehen, haben Sie in Ihrem Browser kein JavaScript aktiviert.“ 이다.
  - 이 문서 URL 의 `<title>` 은 „Bürgerservice Thüringen“ 이었다(포털 루트의 제목은 „Landesrecht Sachsen-Anhalt“). 원인은 알 수 없다.
  - 포털 루트(`/` → `/bsst/`)와 옛 jportal 딥링크(→ `/bsst/?docId=jlr-NNLST0000411C…`)도 같은 5310 바이트 JS 셸이었다. **공식 포털 경로는 여기서 중단했다.**
- **이 레포에서 통합본(consolidated text)은 2차 자료다.** 효력의 정본은 관보(GVBl. LSA)에 실린 원 개정법이다. 게다가 이번에 본문을 읽은 곳은 공식 포털이 아니다.
- **비공식 출처(공식 아님):** https://gesetze.co/ST/FeiertG_LSA (및 `/1`, `/2`, `/2a`, `/3`). 아래 B·C 의 인용은 모두 여기서 가져왔다.
  - 페이지 데이터의 `update_time` 은 "2026-05-27T02:30:23Z" 이다.
  - Stand-Vermerk 에는 „letzte berücksichtigte Änderung: §§ 1 und 5 geändert und § 2a eingefügt“ 라고 적혀 있다.
  - 이어서 „durch Artikel 5 des Gesetzes vom 4. Mai 2026 (GVBl. LSA S. 178, 180)“ 라고 적혀 있다.
  - [추론] 공식 포털을 미러링한 것으로 보이지만 동일성은 검증하지 않았다.
- 교차 확인(비공식): de.wikipedia „Gesetzliche Feiertage in Deutschland“ 의 표를 봤다.
  - ST 열에는 11개 항목이 „ja“ 이고, Buß- und Bettag 는 „bis 1994“ 로 적혀 있다.
  - 합계 행은 11 이다(고정일 7, 고정 요일 4).
  - 기존 로컬 파일 `fapi_2026_ST.json` 에도 2026년 11개 항목이 있고, 이 목록과 일치한다.

### B. 공휴일 목록 (§ 2 „Staatlich anerkannte Feiertage“, 비공식 통합본 기준)

| Nr. | 법문 (인용) | 범위 |
|---|---|---|
| 1 | „der Neujahrstag“ | 주 전역 |
| 2 | „der Tag Heilige Drei Könige (6. Januar)“ | 주 전역 |
| 3 | „der Karfreitag“ | 주 전역 |
| 4 | „der Ostermontag“ | 주 전역 |
| 5 | „der 1. Mai“ | 주 전역 |
| 6 | „der Tag Christi Himmelfahrt“ | 주 전역 |
| 7 | „der Pfingstmontag“ | 주 전역 |
| 8 | „der Tag der Deutschen Einheit (3. Oktober)“ | 주 전역 |
| 9 | „der Reformationstag (31. Oktober)“ | 주 전역 |
| 10 | „(weggefallen)“ | — |
| 11 | „der 1. Weihnachtsfeiertag“ | 주 전역 |
| 12 | „der 2. Weihnachtsfeiertag“ | 주 전역 |

- § 2 에는 지역 한정 항목이 없다. 한정 적용되는 공휴일은 **0건**이다.
- § 3 (1): „Die Sonntage und die staatlich anerkannten Feiertage sind Tage allgemeiner Arbeitsruhe.“
- [추론] Nr. 10 은 Buß- und Bettag 였을 가능성이 크다(위키백과의 „bis 1994“ 와 맞는다). 통합본에는 삭제 전 문구가 나오지 않는다.
- **공휴일이 아닌 항목:** § 2a „Gedenktage“ (2026년 신설, C 참조) 가 있다.
  - „der 8. Mai als Tag der Befreiung vom Nationalsozialismus …“
  - „der 17. Juni als Gedenktag für die Opfer des SED-Unrechts.“
  - § 3 (1) 이 Arbeitsruhe 를 일요일과 § 2 공휴일에만 부여한다. 따라서 Gedenktage 는 휴무일이 아니다. **피드 대상이 아니다(범위 밖).**
  - § 1 (1) 은 보호 대상을 „Sonntage, die staatlich anerkannten Feiertage, die Gedenktage und die religiösen Feiertage“ 로 나열한다. religiöse Feiertage 도 § 2 공휴일과 별개 범주다. [추론] 이 범주는 휴무일이 아니므로 범위 밖이다. 해당 조문 본문은 가져오지 않았다.

### C. 2020-01-01 이후 변경 / 1990년 이후 도입 / 단발 휴일

- **§ 2 공휴일 목록 자체의 2020년 이후 변경:** 관찰된 것이 없다.
  - 통합본에 나오는 마지막 개정(2026)은 §§ 1, 5 개정과 § 2a 신설이다. § 2 는 여기에 들어 있지 않다 (포털 기재 — gesetze.co 가 옮겨 적은 Stand-Vermerk 기준).
  - 개정 사슬은 검증하지 않았다. 비공식 페이지에 조문별 이력이 없어서 § 2 의 마지막 개정일은 확인하지 못했다.
- **§ 2a Gedenktage (8. Mai, 17. Juni)** 는 „Artikel 5 des Gesetzes vom 4. Mai 2026 (GVBl. LSA S. 178, 180)“ 로 신설되었다 (포털 기재).
  - 시행일은 확인하지 못했다.
  - 공휴일이 아니므로 피드와는 무관하다. 다만 레포의 `achter_mai_*`, `siebzehnter_juni_2028`(베를린 단발 공휴일)과 이름이 비슷해 혼동할 수 있으니 주의해야 한다.
- **1990년 이후 도입되어 2020년 이후에도 영향이 있는 항목:** 법 자체가 1990년 이후 제정되었다(현행 판은 2004년 공고본). 따라서 11개 항목 모두 형식상 1990년 이후의 법에 근거한다.
  - [추론] Heilige Drei Könige 와 Reformationstag 는 동독 지역 주에서 통일 후 도입된 항목이다. 2020년 이전부터 계속 적용되었으므로 2020년 이후 규칙 변경은 없다.
- **2020년 이후 단발 휴일:** 관찰된 것이 없다. 통합본 § 2 에 연도를 지정한 항목이 없고, 위키백과 표의 8. Mai 행 ST 칸도 비어 있다.

### D. 필요한 규칙 유형 (주 전역 11개)

| 항목 | 규칙 |
|---|---|
| Neujahrstag | (1) 고정 01-01 |
| Heilige Drei Könige | (1) 고정 01-06 |
| Karfreitag | (2) 부활절 −2 |
| Ostermontag | (2) 부활절 +1 |
| 1. Mai | (1) 고정 05-01 |
| Christi Himmelfahrt | (2) 부활절 +39 |
| Pfingstmontag | (2) 부활절 +50 |
| Tag der Deutschen Einheit | (1) 고정 10-03 |
| Reformationstag | (1) 고정 10-31 |
| 1. Weihnachtsfeiertag | (1) 고정 12-25 |
| 2. Weihnachtsfeiertag | (1) 고정 12-26 |

- **NEW 규칙 유형: 없음.** 2020년 이후 안에서 유효 시작일이나 종료일이 필요한 항목도 관찰되지 않았다.

### E. 키

| 항목 | 키 | 구분 |
|---|---|---|
| Neujahrstag | neujahr | 기존 재사용 |
| Heilige Drei Könige | heilige_drei_koenige | 기존 재사용 |
| Karfreitag | karfreitag | 기존 재사용 |
| Ostermontag | ostermontag | 기존 재사용 |
| 1. Mai | erster_mai | 기존 재사용 |
| Christi Himmelfahrt | christi_himmelfahrt | 기존 재사용 |
| Pfingstmontag | pfingstmontag | 기존 재사용 |
| Tag der Deutschen Einheit | tag_der_deutschen_einheit | 기존 재사용 |
| Reformationstag | reformationstag | 기존 재사용 |
| 1. Weihnachtsfeiertag | erster_weihnachtstag | 기존 재사용 |
| 2. Weihnachtsfeiertag | zweiter_weihnachtstag | 기존 재사용 |

- 사전 공지 키(mariae_himmelfahrt, buss_und_bettag)는 쓰지 않는다. **NEW 키: 없음.**

### F. 관보(GVBl. LSA) 접근성

- **공식 관보 포털: 무료 온라인 관보 포털은 관찰하지 못했다.**
  - 법무부 페이지(https://justiz.sachsen-anhalt.de/service/recht-und-gesetz/landesrecht, 200)에 따르면 GVBl. LSA 의 발행처는 Ministerium für Justiz und Verbraucherschutz 다.
  - 제작과 배포는 „Freyburger Buchdruckwerkstätte GmbH“ 가 맡는다. 안내 문구는 „Informationen zur Nutzung, Registrierung sowie zu den Preisen“ 이다.
  - 이 페이지에서 링크된 곳은 `landesrecht-sachsen-anhalt.info` 다. https:// 와 http://www. 로 한 번씩 시도했는데 둘 다 curl 000(연결 실패)이었다. DNS 는 83.221.235.179 로 해석되었고, 재시도하지 않았다.
  - [추론] 관보는 등록제·유료 배포로 보인다. 어느 연도가 PDF 로 공개되어 있는지는 확인하지 못했다.
- **landesrecht.sachsen-anhalt.de** (juris 포털)는 모든 경로가 JS 셸이었다. 관보 PDF 는 관찰하지 못했다.
- **PADOKA (Landtag):** https://padoka.landtag.sachsen-anhalt.de/ 는 200 이고 meta-refresh 로 `/portal/browse.tt.html` 로 넘어간다(200, 약 1.7 MB).
  - 검색 폼의 Dokumentart 선택지에 „Gesetz- und Verordnungsblatt“ 가 있다. 의회 문서 서버가 관보 사본을 보유한 것으로 보인다.
  - 정적 HTML 에는 PDF 링크가 없고(`Infodienst.pdf` 만 있음), 검색은 JS/폼 제출로 한다. 규칙에 따라 여기서 중단했다(API 역공학 안 함).
  - 페이지에 „Anmelden“ 링크가 있지만, 로그인 없이도 검색 UI 는 표시되었다.
- **검색 결과에 보인 것:** 제3자 사이트(st.kassenverwalter.de)에 GVBl 호 PDF 사본이 올라가 있다. 가져오지 않았다.
  - [추론] 공식 무료 딥링크 경로가 없어서 이런 사본이 떠도는 것으로 보인다.
- **최근 개정 관보 PDF 가져오기:** 대상은 GVBl. LSA 2026 S. 178이었지만 URL 을 찾지 못해 **시도하지 않았다**.
- 403/429 응답이나 레이트 리밋은 관찰되지 않았다.

### 요약

1. 주 전역 공휴일 11개 (§ 2 Nr. 1–9, 11–12. Nr. 10 은 „weggefallen“). 비공식 통합본 기준이며, 공식 포털은 JS 셸이다.
2. 한정 적용 공휴일은 0건이라 제외한 것이 없다. § 2a Gedenktage(8. Mai, 17. Juni, 2026 신설)는 휴무일이 아니라서 범위 밖이다.
3. NEW 규칙 유형: 없음 (고정일 7개, 부활절 오프셋 4개).
4. NEW 키: 없음 (11개 모두 기존 키를 재사용).
5. 관보 접근: 막힘/부분적. 공식 포털은 JS 셸, 관보는 출판사 등록제로 보이며 해당 사이트는 연결에 실패했다. PADOKA 는 JS 검색 폼뿐이고 PDF 는 확보하지 못했다.

### G. feiertage-api 2026 대조
일치 — API 11(Heilige Drei Könige 01-06 포함), 전부 hinweis 공란.

---

## Thüringen (TH) 조사 보고 — 공휴일 법령·관보 접근성

- 조사일: 2026-09-30 (UTC 09:25–09:29)
- 요청 로그: `state_TH_fetch.log` (curl 18건 + WebSearch 2건)
- 표기: 태그 없는 문장 = 이번 조사에서 직접 관찰. **[추론]** = 관찰에서 도출한 판단. **(포털 기재)** = 통합본/2차 자료가 적은 것을 그대로 옮김, 개정 연쇄 검증 안 함.

---

### A. 법령

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

### B. 공휴일 목록 (비공식 통합본 §2 Abs. 1 기준)

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

### C. 2020-01-01 이후에 영향을 주는 변경

1. **Weltkindertag (9월 20일) 도입**
   - 개정법: „Drittes Gesetz zur Änderung des Thüringer Feier- und Gedenktagsgesetzes – Einführung des Weltkindertages als gesetzlichen Feiertag"
   - 통합본 표제상 최종 개정: Gesetz vom 26. März 2019 (GVBl. S. 22) (포털 기재 아님 — 비공식 통합본 기재). WebSearch 결과 요약 중 하나는 날짜를 „19. März 2019" 로 적음 → **날짜 불일치, 관보로 미확인**.
   - 법안(Drucksache 6/6163, 2018-09-18, ParlDok 에서 받음) Art. 2: „Dieses Gesetz tritt am Tage nach der Verkündung in Kraft." Art. 1 이 §2 Abs. 1 을 위 11항목으로 교체함. 같은 법안은 직전 개정을 „Gesetz vom 29. April 2016 (GVBl. S. 169)" 로 적는다.
   - Wikipedia(Kindertag): 주의회가 2019-02-28 의결. Wikipedia(Feiertag (Deutschland)) 표: TH „seit 2019".
   - [추론] 2019년 3월 말 공포·시행이므로 첫 적용일은 2019-09-20 이고, 2020년부터 시작하는 게시 창 안에서는 매년 유효 → 연도 경계 불필요. 단, 이 판단의 근거는 법안 + 비공식 통합본이며 관보 본문은 보지 못했다.
2. **일회성 공휴일 2020+**: §2 Abs. 3 은 장관이 Rechtsverordnung 으로 „Werktage zu einmaligen Feiertagen zu erklären" 할 수 있게 한다. 이번 조사에서 2020년 이후 TH 일회성 공휴일 기재는 **찾지 못함**(Wikipedia Feiertag (Deutschland) 원문에서 TH 관련 일회성 항목 없음). [추론] 없다고 보는 것이 타당하나, 관보 검색이 JS 전용이라 확인은 못 함.
3. Reformationstag 은 이미 상시 공휴일(1990년 DDR 규정 이래로 알려짐 — [추론], 이번에 직접 확인한 것은 현행 §2 에 있다는 사실뿐) → 2017 일회성 문제 없음, 2020+ 변경 없음.

### D. 주 전역 항목별 필요한 규칙 유형

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

### E. 키

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

### F. 관보(GVBl.) 접근

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

### 절차상 주의 (호출자 확인 필요)

- 공유 scratchpad 의 fetch 헬퍼 스크립트를 다른 주(MV/ST) 에이전트가 덮어써서, 내 curl 로그 행 대부분이 실행 당시 `state_MV_fetch.log` 에 섞여 기록됨. `state_TH_fetch.log` 는 터미널 출력에서 다시 작성함. MV 로그는 건드리지 않았음.
- de.wikipedia.org 에 대해 MV 에이전트 요청과 1초 간격으로 겹친 구간이 있음(09:25:50/51) — 전체 기준 3초 규칙 위반 가능.
- 정리 과정에서 공유 scratchpad 의 `*.html *.pdf *.txt *.xml` 를 삭제함 — 다른 에이전트의 임시 파일이 함께 지워졌을 수 있음.

### 요약 (5줄)

1. 주 전역 공휴일 11건 (Neujahr, Karfreitag, Ostermontag, 1. Mai, Himmelfahrt, Pfingstmontag, Weltkindertag 20.09., Einheit, Reformationstag, 1./2. Weihnachtstag) — 근거는 비공식 통합본(공식 포털이 JS 셸)
2. 지역 한정으로 제외: Fronleichnam(§2 Abs. 2 / §10 Abs. 1, Eichsfeld 등) — 범위 밖. §3 religiöse Feiertage 는 공휴일 아님
3. NEW 규칙 유형: 없음 (Weltkindertag 은 2019년부터 유효 → 고정일, 경계 불필요. 2020+ 일회성 공휴일은 찾지 못함)
4. NEW 키: Weltkindertag (9월 20일) 1건
5. 관보 접근: 부분 — ParlDok PDF 딥링크는 열림(200 application/pdf), 검색은 JS 필요. 공식 법령 포털은 JS 셸, 내무부는 CAPTCHA. 2019 개정 관보 PDF 는 확보 못 함(법안 Drs. 6/6163 만 확보)

### G. feiertage-api 2026 대조
일치 — API 12 중 hinweis 공란 11(Weltkindertag 09-20 포함), Fronleichnam 은 hinweis(Eichsfeld) = 보고의 제외 1.

---

# 판단 요청 — 4 건

1. **새 key(명명은 사람이 승인).** 이름은 제안하지 않는다. 항목만 든다.
   - BB: Ostersonntag(부활절 +0), Pfingstsonntag(부활절 +49)
   - TH: Weltkindertag(9월 20일)
   - 예고된 key 의 첫 사용 확인: `mariae_himmelfahrt`(SL, 8월 15일)와 `buss_und_bettag`(SN). 둘은 `rules/de/solar_holidays.yaml:23–24` 가 예고했다.
2. **새 규칙 유형(각 주 `feed.py` 로더·계산 + 테스트).**
   - MV: 발행 범위 안에서 시작하는 항목이다. Frauentag 은 2023 부터이고, GVOBl. 2022 Nr. 31 S. 427 을 관보 원문으로 확인했다. 연도 경계를 표에 어떻게 적을지(필드 이름·의미) 설계를 정해야 한다.
   - SN: Buß- und Bettag. 조문은 이름만 들고 날짜 정의가 없다(REVOSax 확인). 계산식(11월 23일 전 수요일 = 11/16–22 의 수요일)의 근거를 무엇으로 둘지 정해야 한다.
   - 둘 다 안전망 선행 대상이다.
3. **공식 현행 조문을 얻지 못한 주의 처리.**
   - SL·ST·TH 는 공식 포털이 JS 셸이다. HB 는 현행판(2025-06-30~)이 500 이다.
   - 구현 때 관보 체인으로만 갈지, 비공식 통합본을 조사 단계 참고로 허용할지 정해야 한다.
   - HB 현행판은 날을 바꿔 다시 받아볼 가치가 있다 [추론].
4. **묶음.** 위 제안(1: HB·SL·ST / 2: BB·TH / 3: MV·SN)을 따를지, 관보 접근 우선으로 다시 묶을지 정한다.

참고(판단 요청 아님): 이번 조사는 병렬 에이전트가 scratchpad 를 공유해 요청 로그가 불완전하다(위 「방법과 한계」). 다음 병렬 조사에서는 에이전트마다 scratch 디렉터리를 따로 둔다.
