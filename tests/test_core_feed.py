"""발행 — core/feed.py 가 이전 발행본을 지키며 파일을 바꾸는가.

이 모듈은 iCalendar 를 모른다. 그래서 여기 테스트도 .ics 를 짓지 않는다.
바이트를 돌려주는 가짜 build_body 로 돌린다 — 진짜 피드로 확인하는 것은
tests/test_published_feed.py 와 tests/test_jp_feed.py 다.

feeds/ 아래에 쓰지 않는다. 전부 tmp_path 다.
"""

from __future__ import annotations

import ast
import datetime as dt
import os
import pathlib

import pytest

from core import feed as core_feed
from core import ics

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)


@pytest.fixture
def confirmed_domain(monkeypatch):
    """발행이 열린 상태를 명시적으로 둔다.

    tests/test_ics.py 의 같은 이름 픽스처와 같은 취지다 — 지금 값이 True 라
    바꾸는 것이 없지만, 누가 플래그를 내려도 발행 로직 자체의 검증은 계속
    돌아야 한다.
    """
    monkeypatch.setattr(ics, "UID_DOMAIN_CONFIRMED", True)


class Recorder:
    """build_body 에 무엇이 넘어왔는지 받아 적는 가짜."""

    def __init__(self, body=b"NEW", raises=None):
        self.body = body
        self.raises = raises
        self.calls = []

    def __call__(self, previous):
        self.calls.append(previous)
        if self.raises is not None:
            raise self.raises
        return self.body


# ---------------------------------------------------------------------------
# build_body 가 받는 값
# ---------------------------------------------------------------------------


def test_a_missing_file_is_reported_as_none(tmp_path, confirmed_domain):
    """첫 발행은 None 이다. 빈 바이트가 아니다.

    core/ics.py 의 read_published() 가 빈 파일을 거부하므로 둘을 섞으면
    첫 발행이 예외가 된다.
    """
    target = tmp_path / "kr.ics"
    build_body = Recorder()

    assert core_feed.publish(build_body, target) == target
    assert build_body.calls == [None]
    assert target.read_bytes() == b"NEW"


def test_an_existing_file_is_handed_over_as_bytes(tmp_path, confirmed_domain):
    target = tmp_path / "kr.ics"
    target.write_bytes(b"OLD")
    build_body = Recorder()

    core_feed.publish(build_body, target)

    assert build_body.calls == [b"OLD"]
    assert target.read_bytes() == b"NEW"


def test_the_previous_bytes_are_read_before_the_file_is_replaced(tmp_path, confirmed_domain):
    """읽기가 쓰기보다 먼저다. 이 함수가 쪼개지지 않은 이유가 이것이다."""
    target = tmp_path / "kr.ics"
    target.write_bytes(b"OLD")
    seen = []

    def build_body(previous):
        # 만드는 시점에 대상 파일이 아직 이전본 그대로인지 본다.
        seen.append((previous, target.read_bytes()))
        return b"NEW"

    core_feed.publish(build_body, target)
    assert seen == [(b"OLD", b"OLD")]


# ---------------------------------------------------------------------------
# 원자성
# ---------------------------------------------------------------------------


def test_a_failing_build_leaves_the_previous_feed_untouched(tmp_path, confirmed_domain):
    """만들다 죽어도 이전 발행본이 남는다. 되돌릴 방법이 git 밖에 없어서다."""
    target = tmp_path / "kr.ics"
    target.write_bytes(b"OLD")

    with pytest.raises(ics.IcsError, match="터졌다"):
        core_feed.publish(Recorder(raises=ics.IcsError("터졌다")), target)

    assert target.read_bytes() == b"OLD"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["kr.ics"]


def test_the_temp_file_sits_next_to_the_target(tmp_path, monkeypatch, confirmed_domain):
    """임시 파일은 대상과 같은 디렉터리다. /tmp 가 아니다.

    파일시스템이 다르면 os.replace 가 복사로 떨어져 원자성이 깨진다. 그
    순간을 보려면 바꿔치기 직전을 잡아야 하므로 os.replace 를 감싼다.
    """
    target = tmp_path / "feeds" / "kr.ics"
    seen = {}
    real_replace = os.replace

    def spy(src, dst):
        seen["src"] = pathlib.Path(src)
        seen["dst"] = pathlib.Path(dst)
        seen["src_exists"] = seen["src"].exists()
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    core_feed.publish(Recorder(), target)

    assert seen["dst"] == target
    assert seen["src"].parent == target.parent   # /tmp 가 아니라 대상 옆이다
    assert seen["src"].name == ".kr.ics.tmp"
    assert seen["src_exists"] is True

    # 부모 디렉터리가 없어도 만들고, 임시 파일을 남기지 않는다.
    assert target.read_bytes() == b"NEW"
    assert sorted(p.name for p in target.parent.iterdir()) == ["kr.ics"]


