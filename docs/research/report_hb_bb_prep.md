# HB(브레멘)·BB(브란덴부르크) 주 피드 구현 준비 조사

- 측정 시점: 2026-09-30. `origin/main` = `be1c45fa8667fa60e71678a2e95dc3687ddf1388`.
- `git fetch --prune` 출력은 없었다(prune 0).
- 범위: 조사만 했다. 레포 변경·브랜치·PR 없음. 병렬화하지 않았다(scratch 디렉터리 하나).
- 재현 기록은 `~/holidays-reports/report_hb_bb_prep/` 에 있다.
  - `fetch.sh`·`fetch.log`: 요청 26 건. 200 이 25 건이고 500 이 1 건(HB 현행판 PDF)이다. 로그에는 sha256 두 줄도 함께 적혀 있다.
  - `hb_index_scan.txt`
  - `hb_2018_63_text.txt`: 관보 텍스트층 전사
  - `drafts/`
- 받은 관보 PDF 는 폴더에 두지 않았다. 판독 뒤 scratch 째 지웠다(`docs/research/README.md` 「넣지 않는 것」).
- 표기: 명령 출력·원문에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- 전제 보고 `report_batch2_survey.md` 는 2차 자료로만 썼다. 아래 값은 전부 이번에 다시 받은 것이다.

---

## 0. 사전 확인

### 0-1. sha
- `be1c45f` 이다. 멈춤 조건에 해당하지 않는다.

### 0-2. 주 피드 추가 지점 — 구현 체크리스트

가장 최근의 주 피드 추가는 **#63(de_rp, `292d86f`)** 이다. 그 diff 는 14 파일이다: `publish.yml`·`DESIGN.md`·`feeds/de_rp.ics`·`rules/de_rp/{__init__,feed,status}.py`·두 YAML·`rules/status.py`·`status.json`·`tests/test_de_be_feed.py`·`tests/test_de_rp_feed.py`·`tests/test_de_scope.py`·`tests/test_published_feed.py`.

그 뒤 랜딩 생성·스캔 기반 테스트가 들어와 지점이 바뀌었다.
- 현재의 정본 절차는 `docs/operations.md:75–150` 「피드 추가 — 손대는 순서와 빠뜨리면 무엇이 잡는지」 다.
- 아래 표는 그 절차와 `git grep de_rp`·`git grep -i 'rheinland\|라인란트'` 결과를 맞춘 것이다. 대소문자 구분·무시 결과는 같다.

| # | 자리 | 현재 위치 | 빠뜨리면 | 비고 |
|---|---|---|---|---|
| 1 | `rules/de_xx/` — `__init__.py`·`feed.py`(`__main__`, `TOKEN_PREFIX`, `LAND_NAME`, `LAND_NAME_DE`, `CALNAME`)·`status.py`·`solar_holidays.yaml`·`easter_holidays.yaml` | 전례 `rules/de_rp/` | `test_feed_set.py`(operations.md 항목 1) | feed.py 는 de_rp 복제 + 접두사·주명 |
| 2 | `.github/workflows/publish.yml:71` `FEEDS` | 한 줄 | `test_every_rules_package_is_in_feeds_and_vice_versa` | – |
| 3 | `rules/status.py:58`(import)·`:89`(등록) | 두 줄 | `test_the_status_registry_matches_feeds` | – |
| 4 | `landing/layout.yaml` | 손댈 것 없음 — `prefix: de_` 규칙 | – | operations.md 항목 4 |
| 5 | `landing/locales/*` | 손댈 것 없음 — 주 피드는 `state_feed` 틀 | – | 항목 5 는 주 피드가 아닐 때만 |
| 6 | `LAND_NAME_DE` (feed.py) | 표기 근거 `rules/de/feed.py:75–90`(기본법 전문 16 주, `:82` 에 Brandenburg·Bremen 포함) | render 가 AttributeError | – |
| 7 | `feeds/de_xx.ics` 생성·커밋 | `uv run python -m rules.de_xx.feed feeds/de_xx.ics` | CI `test_feed_set`·`test_landing`·`test_readme` | – |
| 8 | `status.json` 재생성·커밋 | `uv run python -m rules.status status.json` | CI `test_landing` | – |
| 9 | `index.html`·`en/`·`ja/` 재생성·커밋 | `uv run python -m landing.render` | CI `test_landing_render` 언어마다 | – |
| 10 | `tests/test_landing.py:208–218` `LAND_NAMES_DE` | 표에 한 줄 | KeyError | – |
| 11 | `README.md:18–32` 구독 표(주 행은 `:21–29`) | 행 추가(주 순서는 코드순) | `test_readme` | – |
| 12 | `tests/test_de_scope.py:75–85` `LAND_NAMES` | 표에 한 줄 | KeyError | – |
| 13 | `README.md:139–141` 「구조」 절의 주 열거(「아홉(de_be, …)」) | 문장 수정 | 없음(사람 몫) | – |
| 14 | `tests/test_published_feed.py:294–295` 잠정 0 리터럴 목록 | 코드 추가 | 없음(사람 몫) | – |
| **15** | **`tests/test_de_be_feed.py:227–242` `STATE_FEEDS` dict(교집합 == 전국 9)** | import 한 줄 + dict 한 줄 | **없음 — operations.md 에 없다** | #63 diff 에는 있었다(`test_de_be_feed.py` +6). 손으로 적는 목록이라 새 주가 교집합 검사에서 조용히 빠진다 [추론] |
| 16 | `tests/test_de_<xx>_feed.py` 새 파일 | 전례 `tests/test_de_rp_feed.py` | – | feiertage-api 대조·상위집합·UID 접두사·재현 |
| 17 | `README.md:74–77`(「Fronleichnam 은 다섯 주 피드…」) | HB·BB 에 Fronleichnam 이 없어 손댈 것 없음 [추론] | – | – |

