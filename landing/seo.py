"""robots.txt 와 sitemap.xml 생성.

두 파일은 render.py 의 index.html 과 같은 성질의 산출물이다 — 같은 입력이면
같은 출력이고 시계를 읽지 않는다. URL 집합은 render.languages() ×
render.page_path() 에서 유도하고, 여기서 언어·경로·도메인을 따로 정하지
않는다. 근거는 docs/seo.md 「색인 대상」·「robots.txt 는 허용목록이다」·
「sitemap lastmod」.

render.py 에 합치지 않은 이유: render 의 진입점은 언어마다 파일 하나를
쓰는 반복문이고, 이 둘은 사이트에 하나씩이다.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from landing.render import OG_IMAGE_PATH, ROOT, _site_base, languages, page_path

ROBOTS_PATH = ROOT / "robots.txt"
SITEMAP_PATH = ROOT / "sitemap.xml"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# 크롤 전용 경로 — 색인되기를 기대하지 않지만 크롤러가 가져가야 하는 URL.
# 색인 대상(languages() × page_path())과 별개 상수다. 그 유도식에 섞지
# 않는다 — 섞으면 이 줄이 언어에서 유도되는 것으로 읽힌다.
#
# /sitemap.xml: Google 은 Sitemap: 지시자가 가리키는 URL 을 가져올 때도
# robots 규칙을 적용한다 — Google robots.txt 사양 sitemap 항목 "may be
# followed by all crawlers, provided it isn't disallowed for crawling",
# Search Console 도움말(answer 7451001) "Google respects robots.txt when
# fetching sitemaps". 이 줄이 없으면 /sitemap.xml 은 Disallow: / 에 걸려
# Google 이 가져오지 못한다. docs/seo.md 「색인 대상」의 두 축 참조.
#
# /assets/og.png: 세 면의 <head> 가 og:image 로 가리키는 이미지(render 의
# OG_IMAGE_PATH). 링크 프리뷰 크롤러가 이미지를 가져가려면 열려 있어야 한다 —
# X Cards 문서(Getting started, URL Crawling & Caching) "Twitter's crawler
# respects Google's robots.txt specification … If an image URL is blocked, no
# thumbnail or photo will be shown". 이 줄이 없으면 Disallow: / 에 걸린다.
# 색인 대상이 아니라 sitemap 에는 들어가지 않는다.
CRAWL_ONLY_PATHS = ("/sitemap.xml", "/" + OG_IMAGE_PATH)


def page_urls() -> list[str]:
    """색인 대상의 절대 URL. languages() 순서."""
    base = _site_base().rstrip("/")
    return [base + page_path(lang) for lang in languages()]


def robots_txt() -> str:
    """허용목록 robots.txt.

    Disallow: / 를 먼저 두고 색인 대상과 크롤 전용만 Allow 한다. 색인 대상의
    Allow 값은 page_path() 가 주는 디렉터리 형태에 `$` 를 붙인 것이고, 크롤
    전용은 CRAWL_ONLY_PATHS 상수다.

    `$` 는 URL 의 끝을 뜻한다 — Google robots.txt 문서(developers.google.com
    /search/docs/crawling-indexing/robots/robots_txt)와 RFC 9309 §2.2.3 이
    같은 뜻으로 정의한다. 붙이지 않으면 `Allow: /` 가 `Disallow: /` 와 같은
    길이로 충돌해 덜 제한적인 쪽(Allow)이 이기고 사이트 전체가 열린다.
    붙이면 `Allow: /$` 가 `/` 에만 맞고 `/feeds/kr.ics` 에는 맞지 않아
    `Disallow: /` 가 남는다 — Google 문서의 예시 표가 정확히 이 두 규칙의
    조합을 보인다. 우선순위는 "경로가 긴 규칙 우선, 충돌 시 덜 제한적인
    규칙" 이다.

    `$` 를 모르는 크롤러는 그것을 글자 그대로 보아 어떤 URL 에도 Allow 가
    맞지 않고, 그 크롤러에게는 사이트 전체가 닫힌다. 허용목록을 택한 대가로
    받아들인다 — 기본값이 차단이어야 새 경로가 조용히 열리지 않는다.

    Sitemap: 은 user-agent 그룹에 묶이지 않는 지시자라 위치가 무관하다.
    맨 뒤에 둔다.
    """
    lines = ["User-agent: *", "Disallow: /"]
    lines += [f"Allow: {page_path(lang)}$" for lang in languages()]
    lines += [f"Allow: {path}$" for path in CRAWL_ONLY_PATHS]
    lines += ["", f"Sitemap: {_site_base()}sitemap.xml"]
    return "\n".join(lines) + "\n"


def sitemap_xml() -> str:
    """색인 대상의 sitemap. <loc> 만 둔다. 크롤 전용은 들어가지 않는다.

    lastmod·changefreq·priority 를 넣지 않는다. lastmod 는 발행 시각이 아니라
    실제 변경일이어야 하는데 워크플로에서 얻을 수 없고(fetch-depth: 1), 틀린
    값보다 없는 값이 낫다. 나머지 둘은 Google 이 무시한다. docs/seo.md 참조.
    """
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{SITEMAP_NS}">']
    lines += [f"  <url><loc>{escape(url)}</loc></url>" for url in page_urls()]
    lines += ["</urlset>"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover
    for _target, _text in ((ROBOTS_PATH, robots_txt()), (SITEMAP_PATH, sitemap_xml())):
        _target.write_text(_text, encoding="utf-8")
        print(f"[seo] {_target.relative_to(ROOT)}")
