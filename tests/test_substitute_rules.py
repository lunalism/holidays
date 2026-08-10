"""rules/kr/substitute_holidays.yaml 을 실제로 로드해서 유도가 맞는지 확인한다.

여기서 도는 것은 결과 주장이 아니라 유도 그 자체다.
tests/fixtures/kr.yaml 의 substitute_rules 는 정답, 규칙 테이블은 입력이고,
이 파일이 입력 → 정답 대조를 돌린다. 둘이 어긋나면 여기서 잡힌다.

주의: tests/test_kr_fixtures.py 의 test_substitute_eligibility 와 대상이 다르다.
그쪽은 아직 없는 최종 달력 구현(rules.kr.holiday_calendar)을 검증하고,
이쪽은 규칙 테이블과 그 로더를 검증한다. 둘 다 같은 정답을 본다.
"""

from __future__ import annotations

import os
from datetime import date

import pytest

from rules.kr import substitute_rules as sr
from tests.fixture_loader import SUBSTITUTE_RULES as FIXTURE_RULES
from tests.fixture_loader import params

# tests/test_rule_table_mutations.py 가 변이시킨 표를 물려 이 파일을 다시 돌린다.
# 이음매를 테스트 쪽에만 두어 rules/ 는 테스트를 의식하지 않게 한다.
TABLE = sr.load(os.environ.get("KR_RULE_TABLE") or None)

# 정답 픽스처는 사람이 읽는 이름, 규칙 테이블은 키를 쓴다. 이름 → 키 대응.
# 정답 쪽 표기를 규칙 테이블에 맞추면 두 파일이 서로 오염되므로 여기서만 잇는다.
NAME_TO_KEY = {meta["name"]: key for key, meta in TABLE.holidays.items()}
for _key, _meta in TABLE.holidays.items():
    for _alias in _meta.get("aliases") or ():
        NAME_TO_KEY[_alias] = _key

# 제2조 배열을 두 시점 모두 확보해서 coverage 전 구간이 유도 가능하다.
# 규칙 자체를 보는 테스트는 현행 구간을 기준으로 쓴다.
RESOLVED_DAY = date(2026, 6, 1)


def _eligibility_or_skip(case, key):
    try:
        return TABLE.eligibility_for_date(key, case["date"])
    except sr.MappingUnresolved as exc:
        pytest.skip(f"{case['id']}: {exc}")


# ---------------------------------------------------------------------------
# 테이블 구조
# ---------------------------------------------------------------------------


def test_table_loads_and_validates():
    """load() 안에서 구조 검증이 돈다. 여기까지 왔다면 통과한 것이다."""
    assert TABLE.rulesets, "ruleset 이 하나도 없다"
    assert TABLE.holidays


def test_saturday_is_not_a_holiday():
    """유도 전체가 이 전제 위에 서 있다."""
    assert sr.SATURDAY not in TABLE.weekly_holidays
    assert sr.SUNDAY in TABLE.weekly_holidays


def test_sunday_is_not_emitted_to_the_feed():
    """규칙 판정에서 일요일을 공휴일로 다루는 것과 피드에 내보내는 것은 별개다."""
    assert TABLE.sunday_in_output is False


def test_effective_from_is_a_date_not_a_year():
    """연 단위로는 2021-08-04 같은 연중 개정을 표현할 수 없다."""
    for rs in TABLE.rulesets:
        assert isinstance(rs.effective_from, date), rs.id


# ---------------------------------------------------------------------------
# 유도 — 정답 픽스처와 대조
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", params(FIXTURE_RULES))
def test_derivation_matches_fixture(case):
    """규칙 테이블에서 유도한 값이 정답 픽스처와 일치하는가."""
    key = NAME_TO_KEY[case["holiday"]]
    got = _eligibility_or_skip(case, key)
    expect = case["expect"]

    detail = (
        f"\ncase   : {case['id']}"
        f"\nholiday: {case['holiday']} ({key}) @ {case['date']}"
        f"\nruleset: {got.ruleset}"
        f"\nclauses: {got.clauses or '(해당 호 없음)'}"
        f"\nwhy    :\n" + "\n".join(f"  {ln}" for ln in case["why"].rstrip().splitlines())
    )

    assert got.saturday == expect["applies_to_saturday"], detail
    assert got.sunday == expect["applies_to_sunday"], detail


@pytest.mark.parametrize("case", params(FIXTURE_RULES))
def test_derivation_is_backed_by_a_clause(case):
    """대상이라고 답했으면 근거가 된 호가 있어야 한다.

    결과만 맞고 근거가 비어 있으면 유도가 아니라 우연이다.
    반대로 대상이 아니라고 답했는데 그 해에 규칙이 아예 없었다면 근거도 없어야 한다.
    """
    key = NAME_TO_KEY[case["holiday"]]
    got = _eligibility_or_skip(case, key)

    if got.saturday or got.sunday:
        assert got.clauses, f"{case['id']}: 대상이라면서 근거 조문이 없다"
        assert got.ruleset, f"{case['id']}: 대상이라면서 근거 ruleset 이 없다"


