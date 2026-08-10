"""core/ics.py + rules/kr/feed.py — 발행되는 .ics 가 약속대로 나오는가.

UID 와 결정성에 무게를 둔다. 둘 다 한 번 틀리면 되돌릴 수 없는 종류다.
UID 가 바뀌면 구독자 캘린더에 중복이 생기고, 발행된 .ics 는 회수할 수 없다.

시계를 읽지 않는다. today 와 dtstamp 를 전부 고정값으로 넘긴다.
그게 가능하다는 것 자체가 이 설계의 요점이다(core/ics.py 의 DTSTAMP 참조).
"""

from __future__ import annotations

import datetime as dt
import re

import pytest

from core import ics
from rules.kr import feed
from rules.kr import holiday_calendar as hc

TODAY = dt.date(2026, 8, 10)
DTSTAMP = dt.datetime(2026, 8, 10, 0, 0, 0, tzinfo=dt.UTC)


def _build(today=TODAY, dtstamp=DTSTAMP) -> str:
    return feed.build(today=today, dtstamp=dtstamp).decode("utf-8")


def _unfold(text: str) -> str:
    """RFC 5545 의 접힌 줄을 편다. 속성값을 문자열로 찾으려면 먼저 펴야 한다."""
    return text.replace("\r\n ", "").replace("\n ", "")


def _events(text: str) -> list:
    return re.findall(r"BEGIN:VEVENT.*?END:VEVENT", _unfold(text), re.S)


def _on(text: str, yyyymmdd: str) -> list:
    """그 날짜에서 시작하는 이벤트 블록들."""
    return [b for b in _events(text) if f"DTSTART;VALUE=DATE:{yyyymmdd}" in b]


def _prop(block: str, name: str) -> str:
    match = re.search(rf"^{name}:(.*)$", block, re.M)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# 결정성
# ---------------------------------------------------------------------------


def test_the_same_input_produces_byte_identical_output():
    """같은 입력으로 두 번 생성하면 바이트가 같다.

    DTSTAMP 를 인자로 받기 때문에 성립한다. 안에서 시계를 읽었다면 이 테스트는
    쓸 수 없고, 내용이 안 바뀐 재발행에도 diff 가 떠서 무엇이 실제로 바뀌었는지
    볼 수 없게 된다.
    """
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


def test_dtstamp_is_an_input_not_a_clock_read():
    """DTSTAMP 가 정말 인자로만 정해지는지.

    위 테스트는 "두 번 같다"만 본다. 시계를 읽으면서 우연히 같은 초에 두 번
    돌았어도 통과한다. 다른 값을 주면 출력이 달라진다는 것까지 봐야 인자가
    실제로 쓰인다는 것이 확인된다.
    """
    other = dt.datetime(2027, 1, 1, tzinfo=dt.UTC)
    assert feed.build(today=TODAY, dtstamp=other) != feed.build(today=TODAY, dtstamp=DTSTAMP)
    assert "DTSTAMP:20270101T000000Z" in _build(dtstamp=other)


def test_a_naive_dtstamp_is_rejected():
    """타임존 없는 dtstamp 는 거부한다. DTSTAMP 는 UTC 여야 한다."""
    with pytest.raises(ics.IcsError, match="타임존"):
        feed.build(today=TODAY, dtstamp=dt.datetime(2026, 8, 10))


# ---------------------------------------------------------------------------
# UID
# ---------------------------------------------------------------------------


def test_overlapping_holidays_become_two_events_with_distinct_uids():
    """2025-05-05 어린이날 + 부처님오신날 → 이벤트 2 개, UID 가 다르다."""
    blocks = _on(_build(), "20250505")
    assert len(blocks) == 2, f"이벤트가 {len(blocks)} 개다"

    uids = [_prop(b, "UID") for b in blocks]
    assert len(set(uids)) == 2, f"UID 가 겹친다: {uids}"
    assert set(uids) == {
        "20250505-1@holidays.lunalism.com",
        "20250505-2@holidays.lunalism.com",
    }

    summaries = {_prop(b, "SUMMARY") for b in blocks}
    assert summaries == {"어린이날", "부처님오신날"}


def test_every_uid_in_the_feed_is_unique():
    """피드 전체에서 UID 가 하나도 겹치지 않는지. 겹치면 캘린더가 덮어쓴다."""
    uids = [_prop(b, "UID") for b in _events(_build())]
    dupes = {u for u in uids if uids.count(u) > 1}
    assert not dupes, f"중복 UID: {sorted(dupes)}"


