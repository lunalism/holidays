# 독일 source 자기완결성과 HH 31. Oktober 서지 — 다음 데이터 PR 준비 조사

- 측정 시점: 2026-09-30. `origin/main` = `e5a3e2113a1339957dc793a4cfd8a2834cc2117c` (#118 머지).
- 범위: 조사만 했다. 레포 파일 변경·브랜치·PR 없음. 관보 검색은 새로 돌리지 않았다. D-3 의 HH 호 1 건만 받았다.
- 재현 기록은 `~/holidays-reports/report_source_selfcontain/` 에 있다.
  - `dump_sources.py` → `sources.tsv`: 108 항목. source 는 `_one_line` 과 같게 정규화했다.
  - `classify.py` → `hits.tsv`: 범주 패턴 적중. 대소문자 구분·무시 건수를 함께 낸다.
  - `affected_events.py` → `affected_events.txt`: E 의 이벤트 수.
  - `hh_fetch.log`: D-3 요청 기록.
  - `hh_pdf_text.py` → `hh_pdf_text.txt`: D-3 PDF 텍스트층.
  - HH PDF 원본은 폴더에 두지 않았다(`/tmp/hh_pdf/` 에만 있다). `docs/research/README.md` 「넣지 않는 것」 — 받은 원본.
- 표기: 명령 출력에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.

---

## 0. 사전 확인 — 통과(멈춤 없음)

### 0-1. sha
- `git fetch --prune` 의 prune 은 `origin/docs/noscript-duplication-value` 하나다(#118 머지 브랜치).
- `main` 은 `9a2c001..e5a3e21` 로 fast-forward 했다. 측정 sha 는 `e5a3e21` 이다.

### 0-2. source → DESCRIPTION 경로
독일 피드 10 개(`rules/de/feed.py`, `rules/de_*/feed.py`)가 DESCRIPTION 을 만드는 곳은 파일마다 **정확히 한 곳**이다(`grep -c 'description='` = 1).

| 피드 | 줄 | 식 |
|---|---|---|
| de | `rules/de/feed.py:167` | `f"{BUNDESWEIT_SENTENCE}\n\n근거: {_one_line(entry['source'])}"` |
| de_be | `rules/de_be/feed.py:157` | `f"{SCOPE_SENTENCE[entry['scope']]}\n\n근거: {_one_line(entry['source'])}"` |
| de_bw·by·he·hh·ni·nw·rp·sh | 각 `feed.py:143–149` | 위와 같은 식 |

- `_one_line` 은 열 파일 모두 `_WHITESPACE.sub(" ", (text or "").strip())` 이다.
- de_be 의 designated(일회성) 항목도 같은 `_event()` 를 탄다(`rules/de_be/feed.py:169`).
- 다르게 만드는 피드는 없다.

### 0-3. 이미 있는 부재 단언

| 테스트 | 대상 | 단언 |
|---|---|---|
| `tests/test_de_nw_feed.py:465–470` `test_no_source_states_the_absence_of_amendment_as_a_verdict` | de_nw 전 항목 | `"무개정" not in source` |
| `tests/test_de_nw_feed.py:473–478` `test_no_source_points_to_the_header_comment` | de_nw 전 항목 | `"머리 주석"`·`"solar_holidays.yaml"` 없음 |
| `tests/test_de_he_feed.py:409–415` | de_he 전 항목 | `"머리 주석"`·`"solar_holidays.yaml"`·`"무개정"` 없음 |
| `tests/test_de_be_feed.py:467–474` | de_be 전 항목(designated 포함) | `"머리 주석"`·`"무개정"` 없음, `"rules/"`·`".yaml"` 없음 |

- 셋 모두 **자기 피드만** 본다.
- **반대 방향 단언이 둘 있다.** 데이터 변경과 함께 뒤집어야 한다(E-1).
  - `tests/test_de_feed.py:327` `assert "머리 주석" in source  # 해시 정의가 사는 곳을 가리킨다` — de 의 통일의 날.
  - `tests/test_de_bw_feed.py:474` `assert "rules/de" in source  # 미러라는 사실은 남긴다` — de_bw 의 통일의 날.
- C5 문면(`무개정`)을 **요구하는** 테스트는 없다. `tests/test_de_bw_feed.py` 는 `NEUFASSUNG_1995`·`READ_ON`·`ROOTS`·`"feiertage-api 2026 BW"` 를 요구하는데(:430–443), 어느 것도 `무개정` 문면에 걸리지 않는다. 분류할 수 없는 참조가 없어 멈추지 않았다.

---

## A. 목록

### A-0. 검색한 패턴(`classify.py`)
- **C1**: `rules/`, `docs/`, `tests/`, `\.py\b`, `\.yaml\b`, `\.md\b`
- **C2**: `머리 주석`, `이 파일`, `이 표`, `주석`
- **C3**: `de\.ics`, `\.ics\b`, `전례`, `미러`, `\bde_[a-z]{2}\b`(「와 같은」 앞 제외), `BW 의`, `de_bw 의`
- **C4**: `\btoken\b`, `\bkey\b`, `토큰`, `\bUID\b`
- **C5**: `무개정`, `변경 없음`, `개정 없음`, `개정이 없`, `유효`, `변동 없`, `unverändert`, `keine Änderung`, `gilt fort`, `그대로`
- **C6**: `SUMMARY`, `(erster|zweiter)_weihnachtstag`, `source_todo`, `verified`, `#\d+`, `Holiday_\d`, `참조`, `조사 보고`, `README`, `레포`, `세션`

대소문자 구분과 무시의 적중 건수는 모든 패턴에서 같다(`hits.tsv` 의 `cs_hits == ci_hits`, 차이 0 행). 108 항목 전문도 읽었다. 패턴 밖에서 찾은 것은 C6 에 적는다.

### A-1. 위반 행

- 한 항목이 여러 범주에 걸리면 한 행에 범주를 모두 적는다.
- 인용은 15 단어 이하로 줄였다.
- v = verified 다.

| # | 파일:줄(key) | key | v | 걸린 문면 | 범주 |
|---|---|---|---|---|---|
| 1 | `rules/de/solar_holidays.yaml:89` | tag_der_deutschen_einheit | T | 「— 정의는 이 파일 머리 주석, 2026-09-17 열람」 / 「스캔 판독 자구 일치, Art. 2 무개정」 | C2, C5 |
| 2 | `rules/de_bw/solar_holidays.yaml:139` | tag_der_deutschen_einheit | T | 「정의는 rules/de/solar_holidays.yaml 머리 주석, 2026-09-17 열람; rules/de 의 같은 항목을 미러」 | C1, C2, C3 |
| 3 | `rules/de_bw/easter_holidays.yaml:24` | karfreitag | T | 「§ 1 은 그 뒤 무개정(GBl. 2026 Nr. 79 까지)」 | C5 |
| 4 | `…/easter_holidays.yaml:39` | ostermontag | T | 같음 | C5 |
| 5 | `…/easter_holidays.yaml:54` | christi_himmelfahrt | T | 같음 | C5 |
| 6 | `…/easter_holidays.yaml:69` | pfingstmontag | T | 같음 | C5 |
| 7 | `…/easter_holidays.yaml:85` | fronleichnam | T | 같음 / 「key 는 de_by·de_he·de_nw 와 같은 fronleichnam」 | C5, C4 |
| 8 | `rules/de_bw/solar_holidays.yaml:87` | neujahr | T | 「§ 1 은 그 뒤 무개정(GBl. 2026 Nr. 79 까지)」 | C5 |
| 9 | `…:103` | heilige_drei_koenige | T | 같음 / 「key 는 de_by 와 같은 heilige_drei_koenige(신규 명명 없음)」 | C5, C4 |
| 10 | `…:122` | erster_mai | T | 같음 | C5 |
| 11 | `…:159` | allerheiligen | T | 같음 / 「key 는 de_by·de_nw 와 같은 allerheiligen」 | C5, C4 |
| 12 | `…:177` | erster_weihnachtstag | T | 같음 | C5 |
| 13 | `…:193` | zweiter_weihnachtstag | T | 같음 | C5 |
| 14 | `rules/de_by/solar_holidays.yaml:90` | tag_der_deutschen_einheit | T | 「연방 근거는 Einigungsvertrag Art. 2 Abs. 2 (rules/de)」 | C1 |
| 15 | `rules/de_hh/solar_holidays.yaml:115` | tag_der_deutschen_einheit | F | 「(de.ics 의 서술부 제외 전례)」 / 「Art. 2 Abs. 2 (rules/de)」 | C3, C1 |
| 16 | `rules/de_ni/solar_holidays.yaml:130` | tag_der_deutschen_einheit | F | 「'Tag der Deutschen Einheit'(de.ics 전례)」 / 「Art. 2 Abs. 2(rules/de)」 | C3, C1 |
| 17 | `rules/de_nw/solar_holidays.yaml:149` | erster_mai | T | 「'1. Mai'(de.ics 의 서술부 제외 전례)」 | C3 |
| 18 | `…:168` | tag_der_deutschen_einheit | T | 「서술부를 뺀 표기(de.ics 전례)」 / 「Art. 2 Abs. 2 (rules/de)」 | C3, C1 |
| 19 | `…:185` | allerheiligen | T | 「token 은 de_by 와 같은 allerheiligen(신규 명명 없음)」 | C4 |
| 20 | `rules/de_rp/solar_holidays.yaml:149` | tag_der_deutschen_einheit | F | 「연방 근거는 Einigungsvertrag Art. 2 Abs. 2 (rules/de)」 | C1 |
| 21 | `rules/de_rp/easter_holidays.yaml:86` | christi_himmelfahrt | F | 「(de.ics·de_bw 의 'Christi Himmelfahrt' 와 갈림은 조문 표기 차이)」 | C3 |
| 22 | `…/easter_holidays.yaml:149` | fronleichnam | F | 「(de_bw 의 'Fronleichnam' 과 갈림은 조문 표기 차이)」 / 「key 는 de_bw·de_by·de_nw 와 같은 fronleichnam」 | C3, C4 |
| 23 | `rules/de_rp/solar_holidays.yaml:183` | allerheiligen | F | 「(BW 의 'Allerheiligen' 과 갈림은 조문 표기 차이)」 / 「key 는 de_bw· de_by·de_nw 와 같은 allerheiligen」 | C3, C4 |
| 24 | `…:217` | erster_weihnachtstag | F | 「(뒷 날은 zweiter_weihnachtstag)」 | C6 |
| 25 | `…:251` | zweiter_weihnachtstag | F | 「(앞 날은 erster_weihnachtstag)」 | C6 |
| 26 | `rules/de_sh/solar_holidays.yaml:97` | tag_der_deutschen_einheit | T | 「(de.ics 의 서술부 제외 전례)」 / 「Art. 2 Abs. 2(rules/de)」 | C3, C1 |

- #2 의 「미러」 는 C3 에 넣었다. 다른 피드의 같은 항목을 가리키는 문장이라서다.
- #24·#25 는 다른 항목의 **내부 key 이름**을 구독자 문장에 쓴 것이라 C6 로 뒀다.

### A-2. 범주별·파일별 합계(행 수, 한 행이 여러 범주면 각각 센다)

| 범주 | 행 | 파일 |
|---|---|---|
| C1 레포 경로 | **7** | bw·by·hh·ni·nw·rp·sh (각 1, 전부 통일의 날) |
| C2 머리 주석 | **2** | de·bw (통일의 날) |
| C3 다른 피드 전례·비교 | **9** | bw 1(미러)·hh 1·ni 1·nw 2·rp 3·sh 1 |
| C4 key/token 부기 | **6** | bw 3·nw 1·rp 2 |
| C5 판정어 | **12** | de 1·bw 11 |
| C6 기타 | **2** | rp 2(내부 key 이름) |
| 위반 항목(중복 제거) | **26** | de 1·bw 12·by 1·hh 1·ni 1·nw 3·rp 6·sh 1 |

위반 없는 피드는 **de_be·de_he** 다(0 행).

**보류 목록(위반으로 세지 않음, 판단 요청)**
- **C5b 「X 개정 뒤에도/후에도 … 그대로」 23 행**
  - ni 7(verified F): 「2018 개정(Nds. GVBl. 2018 Nr. 7 S. 122) 후에도 Buchst. b 그대로」 형.
  - rp 9(F): 「1994-12-20 개정(GVBl. S. 474 …) 뒤에도 Nr. 2 그대로」 형.
  - sh 7(T): 「2018-03-21 개정(GVOBl. Schl.-H. 2018 Nr. 6 S. 69) 후에도 Nr. 2 그대로」 형.
  - 이름 붙은 **한 개정법**과의 대조를 적은 것이다. "이후 개정 없음" 이라는 판정은 아니다.
  - `그대로` 적중은 24 행인데, 나머지 1 행은 nw erster_mai 「1989 공고본의 인쇄 그대로다」(판정 아님)다.
- **C6 후보 — `SUMMARY` 라는 내부 필드명 24 행**
  - be 1·bw 2·hh 1·ni 3·nw 4·rp 11·sh 2 의 「SUMMARY 는 괄호 날짜를 뺀 …」 형이다.
  - 구독자에게 보이는 이벤트 제목을 iCalendar 필드명으로 부른 것이다. §6 규칙의 금지 목록에는 없다.

### A-3. §5 서술과 대조

| §5 (docs/holiday_19.md:231–235) | 측정 | 차이 |
|---|---|---|
| `rules/` 경로 — bw·by·hh·ni·nw·rp·sh | C1 7 행, 같은 7 파일 | 없음 |
| `de.ics` 전례 부기 — hh·ni·nw·rp·sh | `de.ics` 적중 6 행(hh 1·ni 1·nw 2·rp 1·sh 1), 같은 5 파일 | §5 는 행 수를 적지 않았다. 더해서 rp 에 `de.ics` 없이 다른 피드와 비교하는 행이 2 개(#22·#23 의 de_bw/BW 비교) 있다 |
| `de_by` token 부기 — bw·nw·rp | C4 6 행(bw 3·nw 1·rp 2), 같은 3 파일 | 문면의 대상은 `de_by` 만이 아니다(`de_he`·`de_nw`·`de_bw` 도 든다) |
| de·de_bw 의 통일의 날 「정의는 이 파일 머리 주석」(#110) | C2 2 행 | de_bw 는 「이 파일」 이 아니라 `rules/de/solar_holidays.yaml 머리 주석` 이다(C1 겸함) |
| BW 형 「무개정(GBl. … 까지)」 이 de·de_bw 에 12 건 | `무개정` 12 행 = de 1 + bw 11 | **BW 형(괄호 범위 있음)은 bw 11 건뿐이다.** de 1 건은 「Art. 2 무개정」 으로 범위가 없다 |
| HH 31. Oktober 에 URL·sha256 없음 | 확인(D-1) | 없음 |

- §5 에 없던 것 — C6 2 행(rp 의 내부 key 이름).

---

## B. C5 행 — 검색 사실이 이미 있는가

### B-1. de 통일의 날(#1) — **B-yes(범위 종류가 다름)**
- 현재: 「스캔 판독 자구 일치, Art. 2 무개정」. 범위가 없다.
- 기록:
  - `rules/de/solar_holidays.yaml:56–57` 「gesetze-im-internet 통합본(XML builddate 20260506)에서 Art. 2 는 개정 기록 없음.」
  - `docs/research/report_bgbl_1990_einigungsvertrag.md:358–364`(E3): `enbez="Art 2"` norm 에 `<standangabe>`·`<fussnoten>` 없음. 문서 수준 「Zuletzt angepasst durch § 11 V v. 15.8.2022 I 1401」. 「미확인: 2022 개정이 어느 조문을 건드렸는지는 보지 않았다(Art. 2 가 아닌 것만 확인)」.
- 범위는 **통합본의 개정 기록**(2026-05-06 빌드)이다. 관보 검색이 아니다.
- 이 기록이 받치는 대체 문면:
  - 「Art. 2 의 개정 기록은 찾지 못함(gesetze-im-internet 통합본, 2026-05-06 빌드)」
- [추론] BW·NW·HE 의 「찾지 못함(관보 …까지)」 과 범위의 종류가 달라 문면에서 그 차이가 드러나야 한다. 위 대체 문면은 그것을 괄호에 적는다.

### B-2. de_bw 11 행(#3–#13) — **B-partial**
- 현재 주장: 「§ 1 은 그 뒤[= 1995-03-23 개정 뒤] 무개정(GBl. 2026 Nr. 79 까지)」. 1995 → 2026 Nr. 79 연속 구간이다.
- 기록:
  - `rules/de_bw/solar_holidays.yaml:32–35`: 「이후: 2014-11-25 (GBl. 2014 Nr. 21 S. 548) § 1a 한시 신설…, 2015-12-01 (GBl. 2015 Nr. 22 S. 1034) §§ 8·10·11·13 — 둘 다 § 1 무관. 1995 Nr. 1~2013 전 호·2016~2023 전 호(Landtag 아카이브)·2024~ 전자 관보 GBl. 2026 Nr. 79 (08.09.2026) 까지 § 1 개정 없음. 체인 전문은 /tmp/report_bw_gesetz_chain.md.」
  - `rules/de_bw/__init__.py:10–12`: 같은 내용이다(「1995~2013 전 호·2016~2023 전 호·2024~ 전자 관보 GBl. 2026 Nr. 79 까지 실측」).
  - `docs/holiday_15.md` §3(「BW — Landtag 사이트맵이 전수 목록」): 사이트맵에 GBl PDF 2,101 건, 텍스트층 없는 호는 이미지 육안(1994 Nr.25–29·2005 Nr.1·2007 Nr.21), 2024~ 는 전자 관보 전문검색.
  - **체인 전문 `/tmp/report_bw_gesetz_chain.md` 는 없다.** `ls` 결과 없음이고, `docs/holiday_15.md:7–12` 가 「다음 세션에서는 받을 수 없다」 고 적는다. `docs/research/` 에도 없다.
- 차이: "전 호" 로 적힌 구간은 1995–2013·2016–2023·2024–2026 Nr. 79 다. **2014·2015 는 개정법 두 건이 § 1 무관이라는 것만 적혀 있고, 그 두 해의 전 호를 봤다는 서술은 없다.**
  - [추론] 두 개정법을 찾은 해라서 따로 적었을 수 있다. 원 보고가 없어 확인할 수 없다.
- 기록 범위에 맞춘 대체 문면(기록된 것만):
  - 「§ 1 의 그 뒤 개정은 찾지 못함(GBl. 1995–2013·2016–2023 전 호, 2024–2026 Nr. 79 전자 관보; 2014·2015 의 FTG 개정 두 건은 § 1 무관)」
- 현재 주장의 전 구간(1995 → 2026 Nr. 79 연속)을 "찾지 못함" 으로 쓰려면 2014·2015 GBl. 전 호 검색이 새로 필요하다. 같은 Landtag 사이트맵 경로다.

---

## C. C1–C4·C6 대체 문면

- 모두 **떼기**다. 뗀 포인터의 내용이 있는 곳을 함께 적는다.
- 줄 번호는 `e5a3e21` 기준이다.

| # | 대체(떼거나 바꾸는 부분 → 새 문면) | 뗀 내용이 있는 곳 | 유일한 사실을 잃는가 |
|---|---|---|---|
| 14 by·20 rp | 「Einigungsvertrag Art. 2 Abs. 2 (rules/de)」 → 「Einigungsvertrag Art. 2 Abs. 2」 (HE 전례: `rules/de_he/solar_holidays.yaml:152` 「연방 근거는 Einigungsvertrag Art. 2 Abs. 2.」) | rp: 머리 주석 `rules/de_rp/solar_holidays.yaml:13–14`. by: 머리 주석에 Einigungsvertrag 언급 **없음**(grep) | 아니다 — 조약 조문명은 source 에 남는다 |
| 15 hh | 「(de.ics 의 서술부 제외 전례)」 삭제, 「(rules/de)」 삭제 | `rules/de_hh/solar_holidays.yaml:35–37`(name 절). Einigungsvertrag 는 hh 머리 주석에 없음 | 아니다 |
| 16 ni | 「(de.ics 전례)」 삭제, 「(rules/de)」 삭제 | `rules/de_ni/solar_holidays.yaml:10–11, 68–69`, `__init__.py:17–18` | 아니다 |
| 17 nw | 「(de.ics 의 서술부 제외 전례)」 삭제 | `rules/de_nw/solar_holidays.yaml:112–113`, `__init__.py:22` | 아니다 |
| 18 nw | 「(de.ics 전례)」 삭제, 「(rules/de)」 삭제 | 같음. Einigungsvertrag 는 nw 머리 주석에 없음 | 아니다 |
| 26 sh | 「(de.ics 의 서술부 제외 전례)」 삭제, 「(rules/de)」 삭제 | `rules/de_sh/solar_holidays.yaml:44`, `__init__.py:21` | 아니다 |
| 21 rp | 「(de.ics·de_bw 의 'Christi Himmelfahrt' 와 갈림은 조문 표기 차이)」 삭제 | `rules/de_rp/easter_holidays.yaml:12–14` | 아니다 |
| 22 rp | 「(de_bw 의 'Fronleichnam' 과 갈림은 조문 표기 차이)」·「key 는 de_bw·de_by·de_nw 와 같은 fronleichnam.」 삭제 | `rules/de_rp/easter_holidays.yaml:13–14`, `rules/de_rp/__init__.py:22–23` | 아니다 |
| 23 rp | 「(BW 의 'Allerheiligen' 과 갈림은 조문 표기 차이)」·「key 는 … 같은 allerheiligen.」 삭제 | `rules/de_rp/solar_holidays.yaml:64, 70–72`, `__init__.py:22–23` | 아니다 |
| 7 bw | 「key 는 de_by·de_he·de_nw 와 같은 fronleichnam.」 삭제 | `rules/de_bw/__init__.py:18–19` | 아니다(easter 머리 주석에는 없고 `__init__` 에 있다) |
| 9 bw | 「key 는 de_by 와 같은 heilige_drei_koenige(신규 명명 없음).」 삭제 | `rules/de_bw/solar_holidays.yaml:58–61` | 아니다 |
| 11 bw | 「key 는 de_by·de_nw 와 같은 allerheiligen.」 삭제 | `rules/de_bw/__init__.py:18–19` | 아니다 |
| 19 nw | 「token 은 de_by 와 같은 allerheiligen(신규 명명 없음).」 삭제 | `rules/de_nw/solar_holidays.yaml:104–107`, `__init__.py:17–18` | 아니다 |
| 24·25 rp | 「(뒷 날은 zweiter_weihnachtstag)」 → 「(뒷 날 26. Dezember 는 별도 항목)」, 「(앞 날은 erster_weihnachtstag)」 → 「(앞 날 25. Dezember 는 별도 항목)」 | `rules/de_rp/solar_holidays.yaml:64–65` | 아니다 |
| 1 de | 「— 정의는 이 파일 머리 주석, 2026-09-17 열람」 → 「— PDF 6 쪽(S. 890)의 이미지 객체를 빈 비밀번호로 복호화한 뒤 필터를 풀지 않은 스트림 바이트, 2026-09-17 열람」 | 전체 정의(경로 `/I5`→`/Im0`, 객체 35 0, 19,643 B, 재현 명령)는 `rules/de/solar_holidays.yaml:44–55` | 아니다 — 머리 주석이 남는다. [추론] 이 경우는 떼기만 하면 해시의 뜻이 구독자 문장에서 사라지므로 짧은 정의를 넣는 쪽을 제안한다 |
| 2 bw | 「— 정의는 rules/de/solar_holidays.yaml 머리 주석, 2026-09-17 열람; rules/de 의 같은 항목을 미러」 → #1 과 같은 짧은 정의 + 「2026-09-17 열람」 | 정의: `rules/de/solar_holidays.yaml:44–55`. 미러라는 사실: `rules/de_bw/solar_holidays.yaml:40–41, 72`, `__init__.py:16–17` | 아니다 |

**C 에 딸린 발견**
- 머리 주석·`__init__`·테스트 docstring 이 가리키는 `/tmp/report_*.md` 가 레포에 없다. 확인한 것: `/tmp/report_bw_gesetz_chain.md`, `/tmp/report_bundesweit.md`, `/tmp/report_de_laender.md`, `/tmp/report_hh_gesetz_chain.md`.
  - source 문면은 아니라 이번 범주 밖이다.
  - B-2 가 partial 로 떨어진 직접 원인이다(원 보고가 사라짐).
- `rules/de_hh/solar_holidays.yaml:133` — tag_der_deutschen_einheit 의 **source_todo** 에 「2026 Nr. 26 (28.08.2026) 까지 무개정」 이 있다.
  - source_todo 는 피드에 나가지 않는다. 머리 주석 `:69` 가 그렇게 적고, DESCRIPTION 식(`rules/de_hh/feed.py:144`)은 `source` 만 읽는다. 이번 규칙의 대상 밖이다. 기록만 한다.

---

## D. HH 31. Oktober

### D-1. 현재 문면
- `rules/de_hh/solar_holidays.yaml:135–145`, key `reformationstag`, verified **true**.
  - source: 「Feiertagsgesetz(HH) § 1 Nr. 8 '31. Oktober' (통칭 Reformationstag) — Fünftes Gesetz zur Änderung des Feiertagsgesetzes vom 12.03.2018, HmbGVBl. 2018 Nr. 9 S. 63 (20.03.2018 공포, luewu.de PDF 2026-09-07 열람). 날짜는 feiertage-api 2026 HH 대조 일치」
- 머리 주석 `:47–53`: 「Nr. 8 "31. Oktober" 만 true … 공포 관보 원문(HmbGVBl. 2018 Nr. 9 S. 63, Fünftes Gesetz … vom 12.03.2018, 20.03.2018 공포)을 luewu.de 의 PDF 사본으로 2026-09-07 에 읽었다. Einziger Paragraph: "Hinter Nummer 7 wird folgende neue Nummer 8 eingefügt: „8. 31. Oktober,“. …"」
- 개정 체인 `:55–64`: 「luewu 1995–2026 Nr. 26 실측」, § 1 개정은 2018-03-12 하나.
- URL·sha256 은 source 에도 머리 주석에도 없다.

### D-2. 공포법
레포가 이미 적은 것:
- Fünftes Gesetz zur Änderung des Feiertagsgesetzes vom 12.03.2018
- HmbGVBl. 2018 Nr. 9 S. 63
- 20.03.2018 공포
- Einziger Paragraph 의 자구

D-3 에서 **새로** 확인한 것(레포에 없던 값):
- 그 호는 S. 61–64(4 쪽)다.
- 개정 대상 표기는 「§ 1 des Feiertagsgesetzes vom 16. Oktober 1953 (Sammlung des bereinigten hamburgischen Landesrechts I 113-a), zuletzt geändert am 12. Dezember 2017 (HmbGVBl. S. 386, 388)」 이다.
- 개정 지시는 두 번호다: 「1. Hinter Nummer 7 …」 「2. Die bisherigen Nummern 8 und 9 werden Nummern 9 und 10.」
- 발행처 표기는 4 쪽 「Herausgegeben von der Justizbehörde … Druck, Verlag und Ausgabestelle Lütcke & Wulff」 다.

### D-3. 온라인 입수(`hh_fetch.log`)
UA 는 `holidays.lunalism.com research (contact: repo issues)` 이고, 요청 간격은 3–10 초다.

| 시각(UTC) | URL | 응답 |
|---|---|---|
| 07:23:28 | `https://www.luewu.de/gvbl/` | 200, `/gesetz-und-verordnungsblatt/` 로 이동, `/gvbl/2018` 링크 있음 |
| 07:23:34 | `https://www.luewu.de/gvbl/2018/` | 200, 호별 링크 목록 |
| (같은 목록) | `…/gvbl/ausgabe-nr-9-vom-20-03-2018-seiten-61-64-groesse-458-kb/` | 200, 「Nr. 9 vom 20.03.2018, Seiten 61 – 64, Größe: 458 KB」, PDF 링크 1 개 |
| 두 번 | `https://www.luewu.de/wp-content/uploads/2025/08/GVBL_HH_2018-9.pdf` | 200 `application/pdf` 457,762 B, 두 번 다 같음 |
| 참고 | `https://suche.transparenz.hamburg.de/?q=HmbGVBl.%202018%20Nr.%209` | 200 HTML, 정적 응답에 결과 목록 없음(스크립트로 채움). 이 줄은 여기서 멈췄다 |

PDF:
- **sha256 `025be364db842223fc6b8356da91adc3b4e7a39f52410103c317273af66a4aa8`**. 두 번 받은 값이 같다 → **결정적이다.** 이미지 스트림 해시는 필요 없다.
- 응답 헤더: `last-modified: Tue, 05 Aug 2025 07:32:31 GMT`, `etag: "6fc22-63b993a18c1c0"`(두 번 같음).
- 4 쪽, 텍스트층 있음(쪽당 1,619–3,238 자). 메타 `creationDate 2018-03-14`, `Adobe InDesign CC 2017`.
- **PDF 3 쪽 = S. 63**(쪽 머리 「Dienstag, den 20. März 2018 63 HmbGVBl. Nr. 9」).
  - 인용: 「Hinter Nummer 7 wird folgende neue Nummer 8 eingefügt: „8. 31. Oktober,“」.
- PDF 1 쪽 목차: 「12. 3. 2018 Fünftes Gesetz zur Änderung des Feiertagsgesetzes … 63」.
- 열람일: **2026-09-30**.
- [추론] 업로드 경로(`/2025/08/`)와 `last-modified` 가 2025-08 이다. 2026-09-07 의 열람도 이 파일이었을 가능성이 높다. 다만 그때 URL·해시가 기록되지 않아 같은 파일인지 확인할 수 없다.

### D-4. 호별 서지 형식과 HH 초안
- 비교 전례는 `rules/de_ni/solar_holidays.yaml:157` (reformationstag)다. 형식: 「… Art. 1 Nr. 1 (Buchst. h 삽입, …), Nds. GVBl. 2018 Nr. 7 S. 122 (28.06.2018 공포, 29.06.2018 시행; 니더작센 포털 PDF <URL> sha256 <hash>, 2026-09-09 열람, 재수령 대조 일치; …)」.
- 같은 꼴의 SH 는 `rules/de_sh/solar_holidays.yaml:114` 다.

초안(이번에 측정한 사실만):

> Feiertagsgesetz(HH) § 1 Nr. 8 '31. Oktober' (통칭 Reformationstag) — Fünftes Gesetz zur Änderung des Feiertagsgesetzes vom 12.03.2018 Einziger Paragraph Nr. 1 (Nr. 7 뒤에 Nr. 8 삽입)·Nr. 2 (구 Nr. 8·9 → 9·10), HmbGVBl. 2018 Nr. 9 S. 63 (20.03.2018 공포; 관보 발행처 Lütcke & Wulff 의 호 PDF https://www.luewu.de/wp-content/uploads/2025/08/GVBL_HH_2018-9.pdf sha256 025be364db842223fc6b8356da91adc3b4e7a39f52410103c317273af66a4aa8, 2026-09-30 열람, 재수령 대조 일치). 날짜는 feiertage-api 2026 HH 대조 일치

- 시행일은 적지 않았다. 이 호의 Einziger Paragraph 에 시행 조항이 없고, 이번에 따로 확인하지 않았다.
- 기존 테스트(`tests/test_de_hh_feed.py:340–360`)가 요구하는 문자열을 이 초안은 모두 담는다.
  - 요구: `§ 1 Nr. 8 '31. Oktober'`, `Fünftes Gesetz zur Änderung des Feiertagsgesetzes`, `12.03.2018`, `HmbGVBl. 2018 Nr. 9 S. 63`, `20.03.2018`, `feiertage-api 2026 HH`.
  - `Drucksache` 는 초안에 없다(테스트는 그 부재를 요구한다).
  - [추론] 문자열 포함만 대조했다. 테스트를 돌려 보지는 않았다.
- 선택 — 머리 주석 `:55–64`(「luewu 1995–2026 Nr. 26 실측」)를 근거로 「§ 1 의 2018 이후 개정은 찾지 못함(HmbGVBl. 2026 Nr. 26 까지, luewu 호별 목록)」 을 더할 수 있다(NW·HE 형). 판단 요청 5.

---

## E. 테스트와 발행물 영향(편집 없음)

### E-1. 테스트
- **새 안전망(최소)** — 독일 규칙 YAML 전부(`rules/de/`·`rules/de_*/` 의 `*.yaml`, designated 포함)를 돌며 source 에 아래가 **없음**을 단언한다.
  - C1 `rules/`·`.yaml`·`.py`
  - C2 `머리 주석`·`이 파일`
  - C3 `.ics`·`전례`·`미러`
  - C4 `key 는`·`token 은`
  - C5 `무개정`
  - C6 `_weihnachtstag`
  - 자리는 `tests/test_de_scope.py` 의 `STATE_FEEDS` 스캔(`:53–71`, rules/de_* 전부를 이끈다) + de 1 벌이다. 또는 새 파일(예: `tests/test_de_source_selfcontained.py`)이다.
  - [추론] 한 곳에 두면 nw·he·be 의 개별 단언(0-3 표)은 중복이 된다. 지울지는 별도 판단이다.
- **데이터와 함께 뒤집는 것**:
  - `tests/test_de_feed.py:327`(「머리 주석」 in)과 그 docstring `:320`
  - `tests/test_de_bw_feed.py:474`(「rules/de」 in)와 docstring `:446`·`:463`
  - [추론] 새 안전망이 먼저 들어가면 이 둘과 충돌한다. 같은 커밋에서 뒤집거나, 안전망을 "현재 위반 목록 허용" 형태로 먼저 넣어야 한다.
- **순서.** AGENTS.md 「안전망은 그것이 지킬 변경보다 **먼저** 머지한다」.
  - 현재 데이터로는 새 단언이 26 항목에서 실패한다.
  - 길은 둘이다.
    - (a) 안전망을 **알려진 위반 목록(26 항목 key)을 허용**하는 형태로 먼저 머지한다. 데이터 PR 이 목록을 비우고 허용을 지운다.
    - (b) 한 PR 안에서 안전망 커밋을 데이터 커밋보다 앞에 둔다(중간 커밋은 빨갛다).
  - 판단 요청 6.
- **HH 서지**를 위한 단언: `tests/test_de_hh_feed.py:340–360` 에 URL·`sha256 <64 hex>`·`재수령 대조 일치` 포함을 더한다(NW·HE·BE 의 「서지를 스스로 든다」 테스트 꼴 — `test_de_nw_feed.py:415`·`test_de_he_feed.py:378`·`test_de_be_feed.py:435`).

### E-2. 발행물
UID = `{YYYYMMDD}-{token}`, token = key(주 피드는 `<feed>-<key>`). key 를 바꾸지 않으므로 **UID 불변**이다.

| 피드 | 전체 이벤트 | DESCRIPTION 이 바뀌는 이벤트 | 항목 |
|---|---|---|---|
| de | 108 | 12 | tag_der_deutschen_einheit |
| de_bw | 144 | **144** | 12 항목 전부 |
| de_by | 144 | 12 | tag_der_deutschen_einheit |
| de_hh | 120 | 24 | tag_der_deutschen_einheit, reformationstag(D) |
| de_ni | 120 | 12 | tag_der_deutschen_einheit |
| de_nw | 132 | 36 | tag_der_deutschen_einheit, erster_mai, allerheiligen |
| de_rp | 132 | 72 | tag_der_deutschen_einheit, christi_himmelfahrt, fronleichnam, allerheiligen, erster·zweiter_weihnachtstag |
| de_sh | 120 | 12 | tag_der_deutschen_einheit |
| de_be·de_he | – | 0 | – |

- 합계는 **8 피드 324 이벤트**(27 항목 × 발행 연도 12, 2020–2031)다.
- C5b(23 행)·SUMMARY(24 행)를 함께 고치면 더 늘어난다. 세지 않았다.

**SEQUENCE**
- `DESIGN.md:123–127`(id `seq-내용변경-정책`): 「지금은 DTSTART/DTEND 가 바뀔 때만 SEQUENCE 를 올린다. SUMMARY·DESCRIPTION·STATUS 변경으로는 올리지 않는다.」
- 이번 변경은 DESCRIPTION 만 바꾸므로 **SEQUENCE 는 바뀌면 안 되고 바뀌지 않는다.**
- 다만 이 항목은 DESIGN.md 「미해결」 아래(`:98` 이하)에 있다. 「실제 구독 테스트 후 재검토한다」(`:137–139`) — 현재 동작이 확정된 결론은 아니라는 뜻이다.
- UID 규칙 쪽은 `DESIGN.md:100–106`(id `seq-증가-도달불가`)이 날짜가 UID 에 들어 있음을 적는다.

---

## 판단 요청 — 9 건

1. **BW 11 행(B-partial).** 둘 중 하나를 고른다.
   - (a) 기록된 범위만 적는 문면(B-2 의 대체안, 2014·2015 는 「개정 두 건 § 1 무관」)으로 바꾼다.
   - (b) 2014·2015 GBl. 전 호 검색을 먼저 새로 하고 연속 구간 문면으로 바꾼다.
2. **de 통일의 날(B-yes, 통합본 범위).** 관보 검색이 아닌 통합본 개정 기록을 범위로 드는 문면 「Art. 2 의 개정 기록은 찾지 못함(gesetze-im-internet 통합본, 2026-05-06 빌드)」 을 받아들이는가.
3. **C5b 23 행**(ni·rp·sh 「X 개정 뒤에도 … 그대로」). 한 개정법과의 대조라 판정어로 보지 않았다. 그대로 둘지, 「… 가 바꾸지 않았다」 류로 통일할지 정한다.
4. **SUMMARY 필드명 24 행.** 구독자 문장에 내부 필드명이 남아 있다. 이번 PR 범위에 넣을지 정한다.
5. **HH 초안.**
   - 열람일을 이번 측정일(2026-09-30)로 바꾸는 것을 받아들이는가. 2026-09-07 열람본은 URL·해시가 없어 같은 파일인지 알 수 없다.
   - 「2018 이후 개정 찾지 못함(HmbGVBl. 2026 Nr. 26 까지)」 을 더할지 정한다.
6. **안전망 순서.** (a) 허용 목록을 가진 안전망 선행 PR 과 (b) 한 PR 안 커밋 순서 중 하나를 고른다. 그리고 nw·he·be 의 개별 단언을 새 공통 단언으로 합칠지 정한다.
7. **C1 대체.**
   - HE 전례대로 「Einigungsvertrag Art. 2 Abs. 2」 만 남길지, 「(BGBl. 1990 II Nr. 35 S. 890)」 을 붙일지 정한다.
   - de·bw 통일의 날의 짧은 해시 정의 문면(C 표 #1·#2)을 정한다.
8. **PR 나누기.** Holiday_19 §5 큐는 「source 자기완결성 정리 + HH 31. Oktober 서지 보강」 을 한 PR 로 묶는다(`docs/holiday_19.md:256–257`). 영향은 8 피드 324 이벤트다. 판단 요청 6 의 (a) 를 고르면 안전망 PR 이 앞에 하나 더 선다.
9. **사라진 `/tmp` 보고 참조.** 머리 주석·`__init__`·테스트 docstring 의 `/tmp/report_*.md` 를 이번 PR 에서 손볼지, 별도로 둘지 정한다(source 밖이라 이번 범주에 넣지 않았다).
