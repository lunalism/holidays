# report_sn_prep — 재현 기록

`report_sn_prep.md`(이 폴더의 상위 `~/holidays-reports/`)의 요청 로그·스크립트·추출 텍스트·비교표·초안이다.
- 조사는 2026-11-18(UTC 06:51:53Z–07:40:28Z), `origin/main` `38c8db2e409c50d270985f144e9c13152213d94f` 에서 했다.
- 병렬화하지 않았다(scratch 하나). 레포 파일은 고치지 않았다(브랜치·커밋·PR 없음). Codex 호출 없음.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- 레포의 의존을 그대로 썼다: `uv run`(playwright 1.62.0, chromium headless shell 151.0.7922.34, holidays 0.102).
- PDF 는 `uv run --no-project --with 'pypdf==5.4.0'`(관보 미리보기는 빈 비밀번호 AES — `--with 'cryptography==44.0.2'`),
  렌더는 `--with 'pypdfium2==5.14.0' --with 'pillow==11.3.0'`.

| 파일 | 무엇 |
|---|---|
| `fetch.sh` → `fetch.log` | 요청 도우미(`report_mv_retry/fetch.sh` 와 같다 — 식별 UA, 3 초 간격, 5xx 재시도 한 번)와 요청 기록 325 줄. 렌더(playwright)는 사람이 여는 화면 URL 한 줄씩만 적는다 |
| `extract_revosax.py` → `text/revosax_3997_48138_r1.txt`·`r2.txt` | A1 — REVOSax 통합본 PDF 두 번(10 초 간격)의 텍스트층과 전문·§ 1·§ 2 의 sha256. 두 파일이 같다 |
| `versions.py` → `versions.tsv` | A2 — 역사판 3997.1–.6 과 현행 화면의 유효 기간·§ 1 Abs. 1·§ 2 |
| `text/revosax_2002_art4.txt` | B — 2002 개정법 Art. 4·Art. 22(REVOSax 개정법 화면, 관보 원문 아님) |
| `render_pages.py` | 텍스트층 없는 쪽의 렌더(렌더 PNG 는 scratch 에만) |
| `text/gvbl_2025_06_S146.txt` | B — SächsGVBl. 2025 Nr. 6 S. 145(텍스트층)·S. 146(렌더 판독) |
| `text/he_gvbl_1971_I_36_S344.txt` | C2 — Hessen GVBl. 1971 I Nr. 36 S. 344 § 1(렌더 판독). Buß- und Bettag 정의와 Totensonntag 정의 |
| `text/sl_amtsbl_1976_13_S214.txt` | C2 — Saarland Amtsblatt 1976 Nr. 13 S. 214 § 2(렌더 판독). 정의 없음 |
| `text/slt_petitionsbericht_2023_p68.txt` | C2 — 작센 주의회 청원 보고서 2023, PDF 68 쪽 텍스트층 그대로 |
| `render_links.py`, `render/c_sachsen_search*.txt`·`.net.tsv` | C2 — sachsen.de 검색 두 번(결과는 JS 렌더). `report_mv_retry/render_links.py` 의 복사본 |
| `revosax_search.py` → `c_revosax_bettag.tsv`, `e_revosax_feiertag.tsv`, `render/*_revosax_*.net.tsv` | C2·E — REVOSax 빠른 검색을 렌더하고 결과 목록을 끝까지 넘긴 표 |
| `c3_compare.py` → `c3_compare.tsv` | C3 — 1990–2100 의 (a)(b)(c) 세 꼴과 python-holidays SN 2020–2031 |
| `pyholidays_sn.py` → `.out` | C3 — python-holidays 0.102 DE(subdiv='SN') 2020–2031 전체 목록 |
| `e_listing.py` → `e_listing.tsv` | E — 판매 사이트 SächsGVBl. 목록 9 쪽(25 건씩)의 호와 상품 화면 주소 |
| `e_fetch_products.sh`, `e_titles.py` → `e_titles.tsv` | E — 2020 이후 192 상품 화면과 그 「Inhaltsverzeichnis」(2024–2026 만 있음) |
| `e_fetch_previews.sh`, `e_toc.py` → `e_toc.tsv` | E — 2021 Nr. 15 – 2023 의 미리보기 PDF 89 건과 그 1 쪽 목차 |
| `e_search.py` → `e_hits.tsv`, `e_classify.py` → `e_classified.tsv` | E — 목차 제목 검색과 적중 분류(REVOSax 2020 이후 27 건 포함) |
| `drafts/` | **초안** — de_sn 표 셋(설계안 (ii)). 적용하지 않음. `drafts/README.md` |

