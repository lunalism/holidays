"""독일 전국 공통 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 여기서 정하는 것은 무엇을 몇 년치
내보낼지, SUMMARY 에 무엇을 쓸지, DESCRIPTION 의 근거를 어디서 끌어올지다.
전부 독일 고유 결정이라 core 에 두지 않는다(core/__init__.py 참조).

--------------------------------------------------------------------------
전국 공통 9 건만
--------------------------------------------------------------------------
16 개 주 전체에서 유효한 법정 공휴일만 싣는다. 주별 항목(Heilige Drei Könige,
Fronleichnam, Reformationstag …)은 여기 없다 — rules/de/__init__.py 참조.

--------------------------------------------------------------------------
두 표, 한 계산
--------------------------------------------------------------------------
    solar_holidays.yaml    월·일 고정 5 건
    easter_holidays.yaml   부활절 오프셋 4 건
부활절은 python-dateutil 의 easter() 로 계산한다. 자체 구현을 두지 않는다 —
그레고리력 computus 는 확립된 알고리즘이고, 우리가 다시 적으면 검증 대상이
하나 늘 뿐이다. 계산 결과는 tests/test_de_feed.py 가 정답 표(2021·2024·2038)
와 라이브러리 하니스로 잡아 둔다.

--------------------------------------------------------------------------
대체공휴일이 없다
--------------------------------------------------------------------------
kr 의 substitute 계열에 해당하는 것이 없다. 일요일과 겹쳐도 그 날짜 그대로
싣는다. 근거는 solar_holidays.yaml 머리 주석에 있다.

--------------------------------------------------------------------------
provisional 은 항상 False
--------------------------------------------------------------------------
kr 의 provisional 은 "규칙 개정 확인 시점 이후"다. de 의 9 건은 고정 날짜와
부활절 계산뿐이라 개정 확인 시점이라는 축이 없다. verified 는 별개의 축이고
(우리가 원문을 대조했는가) 피드에 나가지 않는다(rules/jp/feed.py 와 같은 원칙).

--------------------------------------------------------------------------
SUMMARY 는 법조문 표기
--------------------------------------------------------------------------
YAML 의 name 그대로. BayFTG Art. 1 과 BW FTG § 1 이 일치하는 표기다. 한국어로
옮기지 않는다 — 구독자 캘린더에서 원어 이름이 곧 검색어다.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import yaml
from dateutil.easter import easter

from core import feed as core_feed
from core import ics

# 하한 고정. 이 이전은 내보내지 않는다. kr 과 같은 값이다.
RANGE_START = date(2020, 1, 1)

# 상한은 실행 시점 기준 이만큼 뒤의 12-31 이다. kr 과 같은 정책이다 —
# 규칙이 안정적이라 몇 년치를 미리 내도 잠정 표시가 필요 없다.
YEARS_AHEAD = 5

# PRODID 가 kr·jp 와 같은 값인 것은 의도한 것이다(rules/jp/feed.py 의 주석).
PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "독일 공휴일 (전국 공통)"
TZID = "Europe/Berlin"

KIND_STATUTORY = "statutory"

_HERE = Path(__file__).resolve().parent
SOLAR_PATH = _HERE / "solar_holidays.yaml"
EASTER_PATH = _HERE / "easter_holidays.yaml"

_WHITESPACE = re.compile(r"\s+")

# key 규약. solar_holidays.yaml 머리 주석 참조. UID 에 그대로 실리는 값이라
# 로드 시점에 거른다 — 발행까지 가면 잘못된 UID 로 파일이 나간다.
#
# fullmatch() 로 검사한다. ^...$ 와 match() 는 문자열 끝의 개행 하나를
# 통과시킨다 — "neujahr\n" 이 규약을 지난다. 앵커를 쓰지 않고 전체 일치를
# 요구한다(tests/test_de_feed.py 의 key 경계 절).
_KEY_RE = re.compile(r"[a-z][a-z_]*")


def feed_range(today: date) -> tuple:
    """(시작일, 종료일). 종료일은 today 기준 YEARS_AHEAD 년 뒤의 12-31.

    today 를 인자로 받는다. 시계를 여기서 읽지 않는 이유는 core/ics.py 의
    DTSTAMP 설명과 같다.
    """
    return RANGE_START, date(today.year + YEARS_AHEAD, 12, 31)


def _one_line(text: str) -> str:
    return _WHITESPACE.sub(" ", (text or "").strip())


def _checked(entry: dict, path: Path, *fields) -> dict:
    """항목 하나를 검사해 그대로 돌려준다. 손대지 않는다."""
    where = f"{path.name}: {entry.get('key')!r}"
    for field in ("key", "name", "source", *fields):
        if entry.get(field) in (None, ""):
            raise ics.IcsError(f"{where}: {field} 가 비었다.")
    if not _KEY_RE.fullmatch(entry["key"]):
        raise ics.IcsError(
            f"{where}: key 가 규약 밖이다. [a-z][a-z_]* 만 허용한다 — "
            "서수는 풀어 쓰고 움라우트는 ae/oe/ue/ss 로 옮길 것."
        )
    if not isinstance(entry.get("verified"), bool):
        raise ics.IcsError(f"{where}: verified 는 true/false 여야 한다.")
    return entry


def _load(path: Path, *fields) -> list:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = doc.get("holidays") or ()
    if not entries:
        raise ics.IcsError(f"{path} 에 holidays 가 비었다.")
    return [_checked(e, path, *fields) for e in entries]


def _solar() -> list:
    return _load(SOLAR_PATH, "month", "day")


def _easter_based() -> list:
    return _load(EASTER_PATH, "easter_offset")


def _event(day: date, entry: dict) -> ics.Event:
    return ics.Event(
        day=day,
        summary=entry["name"],
        kind=KIND_STATUTORY,
        # 근거는 데이터의 source 원문 그대로, 한 줄로.
        description=f"근거: {_one_line(entry['source'])}",
        # 항상 False. 모듈 docstring 참조.
        provisional=False,
        token=entry["key"],
        origin=f"key={entry['key']!r}",
    )


def _year(year: int) -> list:
    """한 해의 9 건. 날짜 오름차순."""
    out = [_event(date(year, e["month"], e["day"]), e) for e in _solar()]
    sunday = easter(year)
    out += [_event(sunday + timedelta(days=e["easter_offset"]), e) for e in _easter_based()]
    out.sort(key=lambda e: e.day)
    return out


def events(start: date, end: date) -> list:
    """구간 안의 모든 이벤트. 날짜 오름차순."""
    out = []
    for year in range(start.year, end.year + 1):
        out += [e for e in _year(year) if start <= e.day <= end]
    return out


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


# 발행 위치. SEQUENCE 의 진실 공급원은 여기 있는 직전 발행본이다.
FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "de.ics"


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
    _target = Path(_sys.argv[1]) if len(_sys.argv) > 1 else FEED_PATH
    print(f"발행: {publish(today=_now.date(), dtstamp=_now, path=_target)}")
