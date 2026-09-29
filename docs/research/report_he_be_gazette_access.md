# HE·BE 관보 접근성과 개정 체인 — 조사 보고

- 작성: 2026-09-29. 조사만 했고 레포 변경·브랜치·이슈·PR 은 없다.
- 기준 커밋: `main` = `1c48434` (#113 머지).
- 스크래치(이하 `$S`): `/private/tmp/claude-501/-Volumes-Data-dev-holidays/24975730-c66a-424c-9aac-edbbff0b4553/scratchpad/hebe`
- 도구:
  - PyMuPDF 1.26.5(`uv run --no-project --with`, 격리 실행)
  - macOS Vision OCR(`$S/ocrbin`, NW 조사 때와 같은 바이너리)
  - `curl`, `shasum -a 256`
  - Wayback CDX
- berlin.de 요청: 둘째 요청부터 식별 User-Agent 를 달고 간격을 뒀다 —
  `holidays-lunalism-research/1.0 (+https://holidays.lunalism.com/; one-off gazette survey, low rate)`.
  berlin.de 이용 조건(robots.txt 머리)이 자동 프로그램에 고유 식별을 요구한다.

---

## ⚠ 전제와 실물의 차이 (먼저 읽을 것)

1. **BE designated_holidays 는 "전부 true" 가 아니다.**
   - `achter_mai_2020` 이 `verified: false` 다.
   - source_todo 는 frauentag 와 같은 「2019-01-30 개정 관보 GVBl. S. 22 원문」이다.
   - 보강 지시에 따라 BE 조사 대상에 frauentag 와 함께 넣었다. BE 대상은 기저 9 + frauentag + achter_mai_2020 = 11 건이다.
2. **BE 에는 Neufassung 이 없다.** 기저는 1954 원 공포(GVBl. S. 615)다. 온라인 개정 넷(2010·2015·2019·2024)은 모두 부분 개정이다([C]-BE). 그래서 기저 9 건의 자구는 1954 원문과 1994 개정 이전 호들에 의존한다.
3. **HE 의 Neufassung 은 GVBl. 1971 I Nr. 36 S. 343 이다(§ 1 은 S. 344).** 2 차 소스의 「1972 I S. 343」은 연도가 틀렸다.
4. **HE 현행 § 1 Abs. 1 의 자구 출처는 둘이다.** 1971 Neufassung 과 1994 Fünftes Änderungsgesetz(S. 596). 그 뒤 개정(1997·2010·2012)은 § 1 을 건드리지 않았다.

## 0. 선행 실측 — [실측]

### 0-1. 항목 수·verified·source_todo

| 파일 | 항목 | verified | source_todo |
|---|---|---|---|
| rules/de_he/solar_holidays.yaml | 5 | false 5 | 「공식 포털 hessenrecht(jlr-FeiertGHE1952pP1) 열람 또는 GVBl. 원본」 ×5 |
| rules/de_he/easter_holidays.yaml | 5 | false 5 | 같음 ×5 |
| rules/de_be/solar_holidays.yaml | 6 | false 6 | 기저 5 는 「공식 포털 gesetze.berlin.de 열람 또는 관보 원본」, frauentag 는 「2019-01-30 개정 관보 GVBl. S. 22 원문」 |
| rules/de_be/easter_holidays.yaml | 4 | false 4 | 「공식 포털 gesetze.berlin.de 열람 또는 관보 원본」 ×4 |
| rules/de_be/designated_holidays.yaml | 3 | true 2 · **false 1** | achter_mai_2020: 「2019-01-30 개정 관보 GVBl. S. 22 원문」 |

### 0-2. 머리 주석의 포털 주장(verified 절)

- HE: 「공식 포털 rv.hessenrecht.hessen.de 는 JS 셸만 돌아와 (curl·headless 180초·WebFetch 실패, /tmp/report_de_laender.md HE §1)」. 조문 출처는 umwelt-online Stand 28.08.2023 과 Bistum Fulda PDF.
- BE: 「공식 포털(gesetze.berlin.de)은 JS 셸만 돌아와 … (/tmp/report_de_laender.md BE §1)」. 조문 출처는 umwelt-online 과 berlin.de 안내.
- BE designated: 「2020 건은 2019 개정문을 비공식 사본으로만 읽어 false」.

---

## [A] 공식 통합본 포털 재측정

### A1. 서버 렌더·딥링크 — [실측] 둘 다 여전히 JS 셸

| 포털 | URL | 결과 |
|---|---|---|
| HE | https://www.rv.hessenrecht.hessen.de/bshe/document/jlr-FeiertGHE1952pP1 | 200 `text/html`, 5,519 B. 루트·perma 링크도 같은 5,519 B 셸. `Feiertage sind`·`jlr-Feiert` 0 건 |
| BE | https://gesetze.berlin.de/bsbe/document/jlr-FeiertGBErahmen | 200 `text/html`, 5,432 B. 루트와 같은 셸. § 1 본문 없음 |

두 포털 모두 juris 플랫폼이다. 셸은 `/bshe/assets/index-*.js` 한 스크립트를 싣는다. NW(recht.nrw.de, Drupal 서버 렌더)와 달리 개편되지 않았다.

### A2. 포털이 쓰는 API — [실측] 인증 없이는 거절 → 여기서 멈춤

- HE 번들(`$S/he_index.js` 와 `$S/hejs/`)의 설정: `VITE_apiPath:`/jportal/wsrest/recherche3/``.
- 요청 헤더는 `JURIS-PORTALID`, 세션 쿠키(`credentials:"include"`), 서버가 준 뒤로는 `X-CSRF-TOKEN` 이다.
- 브라우저와 같은 첫 호출 `POST …/jportal/wsrest/recherche3/init`(JSON, `JURIS-PORTALID: bshe`)에 대해 HE·BE 모두 HTTP 500 이 왔다:

  ```
  "msgId":"security_notAuthenticated"
  … iam-kv-service - iam-login-kv-service
  ```

- 페이지 로드도 쿠키를 주지 않았다(cookie jar 비어 있음). 앱 내부 로그인 흐름(`mylexToken`, `getConnectProperties`)을 재현하는 것은 우회가 된다. 그래서 하지 않았다.

### A3. 개정 이력 — 열람 불가

- 위 API 가 막혀 포털의 Änderungshistorie·Fassungen 을 볼 수 없다.
- 검색 결과 스니펫에 BE 문서 제목 「VIS Berlin - FeiertG BE | gültig ab: 09.11.1954」가 보인다. 본문은 아니다.

---

## [B] 관보 원본 온라인

### B-HE — [실측] 헤센 주의회 starweb 이 1945–2026 전 호를 PDF 로 공개

- 목록: https://starweb.hessen.de/portal/browse.tt.html?action=gvbl — HE 포털 번들에도 이 링크가 있다. 주의회(Hessischer Landtag) 서버다.
  - 호 PDF: `https://starweb.hessen.de/cache/GVBL/<연도>/<호 5 자리>.pdf`. 목록에 2,737 링크(1945–2026)가 있고, http 는 https 로 302 된다.
  - 연간 색인:
    - 1946·1949–2009 는 `…/<연도>/inhalt.pdf`
    - 2010–2022 는 `…/<연도>/00000.pdf`
    - 2023–2026 은 404(색인 없음)
- 형태:
  - 1971–1997 호: CCITT G4 스캔, 텍스트층 없음.
  - 2010 이후: 텍스트층 있음. 예외는 2012 Nr. 16(이미지만).
  - 연간 색인 1952–2003·2008–2009 는 텍스트층 없음, 2004–2007 은 있음.
- 다른 디지털화: 찾을 필요가 없었다(공식 호 전체가 있음).
- Wayback: `starweb.hessen.de/cache/GVBL/*` 2,000 건 이상(2008–2025). 1971 Nr. 36 은 13 캡처, 1994 Nr. 25 는 12 캡처가 있고 digest 가 라이브와 같다([D]).

### B-BE — [실측] 공식 온라인은 2004 년부터, 그 이전은 찾지 못함

| 출처 | 범위 | 형태·접근 |
|---|---|---|
| berlin.de 사법행정부 `…/sen/justiz/service/gesetze-und-verordnungen/<연도>/…pdf` | 2004–2026(연도 면: 2004·2005·2006·2007·2008·2009·2010·2012·2013·2014·2015·2016·2017·2018·2019·2020–2026 확인) | 호 단위 PDF, 텍스트층 있음. **429 「Please respect our berlin.de/robots.txt」 가 간헐적으로 온다** — 식별 UA·4~30 초 간격에서도 발생 |
| 베를린 주의회 PARDOK `https://pardok.parlament-berlin.de/starweb/adis/citat/VT/<선거기>/gvbl/g<YY><호 2 자리><면 4 자리>.pdf` | 선거기 16·17·18·19 에서 적중. 12(1990–95)에서 1994 S. 491 은 호 01–99 전부 404 | 법률 단위 발췌(해당 면만), 텍스트층 있음, robots.txt `Disallow:` 공란 |
| gvbl-berlin.de(Wolters Kluwer) | 2009~ 아카이브 | 구독자 전용 — 유료 장벽, 들어가지 않음 |
| reichsgesetzblatt.de(Berlin GVBl 사본) | 1945~ 일부 | 403 Forbidden(robots.txt 포함) — 접근 차단, 우회하지 않음. Wayback 에는 1945–1951 파일 일부만 있고 1954·1991·1994 는 없다(1990 은 IA 일시 장애로 미확인) |
| ZLB 디지털 주립도서관(digital.zlb.de) | Amtsblatt·Dienstblatt 는 있음 | GVBl 적중 없음(제목 검색) |
| Deutsche Digitale Bibliothek API | — | 403(키 필요) — 멈춤 |

**1954 S. 615 와 1994 S. 491 의 온라인 사본은 찾지 못했다.**

Wayback:
- berlin.de 2019 Nr. 3 는 10 캡처(2019–2024).
- PARDOK `g19030022` 는 0 캡처.
- gesetze.berlin.de 문서는 10 캡처(셸).

---

## [C] 체인 개요

### C-HE — [실측]

**기저:** Bekanntmachung der Neufassung vom 29.12.1971, **GVBl. 1971 I Nr. 36 S. 343**(30.12.1971 발행), § 1 은 S. 344.
- 근거: `$S/he/chain/1971-00036.pdf` 1 쪽 목차 OCR 「Neufassung des Gesetzes über die Sonn- und Feiertage」 343, 2 쪽 머리 「344 Nr. 36」.
- 1971 § 1 Abs. 1 Nr. 8(OCR 복사): "8. der Tag der deutschen Einheit (17. Juni),"
- Nr. 9 는 Buß- und Bettag, Nr. 10 은 "der 1. und 2. Weihnachtsfeiertag".

**1971 이후 개정 — 목록의 출처와 닫힘**

| 개정 | 공포 | GVBl. | 닿은 조항 | § 1 Abs. 1 변경 |
|---|---|---|---|---|
| Gesetz zur Änderung kommunalrechtlicher Vorschriften vom 15.05.1974 | 21.05.1974 | 1974 I Nr. 17 S. 241(HFeiertagsG 부분 S. 242) | § 14·§ 16 | 없음 |
| **Fünftes Gesetz zur Änderung des Hessischen Feiertagsgesetzes vom 11.10.1994** | 19.10.1994 (시행 31.12.1994) | **1994 I Nr. 25 S. 596** | § 1·7·8·9·17·18 | **있음** — 복사: "a) Nr. 8 erhält folgende Fassung: „8. der Tag der Deutschen Einheit,"" / "b) Nr. 9 und 10 werden durch folgende Nr. 9 ersetzt:" / "„9. der 1. und 2. Weihnachtstag."" |
| Sechstes Gesetz zur Änderung … vom 26.11.1997 | 02.12.1997 | 1997 I Nr. 24 S. 396 | § 14 | 없음 |
| Gesetz zur Änderung des Hessischen Feiertagsgesetzes und des Hessischen Ladenöffnungsgesetzes vom 02.02.2010 | 2010 | 2010 I Nr. 2 S. 10 | § 6·§ 14·§ 17(2014 실효 조항 추가) | 없음 |
| Art. 3 eines Gesetzes vom 13.12.2012 | 21.12.2012 | 2012 Nr. 28 S. 622 | § 17 Satz 2 삭제 | 없음 |

