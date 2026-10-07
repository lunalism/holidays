# HB — 검색 불가 플래그 쪽 741 개의 분류 (OCR 없이, 조사만)

- 측정 시점: 2026-10-06(UTC, 요청 15:16:20Z–15:35:51Z).
- 범위: 조사만 했다. 레포·`~/holidays-reports/report_hb_fulltext*` 변경 없음, 브랜치·커밋·PR 없음, Codex 호출 없음. 병렬화하지 않았다(scratch 하나).
- 재현 기록: `~/holidays-reports/report_hb_flagged/`(README 참조).
- 표기: 명령 출력·원문에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- **결과 요약: Step 2 표본 검증에서 OTHER 분류가 보이는 모습과 맞지 않았다. 지시대로 Step 6(남는 집합) 전에 멈췄다.** Step 3–5 는 Step 6 이전 단계라 수행했다.

---

## 기준 SHA

- `origin/main` = `50e14d9bdd348df2ab102740c3c6c48c51a94794`(fetch 뒤 다시 확인). 레포 파일은 `git show 50e14d9:<path>` 로만 읽었다.

---

## Step 0 — 사전 확인 (세 전제 모두 성립)

| # | 전제 | 관측 | 판정 |
|---|---|---|---|
| P1 | `flagged_pages.txt` 741 쪽 / 167 파일 | 741 줄(머리 제외), 서로 다른 파일 167 | 성립 |
| P2 | 167 파일 PDF 가 scratch 에 있고 sha256 이 corpus.tsv 와 같다 | **scratch 에 없었다** — 직전 조사 끝에 scratch 를 지웠다(`report_hb_fulltext/README.md` 「scratch 는 판독 뒤 지운다」). 지시대로 corpus.tsv URL 에서 한 번씩 다시 받았다: 167 요청 전부 200·`application/pdf`. **sha256·바이트 수 167/167 일치, 불일치 0** | 성립 |
| P3 | pypdf 5.4.0, 렌더러 | pypdf 5.4.0 사용 가능. 렌더러 **pypdfium2 5.14.0**(PDFium 156.0.8076.0) + pillow 11.3.0 을 `uv run --with` 로 설치했다 | 성립 |

- 요청 수: 지시는 「아주 적을 것」 을 예상했지만, P2 재수령 때문에 168 건이 됐다(167 + Step 4 1). 간격은 매 요청 뒤 3 초 이상이었다. `fetch.log` 에 전부 있다.

---

## 분류 규칙 (실행 전에 고정, 실행 뒤 바꾸지 않음)

쪽마다 내용 스트림을 걷고 Form XObject 안으로 재귀했다(`measure.py`).

- **이미지 XObject**: 개수, 픽셀 W×H, 표시 면적 / MediaBox 면적. 표시 면적은 `Do` 시점 CTM 의 |a·d − b·c| 로 구했다. CTM 을 풀지 못하면 「unknown」 으로 둔다.
- **경로 연산자 수**: m l c v y h re S s f F f* B B* b b* n
- **텍스트 표시 연산자 수**: Tj TJ ' "

| 분류 | 조건 |
|---|---|
| IMAGE | 표시 면적 ≥ 25% 인 이미지 XObject 가 있다(면적 unknown 이면 ≥ 500×500 px) |
| VECTOR | IMAGE 가 아니고, 경로 연산자 ≥ 500 |
| BLANK | 이미지 XObject 가 없고, 경로 연산자 < 50 |
| OTHER | 그 밖 |

- 면적 unknown 인 이미지: 0. 인라인 이미지: 0(참고용, 분류에 쓰지 않음). Form XObject: 172 회 재귀.

---

## 분류 분포와 임계 근처

| 분류 | 쪽 | 파일 |
|---|---|---|
| IMAGE | **621** | 54 |
| VECTOR | **0** | 0 |
| BLANK | **27** | 27 |
| OTHER | **93** | 93 |
| 계 | 741 | 167(겹침 있음) |

