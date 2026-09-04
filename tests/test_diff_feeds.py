"""차집합 피드 kr_only·jp_only — 상대국이 쉬지 않는 날만 실리는가.

발행하지 않는다. build() 로 메모리에서 만들어 본다. feeds/ 아래에 쓰지 않는다.

시계를 읽지 않는다. today 와 dtstamp 를 고정값으로 준다 — kr 형 시그니처라
today 가 필요하다(rules/kr/feed.py 의 feed_range 참조).

두 피드가 지키는 것:
    정의        kr_only 의 날짜 집합과 범위 내 jp 원천의 날짜 집합은 서로소다.
                jp_only 는 대칭.
    분할        범위 내 kr 원천 날짜 = kr_only 날짜 ⊔ (kr ∩ jp 날짜).
                거른 것과 남긴 것을 합치면 원천이고, 둘은 겹치지 않는다.
    날짜 단위   판정은 날짜다. 이름·token 이 달라도 날짜가 겹치면 빠진다.
                2021-02-11(설날 연휴 / 建国記念の日)이 그 대표이고,
                2026-01-01(신정 / 元日)은 같은 token 유형의 대표다.
    UID 분리    token 이 kr_only-kr- / jp_only-jp- 접두사를 달아 기존 세
                피드의 어떤 UID 와도 겹치지 않는다.
    범위        kr_jp 와 같은 (RANGE_START, min(kr 끝, jp 끝)) 이다.
"""

from __future__ import annotations

import datetime as dt
import re

import pytest

from rules.jp import feed as jp_feed
from rules.jp_only import feed as jp_only
from rules.kr import feed as kr_feed
from rules.kr_jp import feed as kr_jp_feed
from rules.kr_only import feed as kr_only

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# (피드 모듈, 자국 코드, 자국 원천 날짜 함수, 상대국 원천 날짜 함수).
# 원천 날짜는 전부 범위로 거른다 — jp 의 events() 는 인자를 받지 않는다.


def _kr_days(start, end):
    return {e.day for e in kr_feed.events(start, end)}


def _jp_days(start, end):
    return {e.day for e in jp_feed.events() if start <= e.day <= end}


FEEDS = [
    pytest.param(kr_only, "kr", _kr_days, _jp_days, id="kr_only"),
    pytest.param(jp_only, "jp", _jp_days, _kr_days, id="jp_only"),
]


def _rendered(feed) -> str:
    """폴딩을 푼 .ics 본문. 한 속성이 한 줄이 되게 한다(test_jp_feed.py 참조)."""
    raw = feed.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
    return raw.replace("\r\n ", "").replace("\r\n\t", "")


def _uids(text: str) -> list:
    # 줄 끝이 CRLF 라 $ 앞에 \r 이 남는다. 값만 본다.
    return [u.strip() for u in re.findall(r"^UID:(.+)$", text, re.MULTILINE)]


# ---------------------------------------------------------------------------
# a. 정의 — 자국 피드의 날짜와 상대국 원천의 날짜는 서로소
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("feed, cc, own_days, other_days", FEEDS)
def test_no_date_in_the_feed_is_a_holiday_of_the_other_country(feed, cc, own_days, other_days):
    start, end = feed.feed_range(TODAY)
    events = feed.events(start, end)
    assert events, "이벤트가 하나도 없다"
    assert {e.day for e in events} & other_days(start, end) == set()


# ---------------------------------------------------------------------------
# b. 분할 — 원천 = 피드 ⊔ 교집합
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("feed, cc, own_days, other_days", FEEDS)
def test_the_feed_and_the_shared_dates_partition_the_source(feed, cc, own_days, other_days):
    """거른 날짜와 남긴 날짜를 합치면 원천이고, 둘은 겹치지 않는다.

    교집합이 비어 있으면 이 단언은 항등식이라 아무것도 검사하지 않는다 —
    그래서 교집합이 실제로 있다는 것을 먼저 못 박는다.
    """
    start, end = feed.feed_range(TODAY)
    own = own_days(start, end)
    shared = own & other_days(start, end)
    assert shared, "두 나라가 같은 날 쉬는 날짜가 하나도 없다 — 분할 검사가 항등식이 된다"

    kept = {e.day for e in feed.events(start, end)}
    assert kept & shared == set()
    assert kept | shared == own


