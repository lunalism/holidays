# HB — v1 R 쪽 시각 판독 (조사만)

- 판독 일시: 2026-10-07.
- 범위: 조사만 했다.
  - 레포·기존 `~/holidays-reports/report_hb_*` 변경 없음. 브랜치·커밋·PR 없음.
  - Codex 호출 없음. 병렬화하지 않았다(scratch 하나). 네트워크 요청 0 건.
- 재현 기록: `~/holidays-reports/report_hb_read/`(README 참조). 코퍼스 PDF 는 scratch 에 남겨 두었고 렌더는 지웠다.
- 표기: 명령 출력·원문·렌더에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- 이번 판독 결과는 모두 **「visual reading」(시각 판독)** 이다. 텍스트층 검색 결과와 구별한다.

---

## 기준 SHA

- `origin/main` = `50e14d9bdd348df2ab102740c3c6c48c51a94794`(fetch 뒤 다시 확인). 레포 파일은 읽지 않았다(이번 단계에 필요 없음).

---

## Step 0 — 사전 확인 (세 전제 모두 성립)

| # | 전제 | 관측 | 판정 |
|---|---|---|---|
| P1 | v1 R = 21 파일 / 67 쪽 | `files_structure.tsv` R 행 21, `nonsearch_pages` 합 67. **2021 Nr. 45 p2 는 R 에 없다**(2021 Nr. 45 는 v1 G) | 성립 |
| P2 | 그 파일들의 PDF 가 scratch 에 있고 sha256 이 corpus.tsv 와 같다 | 22 파일(R 21 + 2021 Nr. 45) 모두 있음, **불일치 0**. 다시 받지 않았다 | 성립 |
| P3 | pypdfium2 버전 | **5.14.0**(pillow 11.3.0) | 기록 |

---

## 읽기 집합

**68 쪽** — v1 R 67 쪽과 E3 의 2021 Nr. 45 p2(v1 G 파일의 쪽)다(`read_set.tsv`).

| 파일 | 유형 | 쪽 |
|---|---|---|
| 2020 Nr. 160 | Ortsgesetz | p8 |
| 2021 Nr. 125 | Verordnung | p3 |
| 2021 Nr. 133 | Gesetz | p5 |
| 2022 Nr. 92 | Ortsgesetz | p13 |
| 2022 Nr. 114 | Zustimmungsgesetz | p2–6 |
| 2022 Nr. 145 | Ortsgesetz | p4–5 |
| 2022 Nr. 146 | Ortsgesetz | p4–5 |
| 2022 Nr. 147 | Ortsgesetz | p2 |
| 2023 Nr. 37 | Ortsgesetz | p3 |
| 2023 Nr. 65 | Gesetz | p7–12 |
| 2023 Nr. 95 | Gesetz | p3 |
| 2023 Nr. 106 | Verordnung | p8–13 |
| 2024 Nr. 39 | Verordnung | p2–3 |
| 2024 Nr. 43 | Verordnung | p2–3 |
| 2024 Nr. 97 | Ortsgesetz | p2 |
| 2025 Nr. 127 | Verordnung | p26–51 |
| 2026 Nr. 9 | Verordnung | p6–7 |
| 2026 Nr. 31 | Gesetz | p16 |
| 2026 Nr. 32 | Gesetz | p17 |
| 2026 Nr. 51 | Ortsgesetz | p4–5 |
| 2026 Nr. 90 | Ortsgesetz | p4–5 |
| 2021 Nr. 45 (E3) | Ortsgesetz | p2 |

- 68 쪽 전부를 150 dpi 로 렌더해 읽었다.
- 지도 14 쪽은 작은 글자 때문에 300 dpi 로 다시 렌더했다. 2×2 타일로 잘라 읽었다: 2020 Nr. 160 p8, 2021 Nr. 45 p2, 2022 Nr. 92 p13, 2022 Nr. 146 p4, 2023 Nr. 95 p3, 2024 Nr. 39 p2·p3, 2024 Nr. 43 p2·p3, 2024 Nr. 97 p2, 2026 Nr. 9 p6·p7, 2026 Nr. 51 p4, 2026 Nr. 90 p4.
- 같은 래스터 세 쌍(이미지 데이터 sha256 일치)은 한쪽의 타일 넷을 읽고, 다른 쪽은 텍스트·서명이 있는 타일을 따로 봤다: 2024 Nr. 39 p2 = 2024 Nr. 43 p2, 2024 Nr. 39 p3 = 2024 Nr. 43 p3 = 2026 Nr. 9 p7.

쪽들이 담은 것(관측, 쪽별은 `r_reading.tsv`):
- **지도·도면 14 쪽**(아래 「명령 부록」 2 쪽 제외): 적용 범위 지도, BID·Innovationsbereich 구역도, 금지 구역도, 공항 필지 평면도, Leinenzwang 지도.
- **필지 표 4 쪽**: BID·Innovationsbereich 의 Gemarkung/Flurstück 목록.
- **예산 개요 4 쪽**: Haushaltsübersicht.
- **보수·학위 표 7 쪽**: 2021 Nr. 133 Anlage 6, 2023 Nr. 65 Anhang 1·2.
- **Staatsvertrag 본문과 서명 5 쪽**: 2022 Nr. 114 — Glücksspielstaatsvertrag 개정, Art. 1 §§ 8·23·27f·27h·27p·32·35, Art. 2 Inkrafttreten, 16 개 주 서명.
- **평정 서식 6 쪽**: 2023 Nr. 106.
- **Mietpreisbremse 감정서 26 쪽**: 2025 Nr. 127, FUB IGES 「Gutachterliche Expertise zum Bremer Wohnungsmarkt」.
- **명령 부록 2 쪽**: 2021 Nr. 125 Anlage 지도, 2023 Nr. 95 Anlage 지도와 정류장 목록.
- 합: 14 + 4 + 4 + 7 + 5 + 6 + 26 + 2 = 68.

