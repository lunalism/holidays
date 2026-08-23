"""일본 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 여기서 정하는 것은 무엇을 읽을지,
SUMMARY 에 무엇을 쓸지, DESCRIPTION 의 근거를 어디서 끌어올지다. 전부 일본
고유 결정이라 core 에 두지 않는다(core/__init__.py 참조).

--------------------------------------------------------------------------
근거는 데이터의 source 하나에서만 온다
--------------------------------------------------------------------------
data/jp/ 는 143 건 전부 source 를 들고 있고 tests/test_cao_source.py 의
test_every_entry_carries_a_source() 가 그것을 강제한다. 그래서 kind 와 무관하게
DESCRIPTION 을 붙인다 — rules/kr/feed.py 의 법정공휴일이 DESCRIPTION 을 비우는
것은 정책이 아니라 결핍이고(그쪽 _description() 주석), 없는 쪽을 따라 할 이유가
없다.

--------------------------------------------------------------------------
verified 와 source_todo 는 나가지 않는다
--------------------------------------------------------------------------
우리 내부 검증 상태다. core/ics.py 의 _vevent() 가 SUMMARY 바로 위에서 같은
것을 적어 두었다 — 잠정·미검증 표시를 붙이지 않는다.

그리고 그 둘은 provisional 자리에도 넣지 않는다. provisional 은 "규칙 개정
확인 시점 이후"(core/ics.py 의 Event 필드 주석)라서 규칙 쪽 사정이고,
verified 는 우리가 원문을 대조했는가다. 범주가 다르다.

jp 는 provisional 이 항상 False 다. 발행 범위의 상한이 内閣府 CSV 의 마지막
날짜라서 정부가 아직 정하지 않은 날짜가 애초에 들어오지 않는다
(sources/jp/build_data.py 의 "발행 범위만 옮긴다" 참조).

--------------------------------------------------------------------------
SUMMARY 는 일본어 원문을 유지한다
--------------------------------------------------------------------------
한국어로 옮기면 天皇誕生日 등에서 우리가 정치적 판정을 하게 된다. 이 레포가
판정할 사안이 아니다. DESCRIPTION 의 서술문은 한국어로 쓰되 축일명과 법령명은
원문을 유지한다.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import yaml

from core import ics
from sources.jp.build_data import (
    KIND_BRIDGE,
    KIND_STATUTORY,
    KIND_SUBSTITUTE,
    RANGE_END,
    RANGE_START,
)

# PRODID 가 kr 과 같은 값인 것은 의도한 것이다.
#
# PRODID 는 이 파일을 만든 제품의 식별자이고, 두 피드를 만드는 제품은 같다.
# 나라마다 다른 값을 주면 같은 생성기가 둘인 것처럼 보인다. 뒤의 //KO 는
# 이 제품의 표기 언어이지 피드가 담은 나라가 아니다 — 어느 나라 공휴일인지는
# X-WR-CALNAME 과 파일 이름이 말한다(docs/holiday_06.md §4 의 PRODID 주).
PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "일본 공휴일"
TZID = "Asia/Tokyo"

# 읽을 곳. sources.jp.build_data.DATA_DIR 을 import 하지 않는다.
#
# 그쪽은 쓰는 쪽의 경로이고 여기는 읽는 쪽이다. 읽는 쪽이 쓰는 쪽의 상수에
# 묶이면 한쪽만 옮길 때 조용히 따라 움직인다. 두 값이 같은 곳을 가리키는지는
# 테스트가 본다(tests/test_jp_feed.py).
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "jp"

# feed_range() 를 두지 않는다.
#
# kr 은 상한을 시계에서 얻으므로 today 를 받아야 했다. jp 의 범위는 시계와
# 무관한 두 상수다 — 内閣府 CSV 가 담은 구간이 곧 범위이고, 그 구간은 우리가
# 언제 돌리든 같다. 인자 없이 답이 정해지는 것에 함수를 씌우면 시계가 관여하는
# 것처럼 읽힌다.

_WHITESPACE = re.compile(r"\s+")

# basis.trigger_weekday 를 한국어로. 데이터에 있는 값만 옮긴다.
#
# 지금 14 건이 전부 日 이지만 나머지 요일도 적어 둔다. 표에 없는 값이 오면
# 예외를 던진다 — 조용히 통과시키면 원본의 표기가 바뀐 것을 놓친다.
_WEEKDAY_KO = {
    "月": "월요일",
    "火": "화요일",
    "水": "수요일",
    "木": "목요일",
    "金": "금요일",
    "土": "토요일",
    "日": "일요일",
}

# SUMMARY 의 괄호. 전각이다(U+FF08 / U+FF09).
#
# 괄호 안이 일본어 축일명이라 그 표기를 따른다. 반각을 쓰면 일본어 글자 사이에
# 폭이 다른 문자가 끼어 어색해진다.
_OPEN, _CLOSE = "（", "）"

# 원인이 둘일 때의 구분자. 전각 중점(U+30FB)이다.
#
# 가운뎃점 · (U+00B7) 이 아니다. 그쪽은 kr 이 쓰는 문자이고 일본어 표기의
# 中黒 과 다르다. 눈으로는 거의 구분되지 않아 코드포인트로 적어 둔다.
_SEPARATOR = "・"


def _one_line(text: str) -> str:
    return _WHITESPACE.sub(" ", (text or "").strip())


def _checked(entry: dict, path: Path) -> dict:
    """항목 하나를 검사해 그대로 돌려준다. 손대지 않는다."""
    where = f"{path.name}: {entry.get('date')!r} {entry.get('name')!r}"

    day = entry.get("date")
    # datetime 은 date 의 하위 클래스라 순서가 중요하다. 먼저 걸러야 한다.
    if isinstance(day, datetime) or not isinstance(day, date):
        raise ics.IcsError(f"{where}: date 가 종일 날짜가 아니다.")

    # 범위 밖은 거른다. 조용히 빼면 발행 범위가 데이터에 따라 말없이 움직인다.
    if not (RANGE_START <= day <= RANGE_END):
        raise ics.IcsError(
            f"{where}: 발행 범위 {RANGE_START}~{RANGE_END} 밖이다.\n"
            "범위는 sources.jp.build_data 가 정한다. data/jp/ 를 다시 만들 것."
        )

    for key in ("name", "uid_token", "kind", "source"):
        if not entry.get(key):
            raise ics.IcsError(f"{where}: {key} 가 비었다.")

    if entry["kind"] not in (KIND_STATUTORY, KIND_SUBSTITUTE, KIND_BRIDGE):
        raise ics.IcsError(f"{where}: 모르는 kind {entry['kind']!r}")

    return entry


def _entries() -> list:
    """data/jp/*.yaml 전부. 날짜 오름차순.

    파일은 이름순으로 읽는다. 항목 순서는 파일 안의 나열에 매이지 않게 날짜로
    다시 정한다 — core.ics.assign_uids() 가 어차피 (날짜, token) 으로 재정렬
    하지만, 여기서 나가는 값도 실행마다 같아야 한다.
    """
    paths = sorted(DATA_DIR.glob("*.yaml"))
    if not paths:
        raise ics.IcsError(
            f"{DATA_DIR} 에 YAML 이 하나도 없다.\n"
            "uv run python -m sources.jp.build_data 로 다시 만들 것."
        )

    out = []
    for path in paths:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for entry in doc.get("holidays") or ():
            checked = _checked(entry, path)
            # 진단용으로 어느 파일에서 왔는지만 얹는다. 값은 손대지 않는다.
            out.append({**checked, "_file": path.name})
    out.sort(key=lambda e: e["date"])
    return out


def _by_date(entries) -> dict:
    """{날짜: 항목}. 괄호 안의 이름을 지어내지 않고 조회하기 위한 색인이다.

    한 날짜에 두 항목이 있으면 멈춘다. 内閣府 CSV 는 한 날짜에 한 행이므로
    (sources/jp/build_data.py 의 uid_token 절) 겹치면 그것이 신호다.
    """
    out = {}
    for entry in entries:
        day = entry["date"]
        if day in out:
            raise ics.IcsError(
                f"{day.isoformat()} 에 항목이 둘이다: "
                f"{out[day]['name']!r}({out[day]['_file']}) / "
                f"{entry['name']!r}({entry['_file']})\n"
                "어느 쪽 이름을 원인으로 적을지 정할 수 없다."
            )
        out[day] = entry
    return out


def _basis(entry: dict, *keys) -> tuple:
    """basis 에서 필요한 값들. 하나라도 없으면 멈춘다."""
    basis = entry.get("basis") or {}
    values = []
    for key in keys:
        value = basis.get(key)
        if not value:
            raise ics.IcsError(
                f"{entry['_file']}: {entry['date']} {entry['name']!r} "
                f"(kind={entry['kind']!r}) 의 basis 에 {key} 가 없다."
            )
        values.append(value)
    return tuple(values)


def _name_on(by_date: dict, day: date, entry: dict, label: str) -> str:
    """그 날짜 항목의 이름. 없으면 멈춘다 — 빈 문자열로 넘어가지 않는다."""
    found = by_date.get(day)
    if found is None:
        raise ics.IcsError(
            f"{entry['_file']}: {entry['date']} {entry['name']!r} 의 "
            f"basis.{label} 가 가리키는 {day.isoformat()} 에 항목이 없다.\n"
            "이름을 지어내지 않는다. data/jp/ 를 확인할 것."
        )
    return found["name"]


def _weekday_ko(entry: dict, raw: str) -> str:
    try:
        return _WEEKDAY_KO[raw]
    except KeyError:
        raise ics.IcsError(
            f"{entry['_file']}: {entry['date']} {entry['name']!r} 의 "
            f"basis.trigger_weekday 가 모르는 값이다: {raw!r}\n"
            f"아는 값은 {''.join(_WEEKDAY_KO)} 뿐이다."
        ) from None


def _summary(entry: dict, by_date: dict) -> str:
    """SUMMARY. 대체휴일·국민의 휴일만 원인을 괄호로 덧붙인다.

    休日 만으로는 구독자가 무엇 때문에 쉬는지 알 수 없고, 같은 이름이 한 해에
    여러 번 나오므로 캘린더에서 구분도 되지 않는다.

    분기는 kind 로 한다. basis 키 모양으로 판별하지 않는다 — 지금은
    kind: substitute ⟺ basis.trigger_date 존재 가 143 건 전체에서 성립하지만,
    그것은 관측이지 규약이 아니다. 키 모양으로 갈래를 정하면 데이터가 한 건
    달라질 때 조용히 다른 갈래로 떨어진다.

    괄호 안의 이름은 지어내지 않고 그 날짜의 항목에서 읽는다.
    """
    if entry["kind"] == KIND_STATUTORY:
        return entry["name"]

    if entry["kind"] == KIND_SUBSTITUTE:
        (trigger_date,) = _basis(entry, "trigger_date")
        origin = _name_on(by_date, trigger_date, entry, "trigger_date")
    else:
        prev_date, next_date = _basis(entry, "prev_date", "next_date")
        origin = _SEPARATOR.join((
            _name_on(by_date, prev_date, entry, "prev_date"),
            _name_on(by_date, next_date, entry, "next_date"),
        ))
    return f"{entry['name']}{_OPEN}{origin}{_CLOSE}"


def _description(entry: dict, by_date: dict) -> str:
    """DESCRIPTION. 한 줄이다.

    줄바꿈을 넣지 않는다. 캘린더 클라이언트마다 여러 줄 DESCRIPTION 을 접는
    방식이 달라 같은 피드가 다르게 보인다.

    근거는 데이터의 source 원문 그대로다. 그 안의 괄호는 반각인데
    (sources/jp/build_data.py 의 LAW 상수) 고치지 않는다 — 우리가 조립하는
    SUMMARY 괄호와 다른 문자지만, source 는 데이터 원문이라 손댈 자리가 아니다.
    _one_line() 만 통과시킨다.
    """
    source = _one_line(entry["source"])
    basis_line = f"근거: {source}"

    if entry["kind"] == KIND_STATUTORY:
        return basis_line

    if entry["kind"] == KIND_SUBSTITUTE:
        trigger_date, trigger_weekday = _basis(entry, "trigger_date", "trigger_weekday")
        name = _name_on(by_date, trigger_date, entry, "trigger_date")
        weekday = _weekday_ko(entry, trigger_weekday)
        return f"{trigger_date.isoformat()} {name}({weekday})의 대체 휴일입니다. {basis_line}"

    # 두 축일 사이에 낀 하루. 앞말이 일본어라 한국어 조사의 형태를 고를 수 없어
    # 과/와 를 쓰지 않고 쉼표로 잇는다 — 敬老の日과 로 할지 敬老の日와 로 할지는
    # 뒤따르는 글자의 받침으로 정해지는데, 그 글자가 일본어면 받침이 없다.
    # 매년 원인이 바뀌므로 손으로 골라 둘 수도 없다.
    prev_date, next_date = _basis(entry, "prev_date", "next_date")
    prev_name = _name_on(by_date, prev_date, entry, "prev_date")
    next_name = _name_on(by_date, next_date, entry, "next_date")
    return (
        f"{prev_date.isoformat()} {prev_name}, {next_date.isoformat()} {next_name} "
        f"사이의 휴일입니다. {basis_line}"
    )


def _event(entry: dict, by_date: dict) -> ics.Event:
    """항목 하나 → Event 하나."""
    return ics.Event(
        day=entry["date"],
        summary=_summary(entry, by_date),
        kind=entry["kind"],
        description=_description(entry, by_date),
        # 항상 False. 모듈 docstring 의 verified 절 참조.
        provisional=False,
        # UID 의 뒷부분. 데이터가 143 건 전부 들고 있다. kind 에서 유도하지
        # 않는 이유는 sources/jp/build_data.py 의 uid_token 절에 있다 —
        # 休日 은 振替/国民 어느 쪽으로 판정되든 token 이 kyujitsu 하나다.
        token=entry["uid_token"],
        # 진단 전용. token 이 겹쳐 멈출 때 어느 파일을 봐야 하는지 알려 준다.
        origin=f"file={entry['_file']!r} uid_token={entry['uid_token']!r}",
    )


def events() -> list:
    """data/jp/ 의 모든 이벤트. 날짜 오름차순.

    구간을 인자로 받지 않는다. jp 의 범위는 데이터가 곧 범위이고, 그 범위는
    RANGE_START~RANGE_END 로 이미 고정되어 있다(위 feed_range 주석 참조).
    """
    entries = _entries()
    by_date = _by_date(entries)
    return [_event(entry, by_date) for entry in entries]


def build(*, dtstamp, previous: bytes = None) -> bytes:
    """피드 한 벌. 같은 (dtstamp, previous) 면 같은 바이트가 나온다.

    previous 는 직전에 발행한 .ics 의 바이트다. SEQUENCE 를 정하는 데만 쓴다.
    None 이면 첫 발행으로 보고 전부 0 이 나간다.

    kr 의 build() 와 달리 today 를 받지 않는다. 받을 자리가 없다 — 범위가
    시계에서 나오지 않는다.
    """
    return ics.render(
        events(),
        dtstamp=dtstamp,
        prodid=PRODID,
        calname=CALNAME,
        tzid=TZID,
        previous=previous,
    )
