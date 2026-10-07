# HB — Brem.GBl. 2020–현재 전문 검색 (조사만)

- 측정 시점: 2026-10-06(UTC, 요청 13:24:07Z–15:03:11Z).
- 범위: 조사만 했다. 레포 변경·브랜치·커밋·PR 없음. Codex 호출 없음. 병렬화하지 않았다(scratch 하나).
- 재현 기록: `~/holidays-reports/report_hb_fulltext/`(README 참조).
- 표기: 명령 출력·원문에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.

---

## 범위 진술

This search decides only one question: whether the current § 2 Abs. 1 equals the 2020-03-14 consolidated text. It does not promote any entry's `verified` status. Entries a–i remain `verified: false` regardless of the outcome, because their promulgated texts (1954 original law and pre-2013 amendments) are still not reachable online. Entry j's `true` candidacy rests on Brem.GBl. 2018 Nr. 63 and is not affected by this search.

---

## 기준 SHA

- `origin/main` = `50e14d9bdd348df2ab102740c3c6c48c51a94794`(「chore: status 갱신 2026-10-05」). 기대값 50e14d9 와 같다.
- 로컬 `main` 은 `39a8d4a` 에 있었다(뒤처짐). 레포 파일은 `git show 50e14d9:<path>` 로 읽었다. 작업 트리는 건드리지 않았다.

---

## Step 0 — 사전 확인 (네 전제 모두 성립 → Step 1 진행)

| # | 전제 | 관측 | 판정 |
|---|---|---|---|
| P1 | 목록 페이지가 정적 HTML, 항목마다 호·날짜·PDF 링크 | `?skip=0&max=100` → 200, `text/html`, 57,286 B, 최종 URL `…/gesetzblatt-1459?max=100&skip=0`. 항목은 `<li class="search-result-item">` 안의 `<h2><a class='download' href='…pdf'>Gesetzblatt YYYY Nr. N</a></h2>`·「Veröffentlichungsdatum: DD.MM.YYYY」·「Hinweistext」·「(S. …)」. 범위: **skip 0–1000**(11 쪽). skip 0 첫 항목은 2026 Nr. 101(03.10.2026), skip 1000 의 마지막은 2019(06.09.2019). 2020 Nr. 1(03.01.2020)·Nr. 2 는 skip 1000 에 있다 | 성립 |
| P2 | 2018 Nr. 63 sha256 | fetch.log 의 URL 로 다시 받음: 200, 241,672 B, `e0a706281f932bd4445366e2e546b0de894f0fcfc1e5ccb1793bdcb8665e23bf` | 일치 |
| P3 | 추출 도구·2018 Nr. 63 대조 | pdftotext·mutool·qpdf 는 없다. **pypdf 5.4.0**(Python 3.9.6, `uv run --no-project --with 'pypdf==5.4.0'`). 추출: 1 쪽, 732 자. 「1. § 2 Absatz 1j wird wie folgt neu gefasst: der Reformationstag.」 「Artikel 2 Inkrafttreten Das Gesetz tritt am Tag nach seiner Verkündung in Kraft.」 — `hb_2018_63_text.txt` 와 같은 자구. 차이: 기존 전사(738 자)의 끝 「Unterzeichner: Senatskanzlei Bremen」 이 pypdf 출력에 없고, 머리의 연도가 「201 8」 로 갈려 나온다. 둘 다 § 2 Absatz 1j·Art. 2 자구 밖이다 | 실질 일치 |
| P4 | 2020 S. 52 법의 호·URL | **Brem.GBl. 2020 Nr. 12**, 공개일 13.03.2020, 「(S. 52)」, `https://www.gesetzblatt.bremen.de/fastmedia/218/2020_03_13_GBl_Nr_0012_signed.pdf` | 성립 |

---

## 코퍼스 요약 (Step 1)