def test_asymmetry_comes_from_clause_membership():
    """설·추석과 국경일류의 비대칭이 소속 호의 차이에서 나오는지 확인한다.

    이 테스트가 보는 것은 결과가 아니라 경로다. 둘이 같은 호에 속하면서
    결과만 다르게 나온다면 어딘가에 예외가 하드코딩된 것이다.
    """
    day = RESOLVED_DAY  # 2026-05-11 이후는 매핑 미확인이라 유도 자체가 안 된다
    chuseok = TABLE.eligibility_for_date("chuseok", day)
    gwangbokjeol = TABLE.eligibility_for_date("gwangbokjeol", day)

    assert chuseok.clauses != gwangbokjeol.clauses, (
        "두 공휴일이 같은 호에 속하는데 결과가 다르다면 예외가 하드코딩된 것이다"
    )
    assert (chuseok.saturday, chuseok.sunday) == (False, True)
    assert (gwangbokjeol.saturday, gwangbokjeol.sunday) == (True, True)


def test_clause_3_covers_the_childrens_day_overlap():
    """제1항제3호가 어린이날·부처님오신날 겹침을 담당할 수 있는 상태인지 확인한다.

    3호는 토·일 판정에 기여하지 않아 eligibility 의 saturday/sunday 로는 존재가
    드러나지 않는다. 이 테스트가 없으면 3호를 통째로 지워도 아무도 모른다.

    실제 사례는 2025-05-05 이다. 그 시점 배열에서 부처님오신날은 제6호,
    어린이날은 제7호이며 둘 다 3호에 들어 있다.

    주의: 트리거가 어린이날인지 부처님오신날인지는 확정하지 않는다.
    open_questions 의 3호-귀속-불명 참조. 여기서 보는 것은 소속뿐이다.
    """
    day = date(2025, 5, 5)
    ruleset = TABLE.ruleset_on(day)
    assert ruleset is not None

    for holiday in ("childrens_day", "buddhas_birthday"):
        clauses = ruleset.clauses_for(holiday)
        weekday_overlap = [c for c in clauses if "other_holiday_on_weekday" in c.overlaps]
        assert weekday_overlap, (
            f"{holiday} 가 공휴일간 겹침(3호) 경로를 갖고 있지 않다. "
            f"2025-05-06 대체공휴일이 유도될 수 없다. ruleset={ruleset.id}"
        )


def test_clause_3_covers_the_2017_chuseok_overlap():
    """2017년 추석×개천절 겹침. 3호 경로가 2013년 규칙에도 있어야 한다.

    이 해에는 국경일이 아직 대체공휴일 대상이 아니므로 개천절은 트리거가 될 수 없고,
    추석 연휴 쪽에만 겹침 경로가 있어야 한다. 소급 금지와 3호가 함께 걸리는 지점이다.
    """
    day = date(2017, 10, 3)
    ruleset = TABLE.ruleset_on(day)
    assert ruleset is not None

    chuseok = ruleset.clauses_for("chuseok")
    assert [c for c in chuseok if "other_holiday_on_weekday" in c.overlaps], (
        f"추석 연휴에 공휴일간 겹침 경로가 없다. ruleset={ruleset.id}"
    )
    assert not ruleset.clauses_for("gaecheonjeol"), (
        "2017년에 개천절이 대체공휴일 대상으로 잡혔다. 국경일은 2021년부터다."
    )


def test_rules_are_not_applied_retroactively():
    """국경일 규칙 시행 전날과 당일의 답이 갈리는지 확인한다.

    2021-08-04 개정은 연중 시행이라 같은 해 안에서 답이 바뀐다.
    연 단위 effective_from 이었다면 이 차이를 표현할 수 없다.
    """
    before = TABLE.eligibility_for_date("gwangbokjeol", date(2021, 8, 3))
    after = TABLE.eligibility_for_date("gwangbokjeol", date(2021, 8, 4))

    assert (before.saturday, before.sunday) == (False, False)
    assert (after.saturday, after.sunday) == (True, True)
    assert not before.clauses
    assert after.clauses


def test_same_year_can_hold_two_answers():
    """2021년 3·1절과 광복절은 같은 해인데 답이 다르다.

    조회 단위가 날짜여야 하는 이유. 연 단위 API 가 있었다면 둘 중 하나는
    반드시 틀린 답을 받았을 것이다.
    """
    samiljeol = TABLE.eligibility_for_date("samiljeol", date(2021, 3, 1))
    gwangbokjeol = TABLE.eligibility_for_date("gwangbokjeol", date(2021, 8, 15))

    assert (samiljeol.saturday, samiljeol.sunday) == (False, False)
    assert (gwangbokjeol.saturday, gwangbokjeol.sunday) == (True, True)