def test_seq_does_not_follow_the_order_the_calendar_returned():
    """seq 는 order_key 순이지 holidays_on() 이 준 순서가 아니다.

    holidays_on() 은 표를 읽은 순서로 쌓는다. 2025-05-05 에서는 양력 표의
    어린이날이 음력 표의 부처님오신날보다 먼저 나온다. 그 순서를 그대로 쓰면
    누가 YAML 줄 순서를 바꿨을 때 UID 가 조용히 뒤바뀐다.

    order_key 는 (key, source_key, name) 이므로 buddhas_birthday <
    childrens_day 가 되어 순서가 뒤집힌다. 그 뒤집힘이 바로 "표 순서를 쓰지
    않았다"는 증거다.
    """
    returned = [h.name for h in hc.holidays_on(dt.date(2025, 5, 5))]
    assert returned == ["어린이날", "부처님오신날"], "전제가 바뀌었다. 이 테스트를 다시 볼 것."

    blocks = _on(_build(), "20250505")
    by_uid = {_prop(b, "UID"): _prop(b, "SUMMARY") for b in blocks}
    assert by_uid["20250505-1@holidays.lunalism.com"] == "부처님오신날"
    assert by_uid["20250505-2@holidays.lunalism.com"] == "어린이날"


def test_the_uid_does_not_carry_the_kind():
    """UID 에 kind 가 들어 있지 않은지.

    kind 는 우리 판정 결과다. open_questions 가 풀리면 어떤 항목의 kind 가
    바뀔 수 있고, kind 가 UID 에 있으면 그 판정 변경이 구독자 캘린더에서
    이벤트 삭제 + 생성으로 나타난다. SEQUENCE 로 수습되지 않는다.
    """
    for block in _events(_build()):
        uid = _prop(block, "UID")
        assert re.fullmatch(r"\d{8}-\d+@holidays\.lunalism\.com", uid), uid
        for kind in ("statutory", "substitute", "temporary", "election"):
            assert kind not in uid, uid


def test_seq_runs_across_the_whole_day_not_per_kind():
    """seq 는 그 날 전체 순번이다. kind 별로 세면 같은 UID 가 두 번 나온다.

    지금 달력에는 한 날짜에 kind 가 섞이는 자리가 없다(2020~2035 전수 확인).
    그래서 실제 피드로는 이 규칙을 확인할 수 없고, Event 를 직접 지어 본다.
    """
    day = dt.date(2030, 3, 1)
    substitute = ics.Event(
        day=day, summary="대체공휴일", kind="substitute", order_key=("", "z", "대")
    )
    statutory = ics.Event(
        day=day, summary="삼일절", kind="statutory", order_key=("samiljeol", "", "삼")
    )
    made = ics.assign_uids([substitute, statutory])
    uids = [uid for _, uid in made]
    assert uids == [
        "20300301-1@holidays.lunalism.com",
        "20300301-2@holidays.lunalism.com",
    ], uids
    assert len(set(uids)) == 2


def test_a_tie_in_order_key_is_an_error_not_a_coin_flip():
    """order_key 가 겹치면 seq 를 임의로 고르지 않고 멈춘다.

    임의로 고르면 그 선택이 다음 실행에서 뒤집힐 수 있고, 뒤집히는 순간
    UID 가 바뀐다. 그건 조용히 넘어가면 안 되는 종류다.
    """
    same = dict(day=dt.date(2030, 1, 1), kind="statutory", order_key=("k", "", "이름"))
    with pytest.raises(ics.IcsError, match="order_key"):
        ics.assign_uids([ics.Event(summary="가", **same), ics.Event(summary="나", **same)])


# ---------------------------------------------------------------------------
# 이벤트 내용
# ---------------------------------------------------------------------------


def test_a_substitute_holiday_summary_is_just_the_generic_name():
    """2027-02-09 대체공휴일의 SUMMARY 는 "대체공휴일" 이다.

    원인 공휴일명을 붙이지 않는다. source_key 는 겹침 사례에서 확정된 트리거가
    아니다(substitute_holidays.yaml 의 3호-귀속-불명).
    """
    blocks = _on(_build(), "20270209")
    assert len(blocks) == 1
    assert _prop(blocks[0], "SUMMARY") == "대체공휴일"
    assert "설날" not in blocks[0], "원인 공휴일명이 새어 나왔다"


def test_a_substitute_description_cites_the_decree_number():
    """대체공휴일 DESCRIPTION 은 ruleset 호수에서 온다."""
    block = _on(_build(), "20270209")[0]
    assert _prop(block, "DESCRIPTION") == (
        "「관공서의 공휴일에 관한 규정」(대통령령 제36290호)에 따른 대체공휴일."
    )


def test_a_statutory_holiday_has_no_description():
    """법정공휴일에는 근거를 적지 않는다. 표에 조문 대응이 없기 때문이다."""
    block = _on(_build(), "20260815")[0]
    assert _prop(block, "SUMMARY") == "광복절"
    assert "DESCRIPTION" not in block


def test_a_temporary_holiday_description_carries_its_source():
    """2015-08-14 임시공휴일의 DESCRIPTION 에 근거가 있다.

    발행 범위(2020-01-01~) 밖이라 build() 결과에는 없다. 근거를 싣는 규칙 자체는
    범위와 무관하므로 events() 를 직접 불러 확인한다.
    """
    published = _on(_build(), "20150814")
    assert not published, "하한이 2020-01-01 인데 2015 년 이벤트가 실렸다"

    found = feed.events(dt.date(2015, 8, 14), dt.date(2015, 8, 14))
    assert len(found) == 1
    assert found[0].kind == "temporary"
    assert found[0].description == (
        "근거: 2015-08-11 국무회의 의결 "
        "(광복 70주년 계기 국민 사기 진작 방안, 2015-08-04 확정 / 외교부 공지로 교차 확인)"
    )


