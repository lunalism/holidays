"""robots.txt 와 sitemap.xml 은 같은 소스에서 나온 URL 집합을 말한다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    robots.txt 의 Allow 집합 == 색인 대상 집합 ∪ 크롤 전용 집합
    sitemap.xml 의 <loc> 집합 == 색인 대상 집합

두 축은 docs/seo.md 「색인 대상」이 가른다.

- 색인 대상: 검색 결과에 나오기를 기대하는 URL. languages() × page_path() 로
  유도하고 개별 URL 을 열거하지 않는다.
- 크롤 전용: 색인되기를 기대하지 않지만 크롤러가 가져가야 하는 URL. 상수다.
  현재 /sitemap.xml 하나 — Sitemap: 지시자가 가리키는 URL 의 취득에 Google 이
  robots 규칙을 적용하므로(Google robots.txt 사양 sitemap 항목 "provided it
  isn't disallowed for crawling"), Allow 가 없으면 Disallow: / 에 걸린다.

크롤 전용을 "예외" 로 빼고 비교하지 않는다. 예외로 두면 다음 항목이 같은
길로 조용히 샌다. 합집합 모델로 두면 Allow 에 무엇이 더 들어와도 두 상수
집합 중 하나에 있어야 하고, 없으면 여기서 걸린다.

--------------------------------------------------------------------------
마커
--------------------------------------------------------------------------
커밋된 robots.txt·sitemap.xml 을 읽는 검사는 published_artifact 다. 두 파일은
발행 파이프라인의 산출물이고(publish.yml), 언어를 늘리고 재생성하지 않은
찰나에 깨지는 것이 정상이다 — tests/test_landing_render.py 와 같은 자리.

생성기의 성질(결정성, Allow 가 하위 경로를 열지 않음, XML 파싱)은 생성기만
부르고 커밋본을 읽지 않으므로 마커가 없다 — tests/test_landing_contract.py
와 같은 자리. 함수 단위로 나눠 붙인다.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from landing import render, seo

ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# Allow 값은 정확 일치를 위해 `$` 로 끝난다. 집합 비교에서는 그것을 뗀다.
ALLOW_LINE = re.compile(r"^Allow:\s*(\S+?)\$?\s*$", re.MULTILINE)


def _index_paths() -> set[str]:
    """색인 대상 — languages() × page_path(). docs/seo.md 「색인 대상」."""
    return {render.page_path(lang) for lang in render.languages()}


# 크롤 전용. 언어에서 유도되지 않는 상수라 여기 직접 적는다 — 생성기의 상수를
# import 하면 생성기가 무엇을 넣든 통과한다.
CRAWL_ONLY_PATHS = {"/sitemap.xml"}


def _robots_allow_paths(text: str) -> set[str]:
    return set(ALLOW_LINE.findall(text))


def _sitemap_locs(text: str) -> set[str]:
    root = ET.fromstring(text)
    return {loc.text for loc in root.iter(f"{{{SITEMAP_NS}}}loc")}


@pytest.mark.published_artifact
def test_robots_allow_is_index_targets_plus_crawl_only():
    assert ROBOTS.is_file(), "robots.txt 가 없다 — 생성해서 커밋할 것"
    expected = _index_paths() | CRAWL_ONLY_PATHS
    allow = _robots_allow_paths(ROBOTS.read_text(encoding="utf-8"))
    assert allow == expected, (
        f"robots.txt Allow {sorted(allow)} ≠ 색인 대상 ∪ 크롤 전용 {sorted(expected)}"
    )


@pytest.mark.published_artifact
def test_sitemap_loc_is_exactly_index_targets():
    """<loc> 는 색인 대상뿐이다. 크롤 전용(/sitemap.xml 자신)은 들어가지 않는다."""
    assert SITEMAP.is_file(), "sitemap.xml 이 없다 — 생성해서 커밋할 것"
    expected = _index_paths()
    base = render._site_base().rstrip("/")
    locs = {loc.removeprefix(base) for loc in _sitemap_locs(SITEMAP.read_text(encoding="utf-8"))}
    assert locs == expected, f"sitemap.xml <loc> {sorted(locs)} ≠ 색인 대상 {sorted(expected)}"
    assert not (locs & CRAWL_ONLY_PATHS), "크롤 전용 경로가 sitemap 에 들어 있다"


# ---------------------------------------------------------------------------
# 생성기의 성질. 커밋본을 읽지 않으므로 마커 없음.
# ---------------------------------------------------------------------------


def test_generation_is_deterministic():
    """같은 입력이면 같은 바이트. 시계를 읽으면 여기서 걸린다."""
    assert seo.robots_txt() == seo.robots_txt()
    assert seo.sitemap_xml() == seo.sitemap_xml()


def _robots_allows(text: str, path: str) -> bool:
    """Google robots.txt 문서와 RFC 9309 가 정한 판정을 그대로 옮긴 것.

    규칙: 경로가 가장 긴(가장 구체적인) 규칙이 이기고, 길이가 같으면 덜
    제한적인(Allow) 규칙이 이긴다. `$` 는 URL 의 끝이다. 어느 규칙에도 맞지
    않으면 허용이다.

    크롤러가 아니라 문서의 판정 모델이다. 고정하려는 것은 "robots.txt 가 이
    문서의 규칙 아래서 어떻게 읽히는가" 이지 특정 크롤러의 구현이 아니다.

    생성기가 내는 부분집합 — 단일 그룹, `*` 없음, ASCII 경로 — 에 대한
    모델이다. 생성기가 그 밖의 규칙을 내게 되면 이 모델도 함께 넓힌다.
    """
    best: tuple[int, bool] | None = None  # (규칙 길이, 허용 여부)
    for line in text.splitlines():
        kind, _, value = line.partition(":")
        kind, value = kind.strip().lower(), value.strip()
        if kind not in {"allow", "disallow"} or not value:
            continue
        anchored = value.endswith("$")
        pattern = value.removesuffix("$")
        matched = path == pattern if anchored else path.startswith(pattern)
        if not matched:
            continue
        candidate = (len(value), kind == "allow")
        if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1]):
            best = candidate
    return True if best is None else best[1]


def test_robots_default_is_disallow_and_every_allow_is_anchored():
    """허용목록의 형태. Disallow: / 가 있고 Allow 는 전부 `$` 로 끝난다."""
    text = seo.robots_txt()
    assert "Disallow: /\n" in text
    allows = [line for line in text.splitlines() if line.startswith("Allow:")]
    assert allows, "Allow 가 하나도 없다"
    assert all(line.endswith("$") for line in allows), allows


@pytest.mark.parametrize("path", sorted(_index_paths()))
def test_robots_allows_each_index_target(path):
    assert _robots_allows(seo.robots_txt(), path)


@pytest.mark.parametrize("path", sorted(CRAWL_ONLY_PATHS))
def test_robots_allows_each_crawl_only_path_by_its_own_line(path):
    """크롤 전용 경로는 자기 Allow 줄로 허용된다 — Allow: /$ 가 여는 것이 아니다.

    아래 하위 경로 검사가 Allow: /$ 는 /index.html 도 열지 않음을 고정하므로,
    /sitemap.xml 이 허용된다면 그것은 자기 줄 때문일 수밖에 없다. 그 줄의
    존재를 여기서 직접 본다.
    """
    text = seo.robots_txt()
    assert f"Allow: {path}$" in text.splitlines(), f"Allow: {path}$ 줄이 없다"
    assert _robots_allows(text, path)


@pytest.mark.parametrize(
    "path",
    [
        # 루트 Allow 가 하위 경로를 열지 않는다 — 허용목록의 핵심 위험.
        # /sitemap.xml 이 여기 없는 것은 자기 줄로 허용되기 때문이다(위 검사).
        "/index.html",
        "/feeds/kr.ics",
        "/status.json",
        "/data/jp/2026.yaml",
        "/landing/template.html",
        "/docs/seo.md",
        # 언어 디렉터리 Allow 도 마찬가지.
        "/en/index.html",
        "/ja/anything",
    ],
)
def test_robots_allow_does_not_open_subpaths(path):
    assert not _robots_allows(seo.robots_txt(), path)


def test_sitemap_parses_and_has_only_loc():
    """XML 로 파싱되고, <url> 아래에 <loc> 말고는 없다 — lastmod 도 없다."""
    root = ET.fromstring(seo.sitemap_xml())
    assert root.tag == f"{{{SITEMAP_NS}}}urlset"
    urls = list(root)
    assert urls, "<url> 이 없다"
    for url in urls:
        assert [child.tag for child in url] == [f"{{{SITEMAP_NS}}}loc"], [c.tag for c in url]
    assert "lastmod" not in seo.sitemap_xml()


# ---------------------------------------------------------------------------
# 커밋된 산출물의 최신성. tests/test_landing_render.py 와 같은 질문.
# ---------------------------------------------------------------------------


@pytest.mark.published_artifact
@pytest.mark.parametrize(
    ("path", "generate"),
    [(ROBOTS, seo.robots_txt), (SITEMAP, seo.sitemap_xml)],
    ids=["robots.txt", "sitemap.xml"],
)
def test_the_committed_file_is_reproducible(path, generate):
    assert path.is_file(), f"{path.name} 이 없다 — 생성해서 커밋할 것"
    assert path.read_text(encoding="utf-8") == generate(), (
        f"커밋된 {path.name} 이 지금 landing/ 으로 재현되지 않는다. 갱신할 것:\n"
        "  uv run python -m landing.seo"
    )