1994 호가 § 1 Abs. 1 전체를 다시 싣지는 않는다. Nr. 8 은 새 문언을 주고, Nr. 9·10 은 새 Nr. 9 로 바꾼다. Nr. 1–7 은 1971 자구 그대로다.

**목록의 출처**
1. 공식 연간 색인
   - 1952–2009: 1952–2003·2008–2009 는 스캔이라 58 권 전 쪽(777 쪽)을 Vision OCR 로, 2004–2007 은 텍스트층으로 봤다.
   - 2010·2012 는 `00000.pdf` 다.
   - 적중: 1952 제정, 1954·1957 Ergänzung, 1964 Drittes, 1971 Viertes·Neufassung, 1994 Fünftes, 1997 Sechstes.
   - 색인은 1974 옴니버스 개정을 「Feiertag」 항목으로 올리지 않았다.
2. 각 개정 공포본 서두의 자기 인용 — 이것이 1974 를 잡았다.
   - 1994 S. 596 서두(OCR 복사): "Fassung vom 29. Dezember … S. 344), geändert durch … 15. Mai 1974 (GVBl. I S. 241)"
   - 1997 S. 396: "zuletzt geändert … vom 11. Oktober 1994"
   - 2010 S. 10: "zuletzt geändert durch Gesetz vom 26. November 1997 (GVBl. I S. 396)"
   - 2012 Nr. 28 Art. 3: "zuletzt geändert durch Gesetz vom 2. Februar 2010 (GVBl. I S. 10)"
   - 2021 Nr. 17(코로나 검사 명령): "zuletzt geändert durch Gesetz vom 13. Dezember 2012 (GVBl. S. 622)"

   → **1971 → 2021 전 구간이 공포본 자기 인용으로 닫힌다.**
