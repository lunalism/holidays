# HB — 검색 불가 쪽: 파일 단위 구조 검사 (조사만)

- 측정 시점: 2026-10-06(UTC, 요청 15:41:49Z–15:58:31Z). 판독은 2026-10-07 까지.
- 범위: 조사만 했다.
  - 레포·`~/holidays-reports/report_hb_fulltext*`·`report_hb_flagged*` 변경 없음. 브랜치·커밋·PR 없음.
  - Codex 호출 없음. 병렬화하지 않았다(scratch 하나).
- 재현 기록: `~/holidays-reports/report_hb_structure/`(README 참조). 코퍼스 PDF 167 개는 scratch 에 남겨 두었다.
- 표기: 명령 출력·원문에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- **결과 요약 — Step 4 는 시작하지 않았다.** 멈춘 이유는 둘이다.
  - (1) Step 1 표본에서 OTHER 1 쪽이 불일치했다.
  - (2) v1 R 합계가 67 쪽으로 60 을 넘었다.

---

## 기준 SHA

- `origin/main` = `50e14d9bdd348df2ab102740c3c6c48c51a94794`(fetch 뒤 다시 확인). 레포 파일은 `git show 50e14d9:<path>` 로만 읽었다.

---

## Step 0 — 사전 확인 (세 전제 모두 성립)

| # | 전제 | 관측 | 판정 |
|---|---|---|---|
| P1 | `pages_measured.tsv` 741 행, IMAGE 621 · VECTOR 0 · BLANK 27 · OTHER 93 | 그대로 | 성립 |
| P2 | 167 PDF 가 scratch 에 있고 sha256 이 corpus.tsv 와 같다 | **scratch 에 없었다** — 직전 조사 끝에 지웠다(`report_hb_flagged/README.md`). corpus.tsv URL 에서 한 번씩 다시 받았다: 순차, 매 요청 뒤 3 초, 167 건 전부 200·`application/pdf`(`fetch.log`). **sha256 167/167 일치** | 성립 |
| P3 | pypdf 5.4.0, pypdfium2 5.14.0 | 둘 다 그 버전으로 받았다(pillow 11.3.0) | 성립 |

---

## 규칙 변경 (D1, 실행 전에 고정)

- 경로 구성 연산자(m l c v y h re) 뒤에 `W` 또는 `W*` 가 오고 이어 `n` 으로 끝나는 경로(클립만, 칠하지 않음)는 경로 연산자 합계에서 뺀다. 그 구성 연산자와 `n` 을 모두 뺀다.
- `W` 뒤 칠하기(S s f F f* B B* b b*)로 끝나는 경로는 센다.
- 나머지 측정·분류 규칙·임계는 `report_hb_flagged` 그대로다.
  - IMAGE: 표시 면적 ≥ 25% 인 이미지.
  - VECTOR: 경로 ≥ 500.
  - BLANK: 이미지 없음 + 경로 < 50.
  - OTHER: 나머지.
- 741 쪽 전부에 적용했다(`reclassify.py`).

---

## 재분류와 표본 검증 (Step 1)

| 옛 → 새 | 쪽 |
|---|---|
| BLANK → BLANK | 27 |
| IMAGE → IMAGE | 621 |
| OTHER → BLANK | **89** |
| OTHER → OTHER | 4 |

**새 분류: IMAGE 621 · VECTOR 0 · BLANK 116 · OTHER 4.**

- OTHER 4 쪽:
  - 2024 Nr. 133 p3: 경로 154 → 84.
  - 2021 Nr. 45 p2: 경로 491 → 183, 이미지 181 개(각 1.6%).
  - 2024 Nr. 97 p2: 경로 → 0, 이미지 20.5%.
  - 2022 Nr. 104 p13: 경로 → 0, 이미지 18.2%.
- 마지막 둘은 클립을 빼면 경로가 0 이지만 이미지가 있어 BLANK 가 아니다.
- **검색 불가 쪽(새 분류에서 BLANK 아님): 625 쪽, 57 파일.**

표본(`sample_list.tsv`): 시드 **20261007**, 분류마다 정렬 뒤 `random.Random(seed).sample` 로 최대 10 쪽, 100 dpi. 렌더는 판정 뒤 지웠다. 판정(`sample_check.tsv`):