- 자동 편입(손댈 것 없음, 확인함): `tests/test_de_source_selfcontained.py` 의 `rules/` 스캔, `tests/test_de_scope.py:57–62` `STATE_CODES` 스캔, `tests/test_published_feed.py:135–137` `FEED_CODES` 스캔(재현·UID 배타·status 서술).
- `DESIGN.md:150` 은 목록 대신 「`publish.yml` 의 `FEEDS`」 를 가리키므로 #63 때와 달리 고칠 곳이 아니다.

### 0-3. UID·token 형식
- `core/ics.py:183` — `f"{day:%Y%m%d}-{event.token}@{UID_DOMAIN}"`, `UID_DOMAIN = "holidays.lunalism.com"`(`:51`).
- 주 피드 token 은 `TOKEN_PREFIX + entry["key"]` 다(`rules/de_rp/feed.py:68, 150`).
- 따라서 예시는 `20260405-de_bb-ostersonntag@holidays.lunalism.com` 이다. 기대와 일치한다.

---

## HB — 브레멘

### HB-1. 현행 조문

**공식 현행 통합본 — 여전히 못 받았다.**
- `…/detail.php?gsid=bremen2014_tp.c.296390.de&template=00_html_to_pdf_d` → **500**, 본문 「db-connection failed」(09:46:44Z).
- `template` 없이 요청하면 200 이지만 본문은 「Sorry. no id, no template, no output.」(37 B)이다.
- 이전 조사의 두 번까지 합해 세 번째 500 이다. 차단 신호(403/429/인증)는 아니다.

**대체 경로 — Brem.GBl. 제목 검색(`hb_index_scan.txt`).**
- 공식 관보 포털 `gesetzblatt.bremen.de` 는 정적 HTML 이고 연간 목록 PDF 를 둔다.
- 2020–2025 연간 목록 여섯과 2026 목록 페이지(97 호 전부)의 제목에서 `Feiertag|Gedenk|113-c` 를 찾았다.
  - 적중은 1 건뿐이다: 2020 「Gesetz zur staatlichen Anerkennung des Tags der Befreiung … als Gedenktag (S. 52)」, 13.03.2020. 이것은 기념일이지 공휴일이 아니다.
  - 2021–2026 은 0 건이다.
- 2025 판이 생긴 까닭을 찾았다.
  - 구판 PDF(145882, 이번에 다시 받음, 200, 295,467 B)의 머리 메타가 「Zuletzt geändert durch: … Geschäftsverteilung des Senats vom 02.09.2025 (Brem.GBl. S. 674)」 라고 적는다.
  - 그 호 2025 Nr. 98(S. 674–724)은 「Bekanntmachung über die Änderung von Zuständigkeiten」(§ 7 Rechtsbereinigungsgesetz) 이다. 이 법을 든 자리는 「Gesetz über die Sonn-, Gedenk- und Feiertage … § 11」 하나다 — 관할 조항이지 § 2 가 아니다.
  - 판 교체일과 같은 날의 2025 Nr. 76(30.06.2025, 「Änderung der Geschäftsverteilung im Senat」)에는 Feiertag·Sonn·Gedenk·113-c 가 없다.