- 대상: 목록의 2020 Nr. 1(03.01.2020)부터 **2026 Nr. 101(03.10.2026, 13:24Z 목록 수령 시점의 최신)** 까지.
- URL 은 전부 목록 href 그대로다(퍼센트 인코딩 포함, 예: `2025_06_30_GBl%200076_signed.pdf`). 패턴으로 만든 URL 없음.
- 요청: 순차, 매 요청 뒤 3 초 대기. 코퍼스 PDF 1,056 건 모두 첫 요청에 200·`application/pdf`. 5xx 재시도는 Step 7 에서만 일어났다.
- `fetch.log`: 요청 1,077 줄(목록 11, 2018 Nr. 63 1, 코퍼스 1,056, 연간 목록 6, Step 7 3) — 200 이 1,074, 500 이 3. sha256 7 줄.

| 연도 | 목록 항목 | 번호 범위 | 빠짐 | 중복 | PDF 없음 | 연간 목록 PDF 「Alle Gesetzblätter des Jahrganges」 | 받은 PDF | 쪽 | 추출 문자 |
|---|---|---|---|---|---|---|---|---|---|
| 2020 | 176 | 1–176 | 0 | 0 | 0 | 176 (일치) | 176 | 1,744 | 3,359,126 |
| 2021 | 158 | 1–158 | 0 | 0 | 0 | 158 (일치) | 158 | 946 | 1,712,245 |
| 2022 | 167 | 1–167 | 0 | 0 | 0 | 167 (일치) | 167 | 1,103 | 1,993,446 |
| 2023 | 130 | 1–130 | 0 | 0 | 0 | 130 (일치) | 130 | 644 | 1,116,947 |
| 2024 | 159 | 1–159 | 0 | 0 | 0 | 159 (일치) | 159 | 1,142 | 2,121,268 |
| 2025 | 167 | 1–167 | 0 | 0 | **2** | 167 (일치) | 165 | 1,493 | 2,697,200 |
| 2026 | 101 | 1–101 | 0 | 0 | 0 | (연간 목록 없음) | 101 | 662 | 1,174,766 |
| 계 | 1,058 | | **0** | **0** | 2 | | **1,056** | **7,734** | 14,174,998 |

- 2025 의 PDF 없는 두 호: **Nr. 12** 「Gesetzblatt 2025 Nr. 12 wurde zurückgezogen」(21.02.2025), **Nr. 91** 「Gesetzblatt 2025 Nr. 91 wurde aufgehoben」(25.07.2025). 둘 다 목록 href 가 비어 있다. 2025 연간 목록 PDF 에도 같은 두 줄이 있다.
- 한 호에 PDF 가 둘 이상인 항목(Sonderausgabe 등): **없음**(모든 항목 링크 1 개).
- 연간 목록 대조: 각 PDF 의 「Alle Gesetzblätter des Jahrganges YYYY: N」, 「Veröffentlichungsdatum」 수, 서로 다른 「Gesetzblatt … Nr.」 번호 수, 최대 번호가 모두 위 표의 목록 항목 수와 같다. 연간 목록 PDF 여섯의 바이트 수는 이전 조사(`report_hb_bb_prep/fetch.log`)와 같다.
- 목록 표기 불규칙: 연도 없는 「Gesetzblatt Nr. N」 4 건(2020 Nr. 31, 2022 Nr. 113, 2023 Nr. 25, 2024 Nr. 5)과 「Nr:」 2 건(2020 Nr. 85, 171). 공개일 연도로 보충했다. 공개일·번호 순서 모순은 없었다.
- 범위 경계: 2019 의 마지막은 Nr. 137(23.12.2019, 「Verordnung über die Sonntagsöffnung … im Jahre 2020」). 범위 밖이라 받지 않았다.
- PDF 는 scratch 에만 두었고 보고 폴더에 복사하지 않았다.

---

## 텍스트층 결과 (Step 2)