| 분류 | 표본 | 판정 |
|---|---|---|
| BLANK | 10 | **10/10 일치** — 쪽 머리와 짧은 본문(시행 조항·서명)뿐이다. 이미지·도형 없음 |
| IMAGE | 10 | **10/10 일치** — 본문 영역이 래스터다(스캔 쪽·손 서명·지도·표). 텍스트층에 없는 내용이 보인다 |
| OTHER | 4(전부) | **3 일치, 1 불일치** |

- OTHER 판정:
  - 2024 Nr. 133 p3: 가벼운 벡터 표 → 일치.
  - 2022 Nr. 104 p13: 쪽의 약 1/5 래스터 → 일치.
  - 2024 Nr. 97 p2: 쪽 폭 지도, 높이 약 1/4 → 일치.
  - **2021 Nr. 45 p2: 쪽의 약 절반을 덮는 래스터 지도로 보인다.** 이미지가 가는 띠 181 개로 나뉘어 있고 띠마다 25% 미만이라 OTHER 가 됐다. 보이는 모습은 IMAGE 다 → **불일치.**
- [추론] 이 불일치는 그 쪽이 검색 불가 쪽(BLANK 아님)이라는 사실은 바꾸지 않는다. 다만 지시(「A mismatch in any class: … do not start Step 4」)에 따라 Step 4 를 시작하지 않았다.

---

## 클립 아닌 OTHER 두 쪽

| 쪽 | 새 분류 | 보이는 것 | 텍스트층에 없는 읽을 수 있는 글자 |
|---|---|---|---|
| 2024 Nr. 133 p3 | OTHER(경로 84, 이미지 없음) | 벡터 표 한 개 — 머리 칸에 음영, 칸 선. 칸 글자 「Nummer」 「Gebührentatbestand」 「Gebührensatz in Euro」 「Entscheidung darüber obliegt der zuständigen Behörde.」 | **없음** — 텍스트층과 같은 글자다 |
| 2021 Nr. 45 p2 | OTHER(경로 183, 이미지 181 띠) | 래스터 지도(쪽의 약 절반) — 범례·축척 막대·방위표·제목 칸. 텍스트층은 쪽 머리와 「Anlage Leinenzwang im Park links der Weser (zu § 6 Absatz 3 Satz 1)」 뿐이다 | **있음** — 지도 안의 지명·범례·제목 칸 글자(예: 제목 칸 「Anlage 1 zu § 6 Abs. 3 des Ortsgesetzes über die öffentliche Ordnung Park links der Weser」, 「Übersichtsplan」). 분류 확인을 위한 관찰이다. 법 내용으로 쓰지 않았다 |

---

## G/R 규칙 (실행 전에 고정, `structure.py` 머리 주석이 정본)

- 대상: 검색 불가 쪽이 하나라도 있는 파일 57 개.
- 공통: 텍스트층 정규화는 줄 끝 하이픈 잇기 → 공백 축약 → casefold.
- G1–G4 가 모두 충족일 때만 **G** 다. 하나라도 불충족·판정 불가면 **R** 이다.

**G1 — 제목**
- 목록 제목과 텍스트층을 둘 다 `[0-9a-zäöüß]` 만 남겨 비교한다. 제목 전체가 텍스트층의 부분 문자열이어야 한다.

**G2 — 실행부와 서명 줄**
- 실행부 꼴(유형별):
  - 법령형(Gesetz·Ortsgesetz·Zustimmungsgesetz·Verordnung·unclear): `artikel N`/`§ N` 구조와 시행 조항 `tritt … in kraft`.
  - Berichtigung: `ist wie folgt zu berichtigen`/`zu ergänzen`.
  - Bekanntmachung: `gibt … bekannt`/`bekannt gemacht`.
  - Vertrag: `vereinbar…`/`schließen … Vertrag`.
- 서명 줄 꼴: `Bremen|Bremerhaven, (den) D. Monat YYYY` 뒤 150 자 안에 서명 주체 — der Senat·Senator(in)·Senatskanzlei·Magistrat·Bürgermeister·Präsident·Vorstand·Rektor·Minister.
- 「서명 쪽」 은 실행부 표지 뒤 첫 서명 줄이 있는 쪽이다.

