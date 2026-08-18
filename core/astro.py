"""천문 계산 — 태양 황경.

나라 이름이 이 파일에 나오지 않는다. 태양이 언제 어느 황경에 있는지는 어느
나라에서 보든 같은 값이고, 그 시각을 어느 날짜로 읽을지만 나라마다 다르다.
그 읽기는 core/timekeeping.py 가 하고, 어느 오프셋을 물릴지는
rules/<국가>/astro.py 가 정한다.

삭(朔)은 여기 없다. 삭 급수는 아직 한국 음력에서만 쓰이므로
rules/kr/astro.py 에 있다. 쓰는 나라가 둘이 되면 그때 올린다 — 미리 올려
두면 "왜 여기 있는가"에 답할 근거가 없다.

--------------------------------------------------------------------------
쓰는 급수와 그 정확도
--------------------------------------------------------------------------
Meeus, Astronomical Algorithms 2판 제25장 저정밀도 식. 문헌이 밝히는 오차는
약 0.01° 다. 시간으로 환산하면 약 15 분이다(태양은 하루에 약 0.9856° 간다).

문헌 오차를 그대로 믿지 않는다. 우리가 옮겨 적은 계수가 맞는지는 별개 문제이고,
그건 실측 대조로만 확인된다. tests/test_astro.py 가 그 대조를 맡는다.

--------------------------------------------------------------------------
이 값을 흔들어 보는 테스트가 있다
--------------------------------------------------------------------------
tests/test_lunar.py 가 apparent_solar_longitude 를 갈아끼워 급수 오차가
공휴일 날짜를 바꾸는지 본다. solar_term_jde() 는 이 이름을 모듈 전역에서
호출 시점에 읽는다 — 그래야 그 패치가 물린다.

import 시점에 캡처하지 말 것(partial, 기본인자, 지역 별칭 — 전부 그 테스트를
무력화한다). 다른 모듈이 이 이름을 재수출해도 그쪽을 갈아끼우는 것으로는
여기까지 오지 않는다. 패치는 이 모듈에 걸어야 한다.
"""

from __future__ import annotations

import math

J2000 = 2451545.0

# 태양이 하루에 가는 평균 황경. 중기 시각을 뉴턴법으로 좁힐 때 기울기로 쓴다.
# 실제 속도는 근일점 근처에서 3% 남짓 빠르므로 반복이 필요하다.
SOLAR_DEGREES_PER_DAY = 0.98565

_TERM_TOLERANCE_DEG = 1e-7   # 시간으로 약 0.01 초

# 뉴턴법 반복 상한. 수렴 실패를 무한 루프 대신 예외로 드러내기 위한 값이다.
_TERM_MAX_ITER = 30


class AstroError(ValueError):
    """천문 계산이 답을 내지 못했다."""


def apparent_solar_longitude(jde: float) -> float:
    """겉보기 태양 황경(도). 장동과 광행차를 포함한다."""
    t = (jde - J2000) / 36525.0
    mean_longitude = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    anomaly = math.radians(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    center = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(anomaly)
        + (0.019993 - 0.000101 * t) * math.sin(2 * anomaly)
        + 0.000289 * math.sin(3 * anomaly)
    )
    node = math.radians(125.04 - 1934.136 * t)
    return (mean_longitude + center - 0.00569 - 0.00478 * math.sin(node)) % 360.0


def solar_term_jde(longitude: float, guess: float) -> float:
    """태양 황경이 그 값이 되는 시각. guess 근처의 해를 찾는다.

    guess 가 며칠 어긋나도 수렴하지만 한 달 이상 어긋나면 옆 해로 넘어간다.
    호출자가 30 일 안쪽 추정을 주는 것을 전제로 한다.
    """
    jde = guess
    for _ in range(_TERM_MAX_ITER):
        gap = (longitude - apparent_solar_longitude(jde) + 180.0) % 360.0 - 180.0
        if abs(gap) < _TERM_TOLERANCE_DEG:
            return jde
        jde += gap / SOLAR_DEGREES_PER_DAY
    raise AstroError(f"황경 {longitude}° 시각이 수렴하지 않았다(시작 {guess}).")
