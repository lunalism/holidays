"""core/ics.py + rules/kr/feed.py — 발행되는 .ics 가 약속대로 나오는가.

UID 와 결정성에 무게를 둔다. 둘 다 한 번 틀리면 되돌릴 수 없는 종류다.
UID 가 바뀌면 구독자 캘린더에 중복이 생기고, 발행된 .ics 는 회수할 수 없다.

시계를 읽지 않는다. today 와 dtstamp 를 전부 고정값으로 넘긴다.
그게 가능하다는 것 자체가 이 설계의 요점이다(core/ics.py 의 DTSTAMP 참조).
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import pytest
from icalendar import Calendar

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
        "20250505-buddhas_birthday@holidays.lunalism.com",
        "20250505-childrens_day@holidays.lunalism.com",
    }

    summaries = {_prop(b, "SUMMARY") for b in blocks}
    assert summaries == {"어린이날", "부처님오신날"}


def test_every_uid_in_the_feed_is_unique():
    """피드 전체에서 UID 가 하나도 겹치지 않는지. 겹치면 캘린더가 덮어쓴다."""
    uids = [_prop(b, "UID") for b in _events(_build())]
    dupes = {u for u in uids if uids.count(u) > 1}
    assert not dupes, f"중복 UID: {sorted(dupes)}"


def test_the_uid_token_comes_from_the_holiday_key():
    """key 가 있으면 UID 에 key 가 그대로 들어간다.

    holidays_on() 이 준 순서와도, 그 날 몇 번째인지와도 무관하다.
    2025-05-05 은 양력 표의 어린이날이 음력 표의 부처님오신날보다 먼저 나오는데
    UID 는 그 순서를 전혀 반영하지 않는다.
    """
    returned = [h.name for h in hc.holidays_on(dt.date(2025, 5, 5))]
    assert returned == ["어린이날", "부처님오신날"], "전제가 바뀌었다. 이 테스트를 다시 볼 것."

    by_uid = {_prop(b, "UID"): _prop(b, "SUMMARY") for b in _on(_build(), "20250505")}
    assert by_uid["20250505-childrens_day@holidays.lunalism.com"] == "어린이날"
    assert by_uid["20250505-buddhas_birthday@holidays.lunalism.com"] == "부처님오신날"


def test_designated_holidays_use_their_uid_token():
    """key 가 없는 지정 공휴일은 designated_holidays.yaml 의 uid_token 을 쓴다."""
    text = _build()
    assert (
        _prop(_on(text, "20260603")[0], "UID")
        == "20260603-local_election@holidays.lunalism.com"
    )
    assert (
        _prop(_on(text, "20250127")[0], "UID")
        == "20250127-cabinet_designated@holidays.lunalism.com"
    )
    # 2015-08-14 은 발행 범위 밖이라 events() 로 직접 본다.
    (liberation,) = feed.events(dt.date(2015, 8, 14), dt.date(2015, 8, 14))
    assert liberation.token == "liberation_70th"


def test_only_substitutes_still_take_their_token_from_kind():
    """대체공휴일만 kind 에서 token 이 나온다. 나머지 약어는 전부 지웠다."""
    assert feed._KIND_ABBREV == {"substitute": "sub"}
    assert _prop(_on(_build(), "20270209")[0], "UID") == "20270209-sub@holidays.lunalism.com"


def test_the_uid_carries_no_positional_number_and_no_kind():
    """UID 가 위치에도 kind 에도 기대지 않는지.

    전에는 UID 문자열에 'temporary'/'election' 이 없는지만 봤다. 그때 구현은
    약어 tmp/elc 를 쓰고 있었으므로 그 검사는 통과하면서도 kind 의존을 놓쳤다.
    이름만 보고 안심하게 만드는 테스트였다.

    이제 실제로 확인한다 — kind 만 바꾼 같은 항목이 같은 token 을 내는가.
    """
    for block in _events(_build()):
        uid = _prop(block, "UID")
        token = uid.split("@")[0].split("-", 1)[1]
        assert not token.isdigit(), f"위치 기반 순번으로 보인다: {uid}"

    # kind 만 다르고 나머지가 같은 항목 둘. token 이 같아야 한다.
    base = dict(name="임시공휴일", key="", source_key="", uid_token="liberation_70th")
    as_temporary = feed._token(_FakeHoliday(kind="temporary", **base))
    as_election = feed._token(_FakeHoliday(kind="election", **base))
    assert as_temporary == as_election == "liberation_70th"


def test_reclassifying_2025_06_03_does_not_change_its_uid():
    """2025-06-03 을 temporary 에서 election 으로 바꿔도 UID 가 그대로인지.

    designated_holidays.yaml 의 선거일-kind-판정 이 실제로 이 항목을 가리킨다.
    제21대 대통령선거일인데 궐위 선거라 지금은 temporary 로 두었고, 그 해석이
    정정되면 election 이 된다. 그때 UID 가 바뀌면 구독자 캘린더에서 이벤트가
    지워졌다가 새로 생긴다.

    uid_token 이 'presidential_election' 인 이유가 이것이다 — 우리 분류가
    아니라 그날 있었던 일을 가리킨다.
    """
    day = dt.date(2025, 6, 3)
    (real,) = feed.events(day, day)
    assert real.kind == "temporary", "전제가 바뀌었다. 이 테스트를 다시 볼 것."
    assert real.token == "presidential_election"

    reclassified = feed._event(
        day,
        _FakeHoliday(
            name="제21대 대통령선거",
            kind="election",
            uid_token="presidential_election",
        ),
        provisional=False,
    )
    assert reclassified.token == real.token
    assert ics.assign_uids([reclassified])[0][1] == ics.assign_uids([real])[0][1]
    assert ics.assign_uids([real])[0][1] == (
        "20250603-presidential_election@holidays.lunalism.com"
    )


def test_a_duplicate_token_on_one_day_is_an_error():
    """같은 날 token 이 겹치면 멈춘다. 넘어가면 공휴일 하나가 덮여 사라진다."""
    same = dict(day=dt.date(2030, 1, 1), kind="statutory", token="dup")
    with pytest.raises(ics.IcsError, match="token 이 겹쳐"):
        ics.assign_uids([ics.Event(summary="가", **same), ics.Event(summary="나", **same)])


def test_an_empty_token_is_an_error():
    """token 이 비면 UID 가 날짜만 남는다. 그것도 멈춘다."""
    with pytest.raises(ics.IcsError, match="token 이 빈"):
        ics.assign_uids([ics.Event(day=dt.date(2030, 1, 1), summary="가", kind="statutory")])


class _FakeHoliday:
    """Holiday 처럼 생긴 것. 달력이 만들어 주지 않는 상황을 지어내기 위한 것이다.

    실제 달력에는 같은 날 대체공휴일이 둘인 자리도, 임시공휴일이 둘인 자리도
    없다(2020~2035 전수 확인). 그래서 충돌 경로는 지어내지 않으면 밟을 수 없다.
    """

    def __init__(self, name="무언가", kind="temporary", key="", source_key="", uid_token=""):
        self.name = name
        self.kind = kind
        self.key = key
        self.source_key = source_key
        self.uid_token = uid_token


def _collision_message(day, holidays) -> str:
    """feed 의 실제 Event 생성 경로를 태워서 충돌을 일으키고 메시지를 돌려준다."""
    events = [feed._event(day, h, provisional=False) for h in holidays]
    with pytest.raises(ics.IcsError) as exc:
        ics.assign_uids(events)
    return str(exc.value)


def test_two_substitutes_on_one_day_report_what_collided():
    """같은 날 대체공휴일 2 건 → IcsError, 메시지에 무엇이 부딪혔는지 다 나온다.

    이 경우가 가장 알아보기 어렵다. name 과 kind 가 똑같고 source_key 만 다르다.
    token 목록만 찍으면 ['sub', 'sub'] 라 어느 데이터를 봐야 할지 알 수 없다.
    """
    day = dt.date(2025, 5, 6)
    message = _collision_message(
        day,
        [
            _FakeHoliday("대체공휴일", "substitute", source_key="childrens_day"),
            _FakeHoliday("대체공휴일", "substitute", source_key="buddhas_birthday"),
        ],
    )

    assert "2025-05-06" in message
    assert "sub" in message
    assert message.count("name='대체공휴일'") == 2
    assert message.count("kind='substitute'") == 2
    assert "source_key='childrens_day'" in message
    assert "source_key='buddhas_birthday'" in message
    assert "key=''" in message

    assert "같은 날 같은 token 은 자동 구분하지 않는다." in message
    assert "데이터 입력 오류인지 확인하고, 실제로 별개 공휴일이라면" in message
    assert "UID 규칙을 사람이 결정해야 한다." in message


def test_two_temporary_holidays_on_one_day_report_what_collided():
    """같은 날 임시공휴일 2 건도 같다. 여기서는 uid_token 이 같아야 부딪힌다."""
    day = dt.date(2025, 1, 27)
    message = _collision_message(
        day,
        [
            _FakeHoliday("임시공휴일", "temporary", uid_token="cabinet_designated"),
            _FakeHoliday("임시공휴일(가칭)", "temporary", uid_token="cabinet_designated"),
        ],
    )

    assert "2025-01-27" in message
    assert "cabinet_designated" in message
    assert "name='임시공휴일'" in message
    assert "name='임시공휴일(가칭)'" in message
    assert message.count("kind='temporary'") == 2
    assert "같은 날 같은 token 은 자동 구분하지 않는다." in message
    assert "UID 규칙을 사람이 결정해야 한다." in message


def test_the_collision_message_only_lists_the_clashing_items():
    """충돌하지 않은 항목까지 늘어놓지 않는다. 봐야 할 것만 남긴다."""
    day = dt.date(2025, 5, 6)
    message = _collision_message(
        day,
        [
            _FakeHoliday("어린이날", "statutory", key="childrens_day"),
            _FakeHoliday("대체공휴일", "substitute", source_key="a"),
            _FakeHoliday("대체공휴일", "substitute", source_key="b"),
        ],
    )
    assert "어린이날" not in message
    assert message.count("kind='substitute'") == 2


def test_a_non_substitute_without_key_or_uid_token_is_an_error():
    """key 도 uid_token 도 없는 non-substitute 는 지어내지 않고 터진다."""
    with pytest.raises(ics.IcsError, match="UID token 을 정할 수 없다"):
        feed._token(_FakeHoliday(name="무언가", kind="brand_new_kind"))

    # temporary 도 예외가 아니다. 약어 폴백을 지웠으므로 uid_token 이 필수다.
    with pytest.raises(ics.IcsError, match="UID token 을 정할 수 없다"):
        feed._token(_FakeHoliday(name="임시공휴일", kind="temporary"))


# ---------------------------------------------------------------------------
# designated_holidays.yaml 의 uid_token 검증 — 로드 시점에 막는다
#
# 발행 시점이 아니라 로드 시점이어야 한다. 발행까지 가면 잘못된 UID 로 파일이
# 이미 만들어진 뒤이고, 그 파일이 나가면 되돌릴 수 없다.
# ---------------------------------------------------------------------------


def _entry(day, name="임시공휴일", kind="temporary", **extra):
    return {"date": day, "name": name, "kind": kind, **extra}


def _load_designated(entries):
    """_designated() 의 검증을 임의 항목으로 태운다. 실제 YAML 은 건드리지 않는다."""
    raw = {
        "kinds": {"temporary": {}, "election": {}},
        "holidays": entries,
    }
    hc._designated.cache_clear()
    hc._designated_raw.cache_clear()
    original = hc._designated_raw
    hc._designated_raw = lambda: raw
    try:
        return hc._designated()
    finally:
        hc._designated_raw = original
        hc._designated.cache_clear()
        hc._designated_raw.cache_clear()


@pytest.mark.parametrize("token", ["temporary", "election", "tmp", "elc", "ELECTION", "Tmp"])
def test_a_forbidden_uid_token_is_rejected_at_load_time(token):
    """kind 이름과 그 약어는 uid_token 이 될 수 없다. 대소문자도 가리지 않는다.

    kind 는 우리 판정 결과라 정정될 수 있고, kind 에서 유도한 token 을 쓰면
    그 정정이 곧 UID 변경이 된다. 그게 이 규칙이 있는 이유다.
    """
    with pytest.raises(hc.CalendarError, match="쓸 수 없다"):
        _load_designated([_entry(dt.date(2030, 1, 1), uid_token=token)])


@pytest.mark.parametrize("token", ["Liberation", "70th_liberation", "has-dash", "has space", "_x"])
def test_a_malformed_uid_token_is_rejected_at_load_time(token):
    """소문자로 시작하는 [a-z0-9_] 만 받는다. UID 에 그대로 실리는 값이다."""
    with pytest.raises(hc.CalendarError, match="형식에 맞지 않는다"):
        _load_designated([_entry(dt.date(2030, 1, 1), uid_token=token)])


def test_a_missing_uid_token_is_rejected_at_load_time():
    """지정 공휴일에는 uid_token 이 필수다. key 가 없으므로 대신할 것이 없다."""
    with pytest.raises(hc.CalendarError, match="uid_token 이 없다"):
        _load_designated([_entry(dt.date(2030, 1, 1))])


def test_two_entries_on_one_day_may_not_share_a_uid_token():
    """같은 날 uid_token 이 겹치면 로드 시점에 막는다. UID 가 같아진다."""
    with pytest.raises(hc.CalendarError, match="uid_token 이 겹친다"):
        _load_designated(
            [
                _entry(dt.date(2030, 1, 1), name="가", uid_token="cabinet_designated"),
                _entry(dt.date(2030, 1, 1), name="나", uid_token="cabinet_designated"),
            ]
        )


def test_the_same_token_on_different_days_is_fine():
    """다른 날이면 같은 token 을 써도 된다. 날짜가 UID 를 갈라 준다.

    cabinet_designated 5 건이 실제로 그렇다.
    """
    loaded = _load_designated(
        [
            _entry(dt.date(2030, 1, 1), uid_token="cabinet_designated"),
            _entry(dt.date(2030, 2, 2), uid_token="cabinet_designated"),
        ]
    )
    assert len(loaded["by_date"]) == 2


def test_the_real_table_has_a_uid_token_on_every_entry():
    """실제 표 17 건이 전부 검증을 통과하고 금지값을 쓰지 않는지."""
    entries = [e for day in hc._designated()["by_date"].values() for e in day]
    assert len(entries) == 17
    for entry in entries:
        token = entry["uid_token"]
        assert token
        assert token.lower() not in {"temporary", "election", "tmp", "elc"}
        assert re.fullmatch(r"[a-z][a-z0-9_]*", token), token


# ---------------------------------------------------------------------------
# UID 안정성 — 같은 날 항목이 늘고 줄어도 남의 UID 가 밀리지 않는가
# ---------------------------------------------------------------------------


def _uids_by_summary(events) -> dict:
    return {event.summary: uid for event, uid in ics.assign_uids(events)}


def test_adding_or_removing_a_sibling_never_moves_another_uid():
    """같은 날에 항목을 앞·중간·뒤로 넣고 빼도 나머지 UID 가 전부 그대로인지.

    이것이 위치 기반 순번을 버린 이유다. 순번이었다면 앞에 하나 끼우는 것만으로
    뒤 항목들의 UID 가 전부 밀리고, 구독자 캘린더에서는 손대지 않은 공휴일이
    지워졌다가 새로 생긴 것으로 보인다.

    임시공휴일이 기존 공휴일과 같은 날 지정되면 실제로 밟히는 경로다.
    """
    day = dt.date(2030, 5, 5)

    def event(summary, token):
        return ics.Event(day=day, summary=summary, kind="statutory", token=token)

    base = [event("중간", "mmm"), event("끝", "zzz")]
    baseline = _uids_by_summary(base)
    assert baseline == {
        "중간": "20300505-mmm@holidays.lunalism.com",
        "끝": "20300505-zzz@holidays.lunalism.com",
    }

    # 앞 / 중간 / 뒤 어디에 끼워도 기존 둘은 그대로여야 한다.
    for label, token in (("맨앞", "aaa"), ("사이", "ppp"), ("맨뒤", "zzzz")):
        grown = _uids_by_summary([*base, event(label, token)])
        for summary, uid in baseline.items():
            assert grown[summary] == uid, f"{label} 추가에 {summary} 의 UID 가 밀렸다"

    # 빼는 방향도 같다. 앞엣것을 지워도 뒤엣것이 당겨지지 않는다.
    shrunk = _uids_by_summary([event("끝", "zzz")])
    assert shrunk["끝"] == baseline["끝"]


def test_a_new_holiday_on_a_busy_day_leaves_the_real_feed_uids_alone():
    """실제 피드에 임시공휴일 하나를 끼워도 그 날 기존 UID 가 안 바뀌는지.

    2025-05-05 은 이미 두 건이 있는 날이다. 여기에 세 번째가 생기는 상황이
    가장 위험한 자리라 실제 이벤트로 확인한다.
    """
    real = feed.events(dt.date(2025, 5, 5), dt.date(2025, 5, 5))
    before = _uids_by_summary(real)
    assert len(before) == 2

    extra = ics.Event(day=dt.date(2025, 5, 5), summary="임시공휴일", kind="temporary", token="tmp")
    after = _uids_by_summary([*real, extra])

    for summary, uid in before.items():
        assert after[summary] == uid, f"{summary} 의 UID 가 바뀌었다"
    assert after["임시공휴일"] == "20250505-tmp@holidays.lunalism.com"


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
# 직렬화 — 접지 않은 원본 바이트를 본다
#
# 아래 셋은 _unfold() 를 쓰지 않는다. 헬퍼로 줄을 펴 버리면 접기 자체가
# 검사 대상에서 사라진다. 지금은 icalendar 라이브러리가 처리하고 있어 맞지만,
# 업그레이드나 호출 방식 변경으로 깨져도 펴 놓고 보면 통과한다.
# 한글은 문자 수와 UTF-8 옥텟 수가 달라 특히 위험한 자리다.
# ---------------------------------------------------------------------------


def test_every_line_ends_with_crlf():
    raw = feed.build(today=TODAY, dtstamp=DTSTAMP)
    assert raw.count(b"\n") == raw.count(b"\r\n"), "CR 없는 LF 가 있다"
    assert raw.endswith(b"\r\n")


def test_no_physical_line_exceeds_75_octets():
    """RFC 5545 의 접기 한계. 문자 수가 아니라 옥텟 수다."""
    raw = feed.build(today=TODAY, dtstamp=DTSTAMP)
    too_long = [line for line in raw.split(b"\r\n") if len(line) > 75]
    assert not too_long, "75 옥텟을 넘는 줄:\n" + "\n".join(
        f"  {len(line)}옥텟 {line[:40]!r}" for line in too_long[:5]
    )


def test_special_characters_survive_a_round_trip():
    """쉼표·세미콜론·역슬래시·개행이 든 값이 원문 그대로 돌아오는지.

    RFC 5545 의 TEXT 는 이 넷을 이스케이프해야 한다. 이스케이프가 빠지면
    쉼표에서 값이 잘리고, 과하면 역슬래시가 불어난다. 둘 다 왕복으로 잡힌다.

    긴 한글을 함께 넣는 이유는 접기와 겹쳐서 깨지는지 보기 위해서다.
    코드포인트 중간에서 접히면 왕복이 실패한다.
    """
    nasty = "쉼표, 세미콜론; 역슬래시\\ 그리고\n줄바꿈"
    long_korean = "대체공휴일 근거 문장을 길게 늘여 접기 경계를 넘긴다 " * 4
    events = [
        ics.Event(
            day=dt.date(2030, 1, 1),
            summary=nasty,
            kind="statutory",
            description=long_korean + nasty,
            token="nasty",
        )
    ]
    raw = ics.render(
        events, dtstamp=DTSTAMP, prodid=feed.PRODID, calname=feed.CALNAME, tzid=feed.TZID
    )

    assert not [line for line in raw.split(b"\r\n") if len(line) > 75]

    parsed = Calendar.from_ical(raw)
    (vevent,) = parsed.walk("VEVENT")
    assert str(vevent["SUMMARY"]) == nasty
    assert str(vevent["DESCRIPTION"]) == long_korean + nasty


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


def test_first_publication_marks_every_event_free_and_sequence_zero():
    """previous 없는 첫 발행 기준이다. SEQUENCE 가 늘 0 이라는 뜻이 아니다."""
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


# ---------------------------------------------------------------------------
# SEQUENCE — 진실 공급원은 이전 발행본이다
#
# 상태 파일을 두지 않는다. 발행본이 사실이고, 그것과 어긋날 수 있는 사본을
# 만들지 않는다. build() 는 그 바이트를 인자로 받는다 — dtstamp 와 같은 이유로
# 모듈 안에서 파일을 읽지 않는다.
# ---------------------------------------------------------------------------


def _render(events, previous=None) -> bytes:
    return ics.render(
        events,
        dtstamp=DTSTAMP,
        prodid=feed.PRODID,
        calname=feed.CALNAME,
        tzid=feed.TZID,
        previous=previous,
    )


def _sequences(raw: bytes) -> dict:
    return {
        str(v["UID"]): int(v["SEQUENCE"]) for v in Calendar.from_ical(raw).walk("VEVENT")
    }


def _sample(day=dt.date(2030, 1, 1), summary="가", token="alpha", **kw):
    return ics.Event(day=day, summary=summary, kind="statutory", token=token, **kw)


def _published(uid, dtstart, dtend, sequence, summary="가") -> bytes:
    """이전 발행본을 손으로 짓는다.

    UID 와 DTSTART 를 따로 줄 수 있어야 "같은 UID 인데 날짜가 바뀐" 상태를
    만들 수 있다. 우리 생성기로는 그 상태가 나오지 않는다 — UID 에 날짜가
    들어 있기 때문이다(아래 test_moving_a_date_shows_up_as_a_dropped_uid 참조).
    """
    return (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//KO\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTART;VALUE=DATE:{dtstart:%Y%m%d}\r\n"
        f"DTEND;VALUE=DATE:{dtend:%Y%m%d}\r\n"
        f"SUMMARY:{summary}\r\n"
        f"SEQUENCE:{sequence}\r\n"
        "DTSTAMP:20260810T000000Z\r\n"
        "END:VEVENT\r\nEND:VCALENDAR\r\n"
    ).encode()


def test_without_a_previous_feed_every_sequence_is_zero():
    """첫 발행이면 전부 0 이다."""
    raw = _render([_sample(), _sample(token="beta", summary="나")])
    assert set(_sequences(raw).values()) == {0}


def test_the_real_feed_starts_at_sequence_zero():
    assert {int(_prop(b, "SEQUENCE")) for b in _events(_build())} == {0}


def test_an_unchanged_date_keeps_the_previous_sequence():
    """날짜가 그대로면 SEQUENCE 를 물려받는다. 0 으로도, +1 로도 가지 않는다."""
    uid = "20300101-alpha@holidays.lunalism.com"
    prior = _published(uid, dt.date(2030, 1, 1), dt.date(2030, 1, 2), sequence=3)
    assert _sequences(_render([_sample()], previous=prior)) == {uid: 3}


def test_a_changed_date_bumps_the_sequence_by_one():
    """DTSTART 가 바뀌면 이전 값 + 1.

    우리 생성기로는 이 상태가 나오지 않는다 — UID 에 날짜가 들어 있어 날짜가
    바뀌면 UID 도 바뀐다. 그래서 이전 발행본을 손으로 지어 이 경로를 태운다.
    규칙 자체는 고정해 둔다. UID 규칙이 바뀌면 그때 살아나는 경로다.
    """
    uid = "20300101-alpha@holidays.lunalism.com"
    prior = _published(uid, dt.date(2029, 12, 25), dt.date(2029, 12, 26), sequence=2)
    assert _sequences(_render([_sample()], previous=prior)) == {uid: 3}


def test_bumping_one_event_leaves_the_others_alone():
    """한 건이 올라가도 나머지는 그대로다."""
    moved_uid = "20300101-alpha@holidays.lunalism.com"
    kept_uid = "20300101-beta@holidays.lunalism.com"
    prior = (
        _published(moved_uid, dt.date(2029, 1, 1), dt.date(2029, 1, 2), sequence=1).replace(
            b"END:VCALENDAR\r\n", b""
        )
        + _published(kept_uid, dt.date(2030, 1, 1), dt.date(2030, 1, 2), sequence=5, summary="나")
        .replace(b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//KO\r\n", b"")
    )
    got = _sequences(_render([_sample(), _sample(token="beta", summary="나")], previous=prior))
    assert got == {moved_uid: 2, kept_uid: 5}


@pytest.mark.parametrize(
    "changed",
    [
        {"summary": "다른 이름"},
        {"description": "다른 근거"},
        {"provisional": True},
    ],
    ids=["summary", "description", "status"],
)
def test_non_date_changes_do_not_bump_the_sequence(changed):
    """SUMMARY·DESCRIPTION·STATUS 가 바뀌어도 올리지 않는다.

    표기나 우리 확신도가 달라진 것이지 일정이 달라진 것이 아니다. 구독자가
    다시 알림을 받을 일이 아니다. 잠정이 확정으로 바뀌는 것도 마찬가지다 —
    날짜가 그대로면 이미 잡아 둔 일정은 유효하다.
    """
    uid = "20300101-alpha@holidays.lunalism.com"
    prior = _published(uid, dt.date(2030, 1, 1), dt.date(2030, 1, 2), sequence=4)
    assert _sequences(_render([_sample(**changed)], previous=prior)) == {uid: 4}


def test_a_uid_that_disappears_fails_the_build():
    """이전 발행본에 있던 UID 가 새 피드에 없으면 멈춘다.

    그냥 빼면 구독자 캘린더에는 그대로 남는다. 없어졌다는 사실이 전달되지 않는다.
    """
    gone = "20300101-alpha@holidays.lunalism.com"
    prior = _published(gone, dt.date(2030, 1, 1), dt.date(2030, 1, 2), 0, summary="사라질 것")

    with pytest.raises(ics.IcsError) as exc:
        _render([_sample(token="beta", summary="남을 것")], previous=prior)

    message = str(exc.value)
    assert gone in message
    assert "SUMMARY='사라질 것'" in message
    assert "STATUS:CANCELLED" in message


def test_moving_a_date_shows_up_as_a_dropped_uid():
    """날짜를 옮기면 SEQUENCE 가 오르는 게 아니라 UID 가 사라진 것으로 잡힌다.

    UID 에 날짜가 들어 있기 때문이다. 지금 규칙에서는 이것이 날짜 변경의
    실제 모습이고, +1 경로는 정상 운영에서 밟히지 않는다.
    이 테스트는 그 사실 자체를 고정해 둔다.
    """
    v1 = _render([_sample(day=dt.date(2030, 1, 1))])
    with pytest.raises(ics.IcsError, match="새 피드에 없다"):
        _render([_sample(day=dt.date(2030, 1, 2))], previous=v1)


def test_an_unreadable_previous_feed_fails_the_build():
    """읽지 못하는 이전 발행본은 0 으로 재시작하지 않고 멈춘다."""
    with pytest.raises(ics.IcsError, match="이전 발행본을 읽지 못했다"):
        _render([_sample()], previous="이건 ics 가 아니다".encode())

    message = ""
    try:
        _render([_sample()], previous=b"\x00\x01\x02")
    except ics.IcsError as exc:
        message = str(exc)
    assert "0 으로 다시 시작하지 않는다" in message


def test_a_previous_feed_missing_required_fields_fails_the_build():
    broken = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//KO\r\n"
        b"BEGIN:VEVENT\r\nDTSTAMP:20260810T000000Z\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    with pytest.raises(ics.IcsError, match="UID 없는 VEVENT"):
        _render([_sample()], previous=broken)


def test_a_previous_feed_with_a_duplicate_uid_fails_the_build():
    uid = "20300101-alpha@holidays.lunalism.com"
    one = _published(uid, dt.date(2030, 1, 1), dt.date(2030, 1, 2), 0)
    doubled = one.replace(b"END:VCALENDAR\r\n", b"") + one.replace(
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//KO\r\n", b""
    )
    with pytest.raises(ics.IcsError, match="UID 가 중복"):
        _render([_sample()], previous=doubled)


def test_a_negative_sequence_in_the_previous_feed_fails_the_build():
    uid = "20300101-alpha@holidays.lunalism.com"
    prior = _published(uid, dt.date(2030, 1, 1), dt.date(2030, 1, 2), sequence=-1)
    with pytest.raises(ics.IcsError, match="SEQUENCE 가 음수"):
        _render([_sample()], previous=prior)


def test_republishing_unchanged_content_keeps_every_sequence():
    """내용이 그대로면 SEQUENCE 가 하나도 안 움직인다.

    두 번째 발행에 다른 DTSTAMP 를 준다. 같은 값을 쓰면 바이트가 같은 것만
    확인하게 되는데, 실제 재발행은 시계를 다시 읽으므로 DTSTAMP 가 늘 다르다.
    같은 값으로 확인해 놓고 "무변경 재발행은 diff 가 없다"고 적으면 코드가
    하지 않는 주장을 하는 것이 된다.

    실제로 달라지는 것은 DTSTAMP 뿐이다. 그것까지 여기서 못 박는다.
    """
    later = dt.datetime(2026, 9, 1, 12, 0, tzinfo=dt.UTC)

    first = feed.build(today=TODAY, dtstamp=DTSTAMP)
    again = feed.build(today=TODAY, dtstamp=later, previous=first)

    assert _sequences(again) == _sequences(first)
    assert set(_sequences(again).values()) == {0}

    # DTSTAMP 만 빼면 완전히 같아야 한다.
    def _without_dtstamp(raw):
        return [ln for ln in raw.decode().split("\r\n") if not ln.startswith("DTSTAMP:")]

    assert _without_dtstamp(again) == _without_dtstamp(first)
    assert again != first, "DTSTAMP 가 반영되지 않았다"


def test_adding_a_future_year_leaves_existing_uids_and_sequences_alone():
    """상한이 늘어 새 연도가 들어와도 기존 UID 와 SEQUENCE 가 그대로인지.

    피드는 해마다 다시 발행되고 그때마다 뒤쪽 연도가 하나씩 붙는다. 그 흔한
    변화가 기존 이벤트를 건드리면 구독자 캘린더 전체가 흔들린다.
    """
    first = feed.build(today=TODAY, dtstamp=DTSTAMP)  # ~2031
    grown = feed.build(today=dt.date(2027, 8, 10), dtstamp=DTSTAMP, previous=first)  # ~2032

    before, after = _sequences(first), _sequences(grown)
    assert set(before) < set(after), "새 연도가 붙지 않았다"
    for uid, seq in before.items():
        assert after[uid] == seq, f"{uid} 의 SEQUENCE 가 움직였다"

    added = set(after) - set(before)
    assert added and all(uid.startswith("2032") for uid in added), sorted(added)[:3]
    assert all(after[uid] == 0 for uid in added)


def test_an_empty_previous_calendar_fails_the_build():
    """파싱은 되는데 VEVENT 가 0 건인 이전본은 받지 않는다.

    받으면 모든 UID 가 "처음 보는 것"이 되어 SEQUENCE 가 전부 0 으로 되감긴다.
    파싱 실패와 결과가 같으므로 같이 막는다. 첫 발행은 previous=None 이다.
    """
    empty = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//KO\r\nEND:VCALENDAR\r\n"
    with pytest.raises(ics.IcsError, match="VEVENT 가 하나도 없다"):
        _render([_sample()], previous=empty)


def test_a_non_integer_sequence_in_the_previous_feed_fails_the_build():
    """SEQUENCE 가 정수가 아니면 IcsError. 라이브러리 예외가 새어 나가면 안 된다."""
    prior = _published(
        "20300101-alpha@holidays.lunalism.com", dt.date(2030, 1, 1), dt.date(2030, 1, 2), 0
    ).replace(b"SEQUENCE:0", b"SEQUENCE:abc")
    with pytest.raises(ics.IcsError, match="SEQUENCE 가 정수가 아니다"):
        _render([_sample()], previous=prior)


def test_a_timed_dtstart_in_the_previous_feed_fails_the_build():
    """DTSTART 에 시각이 붙어 있으면 IcsError.

    그냥 통과시키면 date 와의 비교가 늘 다르다고 나와, 바뀐 것이 없는데도
    SEQUENCE 가 올라간다. 예외가 아니라 조용한 오답이라 더 나쁘다.
    """
    timed = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//KO\r\nBEGIN:VEVENT\r\n"
        b"UID:20300101-alpha@holidays.lunalism.com\r\n"
        b"DTSTART:20300101T090000Z\r\nDTEND:20300101T100000Z\r\n"
        b"SEQUENCE:2\r\nDTSTAMP:20260810T000000Z\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    with pytest.raises(ics.IcsError, match="종일 날짜가 아니다"):
        _render([_sample()], previous=timed)


# ---------------------------------------------------------------------------
# publish() — 실제 발행 경로
#
# stdout 리다이렉션을 쓸 수 없다. 이 피드는 자기 자신의 직전 판을 입력으로
# 받는데, 셸의 `> feeds/kr.ics` 는 프로세스가 뜨기 전에 그 파일을 비운다.
# 읽을 이전본이 사라진 뒤에 프로그램이 시작하는 것이다.
# ---------------------------------------------------------------------------


def test_publish_writes_the_feed_and_returns_the_path(tmp_path, confirmed_domain):
    target = tmp_path / "kr.ics"
    written = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)

    assert written == target
    assert target.read_bytes() == feed.build(today=TODAY, dtstamp=DTSTAMP)


def test_publish_reads_the_previous_file_before_replacing_it(tmp_path, confirmed_domain):
    """두 번째 발행이 첫 번째를 이전본으로 읽는지.

    읽기가 쓰기보다 먼저여야 한다. 순서가 뒤집히면 자기가 방금 쓴 것을
    이전본으로 읽게 되고 SEQUENCE 가 의미를 잃는다.
    """
    target = tmp_path / "kr.ics"
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    first = target.read_bytes()

    later = dt.datetime(2026, 9, 1, 12, 0, tzinfo=dt.UTC)
    feed.publish(today=TODAY, dtstamp=later, path=target)
    second = target.read_bytes()

    assert _sequences(second) == _sequences(first)
    assert second != first  # DTSTAMP 는 달라진다


def test_publish_leaves_no_temp_file_behind(tmp_path, confirmed_domain):
    target = tmp_path / "kr.ics"
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert [p.name for p in tmp_path.iterdir()] == ["kr.ics"]


def test_publish_does_not_destroy_the_previous_feed_when_the_build_fails(
    tmp_path, confirmed_domain
):
    """빌드가 실패하면 기존 발행본이 그대로 남아야 한다.

    이것이 stdout 리다이렉션과 갈리는 지점이다. 셸이라면 이미 비운 뒤였다.
    """
    target = tmp_path / "kr.ics"
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    intact = target.read_bytes()

    with pytest.raises(ics.IcsError):
        feed.publish(today=TODAY, dtstamp=dt.datetime(2026, 8, 10), path=target)  # naive

    assert target.read_bytes() == intact


@pytest.fixture
def confirmed_domain(monkeypatch):
    """발행이 열린 상태를 명시적으로 둔다.

    도메인을 확정한 뒤로 core/ics.py 의 UID_DOMAIN_CONFIRMED 는 True 라 이
    픽스처는 지금 값을 바꾸지 않는다. 그래도 남겨 두는 것은 아래 발행
    테스트들이 그 전역값에 매이지 않게 하기 위해서다 — 누가 플래그를 다시
    내려도 발행 로직 자체의 검증은 계속 돌아야 한다.
    """
    monkeypatch.setattr(ics, "UID_DOMAIN_CONFIRMED", True)


def _run_entry_point(target: Path, *, confirmed=True):
    """python -m rules.kr.feed 를 자식 프로세스에서 돌린다.

    confirmed 값을 자식 안에서 UID_DOMAIN_CONFIRMED 에 넣고 진입점을 실행한다.
    monkeypatch 는 자식에 닿지 않고, 그렇다고 프로덕션에 환경변수 우회를
    만들면 그것이 곧 상시 우회 경로가 된다. 테스트가 자기 자식에서만 바꾸는
    편이 낫다.
    """
    code = (
        "import sys, runpy, core.ics;"
        f"core.ics.UID_DOMAIN_CONFIRMED = {bool(confirmed)!r};"
        f"sys.argv = ['rules.kr.feed', {str(target)!r}];"
        "runpy.run_module('rules.kr.feed', run_name='__main__')"
    )
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_uid_namespace_is_confirmed_and_frozen():
    """발행이 열려 있다는 사실을 못 박는다.

    holidays.lunalism.com 을 확정하고 이 플래그를 올린 시점부터 UID 는 영구
    고정이다. 되돌리면 이미 나간 구독자 캘린더에서 모든 공휴일이 삭제 +
    재생성으로 나타나고, SEQUENCE 를 올려도 수습되지 않는다 — UID 가 달라지면
    캘린더는 애초에 다른 이벤트로 본다(core/ics.py 의 UID 절 참조).

    이 테스트는 값이 실수로 다시 내려가거나 도메인 문자열이 바뀌는 것을 잡는다.
    정말 바꿔야 한다면 구독자 영향을 먼저 확인하고 여기를 함께 고칠 것.
    """
    assert ics.UID_DOMAIN == "holidays.lunalism.com"
    assert ics.UID_DOMAIN_CONFIRMED is True


def test_publish_refuses_when_the_uid_domain_is_not_confirmed(monkeypatch):
    """플래그를 내리면 발행이 멈추는지. 가드가 장식이 아닌지 확인한다.

    확정한 뒤에도 이 검증을 남기는 이유는, 이 자리가 다음 국가 피드나 네임
    스페이스를 다시 손대는 상황에서 그대로 다시 쓰이기 때문이다. 지금 통과한다고
    지워 두면 그때 가드가 살아 있는지 아무도 모른다.

    build() 는 막지 않는다 — 막아야 하는 것은 만드는 것이 아니라 나가는 것이다.
    """
    monkeypatch.setattr(ics, "UID_DOMAIN_CONFIRMED", False)

    with pytest.raises(ics.IcsError, match="확정되지 않아 발행하지 않는다"):
        feed.publish(today=TODAY, dtstamp=DTSTAMP, path=Path("/tmp/should-not-exist.ics"))

    assert feed.build(today=TODAY, dtstamp=DTSTAMP).startswith(b"BEGIN:VCALENDAR")


def test_the_entry_point_refuses_when_the_uid_domain_is_not_confirmed(tmp_path):
    """진입점도 같은 자리에서 멈추는지. 워크플로가 실제로 밟는 경로다."""
    target = tmp_path / "kr.ics"
    done = _run_entry_point(target, confirmed=False)

    assert done.returncode != 0
    assert "확정되지 않아 발행하지 않는다" in done.stderr
    assert not target.exists(), "거부했는데 파일이 생겼다"


def test_the_module_entry_point_publishes_to_a_file(tmp_path):
    """python -m rules.kr.feed 가 실제로 파일을 쓰는지 subprocess 로 확인한다.

    진짜 __main__ 을 돌린다. 여기서 밟지 않으면 발행 경로가 통째로 검증 밖에
    남고, 리다이렉션 사고 같은 것이 운영에서 처음 드러난다.

    시계는 여기서 고정할 수 없다(진입점이 읽는다). DTSTAMP 를 뺀 나머지가
    우리가 기대하는 피드와 같은지로 확인한다.
    """
    target = tmp_path / "kr.ics"
    done = _run_entry_point(target)

    assert done.returncode == 0, done.stderr
    assert target.exists(), done.stdout + done.stderr
    assert str(target) in done.stdout

    written = target.read_bytes()
    assert written.startswith(b"BEGIN:VCALENDAR")
    assert set(_sequences(written).values()) == {0}


def test_the_entry_point_can_run_twice_against_the_same_file(tmp_path):
    """진입점을 같은 경로로 두 번 돌려도 SEQUENCE 가 흔들리지 않는지.

    `python -m rules.kr.feed > feeds/kr.ics` 였다면 두 번째에 이전본이 이미
    비워진 뒤라 빌드가 실패했을 자리다. publish() 는 읽고 나서 바꾼다.
    """
    target = tmp_path / "kr.ics"
    assert _run_entry_point(target).returncode == 0
    first = _sequences(target.read_bytes())

    second_run = _run_entry_point(target)
    assert second_run.returncode == 0, second_run.stderr
    assert _sequences(target.read_bytes()) == first
    assert set(first.values()) == {0}


def test_publish_survives_being_pointed_at_its_own_output_twice(tmp_path, confirmed_domain):
    """같은 경로로 세 번 발행해도 SEQUENCE 가 흔들리지 않는지.

    stdout 리다이렉션이었다면 두 번째에 이미 깨졌을 자리다.
    """
    target = tmp_path / "kr.ics"
    stamps = [
        DTSTAMP,
        dt.datetime(2026, 9, 1, tzinfo=dt.UTC),
        dt.datetime(2026, 10, 1, tzinfo=dt.UTC),
    ]
    for stamp in stamps:
        feed.publish(today=TODAY, dtstamp=stamp, path=target)

    assert set(_sequences(target.read_bytes()).values()) == {0}