3. 2013–2026 의 닫힘 방식(보강 지시 3):

| 연도 | 연간 색인 | 호별 검색 | 비고 |
|---|---|---|---|
| 2013–2022 | `00000.pdf` 있음(텍스트층) — 개정 적중 0 | 전 호 텍스트층 전문 검색 — 개정 적중 0 | 2013 색인에 「Reformationstag 2017」 명령(부수 관찰 2) |
| 2023–2026 | **없음**(404) | **전 호 텍스트층 전문 검색**(2023 39·2024 91·2025 117·2026 65 호, 2026 은 목록상 마지막 호까지) — `Feiertagsgesetz`·`HFeiertagsG` 적중 0 | 연간 색인이 없어 호별 검색만으로 닫힌다 |

- 2010–2026 호별 검색 결과는 `$S/he/issues_scan.tsv` 에 있다(776 호 / 목록 776 링크, NETFAIL 0, 재시도 0).
- 텍스트층이 없는 호는 2012 Nr. 16 하나다. 그 호는 1 쪽 목차만 OCR 로 봤다(식품화학사 규정 등 무관).
- 2021 자기 인용이 2012 → 2021 을 따로 닫는다.

### C-BE — [실측] + 보강 지시 2

**기저:** Gesetz über die Sonn- und Feiertage vom 28.10.1954, GVBl. S. 615. Neufassung 공고는 찾지 못했다. 이후 개정은 모두 이 원 공포본을 인용한다.

