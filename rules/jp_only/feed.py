"""일본만 쉬는 날 피드 — jp 이벤트 중 kr 이 같은 날 쉬지 않는 것만.

정의는 차집합이다. jp 이벤트를 그대로 싣되, 그 날짜에 kr 공휴일이 하나라도
있으면 뺀다. 세 가지를 못 박는다.

1. 판정은 날짜 단위다. 이름이 달라도, token 이 달라도 날짜가 겹치면 뺀다.
   建国記念の日(2021-02-11)와 설날 연휴는 다른 공휴일이지만 같은 날이라
   이 피드에 없다. "같은 공휴일인가" 는 판정이고 판정은 근거를 요구하는데,
   이 피드가 답하는 물음은 "그날 상대국도 쉬는가" 뿐이다.

2. "상대국이 쉬지 않는다" 의 기준은 상대국 공휴일 집합뿐이다. 주말·근무
   형태·회사별 휴무는 개입하지 않는다. 토요일에 걸린 jp 공휴일도 그날 kr
   공휴일이 없으면 실린다.

3. 파일 내 순서는 core.ics.assign_uids() 의 (날짜, token) 정렬 결과다.
   원천을 가져오고 거르는 순서에 의존하지 않는다.

--------------------------------------------------------------------------
UID 는 kr.ics·jp.ics·kr_jp.ics 와 분리한다
--------------------------------------------------------------------------
token 에 jp_only-{cc}- 접두사를 단다. 발행된 세 피드의 UID 와 겹치면 안
된다 — 함께 구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다. 접두사가 그
겹침을 구조적으로 막는다. cc 가 항상 jp 인데도 접두사에 넣는 것은 kr_jp 의
kr_jp-{cc}- 와 같은 꼴을 유지하기 위해서다 — 접두사만 보고 어느 나라 항목인지
읽힌다.

한 번 발행되면 이 접두사도 영구값이다. UID 규칙 전반은 core/ics.py 참조.

--------------------------------------------------------------------------
발행 범위는 두 나라 중 짧은 쪽까지
--------------------------------------------------------------------------
rules/kr_jp/feed.py 와 같다 — 끝은 min(kr 의 feed_range(today) 끝, jp 의
RANGE_END). 상대국 공휴일이 없는 구간을 실으면 그 구간 전체가 "일본만
쉬는 날" 로 읽힌다. 상대국 데이터가 없는 것과 상대국이 쉬지 않는 것은 다르다.
jp 의 범위는 상수지만 kr 쪽 끝이 today 를 따라 움직이므로 이 피드의 범위도
함수다.

원천 import 는 rules.kr.feed 와 rules.jp.feed 뿐이다. sources/ 를 직접
보지 않는다 — 원천 피드가 내보내는 것만이 이 피드의 입력이다.
"""

from __future__ import annotations

import dataclasses
from datetime import date
from pathlib import Path

from core import feed as core_feed
from core import ics
from rules.jp import feed as jp_feed
from rules.kr import feed as kr_feed

# 하한 고정. rules/kr_jp/feed.py 의 RANGE_START 와 같은 값이고 같은 이유로
# 어느 쪽도 import 하지 않는다 — 한쪽이 하한을 내리면 이 피드는 "두 나라
# 다 있는 구간" 을 지키기 위해 따라가면 안 된다.
RANGE_START = date(2020, 1, 1)

# PRODID 가 다른 피드와 같은 값인 것은 의도한 것이다 — 피드를 만드는 제품은
# 하나다(rules/jp/feed.py 의 PRODID 주석 참조).
PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "일본만 쉬는 날"
TZID = "Asia/Tokyo"


def feed_range(today: date) -> tuple:
    """(시작일, 종료일). 종료일은 kr 의 끝과 jp 의 끝 중 작은 쪽.

    rules/kr_jp/feed.py 의 feed_range 와 같은 식이다. today 를 인자로 받는
    이유도 같다 — 시계를 여기서 읽지 않는다.
    """
    return RANGE_START, min(kr_feed.feed_range(today)[1], jp_feed.RANGE_END)


def _tagged(event: ics.Event, cc: str) -> ics.Event:
    """나라 접두사를 단 Event. token 과 summary 만 바꾼다.

    나머지 필드(kind·description·provisional·origin)는 원천의 것 그대로다.
    jp 는 잠정 항목이 없어(rules/jp/feed.py) STATUS:TENTATIVE 가 나올 일이
    없지만, 생기더라도 provisional 이 그대로 실린다.
    """
    return dataclasses.replace(
        event,
        token=f"jp_only-{cc}-{event.token}",
        summary=f"[{cc.upper()}] {event.summary}",
    )


def events(start: date, end: date) -> list:
    """구간 안의 jp 이벤트 중 그날 kr 공휴일이 없는 것. 날짜 오름차순.

    상대국 날짜 집합은 kr 의 events(start, end) 에서 만든다 — kr 은 구간을
    넘겨야 이벤트를 낸다. 자국 jp 는 전량을 받아 구간으로 거른다(jp 의
    events() 는 인자를 받지 않는다).
    """
    other_days = {e.day for e in kr_feed.events(start, end)}
    kept = [
        _tagged(e, "jp")
        for e in jp_feed.events()
        if start <= e.day <= end and e.day not in other_days
    ]
    kept.sort(key=lambda e: e.day)
    return kept


def build(*, today: date, dtstamp, previous: bytes = None) -> bytes:
    """피드 한 벌. 같은 (today, dtstamp, previous) 면 같은 바이트가 나온다.

    previous 는 직전에 발행한 .ics 의 바이트다. SEQUENCE 를 정하는 데만 쓴다.
    None 이면 첫 발행으로 보고 전부 0 이 나간다.
    """
    start, end = feed_range(today)
    return ics.render(
        events(start, end),
        dtstamp=dtstamp,
        prodid=PRODID,
        calname=CALNAME,
        tzid=TZID,
        previous=previous,
    )


# 발행 위치. SEQUENCE 의 진실 공급원은 여기 있는 직전 발행본이다
# (rules/kr/feed.py 의 FEED_PATH 주석 참조).
FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "jp_only.ics"


def publish(*, today: date, dtstamp, path: Path = None) -> Path:
    """피드를 파일로 낸다. 읽기·쓰기의 순서와 원자성은 core.feed 가 맡는다."""
    path = path or FEED_PATH
    return core_feed.publish(
        lambda previous: build(today=today, dtstamp=dtstamp, previous=previous),
        path,
    )


if __name__ == "__main__":  # pragma: no cover
    import datetime as _dt
    import sys as _sys

    # 시계를 읽는 곳은 여기 하나다. 모듈 안에서는 읽지 않는다.
    _now = _dt.datetime.now(_dt.UTC)

    # 경로를 인자로 받는다. 없으면 FEED_PATH. 리다이렉션을 쓸 수 없는 이유는
    # core/feed.py 의 publish() docstring 참조.
    _target = Path(_sys.argv[1]) if len(_sys.argv) > 1 else FEED_PATH
    print(f"발행: {publish(today=_now.date(), dtstamp=_now, path=_target)}")
