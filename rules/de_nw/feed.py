"""독일·노르트라인베스트팔렌 주 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 계약은 rules/de_hh/feed.py 와 같다 —
feed_range(today) / events(start, end) / build(...) / publish(...).

--------------------------------------------------------------------------
두 표, 한 계산
--------------------------------------------------------------------------
    solar_holidays.yaml       월·일 고정 6 건
    easter_holidays.yaml      부활절 오프셋 5 건
부활절은 python-dateutil 의 easter() 로 계산한다(rules/de/feed.py 의 근거).
일회성 표는 두지 않는다 — 조사에서 확인된 일회성 항목이 없다. 사례가 오면 de_be 의
로더를 그때 이식한다. key 규약은 그때를 위해 연도 접미사까지 지금부터 허용한다
(_KEY_RE).

--------------------------------------------------------------------------
UID token 에 접두사를 단다
--------------------------------------------------------------------------
token 은 "de_nw-" + key 다. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
key 는 전부 기존 확립값(공통 9 종은 de·de_be·de_by·de_he·de_hh 와, fronleichnam 은
de_by·de_he 와, allerheiligen 은 de_by 와 같다)이라 접두사가 없으면 같은 날 같은
항목이 같은 UID 로 나간다. 함께 구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다
(rules/kr_only/feed.py 의 같은 절). 한 번 발행되면 이 접두사도 영구값이다.

--------------------------------------------------------------------------
대체공휴일이 없고 provisional 은 항상 False
--------------------------------------------------------------------------
rules/de/feed.py 와 같다. verified 는 별개의 축이고 피드에 나가지 않는다.

--------------------------------------------------------------------------
SUMMARY 는 NW 조문 표기에서 서술부·괄호를 뺀 것
--------------------------------------------------------------------------
YAML 의 name 그대로 — § 2 Abs. 1 의 열거(lexmea 현행판)에서 정관사 der 와 서술부·
괄호를 뺀 것이다. de.ics 가 BayFTG 의 "der 3. Oktober als …" 서술부를 뺀 전례와
동형: "1. Mai", "Fronleichnamstag", "Tag der Deutschen Einheit", "Allerheiligentag".
Nr. 5 는 조문의 하이픈 표기 "Christi-Himmelfahrts-Tag" 그대로다. 각 피드는 자기
근거 조문의 표기를 쓴다(de_be·de_he·de_hh 와 같은 결정).
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import yaml
from dateutil.easter import easter

from core import feed as core_feed
from core import ics

# 하한·상한 정책은 kr·de 와 주 피드 넷과 같다.
RANGE_START = date(2020, 1, 1)
YEARS_AHEAD = 5

PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "독일·노르트라인베스트팔렌 공휴일"
TZID = "Europe/Berlin"

KIND_STATUTORY = "statutory"

# UID token 접두사. 모듈 docstring 참조.
TOKEN_PREFIX = "de_nw-"

_HERE = Path(__file__).resolve().parent
SOLAR_PATH = _HERE / "solar_holidays.yaml"
EASTER_PATH = _HERE / "easter_holidays.yaml"

_WHITESPACE = re.compile(r"\s+")

# key 규약. rules/de_be/feed.py 와 같다 — [a-z][a-z_]* 에 일회성용 연도 접미사
# (_YYYY)만 허용. fullmatch() 인 이유도 같다(끝 개행이 새지 않게).
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
    """한 해의 11 건. 날짜 오름차순."""
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


FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "de_nw.ics"


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
