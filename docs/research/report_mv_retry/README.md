# report_mv_retry — 재현 기록

`report_mv_retry.md`(이 폴더의 상위 `~/holidays-reports/`)의 요청 로그·렌더 기록·스크립트·추출 텍스트다.
- 조사는 2026-11-18(UTC 04:51:39Z–05:00:35Z), `origin/main` `399a3743d00145c68e1670dd9b1cdc30a40629c0` 에서 했다.
- 병렬화하지 않았다(scratch 하나). 레포 파일과 기존 `report_mv_prep*` 는 고치지 않았다(브랜치·커밋·PR 없음).
- 환경은 이 조사 전, 2026-11-18 에 새로 세웠다: uv 0.13.9 설치, `uv sync` 로 `.venv` 재생성(파이썬 3.12.16), chromium headless shell 설치, `~/holidays-reports` → `<local>/holidays-reports` 심볼릭 링크(가림 — 아래 「옮긴 기록」).

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- 레포의 의존을 그대로 썼다: `uv run`(playwright 1.62.0, chromium headless shell 151.0.7922.34 — report_mv_prep 과 같은 빌드).
- `extract_para2.py`·`summarize_search.py` 는 표준 라이브러리만 쓴다(`python3`).

| 파일 | 무엇 |
|---|---|
| `fetch.sh` → `fetch.log` | 요청 도우미(report_mv_prep/fetch.sh 와 같은 동작이되 **5xx 재시도는 한 번뿐**)와 요청 기록. 렌더는 사람이 여는 화면 URL 한 줄씩만 적는다(아래) |
| `render_doc.py` | landesrecht-mv.de 문서를 헤드리스 chromium 으로 렌더. 하위 요청 전부(실패 포함)를 `render/<이름>.net.tsv` 에 |
| `portal_search.py` | 포털 시작 화면의 Schnellsuche 편집기에 검색어를 타이핑하고 검색. `recherche3/search` 응답 본문은 scratch 에만 |
| `summarize_search.py` → `search_results.tsv` | 세 검색어의 결과 목록(검색어, 보고된 건수, 순번, docId, 날짜, 분류, 제목, 부제) |
| `extract_para2.py` → `text/ftg_mv_p2_r1.txt`·`r2.txt` | § 2 렌더 innerText 에서 문서 머리와 § 2 를 뽑고 정규화한 § 2 의 sha256 을 적는다. 두 렌더(10 초 간격)의 결과가 같다 |
| `render_links.py` | land-mv.de 화면 렌더와 링크 수집(관보 목록을 사이트 링크로 찾을 때). URL 을 만들지 않고 화면의 href 만 따라갔다 |
| `expand_listing.py` → `listing_2026.tsv` | 관보 화면의 「Mehr anzeigen」 을 펼친 뒤 PDF 링크 전부. 2026 Nr. 1–31, 파일 이름의 날짜 |
| `render/a1_r1·a1_r2` | A1(`jlr-FeiertGMVrahmen`) 두 렌더의 innerText·요청. `recherche3/document`·`toc` 500 |
| `render/a2_q1–q3.net.tsv` | A2 검색 세 번의 요청 |
| `render/a2_doc_r1` | 법 전체 id `jlr-NNLMV00007A2F` 렌더(「Inhalt」 탭 — 머리와 Stand 줄) |
| `render/a2_p2_r1·r2` | § 2 id `jlr-NNLMV00007A2FNN00000000003` 두 렌더(10 초 간격) |
| `render/b_*.net.tsv`, `b_list.txt`, `b_theme.links.tsv` | Part B 의 land-mv.de 화면들(법무부·주제·첫 화면·관보 화면) |
| `render/c_list.*` | Part C 의 관보 화면 펼침 |

