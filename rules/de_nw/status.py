"""de_nw 조각만 낸다.

파일은 rules/status.py 가 쓴다. 꼴은 rules/de_hh/status.py 와 같다.
"""

from __future__ import annotations

from datetime import date

from rules.de_nw import feed


def feed_status(*, today: date) -> dict:
    """de_nw 피드 한 벌의 상태. status.json 의 feeds.de_nw 에 그대로 들어간다."""
    start, end = feed.feed_range(today)
    events = feed.events(start, end)
    provisional = [e for e in events if e.provisional]
    return {
        "path": str(feed.FEED_PATH.relative_to(feed.FEED_PATH.parents[1])),
        "events": len(events),
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "provisional_events": len(provisional),
    }
