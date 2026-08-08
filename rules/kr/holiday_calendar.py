"""대한민국 공휴일 달력.

    holidays_on(day)                  -> 그 날짜의 공휴일 목록
    substitute_eligibility(holiday, day) -> 대체공휴일 대상 여부
    resolve_lunar(key, year)          -> 음력 공휴일의 양력 환산

조회 축은 날짜다. substitute_rules.eligibility_for_date 와 같은 축을 쓴다.
연 단위 조회는 두지 않는다. 규칙이 연중에 바뀌는 해가 있어 답이 하나로 정해지지 않는다.

--------------------------------------------------------------------------
범위
--------------------------------------------------------------------------
양력 고정 공휴일, 음력 공휴일(설날·추석·부처님오신날), 지정 공휴일(선거일·
임시공휴일), 대체공휴일까지 다룬다.

음력 날짜는 계산으로 유도한다. rules/kr/lunar.py 가 삭과 중기에서 달 번호를
세우고 rules/kr/astro.py 가 그 시각을 KST 로 옮긴다. 한국천문연구원 발표값과
갈리는 해는 lunar_holidays.yaml 의 exceptions 가 발표값으로 덮는다.

require_supported() / LunarNotImplemented 는 남아 있지만 지금은 아무것도
막지 않는다. unresolved_holidays() 가 비었기 때문이다. 정답 픽스처의
depends_on 도 같은 이유로 더 이상 skip 되지 않는다.

--------------------------------------------------------------------------
일요일
--------------------------------------------------------------------------
공휴일 규정은 일요일을 공휴일로 열거한다. 대체공휴일 판정에는 그대로 쓰지만
(일요일과 겹치면 대체공휴일이 생긴다) 결과 목록에는 넣지 않는다.
substitute_holidays.yaml 의 sunday_in_output: false 가 그 결정이다.
토요일은 공휴일이 아니다. 판정에도 출력에도 들어가지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

import yaml

from rules.kr import lunar, substitute_rules

_HERE = Path(__file__).parent
SOLAR_PATH = _HERE / "solar_holidays.yaml"
DESIGNATED_PATH = _HERE / "designated_holidays.yaml"
LUNAR_PATH = _HERE / "lunar_holidays.yaml"

KIND_STATUTORY = "statutory"
KIND_SUBSTITUTE = "substitute"
SUNDAY = 6
SATURDAY = 5

# 대체공휴일이 원래 공휴일에서 얼마나 멀어질 수 있는지의 상한.
# 연휴가 겹치고 제2항 연장까지 걸려도 이 안에서 끝난다. 무한 루프 방지용이다.
_MAX_PLACEMENT_SEARCH = 30


class CalendarError(ValueError):
    """달력 데이터가 잘못되었다."""


class UnsupportedYear(CalendarError):
    """신뢰 구간 밖의 날짜를 물었다.

    빈 결과를 돌려주지 않는 이유: 데이터가 없는 것과 공휴일이 아닌 것은 다르다.
    둘을 같은 값으로 답하면 호출자가 구분할 수 없고, 누락이 오류로 드러나지 않는다.
    피드로 나가면 구독자 캘린더에서 공휴일이 조용히 사라진다.
    """


# 조문의 호 번호를 공휴일로 옮기는 매핑이 미확인이라 답할 수 없을 때.
# substitute_rules 쪽에서 정의한 것을 그대로 쓴다. 호출자가 두 모듈을 다 import
# 하지 않아도 되게 여기서도 이름을 노출한다.
MappingUnresolved = substitute_rules.MappingUnresolved


class LunarNotImplemented(NotImplementedError):
    """음력 공휴일은 아직 환산하지 못한다.

    NotImplementedError 를 상속하되 별도 타입으로 둔 이유는, 호출자가 "아직 안 만든
    기능"과 "정말로 틀린 답"을 구분해야 하기 때문이다. 테스트는 이 예외를 skip 으로
    돌리고, 일반적인 실패와 섞이지 않게 한다.
    """


@dataclass(frozen=True)
class Holiday:
    name: str
    kind: str
    key: str = ""
    source_key: str = ""  # 대체공휴일일 때 원인이 된 공휴일 키
    provisional: bool = False  # 개정 확인 시점 이후라 확정이 아님

    # 음력 공휴일 전용. 초하루를 정한 삭이 KST 자정에 가까워 계산 오차만으로
    # 날짜가 하루 갈릴 수 있는 자리다. 값을 바꾸지는 않는다 — 표시만 한다.
    # 옮기려면 발표값이 있어야 하고 그건 lunar_holidays.yaml 의 exceptions 다.
    lunar_boundary_risk: bool = False


# ---------------------------------------------------------------------------
# 데이터 적재
# ---------------------------------------------------------------------------


def _read(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _coverage_of(raw: dict, path: Path) -> substitute_rules.Coverage:
    """축 선택 규칙은 substitute_rules 가 들고 있다. 여기서 다시 쓰지 않는다.

    규칙이 두 군데에 있으면 한쪽만 고쳐 놓고 표마다 다른 스키마를 허용하게 된다.
    예외 타입만 이 모듈 것으로 바꿔 준다. 호출자가 두 모듈을 다 알 필요는 없다.
    """
    try:
        return substitute_rules.read_coverage(raw, path.name)
    except substitute_rules.RuleTableError as exc:
        raise CalendarError(str(exc)) from exc


@lru_cache(maxsize=1)
def _rules():
    return substitute_rules.load()


@lru_cache(maxsize=1)
def _solar_raw() -> dict:
    return _read(SOLAR_PATH)


@lru_cache(maxsize=1)
def _designated_raw() -> dict:
    return _read(DESIGNATED_PATH)


@lru_cache(maxsize=1)
def _solar() -> tuple:
    raw = _solar_raw()
    registry = _rules().holidays
    out = []
    for h in raw["holidays"]:
        if h["key"] not in registry:
            raise CalendarError(
                f"solar_holidays.yaml 의 키 {h['key']!r} 가 공휴일 레지스트리에 없다. "
                "substitute_holidays.yaml 의 holidays 에 추가할 것."
            )
        out.append(h)
    return tuple(out)


@lru_cache(maxsize=1)
def _designated() -> dict:
    raw = _designated_raw()
    kinds = raw["kinds"]
    by_date = {}
    for h in raw["holidays"]:
        if h["kind"] not in kinds:
            raise CalendarError(f"designated_holidays.yaml: 모르는 kind {h['kind']!r}")
        by_date.setdefault(h["date"], []).append(h)
    return {"kinds": kinds, "by_date": by_date}


@lru_cache(maxsize=1)
def _lunar_raw() -> dict:
    return _read(LUNAR_PATH)


@lru_cache(maxsize=1)
def _lunar() -> dict:
    """음력 공휴일 정의와 발표값 예외.

    exceptions 는 (키, 연도) → 발표 날짜다. 우리 계산과 한국천문연구원 발표가
    갈릴 때 발표를 쓴다. 계산을 고치지 않는 이유는 lunar_holidays.yaml 참조.
    """
    raw = _lunar_raw()
    registry = _rules().holidays
    entries = []
    for h in raw["holidays"]:
        if h["key"] not in registry:
            raise CalendarError(
                f"lunar_holidays.yaml 의 키 {h['key']!r} 가 공휴일 레지스트리에 없다."
            )
        entries.append(h)

    keys = {h["key"] for h in entries}
    exceptions = {}
    for item in raw.get("exceptions") or ():
        if item["key"] not in keys:
            raise CalendarError(
                f"lunar_holidays.yaml exceptions: 모르는 키 {item['key']!r}"
            )
        published = item.get("published")
        if not isinstance(published, date):
            raise CalendarError(
                f"lunar_holidays.yaml exceptions {item['key']} {item.get('year')}: "
                "published 가 날짜가 아니다. 발표값 없이 예외를 둘 수 없다."
            )
        if not (item.get("source") or "").strip():
            raise CalendarError(
                f"lunar_holidays.yaml exceptions {item['key']} {item.get('year')}: "
                "source 가 비어 있다. 계산을 덮어쓰려면 무엇으로 덮는지 적어야 한다."
            )
        exceptions[(item["key"], item["year"])] = published
    return {"entries": tuple(entries), "keys": frozenset(keys), "exceptions": exceptions}


def _lunar_keys() -> frozenset:
    return _lunar()["keys"]


@lru_cache(maxsize=1)
def _name_to_key() -> dict:
    """이름·별칭 → 키. 대응표는 YAML 에 있고 여기서는 뒤집기만 한다."""
    out = {}
    for key, meta in _rules().holidays.items():
        out[key] = key
        out[meta["name"]] = key
        for alias in meta.get("aliases") or ():
            out[alias] = key
    return out


# ---------------------------------------------------------------------------
# 미구현 공휴일
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def coverage() -> dict:
    """각 소스의 신뢰 구간과 그 교집합.

    최종 달력이 답할 수 있는 범위는 교집합이다. 한 소스라도 못 믿는 구간은
    전체가 못 믿는 구간이다. 가장 좁은 소스가 전체를 결정한다.

    교집합은 축별로 따로 낸다. 규칙 축(confirmed_through)과 반영 축
    (last_synced_at)은 다른 보증이므로 한 값으로 뭉치지 않는다.
    뭉쳐서 min 을 잡으면 규칙 개정을 2028 년까지 확인해 둔 사실이 지정 표의
    동기화 시점에 가려져 사라진다. substitute_rules.Coverage docstring 참조.

    음력 표의 confirmed_through 는 개정이 아니라 대조를 뜻한다. "이 구간까지
    우리 계산을 발표값과 맞춰 봤다"이다. 주장하는 바는 같다 — 밖은 낸 답이
    틀릴 수 있다. 그래서 같은 축에 싣는다.
    """
    sources = {
        "solar_holidays.yaml": _coverage_of(_solar_raw(), SOLAR_PATH),
        "lunar_holidays.yaml": _coverage_of(_lunar_raw(), LUNAR_PATH),
        "designated_holidays.yaml": _coverage_of(_designated_raw(), DESIGNATED_PATH),
        "substitute_holidays.yaml": _rules().coverage,
    }

    def narrowest(axis: str):
        values = [getattr(c, axis) for c in sources.values() if getattr(c, axis) is not None]
        return min(values) if values else None

    # start 는 가장 늦은 것을, 각 상한은 가장 이른 것을 따른다.
    # 한 소스라도 못 믿는 구간은 전체가 못 믿는 구간이다.
    effective = substitute_rules.Coverage(
        start=max(c.start for c in sources.values()),
        confirmed_through=narrowest("confirmed_through"),
        last_synced_at=narrowest("last_synced_at"),
    )
    for axis in substitute_rules.AXES:
        upper = getattr(effective, axis)
        if upper is not None and effective.start > upper:
            raise CalendarError(
                f"소스들의 coverage {axis} 구간이 비었다:\n"
                + "\n".join(f"  {name}: {c}" for name, c in sources.items())
            )
    return {"sources": sources, "effective": effective, "unresolved": unresolved_holidays()}


def coverage_report() -> str:
    """사람이 읽는 coverage 요약. 로그·CLI 용."""
    cov = coverage()
    width = max(len(n) for n in cov["sources"])
    lines = ["공휴일 데이터 신뢰 구간 (kr)", ""]
    for name, c in cov["sources"].items():
        lines.append(f"  {name:<{width}}  {c}")
    eff = cov["effective"]
    lines += [
        "",
        f"  {'→ 최종(교집합)':<{width}}  {eff}",
        "",
        f"  {eff.start.isoformat()} 이전     : UnsupportedYear 로 거부",
    ]
    if eff.confirmed_through is not None:
        lines.append(
            f"  {eff.confirmed_through.isoformat()} 이후    : 규칙 개정 미확인. "
            "답하되 항목마다 provisional: true"
        )
    if eff.last_synced_at is not None:
        lines.append(
            f"  {eff.last_synced_at.isoformat()} 이후    : 지정 공휴일 미반영. "
            "답은 그대로이나 목록이 늘어날 수 있다 (may_grow)"
        )
    lines += [
        "",
        "  두 상한은 다른 보증이다. 앞은 '낸 답이 틀릴 수 있다', 뒤는 '항목이 더 생길 수 있다'.",
        "",
        "  미구현 공휴일(구간과 무관): "
        + (", ".join(sorted(cov["unresolved"])) or "없음"),
    ]
    return "\n".join(lines)


def require_covered(day: date) -> None:
    """데이터 완결성 경계 이전이면 UnsupportedYear. 상한은 보지 않는다."""
    effective = coverage()["effective"]
    if not effective.contains(day):
        raise UnsupportedYear(
            f"{day.isoformat()} 는 데이터 완결성 경계({effective.start.isoformat()}) "
            "이전이다.\n빈 결과를 돌려주지 않는 이유는 '데이터 없음'과 '공휴일 아님'이 "
            "다르기 때문이다. 범위를 넓히려면 각 소스의 데이터를 먼저 채우고 coverage.from "
            "을 앞당길 것. 추정으로 채우지 말 것.\n" + coverage_report()
        )


def is_provisional(day: date) -> bool:
    """규칙 개정 확인 시점 이후인가. 답은 나오지만 확정이 아니다.

    이 축은 이미 낸 항목이 달라질 수 있다는 뜻이다. 그래서 항목마다 붙는다
    (Holiday.provisional).
    """
    return coverage()["effective"].is_provisional(day)


def may_grow(day: date) -> bool:
    """지정 공휴일 반영 시점 이후인가. 목록에 항목이 더 생길 수 있다.

    is_provisional 과 섞지 말 것. 이 축에 걸린 날짜는 낸 답이 틀린 것이 아니라
    옆자리가 비어 있을 수 있다는 뜻이다. 임시공휴일은 국무회의 의결로 짧은 예고
    후 정해지므로, 반영 시점 이후 날짜의 임시공휴일을 다 아는 것은 원리적으로
    불가능하다. 없는 것이 누락이 아니라 정상이다.

    항목 단위 플래그로 두지 않는 이유도 같다. 없는 항목에는 플래그를 달 수 없다.
    날짜 단위 질문으로만 성립한다.

    피드 생성기가 볼 자리다. 이 축 밖의 날짜를 발행했다면 KASI 를 다시 조회해
    새 지정을 반영하고 재발행해야 한다. 발행 시점을 지나도 답이 자동으로
    갱신되지는 않는다.

    두 번째 효과가 하나 있다. 새로 지정된 임시공휴일이 대체공휴일이 놓일 자리를
    차지하면(제3조제1항 본문) 이미 낸 대체공휴일 날짜가 밀린다. 즉 이 축은
    드물게 기존 항목까지 움직일 수 있다. 그 경우까지 provisional 로 올리면
    반영 시점 이후 전 구간이 잠정이 되어 규칙 축의 신호가 죽으므로 그렇게 하지
    않았다. 재발행으로 흡수한다.
    """
    return coverage()["effective"].may_grow(day)


def unresolved_holidays() -> frozenset:
    """아직 날짜를 계산하지 못하는 공휴일 키.

    지금은 비어 있다. 음력이 들어오면서 마지막 항목이 빠졌다.
    함수는 남겨 둔다. 미구현을 표현하는 자리가 없어지면 다음에 같은 상황이
    왔을 때 그 사실이 어디에도 드러나지 않는다.
    """
    return frozenset()


def require_supported(key: str) -> None:
    """이 공휴일을 계산할 수 있는지 확인한다. 못 하면 LunarNotImplemented.

    정답 픽스처의 depends_on 이 이 함수를 통해 skip 여부를 정한다.
    지금은 모든 키가 계산 가능하므로 아무것도 skip 되지 않는다.
    """
    if key not in _rules().holidays:
        raise CalendarError(f"모르는 공휴일 키: {key!r}")
    if key in unresolved_holidays():
        raise LunarNotImplemented(
            f"{key}: 아직 환산하지 못한다. rules/kr/lunar_holidays.yaml 참조."
        )


def resolve_lunar(key: str, year: int) -> date:
    """음력 공휴일의 그 해 양력 날짜.

    계산이 1차다(rules/kr/lunar.py). 다만 한국천문연구원 발표값과 갈리는 해가
    있으면 exceptions 에 적힌 발표값이 이긴다. 한국 공식 역서는 발표값이고
    우리 계산은 2차 소스이기 때문이다. lunar_holidays.yaml 참조.
    """
    if key not in _lunar_keys():
        raise CalendarError(f"{key!r} 는 음력 공휴일이 아니다. holidays_on() 을 쓸 것.")
    require_supported(key)

    return _lunar_anchor(key, year)[0]


def _lunar_anchor(key: str, year: int, sui: dict = None) -> tuple:
    """(양력 날짜, 경계 위험 여부).

    발표값 예외가 있으면 그 값을 쓰고 위험은 False 다. 계산이 자정에 걸려
    흔들리든 말든 발표값이 답을 정했으므로 더 이상 갈릴 자리가 아니다.
    """
    table = _lunar()
    published = table["exceptions"].get((key, year))
    if published is not None:
        return published, False

    spec = next(h for h in table["entries"] if h["key"] == key)["lunar"]
    if sui is None:
        sui = {(m.number, m.leap): m for m in lunar.months_of_sui(year)}
    month = sui.get((spec["month"], False))
    if month is None:
        raise CalendarError(f"{year} 년 세에 음력 {spec['month']} 월이 없다.")
    return month.day(spec["day"]), month.boundary_risk


# ---------------------------------------------------------------------------
# 달력 조립
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BoundaryRisk:
    """초하루가 하루 갈릴 수 있는 자리에 놓인 음력 공휴일."""

    year: int
    key: str
    name: str
    day: date
    month_start: date
    margin_minutes: float

    def __str__(self) -> str:
        return (
            f"{self.year}  {self.name:<12} {self.day}  "
            f"초하루 {self.month_start}  자정에서 {self.margin_minutes:6.2f} 분"
        )


def lunar_boundary_risks(first_year: int, last_year: int) -> tuple:
    """그 구간에서 초하루가 위태로운 음력 공휴일 목록.

    coverage 를 보지 않는다. 이건 우리 데이터 표의 성질이 아니라 천문 계산의
    성질이라, 우리가 답하기로 한 구간과 무관하게 존재한다. 오히려 구간을 넓힐지
    말지 판단하는 근거가 이 목록이므로, 구간에 갇히면 볼 수 없게 된다.

    값을 바꾸지 않는다. 위험한 자리를 알려 줄 뿐이다. 옮기려면 발표값이
    있어야 하고 그건 lunar_holidays.yaml 의 exceptions 다.
    """
    entries = _lunar()["entries"]
    found = []
    for year in range(first_year, last_year + 1):
        sui = {(m.number, m.leap): m for m in lunar.months_of_sui(year)}
        for entry in entries:
            month = sui.get((entry["lunar"]["month"], False))
            if month is None or not month.boundary_risk:
                continue
            found.append(
                BoundaryRisk(
                    year=year,
                    key=entry["key"],
                    name=entry["name"],
                    day=month.day(entry["lunar"]["day"]),
                    month_start=month.start,
                    margin_minutes=month.start_margin_minutes,
                )
            )
    return tuple(sorted(found, key=lambda r: r.margin_minutes))


def lunar_boundary_report(first_year: int, last_year: int) -> str:
    """사람이 읽는 경계 위험 요약."""
    risks = lunar_boundary_risks(first_year, last_year)
    threshold = lunar.BOUNDARY_MARGIN_MINUTES
    lines = [
        f"음력 초하루 경계 위험 ({first_year}~{last_year})",
        f"기준: 삭이 KST 자정에서 {threshold:.0f} 분 이내",
        "",
    ]
    if not risks:
        lines += [
            "  해당 없음.",
            "",
            "  이 구간의 음력 공휴일은 전부 삭이 자정에서 충분히 떨어져 있다.",
            "  급수 오차가 초하루를 하루 옮길 수 있는 자리가 없다는 뜻이며,",
            "  그 자체가 이 구간의 안전 근거다.",
        ]
        return "\n".join(lines)

    lines += [f"  {risk}" for risk in risks]
    lines += [
        "",
        f"  {len(risks)} 건. 값은 바꾸지 않았다.",
        "  각 날짜를 한국천문연구원 발표값으로 확인할 것.",
        "  갈리면 lunar_holidays.yaml 의 exceptions 에 적는다. 계산을 고치지 않는다.",
    ]
    return "\n".join(lines)


def _active(entry: dict, day: date) -> bool:
    start = entry.get("effective_from")
    end = entry.get("effective_until")
    if start and day < start:
        return False
    if end and day > end:
        return False
    return True


def _base_holidays(year: int) -> dict:
    """대체공휴일을 뺀 그 해의 공휴일."""
    out = {}
    for h in _solar():
        day = date(year, h["month"], h["day"])
        if not _active(h, day):
            continue
        out.setdefault(day, []).append(Holiday(name=h["name"], kind=KIND_STATUTORY, key=h["key"]))

    # 세는 세 공휴일이 공유하므로 한 번만 짓는다. 공휴일마다 다시 지으면
    # 같은 삭·중기 계산을 세 번 돌리게 된다.
    sui = {(m.number, m.leap): m for m in lunar.months_of_sui(year)}
    for h in _lunar()["entries"]:
        anchor, risk = _lunar_anchor(h["key"], year, sui)
        if not _active(h, anchor):
            continue
        out.setdefault(anchor, []).append(
            Holiday(
                name=h["name"], kind=KIND_STATUTORY, key=h["key"], lunar_boundary_risk=risk
            )
        )
        # 연휴는 같은 key 를 단다. 대체공휴일 판정이 이 key 로 호 소속을 찾기
        # 때문이다. 연휴 이름만 다르고 규칙상 성질은 명절 당일과 같다.
        # key 를 비우면 연휴가 일요일에 걸려도 대체공휴일이 생기지 않는다.
        #
        # 경계 위험도 함께 단다. 초하루가 밀리면 연휴 3 일이 통째로 따라 밀리므로
        # 당일만 표시하면 연휴 이틀이 위험 표시 없이 나간다.
        leave = h.get("leave") or {}
        before, after = leave.get("days_before", 0), leave.get("days_after", 0)
        for offset in range(-before, after + 1):
            if offset == 0:
                continue
            out.setdefault(anchor + timedelta(days=offset), []).append(
                Holiday(
                    name=h["leave_name"],
                    kind=KIND_STATUTORY,
                    key=h["key"],
                    lunar_boundary_risk=risk,
                )
            )

    designated = _designated()
    for day, entries in designated["by_date"].items():
        if day.year != year:
            continue
        for e in entries:
            out.setdefault(day, []).append(Holiday(name=e["name"], kind=e["kind"], key=""))
    return out


def _eligible_overlaps(holiday: Holiday, day: date) -> set:
    """이 공휴일이 그 날짜에서 어떤 겹침 조건에 걸리는지.

    등록된 공휴일은 규칙 테이블의 호 소속에서 나오고,
    지정 공휴일(선거일·임시공휴일)은 kind 의 substitute_eligible 이 결정한다.
    두 경로가 갈리는 이유는 지정 공휴일이 제3조의 어느 호에 해당하는지 확인되지
    않았기 때문이다. designated_holidays.yaml 의 kinds source_todo 참조.

    반환값이 None 이면 "모른다"는 뜻이다. 빈 집합("대상 아님")과 구분해야 한다.
    """
    if holiday.kind in (KIND_STATUTORY,) and holiday.key:
        ruleset = _rules().ruleset_on(day)
        if ruleset is None:
            return set()
        try:
            matched = ruleset.clauses_for(holiday.key)
        except substitute_rules.MappingUnresolved:
            return None
        return {o for c in matched for o in c.overlaps}

    kinds = _designated()["kinds"]
    spec = kinds.get(holiday.kind) or {}
    eligible = spec.get("substitute_eligible")

    if eligible == "unresolved":
        # 선거일이 그렇다. 제2조제10의2호(가지번호)인데 제3조는 제10호까지만 열거한다.
        # 가지번호가 그 범위에 드는지는 법제처 해석이 필요하다.
        # true 로도 false 로도 답하지 않는다. 모른다를 모른다로 돌려준다.
        return None
    if eligible is True:
        return {"saturday", "sunday", "other_holiday_on_weekday"}
    return set()


def _placement_flags() -> dict:
    ids = {p["id"] for p in _rules().placement_rules}
    return {
        "requeue_saturday": "제3조제3항" in ids,  # 대체공휴일이 토요일이면 다시 옮긴다
        "extend_on_collision": "제3조제2항" in ids,  # 겹치면 다음 비공휴일까지 연장
    }


def _calendar(year: int) -> dict:
    """그 해의 공휴일. 대체공휴일 포함. 결과는 날짜 → Holiday 목록."""
    # 대체공휴일은 연말 공휴일에서 다음 해로 넘어갈 수 있으므로 앞뒤 해를 함께 짠다.
    span = {}
    for y in (year - 1, year, year + 1):
        for day, items in _base_holidays(y).items():
            span.setdefault(day, []).extend(items)

    flags = _placement_flags()

    def is_rule_holiday(d: date) -> bool:
        """대체공휴일 계산에서의 공휴일. 일요일을 포함한다."""
        return d.weekday() == SUNDAY or d in span

    uncertain = set()

    for day in sorted(span):
        holidays = [h for h in span[day] if h.kind != KIND_SUBSTITUTE]
        weekend = day.weekday() in (SATURDAY, SUNDAY)
        coincide = day.weekday() < SATURDAY and len(holidays) >= 2

        # 매핑 미확인 공휴일이 주말에 있거나 평일에 겹치면 대체공휴일이 생길 수도,
        # 안 생길 수도 있다. 어느 쪽인지 모르므로 그 자리를 불확실로 표시한다.
        # 표시만 하고 대체공휴일을 만들지는 않는다. 없는 확신을 만들지 않기 위해서다.
        if weekend or coincide:
            for h in holidays:
                if _eligible_overlaps(h, day) is None:
                    uncertain.update(_place(day, 1, is_rule_holiday, flags))
                    break

        triggered = []
        for h in holidays:
            overlaps = _eligible_overlaps(h, day)
            if overlaps is None:
                continue  # 모른다. 위에서 불확실로 표시했다.
            if day.weekday() == SATURDAY and "saturday" in overlaps:
                triggered.append(h)
            elif day.weekday() == SUNDAY and "sunday" in overlaps:
                triggered.append(h)

        if triggered:
            count = len(triggered) if flags["extend_on_collision"] else 1
            for offset, placed in enumerate(_place(day, count, is_rule_holiday, flags)):
                span.setdefault(placed, []).append(
                    Holiday(
                        name="대체공휴일",
                        kind=KIND_SUBSTITUTE,
                        source_key=triggered[min(offset, len(triggered) - 1)].key,
                    )
                )
            continue

        # 제1항제3호: 토·일이 아닌 날에 공휴일끼리 겹치는 경우.
        # 겹친 공휴일 중 어느 쪽이 트리거인지는 확정되지 않았다(3호-귀속-불명).
        # 어느 쪽이든 결과가 같으므로 겹침 1건당 대체공휴일 1일로 둔다.
        # 3일 이상 겹치는 경우의 연장 방식은 미해결이다(겹침-판정-대상-단위).
        if coincide:
            # source_key 는 겹친 공휴일 중 실제로 3호 대상인 쪽에서 고른다.
            # 목록의 첫 항목을 그냥 쓰면 대상이 아닌 공휴일이 원인으로 붙는다.
            # 2017-10-06 이 그 경우였다. 개천절과 추석 연휴가 10-03 에 겹치는데
            # 그 해 국경일은 아직 대체공휴일 대상이 아니었으므로 개천절은 트리거가
            # 될 수 없다. 그런데도 배열 순서상 개천절이 원인으로 붙었다.
            #
            # 대상이 둘 이상이면 여전히 어느 쪽인지 모른다. 그건 3호-귀속-불명이
            # 남아 있는 것이고 여기서 정하지 않는다. 다만 "대상이 아닌 것을
            # 원인으로 적는" 것은 미확정이 아니라 그냥 틀린 것이라 막는다.
            triggers = [
                h
                for h in holidays
                if (_eligible_overlaps(h, day) or set()) >= {"other_holiday_on_weekday"}
            ]
            if triggers:
                for placed in _place(day, 1, is_rule_holiday, flags):
                    span.setdefault(placed, []).append(
                        Holiday(
                            name="대체공휴일",
                            kind=KIND_SUBSTITUTE,
                            source_key=triggers[0].key,
                        )
                    )

    return {"span": span, "uncertain": uncertain}


def _place(start: date, count: int, is_rule_holiday, flags: dict) -> list:
    """대체공휴일을 놓을 날짜들. 제3조제1항 본문 + 제2항 + 제3항."""
    out = []
    day = start
    for _ in range(_MAX_PLACEMENT_SEARCH):
        if len(out) >= count:
            break
        day += timedelta(days=1)
        if is_rule_holiday(day) or day in out:
            continue
        if flags["requeue_saturday"] and day.weekday() == SATURDAY:
            continue  # 제3조제3항: 토요일에 놓이면 다음 비공휴일로 다시 옮긴다
        out.append(day)
    if len(out) < count:
        raise CalendarError(f"{start} 의 대체공휴일 배치를 {_MAX_PLACEMENT_SEARCH}일 안에 못 찾았다")
    return out


@lru_cache(maxsize=32)
def _calendar_cached(year: int) -> dict:
    return _calendar(year)


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------


def holidays_on(day: date) -> tuple:
    """그 날짜의 공휴일 목록. 공휴일이 아니면 빈 튜플.

    음력 공휴일은 포함되지 않는다. 모듈 docstring 참조.
    일요일 자체는 결과에 넣지 않는다(sunday_in_output: false).
    """
    if not isinstance(day, date):
        raise CalendarError(f"날짜가 아니다: {day!r}")
    require_covered(day)

    year = _calendar_cached(day.year)
    if day in year["uncertain"]:
        raise MappingUnresolved(
            f"{day.isoformat()} 가 대체공휴일인지 아닌지 유도할 수 없다.\n"
            "직전 공휴일이 주말에 걸리거나 다른 공휴일과 겹치는데, 그 공휴일이 "
            "대체공휴일 대상인지가 제2조 호 배열 미확인으로 정해지지 않는다.\n"
            "'대체공휴일 아님'으로 답하지 않는 이유는 모르는 것을 아는 것처럼 "
            "답하지 않기 위해서다. "
            "rules/kr/substitute_holidays.yaml 의 open_questions 제2조-호-배열 참조."
        )

    found = year["span"].get(day, ())
    if not is_provisional(day):
        return tuple(found)
    # 확정 구간 밖. 답은 그대로 두되 잠정임을 항목마다 표시한다.
    # 피드 생성기가 이 값을 보고 이벤트에 표시하거나 발행 범위를 자를 수 있다.
    return tuple(replace(h, provisional=True) for h in found)


def substitute_eligibility(holiday: str, day: date) -> dict:
    """그 날짜 기준으로 이 공휴일이 토/일과 겹칠 때 대체공휴일 대상인가.

    holiday 는 키('gwangbokjeol')도 이름('광복절')도 별칭('추석')도 받는다.
    대응표는 substitute_holidays.yaml 의 holidays 레지스트리에 있다.
    """
    key = _name_to_key().get(holiday)
    if key is None:
        raise CalendarError(f"모르는 공휴일: {holiday!r}")

    # 여기서는 규칙 표만 본다. 양력·지정 표를 건드리지 않으므로 규칙 표의 구간만 본다.
    rules_coverage = _rules().coverage
    if not rules_coverage.contains(day):
        raise UnsupportedYear(
            f"{day.isoformat()} 는 대체공휴일 규칙 표의 완결성 경계 "
            f"({rules_coverage.start.isoformat()}) 이전이다."
        )

    result = _rules().eligibility_for_date(key, day)
    return {
        "saturday": result.saturday,
        "sunday": result.sunday,
        "ruleset": result.ruleset,
        "clauses": result.clauses,
        "provisional": rules_coverage.is_provisional(day),
    }


if __name__ == "__main__":  # pragma: no cover
    print(coverage_report())