- scratch(`<scratch>/sn/`)에 남긴 것(MV 갈래처럼 닫힐 때까지 지우지 않는다): 받은 PDF(REVOSax 통합본 둘, 관보 미리보기 90, Hessen 1971,
  Saarland 1976, 주의회 보고서), 상품 화면 192·목록 화면 HTML, 렌더 PNG·HTML. 사이트 응답 덤프·관보 PDF 라 이 폴더에 두지 않는다
  (`docs/research/README.md` 「넣지 않는 것」).
- 렌더의 하위 요청은 브라우저가 스스로 내므로 3 초 간격을 줄 수 없었다. 사람이 연 화면 사이는 3 초 이상이다.
- `recht.nrw.de` 의 GV. NW. 1989 Nr. 19 는 두 번 모두 연결 실패(000)라 받지 못했다. 보고의 NW 인용은 레포의 2026-09-29 전사다.
- 옮길 때를 위한 검색(대소문자 무시): `authenticity_token`·`_csrf`·`jsessionid`·`sid=`·`cookie`·`token=`. 적중은
  `render/c_sachsen_search*.txt` 의 쿠키 안내문과 `render/c_sachsen_search*.net.tsv` 의 etracker 측정 요청 주소(사이트 키·시각 값)뿐이다.
  세션 값은 없다. 화면 HTML 에 든 `authenticity_token` 은 scratch 의 HTML 에만 있다.

## 옮긴 기록

- 원본은 레포 밖 `~/holidays-reports/report_sn_prep.md` 와 `~/holidays-reports/report_sn_prep/` 였다. 옮긴 것은
  de_sn 구현 PR 이다(`docs/research/README.md` 「보고의 흐름」).
- 옮길 때 바꾼 것:
  - 보고 본문 한 줄(「기준 SHA와 환경」 표 E2 행)은 보고 디렉터리의 로컬 절대 경로를 적었다. 그 앞부분을
    `<local>/holidays-reports` 로 바꿨다 — 조사 기계의 볼륨 이름이라 공개 레포에 두지 않는다(`docs/research/README.md`
    「이차 기록이다」 의 가림 예외, `report_mv_retry` 와 같은 표지). 나머지 본문은 고치지 않았다.
  - 린트에 걸리는 스크립트 열(`c3_compare.py`·`e_classify.py`·`e_listing.py`·`e_search.py`·`e_titles.py`·`e_toc.py`·
    `render_links.py`·`render_pages.py`·`revosax_search.py`·`versions.py`)은 파일 머리에 `# ruff: noqa` 한 줄만
    더했다. 조사 때 돌린 그대로가 기록이다.
- `drafts/` 는 적용하지 않은 초안 그대로다. 실제 표는 `rules/de_sn/` 다(아래).

## 정정·보충 — 뒤 차례에서 드러난 것

- **규칙 표현은 권고 (ii) 가 아니라 (iii) 로 정해졌다**(사람의 결정 S2). 구현은 `totensonntag_offset: -4` —
  Totensonntag 를 § 2 의 「letzter Sonntag vor dem 1. Advent」 대로 세고 그 4 일 전이다. 초안의 `advent_offset: -11`·
  `de_sn_advent_holidays.yaml` 은 쓰이지 않았다. 두 꼴의 날짜는 같다(보고 C3).
- **source 의 꼴이 초안과 다르다.** 구현의 source 는 Hessen 1971 을 들지 않는다(머리 주석의 교차 확인 한 줄뿐,
  사람의 결정 S3). source_todo 는 「Heft 35/1992」 검색 결과 없음과 보관 상품의 범위를 적는다(S4).
- key `buss_und_bettag` 는 2026-11-18 사람이 승인했다(S1) — 보고 판단 요청 1.
- 보고 C2 의 Saarland 1976 정정은 `docs/research/report_batch2_survey/README.md` 「정정」 절에 적었다(S6).

