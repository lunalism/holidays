# report_de_bb_impl — de_bb 구현 때의 확인 기록

PR #120(브란덴부르크 피드)의 사전 확인에서 돌린 스크립트와 출력이다. 별도 보고서는 없다.
결과는 `rules/de_bb/solar_holidays.yaml` 머리 주석(「§ 2 Abs. 3 일회성 지정」 절)과 PR 본문에
있고, 이 폴더가 그 근거다. 조사 당시 경로는 `~/holidays-reports/report_de_bb_impl/` 이다.
2026-09-30, `origin/main` `be1c45f` 기준.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.** `bravors_search.py` 는 조사 때
돌린 그대로라 바뀐 것은 파일 머리의 `# ruff: noqa` 한 줄뿐이다(#113·#114·#118 폴더와 같다).

## 파일

| 파일 | 무엇 |
|---|---|
| `fetch.sh` | 요청 도우미(식별 UA, 로그 한 줄) |
| `fetch.log` | 요청 기록 전부 — BRAVORS 법령 페이지·연도별 관보 목록 2020–2026·검색 화면, 검색 POST(검색어 포함), feiertage-api. 상태는 전부 200 |
| `bb_oneoff_scan.txt` | 연도별 관보 목록(2020–2026)의 제목 검색 출력. **이 목록은 호 번호만 적고 제목이 없어** 0 건은 아무것도 말하지 않는다 — 그래서 아래 검색으로 바꿨다 |
| `bravors_search.py` → `bravors_search.tsv` | BRAVORS 공개 검색 화면(현행 Schnellsuche 와 außer Kraft 문서를 찾는 Archiv-Schnellsuche)에 검색어 다섯을 넣고 결과 전 쪽의 (문서 id, 제목, 날짜)를 적은 표. 질의마다 새 세션, 결과 화면의 검색어 반향(`echo`)과 보고된 건수(`reported`)를 함께 적는다 |
| `bravors_search_classified.txt` | 위 표의 분류 — 검색어별 집합 비교, 제목에 Feiertag·Gedenk·Jahrestag·einmalig·Trauertag 가 든 문서, 2019 년 이후 날짜 문서 전부 |
| `fapi_crosscheck.txt` | feiertage-api 교차 확인 — BE 2020·2025 의 8. Mai(일회성) 수록 여부, BB 2020–2031 해마다의 날짜 집합 대 피드 계산 |

`fetch.log` 에는 검색 스크립트의 첫 실행(질의 사이 세션을 재사용해 결과가 앞 질의 것으로
남고, 쪽 넘김이 7 쪽에서 멈춘 판)의 요청도 들어 있다. 그 결과는 버렸고, `bravors_search.tsv` 는
질의마다 새 세션으로 다시 돌린 둘째 실행의 것이다.

## 옮기지 않은 것

`docs/research/README.md` 「넣지 않는 것」 — 쿠키 파일, 사이트 응답 덤프(HTML), 세션 값이 든
로그는 두지 않는다.

- `scratch/cookies.txt` — 검색 화면이 준 세션 쿠키(cookie jar). 값 자체라 두지 않는다.
- `scratch/*.html` — BRAVORS 페이지 응답 덤프(법령 본문·연도별 목록·검색 폼·결과 첫 쪽).
  필요한 사실은 `fetch.log`(URL·상태·크기)와 `bravors_search.tsv`(검색 결과 전부)가 든다.
- `scratch/fapi_*.json` — feiertage-api 응답 덤프. `fapi_crosscheck.txt` 가 대신한다.

옮긴 파일 일곱을 대소문자 무시로 검색했다: `_csrf`, `SID=`(빈 값 제외), `cookie`, `jsessionid`,
`sixcms`, `session`, `token`, `password`, `Set-Cookie`. 적중은 `bravors_search.py` 의 코드
이름(`http.cookiejar`·`HTTPCookieProcessor`) 셋뿐이고 값은 없다.