- [추론] 2025 판들은 관할 공고에 따른 부수 갱신이고 § 2 Abs. 1 은 2020 판 그대로다.
  - 근거는 셋이다: (1) 2020–2026 관보 제목에 § 2 를 바꿀 법이 없다. (2) 알려진 2025 변경이 § 11 관할뿐이다. (3) feiertage-api 2026 HB 10 건이 2020 판 목록과 일치한다.
  - 한계: 제목 검색이라 다른 제목의 조항법(Artikelgesetz)이 § 2 를 건드렸다면 놓친다.

**현재 효력 있는 § 2 Abs. 1 로 삼는 것:** Transparenzportal 2020-03-14 판(145882) § 2 Abs. 1 — 「Staatlich anerkannte Feiertage sind:」 a)–j). 출처는 공식 포털의 구판(2차)과 위 관보 검색이다. **공식 현행판 자체는 아니다.**

### HB-2. 항목 (주 전역 10, 전부 기존 규칙 유형)

| Buchst. | 조문 | SUMMARY(name) | scope | key | 규칙 |
|---|---|---|---|---|---|
| a | 「der Neujahrstag」 | Neujahrstag | bundesweit | neujahr | 1. 1. |
| b | 「der Karfreitag」 | Karfreitag | bundesweit | karfreitag | 부활절 −2 |
| c | 「der Ostermontag」 | Ostermontag | bundesweit | ostermontag | +1 |
| d | 「der 1. Mai」 | 1. Mai | bundesweit | erster_mai | 5. 1. |
| e | 「der Himmelfahrtstag」 | Himmelfahrtstag | bundesweit | christi_himmelfahrt | +39 |
| f | 「der Pfingstmontag」 | Pfingstmontag | bundesweit | pfingstmontag | +50 |
| g | 「der 3. Oktober - Tag der deutschen Einheit -」 | Tag der deutschen Einheit | bundesweit | tag_der_deutschen_einheit | 10. 3. |
| h | 「der 1. Weihnachtstag」 | 1. Weihnachtstag | bundesweit | erster_weihnachtstag | 12. 25. |
| i | 「der 2. Weihnachtstag」 | 2. Weihnachtstag | bundesweit | zweiter_weihnachtstag | 12. 26. |
| j | 「der Reformationstag」 | Reformationstag | land | reformationstag | 10. 31. |

- SUMMARY 규칙은 레포의 「--- name ---」 절을 따랐다(`rules/de_nw/solar_holidays.yaml` 등): 조문 표기에서 정관사·서술부·괄호를 뺀다.
- g 는 SH 전례(「3. Oktober - Tag der Deutschen Einheit -」 → 날짜부·대시 제거)를 따랐다. 소문자 d 는 de_be 전례를 따랐다(`rules/de_be/solar_holidays.yaml:28, 104` 「"Tag der deutschen Einheit" 의 소문자 d 도 조문 그대로다」).
- 범위 밖(주 전역 공휴일 아님):
  - § 8 종교 축일(2013 개정으로 이슬람 축일 추가 — 2013 Nr. 33 에서 확인)
  - 2020 Gedenktag 법의 8. Mai(기념일)
- 2026 날짜 10 건이 feiertage-api 2026 HB(hinweis 공란 10)와 같다(`drafts/safety_net_check.txt`).

### HB-3. 공포본 — 온라인으로 닿는 것

| 호 | 내용(판독) | 판정 |
|---|---|---|
| Brem.GBl. 2018 Nr. 63 S. 302 | 「Gesetz zur Änderung des Gesetzes über die Sonn- und Feiertage Vom 26. Juni 2018」 Art. 1 Nr. 1 「§ 2 Absatz 1j wird wie folgt neu gefasst: der Reformationstag.」, Art. 2 「am Tag nach seiner Verkündung」(28.06.2018 공포) | **j 의 현행 자구를 공포본으로 읽음 → verified true 후보.** URL `https://www.gesetzblatt.bremen.de/fastmedia/218/2018_06_28_GBl_Nr_0063_signed.pdf`, 241,672 B, 1 쪽, **sha256 `e0a706281f932bd4445366e2e546b0de894f0fcfc1e5ccb1793bdcb8665e23bf` — 두 번(10 초 간격) 같음 → 결정적**, 2026-09-30 열람. 개정 대상 표기 「vom 12. November 1954 (Brem.GBl. S. 115), zuletzt geändert am 21. Mai 2013 (Brem.GBl. S. 231)」 |
| Brem.GBl. 2013 Nr. 33 S. 231 | 「In Buchstabe i wird nach dem Wort „Weihnachtstag" der Punkt durch ein Komma ersetzt」, 「j) der 31. Oktober 2017 (500. Jahrestag der Reformation).」 추가 | i 는 구두점만이다. a–i 자구의 출처가 아니다. j 의 종전 문언 출처 |
| Brem.GBl. 2013 Nr. 16 S. 89 | §§ 5·6·13 만 | § 2 무관 |
| 1954 원법(Brem.GBl. S. 115)과 2013 이전 개정 | 관보 포털 공개는 2013 년부터다(연간 목록 링크 2013–2025) | **온라인으로 찾지 못함** — a–i 는 verified false |