- 1,056 파일 모두 pypdf 로 열렸다(추출 오류 0, 텍스트 0 자인 파일 0).
- **비공백 200 자 미만 쪽: 741 쪽, 167 파일**(`flagged_pages.txt`). 연도별 741 = 2020 142 · 2021 107 · 2022 92 · 2023 52 · 2024 75 · 2025 199 · 2026 74.
- 이 741 쪽은 **검색할 수 없는 쪽으로 보고한다.** OCR 하지 않았다.
- 플래그 쪽의 구성(관측, `flagged_pages_split.tsv`):
  - **598 쪽(41 파일)**: 텍스트층이 쪽 머리 「Nr. N Gesetzblatt der Freien Hansestadt Bremen vom … <쪽 번호>」 뿐이다. 본문 글자가 텍스트층에 없다.
  - 140 쪽: 머리 뒤에 짧은 본문이 있다(예: 「Artikel 2 Inkrafttreten …」, 서명, 「Anlage 1 (zu § 3 …)」, 「Karte 2: Übersichtskarte …」).
  - 3 쪽: 머리 꼴이 아닌 짧은 텍스트(2026 Nr. 86 p2, 2024 Nr. 55 p15, 2024 Nr. 54 p17).
- 쪽 머리만 있는 쪽이 많은 파일(목록 제목, `flagged_files.tsv` 에 167 파일 전부):
  - 2020 Nr. 108(105/112 쪽) Medienstaatsvertrag · 2025 Nr. 110(83/84) Siebter Medienänderungs-StV · 2021 Nr. 48(67/68) Glücksspiel-StV
  - **2024 Nr. 103(35/36) 「Berichtigung des Gesetzblattes Nr. 100」** · 2025 Nr. 109(32/34) · 2025 Nr. 127(26/51) Mietpreis-VO · 2025 Nr. 36(25/26)
  - **2023 Nr. 65(6/12) 「Gesetz zur Änderung dienstrechtlicher Vorschriften」**(조항법)
  - 그 밖의 Berichtigung: 2024 Nr. 101(5/6) 「… Nr. 99」 · 2024 Nr. 76(7/8) 「… Nr. 70」 · 2025 Nr. 159(2/3) 「… Nr. 8 aus 2002」
- [추론] 쪽 머리만 있는 쪽은 본문이 이미지로 들어 있거나 비어 있는 쪽으로 보인다. 비었는지 확인하지 않았다(렌더·OCR 하지 않음). 이 추론으로 어떤 쪽도 검색 대상에서 빼지 않았다.
- 플래그 쪽이 무관하다고 판단하지 않는다 — 기준 2 와 판단 요청 1 로 넘긴다.

---

## 대조군 (Step 4) — 3/3 적중

| 대조군 | 파일 | 적중 |
|---|---|---|
| 2025 Nr. 98(§ 11 을 든 호) | `2025_098` | p2 `feiertag` 1, `gedenk` 1 — 「gesetz über die sonn-, gedenk- und feiertage 12. november 1954 sabremr § 11」 |
| 2020 Nr. 12(S. 52, P4) | `2020_012` | p1 `feiertag` 4, `gedenk` 6, `113-c` 1 |
| 2018 Nr. 63(범위 밖) | `2018_063` | p1 `feiertag` 3, `reformationstag` 1(`controls_2018_063_hits.tsv`) |

- 세 대조군 모두 적중했다. 방법은 **텍스트층이 있는 쪽에 대해서는** 유효하다. 대조군은 셋 다 플래그 쪽이 없다 — 플래그 쪽에 대한 방법 유효성은 이 대조군이 보여주지 않는다.

---

## 검색 (Step 3)