- IMAGE 621 쪽의 최대 표시 면적은 25.4%–68.9%, 이미지 픽셀의 최소 변은 400 px 이상이다.
- 직전 보고의 「쪽 머리만 있는 쪽」 598 개와의 대응(`report_hb_fulltext/flagged_pages_split.tsv`):
  - IMAGE 597 쪽이 쪽 머리만 있는 쪽이다.
  - 나머지 1 쪽은 OTHER 인 2022 Nr. 104 p13 이다(이미지 919×430, 18.2%).
  - 본문 텍스트가 조금 있는 쪽 143 개는 IMAGE 24 · BLANK 27 · OTHER 92 로 나뉜다.

**임계 ±20% 안의 쪽: 254 개.** 기준: 이미지 면적 20–30%, 경로 연산자 40–60 또는 400–600. 면적 unknown 인 이미지가 없어 px 임계는 해당 없다.
- 254 개 대부분은 IMAGE 쪽의 경로 연산자가 40–60 에 든 경우다. 이 경우 IMAGE 판정이 먼저 정해져 분류에 영향이 없다.
- 임계를 하나씩 ±20% 옮기면 분류가 바뀌는 쪽(`sensitivity.py`, 보고용 — 분류는 바꾸지 않았다):

| 바꾼 임계 | 바뀌는 쪽 |
|---|---|
| 면적 0.20 | 1 (2024 Nr. 97 p2 OTHER→IMAGE, 20.5%) |
| 면적 0.30 | 8 (IMAGE→OTHER: 2025 Nr. 114 p6, 2025 Nr. 23 p2, 2024 Nr. 103 p15·26·36, 2022 Nr. 145 p5, 2022 Nr. 84 p3, 2021 Nr. 134 p12) |
| px 400 / 600 | 0 / 0 |
| VECTOR 400 / 600 | 1 (2021 Nr. 45 p2 OTHER→VECTOR, 491) / 0 |
| BLANK 40 / 60 | 4 (BLANK→OTHER) / **37 (OTHER→BLANK)** |

---

## 표본 검증 (Step 2) — **OTHER 불일치, Step 6 전에 멈춤**

- 렌더러: pypdfium2 5.14.0. 100 dpi. 시드 **20261006**. 분류마다 (file, page) 를 정렬한 뒤 `random.Random(seed).sample` 로 최대 10 쪽을 뽑았다. VECTOR 는 0 쪽이라 표본이 없다.
- 목록: `sample_list.tsv`. 판정: `sample_check.tsv`. 이미지는 scratch 에만 두었다가 지웠다. 법 내용은 판정에 쓰지 않았다.

| 분류 | 표본 | 보이는 것 | 판정 |
|---|---|---|---|
| BLANK | 10 | 쪽 머리와 짧은 본문 몇 줄(조문 끝·서명 형태). 이미지·도형 없음 | 10/10 일치 |
| IMAGE | 10 | 쪽 머리 아래 본문 영역이 래스터다(스캔된 쪽·손 서명·지도·외부 보고서 쪽). 측정된 이미지 영역에 텍스트층에 없는 내용이 보인다 | 10/10 일치 |
| OTHER | 10 | 쪽 머리와 짧은 본문 몇 줄. 이미지·도형이 보이지 않는다 — **BLANK 표본과 모습이 구별되지 않는다** | **10/10 불일치** |

불일치의 측정상 원인(`op_breakdown.tsv`, 관측):
- BLANK 27 쪽 전부: 경로 연산자가 클립 쌍 `re … W* n` 뿐이다. `re` 수는 0–24 다.
- OTHER 93 쪽 중 91 쪽: 경로 연산자가 클립 쌍 `re … W* n` 뿐이다(`re` = `n` = `W*`). `re` 수는 21–82 다.
  - 이 91 쪽 중 89 쪽은 이미지가 없다.
  - 2 쪽(2024 Nr. 97 p2 20.5%, 2022 Nr. 104 p13 18.2%)은 25% 미만 이미지가 있다.