- [추론] a–i 의 현행 자구는 1954 원법에 1990 년대 개정(3. Oktober·Buß- und Bettag 폐지 따위)이 얹힌 것이다. 그 호들은 이번 경로로 닿지 않는다.

---

## BB — 브란덴부르크

### BB-1. 현행 조문
- BRAVORS `https://bravors.brandenburg.de/gesetze/ftg_2015`: 200, 20,288 B, 정적 HTML, 2026-09-30.
- 표제는 「Gesetz über die Sonn- und Feiertage (Feiertagsgesetz - FTG) vom 21. März 1991 (GVBl.I/91, [Nr. 06], S.44) zuletzt geändert durch Gesetz vom 30. April 2015 ( GVBl.I/15, [Nr. 13] )」 이다. 통합본이라 2차 출처다.
- § 2 Abs. 1 「Gesetzlich anerkannte Feiertage sind:」 은 번호 없는 열거 12 건이다(아래 표).

### BB-2. 항목 (주 전역 12, 전부 기존 규칙 유형 — 부활절 +0·+49 도 오프셋)

| 열거 | 조문 | SUMMARY(name) | scope | key | 규칙 |
|---|---|---|---|---|---|
| 1 | 「der Neujahrstag (1. Januar)」 | Neujahrstag | bundesweit | neujahr | 1. 1. |
| 2 | 「der Karfreitag」 | Karfreitag | bundesweit | karfreitag | −2 |
| 3 | 「der Ostersonntag」 | Ostersonntag | land | **ostersonntag**(승인됨) | +0 |
| 4 | 「der Ostermontag」 | Ostermontag | bundesweit | ostermontag | +1 |
| 5 | 「der 1. Mai (Tag der Arbeit)」 | 1. Mai | bundesweit | erster_mai | 5. 1. |
| 6 | 「der Christi Himmelfahrtstag」 | Christi Himmelfahrtstag | bundesweit | christi_himmelfahrt | +39 |
| 7 | 「der Pfingstsonntag」 | Pfingstsonntag | land | **pfingstsonntag**(승인됨) | +49 |
| 8 | 「der Pfingstmontag」 | Pfingstmontag | bundesweit | pfingstmontag | +50 |
| 9 | 「der Tag der deutschen Einheit (3. Oktober)」 | Tag der deutschen Einheit | bundesweit | tag_der_deutschen_einheit | 10. 3. |
| 10 | 「das Reformationsfest (31. Oktober)」 | Reformationsfest | land | reformationstag | 10. 31. |
| 11 | 「der 1. Weihnachtsfeiertag (25. Dezember)」 | 1. Weihnachtsfeiertag | bundesweit | erster_weihnachtstag | 12. 25. |
| 12 | 「der 2. Weihnachtsfeiertag (26. Dezember)」 | 2. Weihnachtsfeiertag | bundesweit | zweiter_weihnachtstag | 12. 26. |

- 조문 인용은 「§ 2 Abs. 1, 열거 n번째」 다(번호 없는 열거 — BW 전례).
- 범위 밖은 § 2 Abs. 2 Gedenk- und Trauertage(Volkstrauertag·Totensonntag·8. Mai)와 Abs. 4 종교 축일이다.
- Abs. 3(주 정부의 일회성 지정 수권)에 따른 2020 이후 명령은 이번에 찾지 않았다. 전제 보고도 「1 쪽만 봐 [추론]」 이다. 판단 요청 3 에 둔다.
- 2026 날짜 12 건이 feiertage-api 2026 BB(hinweis 공란 12)와 같다.

### BB-3. 공포본
- BRAVORS 1994 연도 목록(`…/veroeffentlichungsblaetter_chronologisch/1994`, 200)에 있는 PDF 는 셋뿐이다: `GVBl_I_12_1994.pdf`·`GVBl_I_26_1994.pdf`·`Amtsblatt 51_94.pdf`.
  - Nr. 26(9 월, S. 401–404)을 받아 보니 Wahlprüfungsgesetz 공고였다.
  - **1994-12-19 개정(GVBl. I/94 S. 514)의 호는 목록에 없다.**
  - 1991 연도 목록은 BRAVORS 에 없다(전제 보고: 링크된 연도는 1994–2026).
