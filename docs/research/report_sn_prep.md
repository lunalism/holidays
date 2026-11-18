# SN(작센) 피드 — 출처, Buß- und Bettag 규칙, 일회성 지정 (조사만)

- 측정 시점: 2026-11-18(UTC, 요청 06:51:53Z–07:40:28Z).
- 범위: 조사만 했다.
  - 레포 변경·브랜치·커밋·PR 없음. Codex 호출 없음. 병렬화하지 않았다(scratch 하나).
  - 받은 파일과 렌더는 scratch 에 남겨 두었다 — SN 갈래는 닫히지 않았다.
- 재현 기록: `~/holidays-reports/report_sn_prep/`(README 참조).
- 표기: 명령 출력·원문·렌더에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- 요청: 순차, 매 요청 뒤 3 초 이상. `fetch.log` 325 줄 — 200 이 323, 000(연결 실패) 이 2(recht.nrw.de, 아래 C2).
- **결과 요약**
  - **A** 현행 통합본은 그대로 「Fassung gültig ab: 7. Mai 2025」. PDF 는 두 번 받아 바이트까지 같다. § 1 Abs. 1 은 2002-07-03 판부터 바뀌지 않았다 — 2020 이후 유효한 두 판(2013–2025, 2025–)이 같다.
  - **B** 1992 원법·2002 개정의 관보는 온라인으로 받지 못했다(1992 는 발행사 판매 범위 밖, 2002 는 유료 보관 상품 안). 2025 Nr. 6 S. 146 은 무료 미리보기로 읽었지만 § 1 이 아니라 § 2·§ 6 을 바꾼다. verified 후보 0.
  - **C** SächsSFG 에는 Buß- und Bettag 의 날짜 정의가 없다. **공식 서술을 찾았다** — 작센 주의회 청원 보고서 2023: 「…den Buß- und Bettag als gesetzlichen Feiertag am letzten Mittwoch vor dem Totensonntag beizubehalten.」 다른 주의 옛 조문(Hessen 1971)은 「Mittwoch vor dem letzten Sonntag nach Trinitatis」 와 「Der letzte Sonntag nach Trinitatis ist Totensonntag」 를 함께 적는다. 세 계산꼴은 1990–2100 의 111 해 모두 같다(11월 16–22일). python-holidays 2020–2031 도 같다.
  - **D** 권고는 (ii) 대림절 첫째 주일 기준 오프셋(`advent_offset: -11`), de_sn 로더에만.
  - **E** 2021 Nr. 15 – 2026 의 목차 제목에서 적중 2, REVOSax 「Feiertag」 2020 이후 27 — 전부 「언급뿐」. **2020 전체(Nr. 1–40, 38a, 39a)와 2021 Nr. 1–14 는 목차를 얻지 못했다(공백).**

---

## 기준 SHA와 환경

