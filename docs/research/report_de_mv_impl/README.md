# report_de_mv_impl — de_mv 구현 때의 확인 기록

de_mv(메클렌부르크포어포메른 피드) 구현 PR 의 사전 확인 P1·P3·P4 에서 돌린 스크립트와 출력이다. 별도 보고서는
없다 — `report_de_bb_impl/` 과 같은 꼴이다. 결과는 `rules/de_mv/solar_holidays.yaml` 머리 주석(「현행 자구의 출처」·
「§ 2 Abs. 3 일회성 지정」 절)과 PR 본문에 있고, 이 폴더가 그 근거다. 조사 당시 경로는
`~/holidays-reports/report_de_mv_impl/` 이다. 2026-11-18(UTC 05:14:47Z–05:18:08Z), `origin/main` `399a374` 기준.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- 레포의 의존을 그대로 썼다: `uv run`(playwright 1.62.0, chromium headless shell 151.0.7922.34, holidays 0.102).
- 포털 스크립트 둘은 `report_mv_retry/` 의 스크립트에 한 단계씩 더한 복사본이다. 원본은 기록이라 고치지 않았다.
- 요청은 순차였고 사람이 여는 화면 사이를 3 초 이상 띄웠다. 렌더의 하위 요청은 브라우저가 스스로 낸다 —
  `render/*.net.tsv` 에 전부 있다.

## 파일

| 파일 | 무엇 |
|---|---|
| `fetch.sh`·`fetch.log` | 요청 도우미(`report_mv_retry/fetch.sh` 와 같다)와 요청 기록 다섯 줄. 이번에는 렌더만 했다 — 렌더는 사람이 여는 화면 URL 한 줄씩만 적는다 |
| `render_tab.py` | P1 — `report_mv_retry/render_doc.py` 의 렌더에 문서 탭 하나(「Aktuelle Gesamtausgabe」)를 누르는 단계를 더했다 |
| `render/p1.txt`·`p1.net.tsv` | P1 — 법 전체 `jlr-NNLMV00007A2F` 의 Gesamtausgabe 화면 innerText 와 요청 50 건(전부 200) |
| `extract_gesamt_p2.py` → `text/ftg_mv_gesamt_p2.txt` | P1 — Stand 줄과 § 2 를 `report_mv_retry/extract_para2.py` 와 같은 정규화로 뽑는다. sha256 `e7fe52efabaa7216ae815e4ad7931ad32bde43e6636ca40a40b5155c9b02efb5`(887 B) — 조문 단위 id 추출과 같다 |
| `portal_search_all.py` | P3 — `report_mv_retry/portal_search.py` 의 검색에 (선택) 분류로 좁히기와 결과 목록 끝까지 넘기기(최대 20 쪽)를 더했다 |
| `summarize_all.py` → `p3_results.tsv` | P3 — 검색어마다 결과 전부(docId·날짜·분류·제목·부제). 분류로 좁힌 검색은 좁히기 전 첫 화면을 섞지 않는다 |
| `p3_classify.py` → `p3_classified.tsv` | P3 — 「Feiertag」 87 건 전부(docId·날짜·제목·부제)에 기간(2020 이후 42 · 날짜 없음 3 · 2020 전 42)과 판정·판정 근거를 붙인 표. **판정은 제목과 부제만 읽고 정했다 — 문서 본문은 열지 않았다.** 옮길 때 더한 파일이다(아래) |
| `render/p3_*.net.tsv` | P3 — 검색 네 번의 요청. `p3_q1` 은 분류 화면을 보기 위한 「Feiertag」 첫 검색(`report_mv_retry/portal_search.py` 그대로)이고 표에는 쓰지 않았다 |
| `pyholidays_mv.py` → `.out` | P4 — holidays 0.102 의 DE(subdiv='MV') 2020–2031. 2020–2022 10 건, 2023 부터 11 건(3월 8일 Frauentag) |

## P3 — 포털 검색으로 본 것

- 「Feiertag」 를 분류 Gesetze/Verordnungen 으로 좁혀 87 건 전부(4 쪽)를 받았다. 결과 날짜 2020-01-01 이후 42 건,
  날짜 없음 3 건(FFN 색인), 그 전 42 건. 날짜 필터는 포털의 것을 쓰지 않았고 결과의 `date` 로 골랐다.
- 87 건 모두 판정했다(`p3_classified.tsv`). 2020 전 42 건도 본다 — 결과 날짜는 판(Fassung)의 날짜라 2020 의 날을
  2019 에 선언한 규범은 2019 로 나온다. 87 건 어느 제목·부제도 주 전역 일회성 공휴일이나 Arbeitsruhe 날의 선언이
  아니다. 가까운 것은 Beflaggung(BeflLVO M-V, FlaggTV MV)·Hoheitszeichen·Landtag 의사 규칙의 기한·영업시간·근무 규정·
  국가와 교회의 조약이다.
- **이 판정의 근거는 제목과 부제뿐이다.** 문서 본문을 열어 읽지 않았다. 제목이 선언을 드러내지 않는 규범 안에
  선언이 들어 있었다면 이 판정은 그것을 잡지 못한다.
- 인용 조문으로 찾는 검색은 없다. 「§ 2 Abs. 3 FTG M-V」 는 § 2 조문 문서 한 건으로 바로 열렸고(검색이 인용을
  문서 주소로 풀었다), 「§ 2 Absatz 3 Feiertagsgesetz」 는 0 건이다.
- [추론] 포털은 통합본 데이터베이스라, 날이 지나 효력을 잃은 일회성 선언이 빠져 있다면 이 검색에 들지 않는다.

## 옮기지 않은 것

`docs/research/README.md` 「넣지 않는 것」 — 사이트 응답 덤프는 두지 않는다.
- 렌더 HTML(`p1.html`·`p3_*.html`), 검색 응답 JSON(`p3_*.search.json`), 결과 링크(`p3_*.links.tsv` — href 에
  `oi=` 값)는 scratch(`<scratch>/de_mv_impl/render/`)에만 두었다. 필요한 사실은 `p3_results.tsv`·`render/*.txt`·
  `*.net.tsv` 가 든다.
- 옮길 때 더한 것: `p3_classify.py`·`p3_classified.tsv` — 조사 때 손으로 본 제목 판정을 87 건 표로 남겼다(입력은 조사 때의
  `p3_results.tsv` 그대로).
- 옮길 때 바꾼 것: 린트에 걸리는 스크립트 넷(`extract_gesamt_p2.py`·`portal_search_all.py`·`render_tab.py`·
  `summarize_all.py`)은 파일 머리에 `# ruff: noqa` 한 줄만 더했다. 조사 때 돌린 그대로가 기록이다.
- 넣는 파일 전부를 대소문자 무시로 검색했다: `_csrf`·`SID=`(빈 값 제외)·`cookie`·`bgblxaver`·`ServiceKey`·
  `token`·`password`·`jsessionid`·`oi=`. 이 README 의 이 문장과 「옮기지 않은 것」 의 `oi=` 설명 말고는 적중 0.
