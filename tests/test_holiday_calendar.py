"""holiday_calendar 구현 자체를 본다. 정답 픽스처가 담지 못하는 성질들.

픽스처는 "이 날짜의 답이 무엇인가"를 본다. 여기서는 그 답이 나오는 경로가
맞는지를 본다. 특히 kind 가 대체공휴일 적용 여부를 가르는 지점과,
일요일이 판정에는 쓰이되 출력에는 안 나오는 지점이다.

일부 테스트는 비공개 함수(_eligible_overlaps, _place)를 직접 부른다.
그 게이트를 실제 데이터로 자극할 날짜가 아직 없기 때문이다. 임시공휴일이
일요일에 지정된 적이 없고, 대체공휴일이 토요일에 놓이는 사례는 음력이 있어야
나온다. 데이터를 지어내는 대신 게이트를 직접 부른다.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import date, timedelta

import pytest

from rules.kr import holiday_calendar as hc
from rules.kr import substitute_rules
from tests import fixture_loader


def _names(day):
    return [h.name for h in hc.holidays_on(day)]


def _kinds(day):
    return [h.kind for h in hc.holidays_on(day)]


# ---------------------------------------------------------------------------
# kind 가 대체공휴일 적용 여부를 결정한다
# ---------------------------------------------------------------------------


def test_temporary_holiday_is_not_substitute_eligible():
    """임시공휴일은 대체공휴일 대상이 아니다.

    실제 데이터에는 일요일에 지정된 임시공휴일이 없어 달력만으로는 이 게이트가
    자극되지 않는다. 게이트를 직접 부른다. 지금은 어느 날짜를 줘도 빈 집합이어야 한다.
    """
    temporary = hc.Holiday(name="임시공휴일", kind="temporary")
    for day in (date(2020, 8, 16), date(2020, 8, 15), date(2020, 8, 17)):  # 일, 토, 월
        assert hc._eligible_overlaps(temporary, day) == set(), (
            f"{day}: 임시공휴일이 대체공휴일 대상으로 잡혔다. "
            "designated_holidays.yaml 의 kinds.temporary.substitute_eligible 확인."
        )


def test_election_day_eligibility_is_unresolved():
    """선거일은 대상인지 아닌지 확정되지 않았다.

    제2조제10의2호(가지번호)인데 제3조는 제10호까지만 열거한다. 가지번호가 그
    범위에 드는지는 법제처 해석이 필요하다. true 도 false 도 주장하지 않는다.
    None 이 "모른다"이고, set() 은 "대상 아님"이다. 둘을 섞으면 안 된다.
    """
    election = hc.Holiday(name="제9회 전국동시지방선거", kind="election")
    assert hc._eligible_overlaps(election, date(2026, 6, 3)) is None

    temporary = hc.Holiday(name="임시공휴일", kind="temporary")
    assert hc._eligible_overlaps(temporary, date(2026, 6, 3)) == set()


def test_2020_08_17_does_not_generate_a_substitute():
    """2020-08-17 임시공휴일이 대체공휴일을 만들어내지 않는다.

    광복절(08-15, 토)도 이 해에는 대상이 아니므로 2020년 8월에는 대체공휴일이
    하나도 없어야 한다. 둘 중 어느 쪽이 잘못 발동해도 여기서 잡힌다.
    """
    assert _kinds(date(2020, 8, 17)) == ["temporary"]

    day = date(2020, 8, 1)
    while day.month == 8:
        assert "substitute" not in _kinds(day), (
            f"{day}: 2020년 8월에 대체공휴일이 생겼다. "
            "임시공휴일이나 국경일이 잘못 트리거되었다."
        )
        day = day.fromordinal(day.toordinal() + 1)


def test_election_day_is_a_holiday_but_makes_no_substitute():
    """선거일은 대상이지만 수요일이라 실제로는 대체공휴일이 생기지 않는다."""
    assert _names(date(2026, 6, 3)) == ["제9회 전국동시지방선거"]
    assert _kinds(date(2026, 6, 3)) == ["election"]
    for offset in range(1, 5):
        day = date(2026, 6, 3).fromordinal(date(2026, 6, 3).toordinal() + offset)
        assert "substitute" not in _kinds(day), f"{day}: 선거일이 대체공휴일을 만들었다"


# ---------------------------------------------------------------------------
# 일요일 — 판정에는 쓰되 출력에는 넣지 않는다
# ---------------------------------------------------------------------------


def test_plain_sunday_is_not_in_the_output():
    """아무 일 없는 일요일은 결과에 나오지 않는다 (sunday_in_output: false)."""
    plain = date(2021, 8, 22)
    assert plain.weekday() == 6
    assert hc.holidays_on(plain) == ()


def test_sunday_still_drives_the_substitute_rule():
    """2021-08-15 광복절이 일요일 → 08-16 이 대체공휴일.

    일요일을 출력에서 뺀다고 판정에서까지 빼면 이 대체공휴일이 사라진다.
    출력 정책과 판정 규칙이 분리되어 있는지 확인하는 자리다.
    """
    assert date(2021, 8, 15).weekday() == 6
    assert _names(date(2021, 8, 15)) == ["광복절"]  # 일요일은 이름으로 안 나온다
    assert _kinds(date(2021, 8, 16)) == ["substitute"]


def test_saturday_is_never_a_holiday():
    """토요일은 공휴일이 아니다. 광복절이 토요일이던 2015년으로 확인한다."""
    assert date(2015, 8, 15).weekday() == 5
    assert _kinds(date(2015, 8, 15)) == ["statutory"]  # 광복절 하나뿐
    assert _kinds(date(2015, 8, 17)) == []  # 대체공휴일 없음


# ---------------------------------------------------------------------------
# 배치 규칙
# ---------------------------------------------------------------------------


def test_placement_skips_saturday():
    """제3조제3항: 대체공휴일이 토요일에 놓이면 다음 비공휴일로 다시 옮긴다.

    실제 사례는 아직 픽스처에 없다(음력이 있어야 나온다). 여기서는 배치 함수를
    직접 불러 규칙이 동작하는지만 본다. 실제 사례 확보는 여전히 미해결이며
    substitute_holidays.yaml 의 픽스처구멍-배치규칙-미검증 에 남아 있다.
    """
    flags = hc._placement_flags()
    assert flags["requeue_saturday"], "제3조제3항이 표에서 사라졌다"

    # 일요일은 공휴일이므로 배치에서 건너뛴다. 실제 _calendar 가 넘기는 조건과 같게 둔다.
    sunday_is_holiday = lambda d: d.weekday() == 6  # noqa: E731

    friday = date(2021, 1, 1)
    assert friday.weekday() == 4
    placed = hc._place(friday, 1, sunday_is_holiday, flags)
    assert placed[0].weekday() != 5, "대체공휴일이 토요일에 놓였다"
    assert placed[0] == date(2021, 1, 4)  # 토(2일)·일(3일)을 건너뛴 월요일


def test_placement_extends_on_collision():
    """제3조제2항: 대체공휴일이 여러 개면 연속된 비공휴일로 늘어난다."""
    flags = hc._placement_flags()
    assert flags["extend_on_collision"], "제3조제2항이 표에서 사라졌다"

    sunday_is_holiday = lambda d: d.weekday() == 6  # noqa: E731

    placed = hc._place(date(2021, 1, 1), 2, sunday_is_holiday, flags)
    assert placed == [date(2021, 1, 4), date(2021, 1, 5)]


# ---------------------------------------------------------------------------
# coverage — 신뢰 구간 밖은 거부한다
# ---------------------------------------------------------------------------


def test_effective_coverage_is_the_intersection_of_sources():
    cov = hc.coverage()
    sources = cov["sources"]
    assert set(sources) == {
        "solar_holidays.yaml",
        "lunar_holidays.yaml",
        "designated_holidays.yaml",
        "substitute_holidays.yaml",
    }
    assert cov["effective"].start == max(c.start for c in sources.values())
    # 상한은 축별로 따로 좁힌다. 축을 선언하지 않은 소스는 그 축에 참여하지 않는다.
    for axis in ("confirmed_through", "last_synced_at"):
        declared = [
            getattr(c, axis) for c in sources.values() if getattr(c, axis) is not None
        ]
        assert declared, f"{axis} 를 선언한 소스가 하나도 없다"
        assert getattr(cov["effective"], axis) == min(declared)


def test_the_two_upper_bounds_are_not_collapsed_into_one():
    """규칙 확정과 지정 반영은 다른 보증이다. 한 값으로 뭉치면 안 된다.

    뭉쳐서 min 을 잡으면 규칙 개정을 2028 년까지 확인해 둔 사실이 지정 표의
    동기화 시점에 가려져 사라진다. 그러면 2027 년 대체공휴일이 "규칙 미확인"으로
    보고되는데, 실제로 미확인인 것은 그 해 임시공휴일이 더 생길지 여부다.
    두 축이 각자 살아 있어야 어느 쪽이 열려 있는지 구분된다.
    """
    eff = hc.coverage()["effective"]
    assert eff.confirmed_through is not None
    assert eff.last_synced_at is not None
    assert eff.last_synced_at < eff.confirmed_through

    between = eff.last_synced_at + timedelta(days=1)
    assert hc.is_provisional(between) is False  # 규칙은 확인되어 있다
    assert hc.may_grow(between) is True         # 지정은 더 생길 수 있다

    beyond = date(eff.confirmed_through.year + 1, 1, 1)
    assert hc.is_provisional(beyond) is True
    assert hc.may_grow(beyond) is True


def test_designated_table_declares_the_sync_axis_not_the_rule_axis():
    """지정 표에는 규칙이 없다. 규칙 개정을 확인했다고 주장할 수 없다.

    반대로 규칙을 담은 표는 반영 축을 주장하지 않는다. 소스와 맞출 목록이 없다.
    이 대응이 뒤집히면 표가 자기가 못 가진 것을 보증하게 된다.
    """
    sources = hc.coverage()["sources"]

    designated = sources["designated_holidays.yaml"]
    assert designated.last_synced_at == date(2026, 8, 8)
    assert designated.confirmed_through is None

    for name in ("solar_holidays.yaml", "substitute_holidays.yaml"):
        assert sources[name].confirmed_through is not None, name
        assert sources[name].last_synced_at is None, name


def test_a_table_may_not_declare_both_axes_or_neither():
    """축 선택은 스키마가 강제한다. 주석으로 부탁하지 않는다."""
    base = {"coverage": {"from": date(2015, 1, 1)}}

    for block in (
        {},  # 아무 축도 없음
        {"confirmed_through": date(2028, 12, 31), "last_synced_at": date(2026, 8, 8)},
    ):
        raw = {"coverage": {**base["coverage"], **block}}
        with pytest.raises(substitute_rules.RuleTableError) as exc:
            substitute_rules.read_coverage(raw, "테스트")
        assert "정확히 하나" in str(exc.value)

    ok = substitute_rules.read_coverage(
        {"coverage": {"from": date(2015, 1, 1), "last_synced_at": date(2026, 8, 8)}}, "테스트"
    )
    assert ok.last_synced_at == date(2026, 8, 8)
    assert ok.confirmed_through is None
    assert ok.is_provisional(date(2030, 1, 1)) is False  # 규칙 축을 주장하지 않았다
    assert ok.may_grow(date(2030, 1, 1)) is True


def test_narrowest_source_decides_the_range():
    """가장 좁은 소스가 전체를 결정한다.

    start 는 가장 늦은 것을, 각 상한은 가장 이른 것을 따른다.
    designated 가 2015 부터라 solar(2013)·rules(2013-11-05)보다 늦다.
    그래서 2014 년은 solar 가 답할 수 있어도 전체로는 답하지 않는다.
    """
    cov = hc.coverage()
    assert cov["sources"]["designated_holidays.yaml"].start == cov["effective"].start
    with pytest.raises(hc.UnsupportedYear):
        hc.holidays_on(date(2014, 8, 15))


def test_before_the_completeness_boundary_raises_instead_of_returning_empty():
    """빈 튜플을 돌려주면 '데이터 없음'과 '공휴일 아님'이 구분되지 않는다.

    2024-04-10 은 실제로 공휴일이었다. 이 표에 없던 시절 조용히 () 를 돌려주던 것이
    Codex 리뷰에서 지적된 P1 이다. 지금은 표에 있고, 하한 밖이면 예외가 난다.
    """
    assert _names(date(2024, 4, 10)) == ["제22대 국회의원선거"]

    for before in (date(2012, 12, 31), date(2014, 12, 31)):
        with pytest.raises(hc.UnsupportedYear):
            hc.holidays_on(before)


def test_unsupported_year_message_shows_the_range():
    """예외만 던지고 끝내면 호출자가 어디까지 되는지 모른다."""
    with pytest.raises(hc.UnsupportedYear) as exc:
        hc.holidays_on(date(2000, 1, 1))
    message = str(exc.value)
    assert "2015-01-01" in message
    assert "designated_holidays.yaml" in message


# ---------------------------------------------------------------------------
# provisional — 확정 시점 이후는 거부하지 않고 표시해서 돌려준다
# ---------------------------------------------------------------------------


def test_future_dates_are_answered_not_rejected():
    """상한을 거부로 두면 몇 년치 선발행이 막힌다.

    미래 연도에 임시공휴일이 없는 것은 누락이 아니라 아직 지정되지 않은 상태다.
    없는 것이 정상이므로 오류로 다루지 않는다.
    """
    # 확정 구간은 2028-12-31 까지다(KASI 데이터가 2028 년까지라 그 구간까지 대조했다).
    for far in (date(2029, 1, 1), date(2030, 8, 15), date(2035, 3, 1)):
        hc.holidays_on(far)  # 예외가 없어야 한다
        assert hc.is_provisional(far)

    assert _names(date(2030, 8, 15)) == ["광복절"]


def test_provisional_flag_is_attached_to_each_holiday():
    """피드 생성기가 항목 단위로 보고 표시하거나 잘라낼 수 있어야 한다."""
    confirmed = hc.coverage()["effective"].confirmed_through

    for h in hc.holidays_on(date(2026, 8, 15)):  # 확정 구간
        assert h.provisional is False
    for h in hc.holidays_on(date(2029, 8, 15)):  # 확정 이후
        assert h.provisional is True

    assert hc.is_provisional(confirmed) is False
    assert hc.is_provisional(date(confirmed.year + 1, 1, 1)) is True


def test_substitute_eligibility_reports_provisional():
    """확정 구간과 잠정 구간이 갈리는지."""
    assert hc.substitute_eligibility("광복절", date(2026, 8, 15))["provisional"] is False
    assert hc.substitute_eligibility("광복절", date(2030, 8, 15))["provisional"] is True


def test_provisional_substitutes_still_derive():
    """잠정 구간에서도 대체공휴일 계산은 그대로 돈다. 표시만 다르다.

    2034-08-15 는 화요일이 아니라 일요일이라 08-16 이 대체공휴일이 된다.
    확정 구간(2028-12-31) 이후를 골라야 provisional 이 붙는다.
    잠정이라고 계산을 멈추면 선발행할 피드가 비어 버린다.
    """
    sunday_gwangbokjeol = next(
        d for y in range(2029, 2045)
        for d in [date(y, 8, 15)]
        if d.weekday() == 6
    )
    substitutes = [
        h for h in hc.holidays_on(sunday_gwangbokjeol + timedelta(days=1))
        if h.kind == "substitute"
    ]
    assert substitutes, f"{sunday_gwangbokjeol}: 잠정 구간에서 대체공휴일이 계산되지 않았다"
    assert all(h.provisional for h in substitutes)


def test_constitution_day_first_substitute_is_2027():
    """제헌절 대체공휴일의 첫 발동. 제2조제2호가 국경일을 통째로 참조한 결과다.

    2026-07-17 은 금요일이라 발동하지 않고, 2027-07-17 은 토요일이라 07-19(월)로
    넘어간다. 07-18 은 일요일이므로 건너뛴다.
    """
    assert hc.holidays_on(date(2026, 7, 17))[0].name == "제헌절"
    assert "substitute" not in _kinds(date(2026, 7, 20))

    assert date(2027, 7, 17).weekday() == 5
    assert _kinds(date(2027, 7, 19)) == ["substitute"]


def test_known_substitutes_across_all_rulesets():
    """확인된 대체공휴일이 ruleset 구간마다 하나씩 유도되는지.

    제2조 배열을 확보하기 전에는 2021-08-04 ~ 2026-04-30 을 유도 불가로 두었고
    이 날짜들이 전부 막혀 있었다. 배열이 들어오면서 풀렸다.
    구간 경계를 넘나드는 표본이라 한 ruleset 만 깨져도 여기서 드러난다.
    """
    known = {
        date(2019, 5, 6): "childrens_day",    # 제24828호
        date(2021, 10, 11): "hangeul_day",    # 제31930호
        date(2022, 10, 10): "hangeul_day",    # 제31930호
        date(2025, 3, 3): "samiljeol",        # 제33448호
        date(2026, 3, 2): "samiljeol",        # 제33448호
        date(2026, 8, 17): "gwangbokjeol",    # 제36290호
    }
    for day, source in known.items():
        found = [h for h in hc.holidays_on(day) if h.kind == "substitute"]
        assert found, f"{day}: 대체공휴일이 유도되지 않았다"
        assert found[0].source_key == source, f"{day}: 원인 공휴일이 {found[0].source_key}"


def test_clause_three_never_credits_an_ineligible_holiday():
    """3호 대체공휴일의 원인은 실제로 3호 대상인 공휴일이어야 한다.

    2017-10-03 에 개천절과 추석 연휴가 겹친다. 그 해 국경일은 아직 대체공휴일
    대상이 아니었으므로 개천절은 트리거가 될 수 없고 추석 쪽 규칙이 발동한 것이다
    (정답 픽스처 2017-10-06 케이스의 why 참조).

    겹친 목록의 첫 항목을 그냥 원인으로 적으면 배열 순서에 따라 개천절이 붙는다.
    어느 쪽이 트리거인지 확정되지 않은 것(3호-귀속-불명)과, 대상이 아닌 것을
    원인으로 적는 것은 다르다. 뒤쪽은 미확정이 아니라 틀린 것이다.
    """
    substitutes = [h for h in hc.holidays_on(date(2017, 10, 6)) if h.kind == "substitute"]
    assert substitutes, "2017-10-06 대체공휴일이 유도되지 않았다"

    source = substitutes[0].source_key
    assert source == "chuseok", f"원인이 {source!r} 로 붙었다"

    eligible = hc.substitute_eligibility(source, date(2017, 10, 3))
    assert eligible["clauses"], f"{source} 가 2017 년에 어느 호에도 속하지 않는다"


def test_no_fixture_case_is_provisional():
    """정답 픽스처는 확정 구간 안에만 있어야 한다.

    구현이 낸 잠정 결과를 정답으로 승격하면 정답과 입력이 같은 출처가 되어
    대조가 의미를 잃는다. 구현의 가정이 틀려도 정답이 함께 틀리므로 영원히 통과한다.
    미래 날짜 케이스는 그 날짜가 확정 구간에 들어온 뒤 관보로 확인해서 넣을 것.
    """
    confirmed = hc.coverage()["effective"].confirmed_through
    offenders = [
        c["id"] for c in fixture_loader.ALL_CASES if c["date"] > confirmed
    ]
    assert not offenders, (
        f"확정 시점({confirmed.isoformat()}) 이후 날짜를 쓰는 정답 케이스:\n"
        + "\n".join(f"  - {i}" for i in offenders)
        + "\n잠정 값을 정답으로 승격하지 말 것."
    )


def test_substitute_eligibility_uses_the_rule_table_range():
    """규칙 표만 보는 조회이므로 규칙 표의 구간을 쓴다.

    지정 공휴일 표(2015~)보다 넓어서 2014 년도 답할 수 있다.
    범위가 소스마다 다르다는 사실을 이 테스트가 고정한다.
    """
    assert hc.substitute_eligibility("광복절", date(2014, 8, 15))["saturday"] is False
    with pytest.raises(hc.UnsupportedYear):
        hc.substitute_eligibility("광복절", date(2013, 1, 1))


def test_known_election_days_are_present():
    """coverage 구간 안의 선거일이 빠져 있지 않은지.

    구간을 선언한 이상 그 안은 채워져 있어야 한다. 하나라도 비면 coverage 가
    거짓말이 된다. 이 목록 자체는 아직 관보 대조 전이다(관보-일괄대조 참조).
    """
    expected = {
        date(2016, 4, 13): "election",
        date(2018, 6, 13): "election",
        date(2020, 4, 15): "election",
        date(2022, 3, 9): "election",
        date(2022, 6, 1): "election",
        date(2024, 4, 10): "election",
        date(2026, 6, 3): "election",
        date(2017, 5, 9): "temporary",  # 궐위 선거
        date(2025, 6, 3): "temporary",  # 궐위 선거
    }
    for day, kind in expected.items():
        assert kind in _kinds(day), f"{day}: {kind} 로 등록되어 있어야 한다"


# ---------------------------------------------------------------------------
# 음력 — 인터페이스만 있고 구현은 없다
# ---------------------------------------------------------------------------


def test_nothing_is_unresolved_anymore():
    """미구현 공휴일이 남아 있지 않다.

    비어 있음을 명시적으로 고정한다. 음력이 들어오면서 마지막 항목이 빠졌고,
    그 결과 정답 픽스처의 depends_on 케이스가 전부 실제로 돌기 시작했다.
    이 집합이 다시 채워지면 그만큼 케이스가 조용히 skip 으로 빠진다.
    """
    assert hc.unresolved_holidays() == frozenset()
    for key in ("seollal", "chuseok", "buddhas_birthday", "gwangbokjeol"):
        hc.require_supported(key)  # 예외가 없어야 한다


def test_resolve_lunar_rejects_non_lunar_keys():
    """양력 공휴일을 음력 환산기에 넣으면 미구현이 아니라 오용이다."""
    with pytest.raises(hc.CalendarError):
        hc.resolve_lunar("gwangbokjeol", 2026)


def test_lunar_holidays_are_in_the_output():
    """음력 공휴일이 결과에 나온다. 연휴는 전날·당일·다음날 3 일이다."""
    assert _names(date(2026, 2, 16)) == ["설날 연휴"]
    assert _names(date(2026, 2, 17)) == ["설날"]
    assert _names(date(2026, 2, 18)) == ["설날 연휴"]
    assert _names(date(2026, 2, 19)) == []  # 경계. 하루 밀리면 여기가 잡힌다

    assert _names(date(2026, 9, 25)) == ["추석"]
    assert _names(date(2026, 5, 24)) == ["부처님오신날"]


def test_leave_days_carry_the_festival_key():
    """연휴에도 명절 key 가 붙어야 대체공휴일 판정이 돈다.

    key 를 비워 두면 연휴가 일요일에 걸려도 호 소속을 못 찾아 대체공휴일이
    생기지 않는다. 설·추석은 일요일과 겹칠 때만 대상이라 그 경로가 유일하다.
    """
    for day in (date(2026, 2, 16), date(2026, 2, 18)):
        assert [h.key for h in hc.holidays_on(day)] == ["seollal"]


@contextmanager
def _lunar_raw_patched(mutate):
    """lunar_holidays.yaml 을 바꿔 읽힌 상태로 돌린다. 캐시를 앞뒤로 비운다.

    파일을 건드리지 않는다. 예외 표가 비어 있는 동안에도 덮어쓰기 경로가
    실제로 도는지 확인해야 하는데, 빈 표만 보면 그것을 알 수 없다.
    """
    original = hc._lunar_raw()
    patched = deepcopy(original)
    mutate(patched)
    for cache in (hc._lunar_raw, hc._lunar, hc._calendar_cached, hc.coverage):
        cache.cache_clear()
    hc._lunar_raw = lambda _p=patched: _p
    try:
        yield
    finally:
        hc._lunar_raw = original_reader
        for cache in (hc._lunar, hc._calendar_cached, hc.coverage):
            cache.cache_clear()


original_reader = hc._lunar_raw


def test_lunar_exception_table_overrides_the_calculation():
    """발표값 예외가 계산을 이긴다.

    한국 공식 역서는 한국천문연구원 발표값이고 우리 계산은 2차 소스다.
    갈리면 발표가 맞다. 계산을 손봐서 맞추지 않는다.
    """
    assert hc.resolve_lunar("seollal", 2026) == date(2026, 2, 17)  # 계산값

    def add_exception(raw):
        raw["exceptions"] = [
            {
                "key": "seollal",
                "year": 2026,
                "computed": date(2026, 2, 17),
                "published": date(2026, 2, 18),
                "source": "테스트용 가짜 발표값",
            }
        ]

    with _lunar_raw_patched(add_exception):
        assert hc.resolve_lunar("seollal", 2026) == date(2026, 2, 18)
        # 연휴 3 일이 통째로 따라 움직여야 한다. 당일만 옮기면 연휴가 어긋난다.
        assert _names(date(2026, 2, 17)) == ["설날 연휴"]
        assert _names(date(2026, 2, 19)) == ["설날 연휴"]

    assert hc.resolve_lunar("seollal", 2026) == date(2026, 2, 17)  # 원상복구


@pytest.mark.parametrize(
    "missing, expected",
    [("source", "source 가 비어 있다"), ("published", "published 가 날짜가 아니다")],
)
def test_lunar_exception_needs_a_published_date_and_a_source(missing, expected):
    """근거 없는 예외는 받지 않는다.

    예외는 우리 계산을 덮어쓰는 장치다. 무엇으로 덮는지 적히지 않으면 다음
    사람이 그 값을 확인할 방법이 없고, 계산 버그를 예외로 덮어 감춘 것과
    구분되지 않는다.
    """

    def add_exception(raw):
        item = {
            "key": "seollal",
            "year": 2026,
            "published": date(2026, 2, 18),
            "source": "테스트용 가짜 발표값",
        }
        item[missing] = None
        raw["exceptions"] = [item]

    with pytest.raises(hc.CalendarError) as exc:  # noqa: PT012 - 컨텍스트 안에서 터진다
        with _lunar_raw_patched(add_exception):
            hc.resolve_lunar("seollal", 2026)
    assert expected in str(exc.value)
