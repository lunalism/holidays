"""README 구독 표는 발행본과 어긋나지 않는다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    README 의 구독 표에 있는 주소는 전부 실재하는 발행본을 가리키고,
    실재하는 발행본은 전부 표에 있다.

README 는 랜딩보다 먼저 읽히는 얼굴이다. 그런데 표가 손으로 관리되는 동안
피드는 여섯에서 열다섯으로 늘었고, 표는 여섯에 멈춰 있었다 — 구독자가 주 피드
아홉의 주소를 README 어디에서도 얻을 수 없었다. 그 상태를 잡는 것이 없었기
때문이다.

랜딩은 tests/test_landing.py 가 같은 일을 한다. 목록이 사는 곳이 다르므로
(랜딩은 feed-data 블록, README 는 마크다운 표) 파일을 나누고, 묶는 대상은
같게 둔다 — feeds/*.ics 와 CNAME 이다.

--------------------------------------------------------------------------
왜 status.json 이 아니라 feeds/ 인가
--------------------------------------------------------------------------
표가 약속하는 것은 "이 주소로 받을 수 있다" 이고, 그것을 결정하는 것은 Pages
가 서빙하는 파일의 실재다. status.json 은 그 파일에 대한 주장이지 파일 자체가
아니다. 둘은 tests/test_landing.py 가 이미 묶고 있다.

--------------------------------------------------------------------------
published_artifact 마커
--------------------------------------------------------------------------
커밋된 산출물(feeds/)을 읽는다. 규칙을 바꾸고 발행본·README 를 갱신하기 전의
찰나에 깨지는 것이 정상이다. 마커의 정의 그대로라 발행 워크플로에서는
제외되고 PR 워크플로(ci.yml)가 돌린다.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.published_artifact

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
FEEDS_DIR = ROOT / "feeds"
CNAME = ROOT / "CNAME"

# 구독 절만 본다. 호환성 원칙 절에도 주소가 있어 문서 전체에서 긁으면 섞인다.
SUBSCRIBE_SECTION = re.compile(r"^## 구독\s*$(.*?)^## ", re.MULTILINE | re.DOTALL)

# 표 안의 주소는 백틱 안에 있다.
BACKTICKED_URL = re.compile(r"`(https://[^`\s]+)`")


def _table_urls() -> list[str]:
    """구독 절의 표 행에서 주소를 나온 순서대로."""
    text = README.read_text(encoding="utf-8")
    match = SUBSCRIBE_SECTION.search(text)
    assert match, "README 에 '## 구독' 절이 없다(또는 뒤따르는 절이 없다)"
    rows = [line for line in match.group(1).splitlines() if line.lstrip().startswith("|")]
    assert rows, "구독 절에 표 행이 없다"
    return [url for row in rows for url in BACKTICKED_URL.findall(row)]


def test_every_published_feed_is_in_the_table_and_vice_versa():
    # 양방향으로 잡는다. 발행본이 있는데 표에 없으면 구독자가 주소를 얻을 데가
    # 없고, 표에 있는데 발행본이 없으면 죽은 주소를 건네주는 것이다.
    listed = {url.rsplit("/", 1)[-1] for url in _table_urls()}
    published = {path.name for path in FEEDS_DIR.glob("*.ics")}
    assert listed == published


def test_the_table_lists_each_feed_once():
    # 집합 비교는 중복을 삼킨다. 같은 피드가 두 줄에 있으면 위 테스트는
    # 통과하지만 표는 틀린 상태다.
    urls = _table_urls()
    assert len(urls) == len(set(urls)), urls


def test_every_url_is_assembled_from_the_cname():
    # 주소는 site base + "feeds/" + 파일명이다. CNAME 이 이 도메인을 이 저장소에
    # 붙이고 Pages 가 브랜치 루트를 서빙하므로 feeds/<파일> 이 그대로 경로가
    # 된다. 이 규칙에서 벗어난 주소는 구독자에게 죽은 링크가 된다.
    base = f"https://{CNAME.read_text(encoding='utf-8').strip()}/feeds/"
    for url in _table_urls():
        assert url.startswith(base), url
        assert url.endswith(".ics"), url
        assert "/" not in url[len(base) :], url
