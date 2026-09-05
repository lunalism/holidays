"""de 조각만 낸다.

파일은 rules/status.py 가 쓴다.
"""

from __future__ import annotations

from datetime import date

from rules.de import feed


def feed_status(*, today: date) -> dict:
    """de 피드 한 벌의 상태. status.json 의 feeds.de 에 그대로 들어간다.

    kr 조각과 같은 꼴로 today 를 받는다 — 범위 끝이 today 를 따라 움직인다.

    provisional_events 는 센다. de 는 provisional 이 항상 False 라 결과가 0
    이지만, 0 이라 적어 두는 것과 세는 코드가 0 을 내는 것은 다르다
    (rules/jp/status.py 와 같은 이유).
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