# ---------------------------------------------------------------------------
# 호출부 — 이 리팩터가 발행 결과를 바꾸지 않았는가
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("country", ["kr", "jp"])
def test_the_country_wrappers_write_exactly_what_build_returns(
    tmp_path, country, confirmed_domain
):
    """publish() 가 낸 바이트가 build() 결과와 같다.

    publish() 본문이 core 로 올라갔으므로 두 나라 래퍼가 하는 일은 클로저를
    넘기는 것뿐이다. 그 클로저가 자기 build() 를 제대로 부르고 있는지, 그리고
    이전본 없는 첫 발행과 자기 직전 판을 읽는 두 번째 발행이 둘 다 도는지 본다.
    """
    from rules.jp import feed as jp_feed
    from rules.kr import feed as kr_feed

    today = dt.date(2026, 1, 1)
    if country == "kr":
        call = lambda path: kr_feed.publish(today=today, dtstamp=DTSTAMP, path=path)  # noqa: E731
        expected = kr_feed.build(today=today, dtstamp=DTSTAMP, previous=None)
    else:
        call = lambda path: jp_feed.publish(dtstamp=DTSTAMP, path=path)  # noqa: E731
        expected = jp_feed.build(dtstamp=DTSTAMP, previous=None)

    target = tmp_path / f"{country}.ics"

    assert call(target) == target
    first = target.read_bytes()
    assert first == expected

    # 두 번째는 자기 직전 판을 이전 발행본으로 읽는다. 내용이 같으니 바이트도 같다.
    call(target)
    assert target.read_bytes() == first
    assert sorted(p.name for p in tmp_path.iterdir()) == [f"{country}.ics"]


def test_the_country_wrappers_keep_their_public_signatures():
    """바깥 시그니처를 바꾸지 않았다. __main__ 과 워크플로가 이 모양을 부른다."""
    import inspect

    from rules.jp import feed as jp_feed
    from rules.kr import feed as kr_feed

    kr_params = inspect.signature(kr_feed.publish).parameters
    assert list(kr_params) == ["today", "dtstamp", "path"]
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in kr_params.values())
    assert kr_params["path"].default is None

    jp_params = inspect.signature(jp_feed.publish).parameters
    assert list(jp_params) == ["dtstamp", "path"]
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in jp_params.values())
    assert jp_params["path"].default is None


# ---------------------------------------------------------------------------
# 확정 전에는 나가지 않는다
# ---------------------------------------------------------------------------


def test_an_unconfirmed_namespace_neither_reads_nor_writes(tmp_path, monkeypatch):
    """가드가 맨 앞이다. 읽지도 쓰지도 않고 멈춘다."""
    monkeypatch.setattr(ics, "UID_DOMAIN_CONFIRMED", False)
    target = tmp_path / "kr.ics"
    target.write_bytes(b"OLD")
    build_body = Recorder()

    with pytest.raises(ics.IcsError, match="확정되지 않아 발행하지 않는다"):
        core_feed.publish(build_body, target)

    assert build_body.calls == []          # 만들지 않았다
    assert target.read_bytes() == b"OLD"   # 건드리지 않았다
    assert sorted(p.name for p in tmp_path.iterdir()) == ["kr.ics"]


# ---------------------------------------------------------------------------
# 레이어 방향
# ---------------------------------------------------------------------------


def test_core_feed_does_not_import_rules_or_sources():
    """core/ → rules/ 또는 core/ → sources/ 방향은 금지다.

    FEED_PATH 와 build 를 이름으로 참조하면 그 방향이 생긴다. 인자로 받으면
    생기지 않는다는 것을 import 문으로 확인한다.
    """
    path = pathlib.Path(core_feed.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))

    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")

    assert imported, "import 문을 하나도 찾지 못했다 — 검사가 헛돌고 있다"
    for name in imported:
        root = name.split(".")[0]
        assert root not in ("rules", "sources"), f"{name} 을 import 하고 있다"


def test_core_feed_has_no_default_path():
    """path 에 기본값이 없다. core 는 어느 파일인지 모른다."""
    import inspect

    params = inspect.signature(core_feed.publish).parameters
    assert list(params) == ["build_body", "path"]
    assert params["path"].default is inspect.Parameter.empty
