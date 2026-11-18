# report_mv_prep — 재현 기록

`report_mv_prep.md`(이 폴더의 상위 `~/holidays-reports/`)의 요청 로그·렌더 기록·실험 스크립트·초안이다.
- 조사는 2026-10-07, `origin/main` `887a2984d00bf2280857eeb14f879fd381b80cc7` 에서 했다.
- 병렬화하지 않았다(scratch 하나). 레포 파일은 고치지 않았다(브랜치·커밋·PR 없음).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- 레포의 의존을 그대로 썼다: `uv run`(playwright 1.62.0, chromium headless shell 151.0.7922.34, holidays 0.102).
- 레포 모듈을 import 하는 스크립트는 `PYTHONPATH=<repo>` 로 돌렸다.

| 파일 | 무엇 |
|---|---|
| `fetch.sh` → `fetch.log` | 요청 도우미(`report_hb_fulltext/fetch.sh` 와 같은 동작)와 요청 기록. 렌더 두 번은 문서 URL 한 줄씩만 적는다(아래) |
| `render_portal.py` | landesrecht-mv.de 문서를 헤드리스 chromium 으로 렌더. 문서 URL 한 줄을 `fetch.log` 에, 하위 응답 전부를 `render/r?.net.tsv` 에 적는다 |
| `render/r1.txt`·`r2.txt` | 두 렌더(10 초 간격)의 body innerText — 「Das Laden des Dokumentes jlr-FeiertGMVrahmen ist fehlgeschlagen.」 |
| `render/r1.net.tsv`·`r2.net.tsv` | 렌더 동안 브라우저가 받은 응답 44 건씩(시각·URL·상태·content-type). `recherche3/document`·`toc` 가 500 |
| `render_hashes.txt` | 렌더 HTML·텍스트·평문 요청 HTML 의 sha256. 텍스트는 같고 HTML 은 다르다 |
| `unknown_field.py` → `.out` | B2 실험 — 독일 주 로더에 모르는 필드 `valid_from` 을 넣으면 어떻게 되는가 |
| `pyholidays_mv.py` → `.out` | B4 — holidays 0.102 의 DE(subdiv='MV') 2020~2031 |
| `simulate_effective_from.py` → `.out` | B3 — 설계안 (iii) 을 초안 표에 적용한 시뮬레이션(레포 무변경) |
| `drafts/de_mv_*.yaml` | MV 규칙 표 초안. **적용하지 않음.** Frauentag 외 자구는 미확보 |

- 렌더 HTML 원본·평문 요청 HTML 은 scratch 에만 두었다. 사이트 응답 덤프다(`docs/research/README.md` 「넣지 않는 것」). 해시는 `render_hashes.txt` 에 있다.
- 렌더의 하위 요청은 브라우저가 스스로 내므로 3 초 간격을 줄 수 없었다. 사람이 연 문서 URL 두 번은 10 초 이상 떨어져 있다.
- `net.tsv` 의 URL 에 세션·쿠키 값은 없다(`cookie`·`jsessionid`·`sid=`·`token` 검색 0 건).

## 옮긴 기록

- 원본은 레포 밖 `~/holidays-reports/report_mv_prep.md` 와 `~/holidays-reports/report_mv_prep/` 였다. 옮긴 것은
  de_mv 구현 PR 이다(`docs/research/README.md` 「보고의 흐름」). 보고 본문은 옮기면서 고치지 않았다.
- 옮길 때 바꾼 것: 린트에 걸리는 스크립트 넷(`pyholidays_mv.py`·`render_portal.py`·`simulate_effective_from.py`·
  `unknown_field.py`)은 파일 머리에 `# ruff: noqa` 한 줄만 더했다. 조사 때 돌린 그대로가 기록이다.
- `drafts/de_mv_*.yaml` 은 적용하지 않은 초안 그대로다. 실제 표는 `rules/de_mv/` 다.

## 정정·보충 — 뒤 차례에서 드러난 것

- **A1 의 실패(본문 못 얻음)는 `report_mv_retry` A2 가 대신했다.** 원래 id `jlr-FeiertGMVrahmen` 은 2026-11-18 에도
  문서 API·toc 가 500 이었다. 같은 포털의 검색(Schnellsuche)이 같은 법을 다른 id 로 찾았고, 조문 단위 id
  `jlr-NNLMV00007A2FNN00000000003` 이 § 2 전문을 냈다(「Fassung vom: 07.07.2022 / Gültig ab: 13.07.2022」). 이 보고의
  판단 요청 1 (b)(포털 검색으로 다른 문서 id)가 그 경로였다.
- **초안의 「[미확보]」 자구는 그 § 2 로 채워졌다.** 초안이 비공식 명칭으로 둔 것과 조문 표기가 다른 곳이 있다 —
  「der 1. Mai」, 「der Christi-Himmelfahrtstag」, 「der Tag der Deutschen Einheit (3. Oktober)」.
- **A2(GVOBl. M-V 2022 Nr. 31 재수령)는 이제 할 수 없다.** `report_mv_retry` Part B(2026-11-18): 2026-09-30 의 PDF
  주소는 `https://land-mv.de/` 의 HTML 화면으로 넘어가고, 새 관보 화면은 2014–2025 를 E-Mail 요청으로 돌린다.
- **effective_from 의 값.** 이 보고는 `2022-07-13` 을 공포일 다음 날로 읽은 [추론] 으로 두었다. 구현은 그 값을
  포털 § 2 의 「Gültig ab: 13.07.2022」 문면에 기대어 둔다(사람의 결정 M2) — 추론을 근거로 쓰지 않았다.
- B3 의 권고 (iii)(kr 의 effective_from 을 같은 이름·같은 뜻으로)와 판단 요청 3 (a)(de_mv 로더에만 닫힌 필드 집합)이
  구현됐다(`rules/de_mv/feed.py`).

