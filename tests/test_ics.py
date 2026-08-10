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
