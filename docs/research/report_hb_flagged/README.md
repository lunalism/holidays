# report_hb_flagged — 재현 기록

`report_hb_flagged.md`(이 폴더의 상위 `~/holidays-reports/`)의 요청 로그·측정 표·표본 목록이다.
조사는 2026-10-06(UTC), `origin/main` `50e14d9bdd348df2ab102740c3c6c48c51a94794` 에서 했다. 병렬화하지 않았다(scratch 하나).
레포 파일과 `~/holidays-reports/report_hb_fulltext*` 는 고치지 않았다(읽기만).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- Python 은 시스템 `python3` 3.9.6 이다.
- PDF 읽기는 `uv run --no-project --with 'pypdf==5.4.0' python -I` 로 했다.
- 렌더는 `--with 'pypdfium2==5.14.0' --with 'pillow==11.3.0'`(PDFium 156.0.8076.0)로 했다.

| 파일 | 무엇 |
|---|---|
| `fetch.sh` → `fetch.log` | 요청 도우미(`report_hb_fulltext/fetch.sh` 와 같은 동작)와 요청 168 건(전부 200)의 기록, sha256 1 줄 |
| `refetch.sh` | 플래그 파일 167 개를 `report_hb_fulltext/corpus.tsv` 의 URL 에서 한 번씩 다시 받은 스크립트(scratch 에 PDF 가 없었다) |
| `measure.py` → `pages_measured.tsv` | 플래그 쪽 741 개의 내용 스트림 측정(이미지 XObject·경로·텍스트 연산자, Form XObject 재귀)과 고정 규칙 분류 |
| `sensitivity.py` | 임계를 하나씩 ±20% 옮겼을 때 분류가 바뀌는 쪽(보고용, 분류는 바꾸지 않음) |
| `op_breakdown.py` → `op_breakdown.tsv` | BLANK·OTHER 쪽의 경로 연산자 종류별 수(진단용) |
| `sample_render.py` → `sample_list.tsv` | 분류별 표본(시드 20261006, 최대 10)과 100 dpi 렌더 파일명. 렌더 이미지는 두지 않는다 |
| `sample_check.tsv` | 표본 30 쪽의 육안 판정(분류 검증만, 법 내용은 읽지 않음) |
| `norm_type.py` → `norm_types.tsv` | 167 파일의 목록 제목과 제목 문면 규칙에 따른 규범 유형 |

`remaining_set.tsv` 는 없다 — Step 2 표본 검증에서 불일치가 나와 지시대로 Step 6 전에 멈췄다(보고 「표본 검증」).

받은 PDF·렌더 PNG·추출 텍스트는 두지 않는다(`docs/research/README.md` 「넣지 않는 것」). scratch 는 판독 뒤 지운다.

## 재현 순서

```sh
./refetch.sh ../report_hb_fulltext/flagged_pages.txt ../report_hb_fulltext/corpus.tsv <pdf-dir>
uv run --no-project --with 'pypdf==5.4.0' python -I measure.py ../report_hb_fulltext/flagged_pages.txt <pdf-dir> > pages_measured.tsv
python3 -I sensitivity.py pages_measured.tsv
uv run --no-project --with 'pypdf==5.4.0' python -I op_breakdown.py pages_measured.tsv <pdf-dir> > op_breakdown.tsv
uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I sample_render.py pages_measured.tsv <pdf-dir> <png-dir> > sample_list.tsv
python3 -I norm_type.py ../report_hb_fulltext/flagged_files.tsv > norm_types.tsv
# Step 4: fetch.sh '<145882 URL>' <out.pdf> 뒤 report_hb_fulltext/extract.py 로 추출
```

## 알아 둘 것

- 표시 면적은 Do 시점 CTM 의 |a·d − b·c| 를 MediaBox 면적으로 나눈 값이다. 클리핑은 반영하지 않는다 — 클립으로 잘린 이미지도 전체 면적으로 센다.
- `n` 은 경로 연산자로 센다(지시의 목록대로). 이 PDF 들의 BLANK·OTHER 쪽 경로 연산자는 대부분 클립 `re W* n` 쌍이다(`op_breakdown.tsv`).
- 인라인 이미지(BI…EI)는 따로 세지만 분류에 쓰지 않는다. 이번 741 쪽에는 0 이다.
- 「넣지 않는 것」 검색(`_csrf`·`SID=`·`cookie`·`bgblxaver`·`ServiceKey`·`token`·`password`, 대소문자 무시)의 적중은 `fetch.log` 의 145882 URL `gsid=`(`SID=` 부분 일치)뿐이다.

## 옮김 — de_hb 구현 PR

- 원본은 레포 밖 `~/holidays-reports/report_hb_flagged.md` 와 `~/holidays-reports/report_hb_flagged/` 였다.
  보고 본문은 옮기면서 고치지 않았다.
- 옮길 때 바꾼 것:
  - 린트에 걸리는 스크립트 다섯(`measure.py`·`norm_type.py`·`op_breakdown.py`·`sample_render.py`·`sensitivity.py`)은
    파일 머리에 `# ruff: noqa` 한 줄만 더했다.
  - `fetch.log` 의 sha256 한 줄은 받은 파일을 조사 세션의 임시 디렉터리 경로로 적었다. 그 앞부분을 `<scratch>/` 로
    바꿨다. 해시는 그대로다.

## 정정 — 뒤 차례에서 드러난 것

- **145882 통합본의 sha256 은 재현되는 기준값이 아니다.** 보고 「수권 조항」 은 sha256 `9c1f5e7a…` 를 기록했고
  사람은 그것을 기준값으로 삼았다. 2026-10-07 에 다시 받은 PDF 는 295,461 B, sha256 `dbed1258…` 로 다르다.
  메타데이터 `/CreationDate` 가 받은 시각이다 — [추론] 포털이 요청 때마다 PDF 를 새로 만든다. 텍스트층(8 쪽,
  쪽별 비공백 문자 수)과 § 2 Abs. 1 a)–j) 는 같다(`report_hb_fulltext/addendum_2026-10-07.md`).
- 이 폴더의 판정은 `report_hb_structure` 가 클립 제외 규칙으로 다시 잰 것으로 대체됐다(그 보고).