**온라인 개정 넷의 § 1 Abs. 1 지시문(복사 인용, 15 단어 이내 조각)**

| 개정 | GVBl.(호·면) | § 1 Abs. 1 지시문 | 분류 |
|---|---|---|---|
| Art. VI eines Gesetzes vom 15.12.2010 | 2010 Nr. 32 S. 560 | § 1 Abs. 1 지시 없음. 복사: "1. § 2 wird wie folgt geändert:" / "2. In § 4 Satz 1 wird das Wort „kirchlichen" …" | 해당 없음(§ 2·§ 4 만) |
| Gesetz zur Änderung … vom 14.10.2015, Art. 1·2 | 2015 Nr. 22 S. 378 | Art. 1: "1. In Nummer 9 wird der Punkt am Ende gestrichen." / "2. Folgende Nummer 10 wird angefügt:" / "„10. der 31. Oktober 2017 (500. Jahrestag der Reformation)."". Art. 2(2018-01-01 시행): "2. Nummer 10 wird aufgehoben." | **부분 개정** |
| Drittes Gesetz zur Änderung … vom 30.01.2019, Art. 1·2 | 2019 Nr. 3 S. 22 | Art. 1: "a) Nach Nummer 1 wird folgende neue Nummer 2 eingefügt:" / "„2. der Frauentag (8. März)"" / "b) Die bisherigen Nummern 2 bis 9 werden die Nummern 3 bis 10." / "d) Folgende Nummer 11 wird angefügt:" / "„11. der 8. Mai 2020 (75. Jahrestag der Befreiung vom Na­tionalsozialismus …"". Art. 2(2020-05-09 시행): "2. Nummer 11 wird aufgehoben." | **부분 개정** |
| Viertes Gesetz zur Änderung … vom 10.07.2024, Art. 1–3 | 2024 Nr. 28 S. 460 | Art. 1: "2. Folgende neue Nummern 11 und 12 werden angefügt:" (8. Mai 2025, 17. Juni 2028). Art. 2(2025-05-09 시행): "Nummer 11 wird aufgehoben." / "Nummer 12 wird zu Nummer 11 …". Art. 3(2028-06-18 시행): "Nummer 11 wird aufgehoben." | **부분 개정** |

**보강 지시 2 의 답**
- § 1 Abs. 1 을 전부 다시 싣는("wird wie folgt gefasst"/"erhält folgende Fassung" + 전체 목록) 온라인 개정은 **없다**. 넷 모두 삽입·삭제·재번호다.
- 따라서 현행 Nr. 1·3–10(기저 9 건)의 자구는 온라인 공포본 어디에도 전체로 실려 있지 않다. 1954 S. 615 와 그 뒤 1994 까지의 개정(적어도 1994 S. 491)이 **여전히 자구 원천으로 필요하다**.
  - 2019 Art. 1 b) 는 번호만 옮기고 자구를 싣지 않는다.
