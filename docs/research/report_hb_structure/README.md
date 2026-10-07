# report_hb_structure — 재현 기록

`report_hb_structure.md`(이 폴더의 상위 `~/holidays-reports/`)의 요청 로그·재분류 표·표본 목록·파일 구조 표다.
조사는 2026-10-06–07(UTC), `origin/main` `50e14d9bdd348df2ab102740c3c6c48c51a94794` 에서 했다. 병렬화하지 않았다(scratch 하나).
레포 파일과 `~/holidays-reports/report_hb_fulltext*`·`report_hb_flagged*` 는 고치지 않았다(읽기만).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
Python 은 시스템 `python3` 3.9.6 이다. PDF 는 `uv run --no-project --with 'pypdf==5.4.0' python -I` 로 읽었다. 렌더는 `--with 'pypdfium2==5.14.0' --with 'pillow==11.3.0'` 로 했다.

| 파일 | 무엇 |
|---|---|
| `fetch.sh`·`refetch.sh` → `fetch.log` | 플래그 파일 167 개 재수령(scratch 에 없었다) — 요청 167 건, 전부 200 |
| `reclassify.py` → `pages_reclassified.tsv` | 741 쪽을 클립 제외 규칙(D1)으로 다시 재고 다시 분류. 옛 분류·옛/새 경로 수·클립 경로 수·새 분류 |
| `sample_render.py` → `sample_list.tsv` | 새 분류별 표본(시드 20261007, 최대 10)과 100 dpi 렌더 파일명. 렌더 이미지는 두지 않는다 |
| `sample_check.tsv` | 표본 24 쪽의 육안 판정(분류 대 모습만, 법 내용 없음). 클립 아닌 OTHER 두 쪽 기록 포함 |
| `structure.py` → `files_structure.tsv` | **v1(정본)** — 실행 전에 고정한 G1–G4 규칙으로 57 파일 판정 |
| `structure_v2.py` → `files_structure_v2.tsv` | **v2(참고)** — v1 의 시행 조항 정규식 결함(날짜 마침표) 하나만 고친 판. 보고 「G/R 결과」 참조 |

`r_reading.tsv` 는 없다 — Step 1 표본에서 불일치(2021 Nr. 45 p2)가 나왔고 v1 R 합계가 67 쪽(> 60)이라 지시대로 Step 4 를 시작하지 않았다.

**코퍼스 PDF 167 개는 지시대로 scratch 에 남겨 두었다**(`…/scratchpad/st/pdf/`, sha256 은 `report_hb_fulltext/corpus.tsv` 와 같음). 렌더 PNG 는 지웠다. 받은 PDF·추출 텍스트는 이 폴더에 두지 않는다(`docs/research/README.md` 「넣지 않는 것」).

## 재현 순서

```sh
./refetch.sh ../report_hb_fulltext/flagged_pages.txt ../report_hb_fulltext/corpus.tsv <pdf-dir>
uv run --no-project --with 'pypdf==5.4.0' python -I reclassify.py ../report_hb_flagged/pages_measured.tsv <pdf-dir> > pages_reclassified.tsv
uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I sample_render.py pages_reclassified.tsv <pdf-dir> <png-dir> > sample_list.tsv
# 새 분류가 BLANK 아닌 쪽이 있는 57 파일만 텍스트층 추출:
uv run --no-project --with 'pypdf==5.4.0' python -I ../report_hb_fulltext/extract.py <scope-pdf-dir> <txt-dir>
python3 -I structure.py pages_reclassified.tsv ../report_hb_flagged/norm_types.tsv <txt-dir> > files_structure.tsv
python3 -I structure_v2.py pages_reclassified.tsv ../report_hb_flagged/norm_types.tsv <txt-dir> > files_structure_v2.tsv
```

## 알아 둘 것

- 클립 제외: 경로 구성(m l c v y h re) 뒤 `W`/`W*` 가 있고 `n` 으로 끝난 경로는 구성 연산자와 `n` 을 세지 않는다. `W` 뒤 칠하기로 끝나면 센다.
- G3 의 부속 낱말은 부분 문자열로 찾는다. 기록된 증거 문장이 합성어일 수 있다(「Anlagenüberwachung」 2020 Nr. 170, 「Treppenanlage」 2025 Nr. 103). 두 파일은 다른 진짜 언급(「Staatsvertrag」, 「(Anlage 1)」)이 있음을 손으로 확인했다(보고 「G/R 결과」).
- 「넣지 않는 것」 검색(`_csrf`·`SID=`·`cookie`·`bgblxaver`·`ServiceKey`·`token`·`password`, 대소문자 무시) 적중은 0 이다.

## 옮김 — de_hb 구현 PR

- 원본은 레포 밖 `~/holidays-reports/report_hb_structure.md` 와 `~/holidays-reports/report_hb_structure/` 였다.
  보고 본문은 옮기면서 고치지 않았다.
- 옮길 때 바꾼 것: 린트에 걸리는 스크립트 넷(`reclassify.py`·`sample_render.py`·`structure.py`·`structure_v2.py`)은
  파일 머리에 `# ruff: noqa` 한 줄만 더했다.
- 위의 「코퍼스 PDF 167 개는 … scratch 에 남겨 두었다(`…/scratchpad/st/pdf/`)」 의 scratch 는 조사 세션의 임시
  디렉터리다. 레포에는 PDF 를 두지 않는다. 파일은 `report_hb_fulltext/corpus.tsv` 의 URL·sha256 으로 다시 받아 대조한다.

## 정정 — 뒤 차례에서 드러난 것

- **v1 이 정본이고 v2 는 참고 기록이다.** `structure.py`(v1)의 시행 조항 정규식은 날짜의 마침표(「am 1. Januar
  2022」)에서 끊겨 15 파일을 R 로 보냈다. `structure_v2.py` 는 그 정규식만 고친 판이다(G 51 / R 6). 사람은 v1 을
  그대로 공식 G/R 로 정했고 v2 를 채택하지 않았다. `report_hb_read` 는 v1 R 67 쪽 전부를 읽었다 — v2 R 9 쪽을 포함한다.
- G 의 쪽 수는 `report_hb_read` 에서 557 이 된다(그 폴더 README 정정).
