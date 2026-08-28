"""kr 조각만 낸다.

파일은 rules/status.py 가 쓴다.
"""

from __future__ import annotations

from datetime import date

from core import ics
from rules.kr import feed
from rules.kr import holiday_calendar as hc
from sources.kr import key_expiry


def feed_status(*, today: date) -> dict:
    """kr 피드 한 벌의 상태. status.json 의 feeds.kr 에 그대로 들어간다."""
    start, end = feed.feed_range(today)
    events = feed.events(start, end)
    provisional = [e for e in events if e.provisional]
    return {
        "path": str(feed.FEED_PATH.relative_to(feed.FEED_PATH.parents[1])),
        "events": len(events),
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "provisional_events": len(provisional),
    }


def top_level_sections(*, today: date) -> dict:
    """status.json 의 최상위 절들 — coverage, uid, verification, kasi_key.

    kr 전용이지만 아직 국가 키 밑으로 들어가지 않았다. jp 검증 상태를 status 에
    실을 때 함께 옮긴다.
    """
    coverage = hc.coverage()["effective"]
    return {
        "coverage": {
            # 규칙 개정을 확인한 시점. 이후 항목은 provisional 로 나간다.
            "confirmed_through": (
                coverage.confirmed_through.isoformat() if coverage.confirmed_through else None
            ),
            # 지정 공휴일을 소스와 맞춘 시점. 이후는 항목이 늘 수 있다.
            "designated_last_synced_at": (
                coverage.last_synced_at.isoformat() if coverage.last_synced_at else None
            ),
            "start": coverage.start.isoformat(),
        },
        "uid": {
            "domain": ics.UID_DOMAIN,
            # False 인 동안 publish() 가 거부한다. 밖에서도 보이게 싣는다.
            "confirmed": ics.UID_DOMAIN_CONFIRMED,
        },
        "verification": {
            # 법령·관보 원문 대조가 남은 항목 수. 랜딩 페이지(index.html)가
            # 이 값을 읽어 "확인 대기: N건" 으로 띄운다.
            #
            # 표별 내역을 함께 싣는다. 숫자 하나만 두면 그것이 무엇을 세는지
            # 밖에서 확인할 방법이 없고, 확인할 수 없는 숫자를 공개 페이지에
            # 띄우는 것은 이 저장소가 하려는 것과 반대다.
            # 분모. 랜딩이 "규칙표 N 건 중 M 건 확인 대기" 로 쓴다.
            #
            # feed.events 를 분모로 쓰면 안 된다. 그건 VEVENT 개수라 같은
            # 공휴일이 해마다 다시 세어지고, 규칙표 항목과 단위가 다르다.
            # hc.verifiable_items() docstring 참조.
            "item_count": hc.verifiable_item_count(),
            "unverified_count": hc.unverified_count(),
            "unverified_by_table": {
                name: len(items) for name, items in hc.unverified().items()
            },
        },
        "kasi_key": {
            "expires_on": key_expiry.expires_on().isoformat(),
            "days_left": key_expiry.days_left(today),
            "min_days": key_expiry.MIN_DAYS,
        },
    }