- frauentag·achter_mai_2020 은 **§ 1 Abs. 1** 에 있다(다른 단락이 아니다). 둘의 자구는 2019 S. 22 Art. 1 a)·d) 가 새 문언으로 스스로 싣는다. 2020 건의 소멸은 같은 호 Art. 2 다.
  - 2019 호 Art. 1 의 다른 줄: "2. § 3 wird wie folgt gefasst:" 은 § 3(Gedenk- und Trauertage)을 새로 싣는 것이라 공휴일과 무관하다.

**1954 → 2010 의 목록과 닫힘**
- 2010 Art. VI 서두(복사): "das zuletzt durch Gesetz vom 2. Dezember 1994 (GVBl. S. 491) geändert worden ist" → 1994 → 2010 이 닫힌다.
- 2015 서두: "zuletzt durch Artikel VI des Gesetzes vom 15. Dezember 2010 (GVBl. S. 560)"
- 2019 서두: "zuletzt durch Gesetz vom 14. Oktober 2015 (GVBl. S. 378)"
- 2024 Art. 1 서두: "zuletzt durch Artikel 2 des Gesetzes vom 30. Januar 2019 (GVBl. S. 22)"

  → **1994 → 2024 는 공포본 자기 인용으로 닫힌다.**
- 1954 → 1994 의 개정 목록은 **미확인**이다.
  - umwelt-online 의 이력 줄은 "(GVBl. 1954 S. 615; ...; 02.12.1994 S. 491; …" 로 그 사이를 줄임표로 생략한다.
  - datumsrechner.de 사본(2 차)은 "Zuletzt geändert am 02. Dezember 1994 (GVBl. S. 491)" 과 9 호 목록만 있다.
  - 1994 개정문 서두가 그 앞을 닫아 줄 수 있지만, 1994 호를 온라인에서 찾지 못했다.
- 2024 이후(2024-07 → 2026-09): 온라인 공포본의 자기 인용은 없다. berlin.de 2024 후반~2026 호 검색은 429 로 하지 않았다(미확인).

