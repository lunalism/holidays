"""KASI 파서. 캐시된 실제 응답으로 돌린다. API 를 부르지 않는다.

sources/kr/cache/ 의 원본 관측 기록이 곧 테스트 입력이다. 응답이 바뀌면 캐시를
갱신하게 되고, 그 diff 가 무엇이 달라졌는지 보여 준다.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from rules.kr import substitute_rules
from sources.kr import kasi_parser as kp

CACHE_2026 = Path(__file__).parent.parent / "sources" / "kr" / "cache" / "getRestDeInfo_2026.xml"

pytestmark = pytest.mark.skipif(
    not CACHE_2026.exists(),
    reason="캐시된 2026 응답이 없다. sources.kr.kasi_client 로 먼저 받을 것.",
)


def _parsed():
    return kp.parse(CACHE_2026.read_text(encoding="utf-8"))


def test_parses_the_cached_response():
    holidays = _parsed()
    assert len(holidays) == 22  # 응답의 totalCount
    assert holidays[0].date == date(2026, 1, 1)
    assert holidays[-1].date == date(2026, 12, 25)


def test_keys_exist_in_the_holiday_registry():
    """매핑 표의 키가 규칙 테이블의 정본 목록과 어긋나지 않는지.

    오타 하나면 그 공휴일이 조용히 대조에서 빠진다.
    """
    registry = set(substitute_rules.load().holidays)
    for holiday in _parsed():
        if holiday.key is None:
            continue
        assert holiday.key in registry, f"{holiday.name}: 레지스트리에 없는 키 {holiday.key!r}"


def test_locdate_is_the_key_and_seq_is_ignored():
    """seq 는 읽지 않는다. 의미를 모르는 값을 계산에 끌어들이지 않는다."""
    assert not hasattr(kp.KasiHoliday, "seq")
    assert "seq" not in kp.KasiHoliday.__dataclass_fields__

    # locdate 가 유일 키다. 2026 년 응답에는 같은 날짜가 겹치지 않는다.
    dates = [h.date for h in _parsed()]
    assert len(dates) == len(set(dates))


def test_substitute_cause_is_preserved_separately():
    """괄호 안 원인 공휴일은 별도 필드로 남는다. 이름 자체에는 섞지 않는다."""
    substitutes = {h.date: h for h in _parsed() if h.is_substitute}
    assert set(substitutes) == {
        date(2026, 3, 2),
        date(2026, 5, 25),
        date(2026, 8, 17),
        date(2026, 10, 5),
    }

    aug = substitutes[date(2026, 8, 17)]
    assert aug.name == "대체공휴일(광복절)"
    assert aug.caused_by_name == "광복절"
    assert aug.key is None  # 대체공휴일 자체는 레지스트리의 공휴일이 아니다


def test_unmapped_name_raises_instead_of_being_skipped():
    """모르는 이름을 만나면 터뜨린다.

    건너뛰면 KASI 가 추가한 공휴일을 놓치고, 놓친 것은 오류로 드러나지 않는다.
    """
    xml = (
        '<response><header><resultCode>00</resultCode></header><body><items>'
        "<item><dateName>새로운공휴일</dateName><locdate>20260401</locdate></item>"
        "</items><totalCount>1</totalCount></body></response>"
    )
    with pytest.raises(kp.UnmappedHolidayName) as exc:
        kp.parse(xml)
    assert "새로운공휴일" in str(exc.value)


def test_unmapped_substitute_cause_also_raises():
    """대체공휴일의 원인 공휴일이 표에 없어도 터뜨린다.

    원인 쪽이 매핑되어 있지 않으면 교차검증이 성립하지 않는다.
    """
    xml = (
        '<response><header><resultCode>00</resultCode></header><body><items>'
        "<item><dateName>대체공휴일(없는날)</dateName><locdate>20260401</locdate></item>"
        "</items><totalCount>1</totalCount></body></response>"
    )
    with pytest.raises(kp.UnmappedHolidayName):
        kp.parse(xml)


def test_error_response_is_rejected():
    xml = '<response><header><resultCode>30</resultCode></header></response>'
    with pytest.raises(kp.KasiParseError):
        kp.parse(xml)


def test_truncated_page_is_rejected():
    """totalCount 와 항목 수가 다르면 페이지네이션에 걸린 것이다."""
    xml = (
        '<response><header><resultCode>00</resultCode></header><body><items>'
        "<item><dateName>어린이날</dateName><locdate>20260505</locdate></item>"
        "</items><totalCount>2</totalCount></body></response>"
    )
    with pytest.raises(kp.KasiParseError, match="totalCount"):
        kp.parse(xml)


def test_lunar_dates_confirmed_by_the_api():
    """정답 픽스처의 음력 날짜가 API 관측과 맞는지.

    이 대조가 설날·추석 케이스의 verified: true 근거다.
    음력 환산 구현 자체는 아직 없고, 여기서는 날짜 사실만 확인한다.
    """
    by_date = {h.date: h.name for h in _parsed()}
    for day in (date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18)):
        assert by_date.get(day) == "설날", f"{day} 가 설날 연휴가 아니다"
    for day in (date(2026, 9, 24), date(2026, 9, 25), date(2026, 9, 26)):
        assert by_date.get(day) == "추석", f"{day} 가 추석 연휴가 아니다"

    # 경계. 연휴 바로 다음날은 없어야 한다.
    assert date(2026, 2, 19) not in by_date
    assert date(2026, 9, 27) not in by_date