- `origin/main` = `38c8db2e409c50d270985f144e9c13152213d94f`(Merge pull request #124). 기대값 38c8db2 와 같다. 로컬 `main` 도 같은 커밋이다.

| # | 전제 | 관측 | 판정 |
|---|---|---|---|
| E1 | 기준 SHA 에서 `uv run pytest -q` | **1979 passed, 4 xfailed, 29 xpassed** | 성립 |
| E2 | 보고 디렉터리가 있고 쓸 수 있다 | `~/holidays-reports`(→ `<local>/holidays-reports`), 쓰기 확인 | 성립 |

- 도구: `uv run`(playwright 1.62.0, chromium 151.0.7922.34, holidays 0.102). PDF: `uv run --no-project --with 'pypdf==5.4.0'`(관보 미리보기는 빈 비밀번호 AES 라 `cryptography==44.0.2` 를 더함), 렌더 `pypdfium2==5.14.0`·`pillow==11.3.0`.

---

## Part A — 현행 공식 조문(REVOSax)

### A1

- 화면 `https://www.revosax.sachsen.de/vorschrift/3997-SaechsSFG` — 06:51:53Z, 200, 32,167 B, sha256 `d9738d17…`.
  - 「Rechtsbereinigt mit Stand vom 7. Mai 2025」, 「Fassung gültig ab: 7. Mai 2025」, 「Fundstelle … SächsGVBl. 1992 Nr. 35, S. 536 / Fsn-Nr.: 114-2」.
  - Vollzitat: 「Gesetz über Sonn- und Feiertage im Freistaat Sachsen vom 10. November 1992 (SächsGVBl. S. 536), das zuletzt durch das Gesetz vom 23. April 2025 (SächsGVBl. S. 146) geändert worden ist」.
  - **판은 그대로 「gültig ab 7. Mai 2025」 다.** 새 판 없음.
- PDF `https://www.revosax.sachsen.de/vorschrift_gesamt/3997/48138.pdf`(화면의 「Vorschrift als PDF」 링크) — 06:52:05Z 와 06:52:20Z(10 초 뒤) 두 번:
  - 둘 다 200, `application/pdf`, **53,502 B**(2026-09-30 조사와 같은 바이트 수), sha256 **같음** `93d9dc8b5cdeea97fde557b9c72654ac04b4492a691fb6d2b8af218ba62157c4`.
  - 텍스트층 추출(`extract_revosax.py`, 4 쪽)도 같다: 전문 `4f9b905c…`, § 1 `5e6fdcb4…`, § 2 `fed4093e…`.
  - **바이트 안정이다.** HB 145882 처럼 요청마다 새로 만들어지지 않는다(관측 두 번).
- PDF 의 꼬리 줄: 「SächsSFG / http://web:3000 / Fassung vom 07.05.2025 / Seite 1 von 4」.

**§ 1 Abs. 1(원문 그대로)** — REVOSax 의 § 1 Abs. 1 에는 **번호가 없다**. HTML 은 항목을 `<br>` 로만 나누고(번호 목록이 아니다), PDF 텍스트층에도 항목 앞 번호가 없다. 아래 번호는 열거 순서다(지시의 「Nr. 1–12」 에 해당하는 것).

> (1) Gesetzliche Feiertage sind:
> [1] Neujahr (1. Januar),
> [2] Karfreitag,
> [3] Ostermontag,
> [4] Tag der Arbeit (1. Mai),
> [5] Christi Himmelfahrt,
> [6] Pfingstmontag,
> [7] Fronleichnam (nur in den vom Staatsministerium des Innern durch Rechtsverordnung bestimmten Regionen),
> [8] Tag der Deutschen Einheit (3. Oktober),
> [9] Reformationsfest (31. Oktober),
> [10] Buß- und Bettag,
> [11] 1. Weihnachtstag (25. Dezember),
> [12] 2. Weihnachtstag (26. Dezember).
> (2) Die gesetzlichen Feiertage sind Feiertage im Sinne bundes- und landesrechtlicher Vorschriften.

**§ 2(원문 그대로, 여기는 번호가 있다)**

> Gedenk- und Trauertage im Sinne dieses Gesetzes sind:
> 1. der Volkstrauertag (vorletzter Sonntag vor dem 1. Advent),
> 2. der Totensonntag (letzter Sonntag vor dem 1. Advent),
> 3. der 8. Mai als Tag der Befreiung vom Nationalsozialismus und der Beendigung des Zweiten Weltkriegs in Europa.

- 참고: 같은 법 § 3 Abs. 1 은 다른 수요일을 날짜로 정의한다 — 「Frühjahrsbußtag (7. Mittwoch vor Ostern)」. Buß- und Bettag 에는 그런 괄호가 없다.

### A2 — 역사판

화면의 링크 `/vorschrift/3997.1`–`.6` 를 받았다(06:53:30Z–06:53:52Z, 모두 200). `versions.py` → `versions.tsv`.

| 판 | 유효 기간(화면 그대로) | § 1 Abs. 1 의 sha256(앞 16) |
|---|---|---|
| 3997.1 | 21. November 1992 – 2. Juli 2002 | `165b6ea6bf5615d5` |
| 3997.2 | 3. Juli 2002 – 26. April 2008 | `5032d51f21c54872` |
| 3997.3 | 27. April 2008 – 20. Dezember 2010 | 같음 |
| 3997.4 | 21. Dezember 2010 – 9. Februar 2013 | 같음 |
| 3997.5 | 10. Februar 2013 – 6. Mai 2025 | 같음 |
| 3997.6 | ab 7. Mai 2025 | 같음 |

- **2020-01-01 이후 유효한 판(3997.5·3997.6)의 § 1 Abs. 1 은 같다. 그 기간에 § 1 Abs. 1 의 변경은 없다.**
- 유일한 변경(3997.1 → 3997.2)은 「Reformationstag (31. Oktober)」 → 「Reformationsfest (31. Oktober)」 다. Buß- und Bettag 는 1992 판부터 날짜 없이 있다.
- § 1 의 각주(현행 화면, 링크 title): 「§ 1 Absatz 1 geändert durch Artikel 4 des Gesetzes vom 6. Juni 2002 (SächsGVBl. S. 168, 170)」.
- 그 밖의 각주: § 2 「neu gefasst durch Artikel 1 der Verordnung vom 23. April 2025 (SächsGVBl. S. 146)」 — 2026-09-30 조사가 적은 「Verordnung」 표기 불일치는 그대로다(개정법 자체는 「Gesetz」, B 참조). § 2a 2008, § 3 Abs. 1 2002, § 4 2010·2013, § 6 2008·2025, § 8 Abs. 2 2002.
- Normenhistorie(`/law_versions/48138/impacts`)는 Stammfassung 과 개정 넷(2002·2008·2010·2013)과 2025 를 같은 판 목록과 함께 든다.
- 1992 판의 § 2 는 지금과 꼴이 달랐다(「…sind der Volkstrauertag (vorletzter Sonntag vor dem 1. Advent) und der Totensonntag (letzter Sonntag vor dem 1. Advent).」). 두 정의는 1992 부터 같은 문언이다.

---

## Part B — 공포본(verified 용)

### B1 — 온라인으로 닿는가

REVOSax 화면은 관보 PDF 로 가는 링크가 없다(각주는 REVOSax 의 개정법 화면으로만 간다). 관보는 발행사 SV SAXONIA Verlag 의 판매 사이트 recht-sachsen.de 에 있다.

| 호 | 결과 |
|---|---|
| **1992 Nr. 35 S. 536**(원법) | **닿지 않음.** 판매 사이트 검색 「Heft 35/1992」 → 「keine Ergebnisse」(06:57:53Z). 「Archiv」 화면의 보관 상품은 「Archivabo zum Sächsisches Gesetz- und Verordnungsblatt Jahrgänge 1999 - 2018」(Ab 45,00 €) 하나다 — 1992 는 그 범위 밖이다 |
| **2002 Nr. 9 S. 168, 170**(§ 1 Abs. 1 개정) | **받지 않음.** 판매 사이트 검색 「Heft 9/2002」 는 무관한 상품(SächsABl. 2025 Heft 44)으로 넘어갔다. 2002 는 위 유료 보관 상품(1999–2018) 안에만 있다. 사지 않았다 |
| **2025 Nr. 6 S. 146**(§ 2 Gedenktag) | **받음** — 상품 화면의 「Vorschau」 첨부(attachment/id/3249), 무료·로그인 없음 |

- 2002 개정의 문언은 REVOSax 의 개정법 화면(`Text.link?stid=4565&jabs=a4` → `/vorschrift/4371-…#a4`)으로 읽었다. 관보 원문이 아니다.
  - Art. 4 Nr. 1 「In § 1 Abs. 1 wird das Wort „Reformationstag" durch das Wort „Reformationsfest" ersetzt.」
  - Art. 22 「… Im Übrigen tritt dieses Gesetz am Tage nach seiner Verkündung in Kraft …」
  - 화면의 출처 표기 「SächsGVBl. 2002 Nr. 9, S. 168」.
- REVOSax FAQ(`/faq`)에는 통합본의 법적 지위(구속력·정본 여부)에 대한 문장이 없다.

### B2 — 받은 것

**SächsGVBl. 2025 Nr. 6**(`text/gvbl_2025_06_S146.txt`)
- 06:56:43Z, 200, `application/octet-stream`(실제 PDF 1.6), **893,093 B**(2026-09-30 과 같은 바이트 수), sha256 `f01131af434d35fb2101648d6e64f31aedb9298761dc1ae855cfcfddd915c6e9`. 48 쪽. 메타데이터 Title 「Sächsisches Gesetz- und Verordnungsblatt Nr. 6/2025」.
- 1 쪽(S. 145)은 텍스트층이 있다 — 호 줄 「Nr. 6/2025 6. Mai 2025」.
- **2 쪽(S. 146)은 텍스트층이 없다. 150 dpi 로 렌더해 읽었다.** 워터마크·흐림 없이 읽힌다.
  - 쪽 머리 「Sächsisches Gesetz- und Verordnungsblatt Nr. 6 6. Mai 2025」.
  - Art. 1 Nr. 1 은 § 2 를 새로 쓴다(위 A1 의 § 2 와 같은 자구), Nr. 2 는 § 6 의 인용을 바꾼다. **§ 1 은 건드리지 않는다.**
  - Art. 2 「Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.」 — [추론] 호 날짜 6. Mai 2025 를 Verkündung 으로 보면 2025-05-07 이고, REVOSax 의 「Fassung gültig ab: 7. Mai 2025」 와 같다.

### B3 — verified 로 둘 수 있는 항목

- **true 후보: 없다.** 11 건 모두 § 1 Abs. 1 의 자구에 기대는데, 그 자구는 1992 원법(받지 못함)과 2002 개정(Reformationsfest, 받지 못함)에서 온다.
- 2025 Nr. 6 은 공포본을 읽었지만 § 2(Gedenk- und Trauertage)와 § 6 만 바꾼다 — 공휴일 항목의 근거가 아니다. 다만 Buß- und Bettag 의 날짜 관행이 기대는 Totensonntag 의 정의(「letzter Sonntag vor dem 1. Advent」)는 이 공포본에서 읽은 자구다(C).
- 남는 경로: 2002 Nr. 9 는 발행사 유료 보관 상품(1999–2018), 1992 Nr. 35 는 온라인 판매·보관 밖 — 실물 관보나 도서관(이번에 찾지 않음).

---

## Part C — Buß- und Bettag 의 날짜 관행

### C1 — SächsSFG 에는 정의가 없다

- A1 텍스트에서 「Buß- und Bettag」 는 § 1 Abs. 1 의 열 번째 항목 「Buß- und Bettag,」 한 번뿐이다. 괄호도 정의 문장도 없다(HTML 과 PDF 텍스트층 둘 다). 역사판 여섯도 같다.
- § 2 의 정의(현행 통합본, 2025 공포본 S. 146 과 같은 자구): 「der Volkstrauertag (vorletzter Sonntag vor dem 1. Advent)」, 「der Totensonntag (letzter Sonntag vor dem 1. Advent)」.

### C2 — 공식 서술

찾은 순서대로.

1. **작센 주 정부·주의회 화면**
   - sachsen.de 검색(화면 첫 쪽의 GET 폼, 결과는 JS 로 렌더):
     - 「Buß- und Bettag」 → 57 건(첫 쪽 10 건을 읽음). 날짜 정의 없음. 가까운 것: Gewerbeaufsicht 연보 2017 「am Buß- und Bettag (Mittwoch)」(요일만).
     - 「Bettag Mittwoch vor dem」 → 17 건. **찾음:**
   - **Sächsischer Landtag, 청원위원회 보고서 2023**(`SLT_BR_Petitionsbericht_2023_Web_PDFUA.pdf`, PDF 메타데이터 CreationDate 2024-07-24) — `https://www.landtag.sachsen.de/download/publikationen/SLT_BR_Petitionsbericht_2023_Web_PDFUA.pdf`, 2026-11-18 받음, 5,320,069 B, sha256 `96092ac6…`, PDF 68 쪽 텍스트층:
     > 「Der Landesgesetzgeber entschied sich dafür, den Buß- und Bettag als gesetzlichen Feiertag am letzten Mittwoch vor dem Totensonntag beizubehalten.」
     - 문맥: SGB XI § 58 의 보험료 분담과 1993-12-31 기준 공휴일 수를 설명하는 절이다(`text/slt_petitionsbericht_2023_p68.txt`).
     - [추론] 법률 조문이 아니라 주의회 위원회가 입법 경과를 적은 공식 간행물의 문장이다.
   - REVOSax 빠른 검색 「Buß- und Bettag」 → 10 건(SächsSFG, SächsLadÖffG, Spielbankengesetz, VwV 여럿). 결과 목록의 제목만 봤다 — 본문은 열지 않았다. SächsSFG 본문에는 정의가 없다(C1).
   - landtag.sachsen.de 의 EDAS(의회 문서 시스템)는 이번에도 열지 않았다(2026-09-30 조사: frameset/JS).
2. **1992 공포본·옛 공식판**
   - 1992 Nr. 35 는 받지 못했다(B1). REVOSax 1992 판(3997.1)에는 정의가 없다(A2).
   - SächsSFG § 10 이 폐지한 동독 법령 — 「Verordnung über die Einführung gesetzlicher Feiertage vom 16. Mai 1990 (GBl. I Nr. 27 S. 248)」 와 그 「Erste Durchführungsbestimmung vom 7. Juni 1990 (GBl. I Nr. 31 S. 281)」 — 은 날짜를 정의했을 수 있지만 [추론], 공식 온라인 색인을 찾지 않았다(단서로만 적는다).
3. **다른 주·연방 법률(현행·옛)**
   - **Hessen, GVBl. 1971 I Nr. 36 S. 344** — Hessisches Feiertagsgesetz in der Fassung vom 29. Dezember 1971, § 1. `https://starweb.hessen.de/cache/GVBL/1971/00036.pdf`(헤센 주의회 서버의 관보 목록), 2026-11-18 받음, 269,786 B, sha256 `fc2067c2…`(레포 기록 2026-09-29 와 같음). 텍스트층 없음 — 300 dpi 렌더 판독(`text/he_gvbl_1971_I_36_S344.txt`):
     > 「9. der Buß- und Bettag (Mittwoch vor dem letzten Sonntag nach Trinitatis),」
     > 「(3) Der letzte Sonntag nach Trinitatis ist Totensonntag.」
     - 같은 조문 안에서 Buß- und Bettag = Totensonntag 앞 수요일이 된다.
   - **Nordrhein-Westfalen, GV. NW. 1989 Nr. 19 S. 222**(§ 2 Abs. 1 Nr. 10)와 **1977 Nr. 12 S. 98** — 레포의 전사(`docs/research/report_nw_feiertagsgesetz_chain/1989_S222_par2.txt`·`1977_S98_par2abs1.txt`, 2026-09-29 받은 공포본의 렌더 판독): 「10. der Buß- und Bettag (Mittwoch vor dem letzten Sonntag nach Trinitatis),」. 이번에 다시 받으려 했으나 `recht.nrw.de` 가 두 번 모두 연결 실패(000, 07:00:22Z·07:01:57Z)라 **오늘 다시 보지 못했다**. 레포 기록의 sha256 `b72dd60b…` 만 있다.
   - **Saarland, Amtsblatt 1976 Nr. 13 S. 214** — `https://www.amtsblatt.uni-saarland.de/hefte/1976/1976-013.pdf`, 2026-11-18 받음, 180,842 B. 렌더 판독(`text/sl_amtsbl_1976_13_S214.txt`): § 2 Abs. 1 Nr. 11 「der Buß- und Bettag,」 — **정의가 없다.**
     - **정정(2026-09-30 조사 `state_SL.md`)**: 그 보고의 「1976 원문의 Buß- und Bettag(11월 23일 이전 마지막 수요일 …)」 은 1976 조문에 없는 서술이다. 조문은 이름만 든다.
   - 연방법: SGB XI § 58 은 날짜를 정의하지 않는다는 것을 청원 보고서 문맥이 보이지만 [추론], 조문 자체를 이번에 받지 않았다.
- **쓰지 않은 단서**: 위키백과·교회·달력 사이트는 이번에 요청하지 않았다(2026-09-30 조사가 REVOSax 주소를 찾으려고 위키백과를 한 번 받은 기록이 `state_SN_fetch.log` 에 있다 — 근거로 쓰지 않음).

### C3 — 계산 비교(`c3_compare.py` → `c3_compare.tsv`)

- (a) 11월 23일보다 엄격히 앞선 마지막 수요일.
- (b) 대림절 첫째 주일(11월 27일–12월 3일의 일요일)에서 11일 전 — § 2 의 Totensonntag 앞 수요일.
- (c) Hessen 1971·NW 의 꼴 「Mittwoch vor dem letzten Sonntag nach Trinitatis」 — Trinitatis = 부활절 + 56 일에서 7 일씩 세어 대림절 첫째 주일 앞에서 멈춘 마지막 일요일 앞의 수요일. [추론] 「Sonntage nach Trinitatis」 가 대림절에서 끝난다는 것은 교회력 관행이고 조문은 적지 않는다.

| 결과 | 값 |
|---|---|
| 1990–2100(111 해) (a) = (b) = (c) | **모든 해 같다. 다른 해 없음** |
| 날짜 범위 | **11월 16일 – 22일** |
| 「n. Sonntag nach Trinitatis」 의 n | 22 – 27 |
| python-holidays 0.102 DE(subdiv='SN') 2020–2031 | 12 해 모두 같다(2020-11-18, 2021-11-17, 2022-11-16, 2023-11-22, …, 2031-11-19) |
| feiertage-api 스냅숏(레포 `docs/research/report_batch2_survey/fapi_2026_summary.txt`) | 2026 만 있다 — 「2026-11-18 Buß- und Bettag」, 같다 |

- python-holidays 의 계산(`holidays/countries/germany.py`): `self._add_holiday_1st_wed_before_nov_22(tr("Buß- und Bettag"))`(SN 은 1995 부터). 이 이름은 `holiday_base.py` 가 `_get_nth_weekday_from(-1, WED, date(year, 11, 22))` 로 푼다. 그 함수는 기준일이 수요일이면 그날을 낸다 — 즉 「11월 22일 이하의 마지막 수요일」 = (a). 2023-11-22(수요일)이 예다.
- 연도별 SN 전체 목록(11 건/해): `pyholidays_sn.out`. Fronleichnam 은 기본 범주가 아니라 들지 않는다.
- [추론] (a)–(c) 가 같은 까닭: 대림절 첫째 주일이 11월 27일–12월 3일이면 그 11일 전은 11월 16–22일의 이레 안에 있고, 이레 안의 수요일은 하나뿐이다.

---

## Part D — 규칙 표현 설계(코드 없음)

### D1 — 독일 로더가 지금 표현하는 것(인용)

- 고정 날짜·부활절 오프셋 — `rules/de_hb/feed.py:153–159`:
  ```python
  out = [_event(date(year, e["month"], e["day"]), e) for e in _solar()]
  sunday = easter(year)
  out += [_event(sunday + timedelta(days=e["easter_offset"]), e) for e in _easter_based()]
  ```
- 일회성 `_YYYY` — `rules/de_be/feed.py:137–143·169`: `_load(DESIGNATED_PATH, "date")`, `date` 가 날짜가 아니면 거부, key 가 `_{e['date'].year}` 로 끝나야 한다. `out += [_event(e["date"], e) for e in _designated() if e["date"].year == year]`.
- 시작 경계·닫힌 필드 — `rules/de_mv/feed.py`:
  - `_COMMON_FIELDS = frozenset({"key", "name", "scope", "verified", "source", "source_todo", "effective_from"})`(115–117), `_checked` 가 공통 필드 + 표의 날짜 필드 밖을 「모르는 필드」 로 거부, `effective_from` 은 `type(start) is not date` 면 거부.
  - `_active`(203–206): `return not (start and day < start)`.
  - `_year`(222–229): 고정·부활절 날짜를 모은 뒤 `_active` 로 거른다.
  - 최상위 키는 `holidays` 하나, 중복 키 거부(`_UniqueKeyLoader`).
- 요일 기반 규칙은 어느 로더에도 없다.

### D2 — 선택지(SN 만)

| | (i) 요일 + 배타 경계 | (ii) 대림절 첫째 주일 오프셋 | (iii) Totensonntag 오프셋 |
|---|---|---|---|
| 계산 | 11월 23일 앞의 마지막 수요일 | 대림절 첫째 주일 − 11 일 | (대림절 첫째 주일 − 7) − 4 일 |
| 로더(de_sn 만) | 새 표 `weekday_holidays.yaml`, 필드 `weekday`(닫힌 이름 집합)·`before_month`·`before_day`. 계산 함수 하나 | 새 표 `advent_holidays.yaml`, 필드 `advent_offset`(int, bool 거부). `_advent1(year)` = 11월 27일부터 첫 일요일. `_year` 에 한 줄 | 새 표, 필드 `totensonntag_offset`. Totensonntag = `_advent1 − 7` |
| YAML | `weekday: wednesday` / `before_month: 11` / `before_day: 23` | `advent_offset: -11` | `totensonntag_offset: -4` |
| source 의 관행 서술 | 「11월 23일 전의 마지막 수요일」 — 공식 문서에서 이 꼴의 서술은 찾지 못했다(python-holidays 의 꼴) | 「같은 법 § 2 의 Totensonntag(letzter Sonntag vor dem 1. Advent) 앞 수요일 = 대림절 첫째 주일 − 11 일」 + 주의회 문장 | 주의회 문장 「am letzten Mittwoch vor dem Totensonntag」 를 그대로 + § 2 의 정의 |
| 테스트 | 1990–2100 (a)=(b)=(c), python-holidays SN 2020–2031, feiertage-api 2026, 11월 16–22일 범위, 필드 형 거부 | 같다 | 같다 |
| 다른 피드 | 없음 — 로더는 주마다 복제본이고 새 표·필드는 de_sn 에만 있다. `test_published_feed` 재현성(다른 피드 바이트 동일)·교집합 검사(D3)·de_mv 의 닫힌 필드가 보인다 | 같다 | 같다 |
| 나중에 재사용 | 다른 「요일 + 경계」 날에 쓸 수 있다 | 대림절 기준 날(Volkstrauertag·Totensonntag 는 공휴일이 아니라 지금은 없음) | Totensonntag 기준 날만 |

**권고 — (ii) `advent_offset: -11`**
1. 사람의 방향(Holiday_20 §5 「부활절 오프셋과 같은 꼴」)과 맞는다 — `easter_offset` 과 같은 「기준일 + 정수 오프셋」 이다.
2. 기준일이 같은 법 § 2 의 정의어(「1. Advent」)다. 공포본(2025 Nr. 6 S. 146)에서 읽은 자구에 닿는다. (i) 의 「11월 23일」 은 어느 공식 문서에서도 찾지 못한 꼴이다.
3. source 는 주의회 문장(「am letzten Mittwoch vor dem Totensonntag」)과 § 2 의 Totensonntag 정의를 함께 들어 자기완결로 쓸 수 있다(초안 `drafts/de_sn_advent_holidays.yaml`, 금지 문자열 검사 통과).
4. (iii) 은 같은 계산이지만 기준일을 한 번 더 거친다. 문장에 가깝게 쓰고 싶다면 (iii) 도 같은 결과다(C3).
- 초안: `drafts/`(11 건 — 고정 6, 부활절 4, 대림절 1). Fronleichnam 은 범위 밖. 전부 verified: false.

### D3 — de.ics 교집합

- `tests/test_de_be_feed.py:227–231` 의 `STATE_FEEDS` 는 `rules/` 스캔이고, `test_the_intersection_of_state_feeds_is_the_nationwide_feed`(242–259)는 해마다 주 피드 날짜 집합의 교집합 == de.ics 를 단언한다.
- Buß- und Bettag(11월 16–22일)는 다른 주 피드 어디에도 없다 → 교집합에 들지 않는다 → de.ics 그대로. **`land` scope 다.** Reformationsfest 도 `land`(de_bb·de_hb·de_hh·de_mv·de_ni·de_sh 와 같은 key 의 land 항목).

---

## Part E — 2020 이후 일회성 지정

### 목록(색인)

- 발행사 판매 사이트의 SächsGVBl. 목록(`sgvl.html`, 화면 툴바가 밝힌 `product_list_limit=25` GET)을 9 쪽 받았다 — 215 상품(호 206 + 구독 상품 3 + Anlageband 2 + a 호 4). `e_listing.py` → `e_listing.tsv`.
- 2020–2026 호(192 상품): 2020 Nr. 1–40(+38a·39a), 2021 Nr. 1–46(+40a), 2022 Nr. 1–34(+16a), 2023 Nr. 1–20(+2 Anlageband), 2024 Nr. 1–15, 2025 Nr. 1–17, 2026 Nr. 1–14(+06 Anlageband). **번호 빠짐 없음**(목록 안에서 — 그해 마지막 번호가 실제 마지막 호인지는 목록만으로 알 수 없다).
- 제목을 얻은 경로:
  - 2024–2026: 상품 화면 「Beschreibung」 의 「Inhaltsverzeichnis」(192 상품 화면 모두 200). `e_titles.py` → `e_titles.tsv`.
  - 2021 Nr. 15 – 2023: 상품 화면에 목차가 없다. 「Vorschau」 미리보기 PDF 89 건(전부 200)의 1 쪽 목차 텍스트층. `e_toc.py` → `e_toc.tsv`(390 제목). 2023 Anlageband 는 목차 없음.
  - **2020 전체(42 상품)와 2021 Nr. 1–14: 상품 화면에 목차도 미리보기도 없다 — 제목을 얻지 못했다.** 연간 색인 「Inhaltsverzeichnis … Jahrgang 2021」 은 2022 Nr. 5 의 목차에 있지만 그 미리보기(72 쪽)에는 색인 쪽이 없다(마지막 두 쪽은 S. 115 Impressum·S. 116 뒤표지, 렌더 확인).

| 연도 | 호 | 제목 출처 | 공백 |
|---|---|---|---|
| 2020 | 1–40, 38a, 39a | — | **전부** |
| 2021 | 1–46, 40a | 15–46·40a 미리보기 1 쪽 | **1–14** |
| 2022 | 1–34, 16a | 미리보기 1 쪽 | 없음 |
| 2023 | 1–20 (+Anlageband) | 미리보기 1 쪽 | Anlageband 목차 없음 |
| 2024–2026 | 1–15 / 1–17 / 1–14 | 상품 화면 목차 | 없음 |

### 제목 검색과 REVOSax

- 검색어(`e_search.py`): feiertag, gedenktag, einmalig, bettag, arbeitsruhe, sächssfg — casefold 와 공백 제거본 둘 다.
- REVOSax 빠른 검색 「Feiertag」(sachsen.de 의 GET 폼과 같은 주소, `revosax_search.py`로 14 쪽 넘김): 67 건. 결과의 Erlassdatum 이 2020-01-01 이후인 것 27 건을 분류했다. 화면의 필터(연도 패싯)는 토큰이 든 POST 폼이라 쓰지 않았고 결과 날짜로 골랐다. 화면 숨은 필드 `search_request[valid_day]=2026-11-18` 이 있다 — [추론] 그날 유효한 문서만 찾는다. 날이 지난 일회성 선언은 들지 않을 수 있다.

**분류**(`e_classify.py` → `e_classified.tsv`)

| 출처 | 적중 | A § 1 개정 | C 일회성 지정 | D 언급뿐 |
|---|---|---|---|---|
| 관보 목차 제목(2021 Nr. 15 – 2026) | 2 | 0 | 0 | 2 |
| REVOSax 「Feiertag」, 2020 이후 | 27 | 0 | 0 | 27 |

- 관보 목차 적중 둘:
  - 2025 Nr. 6 「Gesetz zur Einführung eines Gedenktages …」 — SächsSFG § 2·§ 6 개정. § 1 무관(S. 146 판독).
  - 2022 Nr. 25 「… Gewährung eines einmaligen Heizkostenzuschusses …」 — 공휴일과 무관.
- REVOSax 27 건: 근무시간·급여·절차·방송·교정·선거 등 다른 법이 Feiertag 를 언급한다. 정식 제목만 보고 판정했다 — 본문은 열지 않았다.
- [추론] SächsSFG 에는 HE·SL·MV 같은 일회성 지정 수권 조항이 없다(현행 통합본 전문에 「einmalig」·「erklären」 이 없다 — A1 텍스트). 일회성 공휴일은 법률 개정으로만 생길 것이고, 2020 이후 SächsSFG 개정은 2025(§ 2·§ 6) 하나다(A2).

---

## 사람의 판단 요청

1. **key `buss_und_bettag` 의 승인.** `rules/de/solar_holidays.yaml:23–24` 가 예고한 값이다(「주별 피드에서 … Buß- und Bettag (→ buss_und_bettag) 이 처음 쓰게 된다」). 지금 어느 표에도 없다 — 승인하면 신규 key 하나다.
2. **규칙 표현.** 권고 (ii) `advent_offset: -11`(de_sn 로더에만). (iii) Totensonntag 오프셋도 같은 결과다. (i) 은 공식 서술이 없는 꼴이다.
3. **날짜 관행의 근거로 무엇을 source 에 둘지.**
   - 작센 주의회 청원 보고서 2023 의 문장(조문이 아니라 위원회 간행물) — 작센 공식 문서로 찾은 유일한 날짜 서술.
   - SächsSFG § 2 의 Totensonntag 정의(2025 공포본에서 읽음).
   - Hessen 1971 의 조문 정의(다른 주의 옛 법률) — 교차 확인으로 머리 주석에만 둘지.
4. **verified.** 11 건 전부 false 가 된다(B3). 2002 Nr. 9 를 유료 보관 상품으로 살지는 사람이 정한다(이번에는 사지 않았다).
5. **Part E 의 공백.** 2020 전체와 2021 Nr. 1–14 의 목차를 얻지 못했다. 이 공백을 머리 주석에 「찾지 못함(범위)」 으로 쓰고 갈지 정한다. [추론] SächsSFG 에 일회성 수권이 없다는 점(위)은 그 공백의 무게를 줄이지만 지우지는 않는다.
6. **state_SL.md 의 정정.** 2026-09-30 조사의 「1976 원문의 Buß- und Bettag(11월 23일 이전 마지막 수요일)」 은 조문에 없다(C2). 그 폴더 README 에 정정 절을 둘지 정한다.
7. **Fronleichnam(지정 지역)** 은 2026-09-30 조사대로 범위 밖으로 둔다 — 확인 요청.