---

## [D] 취득과 결정성 — [실측]

재수령은 같은 URL 을 다시 받아 sha256 을 비교한 것이다.

| 주 | 호·파일 | URL | 크기 | 텍스트층·필터 | 1 차 sha256 | 재수령 |
|---|---|---|---|---|---|---|
| HE | 1971 I Nr. 36 (S. 343–346) | https://starweb.hessen.de/cache/GVBL/1971/00036.pdf | 269,786 | 없음, CCITT | `fc2067c2778f3db8a8b7295c72d25f7df020b1b18e512fb2b648432f9ec21f55` | 동일, Wayback 7 캡처 digest 동일(2023–2026) |
| HE | 1974 I Nr. 17 (S. 237–254) | …/GVBL/1974/00017.pdf | 1,255,095 | 없음, CCITT | `c60d3c2485044454b68433e65da308b1d4c4652a4421b721b8d9d12b3fa85324` | 동일 |
| HE | 1994 I Nr. 25 (S. 575–622) | …/GVBL/1994/00025.pdf | 3,867,324 | 없음, CCITT | `a16fbf4cc3298d219e56cc8e0d1f7354d3d33c822058f41b3c07153ef0ef8ff5` | 동일, Wayback 6 캡처 digest 동일 |
| HE | 1997 I Nr. 24 (S. 389–400) | …/GVBL/1997/00024.pdf | 719,897 | 없음, CCITT | `5e6c9c12ee5a54a744fdf4e8473dc1e1287d9bd5ad81d5c5b1b70abd611ff6da` | 동일 |
| HE | 2010 I Nr. 2 (S. 9–16) | …/GVBL/2010/00002.pdf | 76,978 | 있음 | `f00147e4ec7e21951f019f46394816d3a351ea1e7be33326263846cb06608ebb` | 동일 |
| HE | 2012 Nr. 28 | …/GVBL/2012/00028.pdf | 5,005,836 | 있음 | `c540eb5b8aaec7e6be8e559f06991e052c928908bdc95602e72a5cfbe74a22b5` | 동일 |
| BE | 2010 S. 560 (PARDOK 발췌 5 쪽) | https://pardok.parlament-berlin.de/starweb/adis/citat/VT/16/gvbl/g10320560.pdf | 701,496 | 있음 | `9aa97d9087f162a3d8e64810211a0ce61e3342460b548a9700a685fd750dee4d` | 동일 |
| BE | 2015 S. 378 (PARDOK 1 쪽) | …/VT/17/gvbl/g15220378.pdf | 1,267,735 | 있음 | `818cb238056014e77cb2fe098e55ccaade8bae6aa694fce75091169a40c93941` | 동일 |
| BE | 2019 S. 22 (PARDOK 1 쪽) | …/VT/18/gvbl/g19030022.pdf | 105,284 | 있음 | `714f8bfc1cb1ac1babe023519d62b02546bd2310dfe8429ce452cce380bc85e2` | 동일 |
| BE | 2024 S. 460 (PARDOK 1 쪽) | …/VT/19/gvbl/g24280460.pdf | 100,555 | 있음 | `750494cd72ff03c5259022a396f2641be42ac6aff5b1d5367c2994c469503353` | 동일 |
| BE | 2010 Nr. 32 호 전체(S. 549–572) | berlin.de `…/2010/mdb-senatsverwaltungen-justiz-gesetz-undverordnungsblatt2010-ausgabe_nr__32_v__28_12_2010_seite_549_bis_572.pdf` | 1,101,580 | 있음 | `467dd54acb34d6a4eb8c02d6ba76a38cab3a3867167d8c2bb815b5b85035d38f` | 동일 |
| BE | 2015 Nr. 22 호 전체(S. 377–380) | berlin.de `…/2015/ausgabe-nr-22-vom-24-10-2015-seite-377-bis-380.pdf` | 1,335,409 | 있음 | `5712b8aad9006a95a7fdecf58470c3ad8b6706bc8f4daecdb45b29cf75e869ad` | **미확인** — 다른 시도가 429 |
| BE | 2019 Nr. 3 호 전체(S. 21–32) | berlin.de `…/2019/ausgabe-nr-3-vom-6-2-2019-s-21-32.pdf` | 1,701,342 | 있음 | `41d37be751c8b755ac859be3593d67c7fed2087952edfef3a7cc2d16348b3978` | 재수령은 429. Wayback 200 캡처 7 개 중 5 개가 digest 동일(2019-02~2024-06), **2 개(2019-07·2021-05)는 다른 digest·약 1.02 MB** — 같은 URL 이 두 판을 낸 적이 있다 |
| BE | 2024 Nr. 28 호 전체(S. 457–484) | berlin.de `…/2024/ausgabe-nr-28-vom-2072024-s-457-484.pdf` | 420,867 | 있음 | `4dca2ff84516083ce6e8e5cfe5fcfef3167580204d1f852921a5354ca59af849` | **미확인** — 다른 시도가 429 |
| BE | 1954 S. 615 / 1994 S. 491 | — | — | — | — | **온라인 원본 없음** |

