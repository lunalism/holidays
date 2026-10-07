# report_hb_fulltext — 재현 기록

`report_hb_fulltext.md`(이 폴더의 상위 `~/holidays-reports/`)의 요청 로그·코퍼스 표·검색 출력·전사본이다.
조사는 2026-10-06(UTC), `origin/main` `50e14d9bdd348df2ab102740c3c6c48c51a94794` 에서 했다. 병렬화하지 않았다(scratch 하나).
레포 파일은 고치지 않았다(브랜치·커밋·PR 없음).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
Python 은 시스템 `python3` 3.9.6 으로, PDF 추출만 `uv run --no-project --with 'pypdf==5.4.0' python -I` 로 돌렸다.

| 파일 | 무엇 |
|---|---|
| `fetch.sh` → `fetch.log` | 요청 도우미(`report_hb_bb_prep/fetch.sh` 를 고친 것: 요청 뒤 3 초 쉼, 5xx 면 두 번까지 재시도)와 요청 1,077 건의 기록(200 이 1,074, 500 이 3), sha256 일곱 줄 |
| `parse_listing.py` → `listing.tsv` | 관보 목록 11 쪽(`?skip=0…1000&max=100`)에서 뽑은 1,100 항목(2019 Nr. 96 – 2026 Nr. 101) |
| `download.sh` | `listing.tsv` 의 2020 년 이후 PDF 1,056 건을 목록의 href 그대로 순차로 받은 스크립트 |
| `extract.py` → `extract_stats.tsv` | pypdf 5.4.0 쪽별 텍스트 추출. 파일마다 쪽 수·문자 수·쪽별 비공백 문자 수 |
| `corpus.py` → `corpus.tsv`, `flagged_pages.txt` | 코퍼스 표 1,058 줄(PDF 없는 2 항목 포함)과 비공백 200 자 미만 쪽 741 개 |
| `flagged_pages_split.tsv`, `flagged_files.tsv` | 플래그 쪽을 「쪽 머리(호·날짜·쪽 번호)만 있는 쪽」 과 나머지로 나눈 것, 그리고 파일별 합계와 목록 제목 |
| `search.py` → `hits.tsv` | 정규화·패턴 검색. 적중 164 건 |
| `controls_2018_063_hits.tsv` | 같은 파이프라인을 범위 밖 대조군 2018 Nr. 63 에 돌린 적중 4 건 |
| `classify.py` → `classification.tsv` | 적중별 분류(A/B/C/D). 판정은 조사자가 문맥을 읽고 정했고 스크립트는 그 표를 옮긴다 |
| `hb_2020_012_text.txt` | Brem.GBl. 2020 Nr. 12 S. 52 텍스트층 전사 |

받은 관보 PDF·목록 HTML·추출 텍스트 전체는 두지 않는다(`docs/research/README.md` 「넣지 않는 것」).
PDF 의 URL·sha256 은 `corpus.tsv` 에 있어 다시 받아 대조할 수 있다. scratch 는 판독 뒤 지운다.

## 재현 순서

```sh
# 목록 11 쪽: fetch.sh 'https://www.gesetzblatt.bremen.de/?skip=N&max=100' <dir>/skipNNNN.html  (N = 0, 100, …, 1000)
python3 -I parse_listing.py <html-dir> > listing.tsv
./download.sh listing.tsv <pdf-dir>
uv run --no-project --with 'pypdf==5.4.0' python -I extract.py <pdf-dir> <txt-dir> > extract_stats.tsv
python3 -I corpus.py listing.tsv fetch.log <pdf-dir> extract_stats.tsv corpus.tsv flagged_pages.txt
python3 -I search.py <txt-dir> > hits.tsv
python3 -I classify.py hits.tsv > classification.tsv
```

## 알아 둘 것

- 목록의 호 표기는 고르지 않다: 「Gesetzblatt Nr. 5」(연도 없음 — 2020 Nr. 31, 2022 Nr. 113, 2023 Nr. 25, 2024 Nr. 5),
  「Gesetzblatt 2020 Nr: 171」(콜론 — 2020 Nr. 85, 171). 연도가 없으면 공개일의 연도를 쓰고 `listing.tsv` 의 `year_src` 에 `date` 라고 적었다.
