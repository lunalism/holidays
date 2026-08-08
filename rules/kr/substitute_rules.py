"""substitute_holidays.yaml 로더.

규칙 테이블을 읽어 "이 공휴일이 토/일과 겹치면 대체공휴일 대상인가"를 유도한다.
유도는 조문의 각 호가 어떤 겹침 조건(overlaps)을 갖는지에서만 나온다.
공휴일 이름이나 group 으로 분기하는 곳은 없어야 한다.

    applies_to_saturday  = 유효한 호 중 overlaps 에 saturday 를 가진 호가 있는가
    applies_to_sunday    = 유효한 호 중 overlaps 에 sunday 를 가진 호가 있는가

"설·추석은 일요일만 대상"은 여기에 적혀 있지 않다. 설·추석이 제2호(overlaps: [sunday])에
속하고 국경일류가 제1호(overlaps: [saturday, sunday])에 속한다는 소속 관계에서 나온다.

배치 규칙(제3조제1항 본문·제2항·제3항)은 데이터로 읽어 두기만 하고 아직 계산하지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).parent / "substitute_holidays.yaml"

SATURDAY = "saturday"
SUNDAY = "sunday"


class RuleTableError(ValueError):
    """규칙 테이블 자체가 잘못되었다."""


@dataclass(frozen=True)
class Clause:
    """조문의 한 호."""

    id: str
    overlaps: tuple
    applies_to: frozenset
    verified: bool
    source_todo: str

    def covers(self, holiday: str) -> bool:
        return holiday in self.applies_to


@dataclass(frozen=True)
class Ruleset:
    """한 시점부터 유효한 규칙 묶음. 다음 ruleset 직전까지 유효하다."""

    id: str
    effective_from: date
    summary: str
    clauses: tuple
    source: str
    verified: bool
    source_todo: str

    def clauses_for(self, holiday: str) -> tuple:
        return tuple(c for c in self.clauses if c.covers(holiday))


@dataclass(frozen=True)
class Eligibility:
    """대체공휴일 대상 여부와 그 근거.

    saturday/sunday 만 보지 말 것. clauses 가 비어 있는데 True 면 유도가 깨진 것이다.
    """

    holiday: str
    saturday: bool
    sunday: bool
    ruleset: str          # 근거 ruleset id. 유효한 규칙이 없으면 None
    clauses: tuple        # 근거가 된 호의 id


@dataclass(frozen=True)
class Coverage:
    """데이터를 신뢰할 수 있는 구간. 두 축을 구분한다.

        start              데이터 완결성 경계. 이전은 조회를 거부한다.
        confirmed_through  개정을 확인한 시점. 이후는 답하되 잠정으로 표시한다.

    상한을 거부로 두지 않는 이유는 피드가 몇 년치를 미리 발행해야 하기 때문이다.
    또 미래의 임시공휴일이 없는 것은 누락이 아니라 아직 지정되지 않은 상태다.
    반대로 start 이전은 있었어야 할 데이터가 없는 것이라 성격이 다르다.
    """

    start: date
    confirmed_through: date

    def contains(self, day: date) -> bool:
        """조회 가능한가. 상한은 보지 않는다."""
        return day >= self.start

    def is_provisional(self, day: date) -> bool:
        return day > self.confirmed_through

    def __str__(self) -> str:
        return f"{self.start.isoformat()} ~ [확정 {self.confirmed_through.isoformat()}] ~ (잠정)"


@dataclass(frozen=True)
class RuleTable:
    coverage: Coverage
    weekly_holidays: frozenset
    sunday_in_output: bool
    overlap_vocabulary: frozenset
    placement_rules: tuple
    holidays: dict
    rulesets: tuple       # effective_from 오름차순
    open_questions: tuple

    # -- 조회 -------------------------------------------------------------

    def ruleset_on(self, day: date):
        """그 날짜에 유효했던 ruleset. 제도 도입 전이면 None."""
        active = None
        for rs in self.rulesets:
            if rs.effective_from <= day:
                active = rs
            else:
                break
        return active

    def eligibility_for_date(self, holiday: str, day: date) -> Eligibility:
        """그 날짜 기준 대체공휴일 대상 여부.

        조회 단위는 날짜뿐이다. 연 단위 조회는 두지 않는다.
        규칙이 연중에 바뀌는 해(2021-08-04 등)에는 연 단위 답이 성립하지 않고,
        성립하는 척하면 어느 쪽이든 절반은 틀린 답을 조용히 돌려주게 된다.
        연 단위 집계가 정말 필요해지면 그때 날짜 순회로 구현할 것.
        """
        if holiday not in self.holidays:
            raise RuleTableError(f"모르는 공휴일 키: {holiday!r}")

        ruleset = self.ruleset_on(day)
        if ruleset is None:
            # 제도 도입 전. 규칙 부재는 대체공휴일 없음이다.
            return Eligibility(holiday, False, False, None, ())

        matched = ruleset.clauses_for(holiday)
        return Eligibility(
            holiday=holiday,
            saturday=any(SATURDAY in c.overlaps for c in matched),
            sunday=any(SUNDAY in c.overlaps for c in matched),
            ruleset=ruleset.id,
            clauses=tuple(c.id for c in matched),
        )

    # -- 감사 -------------------------------------------------------------

    def unverified(self) -> list:
        """법제처 원문 대조가 남은 항목. (종류, id) 목록."""
        out = []
        for rs in self.rulesets:
            if not rs.verified:
                out.append(("ruleset", rs.id))
            for c in rs.clauses:
                if not c.verified:
                    out.append(("clause", f"{rs.id} / {c.id}"))
        for p in self.placement_rules:
            if not p.get("verified"):
                out.append(("placement", p["id"]))
        return out


def _clause(raw: dict) -> Clause:
    return Clause(
        id=raw["id"],
        overlaps=tuple(raw["overlaps"]),
        applies_to=frozenset(raw["applies_to"]),
        verified=bool(raw.get("verified")),
        source_todo=raw.get("source_todo") or "",
    )


def _ruleset(raw: dict) -> Ruleset:
    return Ruleset(
        id=raw["id"],
        effective_from=raw["effective_from"],
        summary=raw.get("summary") or "",
        clauses=tuple(_clause(c) for c in raw["clauses"]),
        source=raw.get("source") or "",
        verified=bool(raw.get("verified")),
        source_todo=raw.get("source_todo") or "",
    )


def _coverage(raw: dict, path) -> Coverage:
    block = raw.get("coverage")
    if not block:
        raise RuleTableError(f"{path}: coverage 선언이 없다. 신뢰 구간을 밝히지 않은 표는 쓸 수 없다.")
    start, confirmed = block.get("from"), block.get("confirmed_through")
    if not isinstance(start, date) or not isinstance(confirmed, date):
        raise RuleTableError(
            f"{path}: coverage.from / coverage.confirmed_through 가 날짜가 아니다."
        )
    if start > confirmed:
        raise RuleTableError(f"{path}: coverage 구간이 뒤집혀 있다({start} > {confirmed}).")
    return Coverage(start=start, confirmed_through=confirmed)


def load(path=None) -> RuleTable:
    """규칙 테이블을 읽고 검증한다. 구조가 깨져 있으면 RuleTableError."""
    path = Path(path) if path else DEFAULT_PATH
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    table = RuleTable(
        coverage=_coverage(raw, path),
        weekly_holidays=frozenset(raw["weekly_holidays"]),
        sunday_in_output=bool(raw["sunday_in_output"]),
        overlap_vocabulary=frozenset(raw["overlap_vocabulary"]),
        placement_rules=tuple(raw["placement_rules"]),
        holidays=dict(raw["holidays"]),
        rulesets=tuple(_ruleset(r) for r in raw["rulesets"]),
        open_questions=tuple(raw.get("open_questions") or ()),
    )
    _validate(table)
    return table


def _validate(table: RuleTable) -> None:
    if SATURDAY in table.weekly_holidays:
        raise RuleTableError(
            "토요일이 weekly_holidays 에 들어 있다. 토요일은 공휴일이 아니다. "
            "이대로 두면 설·추석이 토요일과 겹칠 때 대체공휴일이 잘못 생긴다."
        )

    # 타입 검사가 정렬보다 먼저다. 연도(int)가 섞여 있으면 sorted() 가 먼저 터져서
    # 정작 원인인 "날짜가 아니다"라는 메시지를 못 보게 된다.
    for rs in table.rulesets:
        if not isinstance(rs.effective_from, date):
            raise RuleTableError(
                f"{rs.id}: effective_from 이 날짜가 아니다({rs.effective_from!r}). "
                "연 단위로 두면 2021-08-04 같은 연중 개정을 표현할 수 없다."
            )

    froms = [rs.effective_from for rs in table.rulesets]
    if froms != sorted(froms):
        raise RuleTableError("rulesets 가 effective_from 오름차순이 아니다.")
    if len(set(froms)) != len(froms):
        raise RuleTableError("effective_from 이 겹치는 ruleset 이 있다.")

    for rs in table.rulesets:
        for c in rs.clauses:
            unknown = set(c.overlaps) - table.overlap_vocabulary
            if unknown:
                raise RuleTableError(f"{rs.id} / {c.id}: 모르는 겹침 조건 {sorted(unknown)}")
            missing = c.applies_to - set(table.holidays)
            if missing:
                raise RuleTableError(
                    f"{rs.id} / {c.id}: holidays 레지스트리에 없는 키 {sorted(missing)}"
                )
