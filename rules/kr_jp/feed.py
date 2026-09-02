"""한국·일본 합집합 피드 — kr·jp 이벤트를 하나의 .ics 로.

정의는 합집합이다. kr 이벤트와 jp 이벤트를 각각 그대로 싣는다. 같은 날
양쪽에 있으면 VEVENT 둘이다 — 합치거나 하나를 고르지 않는다. 어느 쪽을
남길지는 판정이고, 판정은 근거를 요구하는데 "같은 날"은 근거가 아니다.

--------------------------------------------------------------------------
UID 는 kr.ics·jp.ics 와 분리한다
--------------------------------------------------------------------------
token 에 kr_jp-{cc}- 접두사를 단다. 이유는 둘이다.

1. 발행된 kr.ics·jp.ics 의 UID 와 겹치면 안 된다. 세 피드를 함께 구독한
   캘린더에서 같은 UID 는 서로를 덮어쓴다. 접두사가 그 겹침을 구조적으로
   막는다(tests/test_kr_jp_feed.py 가 발행본과의 교집합 0 을 단언한다).

2. 나라 구분 없이 합치면 이 피드 안에서 부딪힌다. 신정(new_years_day)과
   어린이날(childrens_day)은 양국이 같은 날 같은 token 이라,
   core.ics.assign_uids() 의 같은날-같은-token 가드에 걸려 빌드가 멈춘다.

한 번 발행되면 이 접두사도 영구값이다. UID 규칙 전반은 core/ics.py 참조.

--------------------------------------------------------------------------
이벤트 순서
--------------------------------------------------------------------------
events() 는 kr 목록과 jp 목록을 이어 붙인 뒤 날짜로 안정 정렬해 돌려준다.
파일 순서는 core.ics.assign_uids() 의 (날짜, token) 정렬을 따른다. 같은
날은 token 사전순이라 jp 항목이 kr 항목 앞에 실린다. 캘린더 앱은 어차피
순서를 보지 않고, UID 는 token 에서 나오므로 이 정렬은 UID 에 영향을 주지
않는다.

--------------------------------------------------------------------------
발행 범위는 두 나라 중 짧은 쪽까지
--------------------------------------------------------------------------
끝은 min(kr 의 feed_range(today) 끝, jp 의 RANGE_END) 다. 한쪽만 있는
구간을 실으면 다른 나라의 공휴일이 없는 것처럼 읽힌다 — 이 피드의 독자는
"두 나라 다" 를 구독한 것이지 "있는 만큼" 을 구독한 것이 아니다.
상수가 아니라 함수인 것은 kr 쪽 끝이 today 를 따라 움직이기 때문이다.
jp 의 CSV 가 kr 의 상한(지금 today+5년)을 넘어 늘어나면 min 이 kr 쪽으로
넘어간다 — 그때 코드는 고칠 것이 없다.

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

# 하한 고정. kr·jp 의 RANGE_START 가 둘 다 이 값이다(rules/kr/feed.py:35,
# sources/jp/build_data.py:51). 어느 한쪽을 import 해 쓰지 않는 것은 의도다 —
# 한쪽이 하한을 내리면 이 피드는 "두 나라 다" 를 지키기 위해 따라가면 안 된다.
RANGE_START = date(2020, 1, 1)

# PRODID 가 kr·jp 와 같은 값인 것은 의도한 것이다. 세 피드를 만드는 제품은
# 하나다 — rules/jp/feed.py 의 PRODID 주석 참조.
PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "대한민국·일본 공휴일"
TZID = "Asia/Seoul"


def feed_range(today: date) -> tuple:
    """(시작일, 종료일). 종료일은 kr 의 끝과 jp 의 끝 중 작은 쪽.

    today 를 인자로 받는 이유는 rules/kr/feed.py 의 feed_range 와 같다 —
    시계를 여기서 읽지 않는다.
    """
    return RANGE_START, min(kr_feed.feed_range(today)[1], jp_feed.RANGE_END)


def _tagged(event: ics.Event, cc: str) -> ics.Event:
    """나라 접두사를 단 Event. token 과 summary 만 바꾼다.

    나머지 필드(kind·description·provisional·origin)는 원천의 것 그대로다.
    STATUS:TENTATIVE 와 X-HOLIDAY-STATUS 는 provisional 에서 나오므로
    (core/ics.py) kr 의 잠정 표시도 그대로 실린다.
    """
    return dataclasses.replace(
        event,
        token=f"kr_jp-{cc}-{event.token}",
        summary=f"[{cc.upper()}] {event.summary}",
    )


def events(start: date, end: date) -> list:
    """구간 안의 모든 이벤트. 날짜 오름차순 — 반환 목록의 순서다.
    파일에 실리는 순서는 다르다(모듈 docstring 의 이벤트 순서 절).

    kr 은 구간을 넘겨 만들고 jp 는 전량을 받아 구간으로 거른다 — jp 의
    events() 는 인자를 받지 않는다(범위가 상수라서다).
    """
    merged = [_tagged(e, "kr") for e in kr_feed.events(start, end)]
    merged += [_tagged(e, "jp") for e in jp_feed.events() if start <= e.day <= end]
    merged.sort(key=lambda e: e.day)
    return merged


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
FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "kr_jp.ics"


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