- 따라서 BLANK/OTHER 경계(경로 연산자 50)는 눈에 보이지 않는 클립 사각형의 개수다.
- 클립 쌍이 아닌 경로가 있는 OTHER 는 2 쪽뿐이다(둘 다 표본에 들지 않았다):
  - 2024 Nr. 133 p3: re 77, f* 42.
  - 2021 Nr. 45 p2: m 23 · l 110 · S 15 · re 164 등 491 개, 이미지 181 개(각 1164×52 px, 각 1.6%).
- [추론] 이 OTHER 91 쪽 대부분은 BLANK 처럼 텍스트층이 보이는 글자를 다 담은 쪽이다. 표본 10 쪽 밖은 보지 않았다.

지시(「Any mismatch: report it and stop before Step 6」)에 따라 **남는 집합(`remaining_set.tsv`)을 만들지 않았다.** 규칙도 고치지 않았다.

---

## 규범 유형 (Step 3)

- 167 파일에 목록 제목(Hinweistext)을 붙였다. 유형은 제목 문면만으로 정했다(`norm_type.py` 규칙 R1–R11, `norm_types.tsv`).

| 유형 | 파일 |
|---|---|
| Verordnung | 61 |
| Gesetz | 46 |
| other(Ortsgesetz) | 26 |
| Zustimmungsgesetz zu Staatsvertrag | 22 |
| Berichtigung | **5** |
| unclear | 5 |
| Bekanntmachung | 1 |
| other(Vertrag) | 1 |
| Satzung | 0 |

- **unclear 5**:
  - 2021 Nr. 21 「Fortbildungsprüfungsregelung nach § 54 des Berufsbildungsgesetzes …」
  - 2023 Nr. 42 「Gesetz zum Abkommen über die Errichtung … der Akademie für Öffentliches Gesundheitswesen」 — Abkommen 이지 Staatsvertrag 라고 쓰지 않음
  - 2024 Nr. 133 「Gebührenordnung für Unterbringungen nach dem Aufnahmegesetz」
  - 2025 Nr. 95 「Entwurf eines Verwaltungsverfahrenseffektivierungsgesetzes」
  - 2025 Nr. 139 「Gebührenordnung für die Unterbringung … in der Stadt Bremerhaven」
- **Ortsgesetz** 는 지시의 유형 목록에 없다. 「Satzung」 으로 옮기지 않고 other(Ortsgesetz) 로 두었다.
- **other(Vertrag)**: 2022 Nr. 104 「Vertrag zwischen der Freien Hansestadt Bremen (Stadtgemeinde) und der Stadt Bremerhaven …」.
- **Bekanntmachung**: 2026 Nr. 54 「Bekanntmachung einer Entscheidung des Staatsgerichtshofs …」.
- Zustimmungsgesetz 중 2025 Nr. 109 는 제목에 「… und zur Änderung des Bremischen Landesmediengesetzes」 가 함께 있다.
- 「Haushaltsgesetz der Stadtgemeinde Bremen」(2024 Nr. 55, 2026 Nr. 31·32)은 제목 문면대로 Gesetz 다.
- **Berichtigung 은 넷이 아니라 다섯이다.** 직전 보고는 2025 Nr. 23 「Berichtigung des Gesetzblattes Nr. 18」 을 빠뜨렸다.

---

## 수권 조항 (Step 4)

- 요청 1 회: `…detail.php?gsid=bremen2014_tp.c.145882.de&template=00_html_to_pdf_d`
  - 결과: 15:35:51Z, 200, `application/pdf`, **295,467 B**(앞선 295,467 B 와 같음).
  - sha256 `9c1f5e7a085fcf3d313b8215ddfdcb417d4af68b9c3904eaa2566861bfd6b33c`.
  - 앞선 수령의 sha256 은 기록돼 있지 않아 해시 대조는 못 했다.
- 텍스트층: 8 쪽, 11,116 자. 머리 「Inkrafttreten: 14.03.2020」, 「Zuletzt geändert durch: … Geschäftsverteilung des Senats vom 02.09.2025 (Brem.GBl. S. 674)」. 각 쪽 끝에 「außer Kraft」 가 있다.
- 검색 범위: §§ 1–14 와 각주 전문(8 쪽 전부).
  - 「Verordnung」·「Rechtsverordnung」·「einmalig」 은 0 회다.
  - 「ermächtigt」 은 2 회다(§ 10 Abs. 2, § 12).
  - 「erklär」 은 1 회다(§ 12).
