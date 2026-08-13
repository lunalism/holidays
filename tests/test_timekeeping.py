"""core/timekeeping.py — 율리우스일과 ΔT.

여기서는 시각을 날짜로 옮기는 일만 본다. 그 날짜에 한국 오프셋을 물리는 일은
rules/kr/astro.py 의 몫이고 tests/test_astro.py 가 본다.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import pytest

from core import timekeeping

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
    assert timekeeping.julian_day(day) == expected


def test_julian_day_round_trips_over_a_long_span():
    """정수 JD ↔ 날짜가 어긋나면 모든 날짜 판정이 하루씩 밀린다."""
    day = date(1900, 1, 1)
    while day < date(2101, 1, 1):
        number = math.floor(timekeeping.julian_day(day) + 0.5)
        assert timekeeping.civil_from_day_number(number) == day, day
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
        before = timekeeping.delta_t_seconds(boundary - 1e-6)
        after = timekeeping.delta_t_seconds(boundary + 1e-6)
        assert abs(after - before) < 1.0, (
            f"{boundary} 이음매에서 ΔT 가 {after - before:.3f} 초 튄다"
        )


def test_delta_t_is_near_the_observed_value_in_our_range():
    """2005~2050 구간 식은 실측이 평평해지면서 몇 초 높게 나온다.

    그 편차를 알고 쓴다는 것을 고정한다. 우리 판정 단위는 분이므로 결과를
    바꾸지 못한다. 크게 벌어지면 식을 잘못 옮긴 것이다.
    """
    assert 68 < timekeeping.delta_t_seconds(2020.0) < 75
