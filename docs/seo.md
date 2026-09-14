# 검색 노출 — 기대와 경계

이 사이트가 검색에서 무엇이어야 하고 무엇이 아니어야 하는지를 적는다.
`robots.txt`·`sitemap.xml`·canonical·hreflang 의 구현은 이 문서를 근거로
한다. 구현이 이 문서와 어긋나면 구현이 틀린 것이고, 기대를 바꾸려면 이
문서를 먼저 고친다.

값은 코드에서 유도한다. 언어 목록·경로·로캘 태그를 여기 적지 않는 것은
적는 순간 그 자리가 낡기 때문이다 — 유도 함수의 이름만 적는다.

## 이 사이트는 검색에서 무엇인가

**구독 엔드포인트다.** 공휴일 정보를 읽는 곳이 아니라 구독 주소를 건네주는
곳이다. 이 문장이 아래 모든 경계의 근거다 — 무엇을 잡고 무엇을 잡지 않을지,
어느 URL 을 색인시키고 어느 URL 을 막을지, 문구에 무엇을 쓰지 않을지가
전부 여기서 나온다.

## 목표 쿼리군

**구독 의도** — 캘린더 앱에 공휴일 피드를 붙이려는 검색.

- "공휴일 캘린더 구독", "공휴일 ics", "구글 캘린더 공휴일"
- "Feiertage ICS Abo", "Feiertagskalender abonnieren"
- "祝日カレンダー 購読", "祝日 ics"

**브랜드** — `holidays.lunalism.com`, "lunalism holidays".

## 비목표 쿼리군

- 날짜 정보성 검색 — 특정 연도의 대체공휴일이 언제인가 같은 것.
- 국가별·주별 공휴일 목록 열람.

이 쿼리군을 잡으려면 국가별·연도별 데이터 페이지가 있어야 한다. 그 확장은
발행 중인 피드의 근거 품질 작업보다 뒤에 둔다. 검색 성과가 낮을 것이라는
판정이 아니라 범위 결정이다 — 지금 이 사이트는 구독 엔드포인트이고, 데이터
페이지를 두는 순간 그 페이지의 근거를 유지하는 일이 따라온다.

## 색인 대상

`landing/render.py` 의 `languages()` × `page_path()` 로 유도되는 URL 집합
뿐이다. 루트 언어는 `/`, 그 밖은 `/<lang>/` 이다. 언어를 늘리면 대상도
따라 늘어난다 — `landing/locales/` 에 파일 하나를 더하는 것이 언어를
늘리는 일의 전부이고, 색인 대상도 거기서 유도되어야 한다. 개별 URL 을
열거하지 않는다.

### 색인 대상과 크롤 전용은 다른 축이다