- **수권 조항(인용):**
  - **§ 12** 「Der Senat wird ermächtigt: a) den Tag zu bestimmen, an dem der Volkstrauertag begangen wird; b) aus besonderem Anlaß im Einzelfall Vorschriften dieses Gesetzes auch für in § 3 nicht genannte Tage ganz oder teilweise für anwendbar zu erklären.」(텍스트층에서는 a)·b) 표지가 쪽 머리 쪽으로 따로 빠져 나온다.)
    - 수단은 적혀 있지 않다(Verordnung 이라고 쓰지 않음).
    - 참고 § 3: 「Die Sonntage und die staatlich anerkannten Feiertage sind Tage allgemeiner Arbeitsruhe.」
  - § 10 Abs. 2 「Die Senatorin für Bildung und Wissenschaft wird ermächtigt, an anderen als den im § 8 genannten Feiertagen Unterrichtsbefreiung zu gewähren.」 — 수업 면제이고 공휴일 지정이 아니다. 인용만 둔다.
  - § 2 Abs. 1(a–j 목록)을 법률 아닌 수단으로 늘리는 수권 문언은 없다.
- **2020 Nr. 12**: 전사(`report_hb_fulltext/hb_2020_012_text.txt`)의 개정 지시는 셋이다 — 표제, I. Abschnitt 표제, § 7a 신설. § 7a 는 8. Mai 를 「staatlich anerkannter Gedenktag」 로 정하고 Abs. 2 는 행사 참석 기회를 정한다. 수권 문언(「ermächtigt」)은 없다. 145882 텍스트층의 § 7a 자구도 같다.
- [추론] 판정 기준과 규범 유형의 관계:
  - **기준 4(A, § 2 Abs. 1 개정)**: 법률 조문을 바꾸는 것은 법률(조항법 포함)이다.
    - 영향 가능: Gesetz, Zustimmungsgesetz(2025 Nr. 109 처럼 조항법을 겸하는 것), unclear 의 Gesetz 형, 그리고 공포 자구를 바로잡는 Berichtigung.
    - 영향 없음: Verordnung·Ortsgesetz.
  - **기준 5(C, 일회성 공휴일 지정)**:
    - 법률이 직접 정할 수 있다.
    - § 12 b) 로 Senat 가 「im Einzelfall」 이 법의 규정(§ 3 의 Arbeitsruhe 포함)을 다른 날에 적용한다고 선언할 수 있다. 그 수단은 조문에 없으므로 Verordnung·Bekanntmachung 등 법률 아닌 꼴로 실릴 수 있다.
    - Ortsgesetz(시 단위)는 주 전역 지정을 할 수 없다.
    - § 12 b) 선언이 「staatlich anerkannter Feiertag」 지정과 같은지는 법 해석이라 판단 요청 2 로 넘긴다.

---

## 2023 Nr. 65 (Step 5)

- 「Gesetz zur Änderung dienstrechtlicher Vorschriften Vom 2. Mai 2023」, 공포 19.05.2023, 12 쪽.
- 플래그 쪽 6 개(p7–p12)는 전부 **IMAGE**다. 각 쪽에 1656×2339 px 이미지 하나가 있다. 면적은 p8 이 68.1%, 나머지가 58.0% 다.
- 텍스트층 p1–p6 의 Artikel 구조:

| Artikel | 표제 | 개정 대상 |
|---|---|---|
| 1 | Änderung des Bremischen Beamtengesetzes | Bremisches Beamtengesetz vom 22.12.2009 — § 80(Abs. 6·9·10), § 111 |
| 2 | Änderung des Bremischen Beamtenversorgungsgesetzes | Bremisches Beamtenversorgungsgesetz vom 4.11.2014 — § 64(Abs. 10·11), § 83 |
| 3 | Änderung des Bremischen Besoldungsgesetzes | Bremisches Besoldungsgesetz vom 20.12.2016 — § 15, § 28, § 35, Anlage I, Anlage III, Nr. 6 「Die Anlage 6 erhält die aus dem Anhang 1 zu diesem Gesetz ersichtliche Fassung.」 |
| 4 | Änderung der Bremischen Laufbahnverordnung | Bremische Laufbahnverordnung vom 9.3.2010 — Anlage 1 Tabelle 「… die aus dem Anhang 2 zu diesem Gesetz ersichtliche Fassung」 |
| 5 | Inkrafttreten | Abs. 1–5. 이어 「Bremen, den 2. Mai 2023 Der Senat」 |