**G3 — 위치와 부속 언급**
- 검색 불가 쪽 전부가 서명 쪽보다 뒤에 있어야 한다.
- 서명 쪽까지의 텍스트층에 부속 낱말이 있어야 한다. 부속 낱말(우선순위 순서): ersichtliche Fassung · beigefügt · angefügt · Anlage · Anhang · Staatsvertrag · Abkommen · Vertrag.
- 우선순위 첫 낱말의 문장과 쪽을 기록한다.

**G4 — Feiertagsgesetz 아님**
- 부속 낱말과 `feiertag|113-c|sonn-` 이 함께 든 문장이 없어야 한다.
- 「… die aus dem Anhang/der Anlage … ersichtliche Fassung」 의 주어를 기록한다.

---

## G/R 결과

### v1 — 정본(고정 규칙 그대로 실행)

| 그룹 | 파일 | 검색 불가 쪽 |
|---|---|---|
| **G** | **36** | **558** |
| **R** | **21** | **67** |

- G 36 파일의 유형: Zustimmungsgesetz 21 · Berichtigung 5 · Verordnung 6 · Ortsgesetz 1 · Vertrag 1 · unclear 2 · Gesetz 0.
- 유형 전체 57 파일: Zustimmungsgesetz 22 · Verordnung 12 · Ortsgesetz 10 · Gesetz 5 · Berichtigung 5 · unclear 2 · Vertrag 1.
- G4 불충족은 0 이다. Feiertag·113-c·sonn- 과 부속 낱말이 함께 든 문장은 57 파일 텍스트층 어디에도 없다.
- 「Fassung」 기록:
  - 2023 Nr. 65: 「die Anlage 6 erhält …」(Bremisches Besoldungsgesetz).
  - 2023 Nr. 37: 「Haushaltsplan … Gesamtplan erhält …」.
  - 나머지는 `files_structure.tsv` G4 열.

### v1 의 결함과 v2(참고)

- R 21 파일 중 19 개가 G2 불충족이다. 원인은 대부분 **시행 조항 정규식 `tritt[^.]{0,200}?in kraft` 의 구현 결함**이다. 날짜 「am 1. Januar 2022」 의 마침표에서 끊겨 실제 시행 조항을 놓쳤다.
  - 예: 2021 Nr. 133 「Dieses Gesetz tritt vorbehaltlich des Absatzes 2 am 1. Januar 2022 in Kraft.」
  - 예: 2023 Nr. 65 「… am 1. Juni 2023 in Kraft.」
  - 시행 조항을 못 찾으면 서명 줄을 찾을 기준점이 없어 G3 도 함께 불충족이 된다.
- 규칙(「시행 조항이 있어야 한다」)은 바꾸지 않고, 정규식만 숫자 바로 뒤 마침표를 허용하도록 고친 **v2** 를 따로 돌렸다(`structure_v2.py`, 차이는 그 한 줄).
  - v2: **G 51 파일 / 616 쪽, R 6 파일 / 9 쪽.** v1→v2 에서 R→G 로 옮긴 파일은 15 개다.
  - 고정 규칙을 실행 뒤 손댄 결과이므로 **정본은 v1** 이다. v2 를 쓸지는 판단 요청 1 이다.
- 증거 문장 감사(손 확인, G 판정을 바꾸지 않음):
  - 우선순위 첫 낱말이 합성어로 잡힌 경우가 둘이다.
    - 2020 Nr. 170: 「Anlagenüberwachung」. 같은 쪽에 「Staatsvertrag」 언급이 있다.
    - 2025 Nr. 103: 「Treppenanlage」. p2 에 「im Maßstab 1 : 35 000 (Anlage 1)」 이 있다.
  - 2021 Nr. 45 의 첫 낱말은 「angefügt」(문장 추가 지시)다. 같은 쪽에 「Dem Ortsgesetz wird folgende Anlage angefügt」 가 있다.
  - Zustimmungsgesetz 21 개의 부속 증거는 제목 속 「Staatsvertrag」 다. 규칙 문면(「names at least one attachment (… Staatsvertrag …)」)대로 충족으로 셌다.

---

## 그룹 R (Step 3)

