# 랜딩 피드 목록의 이중 적재 — feed-data JSON 과 noscript 목록 (조사)

- 측정 시점: 2026-09-30, `origin/main` = `9a2c001e7bd57d6aeecce087693e770f5072a85a` (#117 머지)
- 범위: 조사만 했다. 레포 파일 변경·브랜치·PR 없음. 스크래치 워크트리 `/tmp/wt_noscript` 는 측정 뒤 지웠다(`git worktree list` 에 main 하나, `git status --porcelain` 0 줄).
- 재현 스크립트·원자료: `~/holidays-reports/report_noscript_duplication/`
  - `measure.py`: 블록 추출과 크기 측정(B·C)
  - `synth_states.sh`: C 의 SYNTHETIC 주 7 개
  - `noscript_dom.py`: F
  - `domparser_probe.py`: 옵션 2 의 전제 확인
  - `measure_head15.tsv`, `measure_syn22.tsv`, `headers.txt`, `wire.txt`, `gzip_levels.txt`, `noscript_dom_head15.txt`, `domparser_probe.txt`, `live_{ko,en,ja}.html`
- 표기: 명령 출력에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.

---

## 0. 사전 확인 — 전부 통과

### 0-1. sha 와 피드 수
- `git fetch --prune` 결과 prune 된 원격 브랜치는 없다. `main` 은 `origin/main` 으로 fast-forward 했다(9a2c001).
- `feeds/*.ics` 는 **15** 개다: de, de_be, de_bw, de_by, de_he, de_hh, de_ni, de_nw, de_rp, de_sh, jp, jp_only, kr, kr_jp, kr_only.
- 페이지 목록도 15 행이다.
  - `feed_data(lang)` 의 그룹 feeds 와 아코디언 feeds 를 합한 수가 ko·en·ja 모두 15 다.
  - F 의 headless 실행에서 JS 켬 `#feed-groups .feed-row` = 15, JS 끔 noscript 안 `.feed-row` = 15 다.

### 0-2. 생산 경로 — 둘 다 `feed_data()` 에서 나온다
| 블록 | 만드는 곳 | 템플릿 자리 | 모양 |
|---|---|---|---|
| JSON | `render.py:622` `page.replace(PLACEHOLDER, _dumps_feed_data(feed_data(lang)))`. 직렬화는 `_dumps_feed_data`(render.py:301), 이스케이프는 `_script_json`(render.py:275) | `template.html:706–708` `{{FEED_DATA}}` | `<script type="application/json" id="feed-data">` |
| noscript 목록 | `_noscript(lang, column)`(render.py:396). 안에서 `data = feed_data(lang)`(render.py:415), 이스케이프는 `html.escape` | `template.html:489` `{{NOSCRIPT}}`(구독 `<section>` 안, `#feed-groups` 바로 뒤) | 속성 없는 `<noscript>` … `</noscript>` |
| head noscript style | 템플릿 리터럴. render 가 만들지 않는다 | `template.html:29–31` | `<noscript><style> .ranges, #updated-ok { display: none; } </style></noscript>` |

- `feed_data()` 는 render.py:239 에 있다. Holiday_15 의 서술과 같다.
- head 의 noscript style 은 피드 목록과 무관하다. 상태 블록을 숨기는 용도다. 비교용으로만 쟀다.

### 0-3. HEAD 재생성과 라이브 대조
- 스크래치 워크트리(HEAD)에서 `uv run python -m landing.render` 를 돌렸다. `index.html`·`en/index.html`·`ja/index.html` 셋 모두 커밋본과 `cmp` 가 같다.
- 라이브 `https://holidays.lunalism.com/`·`/en/`·`/ja/` 를 받아 커밋본과 비교했다. 셋 모두 `cmp` 가 같다(`live_*.html`).

---

## A. 실제로 나가는 바이트

`curl -sI -H 'Accept-Encoding: gzip, br'` 결과(`headers.txt`):

| URL | content-encoding | content-length(압축) | identity 크기 |
|---|---|---|---|
| `/` | gzip | 13829 | 53457 |
| `/en/` | gzip | 14111 | 53031 |
| `/ja/` | gzip | 14270 | 53646 |

- `br` 을 함께 보내도 Pages 는 **gzip** 으로 준다. `Accept-Encoding: br` 만 보내면 content-encoding 없이 준다(비압축).
- `curl -s -o /dev/null -w '%{size_download}'` 는 `--compressed` 를 붙여도 떼도 13829 / 14111 / 14270 이다. `size_download` 는 전송된 압축 바이트를 센다. `Accept-Encoding: identity` 로 받은 크기는 53457 / 53031 / 53646 이다(`wire.txt`).
- **보정.** Python `gzip.compress(level, mtime=0)` 의 1–9 레벨을 세 면에 대 보면 **레벨 5 가 세 면 모두 서빙 바이트 수와 정확히 같다**(13829·14111·14270, `gzip_levels.txt`).
  - 그래서 B·C 의 "서빙 기준" 열은 gzip -5 로 잰다. 참고용으로 -9 도 적는다.
  - [추론] Pages 의 압축기가 zlib 레벨 5 와 같은 출력을 낸다. 서버 설정을 본 것은 아니고 바이트 수 세 개가 일치한 것이다.

## B. 블록별 한계 비용 — 현재 15 피드

- 추출은 `measure.py::spans()` 가 한다.
  - 앵커는 정확한 여는 태그(JSON 은 `id="feed-data"`, head 는 `<noscript><style>`)와, 속성 없는 `<noscript>` 중 head 가 아닌 것이다. 뒤의 것에는 안에 `<div class="feed-group">` 이 있는지도 단언한다.
  - 각 앵커가 정확히 1 개가 아니면 멈춘다.
  - 떼는 단위는 블록 첫 줄의 줄머리부터 마지막 줄의 줄바꿈까지다.
- d_* 는 "full − 그 블록을 뗀 페이지" 이고, 단위는 바이트다.

| 면 | 변형 | raw | gzip5(서빙) | gzip9 | d_raw | d_gzip5 | d_gzip9 |
|---|---|---|---|---|---|---|---|
| ko | full | 53457 | 13829 | 13637 | – | – | – |
| ko | −JSON | 50634 | 13351 | 13169 | **2823** | **478** | 468 |
| ko | −noscript 목록 | 44980 | 13107 | 12972 | 8477 | 722 | 665 |
| ko | −head style | 53377 | 13794 | 13605 | 80 | 35 | 32 |
| ko | −둘 다(JSON+목록) | 42157 | 12521 | 12398 | 11300 | 1308 | 1239 |
| en | full | 53031 | 14111 | 13930 | – | – | – |
| en | −JSON | 50333 | 13599 | 13432 | **2698** | **512** | 498 |
| en | −noscript 목록 | 44769 | 13394 | 13269 | 8262 | 717 | 661 |
| en | −head style | 52951 | 14075 | 13897 | 80 | 36 | 33 |
| en | −둘 다 | 42071 | 12800 | 12683 | 10960 | 1311 | 1247 |
| ja | full | 53646 | 14270 | 14088 | – | – | – |
| ja | −JSON | 50893 | 13802 | 13628 | **2753** | **468** | 460 |
| ja | −noscript 목록 | 45134 | 13514 | 13398 | 8512 | 756 | 690 |
| ja | −head style | 53566 | 14236 | 14057 | 80 | 34 | 31 |
| ja | −둘 다 | 42381 | 12932 | 12823 | 11265 | 1338 | 1265 |

블록 위치(커밋본):
- ko: JSON 895–936 행, 목록 499–664 행, head 33–35 행.
- en: JSON 903–944, 목록 500–665.
- ja: JSON 895–936, 목록 499–664.

읽는 법:
- JSON 블록이 서빙 바이트에서 차지하는 몫은 478 / 512 / 468 B 다. 페이지 서빙 크기의 3.5% / 3.6% / 3.3% 다.
- [추론] "데이터를 한 벌로" 만들어 지금 줄일 수 있는 서빙 바이트는 어느 쪽을 지우든 면당 약 0.5–0.7 KB 다. 한 벌은 남아야 하므로 −둘 다(약 1.3 KB)는 가능한 선택지가 아니다.
- [추론] 단일 출처로 줄이는 값은 JSON 을 지우면 ≈ d(−JSON), noscript 를 지우면 ≈ d(−목록)이다. 둘 중 하나만 지워도 JSON 의 필드는 대부분 남는다(D 참조). 스크립트가 커지는 몫은 여기 포함하지 않았다(옵션 2 에서 따로 적는다).
- 두 블록을 따로 뗀 값의 합(ko 478 + 722 = 1200)이 함께 뗀 값(1308)보다 작다.
  - [추론] 두 블록이 서로를 압축 사전으로 쓴다. 하나를 지우면 남은 쪽의 압축 효율이 조금 떨어진다. 그래서 중복 제거의 실제 이득은 각 d 값 이하에 머문다.
- Holiday_15 의 "#88 로 +20%(약 9KB)" 와 대조했다. 지금 목록 블록은 raw 8477 B 이고, 목록을 뗀 페이지(44980 B) 대비 +18.8% 다.
  - [추론] 반올림한 표현으로 같은 크기다. 다만 이 값은 **raw** 기준이다. 서빙 기준(gzip)으로는 +722 B, +5.5% 다(13107 → 13829).

## C. 22 피드 투영 — SYNTHETIC

- 경로는 render 가 쓰는 것 그대로다.
  - 스크래치 워크트리의 `rules/` 에 SYNTHETIC 주 모듈 7 개(de_bb·de_hb·de_mv·de_sl·de_sn·de_st·de_th)를 넣었다.
  - 모듈에는 `FEED_PATH`·`CALNAME`·`LAND_NAME`·`LAND_NAME_DE` 넷만 둔다. `render.py::_row` 가 주 피드에서 읽는 필드는 이 넷뿐이다.
- 그 뒤 `python -m landing.render` 를 돌렸다. `feed_data()` 는 세 언어 모두 22 행을 낸다.
- layout·locale 은 손대지 않았다. 주 피드는 layout 의 `prefix: de_` 규칙으로, 문구는 locale 의 `state_feed` 틀로 자동 편입된다.
- 주 이름(한국어·독일어)은 실제 주명을 넣었다. 그래서 행의 문면 길이는 실제 2차 배치와 같은 꼴이다.
- 이 데이터는 커밋하지 않았다. 워크트리째 지웠다.

| 면 | 변형 | raw | gzip5 | gzip9 | d_raw | d_gzip5 | d_gzip9 |
|---|---|---|---|---|---|---|---|
| ko | full | 58555 | 14250 | 14031 | – | – | – |
| ko | −JSON | 54541 | 13628 | 13417 | **4014** | **622** | 614 |
| ko | −noscript 목록 | 46171 | 13269 | 13129 | 12384 | 981 | 902 |
| ko | −head style | 58475 | 14212 | 13995 | 80 | 38 | 36 |
| ko | −둘 다 | 42157 | 12521 | 12398 | 16398 | 1729 | 1633 |
| en | full | 57921 | 14508 | 14308 | – | – | – |
| en | −JSON | 54115 | 13907 | 13708 | **3806** | **601** | 600 |
| en | −noscript 목록 | 45877 | 13542 | 13417 | 12044 | 966 | 891 |
| en | −head style | 57841 | 14470 | 14272 | 80 | 38 | 36 |
| en | −둘 다 | 42071 | 12800 | 12683 | 15850 | 1708 | 1625 |
| ja | full | 58711 | 14655 | 14468 | – | – | – |
| ja | −JSON | 54808 | 14059 | 13869 | **3903** | **596** | 599 |
| ja | −noscript 목록 | 46284 | 13671 | 13554 | 12427 | 984 | 914 |
| ja | −head style | 58631 | 14617 | 14434 | 80 | 38 | 34 |
| ja | −둘 다 | 42381 | 12932 | 12823 | 16330 | 1723 | 1645 |

검산:
- "−둘 다" 의 raw·gzip 은 15 피드와 22 피드에서 바이트 단위까지 같다(ko 42157/12521, en 42071/12800, ja 42381/12932).
- 피드 수에 따라 변하는 부분이 정확히 두 블록이고, 추출이 그 둘을 빠짐없이 잡는다는 뜻이다.

15 → 22 의 변화(서빙 gzip5 기준):

| 면 | 페이지 전체 | JSON 블록 몫 | noscript 목록 몫 | JSON 몫 / 페이지 |
|---|---|---|---|---|
| ko | 13829 → 14250 (+421) | 478 → 622 (+144) | 722 → 981 (+259) | 3.5% → 4.4% |
| en | 14111 → 14508 (+397) | 512 → 601 (+89) | 717 → 966 (+249) | 3.6% → 4.1% |
| ja | 14270 → 14655 (+385) | 468 → 596 (+128) | 756 → 984 (+228) | 3.3% → 4.1% |

- raw 기준 JSON 블록은 2823 → 4014 B(ko)다. 7 피드에 +1191 B, 피드당 약 170 B 다.
- raw 기준 noscript 목록은 8477 → 12384 B(ko)다. 7 피드에 +3907 B, 피드당 약 558 B 다.
- [추론] gzip 뒤 한계 비용은 JSON 이 주 피드 1 개당 약 13–21 B, noscript 목록이 약 33–37 B 다. 주 피드 행은 같은 틀에 주 이름만 바뀌어 압축이 잘 된다. 주 피드가 아닌 피드(문구가 제각각)를 늘릴 때는 이보다 크다 — 측정은 하지 않았다.
- [추론] 22 피드에서도 중복의 서빙 비용은 면당 0.6 KB 안팎(JSON 을 지울 경우)이다. 첫 방문 한 면의 전체 전송 크기는 약 14.3–14.7 KB 다.

## D. 필드 목록 — JSON 항목 vs noscript 행

출처:
- JSON 모양: `_row`(render.py:220–237)와 `_dumps_feed_data`
- noscript 모양: `_noscript`(render.py:396–462)
- 스크립트 모양: `template.html:737–849`

| 필드 | JSON | noscript | 스크립트가 그린 행 | 비고 |
|---|---|---|---|---|
| `site_base` | 최상위 키 | 없음(값은 URL 안에 합쳐져 있다) | 사용(`base + "feeds/" + file`) | – |
| `key` | 있음 | **없음** | **쓰지 않음**(buildRow·buildGroup·buildAccordion 어디에도 `feed.key` 없음) | **JSON 에만.** 읽는 쪽은 테스트뿐이다(E). 15 피드 모두 `file == key + ".ics"`(`domparser_probe.txt`) |
| `file` | 있음 | 없음(URL 안에 합쳐져 있다) | URL 조립 | noscript 의 `code.url` 텍스트에서 되찾을 수 있다 |
| `label` | 있음 | `p.feed-label` | `p.feed-label` | 양쪽 |
| `desc` | 있음 | `p.feed-desc` | `p.feed-desc` | 양쪽 |
| 구독 URL(https) | 없음(조립한다) | `code.url` 텍스트 | `code.url` | **noscript 에만**(완성형) |
| webcal 링크 | 없음(조립한다) | `a.btn[href=webcal:…]` | `a.btn` | **noscript 에만**(완성형) |
| "앱에서 열기" 문구 | 없음(`{{j:open_in_app}}`) | 있음(`locale.ui.open_in_app`) | 있음 | JSON 밖. 스크립트 리터럴로도 있다 |
| 복사 버튼 | 없음 | **없음**(의도적, DESIGN.md 「JS 없는 쪽은…」) | 있음 | **스크립트에만** |
| 그룹 제목 | `groups[].title` | `p.feed-group-title` | 같음 | 양쪽 |
| 그룹 소속·순서 | 배열 구조 | 마크업 순서·중첩 | – | 양쪽(구조로) |
| 아코디언 제목 | `accordion.title` | `<summary>` 텍스트 | `<summary>` | 양쪽 |
| 아코디언 개수 "(9)" | 없음(세어서 낸다) | **없음**(render.py:449–453 주석이 의도적이라고 적었다) | `span` 에 `accordion.feeds.length` | **스크립트에만** |
| chevron 아이콘 | 없음 | 없음 | SVG | 스크립트에만 |
| 수록 기간·항목 수·provisional 수 | 없음 | 없음 | 없음 | 두 블록 모두 아니다 — `status.json` 에서 온다 |

- JSON 에만 있는 것은 **`key` 하나**다.
- noscript 에만 있는 것은 완성형 URL·webcal href 다. 이 둘은 JSON 의 `site_base`+`file` 에서 조립되는 값이다.

## E. JSON 블록을 읽는 쪽

- 인용은 15 단어 이하로 줄였다.
- 대소문자 무시 검색(`git grep -i 'feed-data\|feed_data\|noscript'`)과 구분 검색의 결과가 같았다.

**페이지 JS**
- `landing/template.html:738`: `var data = JSON.parse($("feed-data").textContent);` — 유일한 런타임 소비자다(`renderSubscribe`).
- `landing/template.html:717`: 「피드 목록은 위 feed-data 블록이 정의하고 이 스크립트가 짠다.」
- `landing/template.html:41`, `:484`: 같은 서술의 주석이다.

**테스트**
- `tests/test_landing.py:78–92`: `DATA_BLOCK` regex 와 `_html_and_data()` 가 **커밋본 HTML 의 JSON 을 파싱**한다.
  - 이것을 쓰는 테스트는 11 개(파일 전체 13 개 중)다. 105 `test_the_page_still_reads_status_json`, 113 `…every_published_feed_has_a_row_and_vice_versa`, 124 `…feed_rows_match_status_json_feed_keys`, 133 `…kr_subscription_url_is_derived_from_the_cname`, 145 `…state_feeds_live_in_the_accordion…`, 159 `…labels_and_descriptions_are_present`, 167 `…state_labels_and_descs_are_derived…`, 247 `…accordion_is_sorted_by_key`, 260 `…groups_keep_their_titles`, 277 `…no_per_feed_markup_remains`, 288 `…feed_list_is_read_from_the_data_block`.
  - 이 가운데 `key` 를 쓰는 것: 113·124(feeds/·status.json 과의 집합 비교), 145·247(아코디언 소속·정렬), 288(`feed["key"].startswith("de_")`).
- `tests/test_landing.py:6`: 「피드를 하나 늘릴 때 랜딩에서 손대는 곳은 feed-data 블록의 한 줄뿐이다.」
- `tests/test_landing.py:289–293`: 「목록이 데이터 블록에서 읽히는지.」 `'id="feed-data"'` 와 `'$("feed-data")'` 의 존재를 단언한다.
- `tests/test_landing_contract.py:257`: `test_the_feed_data_block_takes_the_same_escaping` 이 `_dumps_feed_data` 를 직접 부른다.
- `tests/test_landing_contract.py:518–534`: `test_the_feed_data_block_is_script_safe_in_the_rendered_page` 가 렌더본의 블록을 regex 로 찾는다.
- `tests/test_landing_contract.py:537–542`: `test_the_noscript_list_is_html_escaped…`(noscript 쪽 짝)가 `<noscript>\n(.*?)\n\s*</noscript>` 로 찾는다.
- `tests/test_landing_contract.py:351`: 플레이스홀더 배선 테스트의 ids 에 `FEED_DATA`·`NOSCRIPT` 가 있다.
- `tests/test_landing_smoke.py:10`: 「구독 행 수 == feed-data 의 피드 수」.
  - 다만 `feed_count()`(:100–108)는 블록이 아니라 `render.feed_data(lang)` 를 직접 부른다.
  - `ROW_SELECTOR = "#feed-groups .feed-row"`(:92)이고, :90–91 주석은 「JS 가 켜진 브라우저는 noscript 내용을 요소로 세우지 않으므로」 다.
- `tests/test_landing_smoke.py:300`: `test_a_script_terminator_in_the_feed_data_surfaces_as_a_page_error` 는 PR #92 형(JSON 블록 조기 종료)을 재현하는 메타 테스트다.
- `tests/test_landing_render.py:18`: 바이트 비교다. 블록을 파싱하지 않는다(「파싱해서 feed-data 만 비교하면…」).
- `tests/test_feed_set.py:25`, `tests/test_readme.py:15`: docstring 이 "랜딩 feed-data" 를 집합 비교의 한 축으로 서술한다. 코드에서는 test_landing 을 거친다.

**문서**
- `DESIGN.md:246`: 「구독 절의 feed-data 블록은 … 생성된다」(「랜딩은 산출물이다」 절).
- `DESIGN.md:271`: 「구독 절의 줄은 스크립트가 `feed-data` JSON 을 읽어 그린다.」(「JS 없는 쪽은 사람이 아니라 기계다」 절)
- `DESIGN.md:298`: 「목록은 render 가 `feed_data()` 로 만든다. 사람이 쓰지 않는다.」
- `DESIGN.md:303`: 「같은 데이터가 페이지에 두 번 들어가는 것은 안다. 그 대가는 알고 치른다.」
- `docs/browser-smoke.md:39–43`: 「구독 행 수가 데이터의 피드 수와 같다.」와 PR #92 의 15 → 0 사고.
- `docs/browser-smoke.md:76`: 「noscript 목록의 표시 여부」가 스모크 범위 밖이라고 적혀 있다.
- `docs/seo.md`: `noscript`·`feed-data` 언급 0 건이다(대소문자 무시).

**#59 의 "목록은 데이터 블록에서 읽는다"**
- 그 문자열 그대로는 `docs/holiday_15.md:728` 한 곳뿐이다. 이 문서는 #59 를 인용하는 쪽이다.
- 명제를 고정하는 코드는 `tests/test_landing.py:288` `test_the_feed_list_is_read_from_the_data_block` 이다(주석 :289 「목록이 데이터 블록에서 읽히는지」).
- 이 테스트는 `2c9d4fe test(landing): 구독 절 피드 목록의 데이터 주도 사양을 먼저 못 박는다` 에서 들어왔고, 그 커밋은 `6977e0e Merge pull request #59` 로 병합됐다.

## F. headless Chromium 재확인(#88 사실)

- 브라우저: Playwright 의 chromium, `151.0.7922.34`.
- 대상: 커밋본 세 면과 status.json 을 로컬 http 로 서빙했다.
- 원자료: `noscript_dom_head15.txt`.

| | 면 | noscript 요소 수 | 목록 noscript `childElementCount` | `textContent.length` | `innerHTML.length` | noscript 안 `.feed-row` | `#feed-groups .feed-row` |
|---|---|---|---|---|---|---|---|
| JS 켬 | ko | 2 | **0** | 7398 | 7398 | 0 | 15 |
| JS 켬 | en | 2 | **0** | 8223 | 8223 | 0 | 15 |
| JS 켬 | ja | 2 | **0** | 7468 | 7468 | 0 | 15 |
| JS 끔 | ko | 2 | 3 | 3532 | 7398 | **15** | 0 |
| JS 끔 | en | 2 | 3 | 4357 | 8223 | **15** | 0 |
| JS 끔 | ja | 2 | 3 | 3602 | 7468 | **15** | 0 |

- JS 를 켜면 목록 noscript 의 자식 요소는 0 이다. `textContent` 는 원문 마크업 문자열이고, 첫 글자가 `<div class="feed-group">` 로 시작한다. 길이는 `innerHTML` 과 같다.
- JS 를 끄면 요소로 선다. 그룹 3, `.feed-row` 15, `<details>` 1 이다.
- #88 의 서술(JS 켠 브라우저는 noscript 내용을 요소로 세우지 않는다)은 이 버전에서도 그대로다.
- **옵션 2 의 전제 확인**(`domparser_probe.txt`, 구현 아님). JS 켬 상태에서 noscript 의 `textContent` 를 다시 파싱해 봤다.
  - `new DOMParser().parseFromString(…, 'text/html')` 과 `<template>.innerHTML` 둘 다 행 15, 그룹 3, 아코디언 안 행 9 를 낸다. 세 면 모두 같다.
  - 첫 행과 끝 행의 label·URL(`kr.ics`, `jp_only.ics`)도 되찾힌다.
- [추론] 단일 출처 스크립트는 `JSON.parse` 대신 이 문자열을 HTML 로 한 번 더 파싱해야 한다. `querySelector` 로 label·desc·URL 을 뽑거나, 파싱된 노드를 그대로 옮겨 복사 버튼·chevron·개수만 덧붙이는 식이다.

---

## 선택지와 비용 — 권고 없음

**닫힌 것.** noscript 목록을 지우는 선택지는 #88 에서 닫혔다. 읽는 쪽이 기계이기 때문이다(DESIGN.md 「JS 없는 쪽은 사람이 아니라 기계다」). 다시 열지 않는다.

### 1. 둘 다 둔다 — 측정값과 재점검 조건을 기록한다
- 비용(측정): 서빙 gzip 기준으로 JSON 블록 몫이 면당 478 / 512 / 468 B(15 피드)다. 22 피드(SYNTHETIC)에서는 622 / 601 / 596 B 이고, 페이지 서빙 크기의 4.1–4.4% 다.
- 바뀌는 곳: 없음. DESIGN.md:303 「대가는 알고 치른다」에 값을 붙이는 문서 변경만 있다.
- 재점검 조건 후보 — 사람이 고른다:
  - (a) JSON 블록의 서빙 몫이 1 KB 를 넘을 때.
  - (b) 페이지 서빙 크기의 N% 를 넘을 때.
  - (c) 주 피드가 아닌 피드가 늘어 피드당 한계 비용이 C 의 값(JSON ≈13–21 B/피드)에서 크게 벗어날 때.
  - [추론] 주 피드 추가만으로 JSON 몫이 1 KB 에 닿으려면 현재 추세로 수십 피드가 더 필요하다. 이 조건은 사실상 "주 피드가 아닌 성장" 에 걸린다.
- 남는 위험(기록): PR #92 형은 JSON 쪽에서만 목록을 잃는 고장이다. 지금은 `_script_json` 과 스모크 테스트(:300)가 막고 있다.

### 2. JSON 블록을 지우고, 스크립트가 noscript 내용을 읽는다
- 줄어드는 것(측정): d(−JSON) = 서빙 gzip 기준 478 / 512 / 468 B(15), 622 / 601 / 596 B(22)다.
  - [추론] 스크립트가 파싱·추출 코드로 늘어나는 몫이 이것을 일부 상쇄한다. 그 크기는 재지 않았다.
- F 가 말하는 것: JS 켬 상태에서 noscript 는 요소가 아니라 텍스트다. 스크립트는 `DOMParser` 또는 `<template>` 으로 한 번 더 파싱해야 한다(확인됨 — 15 행 복원).
  - [추론] 문자열 → HTML 파싱이 새 경로가 된다. 이 페이지의 규칙은 "문자열을 마크업으로 해석시키지 않는다"(template.html:786 주석)다. 파싱 결과를 문서에 넣지 않고 값만 뽑으면 그 규칙과 양립할 수 있다. 노드를 그대로 옮기면 그 규칙을 다시 봐야 한다.
- 바뀌는 테스트:
  - `tests/test_landing.py` 의 `DATA_BLOCK`/`_html_and_data`(:78–92)와 이를 쓰는 11 테스트는 noscript 파싱으로 바뀐다. :288 `test_the_feed_list_is_read_from_the_data_block` 은 명제 자체가 바뀐다(#59).
  - `tests/test_landing_contract.py:257`·`:518` 은 script 문맥의 feed-data 가 사라져 대상이 없어진다. `:351` 은 ids 가 바뀐다.
  - `tests/test_landing_smoke.py:300` 은 PR #92 형 메타 테스트다. JSON 블록이 없으면 그 고장 경로 자체가 없어진다. [추론] 대신 "noscript 파싱이 실패하면 JS 경로가 빈다" 는 새 고장 경로에 짝이 필요하다.
  - `test_landing_smoke.py:10`·`:100–108` 은 `feed_data()` 를 직접 세므로 그대로 둘 수 있다. [추론]
- 바뀌는 문서:
  - DESIGN.md:246·271·298–303(두 절).
  - browser-smoke.md:39–43(「feed-data 블록의 피드 수」 문면).
  - template.html 주석 :41·:484·:717.
  - render.py 머리 docstring(:42, `{{FEED_DATA}}` 마커 설명)과 `_script_json` docstring(script 문맥이 둘 → 하나).
  - test_landing.py:1–20 docstring.
- JSON 에만 있는 필드(D): `key` 하나다. 런타임 스크립트는 쓰지 않으므로 페이지에서는 갈 곳이 필요 없다.
  - 테스트는 `key` 로 feeds/·status.json 과 비교하고 아코디언 소속·정렬을 본다. 이것은 noscript 의 URL 에서 `file` 을 되찾아 `.ics` 를 떼면 같은 값이 나온다(15 피드 모두 `file == key + ".ics"`, 측정).
  - [추론] 이 대응이 앞으로도 유지된다는 보장은 `_row` 의 `file: module.FEED_PATH.name` 과 `key: code` 가 같은 이름이라는 관례뿐이다. 그 관례를 고정하는 테스트가 있는지는 확인하지 않았다.
  - 또는 noscript 행에 `data-key` 속성을 달아 옮길 수 있다. 마크업이 조금 커진다.

### 3. 그 밖의 모양(나열만, 구현 안 함)
- **3a. noscript 없이 정적 목록을 본문에 내고 JS 가 덧칠한다(점진적 향상).**
  - render 가 목록을 `#feed-groups` 안에 일반 마크업으로 낸다. 스크립트는 복사 버튼·chevron·개수만 붙인다.
  - 데이터가 한 벌이 되고 파싱이 필요 없다. JS 켬·끔 모두 같은 DOM 이다.
  - 비용: 복사 버튼이 없는 행이 JS 실행 전에 잠깐 보인다([추론] 레이아웃 이동은 버튼 폭만큼이다).
  - 기계 쪽에서 보면 목록이 noscript 밖으로 나와 모든 크롤러에 보인다. DESIGN.md 「JS 없는 쪽은…」과 방향은 같다.
  - 바뀌는 곳: #59 의 "스크립트가 짠다" 명제, 스모크의 `ROW_SELECTOR` 와 :90–91 전제, 옵션 2 와 같은 테스트 묶음.
- **3b. JSON 을 슬림하게.**
  - `key` 를 뺀다(`file` 에서 유도). 행을 배열 `[file, label, desc]` 로 바꾼다.
  - [추론] 줄어드는 것은 JSON 몫(≈0.5–0.6 KB gzip)의 일부다. 이중 적재는 그대로다.
- **3c. noscript 행에 데이터 속성**(`data-key`·`data-file`)을 달고 JSON 을 지운다. 옵션 2 의 변형이다. 필드 손실이 없다.
- **3d. JSON 을 별도 파일(`feeds.json`)로 빼서 fetch 한다.** 페이지 크기는 줄지만 요청이 하나 는다.
  - 기존 결정 둘과 충돌한다. template.html 주석 「한 파일로 끝낸다」(:33 이하)와 :729–730 「상태를 못 읽어도 구독은 되어야 하므로 fetch 보다 먼저, 동기적으로」 다. 기록만 한다.

---

## 판단 요청 — 1 건
1. **옵션 선택(1 / 2 / 3a–3d).**
   - 측정 요약: 중복의 서빙 비용은 면당 약 0.5 KB(15 피드)에서 약 0.6 KB(22 피드, SYNTHETIC)다. 페이지 서빙 크기의 3.3–4.4% 다.
   - 옵션 1 을 고르면 재점검 조건(위 (a)–(c) 중 어느 것)을 같이 정해야 한다.

## 측정의 한계
- 서빙 압축 레벨은 바이트 수 일치(레벨 5)로 추정했다. Pages 설정을 본 것은 아니다.
- 7 개 SYNTHETIC 주는 실제 주명을 썼지만 문구 틀은 기존 locale 그대로다. 2차 배치에서 locale 이 바뀌면 값이 달라진다.
- 옵션 2·3 의 스크립트 증가분은 재지 않았다.
- 첫 방문만 셌다. 재방문 캐시(`etag`·`last-modified` 가 있다)는 고려하지 않았다.
