"""독일·작센 주 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 계약은 rules/de_mv/feed.py 와 같다 —
events(start, end) 가 구간 안의 Event 를 날짜 오름차순으로 낸다.

입력은 이 디렉터리의 표 셋이다.
    solar_holidays.yaml          고정 날짜 6 건(§ 1 Abs. 1 열거 1·4·8·9·11·12번째)
    easter_holidays.yaml         부활절 오프셋 4 건(−2, +1, +39, +50 — 열거 2·3·5·6번째)
    totensonntag_holidays.yaml   Totensonntag 오프셋 1 건(−4 — 열거 10번째, Buß- und Bettag)
부활절은 python-dateutil 의 easter() 로 계산한다(rules/de/feed.py 의 근거).
일회성 표는 두지 않는다 — SächsSFG 에는 일회성 지정을 수권하는 조항이 없다. 찾은 범위와 공백은
solar_holidays.yaml 머리 주석에 있다.

--------------------------------------------------------------------------
Totensonntag 기준 오프셋 (사람의 결정 S2)
--------------------------------------------------------------------------
§ 1 Abs. 1 은 「Buß- und Bettag」 의 이름만 든다. 같은 법 § 2 는 Totensonntag 를 「letzter Sonntag
vor dem 1. Advent」 로 정의한다. 이 로더는 그 정의를 그대로 계산한다.

    _advent1(year)        11월 27일부터 첫 일요일 — 대림절 첫째 주일(11월 27일–12월 3일).
    _totensonntag(year)   _advent1(year) − 7 일 — 「letzter Sonntag vor dem 1. Advent」.

표의 항목은 totensonntag_offset(정수 일수)을 갖고, 날짜는 _totensonntag(year) + 오프셋이다.
Buß- und Bettag 는 −4 — Totensonntag 앞 수요일이다. 이것은 부활절 표의 easter_offset 과 같은
「기준일 + 정수」 꼴이고, 필드 이름이 기준일을 그대로 든다(easter_offset 과 짝).
요일 규칙의 일반 장치를 만들지 않는다 — 기준일 하나와 오프셋뿐이다.

--------------------------------------------------------------------------
이 로더만의 규약 — 필드 집합 (rules/de_mv/feed.py 와 같은 꼴)
--------------------------------------------------------------------------
  - 닫힌 필드 집합을 두고 모르는 필드를 거부한다 — 공통 필드(_COMMON_FIELDS)에 표마다 _load() 가
    받는 날짜 필드(solar 는 month·day, easter 는 easter_offset, totensonntag 는
    totensonntag_offset)를 더한 것이 그 표의 집합이다. de_mv 의 effective_from 은 이 피드에 없다.
  - totensonntag_offset 은 int 여야 한다. 문자열·실수·bool 은 거부한다(bool 은 int 의 하위 클래스라
    type 으로 본다).
  - 표의 최상위에는 holidays 하나만 둔다. 한 매핑 안의 중복 키를 거부한다(_UniqueKeyLoader).

다른 주 로더에는 손대지 않았다. 전 로더의 모르는 필드 거부는 따로 열린 항목이다.

--------------------------------------------------------------------------
UID token
--------------------------------------------------------------------------
token 은 "de_sn-" + key 다. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
key 는 buss_und_bettag 밖은 기존 확립값(공통 9 종은 de·다른 주 피드와, reformationstag 는
de_bb·de_hb·de_hh·de_mv·de_ni·de_sh 와 같다)이라 접두사가 없으면 같은 날 같은 항목이 같은 UID 로
나간다. 함께 구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다(rules/kr_only/feed.py 의 같은 절).
buss_und_bettag 는 이 피드가 처음 쓰는 key 다(승인은 totensonntag_holidays.yaml 머리 주석).
한 번 발행되면 접두사와 key 는 영구값이다.

--------------------------------------------------------------------------
피드에 나가지 않는 것
--------------------------------------------------------------------------
verified·source_todo·totensonntag_offset 은 근거 관리용이다. DESCRIPTION 에 싣지 않는다.
Buß- und Bettag 의 날짜 근거는 그 항목의 source 문장으로만 나간다. 이 피드는 11 건 전부
false + source_todo 지만 그 사실도 나가지 않는다.

--------------------------------------------------------------------------
SUMMARY 는 SächsSFG 표기에서 괄호의 날짜만 뺀 것
--------------------------------------------------------------------------
YAML 의 name 그대로 — § 1 Abs. 1 의 열거에는 관사가 없고, 고정 날짜 여섯은 끝에 괄호의 날짜가
붙는다. 괄호만 빼고 나머지 자구는 그대로다: "Reformationsfest (31. Oktober)" → "Reformationsfest"
(Reformationstag 가 아니다 — 조문 표기), "Tag der Arbeit (1. Mai)" → "Tag der Arbeit". 각 피드는
자기 근거 조문의 표기를 쓴다.
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
CALNAME = "독일·작센 공휴일"
TZID = "Europe/Berlin"

KIND_STATUTORY = "statutory"

# UID token 접두사. 모듈 docstring 참조.
TOKEN_PREFIX = "de_sn-"

# scope — YAML 전 항목 필수, 닫힌 집합. 전국 공통 9 건이 bundesweit, 나머지가
# land 다(근거는 YAML 머리 주석의 scope 절). DESCRIPTION 첫 줄이 여기서 갈린다.
SCOPES = frozenset({"bundesweit", "land"})
LAND_NAME = "작센"
SCOPE_SENTENCE = {
    "bundesweit": BUNDESWEIT_SENTENCE,
    "land": f"{LAND_NAME} 주 공휴일입니다.",
}

# 랜딩에 쓰는 독일어 주 이름. 피드에 나가지 않는다 — landing/render.py 만 읽고,
# 위 LAND_NAME(한국어)은 DESCRIPTION 을 만들므로 그대로 둔다. 표기 근거는
# rules/de/feed.py 의 같은 이름 절(기본법 전문).
LAND_NAME_DE = "Sachsen"

_HERE = Path(__file__).resolve().parent
SOLAR_PATH = _HERE / "solar_holidays.yaml"
EASTER_PATH = _HERE / "easter_holidays.yaml"
TOTENSONNTAG_PATH = _HERE / "totensonntag_holidays.yaml"

_WHITESPACE = re.compile(r"\s+")

# key 규약. rules/de_be/feed.py 와 같다 — [a-z][a-z_]* 에 일회성용 연도 접미사
# (_YYYY)만 허용. 날짜형(31_oktober)은 숫자 시작이라 막힌다. fullmatch() 인 이유도
# 같다(끝 개행이 새지 않게).
_KEY_RE = re.compile(r"[a-z][a-z_]*(?:_\d{4})?")

# 세 표가 함께 받는 필드. 표마다의 날짜 필드는 _load() 의 fields 로 더해져 닫힌 집합이 된다
# (_checked). 모듈 docstring 의 「이 로더만의 규약」.
_COMMON_FIELDS = frozenset({"key", "name", "scope", "verified", "source", "source_todo"})


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
            f"{where}: 모르는 필드 {unknown} — 이 표가 받는 필드는 {sorted(allowed)} 뿐이다."
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
    if "totensonntag_offset" in entry:
        offset = entry["totensonntag_offset"]
        # bool 은 int 의 하위 클래스라 isinstance 로는 걸러지지 않는다.
        if type(offset) is not int:
            raise ics.IcsError(
                f"{where}: totensonntag_offset 이 정수가 아니다({offset!r}). "
                "Totensonntag 로부터의 날수를 정수로 적는다."
            )
    return entry


class _UniqueKeyLoader(yaml.SafeLoader):
    """safe_load 와 같되, 한 매핑 안의 중복 키를 거부한다(모듈 docstring 「이 로더만의 규약」)."""


def _construct_unique_mapping(loader, node, deep=False):
    keys = [loader.construct_object(k, deep=deep) for k, _ in node.value]
    dupes = sorted({str(k) for k in keys if keys.count(k) > 1})
    if dupes:
        raise ics.IcsError(
            f"중복 키 {dupes} — 한 매핑에 같은 키를 두 번 적었다({node.start_mark})."
        )
    return loader.construct_mapping(node, deep=deep)


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _load(path: Path, *fields) -> list:
    doc = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader) or {}
    extra = sorted(set(doc) - {"holidays"})
    if extra:
        raise ics.IcsError(f"{path.name}: 최상위의 모르는 키 {extra} — holidays 하나만 둔다.")
    entries = doc.get("holidays") or ()
    if not entries:
        raise ics.IcsError(f"{path} 에 holidays 가 비었다.")
    return [_checked(e, path, *fields) for e in entries]


def _solar() -> list:
    return _load(SOLAR_PATH, "month", "day")


def _easter_based() -> list:
    return _load(EASTER_PATH, "easter_offset")


def _totensonntag_based() -> list:
    return _load(TOTENSONNTAG_PATH, "totensonntag_offset")


def _advent1(year: int) -> date:
    """대림절 첫째 주일 — 11월 27일부터 첫 일요일(11월 27일–12월 3일)."""
    day = date(year, 11, 27)
    return day + timedelta(days=(6 - day.weekday()) % 7)


def _totensonntag(year: int) -> date:
    """SächsSFG § 2 「letzter Sonntag vor dem 1. Advent」 — 대림절 첫째 주일의 7 일 전."""
    return _advent1(year) - timedelta(days=7)


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
    """한 해의 11 건. 날짜 오름차순."""
    out = [_event(date(year, e["month"], e["day"]), e) for e in _solar()]
    sunday = easter(year)
    out += [_event(sunday + timedelta(days=e["easter_offset"]), e) for e in _easter_based()]
    totensonntag = _totensonntag(year)
    out += [
        _event(totensonntag + timedelta(days=e["totensonntag_offset"]), e)
        for e in _totensonntag_based()
    ]
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


FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "de_sn.ics"


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
