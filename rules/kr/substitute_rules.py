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


class MappingUnresolved(RuleTableError):
    """조문의 호 번호를 공휴일로 옮기는 매핑이 아직 확인되지 않았다.

    원문은 적용 대상을 제2조의 호 번호로 규정한다. 그 배열을 모르면 어느 공휴일이
    대상인지 알 수 없다. 이때 "대상 아님"으로 답하면 없는 확신을 만들어내는 것이다.
    모른다는 사실을 예외로 드러낸다. LunarNotImplemented 와 같은 성격이다.
    """


@dataclass(frozen=True)
class Clause:
    """조문의 한 호."""

    id: str
    overlaps: tuple
    applies_to: frozenset  # None 이면 호 번호 ↔ 공휴일 매핑 미확인
    article2_items: tuple
    verified: bool
    source_todo: str
    unresolved_reason: str = ""

    @property
    def resolved(self) -> bool:
        return self.applies_to is not None

    def covers(self, holiday: str) -> bool:
        if self.applies_to is None:
            raise MappingUnresolved(f"{self.id}: {self.unresolved_reason.strip()}")
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
    provisions: tuple = ()   # 조항별 시행일이 갈릴 때만 채운다

    @property
    def resolved(self) -> bool:
        """모든 호의 적용 대상을 공휴일로 옮길 수 있는가."""
        return all(c.resolved for c in self.clauses)

    def clauses_for(self, holiday: str) -> tuple:
        if not self.resolved:
            unresolved = [c.id for c in self.clauses if not c.resolved]
            raise MappingUnresolved(
                f"{self.id}: {', '.join(unresolved)} 의 적용 대상이 미확인이라 "
                f"{holiday} 의 대체공휴일 대상 여부를 유도할 수 없다."
            )
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
    article2: dict        # 제2조 각 호의 배열 (현행)
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
            # 매핑 미확인과 다르다. 이쪽은 "없다"를 아는 것이다.
            return Eligibility(holiday, False, False, None, ())

        matched = ruleset.clauses_for(holiday)  # 매핑 미확인이면 MappingUnresolved
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


def _arrangement_on(article2, day: date):
    """그 시점에 유효했던 제2조 배열.

    배열은 개정마다 바뀐다. ruleset 의 시행일이 속한 배열로만 호 번호를 풀어야
    한다. 다른 시점 배열을 갖다 쓰면 같은 호 번호가 다른 공휴일을 가리킬 수 있다.
    """
    if not article2:
        return None
    for a in article2.get("arrangements") or ():
        start, end = a["effective_from"], a.get("effective_until")
        if start <= day and (end is None or day <= end):
            return a
    return None


def _clause(raw: dict, article2, ruleset_from: date) -> Clause:
    """조문의 한 호를 읽는다. 적용 대상을 푸는 경로는 셋이다.

    1) applies_to 가 직접 적혀 있으면 그대로 쓴다.
    2) article2_items 가 있고 그 ruleset 이 현행 호 번호 체계 안에 있으면
       article2 표를 거쳐 공휴일 키로 푼다.
    3) 둘 다 아니면 미해결. 이유를 반드시 적어야 한다.

    2번에서 번호 체계를 확인하는 것이 핵심이다. 제36290호가 노동절을 제6호로
    끼워 넣으면서 뒤 번호가 밀렸다. 현행 배열을 그 이전 ruleset 에 갖다 쓰면
    조용히 다른 공휴일을 가리키게 된다.
    """
    applies_to = raw.get("applies_to")
    items = tuple(raw.get("article2_items") or ())
    reason = raw.get("unresolved_reason") or ""
    arrangement = _arrangement_on(article2, ruleset_from)

    if applies_to is not None:
        resolved = frozenset(applies_to)
    elif items and arrangement is not None:
        missing = [i for i in items if i not in arrangement["items"]]
        if missing:
            raise RuleTableError(
                f"{raw['id']}: {arrangement['id']} 에 없는 호 번호 {missing}"
            )
        resolved = frozenset(
            key for item in items for key in arrangement["items"][item]["holidays"]
        )
    elif items:
        resolved = None
        reason = reason or (
            f"제2조 호 번호 {list(items)} 로 규정되어 있으나 {ruleset_from} 시점의 "
            "제2조 배열이 article2.arrangements 에 없어 풀 수 없다."
        )
    else:
        resolved = None
        if not reason:
            raise RuleTableError(
                f"{raw['id']}: applies_to 도 article2_items 도 없는데 "
                "unresolved_reason 이 비어 있다. 왜 못 푸는지 적어야 한다."
            )

    return Clause(
        id=raw["id"],
        overlaps=tuple(raw["overlaps"]),
        applies_to=resolved,
        article2_items=items,
        verified=bool(raw.get("verified")),
        source_todo=raw.get("source_todo") or "",
        unresolved_reason=reason,
    )


def _ruleset(raw: dict, article2) -> Ruleset:
    effective_from = raw["effective_from"]
    # 타입 검사가 먼저다. 연도(int)가 섞이면 아래 배열 조회에서 date 와 비교하다가
    # TypeError 로 터져서, 정작 원인인 "날짜가 아니다"라는 메시지를 못 보게 된다.
    if not isinstance(effective_from, date):
        raise RuleTableError(
            f"{raw['id']}: effective_from 이 날짜가 아니다({effective_from!r}). "
            "연 단위로 두면 2021-08-04 같은 연중 개정을 표현할 수 없다."
        )
    provisions = tuple(raw.get("provisions") or ())
    if provisions:
        # 한 개정령 안에서 조항별 시행일이 갈릴 수 있다. ruleset 의 effective_from 은
        # 그중 가장 이른 것이어야 한다. 어긋나면 어느 쪽이 맞는지 알 수 없다.
        earliest = min(p["effective_from"] for p in provisions)
        if effective_from != earliest:
            raise RuleTableError(
                f"{raw['id']}: effective_from({effective_from}) 이 provisions 의 "
                f"가장 이른 시행일({earliest}) 과 다르다."
            )
    return Ruleset(
        id=raw["id"],
        effective_from=effective_from,
        summary=raw.get("summary") or "",
        clauses=tuple(_clause(c, article2, effective_from) for c in raw["clauses"]),
        source=raw.get("source") or "",
        verified=bool(raw.get("verified")),
        source_todo=raw.get("source_todo") or "",
        provisions=provisions,
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
    article2 = raw.get("article2")

    table = RuleTable(
        coverage=_coverage(raw, path),
        weekly_holidays=frozenset(raw["weekly_holidays"]),
        sunday_in_output=bool(raw["sunday_in_output"]),
        overlap_vocabulary=frozenset(raw["overlap_vocabulary"]),
        placement_rules=tuple(raw["placement_rules"]),
        holidays=dict(raw["holidays"]),
        article2=article2,
        rulesets=tuple(_ruleset(r, article2) for r in raw["rulesets"]),
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
            if not c.resolved:
                continue  # 호 번호만 있는 호. 검증할 키가 없다.
            missing = c.applies_to - set(table.holidays)
            if missing:
                raise RuleTableError(
                    f"{rs.id} / {c.id}: holidays 레지스트리에 없는 키 {sorted(missing)}"
                )
