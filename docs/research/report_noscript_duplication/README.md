# report_noscript_duplication — 재현 기록

`docs/research/report_noscript_duplication.md` 의 측정 스크립트와 출력이다. 보고
본문은 조사 당시 경로 `~/holidays-reports/report_noscript_duplication/` 를 가리킨다.
그 폴더가 이 폴더다(아래 두 예외는 옮기지 않았다).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.** 실행은 레포의
`uv run`(Playwright 는 dev 의존)을 전제로 한다. 측정은 2026-09-30, `origin/main`
`9a2c001` 에서 했다. `measure.py`·`domparser_probe.py` 는 조사 때 돌린 그대로라
바뀐 것은 파일 머리의 `# ruff: noqa` 한 줄뿐이다(#113·#114 폴더와 같다).

## 파일

| 파일 | 무엇 | 만든 것 |
|---|---|---|
| `measure.py` | B·C — 페이지에서 feed-data JSON·noscript 목록·head noscript style 을 정확한 앵커로 떼고 raw·gzip5·gzip9 크기를 잰다 | – |
| `synth_states.sh` | C — 스크래치 워크트리의 `rules/` 에 SYNTHETIC 주 피드 7 개(최소 모듈)를 넣는다. 커밋하지 않는다 | – |
| `noscript_dom.py` | F — headless Chromium 에서 JS 켬·끔 각각 noscript 목록의 요소 수·텍스트 길이·행 수 | – |
| `domparser_probe.py` | 옵션 2 의 전제 확인 — noscript 텍스트를 DOMParser·`<template>` 로 다시 파싱해 행을 센다(구현 아님) | – |
| `measure_head15.tsv` | 15 피드(HEAD) 세 면의 측정 | `measure.py HEAD15 index.html en/index.html ja/index.html` |
| `measure_syn22.tsv` | 22 피드(SYNTHETIC) 세 면의 측정 | `synth_states.sh <워크트리>` → `python -m landing.render` → `measure.py SYN22 …` |
| `noscript_dom_head15.txt` | F 의 출력. 앞 9 줄은 스크립트가 띄운 로컬 `http.server` 의 접근 기록(127.0.0.1)이다 | `noscript_dom.py <커밋본 세 면 + status.json 을 둔 디렉터리>` |
| `domparser_probe.txt` | DOMParser 확인 출력과 `file == key + ".ics"` 검사 | `domparser_probe.py <같은 디렉터리>` + `feed_data()` 한 줄 검사 |
| `wire.txt` | 세 URL 의 전송 크기(`curl -w '%{size_download}'`, `--compressed` 유무·identity) | curl(보고 A 절) |
| `gzip_levels.txt` | 세 면의 gzip 레벨 1–9 크기와 서빙 크기 — 레벨 5 가 일치 | Python `gzip.compress` 한 줄(보고 A 절) |
| `headers_excerpt.txt` | 세 URL 의 요청(Accept-Encoding)·상태 줄·`content-encoding`·`content-length` 만 | 아래 `headers.txt` 에서 발췌 |

## 옮기지 않은 것

`docs/research/README.md` 「넣지 않는 것」 — 사이트 응답 덤프(HTML·JS)와 헤더
덤프는 레포에 두지 않고, 필요한 로그는 발췌만 둔다.

- `live_ko.html`·`live_en.html`·`live_ja.html` — 라이브 페이지 응답 덤프.
  보고 0-3 절은 이것이 커밋본과 `cmp` 동일했다고 적는다. 커밋본이 곧 그 내용이다.
- `headers.txt` — 헤더 덤프. `headers_excerpt.txt` 가 대신한다.

보고 본문은 옮기면서 고치지 않았다. 본문에 나오는 `headers.txt`·`live_*.html` 은
이 폴더에 없는 파일을 가리킨다.