- 2015 개정 `GVBl_I_13_2015.pdf`(200, 128,605 B)를 판독했다. 「§ 2 Absatz 2 … Folgende Nummer 3 wird angefügt: „3. der 8. Mai als Tag der Befreiung …"」 — Abs. 2 만 바꿨다. Abs. 1 자구의 출처가 아니다.
- 따라서 **BB 12 건 전부 verified false** 다. 1991 원법과 1994 개정의 공포본을 온라인으로 찾지 못했다. [추론] 1994 개정이 § 2 를 새로 썼는지(포털 기재 「§§ 1, 2, 4, 5, 7-12」)는 이번에도 확인하지 못했다.

---

## 초안 (적용하지 않음) — `report_hb_bb_prep/drafts/`

- `de_hb_solar_holidays.yaml`(6)·`de_hb_easter_holidays.yaml`(4)·`de_bb_solar_holidays.yaml`(6)·`de_bb_easter_holidays.yaml`(6).
- 항목 필드 순서는 기존 표와 같다: key·name·scope·month/day 또는 easter_offset·verified·source(·source_todo).
- **안전망 패턴 검사 0 건**(`drafts/safety_net_check.txt` — `tests/test_de_source_selfcontained.py` 의 금지 문자열 12 개, 대소문자 무시).
- HB verified: reformationstag 만 true(Brem.GBl. 2018 Nr. 63 서지, 재수령 대조 일치). 9 건 false + source_todo.
- BB verified: 12 건 전부 false + source_todo.
- 줄 접기는 하지 않았다. 구현 때 기존 표처럼 접는다.

머리 주석 개요(두 주 공통 뼈대 — 기존 de_rp·de_ni 형):
1. 근거 법령·조문 열거 인용(§ 2 Abs. 1).
2. 공포본(열람처·URL·sha256·열람일). HB 는 2018 Nr. 63, BB 는 「온라인 공포본 없음」 과 확인한 경로.
3. 현행 조문 출처(통합본, 2차) — HB 는 현행판 500 과 구판·관보 제목 검색의 결과를 적는다.
4. 범위 밖 — Gedenktage·종교 축일, BB Abs. 3 수권.
5. 대체공휴일(이동) 규칙 — 실측 필요(python-holidays 교차, 구현 때).
6. key 규약 — UID token 접두사 `de_hb-`·`de_bb-`. BB 신규 key `ostersonntag`·`pfingstsonntag` 는 승인 완료다. 나머지는 기존값.
7. name — SUMMARY 규칙과 이 표의 적용(소문자 deutschen, 서술부·괄호 제거).
8. verified — 무엇을 읽었고 무엇이 남았나.
9. scope 절 — 기존 문구 그대로.

---

## 판단 요청 — 5 건

1. **SUMMARY 표기.**
   - HB g: 「der 3. Oktober - Tag der deutschen Einheit -」 → 「Tag der deutschen Einheit」(SH 형 날짜부 제거 + de_be 형 소문자 d).
   - BB 9: 「Tag der deutschen Einheit」(소문자 d).
   - BB 10: key `reformationstag` 에 SUMMARY 「Reformationsfest」(조문 표기).
   - BB 6·11·12 는 「Christi Himmelfahrtstag」 「1./2. Weihnachtsfeiertag」 다.
   - 이대로 가는가.
2. **HB 현행 조문 근거.** 공식 현행판(2025-06-30 판)이 세 번 500 이었다. 2020 구판과 관보 제목 검색(§ 2 개정 법 없음, 2025 변경은 § 11 관할)으로 § 2 Abs. 1 을 확정하고 구현할지, 현행판을 받을 때까지 기다릴지 정한다.
3. **verified 후보와 BB 일회성.**
   - HB 는 reformationstag 1 건만 true, BB 는 0 건으로 첫 발행한다(HH·NI·RP 전례처럼 false 로 발행 후 승격).
   - BB § 2 Abs. 3 일회성 명령(2020~)은 검색을 더 할지 정한다. BRAVORS 검색은 세션 쿠키가 필요한 POST 폼이다.
4. **체크리스트 누락 — `tests/test_de_be_feed.py:227–242` `STATE_FEEDS`.** `docs/operations.md` 「피드 추가」 표에 없다. 구현 PR 에서 표를 고칠지(또는 그 dict 를 스캔으로 바꿀지) 정한다.
5. **PR 단위.** HB·BB 를 한 PR 로 할지, 주마다 하나로 할지 정한다(MV·SN 은 주마다 하나로 결정돼 있다).
