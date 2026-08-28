"""jp 조각만 낸다.

파일은 rules/status.py 가 쓴다.
"""

from __future__ import annotations

from rules.jp import feed


def feed_status() -> dict:
    """jp 피드 한 벌의 상태. status.json 의 feeds.jp 에 그대로 들어간다.

    kr 조각과 달리 today 를 받지 않는다 — 발행 범위가 상수라 시계가 관여하지
    않는다(rules/jp/feed.py 의 publish() docstring).

    provisional_events 는 센다. jp 는 provisional 이 항상 False 라 결과가 0
    이지만, 0 이라 적어 두는 것과 세는 코드가 0 을 내는 것은 다르다 — 사양이
    바뀌어 잠정 항목이 생기면 적어 둔 0 은 거짓말이 되고, 세는 코드는 따라간다.
    """
    events = feed.events()
    provisional = [e for e in events if e.provisional]
    return {
        "path": str(feed.FEED_PATH.relative_to(feed.FEED_PATH.parents[1])),
        "events": len(events),
        "range": {
            "start": feed.RANGE_START.isoformat(),
            "end": feed.RANGE_END.isoformat(),
        },
        "provisional_events": len(provisional),
    }