- **Artikel 1–5 의 표제·개정 지시·Inkrafttreten·서명은 모두 텍스트층 쪽(p1–p6)에 있다. IMAGE/VECTOR/OTHER 쪽에 놓인 Artikel 구조는 없다.**
- 텍스트층은 Sonn- und Feiertage 법을 개정 대상으로 들지 않는다.
- [추론] p7–p12 는 Art. 3 Nr. 6 의 「Anhang 1」 과 Art. 4 의 「Anhang 2」 다. 텍스트층이 그 두 부속을 가리키고 그 뒤에 IMAGE 쪽만 남기 때문이다. 이미지 내용은 읽지 않았다.

---

## Berichtigungen (Step 5)

| 호 | 대상(텍스트층) | 대상 제목(목록) | 바로잡는 것(텍스트층) | 본문 위치 |
|---|---|---|---|---|
| 2024 Nr. 76(5.7.2024) | Gesetzblatt Nr. 70, 「Gesetz zu dem Fünften Medienänderungsstaatsvertrag」, 5.7.2024 | 2024 Nr. 70 「Gesetz zu dem Fünften Medienänderungsstaatsvertrag」(S. 538) | 「Dem Gesetz wird der nachfolgend angehängte Staatsvertrag als Anhang hinzugefügt.」 | 지시는 p1(텍스트층). 붙인 Staatsvertrag 는 p2–p8, 전부 IMAGE |
| 2024 Nr. 101(12.10.2024) | Gesetzblatt Nummer 99, 「Gesetz zur Zustimmung zum Zweiten Staatsvertrag zur Änderung des IT-Staatsvertrags」, 10.10.2024 | 2024 Nr. 99 같은 제목(S. 719) | 「… wird der nachfolgend angehängte „Zweite Staatsvertrag zur Änderung des IT-Staatsvertrags“ angefügt.」 | 지시 p1. 부속 p2–p6, 전부 IMAGE |
| 2024 Nr. 103(12.10.2024) | Gesetzblatt Nummer 100, 「Gesetz zur Anpassung der Besoldungs- und Beamtenversorgungsbezüge 2023, 2024 und 2025 … sowie zur Änderung dienstrechtlicher Vorschriften」, 10.10.2024 | 2024 Nr. 100 같은 제목(S. 720–729) | 「Dem Gesetzblatt Nummer 100 werden die nachfolgend angehängten Anlagen angefügt.」 | 지시 p1. 부속 p2–p36(35 쪽), 전부 IMAGE |
| 2025 Nr. 159(19.12.2025) | 「Ortsgesetz über die Errichtung eines Sondervermögens Hafen sowie zur Änderung des Haushaltsgesetzes der Freien Hansestadt Bremen (Stadtgemeinde) für das Haushaltsjahr 2002」, 26.3.2002(Brem.GBl. 2002 S. 44) | **목록 범위 밖** — 받아 둔 목록 11 쪽은 2019 Nr. 96 까지만 닿는다. 더 받지 않았다 | 「… ist um die hier beigefügte Anlage vom 18. Januar 2002, bezeichnet als Anlage 1 (bestehend aus Anlage 1.1 und 1.2), zu ergänzen.」 | 지시 p1. 부속 p2–p3, 전부 IMAGE |
| (추가) 2025 Nr. 23(26.3.2025) | Gesetzblatt Nummer 18, 「Ortsgesetz zur Änderung des Ortsgesetzes über die öffentliche Ordnung」(BremGBl. S. 52), 21.3.2025 | 2025 Nr. 18 같은 제목(S. 52–53) | 「Dem Gesetzblatt Nummer 18 wird die beigefügte Anlage angefügt.」 | 지시 p1. 부속 p2, IMAGE(26.9%) |