# ---------------------------------------------------------------------------
# c. 회귀 픽스처 — 날짜 단위 판정의 대표 넷
# ---------------------------------------------------------------------------

# 이름·token 이 다른데 날짜만 겹치는 유형. 설날 연휴 / 建国記念の日,
# 추석 연휴 / 敬老の日. 날짜가 아니라 token 으로 판정하면 양쪽에 남는다.
DIFFERENT_NAME_SAME_DAY = [dt.date(2021, 2, 11), dt.date(2024, 9, 16)]

# 같은 token 유형. 신정 / 元日, 어린이날 / こどもの日.
SAME_TOKEN_SAME_DAY = [dt.date(2026, 1, 1), dt.date(2026, 5, 5)]


@pytest.mark.parametrize("day", DIFFERENT_NAME_SAME_DAY + SAME_TOKEN_SAME_DAY)
def test_a_shared_date_appears_in_neither_feed(day):
    start, end = kr_only.feed_range(TODAY)
    assert start <= day <= end, "픽스처가 발행 범위 밖이다"
    # 픽스처가 실제로 양쪽 원천에 있는 날인지 먼저 본다. 아니면 아래 부재
    # 단언은 아무것도 검사하지 않는다.
    assert day in _kr_days(start, end)
    assert day in _jp_days(start, end)

    assert day not in {e.day for e in kr_only.events(start, end)}
    assert day not in {e.day for e in jp_only.events(start, end)}


# ---------------------------------------------------------------------------
# d. UID — {feed}-{cc}-{원천 token} 에서 유도
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("feed, cc, own_days, other_days", FEEDS)
def test_every_uid_is_derived_from_the_prefixed_token(feed, cc, own_days, other_days):
    """UID 는 {YYYYMMDD}-{feed}-{cc}-{원천 token}@holidays.lunalism.com.

    접두사를 벗긴 token 이 그 날짜의 원천 token 과 같아야 한다 — 접두사만
    붙이고 원천 token 을 손대지 않았다는 것까지 여기서 본다.
    """
    prefix = f"{feed.__name__.rsplit('.', 2)[-2]}-{cc}-"
    assert prefix in (f"kr_only-{cc}-", f"jp_only-{cc}-"), prefix

    uids = _uids(_rendered(feed))
    assert uids, "이벤트가 하나도 없다"
    assert len(uids) == len(set(uids))

    start, end = feed.feed_range(TODAY)
    source = kr_feed.events(start, end) if cc == "kr" else jp_feed.events()
    expected = {f"{e.day:%Y%m%d}-{prefix}{e.token}@holidays.lunalism.com" for e in source}
    pattern = re.compile(rf"^\d{{8}}-{re.escape(prefix)}.+@holidays\.lunalism\.com$")
    for uid in uids:
        assert pattern.match(uid), uid
        assert uid in expected, f"원천 token 에서 유도되지 않은 UID: {uid}"

    tag = f"[{cc.upper()}] "
    bad = [e for e in feed.events(start, end) if not e.summary.startswith(tag)]
    assert bad == []


# ---------------------------------------------------------------------------
# e. 범위 — kr_jp 와 같다
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("feed, cc, own_days, other_days", FEEDS)
@pytest.mark.parametrize(
    "today",
    [
        dt.date(2026, 1, 1),  # jp 가 작은 경우. kr 끝은 2031-12-31.
        dt.date(2020, 6, 1),  # kr 이 작은 경우. kr 끝은 2025-12-31 < 2027-11-23.
    ],
)
def test_the_range_is_the_same_as_kr_jp(feed, cc, own_days, other_days, today):
    start, end = feed.feed_range(today)
    assert (start, end) == kr_jp_feed.feed_range(today)
    assert start == dt.date(2020, 1, 1)
    assert end == min(kr_feed.feed_range(today)[1], jp_feed.RANGE_END)