**v1(정본) R 21 파일 / 67 쪽**

| 파일 | 유형 | 불충족 | 검색 불가 쪽 |
|---|---|---|---|
| 2020 Nr. 160 | Ortsgesetz | G2·G3 | p8 |
| 2021 Nr. 125 | Verordnung | G2·G3 | p3 |
| 2021 Nr. 133 | Gesetz | G2·G3 | p5 |
| 2022 Nr. 92 | Ortsgesetz | G2·G3 | p13 |
| 2022 Nr. 114 | Zustimmungsgesetz | G2·G3 | p2–6 |
| 2022 Nr. 145 | Ortsgesetz | G2·G3 | p4–5 |
| 2022 Nr. 146 | Ortsgesetz | G2·G3 | p4–5 |
| 2022 Nr. 147 | Ortsgesetz | G2·G3 | p2 |
| 2023 Nr. 37 | Ortsgesetz | G2·G3 | p3 |
| 2023 Nr. 65 | Gesetz | G2·G3 | p7–12 |
| 2023 Nr. 95 | Gesetz | G2·G3 | p3 |
| 2023 Nr. 106 | Verordnung | G2·G3 | p8–13 |
| 2024 Nr. 39 | Verordnung | G2·G3 | p2–3 |
| 2024 Nr. 43 | Verordnung | G2·G3 | p2–3 |
| 2024 Nr. 97 | Ortsgesetz | G3 | p2 |
| 2025 Nr. 127 | Verordnung | G2·G3 | p26–51(26 쪽) |
| 2026 Nr. 9 | Verordnung | G3 | p6–7 |
| 2026 Nr. 31 | Gesetz | G2·G3 | p16 |
| 2026 Nr. 32 | Gesetz | G2·G3 | p17 |
| 2026 Nr. 51 | Ortsgesetz | G2·G3 | p4–5 |
| 2026 Nr. 90 | Ortsgesetz | G2·G3 | p4–5 |

- 유형별 R: Verordnung 6 파일 / 39 쪽 · Ortsgesetz 9 / 13 · Gesetz 5 / 10 · Zustimmungsgesetz 1 / 5.
- **R 합계 67 쪽 > 60. 그리고 Step 1 불일치가 있다. 지시대로 여기서 멈췄다.**

**v2(참고) R 6 파일 / 9 쪽** — v2 에서도 R 로 남는 이유:

| 파일 | 불충족 | 이유(관측) | 쪽 |
|---|---|---|---|
| 2021 Nr. 125 | G2·G3 | 서명 「Bremen, den 19. November 2021 Ordnungsamt Bremen」 — 「Ordnungsamt」 가 서명 주체 목록에 없다 | p3 |
| 2024 Nr. 39 | G2·G3 | 시행 조항 뒤 「Der Senat」 만 있고 날짜 붙은 서명 줄이 텍스트층에 없다 | p2–3 |
| 2024 Nr. 43 | G2·G3 | 시행 조항 뒤 「Ordnungsamt Bremen」 만, 날짜 없음 | p2–3 |
| 2022 Nr. 147 | G3 | 검색 불가 p2 가 서명 쪽 p3 보다 앞 | p2 |
| 2024 Nr. 97 | G3 | 검색 불가 p2 가 서명 쪽 p2 와 같다(지도가 서명 위) | p2 |
| 2026 Nr. 9 | G3 | 검색 불가 p6–7 이 서명 쪽 p8 보다 앞 | p6–7 |

---

## Step 4 — 시작하지 않음

- 시작 조건 「Step 1 불일치 없음, R ≤ 60 쪽」 이 둘 다 성립하지 않았다.
  - Step 1 에 불일치 1 쪽이 있다(2021 Nr. 45 p2).
  - v1 R 이 67 쪽이다.
- 그래서 150 dpi 판독을 하지 않았고 `r_reading.tsv` 도 없다.
- v2 를 쓰더라도 Step 1 불일치 때문에 시작 조건은 성립하지 않는다.

---

## 계정(741 쪽 전부)

