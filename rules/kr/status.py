"""status.json — 지금 이 저장소가 무엇을 주장하고 있는지 한 파일로.

--------------------------------------------------------------------------
왜 매번 커밋하는가
--------------------------------------------------------------------------
두 가지 때문이다.

1. 갱신이 끊긴 것을 밖에서 알 수 있어야 한다.
   발행이 실패해도 이미 나가 있는 .ics 는 그대로 남는다. 구독자 쪽에서는
   아무 일도 없어 보인다. generated_at 이 밀리지 않으면 그것이 신호다.

2. GitHub Actions 는 60 일간 저장소 활동이 없으면 schedule 을 비활성화한다.
   공휴일 데이터는 몇 달씩 안 바뀌는 것이 정상이라, 피드에 변화가 없다는
   이유로 커밋이 없으면 예약 실행이 조용히 꺼진다. 꺼진 것도 조용해서
   아무도 모른다.

   status.json 은 generated_at 이 매번 바뀌므로 항상 커밋거리가 된다.
   그 커밋이 저장소를 살아 있게 유지한다.

--------------------------------------------------------------------------
자동 커밋이 근거를 대체하지 않는다
--------------------------------------------------------------------------
이 파일과 logs/build.jsonl 은 기계가 쓴다. 규칙과 데이터(rules/ 의 YAML)는
사람이 근거와 함께 쓴다. 둘을 섞지 말 것 — 자동 커밋이 데이터를 건드리기
시작하면 어느 값이 어디서 왔는지 구분되지 않는다.
"""

from __future__ import annotations

import json
from datetime import date

from core import ics
from rules.kr import feed
from rules.kr import holiday_calendar as hc
from sources.kr import key_expiry


def status(*, today: date, dtstamp) -> dict:
    """지금 상태 한 덩어리. 시계는 인자로 받는다."""
    start, end = feed.feed_range(today)
    events = feed.events(start, end)
    coverage = hc.coverage()["effective"]

    provisional = [e for e in events if e.provisional]
    return {
        "generated_at": dtstamp.isoformat(),
        "feed": {
            "path": str(feed.FEED_PATH.relative_to(feed.FEED_PATH.parents[1])),
            "events": len(events),
            "range": {"start": start.isoformat(), "end": end.isoformat()},
            "provisional_events": len(provisional),
        },
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


def render(*, today: date, dtstamp) -> str:
    """파일에 쓸 문자열. 키를 정렬해 diff 가 값 변화만 보여주게 한다."""
    return json.dumps(status(today=today, dtstamp=dtstamp), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":  # pragma: no cover
    import datetime as _dt
    import sys
    from pathlib import Path

    _now = _dt.datetime.now(_dt.UTC)
    _target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("status.json")
    _target.write_text(render(today=_now.date(), dtstamp=_now), encoding="utf-8")
    print(f"[status] {_target}")
