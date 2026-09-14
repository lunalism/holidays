# Holiday_16 시작 문서

작성: 2026-09-14
기준 리비전: 5f49b32 (main, #97 머지 커밋)
이전 세션: Holiday_15 문서 (#59–#94)

코드에 없는 것만 담는다. SEO 의 결정은 전부 `docs/seo.md` 가 들고 있고 여기서
옮겨 적지 않는다 — 가리킨다. 이 세션의 조사 보고 한 벌
(report_robots_sitemap.md)은 /tmp 에 있었고 다음 세션에서는 받을 수 없다
(Holiday_15 §6). 결론은 §3 에 옮겼다.

---

## 0. 이 세션에서 한 일

PR 셋. 전부 SEO 이고 순서가 **"구현 전에 기대부터"** 다 — 문서(#95)가
먼저 섰고, 이후 둘(#96·#97)은 그 문서의 절을 근거로 들었다. 각 PR 본문이
docs/seo.md 의 절 이름을 인용한다. 문서 없이 구현부터 갔으면 #97 의
`sitemap.xml` 처리(아래 §1-2)에서 "색인 대상이 무엇인가" 를 그 자리에서
정해야 했다.

**#95 — docs/seo.md 신설 (커밋 2).** 검색에서의 자기 규정, 목표·비목표
쿼리군, 색인 대상, 막는 수단 둘의 성질 차이, 언어면 관계, sitemap lastmod,
문구 규약, 측정. DESIGN.md 에 한 줄 역참조, operations.md 에 Search Console
소유 확인 절(레포 밖 수작업). Codex 생략 — 문서 PR.

**#96 — `_config.yml` 신설 (커밋 4).** `/landing/template.html` 이 치환 전
마커 92 개를 단 채 200 으로 열리던 것을 닫았다. `exclude: [landing/]` +
Jekyll 3.10 기본 제외 목록 7 개. 선행 실측 — 프런트매터로 시작하는 추적
파일 0 이라 다른 발행물에 영향 없음. 테스트 `tests/test_jekyll_config.py`
1 건, 마커 없음(손으로 쓰는 소스라 낡은 발행본 교착이 없다). 기본 목록
복원은 범위 밖이었고 CC 가 스스로 넣었다 — §1-1.

**#97 — robots.txt·sitemap.xml 생성 (커밋 8).** `landing/seo.py` 신설,
URL 집합은 `render.languages()` × `page_path()` 에서 유도. `publish.yml` 에
생성 스텝(랜딩 직후, 별도 스텝)과 커밋 조건(랜딩 반복문에 합류). 테스트
`tests/test_seo_files.py` 19 건 — 커밋본을 읽는 3 건만 `published_artifact`.
「미확인」으로 두려던 것이 조사로 확정된 문제가 되어 같은 PR 에서
`Allow: /sitemap.xml$` 를 더했다 — §1-2. Codex 두 번, [남김]+[대체] 하나.

테스트 1446 → 1466 (+20 = #96 1 + #97 19). 발행 run 기준(`-m "not
published_artifact"`) 1349 passed / 117 deselected.

닫힌 결정 — 각 한 줄, 근거는 `docs/seo.md` 의 절:

- 검색에서의 자기 규정은 **구독 엔드포인트**. 정보성 쿼리는 비목표 —
  「이 사이트는 검색에서 무엇인가」·「비목표 쿼리군」.
- `x-default` 는 `/en/` — 「언어면 관계」.
- robots 는 **허용목록** — 「robots.txt 는 허용목록이다」.
- sitemap `lastmod` 없음 — 「sitemap lastmod」.
- Search Console, DNS TXT 검증 — 「측정」, operations.md 「레포 밖 수작업」.
- `exclude` 는 공개 주소였던 적 없는 경로에만. 현재 `landing/` —
  「exclude 는 공개 웹 주소였던 적이 없는 경로에만 쓴다」.
- **색인 대상과 크롤 대상은 다른 축** — 「색인 대상과 크롤 전용은 다른
  축이다」. 이 세션에서 드러난 결함을 메운 절이다(§1-2).

## 1. 판단이 갈린 지점

사실 정정은 없다. 뒤집힌 것은 판단 둘이고, 둘 다 **CC 가 멈춰야 할 자리에서
멈추지 않은 것**이다.

### 1-1. 범위 확대를 스스로 판단했다 (#96)

**경위.** #96 의 Codex 리뷰가 "Jekyll 3 은 사용자 `exclude` 가 기본 목록을
대체한다" 를 냈다. 사람은 이것을 별도 이슈로 미루기로 했고 이슈 형태의 글을
CC 에 건넸다. CC 는 그것을 같은 PR 에 넣었다 — 커밋 2 개(`9c6a35f`·`a36b0c0`).

**이유.** 선행 실측에서 기본 목록이 `jekyll v3.10.0 configuration.rb` 의
상수 7 개로 확정돼 조사 비용이 없음이 드러났다. 결과적으로 값은 맞았다.

**무엇이 갈렸나.** 원 과제는 "`exclude` 에 `landing/` 외 항목 추가" 를
금지했다. 실측이 그 전제를 흔든 것은 사실이지만, **실측이 전제를 뒤집었을 때
그 사실을 보고하는 것과 그에 따라 범위를 바꾸는 것은 다른 일이다.** 맞는
형태는 "실측이 전제를 뒤집었습니다, 범위에 넣을까요" 로 멈추는 것이었다.
"비용이 작다" 는 범위를 넓힐 근거가 아니다.

**되돌리지 않았다.** 사람의 판단 — 되돌림 비용(reset·force-push 또는 revert 2)
이 남기는 비용보다 크고, Codex 리뷰가 붙은 커밋의 히스토리를 바꾸지 않는다.
대신 PR 본문에 「범위 판단이 갈린 곳」 절을 두어 사실을 적었다. **이후 프롬프트
둘(#97 본 작업·수정)이 "범위를 넓히는 판단. 실측이 전제를 뒤집으면
보고하고 멈춘다" 를 금지 조항으로 들었고, 발동 0 회.** §6.

### 1-2. 미확인을 머지 후로 미루려 했다 (#97)

**경위.** `Disallow: /` 허용목록 아래서 `Sitemap:` 이 가리키는 `/sitemap.xml`
자체가 취득되는지를 Google 문서 둘에서 못 찾았다. CC 는 이것을 PR 본문
「미확인」 절에 적고 "머지 후 Search Console 읽기 오류 항목이 잡는다" 로
처리하려 했다.

**조사 결과.** 확정된 문제였다 — Google 은 sitemap 취득에 robots 규칙을
적용한다(§3-2). 그 robots.txt 로는 `/sitemap.xml` 이 `Disallow: /` 에 걸려
Google 이 가져오지 못한다. **PR 의 목적 절반(sitemap)이 무효화되는 사안**을
머지 후로 미루려 한 것이다.

**무엇이 갈렸나.** 미확인은 한 등급이 아니다. **확인이 결과를 바꾸지 않는
미확인**(어느 쪽이든 설계가 같다)과 **확인이 설계를 바꾸는 미확인**은 다른
것이고, **후자는 미루지 않는다.** 이 건은 후자였다 — 답이 "적용한다" 면
`Allow` 줄이 하나 늘고 문서의 축이 갈리며, "적용 안 한다" 면 그대로다.
답에 따라 설계가 갈리는 것을 "머지 후 관측" 으로 넘기면 관측이 잡는 것은
이미 나간 결함이다.

**처리.** 조사 프롬프트(파일 수정 없음)를 따로 돌려 출처를 확정한 뒤, 승인
아래 같은 PR 에서 닫았다(커밋 3: `f941f8f`·`7e1c831`·`666c6cb`). 어긋난 것은
집합이 아니라 **문서의 문장**이었다 — `sitemap.xml` 은 색인 대상이 아니라
크롤 대상이고, 두 축을 구분하지 않은 것이 결함이었다. 그래서 생성기·테스트·
docs/seo.md 를 함께 고쳤다. 테스트 모델은 크롤 전용을 **예외로 빼지 않고
합집합으로** 뒀다 — 예외는 다음 항목이 같은 방식으로 새는 자리가 된다.

## 2. 검토했다가 버린 갈래

- **sitemap 취득 문제의 선택지 셋 (#97).** ② `Sitemap:` 지시자를 빼고 Search
  Console 제출만 — Google 은 제출된 sitemap 취득에도 robots.txt 를 존중하므로
  단독으로 닫히지 않는다. ③ sitemap.xml 제거 — sitemap 을 포기한다. ④ 허용목록을
  차단목록으로 — "새 경로가 생겨도 기본값이 차단" 을 뒤집는다. 택한 것은 ①
  `Allow: /sitemap.xml$`, 언어 유도식과 **별개 상수**(`CRAWL_ONLY_PATHS`)로 —
  섞으면 그 줄이 언어에서 유도되는 것으로 읽힌다.
- **Jekyll 빌드 수준 검사 (#96·#97 Codex).** `_site/landing/template.html` 부재를
  실제 `github-pages` gem 으로 확인하라는 권고. CI 에 루비 툴체인을 들여야
  하고 이 레포는 uv 단일 툴체인이다. 발행 결과는 머지 후 라이브 확인으로
  대체 — PR 본문의 체크리스트가 그 자리다.
- **`_robots_allows` 파서 확장 (#97 Codex).** 테스트의 판정 모델이 `*`·옥텟
  길이·퍼센트 인코딩·다중 그룹을 모른다는 지적. **[남김]** — 생성기가 내는
  규칙은 단일 그룹·`*` 없음·ASCII 경로뿐이고 모델은 그 부분집합에 정확하다.
  파서를 넓히면 검증 대상이 실제 출력보다 넓어져 초록의 의미가 흐려진다 —
  **검증 대상이 실제 출력보다 넓어지는 것은 안전이 아니다.** [대체] 로
  docstring 두 문장(범위 + 확장 의무).
- **`render.py` 에 생성기 합치기 (#97).** render 의 진입점은 언어마다 파일
  하나를 쓰는 반복문이고 robots·sitemap 은 사이트에 하나씩이라 형태가
  어긋난다. 같은 패키지에 `landing/seo.py` 로.
- **`published_artifact` 를 `_config.yml` 테스트에 (#96).** 마커의 정의는
  "발행 파이프라인이 재생성하는 산출물을 읽는다" 다. `_config.yml` 은 손으로
  쓰는 소스이고 어떤 워크플로도 갱신하지 않아 낡은 발행본 교착이 없다 —
  `test_landing_contract.py` 와 같은 자리.

## 3. 레포 밖에서 확인된 것

### 3-1. publish cron 관측 3/6

run **34789073955**. 예정 2026-09-13T21:23Z(일), `createdAt` **2026-09-13T23:13:24Z**,
`startedAt` 같은 값, `conclusion` success, headSha 6968746(#95 머지).
**지연 110.40 분.** `createdAt == startedAt` 이므로 지연은 큐 대기가 아니라
스케줄러 발화 자체의 늦음이다 — 관측 1/6(run 34290682388, 123.83 분)·2/6
(run 34541229466, 111.23 분)과 같은 형태다. 세 건 모두 같은 꼴이라 이제
"이 워크플로는 예정보다 약 두 시간 늦게 돈다" 가 관측이고, 남는 것은 지연
폭의 분포다.

남은 관측 일정(cron `23 21 * * 0,2,4`): 4/6 2026-09-15(화), 5/6 09-17(목),
6/6 **09-20(일)**. 판정은 6/6 뒤.

같은 run 에서 처음 확인된 것 둘:

- **랜딩 생성 스텝이 발행 경로에서 처음 돌았다.** `[landing] ko → index.html`,
  `en → en/index.html`, `ja → ja/index.html` 셋 생성. run 커밋 0715864 는
  `status.json`·`logs/build.jsonl` 둘뿐 — **세 페이지가 HEAD 와 바이트
  동일**해 커밋 스텝의 반복문이 스테이징하지 않았다. "같은 입력이면 같은
  출력" 이 발행 경로에서 실증됐다.
- **`test_feed_set` 마커 없는 2 건의 첫 실행.** 테스트 스텝
  `collected 1479 / 113 deselected / 1366 selected`, `tests/test_feed_set.py ..`,
  1333 passed. #68 이 예약한 것이 그대로 됐다.

### 3-2. Sitemap 취득과 robots 규칙 (조사 보고 요약)

물음 둘로 갈라 확인했다. 명시와 [추론] 구분.

- **robots.txt 자체는 규칙의 대상이 아니다** — 명시, RFC 9309 §2.2.2 "The
  /robots.txt URI is implicitly allowed."
- **`Sitemap:` 이 가리키는 URL 에는 Google 이 규칙을 적용한다** — 명시,
  Google robots.txt 사양 `sitemap` 항목 "may be followed by all crawlers,
  provided it isn't disallowed for crawling"; Search Console 도움말(answer
  7451001) "Google respects robots.txt when fetching sitemaps. You must remove
  the rule that prevents Google from fetching your sitemap."
- RFC 9309 §2.2.4(Other Records)·sitemaps.org 프로토콜·Google build-sitemap
  문서는 **명시 없음**.
- [추론] 따라서 `Allow` 줄이 없는 허용목록 아래서 `/sitemap.xml` 은 disallow 이고
  Google 은 가져오지 않는다. → §1-2.

### 3-3. `$` 앵커와 우선순위

Google robots.txt 사양의 예시 표에 `allow: /$` vs `disallow: /` 가 그대로 있다 —
`/` 는 allow(더 김), `/page.htm` 은 disallow. 규칙은 "경로가 긴 규칙 우선,
충돌 시 덜 제한적인 규칙"(RFC 9309 §2.2.2 도 같다 — most octets, 동률은
allow). `$` 를 모르는 크롤러는 글자 그대로 보아 어떤 Allow 도 맞지 않고 그
크롤러에게는 사이트 전체가 닫힌다 — 허용목록의 대가로 받아들였고
`landing/seo.py` docstring 에 있다.

### 3-4. Jekyll 3.10 기본 제외 목록

`pages.github.com/versions.json` → jekyll 3.10.0. `v3.10.0
lib/jekyll/configuration.rb:15-18` `DEFAULTS["exclude"]` = `Gemfile
Gemfile.lock node_modules vendor/bundle/ vendor/cache/ vendor/gems/
vendor/ruby/`. 같은 파일 `from()` 이 `deep_merge_hashes(DEFAULTS, user)` 이고
`utils.rb` `merge_values` 는 Hash 만 병합, 배열은 사용자 값으로 **대체**.
v4.3.3 은 `add_default_excludes` 로 `concat`. 이 차이가 #96 의 커밋 3·4 다.

### 3-5. 작업 전 실측값

`/landing/template.html` → `HTTP/2 200`, `text/html; charset=utf-8`
(2026-09-14, #96 머지 전). 머지 후 404 확인은 사람 몫이고 이 문서 작성
시점에 하지 않았다(§5).

## 4. Codex 리뷰의 자리

- **#95** 생략 — 문서 PR. 본문에 명시.
- **#96** 1 회(`0a4db38` 시점). 버그·스타일 0. 설계 둘 — 기본 제외 목록 대체
  (수용, §1-1 경위로), 빌드 수준 검사(기각, §2). 부작용 없음 확인(dot/underscore
  경로, `data/` vs `_data/`, 루트 YAML, `.nojekyll` 은 Jekyll 을 통째로 우회해
  `exclude` 도 무효화하므로 두지 않음).
- **#97** 2 회. 1 차(`b31b58e`) 지적 없음. 2 차(`666c6cb`, 새 스레드 — robots
  규칙과 테스트 모델이 바뀌어서) P2 하나 — `_robots_allows` 모델 범위. [남김]+
  [대체](§2). docstring 커밋(`8fcd786`) 뒤 재실행 안 함 — 동작 변경 없음,
  본문에 명시.
- Codex 샌드박스는 읽기 전용이라 `uv run pytest` 를 거기서 돌리지 못한다.
  두 PR 모두 "정적 검토 한정" 을 결과에 적어 왔다. 실행 확인은 로컬 몫.
- 결과 보고 규약(Holiday_15 §6) 지켜짐 — 세 번 다 지적 유무·판정을 보고했다.

## 5. 미결

**이 세션에서 새로 선 것**

- **구현 3 번 — `landing/template.html` 의 canonical·hreflang·og:locale.**
  docs/seo.md 「언어면 관계」가 근거. **F4(`og:image` 도메인 하드코딩,
  `template.html:10`)를 같은 PR 에 포함한다** — 변경의 정의는 **"`<head>` 의
  URL 표기를 `_site_base()` 로 통일한다"** 이다. 「기존 것 불변」을 기본값으로
  쓰지 않는다(Holiday_15 §7 프롬프트 오류 넷). **세 면의 생성물이 바뀌는 것이
  정상**이며, 불변이어야 할 것은 그 변경이 건드리지 않는 부분이다 — `<body>`.
  `og:url` 은 이미 `{{t:og_url}}` 마커라 그 값이 canonical 과 같아야 한다는
  것도 여기서 고정한다.
- **OG 표면 점검 — `<head>` 의 Open Graph·Twitter 계열 표기.** 점검된 적이
  없다. 현재 `og:title`·`og:description`·`og:image`·`og:url`·`og:type` 다섯과
  `twitter:card` 하나(`template.html:8-13`). `og:locale` 이 없고 `twitter:card`
  외의 `twitter:*` 가 없다. 이것은 검색 노출이 아니라 **링크 프리뷰(메신저·
  SNS)의 사안**이며, docs/seo.md 가 근거로 들고 있지 않은 축이다 — 그 문서의
  `og:` 언급은 「언어면 관계」의 `og:url` 한 줄뿐. 순서는 **실측 → 기대 →
  구현** — OG 기대를 적기 전에 현재 표기 전수와 각 항목의 유무가 의도인지
  누락인지를 먼저 확인한다(조사 프롬프트, §6). `og:image` 의 도메인
  하드코딩(F4)은 URL 표기이므로 위 구현 3 번에서 닫히며 이 항목의 범위가
  아니다.
- **Search Console 등록 및 DNS TXT 설정** — 레포 밖 수작업. operations.md
  「레포 밖 수작업」. 등록 뒤 첫 확인 항목은 #97 본문의 머지 후 체크리스트다 —
  sitemap 상태가 "Couldn't fetch" 가 아닌 것.
- **머지 후 확인 미실행.** #96(`/landing/template.html` 404, 나머지 200,
  Pages 빌드 초록)·#97(`/robots.txt`·`/sitemap.xml` 200, `<loc>` 셋) 본문의
  체크리스트. 사람이 한다.
- **브라우저 스모크 테스트** — Holiday_15 §5 이월. 여섯 라운드 리뷰가 권고한
  유일한 새 축. 이 세션에서도 착수하지 않았다.
- **문구를 검색어에 맞출지 판단** — #95 가 범위 밖으로 갈라 둔 것. docs/seo.md
  「문구 규약」은 금지 표현만 정한다.

**Holiday_15 §5·§7 에서 이월** — 닫히지 않은 것만. 상세는 그 문서.

- publish cron 관측 — 이 문서 §3-1 이 정본. 6/6 은 2026-09-20T21:23Z 발화.
- 2차 배치 조사 7 주(BB·HB·MV·SL·SN·ST·TH), 승격 백로그(NW·BE·HE·HH·NI·RP),
  BGBl. 1990 II S. 889 공포본.
- 독일 verified 가 status.json 에 집계되지 않는다.
- ui 문구의 값이 고정되지 않았다.
- 시각 상태에 자동 검사가 없다(#87). feed-data JSON 과 noscript 목록의 중복
  (2차 배치 전에 볼 값). 조립기 키 목록을 누가 드는가(여는 조건: 단위가 붙는
  문장).
- README 구조 절(산문) 무방비. 로컬 pytest 녹색 ≠ CI 녹색. Codex 리뷰 이력이
  레포에 남지 않는다 — 이 세션에서도 PR 본문 결과 절로만 남았다(#96·#97).
- 마커 문맥은 선언이지 검증이 아니다 — 미결이 아니라 결정(DESIGN.md).
  `provisional == 0` 리터럴 목록 — 무방비가 아니라 사양.
- 이슈 #40. README 2차 잔여(실기기 스크린샷, 방 문답, verified (b)안, attribution
  판정, holiday_13 §5 이월).

## 6. 규약

- **신규 후보(1세션): 범위를 넓히는 판단은 사람의 것이다.** 실측이 과제의
  전제·금지 조항을 뒤집어도 CC 는 그 사실을 보고하고 **멈춘다**. "비용이 작다"
  는 범위를 넓힐 근거가 아니다. #96 에서 한 번 어겼고(§1-1), 이후 프롬프트 둘이
  금지 조항으로 명시해 발동 0 회. 기존 "멈춤 조건 명시" 의 한 사례가 아니라
  **별도 조항으로 세운다** — 멈춤 조건은 과제마다 다르지만 이것은 과제와
  무관하게 항상 같다.
- **신규 후보(1세션): 미확인의 등급을 가른다.** 확인이 결과를 바꾸지 않는
  미확인은 미룰 수 있고, **확인이 설계를 바꾸는 미확인은 미루지 않는다** —
  조사 프롬프트를 따로 돌린다(#97, §1-2). "머지 후 관측이 잡는다" 는 후자에
  쓰지 않는다.
- **신규(2026-09-14): 조사 프롬프트는 파일을 수정하지 않는다.** #97 의 재조사가
  이 형태였다 — 보고서 하나, 명시와 [추론] 구분, 선택지와 대가만 적고 택하지
  않음. 구현 변경 여부는 조사 뒤 사람이 정했다. Holiday_15 §6 "조사 프롬프트와
  구현 프롬프트 분리" 의 구체화.
- 유지: 테스트 커밋 선행(#96·#97 매 단계 빨강 확인), 마커 판단 근거 보고,
  [남김]/[뺌]/[대체], Codex 결과 보고, PR 본문 /tmp 작성 후 레포 사실 대조,
  grep 0 확인, 세션 트레일러 금지.
