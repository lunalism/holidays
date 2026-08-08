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

from datetime import date

import pytest

from rules.kr import holiday_calendar as hc
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


def test_election_day_is_substitute_eligible():
    """선거일은 대상이다. 근거 호는 미확인이라 kind 로 게이트한다."""
    election = hc.Holiday(name="제9회 전국동시지방선거", kind="election")
    assert hc._eligible_overlaps(election, date(2026, 6, 3)), (
        "선거일이 대체공휴일 대상에서 빠졌다. "
        "designated_holidays.yaml 의 kinds.election.substitute_eligible 확인."
    )


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
        "designated_holidays.yaml",
        "substitute_holidays.yaml",
    }
    assert cov["effective"].start == max(c.start for c in sources.values())
    assert cov["effective"].confirmed_through == min(
        c.confirmed_through for c in sources.values()
    )


def test_narrowest_source_decides_the_range():
    """가장 좁은 소스가 전체를 결정한다.

    start 는 가장 늦은 것을, confirmed_through 는 가장 이른 것을 따른다.
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
    for far in (date(2027, 1, 1), date(2030, 8, 15), date(2035, 3, 1)):
        hc.holidays_on(far)  # 예외가 없어야 한다
        assert hc.is_provisional(far)

    assert _names(date(2030, 8, 15)) == ["광복절"]


def test_provisional_flag_is_attached_to_each_holiday():
    """피드 생성기가 항목 단위로 보고 표시하거나 잘라낼 수 있어야 한다."""
    confirmed = hc.coverage()["effective"].confirmed_through

    for h in hc.holidays_on(date(2026, 8, 15)):  # 확정 구간
        assert h.provisional is False
    for h in hc.holidays_on(date(2027, 8, 15)):  # 확정 이후
        assert h.provisional is True

    assert hc.is_provisional(confirmed) is False
    assert hc.is_provisional(date(confirmed.year + 1, 1, 1)) is True


def test_substitute_eligibility_reports_provisional():
    assert hc.substitute_eligibility("광복절", date(2026, 8, 15))["provisional"] is False
    assert hc.substitute_eligibility("광복절", date(2030, 8, 15))["provisional"] is True


def test_provisional_substitutes_still_derive():
    """잠정 구간에서도 대체공휴일 계산은 그대로 돈다. 표시만 다르다.

    2027-08-15 는 일요일이라 08-16 이 대체공휴일이 되어야 한다.
    잠정이라고 계산을 멈추면 선발행할 피드가 비어 버린다.
    """
    assert date(2027, 8, 15).weekday() == 6
    substitutes = [h for h in hc.holidays_on(date(2027, 8, 16)) if h.kind == "substitute"]
    assert substitutes, "잠정 구간에서 대체공휴일이 계산되지 않았다"
    assert all(h.provisional for h in substitutes)


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


@pytest.mark.parametrize("key", ["seollal", "chuseok", "buddhas_birthday"])
def test_lunar_holidays_are_declared_unresolved(key):
    assert key in hc.unresolved_holidays()
    with pytest.raises(hc.LunarNotImplemented):
        hc.require_supported(key)
    with pytest.raises(hc.LunarNotImplemented):
        hc.resolve_lunar(key, 2026)


def test_solar_holidays_are_supported():
    for key in ("gwangbokjeol", "childrens_day", "constitution_day"):
        hc.require_supported(key)  # 예외가 없어야 한다


def test_resolve_lunar_rejects_non_lunar_keys():
    """양력 공휴일을 음력 환산기에 넣으면 미구현이 아니라 오용이다."""
    with pytest.raises(hc.CalendarError):
        hc.resolve_lunar("gwangbokjeol", 2026)


def test_lunar_holidays_are_absent_from_the_output():
    """설날이 있어야 할 날짜가 지금은 비어 있다.

    이것이 정답이라는 뜻이 아니다. 음력이 미구현이라 나타나는 결과이고,
    정답 픽스처에서 이 날짜들이 depends_on 으로 skip 되는 이유다.
    구현이 들어오면 이 테스트를 지울 것.
    """
    assert hc.holidays_on(date(2026, 2, 17)) == ()
    assert "seollal" in hc.unresolved_holidays()