def test_a_designated_holiday_without_a_source_gets_no_description():
    """근거가 비어 있으면 DESCRIPTION 을 넣지 않는다. 추측으로 채우지 않는다.

    2024-10-01 임시공휴일이 그 경우다(designated_holidays.yaml 의 source 가 비어
    있고 source_todo 만 있다). source_todo 를 근거처럼 내보내면 미확인 사항이
    구독자에게 근거로 읽힌다.
    """
    block = _on(_build(), "20241001")[0]
    assert _prop(block, "SUMMARY") == "임시공휴일"
    assert "DESCRIPTION" not in block


def test_kasi_is_never_cited_as_a_source():
    """피드 어디에도 KASI 가 근거로 나오지 않는다.

    KASI 는 대조 상대이지 채택 소스가 아니다. 특히 2015-08-14 의 note 에는
    KASI 대조 결과가 들어 있어 근거 필드를 잘못 고르면 그대로 새어 나간다.
    """
    text = _build()
    for word in ("KASI", "천문연구원", "특일정보"):
        assert word not in text, f"{word!r} 가 피드에 들어 있다"

    for event in feed.events(dt.date(2015, 1, 1), dt.date(2015, 12, 31)):
        assert "KASI" not in event.description


# ---------------------------------------------------------------------------
# 잠정 구간
# ---------------------------------------------------------------------------


def test_dates_past_the_confirmed_range_are_marked_tentative():
    """2029 년 이후는 STATUS:TENTATIVE 가 붙는다. 규칙 확정은 2028-12-31 까지다."""
    block = _on(_build(), "20290101")[0]
    assert _prop(block, "STATUS") == "TENTATIVE"
    assert _prop(block, "X-HOLIDAY-STATUS") == "PROVISIONAL"


def test_dates_inside_the_confirmed_range_are_not_marked():
    """2028 년까지는 표시가 없다. 경계 바로 앞뒤로 확인한다."""
    for yyyymmdd in ("20281225", "20260815"):
        block = _on(_build(), yyyymmdd)[0]
        assert "STATUS:TENTATIVE" not in block, yyyymmdd
        assert "X-HOLIDAY-STATUS" not in block, yyyymmdd


def test_the_provisional_marker_never_leaks_into_description_or_summary():
    """잠정은 STATUS 로만 나간다. 사람이 읽는 문구에 섞지 않는다."""
    for block in _events(_build()):
        for word in ("잠정", "PROVISIONAL", "미확인", "미검증"):
            assert word not in _prop(block, "SUMMARY"), block
            if word != "PROVISIONAL":  # X-HOLIDAY-STATUS 는 별도 속성이라 제외
                assert word not in _prop(block, "DESCRIPTION"), block


# ---------------------------------------------------------------------------
# 캘린더 헤더와 범위
# ---------------------------------------------------------------------------


def test_the_calendar_header_is_complete():
    text = _unfold(_build())
    for line in (
        "VERSION:2.0",
        "PRODID:-//lunalism//holidays.lunalism.com//KO",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:대한민국 공휴일",
        "X-WR-TIMEZONE:Asia/Seoul",
    ):
        assert line in text, line


def test_events_are_all_day_with_an_exclusive_end():
    """DTSTART 는 VALUE=DATE, DTEND 는 다음 날이다."""
    for block in _events(_build()):
        start = re.search(r"DTSTART;VALUE=DATE:(\d{8})", block).group(1)
        end = re.search(r"DTEND;VALUE=DATE:(\d{8})", block).group(1)
        parsed = dt.datetime.strptime(start, "%Y%m%d").date()
        assert end == (parsed + dt.timedelta(days=1)).strftime("%Y%m%d")


def test_every_event_is_free_and_sequence_zero():
    for block in _events(_build()):
        assert _prop(block, "TRANSP") == "TRANSPARENT"
        assert _prop(block, "X-MICROSOFT-CDO-BUSYSTATUS") == "FREE"
        assert _prop(block, "SEQUENCE") == "0"


def test_the_range_is_2020_through_five_years_out():
    assert feed.feed_range(TODAY) == (dt.date(2020, 1, 1), dt.date(2031, 12, 31))
    assert feed.feed_range(dt.date(2030, 3, 2)) == (dt.date(2020, 1, 1), dt.date(2035, 12, 31))

    days = sorted(
        re.search(r"DTSTART;VALUE=DATE:(\d{8})", b).group(1) for b in _events(_build())
    )
    assert days[0].startswith("2020"), days[0]
    assert days[-1].startswith("2031"), days[-1]


def test_the_upper_bound_follows_the_given_today():
    """상한이 today 를 실제로 따라가는지. 고정값이면 이 테스트가 깨진다."""
    later = _build(today=dt.date(2030, 3, 2))
    days = sorted(re.search(r"DTSTART;VALUE=DATE:(\d{8})", b).group(1) for b in _events(later))
    assert days[-1].startswith("2035"), days[-1]