def test_constitution_day_enforcement_boundary():
    """제3조 개정 시행일 2026-05-01 전후로 표의 상태가 갈린다.

    이전: 제33448호. 그 시점 제2조제2호는 3·1절·광복절·개천절·한글날만 열거하고
          제헌절이 없다 → 대상 아님.
    이후: 제36290호. 제2조제2호가 「국경일에 관한 법률」 참조로 바뀌어 제헌절이
          별도 열거 없이 들어온다 → 토·일 모두 대상.

    제헌절이 공휴일이 되는 것은 2026-05-11 부터다(제2조제2호 시행일).
    규칙 적용 시점과 공휴일 편입 시점이 다르다는 것이 이 개정령의 특징이다.
    """
    before = TABLE.eligibility_for_date("constitution_day", date(2026, 4, 30))
    assert (before.saturday, before.sunday) == (False, False)
    assert not before.clauses  # 그 시점 제2호는 국경일 4개만 열거한다

    after = TABLE.eligibility_for_date("constitution_day", date(2026, 5, 1))
    assert (after.saturday, after.sunday) == (True, True)
    assert after.clauses == ("제3조제1항제1호", "제3조제1항제3호")


def test_article2_items_resolve_through_the_article2_table():
    """호 번호는 조문 그대로 두고, 공휴일 키는 article2 표를 거쳐 나온다.

    호 번호를 공휴일 이름으로 미리 풀어 적으면 개정 때 무엇이 바뀌었는지 알 수 없다.
    두 단계로 나눈 것이 노동절 삽입에 따른 재번호를 드러낸 이유이기도 하다.
    """
    ruleset = TABLE.ruleset_on(date(2026, 5, 1))
    assert ruleset.id == "제36290호"
    assert ruleset.resolved

    by_id = {c.id: c for c in ruleset.clauses}
    assert by_id["제3조제1항제1호"].article2_items == (2, 5, 6, 7, 10)
    assert by_id["제3조제1항제2호"].article2_items == (4, 9)
    assert by_id["제3조제1항제3호"].article2_items == (2, 4, 5, 6, 7, 9, 10)

    # 제2호가 국경일 전체다. 다섯 공휴일이 한 호에 들어 있다.
    assert by_id["제3조제1항제1호"].applies_to >= {
        "samiljeol", "constitution_day", "gwangbokjeol", "gaecheonjeol", "hangeul_day",
    }
    # 제2호에 노동절은 없다. 제6호로 따로 들어온다.
    assert "labor_day" in by_id["제3조제1항제1호"].applies_to

    # 제4호·제9호가 설·추석이고, 토요일이 없는 것이 비대칭의 전부다.
    assert by_id["제3조제1항제2호"].applies_to == {"seollal", "chuseok"}


def test_every_ruleset_resolves():
    """제2조 배열을 두 시점 모두 확보해서 전 구간이 풀린다."""
    for rs in TABLE.rulesets:
        assert rs.resolved, f"{rs.id} 가 아직 미해결이다"


def test_article2_arrangement_is_chosen_by_period():
    """같은 호 번호가 시점에 따라 다른 공휴일을 가리킨다.

    제5호가 그렇다. 2021-2026 배열에서는 공석이고 현행 배열에서는 노동절이다.
    배열을 시점으로 고르지 않으면 노동절이 2021년부터 있었던 것이 된다.
    """
    old = TABLE.ruleset_on(date(2023, 5, 4))
    new = TABLE.ruleset_on(date(2026, 5, 1))

    old_first = {c.id: c for c in old.clauses}["제3조제1항제1호"]
    new_first = {c.id: c for c in new.clauses}["제3조제1항제1호"]

    assert "labor_day" not in old_first.applies_to
    assert "labor_day" in new_first.applies_to

    # 제6호 이하는 번호가 그대로다. 재번호가 아니라 빈 5호를 채운 것이기 때문이다.
    assert "buddhas_birthday" in old_first.applies_to  # 제6호
    assert "buddhas_birthday" in new_first.applies_to  # 제6호 (그대로)


def test_before_the_scheme_existed():
    """제도 도입 전에는 규칙 부재이며, 그것이 곧 대체공휴일 없음이다."""
    got = TABLE.eligibility_for_date("childrens_day", date(2013, 1, 1))
    assert (got.saturday, got.sunday) == (False, False)
    assert got.ruleset is None


def test_unknown_holiday_key_is_rejected():
    with pytest.raises(sr.RuleTableError):
        TABLE.eligibility_for_date("no_such_holiday", date(2026, 1, 1))


# ---------------------------------------------------------------------------
# 감사 — 법제처 원문 대조 진행 상황
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason="법제처 원문 대조 전. 전부 verified: true 가 되면 xpass 로 바뀐다.",
    strict=True,
)
def test_every_rule_is_verified_against_the_source_text():
    pending = TABLE.unverified()
    assert not pending, "원문 대조 미완:\n" + "\n".join(f"  - {k}: {i}" for k, i in pending)