- 정규화: (1) 줄 끝(뒤 공백 무시)이 「-」 이고 다음 줄이 소문자로 시작할 때만 잇는다, (2) 공백 축약, (3) casefold. 쪽 단위로 한다(쪽 경계는 잇지 않는다).
- 패턴: `feiertag`, `gedenk`, `113-c`, `reformationstag`, `einmalig` — 정규화 텍스트의 부분 문자열.
- **적중 164 건, 64 파일**(`hits.tsv`, 문맥 앞뒤 300 자): feiertag 92 · einmalig 52 · gedenk 17 · reformationstag 2 · 113-c 1.
- `113-c` 는 코퍼스 전체에서 2020 Nr. 12 의 「SaBremR 113-c-1」 한 건뿐이다.
- `reformationstag` 두 건은 모두 2022 Nr. 142 다(학교 방학 규정, 아래 D).

---

## 분류표 (Step 5)

| 분류 | 적중 | 파일 |
|---|---|---|
| A — § 2 Abs. 1 개정 | **0** | — |
| B — 그 법의 다른 조항 개정·표제 변경 | **11** | 2020 Nr. 12 |
| C — 2020 년 이후 날짜의 주 전역 일회성 공휴일 지정 | **0** | — |
| D — 언급뿐 | 153(그중 [추론] 2) | 63 파일 |

**B — 2020 Nr. 12 S. 52(적중 11 건 전부).** 동작 문언:
- Art. 1 Nr. 1 「Die Überschrift wird wie folgt gefasst: „Gesetz über die Sonn-, Gedenk- und Feiertage“.」
- Art. 1 Nr. 2 「Die Überschrift des I. Abschnittes wird wie folgt gefasst: „Die Sonntage und die staatlich anerkannten Gedenk- und Feiertage“」
- Art. 1 Nr. 3 「Nach § 7 wird folgender § 7a eingefügt: „§ 7a (1) Der 8. Mai als Tag der Befreiung … ist staatlich anerkannter Gedenktag. (2) …“」
- 이 호의 적중 중 인용부(「Das Gesetz über die Sonn- und Feiertage vom 12. November 1954 (GVBl. 1954, 115 SaBremR 113-c-1)」)와 법 제목의 「als Gedenktag」 도 같은 개정 법 안의 적중이라 B 로 셌다.

**D [추론] 2 건 — 2025 Nr. 98 p2.** 「Bekanntmachung über die Änderung von Zuständigkeiten」(§ 7 Bremisches Rechtsbereinigungsgesetz) Anlage 1(Senator für Inneres und Sport) 표의 한 줄 「Gesetz über die Sonn-, Gedenk- und Feiertage | 12. November 1954 | SaBremR | § 11」. 관할 이전의 공고이고 조문 자구를 바꾸라는 지시가 없다. 그래서 D 로 읽었다 — 개정 문언이 아니라 내 읽기다.

**D — 나머지 151 건**(`classification.tsv` 에 적중마다 근거):
- 법을 이름으로 인용만: 내무 Kostenverordnung 수수료표(2020 Nr. 67, 2022 Nr. 17, 2024 Nr. 17, 2025 Nr. 100 — 2025 판은 새 법명 「Sonn-, Gedenk- und Feiertage」 를 쓴다), Bremerhaven 일요일 영업 명령 § 2 「Die Vorschriften des Gesetzes über die Sonn- und Feiertage, … bleiben unberührt.」(2021 Nr. 96, 2022 Nr. 35, 2023 Nr. 1, 2023 Nr. 120, 2024 Nr. 139, 2025 Nr. 125).
- 2023 Nr. 63: Ladenschlussgesetz 개정 — 「Sonn- und Feiertage」 는 영업일 수 규정의 낱말.
- **2022 Nr. 142**: 학교 방학 규정 § 4 「gesetzliche Feiertage sind in Bremen: der Neujahrstag, der Karfreitag, der Ostermontag, der 1. Mai, der Himmelfahrtstag, der Pfingstmontag, der 3. Oktober (Tag der deutschen Einheit), der 31. Oktober (Reformationstag), der 1. und der 2. Weihnachtstag.」 — Feiertagsgesetz 를 고치지 않는다. 열거된 10 개는 2020 판 § 2 Abs. 1 a–j 와 같은 날들이다(대조는 판단 요청 5).
- 낱말 쓰임: 근무시간·수당·수수료의 「Sonn- oder Feiertag」, 「Gedenkstätte(n)」·「Gedenkstein」·「Gedenkfeiern」, 「einmalig(e)」(일회성 지급·수수료·재선임·시험 등 52 건 전부).
- 일회성 공휴일을 지정하는 문맥(「einmalig」 + Feiertag 지정)은 적중 문맥에 없다.

