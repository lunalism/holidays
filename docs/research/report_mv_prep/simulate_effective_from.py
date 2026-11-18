# ruff: noqa
"""B3 시뮬레이션(레포 무변경): 설계안 (iii) — effective_from(날짜, 포함 경계)을 독일 주 로더에 들이면
초안 표가 해마다 몇 건을 내는지, python-holidays DE(subdiv='MV') 와 날짜 집합이 같은지.

사용: PYTHONPATH=<repo> uv run python simulate_effective_from.py <drafts-dir>
rules/de_bb/feed.py 를 그대로 import 하고, 표 경로와 _year() 만 이 스크립트 안에서 바꾼다.
"""
import datetime as dt
import pathlib
import sys

import holidays
from dateutil.easter import easter

from rules.de_bb import feed

drafts = pathlib.Path(sys.argv[1])
feed.SOLAR_PATH = drafts / "de_mv_solar_holidays.yaml"
feed.EASTER_PATH = drafts / "de_mv_easter_holidays.yaml"


def _active(entry, day):
    start = entry.get("effective_from")
    if start is not None and not isinstance(start, dt.date):
        raise ValueError(f"{entry['key']}: effective_from 이 날짜가 아니다({start!r})")
    return start is None or day >= start


def _year(year):
    out = [feed._event(dt.date(year, e["month"], e["day"]), e) for e in feed._solar()
           if _active(e, dt.date(year, e["month"], e["day"]))]
    sunday = easter(year)
    out += [feed._event(sunday + dt.timedelta(days=e["easter_offset"]), e) for e in feed._easter_based()
            if _active(e, sunday + dt.timedelta(days=e["easter_offset"]))]
    out.sort(key=lambda e: e.day)
    return out


feed._year = _year
total = 0
for y in range(2020, 2032):
    ours = {e.day for e in feed.events(dt.date(y, 1, 1), dt.date(y, 12, 31))}
    ph = set(holidays.DE(subdiv="MV", years=y).keys())
    total += len(ours)
    print(y, len(ours), "frauentag" if dt.date(y, 3, 8) in ours else "-", "python-holidays 일치" if ours == ph else f"불일치 {sorted(ours ^ ph)}")
print("2020-2031 합계", total)
try:
    _active({"key": "x", "effective_from": 2023}, dt.date(2023, 3, 8))
except ValueError as e:
    print("연도 거부:", e)
