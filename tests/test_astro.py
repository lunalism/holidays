"""rules/kr/astro.py — 삭 시각과 태양 황경.

여기서는 천문 계산만 본다. 그 시각에서 달 번호를 세우는 일은 lunar.py 의
몫이고 tests/test_lunar.py 가 본다. 설날이 하루 밀렸을 때 원인을 두 층으로
갈라 보기 위한 분리다.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import pytest

from rules.kr import astro

# ---------------------------------------------------------------------------
# 율리우스일
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "day, expected",
    [
        (date(2000, 1, 1), 2451544.5),   # Meeus 제7장 예제
        (date(1987, 1, 27), 2446822.5),
        (date(2026, 8, 8), 2461260.5),
    ],
)
def test_julian_day_matches_known_values(day, expected):
    assert astro.julian_day(day) == expected


def test_julian_day_round_trips_over_a_long_span():
    """정수 JD ↔ 날짜가 어긋나면 모든 날짜 판정이 하루씩 밀린다."""
    day = date(1900, 1, 1)
    while day < date(2101, 1, 1):
        number = math.floor(astro.julian_day(day) + 0.5)
        assert astro._civil_from_day_number(number) == day, day
        day += timedelta(days=397)  # 윤년·세기 경계를 골고루 밟는 간격


# ---------------------------------------------------------------------------
# ΔT
# ---------------------------------------------------------------------------


def test_delta_t_is_continuous_across_segment_boundaries():
    """구간별 다항식이라 이음매에서 튈 수 있다.

    튀면 그 해 근처의 삭 시각이 통째로 어긋난다. 1 초 안쪽이면 우리 판정
    단위(분)에 영향이 없다.
    """
    for boundary in (1920, 1941, 1961, 1986, 2005, 2050):
        before = astro.delta_t_seconds(boundary - 1e-6)
        after = astro.delta_t_seconds(boundary + 1e-6)
        assert abs(after - before) < 1.0, (
            f"{boundary} 이음매에서 ΔT 가 {after - before:.3f} 초 튄다"
        )


def test_delta_t_is_near_the_observed_value_in_our_range():
    """2005~2050 구간 식은 실측이 평평해지면서 몇 초 높게 나온다.

    그 편차를 알고 쓴다는 것을 고정한다. 우리 판정 단위는 분이므로 결과를
    바꾸지 못한다. 크게 벌어지면 식을 잘못 옮긴 것이다.
    """
    assert 68 < astro.delta_t_seconds(2020.0) < 75


# ---------------------------------------------------------------------------
# 삭
# ---------------------------------------------------------------------------


def test_new_moon_zero_matches_the_published_instant():
    """k=0 은 2000-01-06 18:14 UT 의 삭이다. KST 로 01-07 03:14.

    급수 계수를 하나라도 잘못 옮기면 여기서 분 단위로 어긋난다.
    이 값이 맞아야 나머지 삭이 의미를 갖는다.
    """
    day, minutes = astro.kst_moment(astro.new_moon_jde(0))
    assert day == date(2000, 1, 7)
    assert abs(minutes - (3 * 60 + 14)) < 2.0, f"KST {minutes / 60:.3f} 시"


def test_new_moon_spacing_stays_near_the_synodic_month():
    """삭 간격은 29.27~29.84 일 사이에서 흔들린다.

    급수의 큰 항을 빠뜨리면 간격이 튄다. 개별 시각이 맞는지는 못 보지만
    계수를 통째로 잘못 옮긴 경우는 여기서 드러난다.
    """
    previous = astro.new_moon_jde(-500)
    for k in range(-499, 700):
        current = astro.new_moon_jde(k)
        gap = current - previous
        assert 29.20 < gap < 29.90, f"k={k} 간격 {gap:.4f} 일"
        previous = current


def test_month_start_k_walks_to_the_right_month():
    """k 추정이 어긋나도 걸어서 확정하는지.

    추정값을 그대로 믿으면 연말·연초에서 조용히 한 달 밀린다.
    """
    day = date(2015, 1, 1)
    while day < date(2031, 1, 1):
        k = astro.month_start_k(day)
        start = astro.kst_moment(astro.new_moon_jde(k))[0]
        following = astro.kst_moment(astro.new_moon_jde(k + 1))[0]
        assert start <= day < following, f"{day}: {start} ~ {following}"
        day += timedelta(days=11)


def test_new_moon_rejects_a_non_integer_k():
    """삭은 정수 k 에서만 정의된다. 실수를 넣으면 망·현이 섞여 나온다."""
    with pytest.raises(astro.AstroError):
        astro.new_moon_jde(0.5)


# ---------------------------------------------------------------------------
# 태양 황경
# ---------------------------------------------------------------------------


def test_solar_longitude_advances_about_one_degree_a_day():
    """근일점 근처가 빠르고 원일점 근처가 느리다. 그 폭 안에 있어야 한다."""
    base = astro.julian_day(date(2026, 1, 1))
    for offset in range(0, 365, 7):
        today = astro.apparent_solar_longitude(base + offset)
        tomorrow = astro.apparent_solar_longitude(base + offset + 1)
        step = (tomorrow - today) % 360.0
        assert 0.95 < step < 1.03, f"{offset} 일째 {step:.4f}°"


@pytest.mark.parametrize(
    "longitude, near, expected_month",
    [(270.0, date(2025, 12, 21), 12), (0.0, date(2026, 3, 20), 3), (90.0, date(2026, 6, 21), 6)],
)
def test_solar_term_lands_on_the_expected_season(longitude, near, expected_month):
    jde = astro.solar_term_jde(longitude, astro.julian_day(near))
    found = astro.kst_moment(jde)[0]
    assert found.month == expected_month
    assert abs((found - near).days) <= 2


def test_solar_term_converges_from_a_rough_guess():
    """추정이 며칠 어긋나도 같은 해를 찾아야 한다."""
    target = astro.solar_term_jde(270.0, astro.julian_day(date(2025, 12, 21)))
    for offset in (-10, -3, 3, 10):
        again = astro.solar_term_jde(270.0, astro.julian_day(date(2025, 12, 21)) + offset)
        assert abs(again - target) < 1e-5


def test_minutes_from_midnight_folds_both_sides():
    """00:05 와 23:55 는 둘 다 자정에서 5 분이다.

    여유를 볼 때 문제는 어느 쪽인지가 아니라 얼마나 가까운지다.
    접지 않으면 자정 직전 값이 1435 분으로 보여 안전해 보인다.
    """
    solstice = astro.winter_solstice_jde(2025)
    assert astro.minutes_from_midnight(solstice) <= 720.0
    assert astro.minutes_from_midnight(solstice) == pytest.approx(
        min(astro.kst_moment(solstice)[1], 1440 - astro.kst_moment(solstice)[1])
    )