- **색인 대상** — 검색 결과에 나오기를 기대하는 URL. 위 유도 집합뿐이다.
- **크롤 전용** — 색인되기를 기대하지 않지만 크롤러가 가져가야 하는 URL.
  현재 `sitemap.xml` 과 `assets/og.png` 둘이다. 앞은 `Sitemap:` 지시자가
  가리키는 URL 의 취득에도 robots 규칙이 적용되기 때문에 필요하다 — Google
  robots.txt 사양의 `sitemap` 항목("may be followed by all crawlers,
  provided it isn't disallowed for crawling")과 Search Console 도움말
  ("Google respects robots.txt when fetching sitemaps"). 뒤는 세 면의
  `og:image` 가 가리키는 이미지이고, 링크 프리뷰 크롤러가 robots 규칙을
  적용하면 막힌 이미지는 프리뷰에 실리지 않는다 — X Cards 문서("If an
  image URL is blocked, no thumbnail or photo will be shown"). 언어에서
  유도되지 않는 상수이고, `landing/seo.py` 의 `CRAWL_ONLY_PATHS` 가 든다.

`robots.txt` 의 `Allow` 는 두 집합의 합이다. `sitemap.xml` 의 `<loc>` 은
색인 대상뿐이다. 둘을 한 집합으로 말하면 크롤 전용이 `<loc>` 로 새거나,
반대로 `Allow` 에서 빠져 sitemap 자체가 막힌다 — 후자가 실제로 있었다.

피드 파일(`feeds/*.ics`)은 색인 대상이 아니다. 검색 결과에서 `.ics` 를
직접 열면 파일을 내려받는 것으로 끝나고, 그것은 구독이 아니라 1 회
임포트라 이후 갱신을 받지 못한다. 구독 주소는 랜딩이 건네준다.

## 색인 대상이 아닌 것과 그 수단

GitHub Pages 는 브랜치 루트를 통째로 낸다(`Deploy from a branch`,
`main`, `/`; 빌드는 legacy 형이라 Jekyll 이 돈다). 그래서 소스·테스트·
문서·캐시가 전부 공개 URL 로 열린다. 이것을 막는 수단은 둘이고 성질이
다르다.

- **`robots.txt`** 는 크롤 요청을 막을 뿐 색인을 막지 않는다. 다른 곳에서
  링크된 URL 은 크롤 없이도 색인될 수 있다. 색인 자체를 막는 `X-Robots-Tag`
  는 응답 헤더인데, GitHub Pages 는 응답 헤더를 설정할 수 없어 쓸 수 없다.
- **`_config.yml` 의 `exclude`** 는 Jekyll 발행 자체에서 제외한다. 해당
  경로는 404 가 된다 — 크롤도 색인도 아니라 존재가 없어진다.

### robots.txt 는 허용목록이다

`Disallow: /` 를 먼저 두고 색인 대상과 크롤 전용만 `Allow` 한다. 색인
대상이 로캘 수만큼으로 한정되고 크롤 전용이 상수 몇 개뿐이므로 열거가
무너지지 않고, 새 경로가 생겨도 기본값이 차단이다. 차단목록(`Disallow` 를
경로마다 적는 것)은 경로를 더할 때마다 빠뜨릴 자리가 늘어난다.

허용목록에서는 색인 대상만으로 충분하지 않다. 발행된 페이지가 가리키는
리소스도 크롤 전용으로 함께 연다 — 문서가 그 URL 을 가리키는데 규칙이
그 URL 을 막으면 가리킨 것이 쓸모없어진다. 현재 그 대상은 `sitemap.xml`
(`Sitemap:` 지시자가 가리킨다)과 `assets/og.png`(세 면의 `og:image` 가
가리킨다)이며, 둘 다 같은 이유로 필요하다.

`Allow` 목록은 색인 대상(`languages()` × `page_path()`)과 크롤 전용
(`CRAWL_ONLY_PATHS`)의 합이다. 앞은 sitemap 의 `<loc>` 과 같은 소스이고,
뒤는 sitemap 에 들어가지 않는다. 사람이 적지 않는다.

### exclude 는 공개 웹 주소였던 적이 없는 경로에만 쓴다

발행된 URL 은 계약이며 404 로 만들지 않는다. UID 영속성과 같은 규칙이다 —
한 번 나간 것은 바꾸지 않는다. 그래서 `exclude` 는 어떤 문서·안내·링크에도
공개 주소로 적힌 적이 없는 경로에만 쓴다.

현재 `exclude` 대상은 `landing/` 하나다. 근거는 치환 전 마커
(`{{t:…}}`·`{{FEED_DATA}}`)가 남은 템플릿이 `/landing/template.html` 로
열린다는 것이다 — 마커가 그대로 보이는 페이지는 어느 쪽에도 쓸모가 없고,
그 경로는 공개 주소로 안내된 적이 없다.

`rules/`·`sources/`·`tests/`·`docs/` 같은 나머지는 `exclude` 하지 않는다.
공개돼 해로운 것이 없고(비밀값은 코드에 두지 않는 것이 규약이다), 그중
어느 경로가 어디에 링크됐는지를 전수 확인하지 않고는 "공개 주소였던 적이
없다" 를 말할 수 없다. 크롤은 `robots.txt` 의 기본 차단이 막는다.

## 언어면 관계

- **각 면에 self-canonical.** `/index.html` 도 `/` 와 같은 200 으로
  열리므로, canonical 이 없으면 같은 문서가 두 URL 로 노출된다. canonical
  값은 `page_path()` 가 주는 디렉터리 형태다 — `og:url` 과 같은 값이다.
- **`<link rel="alternate" hreflang>`** 를 모든 언어와 `x-default` 로 둔다.
  언어 목록은 `languages()` 다. hreflang 값은 locale 의 `lang`(언어 코드)
  을 쓴다. locale 의 `locale` 키(`ko-KR` 형의 지역 태그)는 표시 형식용이고
  hreflang 에 지역을 붙이지 않는다 — 지역별로 다른 페이지가 없다.
- **`x-default` 는 `/en/` 이다.** 원본 언어 표시가 아니라 어느 언어도 맞지
  않는 방문자의 행선지이기 때문이다. 루트가 한국어인 것은 처음 발행된
  URL 을 바꾸지 않아서이지 기본 언어라서가 아니다.

## sitemap lastmod

두지 않는다. 랜딩 HTML 은 같은 입력이면 같은 출력이라 발행마다 바뀌지
않는다 — 발행 시각을 `lastmod` 로 쓰면 사실과 어긋난다. 파일의 실제 변경일을
쓰려면 git 히스토리가 필요한데, publish 워크플로는 `fetch-depth: 1` 이라
워크플로 안에서 얻을 수 없다. 틀린 값보다 없는 값이 낫다.

sitemap 의 URL 집합은 `languages()` × `page_path()` 에서 만든다 — 색인
대상뿐이고, 크롤 전용(`sitemap.xml` 자신)은 들어가지 않는다. `robots.txt`
의 `Allow` 가 색인 대상에 대해 쓰는 것과 같은 소스이고 사람이 적지 않는다.

## 링크 프리뷰 표기

메신저·SNS 가 링크를 펼칠 때 읽는 `<head>` 의 Open Graph·Twitter Card
표기다. **검색이 아니다** — 목표 쿼리군·색인 대상과 무관하고, 검색 결과에
아무 영향이 없다. 이 문서에 두는 것은 `robots.txt` 를 공유하기 때문이다:
프리뷰 크롤러도 robots 규칙을 따르는 경우가 있어(X Cards 문서 "If an
image URL is blocked, no thumbnail or photo will be shown"), 페이지가
가리키는 이미지는 크롤 전용으로 열려 있어야 한다. 현재 그 대상은
`assets/og.png` 이고 「색인 대상과 크롤 전용은 다른 축이다」가 든다.

### 무엇을 두는가

OG 프로토콜(ogp.me)의 필수 넷 `og:title`·`og:type`·`og:image`·`og:url` 과
`og:description` 은 세 면에 이미 있다. 여기에 더하는 것은 **기존 값에서
유도되는 것**뿐이다 — 새 문구를 쓰지 않는다.

- **`og:locale`** — 그 면의 언어. 없으면 소비자가 기본값(`en_US`)으로
  해석하므로 다국어 사이트에서는 세 면이 같은 언어로 읽힌다.
- **`og:locale:alternate`** — 그 면이 아닌 나머지 언어. hreflang 과 같은
  목록(`languages()`)에서 자기를 뺀 것이다.
- **`og:image:width`·`og:image:height`** — 크롤러가 이미지를 내려받기 전에
  크기를 알 수 있게 한다. 값은 `assets/og.png` 의 실제 픽셀 크기
  (1200 × 630)이고 이미지가 바뀌면 같이 바뀐다.

### 형식 — locale 키와 og:locale 은 다르다

`landing/locales/*.yaml` 의 `locale` 키는 하이픈 구분(BCP 47, `ko-KR` 형)
이고 `og:locale` 은 밑줄 구분(`language_TERRITORY`, `ko_KR` 형)이다.
**키를 고치지 않는다** — 그 값은 스크립트의 `toLocaleDateString` 이 쓰는
자리이고 거기서는 하이픈이 맞다. `og:locale` 은 렌더 시점에 변환한다.

같은 값이 두 자리에서 다른 형식으로 쓰이는 것이며, 어느 한쪽으로 통일하지
않는다. 형식이 다른 이유가 각각 있다.

### 무엇을 두지 않는가

- **`twitter:*`** — `twitter:card` 외에는 두지 않는다. X 의 카드 처리기는
  `twitter:title`·`twitter:description`·`twitter:image` 가 없으면 각각
  `og:title`·`og:description`·`og:image` 로 폴백한다(X Cards Markup Tag
  Reference). 같은 값을 두 벌 두면 갈릴 자리만 늘어난다.
- **`og:site_name`** — 두어야 할 근거가 확인되지 않았다.

### 미결

이 절이 닫지 않는 둘.

- **`og:image:alt`** — 문구를 새로 써야 한다. 그것은 「문구 규약」이 다루는
  사안과 같은 성격이라 유도되는 값이 아니다.
- **면별 이미지 분화** — 현재 `og:image` 는 세 면이 같은 파일이고, 그
  파일은 한국어 UI 의 캘린더 화면이다. 면마다 다른 이미지를 둘지는
  결정되지 않았다. 위 `alt` 는 이 결정에 달려 있다 — 이미지가 갈리면
  alt 도 갈린다.

## 문구 규약

title·meta description·og 계열에 **보증 표현을 쓰지 않는다.** "정확한",
"공식", "보장", "안전한" 이 금지 예시다. 이 저장소는 근거를 들고 있다고
주장하지 정확함을 보증하지 않는다 — 잠정 항목이 있고 그것을 status 로
공개한다.

사실 진술만 쓴다 — 대상 국가, 피드의 성격(iCalendar 구독 피드), 항목마다
근거를 병기한다는 사실.

문구를 검색어에 맞출지는 이 문서의 범위 밖이며 별개 사안으로 둔다. 이 절은
그 판단이 넘지 않을 경계만 긋는다.

## 측정

Google Search Console 을 쓴다. 소유 확인은 **DNS TXT** 로 한다 — HTML 파일·
메타 태그 방식은 검증 문자열이 `landing/render.py` 산출물에 들어가므로 쓰지
않는다. DNS 설정은 레포 밖 수작업이다(`docs/operations.md`).

지표는 사실 진술로 적는다. 순위 목표를 적지 않는다.

- 색인된 URL 수와 `languages()` 수의 일치 여부
- Search Console 의 `robots.txt`·`sitemap.xml` 읽기 오류 건수
- 목표 쿼리군에서의 노출 발생 여부