---

## 2020 S. 52 법 (Step 6)

- 전사: `report_hb_fulltext/hb_2020_012_text.txt`. 출처: Brem.GBl. 2020 Nr. 12 S. 52, 200, 197,746 B, sha256 `ab9347a5b0dc85d9c710714815bc6b493bcbc1e5a4053f79bb47e2ed45963653`, 1 쪽, 2026-10-06 열람.
- 법: 「Gesetz zur staatlichen Anerkennung des Tags der Befreiung vom Nationalsozialismus und der Beendigung des Zweiten Weltkrieges in Europa als Gedenktag Vom 3. März 2020」, 13.03.2020 공포.
- 개정 대상 표기: 「Das Gesetz über die Sonn- und Feiertage vom 12. November 1954 (GVBl. 1954, 115 SaBremR 113-c-1), das zuletzt durch Gesetz vom 26. Juni 2018 (Brem.GBl. S. 302) geändert worden ist」 — 직전 개정을 2018 Nr. 63(S. 302)으로 든다.
- **고친 조항**: 표제(Nr. 1), I. Abschnitt 표제(Nr. 2), § 7a 신설(Nr. 3). 그 밖은 없다.
- **표제 변경**: 그렇다 — 「Gedenk-」 를 넣어 「Gesetz über die Sonn-, Gedenk- und Feiertage」 가 됐다.
- **§ 2 Abs. 1**: 건드리지 않는다. 개정 지시 세 개 중 § 2 를 가리키는 것이 없다.
- 시행: Art. 2 「Dieses Gesetz tritt am Tag nach seiner Verkündung in Kraft.」 → 14.03.2020. Transparenzportal 판 145882 의 「Inkrafttreten 14.03.2020」 과 같은 날이다.
- 따라서 2020-01-01–2020-03-13 구간: 이 법은 § 2 Abs. 1 을 바꾸지 않는다. 같은 구간의 다른 호(2020 Nr. 1–11)에는 A·B·C 적중이 없다(Nr. 6·7 의 D 2 건뿐). 같은 구간에 플래그 쪽이 있는 호는 2020 Nr. 11(9/10 쪽, 「Gesetz zum Dreiundzwanzigsten Rundfunkänderungsstaatsvertrag」) 이다.
- [추론] 이 법의 시행일과 2020-03-14 판의 시행일이 같으므로, 145882 판은 이 법을 반영한 통합본이다.

---

## Step 7 — 현행 통합본

- `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.296390.de&template=00_html_to_pdf_d`
  - 15:02:33Z **500**, `text/html; charset=utf-8`, 0 B
  - 15:02:47Z(재시도 1) **500**, 0 B
  - 15:03:11Z(재시도 2) **500**, 0 B
- PDF 를 받지 못했다. § 2 Abs. 1 글자 대조는 하지 못했다. 정책대로 더 요청하지 않았다.
- 이전 조사(2026-09-30 1 회, 그 전 2 회)와 합쳐 이 URL 의 500 은 여섯 번째다.

---

## 판정표 — 실행 전에 정한 기준

