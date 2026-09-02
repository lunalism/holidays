"""한국·일본 합집합 피드 — kr·jp 이벤트가 각각 그대로 실리는가.

발행하지 않는다. build() 로 메모리에서 만들어 본다. feeds/ 아래에 쓰지 않는다.

시계를 읽지 않는다. today 와 dtstamp 를 고정값으로 준다 — kr 형 시그니처라
today 가 필요하다(rules/kr/feed.py 의 feed_range 참조).

이 피드가 지키는 것 셋:
    UID 분리    token 이 kr_jp-{cc}- 접두사를 달아 kr.ics·jp.ics 의 어떤
                UID 와도 겹치지 않는다. 같은 공휴일이라도 별개 이벤트다.
    합집합 불변  접두사(token·summary)를 벗기면 원천 피드의 이벤트와
                같은 집합이다. 여기서 항목을 만들거나 거르지 않는다.
    범위 min    끝은 kr 의 feed_range(today) 끝과 jp 의 RANGE_END 중
                작은 쪽이다. 한쪽만 있는 구간을 실으면 다른 나라의
                공휴일이 없는 것처럼 읽힌다.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import re
from collections import Counter

import pytest

from rules.jp import feed as jp_feed
from rules.kr import feed as kr_feed
from rules.kr_jp import feed

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)


@pytest.fixture(scope="module")
def events():
    return feed.events(*feed.feed_range(TODAY))


@pytest.fixture(scope="module")
def rendered():
    """폴딩을 푼 .ics 본문. 한 속성이 한 줄이 되게 한다(test_jp_feed.py 참조)."""
    raw = feed.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
    return raw.replace("\r\n ", "").replace("\r\n\t", "")


def _uids(text: str) -> list:
    # 줄 끝이 CRLF 라 $ 앞에 \r 이 남는다. 값만 본다.
    return [u.strip() for u in re.findall(r"^UID:(.+)$", text, re.MULTILINE)]


# ---------------------------------------------------------------------------
# UID — 피드 안에서 유일하고, 발행된 kr·jp 와 겹치지 않는다
# ---------------------------------------------------------------------------


def test_every_uid_is_unique(rendered):
    uids = _uids(rendered)
    assert uids, "이벤트가 하나도 없다"
    assert len(uids) == len(set(uids))
    assert all(u.endswith("@holidays.lunalism.com") for u in uids)


@pytest.mark.published_artifact
def test_no_uid_collides_with_the_published_kr_and_jp_feeds(rendered):
    """UID 는 영구값이다. kr.ics·jp.ics 에 이미 나가 있는 UID 를 이 피드가
    다시 쓰면, 세 피드를 함께 구독한 캘린더에서 같은 UID 가 서로를 덮어쓴다.

    kr.ics 와 jp.ics 사이의 기존 겹침 16건(신정·어린이날)은 여기서 보지
    않는다 — 이미 발행된 값이라 고칠 수 없고, 이 피드가 지킬 것은 자신이
    거기에 하나도 더하지 않는다는 것뿐이다.
    """
    published = set()
    for path in (kr_feed.FEED_PATH, jp_feed.FEED_PATH):
        published.update(_uids(path.read_text(encoding="utf-8")))
    assert published, "발행본에서 UID 를 하나도 읽지 못했다"
    assert set(_uids(rendered)) & published == set()


# ---------------------------------------------------------------------------
# SUMMARY — 나라 접두사
# ---------------------------------------------------------------------------


def test_every_summary_carries_a_country_prefix(events):
    assert events, "이벤트가 하나도 없다"
    bad = [
        e for e in events if not (e.summary.startswith("[KR] ") or e.summary.startswith("[JP] "))
    ]
    assert bad == []


# ---------------------------------------------------------------------------
# 합집합 불변 — 접두사를 벗기면 원천과 같다
# ---------------------------------------------------------------------------


def _stripped(event):
    """token·summary 의 접두사를 벗긴 Event. 나머지 필드는 손대지 않는다."""
    for cc, tag in (("kr", "[KR] "), ("jp", "[JP] ")):
        token_prefix = f"kr_jp-{cc}-"
        if event.token.startswith(token_prefix):
            assert event.summary.startswith(tag), (
                f"token 은 {cc} 인데 summary 접두사가 다르다: {event.summary!r}"
            )
            return dataclasses.replace(
                event,
                token=event.token[len(token_prefix) :],
                summary=event.summary[len(tag) :],
            )
    raise AssertionError(f"접두사 꼴이 아니다: token={event.token!r}")


def test_the_union_preserves_both_feeds_events(events):
    """접두사를 벗긴 이벤트 집합 == 범위 내 kr 이벤트 ∪ 범위 내 jp 이벤트.

    Counter 비교라 건수 등식(len == kr + jp)과 잠정 건수 등식이 함께
    따라온다 — provisional 필드까지 같아야 통과한다.
    """
    start, end = feed.feed_range(TODAY)
    expected = kr_feed.events(start, end) + [
        e for e in jp_feed.events() if start <= e.day <= end
    ]
    assert Counter(_stripped(e) for e in events) == Counter(expected)


# ---------------------------------------------------------------------------
# 발행 범위 — 두 피드 중 짧은 쪽
# ---------------------------------------------------------------------------


def test_the_range_end_is_the_smaller_of_the_two_feeds():
    """min 이 실제로 min 인지, today 를 두 개 골라 양쪽 다 밟는다."""
    # jp 가 작은 경우. 2026 기준 kr 끝은 2031-12-31 이다.
    start, end = feed.feed_range(dt.date(2026, 1, 1))
    assert start == dt.date(2020, 1, 1)
    assert end == jp_feed.RANGE_END
    assert end < kr_feed.feed_range(dt.date(2026, 1, 1))[1]

    # kr 이 작은 경우. 2020 기준 kr 끝은 2025-12-31 < 2027-11-23 이다.
    start, end = feed.feed_range(dt.date(2020, 6, 1))
    kr_end = kr_feed.feed_range(dt.date(2020, 6, 1))[1]
    assert start == dt.date(2020, 1, 1)
    assert end == kr_end
    assert kr_end < jp_feed.RANGE_END