---

## 판독 결과(findings) — visual reading

| 찾은 것 | 쪽 수 |
|---|---|
| Sonn- (Gedenk-) und Feiertagsgesetz 를 이름으로 든 개정 지시 | **0** |
| § 12 b) 선언, 또는 어떤 날을 주 전역 공휴일·일반 Arbeitsruhe 날로 정하는 선언 | **0** |
| Feiertag · Gedenk · 113-c · Reformationstag · einmalig 의 출현 | **0** |

- 분류: **A 0 · B 0 · C 0 · D 0**. 판독에서 분류할 적중이 없어 [추론] 분류도 없다.
- 참고(적중 아님): 2022 Nr. 114 p4 의 「einmal im Monat」(Staatsvertrag 개정 § 27p 문맥)는 「einmalig」 이 아니다. 패턴 정의(부분 문자열 `einmalig`)에 맞지 않는다.
- **「partly unreadable」 7 쪽**은 300 dpi 타일로도 일부 글자를 읽지 못했다. 「읽음」 으로 세지 않는다.
  - 2020 Nr. 160 p8 — 지도 안의 거리 이름 라벨.
  - 2021 Nr. 45 p2 — 바탕 지형도의 작은 라벨 일부.
  - 2022 Nr. 92 p13 — 바탕 지형도의 작은 지명·도로 라벨.
  - 2024 Nr. 39 p2 — 옛 시가도의 빗금 구역 안 작은 라벨.
  - 2024 Nr. 43 p2 — 2024 Nr. 39 p2 와 같은 래스터, 같은 영역.
  - 2026 Nr. 9 p6 — 옛 시가도의 빗금 구역 안 작은 라벨.
  - 2024 Nr. 97 p2 — 평면도 안 필지 목록 표와 측량사 도장 칸.
  - 일곱 쪽 모두 제목·범례·표제란·시행 조항·서명은 읽혔다.
- [추론] 읽지 못한 영역은 지도 바탕의 지명·거리명·필지 번호다. 개정 지시나 선언이 들어갈 자리로 보이지 않는다. 다만 이 판단으로 그 영역을 「읽음」 으로 바꾸지 않는다(판단 요청 1).

---

## 계정(741 쪽 전부)

| 구분 | 쪽 | 근거 |
|---|---|---|
| BLANK(새 규칙, 표본 검증) | 116 | `report_hb_structure` |
| G(v1) — 구조적으로 닫힘 | 557 | **[추론]** G1–G4 에 기댄 닫힘. v1 G 558 에서 이번에 따로 판독한 2021 Nr. 45 p2 를 뺀 수 |
| 이번에 읽음(visual reading, 전부 읽힘) | 61 | v1 R 67 − partly unreadable 6 |
| partly unreadable | 7 | R 6 + E3 1(2021 Nr. 45 p2) |
| 미계정 | **0** | |
| 계 | 741 | 116 + 557 + 61 + 7 |

---

## 판정표 (report_hb_fulltext 기준 재기재)

| # | 기준 | 수치 | 판정 |
|---|---|---|---|
| 1 | 코퍼스 빠짐 = 0 | 빠진 번호 0(PDF 없는 2025 Nr. 12·91 은 판단 대기 그대로) | 충족 |
| 2 | 플래그(검색 불가) 쪽 = 0 | 741 쪽(원래 정의) | **미충족** — 원래 정의대로 둔다 |
| 2′ | (별행) 계정 | BLANK 116 + G 557 [추론] + 판독 61 + **partly unreadable 7** + 미계정 0 | 미계정 0. 다만 G 는 추론이고 7 쪽은 일부를 읽지 못했다. 이것이 기준 2 를 대신할지는 사람 판단 |
| 3 | 대조군 3/3 | 3/3 | 충족 |
| 4 | A = 0 | 텍스트층 0 + 시각 판독 0 = **0** | 충족(읽은 범위 안에서 — G 557 쪽은 읽지 않았고 7 쪽은 일부 미판독) |
| 5 | C = 0 (D2: § 12 b) 선언 포함) | 텍스트층 0 + 시각 판독 0 = **0** | 충족(같은 범위 한정) |
| 6 | 2020 S. 52 법이 § 2 Abs. 1 무관 | 개정 지시 3 개: 표제, I. Abschnitt 표제, § 7a | 충족 |

- 최종 A / B / C(텍스트층 + 판독): **A 0 · B 11 · C 0**.
  - B 11 은 모두 텍스트층의 2020 Nr. 12 다(표제·I. Abschnitt 표제·§ 7a). 판독에서 더해진 것은 없다.

**전체 「통과」 는 쓰지 않는다.**

---

## 사람의 판단 요청

1. **partly unreadable 7 쪽.**
   - 읽지 못한 것은 지도 바탕의 작은 라벨뿐이다.
   - 선택지:
     - (a) 이 정도를 「읽음」 으로 받아들인다.
     - (b) 원본 지도 출처(GeoInformation Bremen 등)로 확인한다.
     - (c) 미계정으로 남긴다.
2. **G 557 쪽의 성격.** 구조 추론(G1–G4)으로 닫았고 내용은 읽지 않았다. 지난 보고의 판단 요청 5·6(Zustimmungsgesetz 의 부속 증거 해석 포함)이 그대로 열려 있다.
3. **기준 2′ 의 채택.** 이 계정(미계정 0, 추론 557, 일부 미판독 7)을 기준 2 의 대체로 받아들여 HB 구현으로 넘어갈지 정한다.