- href 는 이미 퍼센트 인코딩돼 있다(`2025_06_30_GBl%200076_signed.pdf`, `GBl_BHV%20Fraktionsbeitr%C3%A4ge%202026_signed.pdf` 등 14 건). 그대로 썼다.
- 2025 Nr. 12 「wurde zurückgezogen」, Nr. 91 「wurde aufgehoben」 은 목록에 href 가 비어 있다. `corpus.tsv` 에 URL 없이 한 줄씩 둔다.
- `fetch.log` 의 Step 7 줄 셋(15:02:33Z·15:02:47Z·15:03:11Z)은 한 번 요청과 5xx 재시도 두 번이다.
- 정규화 규칙(줄 끝 「-」 + 다음 줄 소문자 시작이면 잇기)은 「Sonn-\nund」 를 「sonnund」 로 만든다(`hits.tsv` 2022_017 p2). 패턴 다섯은 그 결합으로 사라지지 않는다 — 하이픈만 지워진다.
- 쪽 경계는 잇지 않는다. 쪽을 넘어 갈린 낱말은 찾지 못한다.
- 「넣지 않는 것」 검색(대소문자 무시 `_csrf`·`SID=`·`cookie`·`bgblxaver`·`ServiceKey`·`token`·`password`)의 적중은 `fetch.log` 의 Step 7 URL 세 줄 `gsid=` 뿐이다(`SID=` 부분 일치, 세션 값 아님).

## 옮김 — de_hb 구현 PR

- 원본은 레포 밖 `~/holidays-reports/report_hb_fulltext.md` 와 `~/holidays-reports/report_hb_fulltext/` 였다.
  보고 본문은 조사 당시 경로 `~/holidays-reports/report_hb_fulltext/` 를 가리킨다. 그 폴더가 이 폴더다.
  보고 본문은 옮기면서 고치지 않았다.
- 옮길 때 바꾼 것:
  - 린트에 걸리는 스크립트 다섯(`classify.py`·`corpus.py`·`extract.py`·`parse_listing.py`·`search.py`)은 파일 머리에
    `# ruff: noqa` 한 줄만 더했다. 조사 때 돌린 그대로가 기록이다.
  - `fetch.log` 의 sha256 일곱 줄은 받은 파일을 조사 세션의 임시 디렉터리 경로로 적었다. 그 경로 앞부분을
    `<scratch>/` 로 바꿨다(지금은 없는 경로다). 해시와 파일 이름 부분은 그대로다. 요청 줄은 손대지 않았다.
- 더한 것: `addendum_2026-10-07.md`·`addendum_2026-10-07_fetch.log` — 구현 PR 의 사전 확인에서 2026 Nr. 101 뒤의
  호(Nr. 102 하나)를 같은 파이프라인으로 본 기록, 145882 통합본 재수령, 현행 통합본(296390) 재요청.

## 정정 — 뒤 차례에서 드러난 것

- **Berichtigung 은 넷이 아니라 다섯이다.** 보고 「텍스트층 결과」 와 판단 요청 1 은 Berichtigung 을 넷
  (2024 Nr. 103·101·76, 2025 Nr. 159)으로 든다. `report_hb_flagged` 가 다섯째 2025 Nr. 23 「Berichtigung des
  Gesetzblattes Nr. 18」 을 찾았다(그 보고의 「규범 유형」 절).
- **scratch 의 PDF 는 이 조사 뒤에 지웠다**(이 README 「scratch 는 판독 뒤 지운다」). 그래서 `report_hb_flagged` 와
  `report_hb_structure` 가 플래그 파일 167 개를 `corpus.tsv` 의 URL 에서 각각 다시 받았다. 두 번 모두 sha256 이
  `corpus.tsv` 와 167/167 일치했다(각 폴더의 `fetch.log`).
