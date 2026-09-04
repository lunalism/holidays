"""jp_only 조각만 낸다.

파일은 rules/status.py 가 쓴다.
"""

from __future__ import annotations

from datetime import date

from rules.jp_only import feed


def feed_status(*, today: date) -> dict:
    """jp_only 피드 한 벌의 상태. status.json 의 feeds.jp_only 에 그대로 들어간다.

    kr 조각과 같은 꼴로 today 를 받는다 — 범위 끝이 kr 쪽을 거쳐 today 를
    따라 움직인다(rules/jp_only/feed.py 의 feed_range).
    """
    start, end = feed.feed_range(today)
    events = feed.events(start, end)
    provisional = [e for e in events if e.provisional]
    return {
        "path": str(feed.FEED_PATH.relative_to(feed.FEED_PATH.parents[1])),
        "events": len(events),
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "provisional_events": len(provisional),
    }
