# report_hb_read — 재현 기록

`report_hb_read.md`(이 폴더의 상위 `~/holidays-reports/`)의 읽기 집합과 시각 판독 기록이다.
조사는 2026-10-07, `origin/main` `50e14d9bdd348df2ab102740c3c6c48c51a94794` 에서 했다. 병렬화하지 않았다(scratch 하나).
레포 파일과 기존 `~/holidays-reports/report_hb_*` 는 고치지 않았다(읽기만). **요청은 없었다** — 코퍼스 PDF 는 scratch 에 남아 있었고 sha256 이 맞았다. 그래서 `fetch.log` 가 없다.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- 렌더는 `uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I` 로 했다.
- 표 정리는 시스템 `python3` 3.9.6 으로 했다.

| 파일 | 무엇 |
|---|---|
| `read_set.tsv` | 읽기 집합 68 쪽 — v1 R 67 쪽(`report_hb_structure/files_structure.tsv` 의 R 행 `nonsearch_pages`)과 E3 의 2021 Nr. 45 p2(v1 G) |
| `render.py` | 읽기 집합을 150 dpi 로, 지정한 쪽을 300 dpi 로 렌더 |
| `tile.py` | 300 dpi 렌더를 2×2 타일(5% 겹침)로 잘라 작은 글자를 읽게 함 |
| `build_reading.py` → `r_reading.tsv` | 판독 메모를 쪽마다 한 줄로 정리. 판독은 조사자가 렌더를 보고 한 것이다(시각 판독) |

렌더 PNG·타일·판독 메모 원본은 두지 않는다. 판독 뒤 지웠다. **코퍼스 PDF 167 개는 scratch 에 남겨 두었다**(`…/scratchpad/st/pdf/`).

## 재현 순서

```sh
uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I render.py read_set.tsv <pdf-dir> <png-dir> 150
uv run --no-project --with 'pypdfium2==5.14.0' --with 'pillow==11.3.0' python -I render.py read_set.tsv <pdf-dir> <png-dir> 300 \
  2020_160.pdf:8 2022_092.pdf:13 2022_146.pdf:4 2023_095.pdf:3 2024_039.pdf:2 2024_039.pdf:3 2024_043.pdf:2 \
  2024_043.pdf:3 2024_097.pdf:2 2026_009.pdf:6 2026_009.pdf:7 2026_051.pdf:4 2026_090.pdf:4 2021_045.pdf:2
uv run --no-project --with 'pillow==11.3.0' python -I tile.py <png-dir>
```

## 알아 둘 것

- 300 dpi 로 다시 렌더한 14 쪽은 모두 지도다.
  - 그중 2024 Nr. 43 p3 과 2026 Nr. 9 p7 은 래스터가 2024 Nr. 39 p3 과 같다(이미지 XObject 데이터 sha256 앞 12 자 `96143f45186b`).
  - 그래서 그 쪽의 타일 넷을 읽었고, 두 쪽은 서명·시행 조항이 있는 오른쪽 아래 타일만 따로 봤다.
  - 2024 Nr. 43 p2 도 2024 Nr. 39 p2 와 래스터가 같다(`0efb97eccbc3`). 왼쪽 위 타일을 따로 봤다.
- 「partly unreadable」 7 쪽은 모두 지도 바탕의 작은 라벨이다. 영역은 `r_reading.tsv` 의 `unreadable_region` 열에 있다. 제목·범례·표제란·서명은 읽혔다.
- 「넣지 않는 것」 검색(`_csrf`·`SID=`·`cookie`·`bgblxaver`·`ServiceKey`·`token`·`password`, 대소문자 무시) 적중은 0 이다.

## 옮김 — de_hb 구현 PR

- 원본은 레포 밖 `~/holidays-reports/report_hb_read.md` 와 `~/holidays-reports/report_hb_read/` 였다.
  보고 본문은 옮기면서 고치지 않았다.
- 옮길 때 바꾼 것: 린트에 걸리는 스크립트 셋(`build_reading.py`·`render.py`·`tile.py`)은 파일 머리에
  `# ruff: noqa` 한 줄만 더했다.
- 위의 scratch(`…/scratchpad/st/pdf/`)는 조사 세션의 임시 디렉터리다. 레포에는 PDF·렌더를 두지 않는다.

## 정정 — 뒤 차례에서 드러난 것

- **G 는 558 이 아니라 557 이다.** `report_hb_structure` 의 v1 G 는 558 쪽이다. 이 판독이 그중 2021 Nr. 45 p2
  (E3)를 따로 읽어 「일부 판독」 7 쪽에 넣었으므로, 계정에서 G 는 557 이다(보고 「계정」 표와 같다).
  `report_hb_structure` 의 표에 남은 558 은 그 시점의 수다.
