# MV — 한 번의 재시도: 공식 포털, GVOBl. M-V 2022 Nr. 31, 일회성 지정 (조사만)

- 측정 시점: 2026-11-18(UTC, 요청 04:51:39Z–05:00:35Z).
- 범위: 조사만 했다.
  - 레포 변경·브랜치·커밋·PR 없음. 기존 `report_mv_prep*` 는 고치지 않았다(기록이다).
  - Codex 호출 없음. 병렬화하지 않았다(scratch 하나).
- 재현 기록: `~/holidays-reports/report_mv_retry/`(README 참조). 렌더 HTML·받은 파일은 scratch 에 남겨 두었다 — MV 갈래는 닫히지 않았다.
- 표기: 명령 출력·원문·렌더에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- 사람의 결정(Holiday_21 §5, 이번 지시): **이 조사가 단 한 번의 재시도다.** 결과와 상관없이 MV 는 이 보고에서 멈춘다. 다음 회차는 제안하지 않는다.
- **결과 요약**
  - **Part A — 얻음.** 원래 문서 id(`jlr-FeiertGMVrahmen`)는 이번에도 실패했다(문서 API·toc 500). 포털 검색이 같은 법을 다른 id 로 찾았다. 조문 단위 id `jlr-NNLMV00007A2FNN00000000003` 이 § 2 전문을 냈다. 머리는 「Fassung vom: 07.07.2022 / Gültig ab: 13.07.2022」 다. 10 초 뒤 두 번째 렌더의 추출 텍스트가 같았다.
  - **Part B — 얻지 못함.** 2026-09-30 의 PDF URL 은 이제 `https://land-mv.de/` 첫 화면(HTML)으로 넘어간다. 새 관보 화면은 2026 년 호만 싣고 2014–2025 는 「E-Mail 로 요청」 이라고 적는다. URL 을 만들지 않았다.
  - **Part C — 멈춤.** 2020–2025 목록에 닿지 못했다. 닿은 2026 목록(Nr. 1–31, 빠짐 없음)은 링크 글자에 제목이 없다. 전문 검색은 하지 않았다.

---

## 기준 SHA와 환경

