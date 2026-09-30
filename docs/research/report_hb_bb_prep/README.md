# report_hb_bb_prep — 재현 기록

`docs/research/report_hb_bb_prep.md` 의 요청 로그·전사본·검색 출력·초안이다. 보고 본문은
조사 당시 경로 `~/holidays-reports/report_hb_bb_prep/` 를 가리킨다. 그 폴더가 이 폴더다.
조사는 2026-09-30, `origin/main` `be1c45f` 에서 했다. 병렬화하지 않았다(scratch 하나).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**

| 파일 | 무엇 |
|---|---|
| `fetch.sh` → `fetch.log` | 요청 도우미와 요청 26 건의 기록(200 이 25, 500 이 1), sha256 두 줄 |
| `hb_2018_63_text.txt` | Brem.GBl. 2018 Nr. 63 S. 302 텍스트층 전사 |
| `hb_index_scan.txt` | Brem.GBl. 2020–2025 연간 목록·2026 목록의 제목 검색 출력 |
| `drafts/` | HB·BB 규칙 YAML 초안 넷과 안전망 검사 출력(`safety_net_check.txt`). BB 초안은 `rules/de_bb/` 로 구현됐다(줄 접기·머리 주석은 구현 쪽이 정본) |

받은 관보 PDF 는 두지 않는다(`docs/research/README.md` 「넣지 않는 것」). URL·sha256 은 보고와
`fetch.log` 에 있어 다시 받아 대조할 수 있다. 보고 본문은 옮기면서 고치지 않았다.
