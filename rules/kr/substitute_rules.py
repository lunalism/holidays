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
class RuleTable:
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


def load(path=None) -> RuleTable:
    """규칙 테이블을 읽고 검증한다. 구조가 깨져 있으면 RuleTableError."""
    path = Path(path) if path else DEFAULT_PATH
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    table = RuleTable(
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