- `origin/main` = `399a3743d00145c68e1670dd9b1cdc30a40629c0`(Merge pull request #123). 기대값 399a374 와 같다. 로컬 `main` 도 같은 커밋이다.
- **환경은 이 조사 전, 2026-11-18 에 새로 세웠다.**
  - `uv` 를 설치했고, `uv sync` 로 `.venv` 를 다시 만들었다. chromium headless shell 을 설치했다.
  - `~/holidays-reports` 는 `<local>/holidays-reports` 로 가는 심볼릭 링크다(링크 시각 2026-11-18 13:49 로컬).
  - 이 준비는 포털에 요청을 보낸 일이 아니다. 사람의 명확화: 「한 번의 시도」 는 포털로 가는 요청에 대한 것이고 로컬 환경 준비는 시도를 바꾸지 않는다.
  - 처음 세션에서 Step 0 을 돌렸을 때는 E2·E3 이 성립하지 않아 요청 전에 멈췄다(`uv` 없음, `.venv` 의 파이썬 링크가 없는 경로를 가리킴). 그때 포털·관보로 간 요청은 0 건이다.

### Step 0 — 사전 확인 (세 전제 모두 성립)

| # | 전제 | 관측 | 판정 |
|---|---|---|---|
| E1 | `report_mv_prep.md` 가 든 보고 디렉터리 | `<local>/holidays-reports`(`~/holidays-reports` 가 이리 링크). `report_mv_prep.md` 있음. 새 보고는 같은 디렉터리에 둔다 | 성립 |
| E2 | 기준 SHA 에서 `uv run pytest -q` | **1850 passed, 4 xfailed, 29 xpassed**(48.25 s). uv **0.13.9**(Homebrew 2026-11-17 aarch64-apple-darwin), `.venv` 파이썬 **3.12.16**(uv 관리형) | 성립 |
| E3 | playwright·headless chromium(레포 환경, report_mv_prep 과 같은 방식) | `uv run` 의 playwright **1.62.0**(레포 고정), 브라우저 디렉터리 `chromium_headless_shell-1234`, 실행 버전 **151.0.7922.34** | 성립 |

**report_mv_prep(2026-10-07)과의 비교**

| 항목 | report_mv_prep | 이번 |
|---|---|---|
| chromium headless shell | 151.0.7922.34(`chromium_headless_shell-1234`) | **151.0.7922.34**(`chromium_headless_shell-1234`) — 같다 |
| playwright | 1.62.0 | 1.62.0 — 같다 |
| uv | 기록 없음(보고 본문). 옛 `.venv/pyvenv.cfg` 는 `uv = 0.12.2` 였다 | 0.13.9 |
| `.venv` 파이썬 | 기록 없음. 옛 `pyvenv.cfg` 는 3.12.13(Homebrew python@3.12) | 3.12.16(uv 관리형) |

- 옛 `pyvenv.cfg` 값은 처음 세션의 Step 0 에서 읽은 것이다. 그 `.venv` 는 `uv sync` 로 다시 만들어져 지금은 없다.

---

## Part A — 공식 포털

요청은 순차였고 사람이 여는 화면 사이를 3 초 이상 띄웠다(`fetch.log`). 하위 요청은 브라우저가 스스로 낸다. 렌더마다 요청 전부를 `render/*.net.tsv` 에 적었다(시각·메서드·URL·상태·content-type).

### A1 — `jlr-FeiertGMVrahmen` (실패, 재시도 1 회도 실패)

- 렌더 1: 04:51:39Z. 문서 URL 200, 렌더 HTML 13,841 B, 요청 46 건.
- 렌더 2(5xx 재시도 1 회): 04:52:11Z. 같은 결과.
- 두 렌더 모두 실패한 요청은 둘뿐이다(`render/a1_r1.net.tsv`·`a1_r2.net.tsv`):
  - `POST https://www.landesrecht-mv.de/jportal/wsrest/recherche3/document` → **500** `application/json`
  - `POST https://www.landesrecht-mv.de/jportal/wsrest/recherche3/toc` → **500** `application/json`
  - 나머지 44 건은 200 이다(`init`·`search` 3 회·`documentZone`·`cmsContent`·`configUpdate`·`pricesDefault`·정적 자원).
- 화면 본문(innerText 393 자)은 「Das Laden des Dokumentes jlr-FeiertGMVrahmen ist fehlgeschlagen.」 이다.
  - innerText sha256 은 두 렌더 모두 `9d2b2f37d746c32aa012c9b132778f7e5ed0fefee739ff476b7d9954f49851b2` 다.
  - 2026-10-07 의 `report_mv_prep/render/r1.txt` 와 같은 해시다.
- 「one attempt plus one retry on 5xx」 에 따라 이 URL 은 더 요청하지 않았다.

### A2 — 포털 검색 (얻음)

포털 시작 화면(`https://www.landesrecht-mv.de/bsmv/`)을 렌더하고 Schnellsuche 편집기(`data-testid="ID_FAST_SEARCH_BAR_EDITOR"`)에 검색어를 타이핑한 뒤 검색 단추를 눌렀다. 결과는 브라우저가 받은 `recherche3/search` 응답의 `resultList` 에서 뽑았다(`search_results.tsv`).

| 검색어 | 시각 | 보고된 건수 | 받은 목록 | FTG M-V 문서 |
|---|---|---|---|---|
| Feiertagsgesetz | 04:53:16Z | 26 | 26(전부) | 13 |
| Sonn- und Feiertage | 04:54:10Z | **91** | **26**(첫 화면) | 5(그 26 안에서) |
| FTG M-V | 04:54:37Z | 18 | 18(전부) | 13 |

**FTG M-V 를 담은 id(세 검색의 합집합) — 원래 id `jlr-FeiertGMVrahmen` 과 다르다**

| docId | 결과의 제목 | 결과의 날짜 | 부제 끝 |
|---|---|---|---|
| `jlr-NNLMV00007A2F` | FTG M-V(법 전체, 「Inhalt」/「Gesamtausgabe」) | 08.03.2002 | Textnachweis ab: 01.01.2005 |
| `jlr-NNLMV00007A2FNN00000000001` | § 1 FTG M-V | 08.03.2002 | Textnachweis ab: 01.01.2005 |
| `jlr-NNLMV00007A2FNN00000000003` | **§ 2 FTG M-V — Gesetzliche Feiertage** | **07.07.2022** | **gültig ab: 13.07.2022** |
| `jlr-NNLMV00007A2FNN00000000004` | § 3 | 08.03.2002 | Textnachweis ab: 01.01.2005 |
| `jlr-NNLMV00007A2FNN00000000005` | § 4 | 08.03.2002 | 같음 |
| `jlr-NNLMV00007A2FNN00000000007` | § 5 — Verbotene Veranstaltungen | 07.07.2022 | gültig ab: 13.07.2022 |
| `jlr-NNLMV00007A2FNN00000000009` | § 6 | 21.06.2021 | gültig ab: 01.07.2021 |
| `jlr-NNLMV00007A2FNN00000000010` | § 7 | 08.03.2002 | Textnachweis ab: 01.01.2005 |
| `jlr-NNLMV00007A2FNN00000000011` | § 8 | 08.03.2002 | 같음 |
| `jlr-NNLMV00007A2FNN00000000012` | § 9 | 08.03.2002 | 같음 |
| `jlr-NNLMV00007A2FNN00000000013` | § 10 | 08.03.2002 | 같음 |
| `jlr-NNLMV00007A2FNN00000000015` | § 11 | 15.11.2012 | — |
| `jlr-NNLMV00007A2FNN00000000016` | § 12 | 08.03.2002 | — |

- FTG 가 아닌 결과(제목만, 전부 `search_results.tsv`):
  - StiftG-/FTGKostVO M-V(`jlr-NNLMV000078F0` 와 조문 id 둘, 2017)
  - 「FFN MV」(`jlr-MVFFNAbsch1`·`Absch2`)
  - Artikel 2 JudGemVtr(1996), Artikel 8 FunktRefG(1994), § 7 SchPflVO M-V(2026), § 10 ÖffZG M-V(2024), MinArbV M-V(2026) 등
  - 판결(NJRE…)과 행정규칙(VVMV…)
- **「Sonn- und Feiertage」 의 27–91 번째 65 건은 받지 않았다.** 다음 화면을 열기 전에 아래 렌더가 성공했고, 지시는 「Stop Part A at the first success」 다.

**렌더한 다른 id**(순서대로, 각 1 회. 둘째는 성공 뒤 10 초 비교)

1. `jlr-NNLMV00007A2F`(법 전체) — 04:55:15Z. 요청 47 건 모두 200(`document`·`toc` 포함).
   - 「Inhalt」 탭이라 조문 본문은 없다. 머리와 Stand 줄만 있다(`render/a2_doc_r1.txt`):
     - 「Neugefasst: 08.03.2002」 「Textnachweis ab: 01.01.2005」 「Fundstelle: GVOBl. M-V 2002, 145」 「Gliederungs-Nr: 1136-1」
     - **「Stand: letzte berücksichtigte Änderung: zuletzt geändert durch Gesetz vom 7. Juli 2022 (GVOBl. M-V S. 427)」**
   - § 2 자구가 없어 성공으로 치지 않고 다음 id 로 갔다.
2. `jlr-NNLMV00007A2FNN00000000003`(§ 2) — 04:55:58Z. 요청 49 건 모두 200. **§ 2 전문이 나왔다.**
3. 같은 id 를 04:56:44Z 에 다시 렌더했다(앞 렌더가 끝나고 10 초 뒤). 요청 49 건 모두 200.

**§ 2 렌더의 문서 머리(Dokumentkopf)**

- Amtliche Abkürzung: FTG M-V
- **Fassung vom: 07.07.2022**
- **Gültig ab: 13.07.2022**
- Dokumenttyp: Gesetz
- Gliederungs-Nr: 1136-1
- 본문 끝 「Redaktionelle Hinweise — Fundstelle: GVOBl. M-V 2002, 145」

**§ 2 원문**(렌더 innerText 그대로. 번호와 항목 사이 줄바꿈만 이어 적었다)

> Gesetz über Sonn- und Feiertage (Feiertagsgesetz Mecklenburg-Vorpommern - FTG M-V -) In der Fassung der Bekanntmachung vom 8. März 2002
>
> § 2 Gesetzliche Feiertage
>
> (1) Gesetzliche Feiertage sind:
> 1. der Neujahrstag (1. Januar),
> 2. der Frauentag (8. März),
> 3. der Karfreitag,
> 4. der Ostermontag,
> 5. der 1. Mai,
> 6. der Christi-Himmelfahrtstag,
> 7. der Pfingstmontag,
> 8. der Tag der Deutschen Einheit (3. Oktober),
> 9. der Reformationstag (31. Oktober),
> 10. der 1. Weihnachtstag (25. Dezember),
> 11. der 2. Weihnachtstag (26. Dezember).
>
> (2) Gedenk- und Trauertage sind:
> 1. der Volkstrauertag (vorletzter Sonntag vor dem 1. Advent),
> 2. der Totensonntag (letzter Sonntag vor dem 1. Advent),
> 3. der 8. Mai als Tag der Befreiung vom Nationalsozialismus und der Beendigung des 2. Weltkrieges.
>
> (3) Die Landesregierung kann bei besonderem Anlass für das ganze Land oder für Teilgebiete des Landes Werktage zu einmaligen Feiertagen, Gedenktagen oder Trauertagen erklären und die Schutzvorschriften der §§ 3 bis 6 auf sie ausdehnen.

**추출 텍스트의 해시와 10 초 비교**(`extract_para2.py`, `text/ftg_mv_p2_r1.txt`·`r2.txt`)

- 추출 범위: 「§ 2」 줄부터 「Redaktionelle Hinweise」 앞까지.
- 정규화: 줄마다 공백을 축약하고 빈 줄을 뺐다.
- **sha256 `e7fe52efabaa7216ae815e4ad7931ad32bde43e6636ca40a40b5155c9b02efb5`**(887 B) — 두 렌더가 같다.
- innerText 전체도 두 렌더가 같다(`17abccc5…`).
- 렌더 HTML 은 다르다(`eb4aff5e…` / `d89dcf28…`). report_mv_prep 의 관찰과 같은 꼴이다.

---

## Part B — GVOBl. M-V 2022 Nr. 31 (얻지 못함)

| 시각 | 요청 | 결과 |
|---|---|---|
| 04:57:25Z | `state_MV_fetch.log` 의 PDF URL 그대로: `https://www.regierung-mv.de/static/Regierungsportal/Justizministerium/Inhalte/Rechtliches/GVOBI.M-V/GVOBl.%20Nr.%2031%20v.%2012.7.2022.pdf` | 200 이지만 **`text/html; charset=utf-8`, 361,171 B, 최종 URL `https://land-mv.de/`**(주 정부 포털 첫 화면). PDF 가 아니다. sha256 `0154b7a41469064358114de799f4f74771cc8c14058135e068d38149ea991605` 은 그 HTML 의 것이다 |
| 04:57:46Z | `state_MV_fetch.log` 의 관보 목록 URL 그대로(`…/verkuendungsblaetter/gesetz-verordnungsblaetter/`) | 200, HTML 202,354 B, 최종 URL `https://land-mv.de/landesregierung/ministerium-fuer-justiz-gleichstellung-und-verbraucherschutz`(법무부 첫 화면). 정적 HTML 에 관보 링크 없음 |

관보 목록을 사이트 안의 링크로만 찾았다. URL 은 만들지 않았다.
- 04:58:42Z 법무부 화면(렌더): 링크 27 개 중 관보 링크 없음. 화면 머리에 「Aufgrund des Wechsels zur neuen Legislaturperiode wird das Regierungsportal aktuell schrittweise angepasst.」 가 있다.
- 04:59:14Z 그 화면의 주제 링크 「Bürgerservices und Digitale Verwaltung」(렌더): FAQ 「Wo finde ich offizielle Gesetz- und Verordnungsblätter?」 아래에 링크 「Gesetz- und Verordnungsblättern」 → `https://land-mv.de/landeregierung/jm/gesetz-verordnungsblaetter`(href 그대로 — 「landeregierung」 철자도 사이트의 것이다).
  - 같은 화면의 문장: 「Sämtliche Jahrgänge von 2020 bis 2025 stehen vollständig online zum Abruf bereit.」
- 04:59:28Z 포털 첫 화면(렌더): 관보 링크 없음.
- 04:59:51Z **관보 화면**(렌더, `render/b_list.txt`):
  - 「Allgemeines」 — System Übersicht GVO 31/2026, Stichwortverz. GVO 31/2026.
  - 「Gesetz- und Verordnungsblätter M-V 2026」 — Nr. 31·30·29 와 「Mehr anzeigen」.
  - **「Sie haben Interesse an Gesetz- und Verordnungsblättern, am Amtsblatt oder dem Amtlichen Anzeiger aus den Jahren 2014-2025? Bitte schreiben Sie eine E-Mail unter Angabe der gewünschten Publikation an: … Schriftleitung …」**
  - 2014–2025 연도 절도 링크도 없다.
- 주제 화면의 「2020 bis 2025 … vollständig online」 과 관보 화면의 「2014-2025 … E-Mail」 은 서로 어긋난다. 관보 화면에는 2020–2025 링크가 없다(관측).

결과:
- **2022 Nr. 31 PDF 를 받지 못했다.** 바이트·sha256 대조(2026-09-30 기록 263,235 B)를 하지 못했다.
- 「ausgegeben」 줄·법 제목과 날짜·§ 2 개정 문장·시행 조항을 이번에 인용하지 못했다.
- 시행일을 관보 문언에서 유도하지 못했다. 참고 사실 둘(관보가 아니다):
  - 포털 § 2 머리의 「Fassung vom: 07.07.2022 / Gültig ab: 13.07.2022」(Part A). 통합본 쪽의 기재다.
  - 2026-09-30 조사(`state_MV.md` C-1)가 그 PDF 에서 관찰해 적은 「ausgegeben 12. Juli 2022」 와 「Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.」. 그때 sha256 은 기록되지 않았고, 이번에 다시 확인하지 못했다.
- 텍스트층이 없어 렌더해 읽은 쪽은 없다(받은 PDF 가 없다).

---

## Part C — 2020 년 이후 일회성 지정 (멈춤)

- 닿은 목록은 위 관보 화면 하나다. 「Mehr anzeigen」 을 눌러 펼쳤다(05:00:35Z, 1 회 누름, `expand_listing.py`). PDF 링크는 33 개다(`listing_2026.tsv`).
  - 「Allgemeines」 2: System Übersicht GVO 31/2026, Stichwortverz. GVO 31/2026.
  - **2026 년 호 31 개: Nr. 1(16.1.2026) – Nr. 31(6.11.2026). 빠진 번호 0, 중복 0.** 날짜는 파일 이름에서 읽었다. Nr. 5 는 「vom 27.2.2026」, Nr. 28 은 「v._28.9(2)」 꼴이다.
  - **링크 글자는 「Gesetz- und Verordnungsblatt Nr. N (PDF … KB)」 뿐이고 제목(내용)이 없다.** 검색어 여섯(Feiertag·Gedenktag·einmalig·Frauentag·Befreiung·8. Mai)의 적중은 0 이다. 제목이 없으니 이 0 은 아무것도 말하지 않는다(de_bb `bb_oneoff_scan.txt` 와 같은 처지).
- **2020–2025 목록에는 닿지 못했다.** 옛 목록 URL 은 법무부 첫 화면으로 넘어가고, 새 관보 화면은 그 해들을 E-Mail 요청으로 돌린다.

| 연도 | 목록 | 호 번호 | 빠짐 | 제목 |
|---|---|---|---|---|
| 2020–2025 | **닿지 못함** | — | — | — |
| 2026 | land-mv.de 관보 화면 | 1–31 | 0 | 없음(링크 글자에 호 번호뿐) |

- 분류(개정 / 일회성 지정 / 언급뿐): **적중이 없어 분류할 것이 없다.**
- 지시(「If no listing can be reached, say so and stop Part C. Do not start a full-text search.」)대로 여기서 멈췄다. 2026 호 PDF 도 받지 않았다.

---

## 이것이 MV 에 바꾸는 것 (사실, 결론에는 [추론])

**사실**
- 공식 포털이 현행 § 2 를 낸다. 원래 id 가 아니라 포털 검색이 찾은 조문 단위 id `jlr-NNLMV00007A2FNN00000000003` 에서다. 10 초 간격 두 렌더의 추출 텍스트가 같다(sha256 `e7fe52ef…`).
- § 2 Abs. 1 은 열한 호다. 2026-09-30 조사가 「미관찰」 로 둔 Nr. 1·3–11 의 자구가 이번에 관찰됐다 — 예: 「der 1. Mai」, 「der Christi-Himmelfahrtstag」, 「der Tag der Deutschen Einheit (3. Oktober)」, 「der Reformationstag (31. Oktober)」.
- § 2 Abs. 1 에 지역·종교 한정 호는 없다. 8. Mai 는 Abs. 2 의 Gedenktag 다.
- § 2 Abs. 3 이 일회성 지정의 수권이다: 「Die Landesregierung kann bei besonderem Anlass … Werktage zu einmaligen Feiertagen, Gedenktagen oder Trauertagen erklären …」.
- 포털은 § 2 를 「Fassung vom: 07.07.2022 / Gültig ab: 13.07.2022」 로 적는다. 법 전체의 Stand 는 「zuletzt geändert durch Gesetz vom 7. Juli 2022 (GVOBl. M-V S. 427)」 다.
- GVOBl. M-V 2022 Nr. 31 은 2026-11-18 현재 온라인 목록에 없다. 옛 PDF URL 은 HTML 첫 화면으로 넘어간다.
- 2020–2025 관보 목록이 온라인에 없다. 그래서 de_bb 식 일회성 지정 확인을 할 수 없었다.

**[추론]**
- [추론] Holiday_21 이 MV 보류의 이유로 든 「공식 현행 조문 없음」 은 § 2 에 대해서는 이번 관찰로 해소된다. 법 전체 본문(다른 조문)은 렌더하지 않았다.
- [추론] `effective_from` 값 `2022-07-13` 은 포털의 「Gültig ab: 13.07.2022」 와 2026-09-30 의 관보 관찰(ausgegeben 12.07.2022 + 「am Tag nach der Verkündung」)이 같은 날을 가리킨다. 다만 Holiday_21 §1-2 가 정한 확정 방식(GVOBl. 2022 Nr. 31 로 확정)은 이번에 수행되지 못했다.
- [추론] 포털 Stand 가 2022 개정을 마지막으로 들므로, 그 뒤 FTG 를 바꾼 법은 포털 기준으로 없다. 일회성 지정은 Abs. 3 에 따른 Landesregierung 의 선언이라 FTG 개정이 아니다. 그래서 이 Stand 줄로는 그런 지정이 없었다고 말할 수 없다.

---

## 사람의 판단 요청

다음 회차를 제안하지 않는다(지시). 아래는 이 보고의 사실로 정할 것들이다.

1. **포털 조문 단위 id 의 § 2 를 「공식 현행 조문」 으로 볼지.**
   - 원래 id 는 여전히 실패하고, 같은 포털의 다른 id 가 낸 것이다.
   - 법 전체 「Gesamtausgabe」 는 렌더하지 않았다(첫 성공에서 멈춤).
2. **`effective_from` 근거.** 관보(2022 Nr. 31)를 이번에 받지 못했다. 선택지:
   - (a) 포털 「Gültig ab: 13.07.2022」(2차)와 2026-09-30 관보 관찰(해시 없음)로 적는다.
   - (b) 값을 [추론] 으로 둔 채 보류를 유지한다.
   - (c) 관보 화면이 적은 E-Mail 요청 경로(Schriftleitung)를 사람이 쓸지 정한다. 레포 밖의 사람 행동이다.
3. **일회성 지정(2020 이후)의 서술.**
   - 2020–2025 관보 목록에 온라인으로 닿지 못했고, 2026 목록에는 제목이 없다.
   - de_bb 처럼 「찾지 못함(범위)」 으로 쓸 범위가 성립하지 않는다.
   - source·머리 주석에 이 공백을 어떻게 적을지 정한다.
4. **받지 않은 검색 결과 65 건**(「Sonn- und Feiertage」 27–91 번째). 첫 성공에서 멈춘 결과다. 이것을 그대로 받아들일지 정한다.
5. **「2020 bis 2025 … vollständig online」 대 「2014-2025 … E-Mail」.** 같은 사이트의 두 화면이 어긋난다. 보고에 사실로만 적었다.
