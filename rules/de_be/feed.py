"""독일·베를린 주 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 계약은 rules/de/feed.py 와 같다 —
feed_range(today) / events(start, end) / build(...) / publish(...).

--------------------------------------------------------------------------
세 표, 한 계산
--------------------------------------------------------------------------
    solar_holidays.yaml       월·일 고정 6 건
    easter_holidays.yaml      부활절 오프셋 4 건
    designated_holidays.yaml  일회성(date 고정) — 그 해에만
부활절은 python-dateutil 의 easter() 로 계산한다(rules/de/feed.py 의 근거).
designated 는 kr 의 designated_holidays.yaml 처럼 날짜를 하나씩 적은 표이지만
로더는 여기 것이다 — rules/kr 을 import 하지 않는다.

--------------------------------------------------------------------------
UID token 에 접두사를 단다
--------------------------------------------------------------------------
token 은 "de_be-" + key 다. de.ics 는 접두사 없는 key 그대로를 token 으로 쓰므로,
접두사가 없으면 Neujahr 같은 날 같은 항목이 두 피드에서 같은 UID 로 나간다.
함께 구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다(rules/kr_only/feed.py 의
같은 절). 한 번 발행되면 이 접두사도 영구값이다.

--------------------------------------------------------------------------
대체공휴일이 없고 provisional 은 항상 False
--------------------------------------------------------------------------
rules/de/feed.py 와 같다. 일회성 항목도 조문에 날짜가 박혀 있어 개정 확인
시점이라는 축이 없다. verified 는 별개의 축이고 피드에 나가지 않는다.

--------------------------------------------------------------------------
SUMMARY 는 베를린 조문 표기
--------------------------------------------------------------------------
YAML 의 name 그대로. § 1 Abs. 1 의 열거에서 정관사를 뺀 것이라 de.ics 의
표기(BayFTG 기준)와 다른 항목이 있다(Neujahrstag, Himmelfahrtstag,
1. Weihnachtstag). 맞추지 않는다 — 각 피드는 자기 근거 조문의 표기를 쓴다.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import yaml
from dateutil.easter import easter

from core import feed as core_feed
from core import ics

# 하한·상한 정책은 kr·de 와 같다.
RANGE_START = date(2020, 1, 1)
YEARS_AHEAD = 5

PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "독일·베를린 공휴일"
TZID = "Europe/Berlin"

KIND_STATUTORY = "statutory"

# UID token 접두사. 모듈 docstring 참조.
TOKEN_PREFIX = "de_be-"

_HERE = Path(__file__).resolve().parent
SOLAR_PATH = _HERE / "solar_holidays.yaml"
EASTER_PATH = _HERE / "easter_holidays.yaml"
DESIGNATED_PATH = _HERE / "designated_holidays.yaml"

_WHITESPACE = re.compile(r"\s+")

# key 규약. de 의 [a-z][a-z_]* 에 일회성용 연도 접미사(_YYYY)를 더한 것이다.
# 숫자는 그 자리에만 온다 — 서수를 숫자로 적은 key(8_mai)는 여전히 막는다.
# fullmatch() 인 이유는 rules/de/feed.py 와 같다(끝 개행이 새지 않게).
_KEY_RE = re.compile(r"[a-z][a-z_]*(?:_\d{4})?")


def feed_range(today: date) -> tuple:
    """(시작일, 종료일). 종료일은 today 기준 YEARS_AHEAD 년 뒤의 12-31."""
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
            f"{where}: key 가 규약 밖이다. [a-z][a-z_]* 에 연도 접미사 _YYYY 만 "
            "허용한다 — 서수는 풀어 쓰고 움라우트는 ae/oe/ue/ss 로 옮길 것."
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


def _designated() -> list:
    entries = _load(DESIGNATED_PATH, "date")
    for e in entries:
        # yaml 은 YYYY-MM-DD 를 date 로 읽는다. 문자열로 적혀 있으면 표가 잘못됐다.
        if not isinstance(e["date"], date):
            raise ics.IcsError(f"{DESIGNATED_PATH.name}: {e['key']!r} 의 date 가 날짜가 아니다.")
        if not e["key"].endswith(f"_{e['date'].year}"):
            raise ics.IcsError(
                f"{DESIGNATED_PATH.name}: {e['key']!r} 는 연도 접미사 _{e['date'].year} 로 "
                "끝나야 한다(머리 주석의 key 규약)."
            )
    return entries


def _event(day: date, entry: dict) -> ics.Event:
    return ics.Event(
        day=day,
        summary=entry["name"],
        kind=KIND_STATUTORY,
        description=f"근거: {_one_line(entry['source'])}",
        provisional=False,
        token=TOKEN_PREFIX + entry["key"],
        origin=f"key={entry['key']!r}",
    )


def _year(year: int) -> list:
    """한 해의 10 건 + 그 해의 일회성. 날짜 오름차순."""
    out = [_event(date(year, e["month"], e["day"]), e) for e in _solar()]
    sunday = easter(year)
    out += [_event(sunday + timedelta(days=e["easter_offset"]), e) for e in _easter_based()]
    out += [_event(e["date"], e) for e in _designated() if e["date"].year == year]
    out.sort(key=lambda e: e.day)
    return out


def events(start: date, end: date) -> list:
    """구간 안의 모든 이벤트. 날짜 오름차순."""
    out = []
    for year in range(start.year, end.year + 1):
        out += [e for e in _year(year) if start <= e.day <= end]
    return out


def build(*, today: date, dtstamp, previous: bytes = None) -> bytes:
    """피드 한 벌. 같은 (today, dtstamp, previous) 면 같은 바이트가 나온다."""
    start, end = feed_range(today)
    return ics.render(
        events(start, end),
        dtstamp=dtstamp,
        prodid=PRODID,
        calname=CALNAME,
        tzid=TZID,
        previous=previous,
    )


FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "de_be.ics"


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

    _now = _dt.datetime.now(_dt.UTC)
    _target = Path(_sys.argv[1]) if len(_sys.argv) > 1 else FEED_PATH
    print(f"발행: {publish(today=_now.date(), dtstamp=_now, path=_target)}")