- HE 1971 Nr. 36 판독은 Vision OCR 로 § 1 을 읽는 데까지만 했다. 전사는 하지 않았다.
- berlin.de 429 이력:
  - 첫 2 요청 뒤 차단됐다.
  - 약 25 분 뒤 식별 UA 로 풀렸다.
  - 연속 요청(4 초 간격)에서 다시 번갈아 429 가 왔다.
  - 30 초 간격 재시도도 첫 요청부터 429 였다.
  - 그 뒤로는 요청하지 않았다.

---

## [E] 판정표

| 주 | 필요한 호 / 온라인 / 결정적 | 빠진 호와 이유 | "이후 무개정" 구간을 닫는 방법 | 판정 |
|---|---|---|---|---|
| HE (10 건) | § 1 자구: 1971 I Nr. 36·1994 I Nr. 25 — 2/2 온라인, 2/2 결정적(Wayback 까지 동일). 체인 증빙용 1974·1997·2010·2012 도 온라인·결정적 | 없음 | 공포본 자기 인용 사슬 1971 → 1974 → 1994 → 1997 → 2010 → 2012 → 2021(Nr. 17). 2013–2022 연간 색인 + 전 호 전문 검색, 2023–2026 전 호 전문 검색(텍스트층) | **온라인으로 NW 식 승격 가능** |
| BE 기저 9 건 | 자구 원천: 1954 S. 615·1994 S. 491(+1954–1994 사이 미상 개정) — 0 온라인. 2019 S. 22(번호 재배치)는 온라인·결정적(PARDOK) | 1954·1994: berlin.de 는 2004~, PARDOK 은 선거기 16~ 에서만 적중, reichsgesetzblatt.de 403, ZLB 없음, gvbl-berlin.de 유료 | 1994 → 2024 는 자기 인용(2010·2015·2019·2024 서두). 1954 → 1994 와 2024-07 이후는 미확인 | **실물 관보 필요**(자구 원천이 오프라인) |
| BE frauentag·achter_mai_2020 (2 건) | 2019 S. 22 — 온라인(PARDOK·berlin.de), PARDOK 판 결정적 | 없음(berlin.de 호 전체 판은 재수령 미확인·두 판 이력) | 2019 → 2024 자기 인용(2024 Art. 1 서두). 2024 개정은 Nr. 11·12 만 다룬다. 2020 건은 2019 Art. 2 로 소멸이 자체 확인된다 | **온라인으로 가능**(2 건만) |

## [추론] 권고

1. **HE 를 다음 승격 대상으로 권한다.**
   - NW 와 같은 모양이다: Neufassung 한 호 + 개정 한 호, 파일 해시형, 체인은 자기 인용.
   - NW 보다 닫힘이 강하다. 공포본 자기 인용이 2021 까지 닿고, 2023–2026 도 호별 전문 검색으로 닫힌다. 색인 공백 같은 것이 없다.
   - 판독은 CCITT 스캔 두 호(S. 344, S. 596)로 끝난다.
   - 주의:
     - HE YAML 이 인용하는 umwelt-online 자구 "1. der Neujahrstag … 9. der 1. und 2. Weihnachtstag" 은 1994 개정 뒤 번호 체계와 맞다.
     - EKHN 사본은 번호가 없고 소문자 "deutschen" 이다. 1994 공포본은 대문자 "Deutschen" 이므로 공포본 쪽이 umwelt-online 과 맞을 공산이 크다. 판독은 다음 세션 몫이다.