- 다섯 건 모두 **바로잡는 지시 자체는 텍스트층(p1)에 있다. 붙이는 부속(Staatsvertrag·Anlagen)은 모두 IMAGE 쪽에 있다.** 다섯 지시 모두 부속을 「붙인다」는 것이고, 대상 법의 조문 자구를 고치지 않는다.
- 대상 호 2024 Nr. 70·99·100, 2025 Nr. 18 은 플래그 파일이 아니다(텍스트층 있음).
- [추론] 다섯 대상은 Medienänderungs-StV·IT-StV·공무원 보수·Sondervermögen Hafen·Bremen 공공질서 Ortsgesetz 다. 어느 것도 제목상 Sonn- und Feiertagsgesetz 가 아니다. 부속 내용은 읽지 않았다.

---

## 남는 집합 (Step 6) — **수행하지 않음**

Step 2 에서 OTHER 표본 10/10 이 불일치였다. 지시에 따라 멈췄다. `remaining_set.tsv` 는 만들지 않았다.
참고로 정의상 남는 집합(IMAGE + VECTOR + OTHER)의 크기는 Step 1 수치로 714 쪽(621 + 0 + 93)이다. 다만 OTHER 93 의 분류가 검증을 통과하지 못했으므로 이 수를 남는 집합으로 쓰지 않는다.

---

## 사람의 판단 요청

1. **OTHER 분류의 처리(Step 6 재개 조건).** OTHER 93 쪽 중 91 쪽은 경로 연산자가 보이지 않는 클립 `re W* n` 뿐이다. 표본 10 쪽은 BLANK 와 같은 모습이었다. 선택지:
   - (a) 규칙을 바꾼다 — 예: 클립 경로(`W`/`W*` 뒤 `n`)를 경로 연산자에서 뺀다. 고정 규칙을 실행 뒤 바꾸는 것이니 새 조사로 한다.
   - (b) OTHER 를 그대로 남는 집합에 넣는다(과대 계상을 받아들임).
   - (c) OTHER 를 따로 렌더 확인한다.
   - 클립 쌍이 아닌 경로가 있는 OTHER 2 쪽(2024 Nr. 133 p3, 2021 Nr. 45 p2)은 어느 경우든 따로 봐야 한다 [추론].
2. **§ 12 b) 의 의미.** 「aus besonderem Anlaß im Einzelfall Vorschriften dieses Gesetzes auch für in § 3 nicht genannte Tage … für anwendbar zu erklären」 은 수단을 적지 않는다. 이것을 기준 5(C)의 「일회성 공휴일 지정」 경로로 볼지, 그래서 Verordnung·Bekanntmachung 유형을 C 검사 대상에 넣을지 정한다.
3. **IMAGE 621 쪽(54 파일)의 처리.** 표본 10/10 일치. OCR 여부는 사람이 정한다.
   - 근거(Step 5): 2023 Nr. 65 와 Berichtigung 다섯 건은 Artikel 구조·바로잡는 지시가 텍스트층에 있고, 부속만 IMAGE 다.
   - 이것을 다른 IMAGE 파일에 일반화하지 않았다.
4. **Berichtigung 다섯째(2025 Nr. 23).** 직전 보고(`report_hb_fulltext.md`)는 넷만 들었다. 그 보고는 기록이라 고치지 않았다. 이후 정정을 어디에 적을지 정한다(레포로 옮길 때 폴더 README 정정 절 — `docs/research/README.md` 「이차 기록이다」).
5. **2025 Nr. 159 의 대상 2002 Nr. 8.** 목록 범위 밖이라 제목을 목록에서 확인하지 못했다. 텍스트층의 대상 표기만 있다. 목록을 더 받을지 정한다.
6. **145882 해시.** 이번 sha256 은 기록했지만 앞선 수령의 해시가 없어 같은 파일인지는 바이트 수로만 확인했다.
