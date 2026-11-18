"""독일·메클렌부르크포어포메른 주 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 계약은 rules/de_hb/feed.py 와 같다 —
events(start, end) 가 구간 안의 Event 를 날짜 오름차순으로 낸다.

입력은 이 디렉터리의 표 둘이다.
    solar_holidays.yaml       고정 날짜 7 건(Nr. 1·2·5·8·9·10·11)
    easter_holidays.yaml      부활절 오프셋 4 건(−2, +1, +39, +50 — Nr. 3·4·6·7)
부활절은 python-dateutil 의 easter() 로 계산한다(rules/de/feed.py 의 근거).
일회성 표는 두지 않는다 — § 2 Abs. 3(Landesregierung 이 「bei besonderem Anlass」 Werktage 를
「einmaligen Feiertagen」 으로 선언)에 따른 선언을 찾지 못했다. 찾은 범위는 solar_holidays.yaml
머리 주석에 있다. 사례가 오면 de_be 의 designated_holidays.yaml 형식을 따른다.

--------------------------------------------------------------------------
이 로더만의 규약 — 필드 집합과 effective_from (사람의 결정 M6)
--------------------------------------------------------------------------
다른 독일 주 로더는 필수 필드가 비었는지만 보고 그 밖의 필드는 조용히 지나보낸다. 경계 필드를
들이면서 그 모양을 두면, 로더가 모르는 이름(예: valid_from)을 적었을 때 오류 없이 2020–2022 에
Frauentag 가 나간다. 그래서 이 로더는

  - 표마다 닫힌 필드 집합을 두고 모르는 필드를 거부한다(_FIELDS).
  - effective_from 을 받는다. kr 의 항목별 effective_from(rules/kr/holiday_calendar.py 의
    _active)과 같은 뜻이다 — 공휴일 지위의 시작, 날짜, 포함 경계. 없으면 발행 범위 내내다.
  - effective_from 은 datetime.date 여야 한다. 연도(int)·문자열·datetime·bool 은 거부한다.
    연 단위로는 연중 시행일(2022-07-13)을 표현할 수 없다 — kr 의 같은 결정
    (tests/test_substitute_rules.py::test_effective_from_is_a_date_not_a_year).
  - 끝 필드(effective_until·valid_until)는 두지 않는다. 모르는 필드로 거부된다.

다른 주 로더에는 손대지 않았다. 전 로더의 모르는 필드 거부는 따로 열린 항목이다.

--------------------------------------------------------------------------
UID token
--------------------------------------------------------------------------
token 은 "de_mv-" + key 다. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
key 는 전부 기존 확립값(공통 9 종은 de·다른 주 피드와, frauentag 는 de_be 와, reformationstag
는 de_bb·de_hb·de_hh·de_ni·de_sh 와 같다)이라 접두사가 없으면 같은 날 같은 항목이 같은 UID 로
나간다. 함께 구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다(rules/kr_only/feed.py 의 같은 절).
한 번 발행되면 이 접두사도 영구값이다. 경계 이전 해(2020–2022)에는 frauentag 이벤트 자체가 없다.

--------------------------------------------------------------------------
피드에 나가지 않는 것
--------------------------------------------------------------------------
verified·source_todo·effective_from 은 근거 관리용이다. DESCRIPTION 에 싣지 않는다.
경계는 Frauentag 의 source 문장으로만 나간다. 이 피드는 11 건 전부 false + source_todo 지만
그 사실도 나가지 않는다.

--------------------------------------------------------------------------
SUMMARY 는 MV 조문 표기에서 관사와 괄호의 날짜를 정리한 것
--------------------------------------------------------------------------
YAML 의 name 그대로 — § 2 Abs. 1 의 열거는 전 호가 "der …" 로 시작하고 고정 날짜 일곱 중 여섯은
끝에 괄호의 날짜가 붙는다. 관사와 괄호만 빼고 나머지 자구는 그대로다: "der Frauentag (8. März)"
→ "Frauentag", "der Christi-Himmelfahrtstag" → "Christi-Himmelfahrtstag", "der Tag der Deutschen
Einheit (3. Oktober)" → "Tag der Deutschen Einheit"(대문자 D 도 조문 그대로). 각 피드는 자기 근거
조문의 표기를 쓴다.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import yaml
from dateutil.easter import easter

from core import feed as core_feed
from core import ics
from rules.de.feed import BUNDESWEIT_SENTENCE

# 하한·상한 정책은 kr·de 와 다른 주 피드들과 같다.
RANGE_START = date(2020, 1, 1)
YEARS_AHEAD = 5

PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "독일·메클렌부르크포어포메른 공휴일"
TZID = "Europe/Berlin"

KIND_STATUTORY = "statutory"

# UID token 접두사. 모듈 docstring 참조.
TOKEN_PREFIX = "de_mv-"

# scope — YAML 전 항목 필수, 닫힌 집합. 전국 공통 9 건이 bundesweit, 나머지가
# land 다(근거는 YAML 머리 주석의 scope 절). DESCRIPTION 첫 줄이 여기서 갈린다.
SCOPES = frozenset({"bundesweit", "land"})
LAND_NAME = "메클렌부르크포어포메른"
SCOPE_SENTENCE = {
    "bundesweit": BUNDESWEIT_SENTENCE,
    "land": f"{LAND_NAME} 주 공휴일입니다.",
}

# 랜딩에 쓰는 독일어 주 이름. 피드에 나가지 않는다 — landing/render.py 만 읽고,
# 위 LAND_NAME(한국어)은 DESCRIPTION 을 만들므로 그대로 둔다. 표기 근거는
# rules/de/feed.py 의 같은 이름 절(기본법 전문).
LAND_NAME_DE = "Mecklenburg-Vorpommern"

_HERE = Path(__file__).resolve().parent
SOLAR_PATH = _HERE / "solar_holidays.yaml"
EASTER_PATH = _HERE / "easter_holidays.yaml"

_WHITESPACE = re.compile(r"\s+")

# key 규약. rules/de_be/feed.py 와 같다 — [a-z][a-z_]* 에 일회성용 연도 접미사
# (_YYYY)만 허용. 날짜형(31_oktober)은 숫자 시작이라 막힌다. fullmatch() 인 이유도
# 같다(끝 개행이 새지 않게).
_KEY_RE = re.compile(r"[a-z][a-z_]*(?:_\d{4})?")

# 표마다 받는 필드 — 닫힌 집합. 모듈 docstring 의 「이 로더만의 규약」.
_COMMON_FIELDS = frozenset(
    {"key", "name", "scope", "verified", "source", "source_todo", "effective_from"}
)
_FIELDS = {
    "solar": _COMMON_FIELDS | {"month", "day"},
    "easter": _COMMON_FIELDS | {"easter_offset"},
}


def feed_range(today: date) -> tuple:
    """(시작일, 종료일). 종료일은 today 기준 YEARS_AHEAD 년 뒤의 12-31."""
    return RANGE_START, date(today.year + YEARS_AHEAD, 12, 31)


def _one_line(text: str) -> str:
    return _WHITESPACE.sub(" ", (text or "").strip())


def _checked(entry: dict, path: Path, *fields) -> dict:
    """항목 하나를 검사해 그대로 돌려준다. 손대지 않는다."""
    where = f"{path.name}: {entry.get('key')!r}"
    allowed = _COMMON_FIELDS | set(fields)
    unknown = sorted(set(entry) - allowed)
    if unknown:
        raise ics.IcsError(
            f"{where}: 모르는 필드 {unknown} — 이 표가 받는 필드는 {sorted(allowed)} 뿐이다. "
            "끝 필드(effective_until·valid_until)는 두지 않는다."
        )
    for field in ("key", "name", "source", "scope", *fields):
        if entry.get(field) in (None, ""):
            raise ics.IcsError(f"{where}: {field} 가 비었다.")
    if entry["scope"] not in SCOPES:
        raise ics.IcsError(
            f"{where}: scope 가 규약 밖이다 — {entry['scope']!r}. "
            f"{sorted(SCOPES)} 중 하나여야 한다."
        )
    if not _KEY_RE.fullmatch(entry["key"]):
        raise ics.IcsError(
            f"{where}: key 가 규약 밖이다. [a-z][a-z_]* 에 연도 접미사 _YYYY 만 "
            "허용한다 — 서수는 풀어 쓰고 움라우트는 ae/oe/ue/ss 로 옮길 것."
        )
    if not isinstance(entry.get("verified"), bool):
        raise ics.IcsError(f"{where}: verified 는 true/false 여야 한다.")
    if "effective_from" in entry:
        start = entry["effective_from"]
        # datetime 은 date 의 하위 클래스라 isinstance 로는 걸러지지 않는다.
        if type(start) is not date:
            raise ics.IcsError(
                f"{where}: effective_from 이 날짜가 아니다({start!r}). "
                "연 단위로 두면 2022-07-13 같은 연중 시행일을 표현할 수 없다."
            )
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


def _active(entry: dict, day: date) -> bool:
    """그 날 공휴일 지위가 있는가. 시작은 포함 경계 — kr 의 _active 와 같은 판정이다."""
    start = entry.get("effective_from")
    return not (start and day < start)


def _event(day: date, entry: dict) -> ics.Event:
    return ics.Event(
        day=day,
        summary=entry["name"],
        kind=KIND_STATUTORY,
        # 구독자용 문장 / 빈 줄 / 근거. 개행은 core/ics.py 가 \n 으로 이스케이프한다.
        description=f"{SCOPE_SENTENCE[entry['scope']]}\n\n근거: {_one_line(entry['source'])}",
        provisional=False,
        token=TOKEN_PREFIX + entry["key"],
        origin=f"key={entry['key']!r}",
    )


def _year(year: int) -> list:
    """한 해의 이벤트 — 2020–2022 는 10 건, 2023 부터 11 건. 날짜 오름차순."""
    days = [(date(year, e["month"], e["day"]), e) for e in _solar()]
    sunday = easter(year)
    days += [(sunday + timedelta(days=e["easter_offset"]), e) for e in _easter_based()]
    out = [_event(day, e) for day, e in days if _active(e, day)]
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


FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "de_mv.ics"


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