2. **BE 는 쪼갠다.**
   - frauentag·achter_mai_2020 두 건은 2019 S. 22(PARDOK 결정적)로 지금 온라인 승격이 가능하다.
   - 기저 9 건은 1954·1994 실물(베를린 ZLB·주의회 도서관·juris 유료)이 필요하다. HH·NI·RP 와 같은 줄에 선다.
3. berlin.de 를 근거 URL 로 쓰면 429 와 두 판 이력 때문에 재현성이 약하다. BE 의 파일 해시형 근거는 PARDOK 발췌를 쓰는 편이 낫다고 본다.

## 결정에 필요한 남은 미확인

- BE 1954 → 1994 사이 § 1 Abs. 1 개정의 목록과 내용. 특히 1990 년 전후 "Tag der deutschen Einheit" 의 의미 전환이 조문 개정으로 됐는지.
- BE 2024-07 이후 개정 유무(berlin.de 2024 후반~2026 호 미검색, 429).
- berlin.de 2015·2024 호 전체 PDF 의 결정성(429 로 재수령 못 함).
- HE 포털·BE 포털의 개정 이력(인증 없이 열람 불가).

## 부수 관찰

1. **레포 이력의 세션 링크.** `git log --all -i --grep=<세션 URL 패턴>` 이 커밋 75 개를 낸다(2026-08-23 ~ 2026-09-06, 예: `a9dc26e` feat(de_be), `fac7955` feat(de_by)). 트레일러 금지 규칙 이전 커밋으로 보인다. 이미 main 이력이라 고치려면 이력 재작성이 필요하다 — 범위 밖, 기록만. [세션 URL 패턴은 레포의 세션 링크 grep 을 0 으로 두려고 가렸다.]
2. **HE 일회성 공휴일.**
   - GVBl. 2013 S. 566 「Verordnung zur Bestimmung des Reformationstages 2017 zum gesetzlichen Feiertag」(16.10.2013)이 있다.
   - HE YAML 「§ 2 … 에 따른 명령은 조사에서 확인된 것이 없어」와 다르다.
   - HE 피드 범위는 `RANGE_START = date(2020, 1, 1)`(`rules/de_he/feed.py:54`)라 발행 영향은 없다.
3. **BE 의 다른 일회성.** 2015 S. 378 이 2017-10-31 을 § 1 Abs. 1 Nr. 10 으로 넣었다가 2018-01-01 에 지웠다. 피드 범위 밖이다.
4. HE 1953 연간 색인에 「Verordnung über den Volkstrauertag im Jahre 1953」 등 초기 명령류가 있다. 범위 밖이다.

## 스크래치 파일

- HE:
  - `$S/starweb_gvbl.html` — 호 목록
  - `$S/he/inhalt/*.pdf` — 연간 색인 1952–2009
  - `$S/he/inhalt_ocr.tsv`·`$S/he/inhalt_txt_*.txt` — 색인 OCR
  - `$S/he/issues/*.pdf`·`$S/he/issues_scan.tsv` — 2010–2026 776 호
  - `$S/he/idx/`
  - `$S/he/chain/*.pdf` — 1971·1974·1994·1997·2012 호
  - `$S/det/*.2.pdf` — 재수령본
- 포털: `$S/p_*.html`(셸), `$S/he_index.js`, `$S/hejs/`(번들 청크 1,346 개, 크롤 중단)
- BE:
  - `$S/be/g*_a.pdf`(PARDOK), `$S/be/bd_*.pdf`(berlin.de; 일부는 429 HTML — 크기 약 340 B 인 파일)
  - `$S/be/uo_feiertg.html`, `$S/be/datumsrechner_berlin.pdf`, `$S/be/robots.txt`
- 스크립트: `$S/he_scan.py`, `$S/he_toc.py`, `$S/he_find.py`, `$S/ocr_inhalt.py`
