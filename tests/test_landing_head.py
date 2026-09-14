"""랜딩 <head> 의 URL 표기는 전부 _site_base() 에서 유도된다.

canonical·hreflang·og:image·og:url — 절대 URL 이 필요한 자리 넷이다. 근거는
docs/seo.md 「언어면 관계」. 이 파일이 고정하는 것은 값이 아니라 **유도식**이다:
CNAME 이 바뀌면 넷이 같이 바뀌어야 하고, 하나라도 리터럴 도메인이면 그 자리만
옛 주소에 남는다.

render.render(lang) 을 직접 부른다 — 커밋된 페이지가 아니라 지금의 landing/ 이
무엇을 내는가를 본다. 커밋본이 이것과 같은지는 tests/test_landing_render.py 가
따로 본다(published_artifact). 그래서 여기는 마커가 없고 발행 run 에서도 돈다.

og:locale·twitter:* 는 여기 없다 — 링크 프리뷰 축이고 docs/holiday_16.md §5 의
OG 표면 점검이 맡는다.
"""

from __future__ import annotations

import re

import pytest

from landing import render

LANGS = render.languages()
every_page = pytest.mark.parametrize("lang", LANGS)

HEAD = re.compile(r"<head>(.*?)</head>", re.DOTALL)
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]*)">')
HREFLANG = re.compile(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)">')
META = r'<meta (?:property|name)="{}" content="([^"]*)">'


def _head(lang: str) -> str:
    m = HEAD.search(render.render(lang))
    assert m, "<head> 가 없다"
    return m.group(1)


def _meta(head: str, name: str) -> str:
    found = re.findall(META.format(re.escape(name)), head)
    assert len(found) == 1, f"{name} 이 {len(found)} 개다"
    return found[0]


@every_page
def test_each_page_has_one_self_canonical_equal_to_og_url(lang):
    # /index.html 도 / 와 같은 200 이라 canonical 이 없으면 같은 문서가 두 URL 로
    # 노출된다. 값은 og:url 과 같은 것을 쓴다 — 같은 값을 두 번 계산하지 않는다.
    head = _head(lang)
    canonical = CANONICAL.findall(head)
    assert len(canonical) == 1, f"canonical 이 {len(canonical)} 개다"
    assert canonical[0] == _meta(head, "og:url")
    assert canonical[0] == render._site_base().rstrip("/") + render.page_path(lang)


@every_page
def test_hreflang_set_is_every_language_plus_x_default(lang):
    # 모든 면이 같은 목록을 갖는다 — 자기 자신도 포함한다(hreflang 은 상호 참조라
    # 자기 항목이 빠지면 무효다).
    links = dict(HREFLANG.findall(_head(lang)))
    assert set(links) == set(LANGS) | {"x-default"}
    for other in LANGS:
        assert links[other] == render._site_base().rstrip("/") + render.page_path(other)


@every_page
def test_x_default_points_to_en(lang):
    # 어느 언어도 맞지 않는 방문자의 행선지. 루트가 ko 인 것은 처음 발행된 URL
    # 을 바꾸지 않아서이지 기본 언어라서가 아니다 — ROOT_LANG 에서 유도하지 않는다.
    links = dict(HREFLANG.findall(_head(lang)))
    assert links["x-default"] == render._site_base().rstrip("/") + "/en/"
    assert links["x-default"] == links["en"]


@every_page
def test_hreflang_values_carry_no_region(lang):
    # locale 의 `locale` 키(ko-KR 형)가 아니라 `lang` 이다. 지역별 페이지가 없다.
    for value, _ in HREFLANG.findall(_head(lang)):
        assert "-" not in value or value == "x-default", value


@every_page
def test_og_image_is_the_site_base_plus_assets_og_png(lang):
    assert _meta(_head(lang), "og:image") == render._site_base() + "assets/og.png"


def test_the_template_carries_no_literal_domain_in_head():
    # 유도의 반대편 — 소스에 도메인이 글자로 있으면 CNAME 을 바꿔도 그 자리는 남는다.
    head = HEAD.search(render.TEMPLATE_PATH.read_text(encoding="utf-8")).group(1)
    assert "https://" not in head, "template.html 의 <head> 에 절대 URL 리터럴이 있다"


@every_page
def test_every_head_url_follows_the_cname(lang, tmp_path, monkeypatch):
    # 유도식의 증명 — CNAME 을 바꾸면 넷이 전부 따라온다. 하나라도 남으면 그
    # 자리가 리터럴이다.
    (tmp_path / "CNAME").write_text("example.test\n", encoding="utf-8")
    monkeypatch.setattr(render, "CNAME_PATH", tmp_path / "CNAME")
    head = _head(lang)
    urls = (
        CANONICAL.findall(head)
        + [href for _, href in HREFLANG.findall(head)]
        + [_meta(head, "og:image"), _meta(head, "og:url")]
    )
    assert len(urls) == 1 + len(LANGS) + 1 + 2
    assert all(u.startswith("https://example.test/") for u in urls), urls
    assert "holidays.lunalism.com" not in head
