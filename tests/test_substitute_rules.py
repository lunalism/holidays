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
from pathlib import Path

import pytest
import yaml

from rules.kr import substitute_rules as sr

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "kr.yaml"

# tests/test_rule_table_mutations.py 가 변이시킨 표를 물려 이 파일을 다시 돌린다.
# 이음매를 테스트 쪽에만 두어 rules/ 는 테스트를 의식하지 않게 한다.
TABLE = sr.load(os.environ.get("KR_RULE_TABLE") or None)
FIXTURE = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))
FIXTURE_RULES = FIXTURE["substitute_rules"]

# 정답 픽스처는 사람이 읽는 이름, 규칙 테이블은 키를 쓴다. 이름 → 키 대응.
# 정답 쪽 표기를 규칙 테이블에 맞추면 두 파일이 서로 오염되므로 여기서만 잇는다.
NAME_TO_KEY = {meta["name"]: key for key, meta in TABLE.holidays.items()}
NAME_TO_KEY.update({"설날": "seollal", "추석": "chuseok"})


def _ids(cases):
    return [c["id"] for c in cases]


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


@pytest.mark.parametrize("case", FIXTURE_RULES, ids=_ids(FIXTURE_RULES))
def test_derivation_matches_fixture(case):
    """규칙 테이블에서 유도한 값이 정답 픽스처와 일치하는가."""
    key = NAME_TO_KEY[case["holiday"]]
    got = TABLE.eligibility_for_date(key, case["date"])
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


@pytest.mark.parametrize("case", FIXTURE_RULES, ids=_ids(FIXTURE_RULES))
def test_derivation_is_backed_by_a_clause(case):
    """대상이라고 답했으면 근거가 된 호가 있어야 한다.

    결과만 맞고 근거가 비어 있으면 유도가 아니라 우연이다.
    반대로 대상이 아니라고 답했는데 그 해에 규칙이 아예 없었다면 근거도 없어야 한다.
    """
    key = NAME_TO_KEY[case["holiday"]]
    got = TABLE.eligibility_for_date(key, case["date"])

    if got.saturday or got.sunday:
        assert got.clauses, f"{case['id']}: 대상이라면서 근거 조문이 없다"
        assert got.ruleset, f"{case['id']}: 대상이라면서 근거 ruleset 이 없다"


def test_asymmetry_comes_from_clause_membership():
    """설·추석과 국경일류의 비대칭이 소속 호의 차이에서 나오는지 확인한다.

    이 테스트가 보는 것은 결과가 아니라 경로다. 둘이 같은 호에 속하면서
    결과만 다르게 나온다면 어딘가에 예외가 하드코딩된 것이다.
    """
    day = date(2026, 9, 25)
    chuseok = TABLE.eligibility_for_date("chuseok", day)
    gwangbokjeol = TABLE.eligibility_for_date("gwangbokjeol", day)

    assert chuseok.clauses != gwangbokjeol.clauses, (
        "두 공휴일이 같은 호에 속하는데 결과가 다르다면 예외가 하드코딩된 것이다"
    )
    assert (chuseok.saturday, chuseok.sunday) == (False, True)
    assert (gwangbokjeol.saturday, gwangbokjeol.sunday) == (True, True)


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
    """제헌절은 2026-05-11 시행. 그 전후로 답이 갈린다.

    주의: 시행 후 값(토·일 모두 대상)은 역산 가정이며 미확정이다.
    open_questions 의 제헌절-대체공휴일-적용시점 참조.
    """
    before = TABLE.eligibility_for_date("constitution_day", date(2026, 5, 10))
    after = TABLE.eligibility_for_date("constitution_day", date(2026, 5, 11))

    assert (before.saturday, before.sunday) == (False, False)
    assert not before.clauses
    assert after.clauses


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
)
def test_every_rule_is_verified_against_the_source_text():
    pending = TABLE.unverified()
    assert not pending, "원문 대조 미완:\n" + "\n".join(f"  - {k}: {i}" for k, i in pending)