| # | 기준 | 수치 | 판정 |
|---|---|---|---|
| 1 | 코퍼스 빠짐 = 0 | 빠진 번호 0, 중복 0, 연간 목록 대조 6/6 일치. 단 PDF 없는 호 2(2025 Nr. 12 zurückgezogen, Nr. 91 aufgehoben) | 충족 (PDF 없는 2 호는 판단 요청 2) |
| 2 | 플래그(검색 불가) 쪽 = 0 | **741 쪽 / 167 파일**(그중 쪽 머리만 598 쪽 / 41 파일) | **미충족** |
| 3 | 대조군 적중 = 3/3 | 3/3 | 충족 |
| 4 | A 적중 = 0 | 0(검색 가능한 텍스트층 안에서) | 충족 |
| 5 | C 적중 = 0 | 0(검색 가능한 텍스트층 안에서) | 충족 |
| 6 | 2020 S. 52 법이 § 2 Abs. 1 을 건드리지 않음 | 개정 지시 3 개: 표제·I. Abschnitt 표제·§ 7a | 충족 |

기준 2 가 미충족이다. **전체 「통과」 는 쓰지 않는다.** 지시에 따라 여기서 보고로 멈춘다. OCR 하지 않았고, 플래그 쪽이 무관하다는 판단도 하지 않았다.

---

## 사람의 판단 요청

1. **기준 2 — 플래그 741 쪽(167 파일).** 어떻게 처리할지 정해 주어야 한다. 선택지는 이렇다.
   - (a) OCR 해서 같은 패턴으로 다시 검색한다(이번 지시에서는 금지됨).
   - (b) 다른 경로로 해당 호를 확인한다 — 예: 연간 목록·Transparenzportal 의 해당 법령, 원문 HTML 판.
   - (c) 범위·기준을 다시 정한다.
   - 근거 자료는 `flagged_files.tsv`(파일별 플래그 수·쪽 머리만 있는 수·목록 제목)와 `flagged_pages_split.tsv` 다.
   - 사실로 적어 둘 것:
     - 쪽 머리만 있는 쪽이 있는 호에 조항법 2023 Nr. 65 「Gesetz zur Änderung dienstrechtlicher Vorschriften」(6/12 쪽)가 있다.
     - Berichtigung 네 건도 있다: 2024 Nr. 103(35/36), 2024 Nr. 101, 2024 Nr. 76, 2025 Nr. 159.
2. **PDF 없는 2025 두 호.** Nr. 12 「wurde zurückgezogen」, Nr. 91 「wurde aufgehoben」. 번호는 이어져 있어 기준 1 은 「빠짐 0」 으로 셌다. 이 두 호를 코퍼스 빠짐으로 볼지 정한다.
3. **2025 Nr. 98 의 D [추론].** 관할 이전 공고의 § 11 언급을 D(언급뿐)로 읽었다. 공고가 조문을 「바꾸는」 것으로 볼지는 사람 판단이다. 어느 쪽이든 § 2 Abs. 1 을 가리키지 않는다(A 아님).
4. **Step 7.** 현행판 PDF 는 이번에도 500 이다(3 회). 글자 대조는 열려 있다.
5. **2022 Nr. 142 § 4 의 열거.**
   - 2022 년 학교 규정이 「gesetzliche Feiertage sind in Bremen」 으로 10 개를 든다. 그중에 「der 31. Oktober (Reformationstag)」 가 있다.
   - 공포본이 § 2 Abs. 1 과 같은 목록을 적은 2차 자료다. 이것을 교차 확인으로 source 에 쓸지 정한다. 쓰더라도 verified 승격 근거는 아니다(범위 진술).
6. **방법의 알려진 한계.**
   - 쪽 경계를 넘는 낱말은 잇지 않았다.
   - 정규화 규칙은 「Sonn-\nund」 를 「sonnund」 로 만든다. 다섯 패턴의 적중에는 영향이 없다 — 하이픈만 지워진다.
   - 추출기가 pypdf 하나뿐이다.
   - 이 한계를 받아들일지 정한다.
