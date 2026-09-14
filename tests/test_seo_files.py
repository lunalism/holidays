"""robots.txt 와 sitemap.xml 은 같은 URL 집합을 말한다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    robots.txt 의 Allow 경로 집합, sitemap.xml 의 <loc> 집합, 그리고
    languages() × page_path() 로 유도한 집합 — 셋이 같다.

색인 대상은 docs/seo.md 「색인 대상」이 정한다: languages() × page_path() 뿐이고
개별 URL 을 열거하지 않는다. robots.txt 와 sitemap.xml 은 그 집합을 각자의
문법으로 적은 것이라 서로 어긋나면 안 된다 — 한쪽에만 있는 URL 은 "크롤은
허용됐는데 sitemap 에 없다" 또는 "sitemap 에 있는데 크롤이 막혔다" 가 된다.

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

from landing import render

ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# Allow 값은 정확 일치를 위해 `$` 로 끝난다. 집합 비교에서는 그것을 뗀다.
ALLOW_LINE = re.compile(r"^Allow:\s*(\S+?)\$?\s*$", re.MULTILINE)


def _expected_paths() -> set[str]:
    """docs/seo.md 「색인 대상」 — languages() × page_path()."""
    return {render.page_path(lang) for lang in render.languages()}


def _robots_allow_paths(text: str) -> set[str]:
    return set(ALLOW_LINE.findall(text))


def _sitemap_locs(text: str) -> set[str]:
    root = ET.fromstring(text)
    return {loc.text for loc in root.iter(f"{{{SITEMAP_NS}}}loc")}


@pytest.mark.published_artifact
def test_robots_allow_and_sitemap_loc_are_the_same_set_as_the_index_targets():
    assert ROBOTS.is_file(), "robots.txt 가 없다 — 생성해서 커밋할 것"
    assert SITEMAP.is_file(), "sitemap.xml 이 없다 — 생성해서 커밋할 것"
    expected = _expected_paths()
    allow = _robots_allow_paths(ROBOTS.read_text(encoding="utf-8"))
    base = render._site_base().rstrip("/")
    locs = {loc.removeprefix(base) for loc in _sitemap_locs(SITEMAP.read_text(encoding="utf-8"))}
    assert allow == expected, f"robots.txt Allow {sorted(allow)} ≠ 색인 대상 {sorted(expected)}"
    assert locs == expected, f"sitemap.xml <loc> {sorted(locs)} ≠ 색인 대상 {sorted(expected)}"
