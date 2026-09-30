# report_source_selfcontain — 재현 기록

`docs/research/report_source_selfcontain.md` 의 스크립트와 출력이다. 보고 본문은 조사
당시 경로 `~/holidays-reports/report_source_selfcontain/` 를 가리킨다. 그 폴더가 이
폴더다(아래 예외는 옮기지 않았다). 측정은 2026-09-30, `origin/main` `e5a3e21` 에서 했다.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.** 네 스크립트는 조사 때
돌린 그대로라 바뀐 것은 파일 머리의 `# ruff: noqa` 한 줄뿐이다(#113·#114·#118 폴더와
같다). 앞의 셋은 레포 루트에서 `uv run python …` 으로, `hh_pdf_text.py` 는
`uv run --no-project --with pymupdf==1.26.5 python …` 격리 실행으로 돈다.

## 파일

| 파일 | 무엇 | 만든 것 |
|---|---|---|
| `dump_sources.py` → `sources.tsv` | A — 독일 규칙 YAML 108 항목의 (파일, key, 날짜, verified, source 한 줄). 정규화는 `feed.py::_one_line` 과 같다 | `uv run python dump_sources.py > sources.tsv` |
| `classify.py` → `hits.tsv` | A — 범주 패턴 적중, 대소문자 구분·무시 건수 병기 | `python classify.py sources.tsv > hits.tsv` |
| `affected_events.py` → `affected_events.txt` | E — 바뀔 항목이 발행본에서 몇 이벤트에 실리는지 | 레포 루트에서 실행 |
| `hh_pdf_text.py` → `hh_pdf_text.txt` | D — HmbGVBl. 2018 Nr. 9 PDF 의 쪽수·텍스트층·조문 위치 | PDF 경로를 인자로 |
| `hh_fetch_excerpt.txt` | D — 요청·응답 상태·PDF 링크·sha256 세 번·응답 헤더 세 필드 | 아래 `hh_fetch.log` 에서 발췌 |

## 옮기지 않은 것

`docs/research/README.md` 「넣지 않는 것」 — 받은 원본, 사이트 응답 덤프, 헤더
덤프는 두지 않고 필요한 로그는 발췌만 둔다.

- HmbGVBl. 2018 Nr. 9 호 PDF(457,762 B). 받은 원본이다. URL·sha256 은 보고 D-3 과
  `rules/de_hh/solar_holidays.yaml` 에 있어 같은 파일을 다시 받아 대조할 수 있다.
- `hh_fetch.log` — 요청 로그. 페이지 HTML 에서 grep 한 링크 목록·스크립트 태그 조각과
  응답 헤더 줄이 섞여 있다. `hh_fetch_excerpt.txt` 가 대신한다.

보고 본문은 옮기면서 고치지 않았다. 본문에 나오는 `hh_fetch.log`·`/tmp/hh_pdf/` 는
이 폴더에 없는 것을 가리킨다.
