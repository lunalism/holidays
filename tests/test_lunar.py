"""rules/kr/lunar.py — 삭과 중기에서 달 번호를 세운다.

--------------------------------------------------------------------------
무엇으로 검증하는가
--------------------------------------------------------------------------
KASI 특일정보 캐시가 덮는 2015~2028 년의 앵커 42 건(설날·추석·부처님오신날
각 14 년)이 유일한 실측 대조다. 그 밖은 대조된 바 없고, 그래서
lunar_holidays.yaml 의 confirmed_through 가 2028-12-31 이다.

앵커 대조만으로는 부족하다. "맞았다"는 사실은 알려 주지만 "왜 맞았는지",
"얼마나 아슬아슬하게 맞았는지"는 알려 주지 않는다. 급수를 조금 잘못 옮겨도
운 좋게 42 건이 다 맞을 수 있다. 그래서 세 가지를 더 본다.

  자정 여유   삭·중기가 KST 자정에서 얼마나 떨어져 있는가.
              가까울수록 급수 오차가 하루를 가를 수 있는 자리다.
  섭동 내성   급수를 일부러 흔들어도 답이 그대로인가.
              문헌 오차의 몇 배까지 견디는지가 실제 안전 여유다.
  시간대 감도 UTC+8 로 계산하면 달라지는가.
              달라지는 해가 실제로 있고, 그 해에 우리 KST 값이 KASI 와 맞는다는
              것이 중국 음력 라이브러리를 쓰지 않은 이유의 실증이다.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from rules.kr import astro, lunar
from rules.kr import holiday_calendar as hc
from sources.kr import kasi_parser as kp

CACHE_DIR = Path(__file__).parent.parent / "sources" / "kr" / "cache"

# 음력 공휴일의 정의. lunar_holidays.yaml 과 같은 값이어야 한다.
SPEC = {"seollal": (1, 1), "chuseok": (8, 15), "buddhas_birthday": (4, 8)}

# 섭동 폭. 문헌 오차의 몇 배인지가 요점이다.
#   태양 황경 Meeus 제25장 문헌 오차 약 0.01° → 5 배
#   삭 시각   Meeus 제49장 문헌 오차 20 초 안쪽 → 15 배
SOLAR_PERTURBATION_DEGREES = 0.05
LUNAR_PERTURBATION_SECONDS = 300

# 카나리아 폭. 위 섭동과 단언 방향이 반대다 — 이만큼 흔들면 반드시 바뀌어야 한다.
# 실측 임계점(-0.06°)의 80 배 남짓이라 임계점이 흘러도 이 단언은 흔들리지 않는다.
SOLAR_CANARY_DEGREES = 5.0

# 섭동 테스트가 도는 구간. 대조 구간보다 넓게 잡는다. 대조되지 않은 구간에서
# 여유가 어떻게 되는지도 알아야 confirmed_through 를 밀 때 근거가 된다.
PROBE_YEARS = range(2015, 2051)


def _cached_paths() -> list:
    return sorted(CACHE_DIR.glob("getRestDeInfo_*.xml"))


pytestmark = pytest.mark.skipif(not _cached_paths(), reason="캐시된 KASI 응답이 없다.")


def _kasi_anchors() -> dict:
    """(연도, 키) → KASI 가 준 명절 당일 날짜.

    설·추석은 연휴 3 일이 같은 이름으로 오므로 가운데 날을 당일로 본다.
    3 일이 아닌 해는 연휴 범위 자체가 다르다는 뜻이라 앵커로 쓰지 않는다.
    """
    found = {}
    for path in _cached_paths():
        for item in kp.parse(path.read_text(encoding="utf-8")):
            if item.key in SPEC:
                found.setdefault((item.date.year, item.key), []).append(item.date)

    anchors = {}
    for (year, key), days in found.items():
        days = sorted(days)
        expected = 3 if key in ("seollal", "chuseok") else 1
        if len(days) != expected:
            continue
        anchors[(year, key)] = days[len(days) // 2]
    return anchors


def _our_dates(years=PROBE_YEARS) -> dict:
    return {
        (year, key): lunar.solar_date(year, *SPEC[key]) for year in years for key in SPEC
    }


# ---------------------------------------------------------------------------
# 실측 대조
# ---------------------------------------------------------------------------


def test_every_cached_anchor_matches_kasi():
    """대조 구간의 앵커가 전부 맞는지. 이것이 1 차 근거다."""
    anchors = _kasi_anchors()
    assert len(anchors) >= 40, f"앵커가 {len(anchors)} 건뿐이다. 캐시나 파서를 의심할 것."

    wrong = []
    for (year, key), published in sorted(anchors.items()):
        computed = lunar.solar_date(year, *SPEC[key])
        if computed != published:
            wrong.append(f"  {year} {key}: 계산 {computed} / KASI {published}")

    assert not wrong, (
        f"앵커 {len(wrong)}/{len(anchors)} 건이 어긋났다:\n" + "\n".join(wrong)
        + "\n계산을 고쳐 맞추기 전에 lunar_holidays.yaml 의 exceptions 를 볼 것. "
        "한국 공식 역서는 발표값이고 우리 계산은 2차 소스다."
    )


def test_leave_spans_three_days_for_seollal_and_chuseok():
    """KASI 가 준 연휴 범위가 전날·당일·다음날인지.

    lunar_holidays.yaml 의 leave 가 그렇게 적혀 있다. 응답과 어긋나면 그 값이
    틀렸다는 뜻이고, 연휴 3 일이 통째로 밀린다.
    """
    found = {}
    for path in _cached_paths():
        for item in kp.parse(path.read_text(encoding="utf-8")):
            if item.key in ("seollal", "chuseok"):
                found.setdefault((item.date.year, item.key), []).append(item.date)

    for (year, key), days in sorted(found.items()):
        days = sorted(days)
        if len(days) != 3:
            continue  # 연휴가 잘려 응답된 해. 앵커에서도 뺀다.
        anchor = lunar.solar_date(year, *SPEC[key])
        assert days[1] == anchor, f"{year} {key}: 가운데 날 {days[1]} ≠ 명절 {anchor}"
        assert (days[2] - days[0]).days == 2, f"{year} {key}: {days}"


@pytest.mark.parametrize(
    "year, expected",
    [
        (2017, "윤5월"),
        (2020, "윤4월"),
        (2023, "윤2월"),
        (2025, "윤6월"),
        (2028, "윤5월"),
        (2026, None),
        (2027, None),
    ],
)
def test_known_leap_months(year, expected):
    """윤달 배치. 무중치윤법이 실제로 도는지 보는 자리다.

    2025 년이 윤6월이라는 것이 2026-02-17 설날의 배경이다. 단순히 354 일을
    더하는 방식으로는 맞출 수 없다는 정답 픽스처의 근거가 여기서 확인된다.
    """
    leap = lunar.leap_month_of(year)
    assert (leap.label if leap else None) == expected


# ---------------------------------------------------------------------------
# 세(歲)의 구조
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", list(PROBE_YEARS))
def test_sui_structure_is_well_formed(year):
    """달 수, 번호 순서, 날짜 연속성.

    앵커 대조는 세 개 달만 본다. 나머지 달이 어긋나 있어도 드러나지 않으므로
    구조를 따로 확인한다.
    """
    months = lunar.months_of_sui(year)
    assert len(months) in (12, 13)

    plain = [m.number for m in months if not m.leap]
    assert plain == [11, 12] + list(range(1, 11)), f"{year}: 번호 순서 {plain}"

    for previous, current in zip(months, months[1:], strict=False):
        assert current.start == previous.end + timedelta(days=1), f"{year}: 달 사이가 비었다"
        assert 29 <= previous.length <= 30, f"{year}: {previous.label} 이 {previous.length} 일"

    leaps = [m for m in months if m.leap]
    assert len(leaps) == (1 if len(months) == 13 else 0)
    if leaps:
        # 윤달은 앞 달의 번호를 물려받는다. 첫 달(11월)은 동지를 품어 윤달이 못 된다.
        index = months.index(leaps[0])
        assert index >= 1
        assert months[index - 1].number == leaps[0].number


def test_month_of_refuses_the_ambiguous_months():
    """11·12 월은 세의 앞머리라 양력으로 전년에 속한다.

    조용히 한 해 전 날짜를 돌려주면 호출자가 알아챌 방법이 없다.
    """
    for month in (11, 12, 0, 13):
        with pytest.raises(lunar.LunarError):
            lunar.month_of(2026, month)


def test_day_beyond_the_month_length_is_rejected():
    """29 일까지인 달에 30 일을 물으면 다음 달 초하루를 돌려주면 안 된다."""
    month = lunar.month_of(2026, 1)
    with pytest.raises(lunar.LunarError):
        month.day(month.length + 1)


# ---------------------------------------------------------------------------
# 자정 여유 — 급수 오차가 하루를 가를 수 있는 자리인가
# ---------------------------------------------------------------------------


def test_new_moons_keep_a_margin_from_kst_midnight():
    """실제로 쓰이는 초하루가 자정에서 얼마나 떨어져 있는가.

    삭이 자정에 아주 가까우면 20 초짜리 급수 오차도 초하루를 하루 옮긴다.
    최소 여유를 고정해 두면 급수를 건드렸을 때 여유가 줄어드는 것이 보인다.
    """
    margins = []
    for year in PROBE_YEARS:
        for month in lunar.months_of_sui(year):
            k = astro.month_start_k(month.start)
            margins.append((astro.minutes_from_midnight(astro.new_moon_jde(k)), month.start))

    worst, day = min(margins)
    assert worst > 1.0, (
        f"{day} 초하루의 삭이 KST 자정에서 {worst:.2f} 분이다.\n"
        "급수 오차가 그대로 하루를 가르는 자리다. 그 날짜는 발표값으로 확인할 것."
    )


def test_mid_terms_keep_a_margin_from_kst_midnight():
    """중기가 자정에 가까우면 윤달 자리가 갈릴 수 있다.

    2025-12-22 동지가 자정에서 1 분 안쪽이다. 태양 황경의 문헌 오차(약 15 분)
    보다 훨씬 작다. 즉 그 동지가 21 일인지 22 일인지 우리 계산은 보증하지 못한다.

    그런데도 답이 안 바뀐다는 것은 아래 섭동 테스트가 따로 보인다.
    자정 여유가 없다는 사실과 결과가 흔들린다는 사실은 다른 이야기다.
    여기서는 전자를 사실대로 기록해 둔다.
    """
    tight = []
    for year in PROBE_YEARS:
        jde = astro.winter_solstice_jde(year - 1)
        for index in range(13):
            longitude = (270.0 + 30.0 * index) % 360.0
            jde = astro.solar_term_jde(longitude, jde + (0 if index == 0 else 30.44))
            margin = astro.minutes_from_midnight(jde)
            if margin < 15.0:
                tight.append((round(margin, 2), astro.kst_moment(jde)[0]))

    # 아슬아슬한 중기는 실제로 있다. 없다고 주장하지 않는다.
    assert tight, "자정에 가까운 중기가 하나도 없다. 계산을 의심할 것."
    assert (0.44, date(2025, 12, 22)) in [(m, d) for m, d in tight], (
        f"2025 동지의 자정 여유가 달라졌다. 관측된 목록: {sorted(tight)[:5]}"
    )


# ---------------------------------------------------------------------------
# 섭동 내성 — 실제 안전 여유
# ---------------------------------------------------------------------------


@pytest.fixture
def perturb(monkeypatch):
    """급수를 일부러 흔든 상태로 돌린다. 패치가 몇 번 불렸는지를 돌려준다.

    횟수를 세는 것이 요점이다. 섭동이 배선에서 끊기면 결과가 안 바뀌고, 안
    바뀌면 `assert not changed` 는 통과한다 — 급수가 견뎌낸 것과 섭동이 아예
    물리지 않은 것이 같은 초록으로 보인다. 그래서 "얼마나 흔들렸나"와 별개로
    "물리기는 했나"를 따로 물어야 한다.

    끊기는 방식은 추상적이지 않다. 이 픽스처는 astro 모듈의 이름을 갈아끼우고,
    astro.solar_term_jde 는 그 이름을 자기 전역에서 찾는다. 급수를 다른 모듈로
    옮기고 astro 가 재수출만 하면 그 조회가 옮겨간 모듈의 전역으로 바뀌므로,
    패치는 그대로 남고 아무도 읽지 않는다.

    두 축을 따로 세는 것은 어느 쪽 배선이 끊겼는지 바로 보이게 하기 위해서다.
    한쪽만 끊기는 경우가 실제로 있다 — new_moon_jde 는 astro 에 남고 태양
    황경만 옮기면 삭 쪽은 멀쩡하고 태양 쪽만 조용히 죽는다.
    """

    def apply(solar_degrees=0.0, lunar_seconds=0.0) -> dict:
        sun, moon = astro.apparent_solar_longitude, astro.new_moon_jde
        calls = {"sun": 0, "moon": 0}

        def patched_sun(jde):
            calls["sun"] += 1
            return (sun(jde) + solar_degrees) % 360.0

        def patched_moon(k):
            calls["moon"] += 1
            return moon(k) + lunar_seconds / 86400.0

        monkeypatch.setattr(astro, "apparent_solar_longitude", patched_sun)
        monkeypatch.setattr(astro, "new_moon_jde", patched_moon)
        return calls

    return apply


def _assert_perturbation_reached(calls, solar_degrees, lunar_seconds):
    """흔든 축의 패치가 실제로 불렸는지.

    흔들지 않은 축(0.0)은 묻지 않는다. 그 축의 패치도 불리기는 한다 — 파이프라인은
    태양 황경과 삭을 매번 둘 다 부르므로 실측하면 양쪽 다 0 이 아니다. 그래도
    단언에서 빼는 이유는, 이 케이스의 결론이 그 호출에 기대고 있지 않기 때문이다.
    단언은 "이 케이스의 판정이 믿을 만한가"만 물어야 한다. 흔들지 않은 축까지
    묶으면 파이프라인의 호출 구조라는 별개의 사실을 여기서 함께 주장하게 되고,
    그 구조가 정당하게 바뀌었을 때 섭동과 무관한 이유로 빨개진다.
    """
    if solar_degrees:
        assert calls["sun"] > 0, (
            "태양 황경 섭동이 파이프라인에 물리지 않았다 — "
            "astro.apparent_solar_longitude 를 갈아끼웠는데 한 번도 불리지 않았다.\n"
            "이 케이스의 결과는 급수가 견뎌서가 아니라 섭동이 도달하지 않아서 나온 것이다."
        )
    if lunar_seconds:
        assert calls["moon"] > 0, (
            "삭 시각 섭동이 파이프라인에 물리지 않았다 — "
            "astro.new_moon_jde 를 갈아끼웠는데 한 번도 불리지 않았다.\n"
            "이 케이스의 결과는 급수가 견뎌서가 아니라 섭동이 도달하지 않아서 나온 것이다."
        )


@pytest.mark.parametrize(
    "solar_degrees, lunar_seconds",
    [
        (SOLAR_PERTURBATION_DEGREES, 0),
        (-SOLAR_PERTURBATION_DEGREES, 0),
        (0, LUNAR_PERTURBATION_SECONDS),
        (0, -LUNAR_PERTURBATION_SECONDS),
    ],
)
def test_holidays_survive_perturbing_the_series(perturb, solar_degrees, lunar_seconds, request):
    """급수를 문헌 오차의 몇 배로 흔들어도 답이 그대로인가.

    이것이 실제 안전 여유다. 자정 여유가 좁은 자리가 있어도, 그 자리가 우리
    세 공휴일의 경계가 아니면 결과는 흔들리지 않는다.

    관측된 임계점(a172b6c 기준. PROBE_YEARS 전 구간, SPEC 3 종):
      태양 황경 -0.058° / +0.18° 까지 무변화. -0.06° 와 +0.19° 에서 첫 변화
      삭 시각   -740 초 / +1200 초까지 무변화. -750 초와 +1300 초에서 첫 변화

    커밋 SHA 를 적는다. 앞선 주석은 "2026-08-08 기준 ±0.1° 까지 무변화"였는데
    지금 실측은 -0.06° 에서 이미 바뀐다. 날짜만 적혀 있어 어느 리비전의 값인지
    알 수 없었고, 그래서 언제 어긋났는지도 추적되지 않았다. 값을 갱신할 때는
    SHA 를 같이 갈 것.

    마이너스 쪽이 얇다. -0.06° 는 이 테스트가 넣는 0.05° 의 1.2 배뿐이다.
    거기서 바뀌는 것은 (2033, chuseok) 하나로 2033-09-08 에서 2033-10-07 로
    한 달 밀린다 — 윤달 자리가 갈리는 자리다.

    여기가 빨개지면 급수를 늘릴 때가 된 것이다(VSOP87).
    lunar_holidays.yaml 의 open_questions 태양-황경-정밀도 참조.
    """
    baseline = _our_dates()
    calls = perturb(solar_degrees=solar_degrees, lunar_seconds=lunar_seconds)
    changed = {
        key: (baseline[key], value)
        for key, value in _our_dates().items()
        if value != baseline[key]
    }
    # 도달 여부를 먼저 본다. 배선이 끊겼으면 changed 는 어차피 비어 있고,
    # 그때 아래 단언이 먼저 통과해 버리면 원인이 가려진다.
    _assert_perturbation_reached(calls, solar_degrees, lunar_seconds)
    assert not changed, (
        f"섭동(태양 {solar_degrees:+}°, 삭 {lunar_seconds:+} 초)에서 "
        f"{len(changed)} 건이 바뀌었다:\n"
        + "\n".join(f"  {k}: {was} → {now}" for k, (was, now) in sorted(changed.items()))
    )


@pytest.mark.parametrize("solar_degrees", [SOLAR_CANARY_DEGREES, -SOLAR_CANARY_DEGREES])
def test_a_large_solar_perturbation_does_move_dates(perturb, solar_degrees):
    """크게 흔들면 반드시 바뀐다. 위 테스트의 초록이 무엇을 뜻하는지 확정한다.

    위 테스트의 단언은 `assert not changed` 하나다. 그 단언은 섭동이 배선에서
    끊겨도 통과하므로, 그것만으로는 "급수가 견뎠다"를 주장할 수 없다. 여기서
    반대 방향을 한 번 확인해 둔다 — 이만큼 흔들면 결과가 반드시 움직인다.

    둘을 같이 두면 초록의 뜻이 확정된다. 이 테스트가 빨개지면 섭동이 결과까지
    가지 못하는 것이고, 그렇다면 위 테스트의 초록은 아무것도 증명하지 않는다.

    건수는 박지 않는다. 임계점 근처가 아니라 한참 위(실측 -0.06° 의 80 배
    남짓)이므로, "비어 있지 않다"만 물으면 무관한 변경에 깨지지 않는다.
    건수를 박으면 그 순간 이 테스트가 임계점 기록이 되어 버린다 — 그건 위
    테스트의 docstring 이 할 일이다.
    """
    baseline = _our_dates()
    calls = perturb(solar_degrees=solar_degrees)
    changed = {
        key: (baseline[key], value)
        for key, value in _our_dates().items()
        if value != baseline[key]
    }
    _assert_perturbation_reached(calls, solar_degrees, 0)
    assert changed, (
        f"태양 황경을 {solar_degrees:+}° 흔들었는데 날짜가 하나도 안 바뀌었다.\n"
        "이 폭이면 반드시 바뀐다. 섭동이 파이프라인에 도달하지 않는다는 뜻이고,\n"
        "그렇다면 test_holidays_survive_perturbing_the_series 의 초록도 무의미하다."
    )


# ---------------------------------------------------------------------------
# 초하루 경계 위험 — 삭이 자정에 걸린 자리
# ---------------------------------------------------------------------------

# 1950~2100 전 구간 스캔 결과(조사 2026-08-08). 삭이 KST 자정에서 10 분 이내인
# 달에 걸린 공휴일이다. 값은 바꾸지 않았다 — 위험 표시일 뿐이다.
#
# 이 목록을 여기 박아 두는 이유는, 급수를 건드렸을 때 목록이 조용히 달라지는
# 것을 잡기 위해서다. 새 항목이 늘면 위태로운 자리가 생긴 것이고, 줄면 계산이
# 달라진 것이다. 둘 다 사람이 볼 일이다.
KNOWN_BOUNDARY_RISKS = {
    (1967, "buddhas_birthday"),
    (1970, "buddhas_birthday"),
    (1978, "seollal"),
    (1997, "seollal"),
    (2063, "buddhas_birthday"),
    (2092, "seollal"),
}

# 그중 이미 지나간 날짜. 발표값이 존재하므로 지금 당장 확인할 수 있다.
BOUNDARY_RISKS_ALREADY_PAST = {(1967, "buddhas_birthday"), (1970, "buddhas_birthday"),
                               (1978, "seollal"), (1997, "seollal")}


def test_boundary_risk_scan_matches_the_recorded_list():
    """1950~2100 스캔 결과가 기록된 목록과 같은지."""
    found = {(r.year, r.key) for r in hc.lunar_boundary_risks(1950, 2100)}
    assert found == KNOWN_BOUNDARY_RISKS, (
        "경계 위험 목록이 달라졌다.\n"
        f"  새로 생김: {sorted(found - KNOWN_BOUNDARY_RISKS)}\n"
        f"  사라짐   : {sorted(KNOWN_BOUNDARY_RISKS - found)}\n"
        "급수를 건드렸다면 어느 쪽이든 사람이 확인할 것."
    )


def test_the_verified_range_has_no_boundary_risk():
    """대조 완료 구간(2015~2028)에는 위태로운 자리가 없다.

    0 건이라는 사실 자체가 이 구간의 안전 근거다. 앵커 42 건이 맞았다는 것에
    더해, 그 42 건이 운으로 맞은 것이 아니라는 뜻이 된다. 삭이 전부 자정에서
    충분히 떨어져 있으므로 급수 오차가 날짜를 옮길 여지가 애초에 없었다.

    이 구간에 위험이 생기면 confirmed_through 를 그대로 두어도 되는지 다시
    판단해야 한다.
    """
    assert hc.lunar_boundary_risks(2015, 2028) == ()
    assert "해당 없음" in hc.lunar_boundary_report(2015, 2028)


def test_boundary_risk_reaches_the_holiday_and_its_leave_days():
    """위험 표시가 명절 당일에만 붙으면 연휴 이틀이 표시 없이 나간다.

    초하루가 밀리면 연휴 3 일이 통째로 따라 밀린다. 위험은 날짜 하나가 아니라
    그 달에 걸린 항목 전부의 성질이다.
    """
    risky = next(r for r in hc.lunar_boundary_risks(1950, 2100) if r.key == "seollal")
    for offset in (-1, 0, 1):
        found = hc._base_holidays(risky.year)[risky.day + timedelta(days=offset)]
        assert found and all(h.lunar_boundary_risk for h in found), (
            f"{risky.day + timedelta(days=offset)}: 위험 표시가 없다"
        )


def test_boundary_risk_does_not_move_any_date():
    """플래그는 표시일 뿐 값을 바꾸지 않는다.

    자동으로 옮기면 근거 없이 답이 달라지고 무엇을 왜 옮겼는지 남지 않는다.
    옮기는 것은 발표값이 있을 때 exceptions 가 할 일이다.
    """
    for risk in hc.lunar_boundary_risks(1950, 2100):
        month, day = SPEC[risk.key]
        assert risk.day == lunar.solar_date(risk.year, month, day)


def test_past_boundary_risks_are_checkable_now():
    """이미 지나간 위험 날짜는 발표값이 존재한다. 확인 대상으로 남겨 둔다.

    미래 날짜(2063·2092)는 기다릴 수밖에 없지만 과거 날짜는 지금 확인할 수 있다.
    확인해서 갈리면 exceptions 에 적을 것. 이 테스트는 그 목록이 잊히지 않게
    붙잡아 두는 자리다.
    """
    past = {(r.year, r.key) for r in hc.lunar_boundary_risks(1950, 2014)}
    assert past == BOUNDARY_RISKS_ALREADY_PAST
    assert all(year < 2015 for year, _ in past), "coverage 시작 이후 날짜가 섞였다"


# ---------------------------------------------------------------------------
# 시간대 감도 — 중국 음력 라이브러리를 쓰지 않은 이유
# ---------------------------------------------------------------------------


def test_utc8_would_give_different_dates_and_ours_is_the_verified_one(monkeypatch):
    """UTC+8 로 계산하면 갈리는 해가 실제로 있다.

    삭 시각이 KST 00:00~01:00 이면 UTC+8 로는 전날이 된다. 그러면 초하루가
    하루 밀리고 연휴 3 일이 통째로 밀린다.

    대조 구간 안에서 갈리는 해가 있고, 그 해에 우리 KST 값이 KASI 와 맞는다.
    그것이 이 선택의 실증이다. 갈리는 해가 없다면 시간대는 취향 문제였을 것이다.
    """
    baseline = _our_dates()
    monkeypatch.setattr(astro, "KST_OFFSET_DAYS", 8 / 24)
    china = _our_dates()

    diverging = {k: (baseline[k], china[k]) for k in baseline if baseline[k] != china[k]}
    assert diverging, (
        "UTC+8 로 바꿔도 아무것도 안 바뀐다. 시간대가 결과에 반영되지 않는다는 뜻이다."
    )

    anchors = _kasi_anchors()
    checked = [key for key in diverging if key in anchors]
    assert checked, (
        f"갈리는 해가 {sorted(diverging)} 인데 대조 구간 밖이라 어느 쪽이 맞는지 "
        "확인되지 않는다. 캐시를 넓히거나 이 테스트의 주장을 낮출 것."
    )

    for key in checked:
        ours, other = diverging[key]
        assert ours == anchors[key], f"{key}: 우리 {ours} / KASI {anchors[key]}"
        assert other != anchors[key], f"{key}: UTC+8 값도 KASI 와 같다. 대조가 성립 안 한다."
