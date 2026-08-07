"""tests/fixtures/kr.yaml 의 정답을 구현에 대조한다.

케이스를 추가할 때 이 파일을 고칠 일은 없어야 한다. YAML 에만 추가한다.

구현 대상 인터페이스 (잠정 — 구현 착수 시 확정할 것):

    rules.kr.holiday_calendar.holidays_on(date) -> Sequence
        해당 날짜의 공휴일 목록. 공휴일이 아니면 빈 시퀀스.
        각 항목은 name / kind 를 가진다. dict 든 dataclass 든 상관없다.

    rules.kr.holiday_calendar.substitute_eligibility(holiday, year) -> Mapping
        {"saturday": bool, "sunday": bool}
        해당 연도 기준으로 그 공휴일이 토/일과 겹칠 때 대체공휴일 대상인지.

구현이 없으면 관련 테스트는 skip 된다. 스키마 검증 테스트는 구현과 무관하게 돈다.
"""

from __future__ import annotations

import pytest

from tests.fixture_loader import ALL_CASES, DAYS, SUBSTITUTE_RULES, ids as _ids, params

try:
    from rules.kr import holiday_calendar as impl
except ImportError:  # 아직 구현 없음
    impl = None


def _require(func_name):
    """구현이 아직 없으면 skip. 부분 구현 상태에서도 있는 것만 돌게 한다."""
    if impl is None:
        pytest.skip("rules.kr.holiday_calendar 미구현")
    func = getattr(impl, func_name, None)
    if func is None:
        pytest.skip(f"rules.kr.holiday_calendar.{func_name}() 미구현")
    return func


def _field(item, key):
    """구현이 dict 를 주든 객체를 주든 받아준다."""
    if hasattr(item, "get"):
        return item.get(key)
    return getattr(item, key, None)


def _explain(case, actual):
    """실패 메시지에 '왜 이 답인지'를 그대로 붙인다. 정답 근거를 찾아 헤매지 않도록."""
    lines = [
        "",
        f"case      : {case['id']}",
        f"expected  : {case['expect']}",
        f"actual    : {actual}",
        "",
        "why:",
        *[f"  {line}" for line in case["why"].rstrip().splitlines()],
    ]
    if case.get("source"):
        lines += ["", f"source: {case['source']}"]
    if case.get("source_todo"):
        lines += ["", f"source TODO(근거 미확인): {case['source_todo']}"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 스키마 검증 — 구현과 무관하게 항상 돈다.
# YAML 에 케이스를 잘못 넣었을 때 조용히 통과하지 않도록 막는 안전망.
# ---------------------------------------------------------------------------


def test_case_ids_are_unique():
    ids = _ids(ALL_CASES)
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplicates, f"중복된 case id: {duplicates}"


@pytest.mark.parametrize("case", ALL_CASES, ids=_ids(ALL_CASES))
def test_case_has_a_why(case):
    """왜 이 답인지 없는 케이스는 나중에 아무도 검증할 수 없다."""
    why = (case.get("why") or "").strip()
    assert why, f"{case['id']}: why 가 비어 있다"


@pytest.mark.parametrize("case", ALL_CASES, ids=_ids(ALL_CASES))
def test_case_declares_verification_status(case):
    """verified 가 빠지면 fixture_loader 가 미검증으로 간주해 조용히 xfail 을 붙인다.

    빠뜨린 것인지 일부러 false 인지 구분되지 않으므로 명시를 강제한다.
    """
    assert isinstance(case.get("verified"), bool), (
        f"{case['id']}: verified 가 없거나 불리언이 아니다"
    )


@pytest.mark.parametrize("case", DAYS, ids=_ids(DAYS))
def test_day_case_shape(case):
    expect = case["expect"]
    assert isinstance(expect["is_holiday"], bool)
    assert isinstance(expect["names"], list)
    assert isinstance(expect["kinds"], list)
    assert len(expect["names"]) == len(expect["kinds"]), (
        f"{case['id']}: names 와 kinds 개수가 다르다"
    )
    if expect["is_holiday"]:
        assert expect["names"], f"{case['id']}: 공휴일인데 names 가 비었다"
    else:
        assert not expect["names"], f"{case['id']}: 공휴일이 아닌데 names 가 있다"


@pytest.mark.xfail(
    reason="근거(관보/고시) 미확인 항목이 남아 있다. 전부 채우면 xpass 로 바뀐다.",
)
def test_every_case_has_a_source():
    """근거 없는 정답은 나중에 검증할 수 없다. 추측으로 채우지 말고 확인해서 채울 것."""
    missing = [
        case["id"]
        for case in ALL_CASES
        if not (case.get("source") or "").strip() or (case.get("source_todo") or "").strip()
    ]
    assert not missing, "근거 미확인 케이스:\n" + "\n".join(f"  - {i}" for i in missing)


# ---------------------------------------------------------------------------
# 정답 대조 — 구현이 생기면 돈다.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", params(DAYS))
def test_holidays_on_date(case):
    holidays_on = _require("holidays_on")

    actual = list(holidays_on(case["date"]))
    expect = case["expect"]

    assert bool(actual) == expect["is_holiday"], _explain(case, actual)
    assert [_field(h, "name") for h in actual] == expect["names"], _explain(case, actual)
    assert [_field(h, "kind") for h in actual] == expect["kinds"], _explain(case, actual)


@pytest.mark.parametrize("case", params(SUBSTITUTE_RULES))
def test_substitute_eligibility(case):
    substitute_eligibility = _require("substitute_eligibility")

    actual = substitute_eligibility(case["holiday"], case["year"])
    expect = case["expect"]

    assert _field(actual, "saturday") == expect["applies_to_saturday"], _explain(case, actual)
    assert _field(actual, "sunday") == expect["applies_to_sunday"], _explain(case, actual)
