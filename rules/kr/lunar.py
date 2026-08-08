"""음력 역법 — 삭과 중기에서 달 번호를 세운다.

    solar_date(year, month, day)  -> 그 음력 날짜의 양력 날짜
    months_of_sui(year)           -> 그 해 설날이 드는 세(歲)의 달 목록

천문 계산은 여기 없다. rules/kr/astro.py 가 진다. 이 파일이 하는 일은
"삭 목록과 중기 목록이 주어졌을 때 어느 달이 1 월인가"를 정하는 것이다.

--------------------------------------------------------------------------
삭만으로는 부족하다
--------------------------------------------------------------------------
"삭이 든 날이 초하루"는 맞지만 그것은 달의 시작만 정한다.
설날은 초하루가 아니라 음력 1 월의 초하루다. 어느 삭이 1 월인지 정하려면
세 가지가 더 필요하다.

  1. 중기(中氣)   태양 황경이 30°의 배수가 되는 순간. 즉 태양 위치 계산.
  2. 무중치윤법   중기가 없는 달이 윤달이다.
  3. 세수(歲首)   동지가 든 달을 11 월로 놓고 거기서부터 센다.

셋 다 KST 자정 기준으로 날짜를 뽑아 비교한다. 시각끼리 비교하지 않는다.
역서가 날짜 단위로 정의되어 있기 때문이고, 그래서 급수 오차는 그 시각이
자정에 가까울 때만 결과를 바꾼다. astro.py 의 모듈 docstring 참조.

--------------------------------------------------------------------------
세(歲)
--------------------------------------------------------------------------
세는 동지가 든 달에서 시작해 다음 동지가 든 달 직전까지다.
그 사이에 삭망월이 12 개면 평년, 13 개면 윤년이다.
윤년이면 그중 중기가 없는 첫 달이 윤달이고, 앞 달의 번호를 물려받는다.

    11 12 1 2 3 4 5 6 7 8 9 10          평년 12 달
    11 12 1 2 3 윤3 4 5 6 7 8 9 10      윤3월이 든 해 13 달

첫 달(11 월)은 동지를 품고 있으므로 윤달이 될 수 없다. 그래서 윤달 탐색은
두 번째 달부터 한다.

--------------------------------------------------------------------------
한계
--------------------------------------------------------------------------
이 규칙은 시헌력 이후의 정기법을 따른 것이고, 경계 사례에서 해석이 갈린 적이
있다(2033 년 윤달 배치 논란이 그것이다). 우리 계산이 유일한 답이라고 보지
않는다. 최종 판정은 한국천문연구원 발표값이고, 갈리는 날짜는 예외 표에 적어
근거와 함께 못박는다. rules/kr/lunar_holidays.yaml 의 exceptions 참조.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from rules.kr import astro

# 중기는 동지(270°)에서 30°씩 간다. 절기가 아니라 중기만 센다.
WINTER_SOLSTICE_LONGITUDE = 270.0
MID_TERM_STEP_DEGREES = 30.0

# 한 세는 12 달 또는 13 달이다. 그 밖이면 계산이 깨진 것이다.
MONTHS_IN_COMMON_SUI = 12
MONTHS_IN_LEAP_SUI = 13


class LunarError(ValueError):
    """음력 계산이 답을 내지 못했다."""


@dataclass(frozen=True)
class LunarMonth:
    """음력 한 달. 경계는 KST 날짜다."""

    number: int      # 1~12
    leap: bool
    start: date      # 초하루
    end: date        # 그믐 (다음 달 초하루 전날)

    @property
    def length(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def label(self) -> str:
        return f"윤{self.number}월" if self.leap else f"{self.number}월"

    def day(self, day_of_month: int) -> date:
        if not 1 <= day_of_month <= self.length:
            raise LunarError(
                f"{self.label} 은 {self.length} 일까지다. {day_of_month} 일은 없다."
            )
        return self.start + timedelta(days=day_of_month - 1)


def _mid_term_days(start_jde: float, count: int) -> list:
    """동지부터 30°씩 나아간 중기들의 KST 날짜."""
    days = []
    jde = start_jde
    for index in range(count):
        longitude = (WINTER_SOLSTICE_LONGITUDE + MID_TERM_STEP_DEGREES * index) % 360.0
        guess = jde if index == 0 else jde + astro._MID_TERM_INTERVAL_DAYS
        jde = astro.solar_term_jde(longitude, guess)
        days.append(astro.kst_moment(jde)[0])
    return days


def months_of_sui(year: int) -> tuple:
    """음력 1 월이 양력 `year` 에 드는 세의 달 목록.

    전년 동지가 든 달(11 월)에서 시작한다. 그래서 앞의 11·12 월은 양력으로
    `year - 1` 에 속하고, 1 월부터 10 월까지가 `year` 에 속한다.
    """
    previous_solstice = astro.winter_solstice_jde(year - 1)
    next_solstice = astro.winter_solstice_jde(year)

    first_k = astro.month_start_k(astro.kst_moment(previous_solstice)[0])
    last_k = astro.month_start_k(astro.kst_moment(next_solstice)[0])
    count = last_k - first_k

    if count not in (MONTHS_IN_COMMON_SUI, MONTHS_IN_LEAP_SUI):
        raise LunarError(
            f"{year} 년 세의 달 수가 {count} 다. 12 또는 13 이어야 한다.\n"
            "동지 시각이나 삭 시각 계산이 깨졌다는 뜻이다."
        )

    starts = [astro.kst_moment(astro.new_moon_jde(first_k + i))[0] for i in range(count + 1)]

    # 중기는 세 전체를 덮을 만큼만 뽑는다. 13 달이면 13 개로 모자랄 수 있으므로
    # 한 개 넉넉히 잡는다. 남는 것은 어느 달에도 안 걸리고 그냥 버려진다.
    terms = _mid_term_days(previous_solstice, count + 1)

    contains_term = [
        any(starts[i] <= term < starts[i + 1] for term in terms) for i in range(count)
    ]

    leap_index = None
    if count == MONTHS_IN_LEAP_SUI:
        # 첫 달은 동지를 품으므로 윤달이 될 수 없다. 두 번째 달부터 찾는다.
        leap_index = next((i for i in range(1, count) if not contains_term[i]), None)
        if leap_index is None:
            raise LunarError(
                f"{year} 년 세가 13 달인데 중기 없는 달이 없다.\n"
                "무중치윤법이 성립하지 않는다. 중기 시각 계산을 의심할 것."
            )

    months = []
    number = 11
    previous_number = None
    for index in range(count):
        span = (starts[index], starts[index + 1] - timedelta(days=1))
        if index == leap_index:
            months.append(LunarMonth(previous_number, True, *span))
            continue
        months.append(LunarMonth(number, False, *span))
        previous_number = number
        number = number % 12 + 1
    return tuple(months)


def month_of(year: int, month: int, leap: bool = False) -> LunarMonth:
    """그 세의 해당 음력 달.

    11·12 월은 받지 않는다. 그 두 달은 세의 앞머리라 양력으로 `year - 1` 에
    속하는데, 호출자가 그것을 알고 물었는지 아닌지 구분할 방법이 없다.
    조용히 한 해 전 날짜를 돌려주느니 거부한다.
    """
    if not 1 <= month <= 10:
        raise LunarError(
            f"음력 {month} 월은 이 함수로 조회하지 않는다(1~10 월만).\n"
            "11·12 월은 세의 앞머리라 양력으로 전년에 속한다. 어느 해를 물은 "
            "것인지 모호해지므로 months_of_sui() 를 직접 쓸 것."
        )
    for candidate in months_of_sui(year):
        if candidate.number == month and candidate.leap == leap:
            return candidate
    label = f"윤{month}월" if leap else f"{month}월"
    raise LunarError(f"{year} 년 세에 {label} 이 없다.")


def solar_date(year: int, month: int, day: int, leap: bool = False) -> date:
    """음력 날짜의 양력 환산. year 는 그 음력 달이 드는 양력 연도다."""
    return month_of(year, month, leap).day(day)


def leap_month_of(year: int):
    """그 세의 윤달. 없으면 None. 검증·리포트용이다."""
    return next((m for m in months_of_sui(year) if m.leap), None)