- 렌더 HTML·검색 응답 JSON·옛 URL 이 넘겨준 HTML(`gvobl_2022_31_redirect.html`, sha256 `0154b7a4…`)·옛 목록 HTML 은 scratch 에만 두었다(`<scratch>/mv_retry/render/`·`dl/`). 사이트 응답 덤프다(`docs/research/README.md` 「넣지 않는 것」). MV 갈래가 닫히지 않아 지우지 않았다.
- A2 결과 링크(`*.links.tsv`)는 옮기지 않았다. href 에 `oi=` 값이 붙어 있다. docId·제목은 `search_results.tsv` 가 담는다.
- 렌더의 하위 요청은 브라우저가 스스로 내므로 3 초 간격을 줄 수 없었다. 사람이 연 화면 사이는 3 초 이상(§ 2 재렌더는 10 초)이다.
- land-mv.de 의 `net.tsv` 에서 상태가 빈 행(`/`, `/gebaerdensprache`, `/node/2046`, 쉬운 말 화면)은 화면 안 링크의 미리 받기 요청이다. 렌더를 닫을 때까지 응답이 기록되지 않았다.
- 옮길 때를 위해 이 폴더의 파일을 대소문자 무시로 검색했다: `jsessionid`·`sid=`·`token`·`cookie`·`_csrf`·`oi=`. `.net.tsv` 적중 0. 걸리는 것은 README 의 이 문장과 `render/b_list.txt`·`c_list.txt` 의 쿠키 안내문(「Diese Website benutzt Cookies für die Webanalyse …」)뿐이다. 값은 없다.

## 옮긴 기록

- 원본은 레포 밖 `~/holidays-reports/report_mv_retry.md` 와 `~/holidays-reports/report_mv_retry/` 였다. 옮긴 것은
  de_mv 구현 PR 이다(`docs/research/README.md` 「보고의 흐름」).
- 옮길 때 바꾼 것:
  - 보고 본문 두 줄(「기준 SHA와 환경」 의 심볼릭 링크 줄과 Step 0 표 E1 행)은 보고 디렉터리의 로컬 절대 경로를
    적었다. 그 앞부분을 `<local>/holidays-reports` 로 바꿨다 — 조사 기계의 볼륨 이름이라 공개 레포에 두지 않는다
    (`docs/research/README.md` 「이차 기록이다」 의 가림 예외). 나머지 본문은 고치지 않았다.
  - 이 README 의 같은 경로와 scratch 경로도 `<local>/`·`<scratch>/` 로 바꿨다.
  - 린트에 걸리는 스크립트 여섯(`expand_listing.py`·`extract_para2.py`·`portal_search.py`·`render_doc.py`·
    `render_links.py`·`summarize_search.py`)은 파일 머리에 `# ruff: noqa` 한 줄만 더했다. 조사 때 돌린 그대로가 기록이다.

## 정정·보충 — 뒤 차례에서 드러난 것

- **환경은 이 조사 전, 2026-11-18 에 새로 세웠다.** 보고 「기준 SHA와 환경」 이 적은 그대로다. 처음 세션의 Step 0 은
  `uv` 가 없어 요청 전에 멈췄다(그때 포털·관보 요청 0 건). 사람이 환경을 세운 뒤 Step 0 부터 다시 돌렸다.
  「한 번의 시도」 는 포털로 가는 요청에 대한 것이라는 사람의 명확화가 그 사이에 있었다.
- **검색 결과 65 건은 받지 않았다.** 「Sonn- und Feiertage」 는 91 건을 보고했고 첫 화면 26 건만 받았다
  (`search_results.tsv`). Part A 가 첫 성공에서 멈췄기 때문이다. 이후 de_mv 구현의 포털 확인
  (`docs/research/report_de_mv_impl/`)도 이 65 건을 받지 않았다 — 그쪽은 'Feiertag' 를 분류 Gesetze/Verordnungen
  으로 좁혀 87 건 전부를 받았다.
- **법 전체 Gesamtausgabe 는 이 조사에서 렌더하지 않았다.** de_mv 구현의 사전 확인 P1(2026-11-18,
  `docs/research/report_de_mv_impl/`)이 `jlr-NNLMV00007A2F` 의 「Aktuelle Gesamtausgabe」 를 렌더했고, 그 § 2 의
  정규화 텍스트 sha256 은 이 조사의 조문 단위 추출과 같다(`e7fe52ef…`, 887 B).
- 보고의 판단 요청 1–3 은 사람의 결정 M1(포털 § 2 를 공식 현행 조문으로)·M2(「Gültig ab: 13.07.2022」 를
  effective_from 의 근거로)·M3/M4(전 항목 false, E-Mail 요청 안 함)로 닫혔다 — 근거의 정본은 `rules/de_mv/` 의 표다.