| 구분 | 쪽 | 근거 |
|---|---|---|
| BLANK(새 규칙, 표본 10/10 일치) | 116 | 측정 + 표본 |
| G — 구조적으로 닫힘(v1) | 558 | **[추론]** G1–G4 에 기댄 닫힘이다. 쪽 내용을 읽지 않았다 |
| R — Step 4 판독 | **0** | Step 4 미실시 |
| 미계정(v1 R) | **67** | 21 파일 |
| 계 | 741 | |

- 참고로 v2 를 쓰면 BLANK 116 · G 616 [추론] · 판독 0 · 미계정 9 이다.

---

## 판정표 (report_hb_fulltext 기준 재기재)

| # | 기준 | 수치 | 판정 |
|---|---|---|---|
| 1 | 코퍼스 빠짐 = 0 | 빠진 번호 0(PDF 없는 2025 Nr. 12·91 은 그대로 판단 대기) | 충족 |
| 2 | 플래그(검색 불가) 쪽 = 0 | 741 쪽(원래 정의) | **미충족** — 원래 정의대로 둔다 |
| 2′ | (별행) 계정 | BLANK 116 + G 558 [추론] + 판독 0 + **미계정 67** | 미계정이 남는다. 이것이 기준 2 를 대신할지는 사람 판단 |
| 3 | 대조군 3/3 | 3/3 | 충족 |
| 4 | A = 0 | 텍스트층 0. Step 4 판독 없음. 미계정 67 쪽은 보지 않았다 | 텍스트층에서 충족, 판독분 없음 |
| 5 | C = 0 (D2: § 12 b) 선언 포함) | 텍스트층 0. 다시 확인: 텍스트층 적중 164 건 중 「anwendbar」·「Arbeitsruhe」·「§ 12」 를 문맥에 담은 것은 1 건이다 — 2022 Nr. 62 수수료표의 다른 법 「§ 12 Satz 2」(D). Step 4 판독 없음 | 텍스트층에서 충족, 판독분 없음 |
| 6 | 2020 S. 52 법이 § 2 Abs. 1 무관 | 개정 지시 3 개 | 충족 |

- [추론] 기준 5 재확인의 한계: § 12 b) 선언이 법 이름(「… Sonn-, Gedenk- und Feiertage」)을 담으면 `feiertag` 적중으로 잡힌다. 법 이름 없이 「§ 12 Buchstabe b」 만 든 선언이 있었다면 이번 패턴으로는 잡히지 않는다.

**전체 「통과」 는 쓰지 않는다.**

---

## 사람의 판단 요청

1. **v1 과 v2.**
   - v1(정본, R 67 쪽)은 시행 조항 정규식의 구현 결함을 안고 있다.
   - v2 는 그 정규식만 고친 것이다(R 9 쪽).
   - v2 를 이후 기준으로 삼을지 정한다. 삼는다면 실행 뒤 고친 것이므로 새 조사로 다시 돌릴지도 정한다.
2. **Step 1 불일치(2021 Nr. 45 p2).**
   - 띠로 나뉜 래스터는 개별 면적 규칙으로 IMAGE 가 되지 못한다.
   - 선택지: (a) 같은 쪽 이미지 면적의 합을 쓰는 규칙으로 바꾼다. (b) 이 쪽만 IMAGE 로 본다. (c) OTHER 그대로 둔다.
   - 어느 쪽이든 이 쪽은 검색 불가 쪽이고, 그 파일(2021 Nr. 45)은 v1·v2 모두 G 다.
3. **서명 주체 목록.** 「Ordnungsamt Bremen」(2021 Nr. 125, 2024 Nr. 43)을 서명 주체로 넣을지 정한다. 이번에는 G 쪽으로 풀지 않았다.
4. **Step 4 실행.** 위 1–3 이 정해지면 R(v2 라면 9 쪽, v1 이라면 67 쪽)을 150 dpi 로 읽을지 정한다.
5. **G 의 성격.** G 558(v2 616) 쪽의 닫힘은 구조 추론이다. 그 쪽들은 Staatsvertrag 본문·지도·표·Anlagen 이고, 내용을 읽지 않았다. 이것을 기준 2 의 대체로 받아들일지 정한다.
6. **Zustimmungsgesetz 의 부속 증거.** 21 파일이 제목 속 「Staatsvertrag」 로 G3 를 충족했다. 이 문면 해석을 받아들일지 정한다.
