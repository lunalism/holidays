"""독일·베를린 주 피드 — rules/de_be/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_be.ics 는 베를린 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über die Sonn- und Feiertage (Berlin) § 1 Abs. 1 이다.
    연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건에, 연도별 일회성이 더해진다.
    대체공휴일(이동) 규칙은 없다 — 일요일과 겹쳐도 그 날짜 그대로다.

근거는 /tmp/report_de_laender.md 의 BE 절이고, 요지는 rules/de_be/ 의 YAML
source 필드에 옮겨 적었다. 여기서는 그 사양을 숫자와 날짜로 못 박는다.

    a. 2026 년 10 건 전수 — 날짜·SUMMARY·token, feiertage-api 2026 BE 와 대조
    b. 일회성 — 연도별 건수(2024=10, 2025=11, 2026=10, 2028=11)와 각 날짜의
       포함/부재. 2020-05-08 도 범위 안이라 같이 잡는다
    c. 상위집합 — de.ics 9 건 ⊂ de_be.ics, 차집합은 Frauentag 과 일회성뿐
    d. 하니스 — python-holidays(subdiv='BE')와 연도별 날짜 집합 대조,
       주 피드 교집합 == de.ics 의 씨앗
    e. 일요일 겹침·UID·DTEND·헤더·범위 — de 관례 이식
    f. UID 가 de.ics 와 겹치지 않는다 — 두 피드를 함께 구독해도 덮어쓰지 않게

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

--------------------------------------------------------------------------
하니스의 자리
--------------------------------------------------------------------------
python-holidays 는 대조 상대이지 채택 소스가 아니다(tests/test_de_feed.py 와
같은 원칙). 0.102 의 DE/BE 는 Frauentag 과 일회성 셋(2020·2025·2028)을 모두
갖고 있어 차집합 허용 목록이 필요 없다 — 필요해지는 날 그 목록이 곧 사양의
불일치 기록이 된다.
"""

from __future__ import annotations

import datetime as dt
import re

import pytest
import yaml

from core import ics
from rules.de import feed as de_feed
from rules.de_be import feed
from rules.de_be import status as de_be_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. de.ics 와 같은 날 같은 항목이 같은 UID 로 나가면 두 피드를
# 함께 구독한 캘린더에서 서로를 덮어쓴다(rules/kr_only/feed.py 의 같은 절).
PREFIX = "de_be-"

# /tmp/report_de_laender.md BE §2 — § 1 Abs. 1 의 조문 표기(정관사 der 제외).
# "Tag der deutschen Einheit" 의 소문자 d 는 조문 그대로다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr"),
    (dt.date(2026, 3, 8), "Frauentag", "frauentag"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai"),
    (dt.date(2026, 5, 14), "Himmelfahrtstag", "christi_himmelfahrt"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag"),
    (dt.date(2026, 10, 3), "Tag der deutschen Einheit", "tag_der_deutschen_einheit"),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag"),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag"),
]

# feiertage-api.de 2026 BE 실측(2026-09-05, /tmp/report_de_laender.md BE §4). 10 건.
FEIERTAGE_API_2026_BE = {
    dt.date(2026, 1, 1),
    dt.date(2026, 3, 8),
    dt.date(2026, 4, 3),
    dt.date(2026, 4, 6),
    dt.date(2026, 5, 1),
    dt.date(2026, 5, 14),
    dt.date(2026, 5, 25),
    dt.date(2026, 10, 3),
    dt.date(2026, 12, 25),
    dt.date(2026, 12, 26),
}

# 일회성. § 1 Abs. 1 에 연도가 박힌 항목이라 그 해에만 있다.
#   2020-05-08  2019-01-30 개정(GVBl. S. 22), 2020 년 한 번
#   2025-05-08  2024-07-10 개정(GVBl. 2024 Nr. 28 S. 460) Nr. 11, 2025-05-09 삭제
#   2028-06-17  같은 개정 Nr. 12 → 현행 Nr. 11, 2028-06-18 삭제 예정
ONE_OFFS = {
    dt.date(2020, 5, 8): ("8. Mai 2020", "achter_mai_2020"),
    dt.date(2025, 5, 8): ("8. Mai 2025", "achter_mai_2025"),
    dt.date(2028, 6, 17): ("17. Juni 2028", "siebzehnter_juni_2028"),
}

REGULAR_TOKENS = {PREFIX + key for _, _, key in EXPECTED_2026}


@pytest.fixture(scope="module")
def events():
    return feed.events(*feed.feed_range(TODAY))


@pytest.fixture(scope="module")
def rendered():
    raw = feed.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
    return raw.replace("\r\n ", "").replace("\r\n\t", "")


def _year(events, year: int) -> list:
    return [e for e in events if e.day.year == year]


def _days(events, year: int) -> set:
    return {e.day for e in _year(events, year)}


def _blocks(rendered) -> list:
    return [b.split("END:VEVENT")[0] for b in rendered.split("BEGIN:VEVENT")[1:]]


def _prop(block: str, name: str) -> str:
    match = re.search(rf"^{name}(?:;[^:]*)?:(.*?)\r?$", block, re.MULTILINE)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# a. 2026 년 10 건 전수
# ---------------------------------------------------------------------------


def test_2026_has_exactly_the_ten_berlin_holidays(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k in EXPECTED_2026]


def test_2026_dates_match_feiertage_api(events):
    """멈춤 조건이었던 대조. 2026 건수·날짜가 API 와 어긋나면 사양부터 다시 본다."""
    assert _days(events, 2026) == FEIERTAGE_API_2026_BE
    assert len(_year(events, 2026)) == len(FEIERTAGE_API_2026_BE) == 10


# ---------------------------------------------------------------------------
# b. 일회성 — 존재/부재가 연도로 갈린다
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "year, count",
    [
        (2020, 11), (2021, 10), (2024, 10), (2025, 11),
        (2026, 10), (2027, 10), (2028, 11), (2029, 10),
    ],
)
def test_the_year_count_is_ten_plus_that_years_one_offs(events, year, count):
    assert len(_year(events, year)) == count


@pytest.mark.parametrize("day", sorted(ONE_OFFS))
def test_each_one_off_appears_in_its_year_only(events, day):
    summary, key = ONE_OFFS[day]
    found = [e for e in events if e.token == PREFIX + key]
    assert [(e.day, e.summary) for e in found] == [(day, summary)]
    # 같은 월·일의 다른 해에는 없다 — 그 해에 따로 정의된 일회성(8. Mai 는
    # 2020 과 2025 둘 다)이 아닌 한.
    for year in range(2020, 2032):
        same_day = day.replace(year=year)
        if year == day.year or same_day in ONE_OFFS:
            continue
        assert same_day not in _days(events, year), (year, day)


def test_no_one_off_leaks_into_a_regular_year(events):
    """2024·2026·2027 은 정규 10 건뿐이다. token 집합이 정규 10 개와 같다."""
    for year in (2024, 2026, 2027):
        assert {e.token for e in _year(events, year)} == REGULAR_TOKENS, year


def test_the_regular_token_set_is_the_same_every_year(events):
    for year in range(2020, 2032):
        regular = {e.token for e in _year(events, year) if e.day not in ONE_OFFS}
        assert regular == REGULAR_TOKENS, year


# ---------------------------------------------------------------------------
# c. 상위집합 — de.ics ⊂ de_be.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_berlin(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    berlin = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= berlin
    extra = berlin - nationwide
    expected_extra = {dt.date(year, 3, 8)} | {d for d in ONE_OFFS if d.year == year}
    assert extra == expected_extra


# ---------------------------------------------------------------------------
# d. 하니스
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_berlin(events, year):
    """python-holidays 의 DE(subdiv='BE') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기(Neujahr, Erster Mai, '75. Jahrestag …')는 우리
    표기(조문)와 다르고 그 차이는 사양이다.

    0.102 는 일회성 셋을 모두 갖고 있다. 차집합 허용 목록을 두지 않는 것은
    그래서다 — 갈리는 날이 생기면 여기서 빨개지고, 그때 어느 쪽이 맞는지는
    법조문으로 정한다.
    """
    holidays = pytest.importorskip("holidays")
    ours = _days(events, year)
    theirs = set(holidays.DE(subdiv="BE", years=year).keys())
    assert ours == theirs


# 주 피드 목록. 두 번째 주 피드가 생기면 여기에 더한다 — 그 순간 아래 교집합
# 테스트가 켜진다.
STATE_FEEDS = {"de_be": feed}


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_intersection_of_state_feeds_is_the_nationwide_feed(year):
    """전국 공통의 정의는 "16 개 주 전체에서 유효"다(rules/de/__init__.py).
    주 피드가 쌓이면 그 교집합이 de.ics 와 같아야 한다 — 주 피드에서 합산
    생성하는 것이 아니라 검증으로 실현되는 정의다(docs/holiday_11.md).

    주 피드가 하나뿐이면 교집합은 자기 자신이라 아무것도 검증하지 못한다.
    그때는 건너뛰고 사유를 남긴다.
    """
    if len(STATE_FEEDS) < 2:
        pytest.skip(
            f"주 피드가 {len(STATE_FEEDS)} 개({', '.join(STATE_FEEDS)})뿐이라 교집합이 "
            "자기 자신이다. 두 번째 주 피드가 생기면 STATE_FEEDS 에 더해 켤 것."
        )
    start, end = dt.date(year, 1, 1), dt.date(year, 12, 31)
    sets = [{e.day for e in f.events(start, end)} for f in STATE_FEEDS.values()]
    nationwide = {e.day for e in de_feed.events(start, end)}
    assert set.intersection(*sets) == nationwide


# ---------------------------------------------------------------------------
# e. 일요일 겹침 — 이동 규칙 부재의 회귀 픽스처
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "year, sunday, key, count",
    [
        (2020, dt.date(2020, 3, 8), "frauentag", 11),
        (2026, dt.date(2026, 3, 8), "frauentag", 10),
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit", 10),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key, count):
    """§ 1 에 이동 조항이 없고, feiertage-api 2026 BE(03-08 일요일)도 보상 휴일
    0 건이다. 일요일에 놓인 항목은 그대로 실리고 건수는 그 해 값 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == count
    on_sunday = [e for e in year_events if e.day == sunday]
    assert [e.token for e in on_sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# f. UID — de.ics 와 겹치지 않고, 결정적이다
# ---------------------------------------------------------------------------


def test_every_uid_is_date_plus_prefixed_token(rendered, events):
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    expected = {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert set(uids) == expected
    assert all(e.token.startswith(PREFIX) for e in events)


def test_no_uid_is_shared_with_the_nationwide_feed(rendered):
    """같은 날 같은 공휴일이라도 de.ics 의 UID 와 달라야 한다. 두 피드를 함께
    구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    de_raw = de_feed.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
    theirs = {_prop(b, "UID") for b in _blocks(de_raw.replace("\r\n ", ""))}
    assert theirs, "de 발행본이 비었다 — 비교가 공허하다"
    assert ours & theirs == set()


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_token_charset_allows_only_a_trailing_year_as_digits(events):
    """서수는 풀어 쓴다(achter_mai). 숫자는 일회성의 연도 접미사로만 온다 —
    같은 월·일의 일회성이 다른 해에 또 생겨도 token 이 구분되게."""
    for e in events:
        key = e.token.removeprefix(PREFIX)
        assert re.fullmatch(r"[a-z][a-z_]*(?:_\d{4})?", key), e.token
        if e.day in ONE_OFFS:
            assert key.endswith(f"_{e.day.year}"), e.token
        else:
            assert not re.search(r"\d", key), e.token


def test_the_header_names_berlin_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·베를린 공휴일" in head
    assert "X-WR-TIMEZONE:Europe/Berlin" in head
    assert "PRODID:-//lunalism//holidays.lunalism.com//KO" in head


def test_every_event_is_transparent_and_free(rendered):
    for block in _blocks(rendered):
        assert _prop(block, "TRANSP") == "TRANSPARENT"
        assert _prop(block, "X-MICROSOFT-CDO-BUSYSTATUS") == "FREE"


def test_nothing_is_marked_tentative(rendered, events):
    assert "STATUS:TENTATIVE" not in rendered
    assert not any(e.provisional for e in events)


def test_the_range_follows_the_kr_policy():
    assert feed.feed_range(dt.date(2026, 1, 1)) == (dt.date(2020, 1, 1), dt.date(2031, 12, 31))
    assert feed.feed_range(dt.date(2020, 6, 1)) == (dt.date(2020, 1, 1), dt.date(2025, 12, 31))


def test_every_event_falls_inside_the_range(events):
    start, end = feed.feed_range(TODAY)
    assert all(start <= e.day <= end for e in events)


# ---------------------------------------------------------------------------
# 근거 — source 는 나가고 verified·source_todo 는 나가지 않는다
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH, feed.DESIGNATED_PATH):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        out.extend(doc["holidays"])
    return out


def test_the_tables_hold_thirteen_entries_with_sources():
    entries = _raw_entries()
    assert len(entries) == 13
    expected = {key for _, _, key in EXPECTED_2026} | {key for _, key in ONE_OFFS.values()}
    assert {e["key"] for e in entries} == expected
    for entry in entries:
        assert entry.get("source"), entry["key"]
        assert isinstance(entry.get("verified"), bool), entry["key"]


def test_only_the_gazette_backed_one_offs_are_verified():
    """관보 원문(GVBl. 2024 Nr. 28 S. 460)을 본 것은 2025·2028 일회성 둘이다.
    2020 일회성은 2019 개정 관보를 보지 못했고, Frauentag 과 정규 9 건은
    비공식 현행판·정부 안내·API 대조까지라 false 다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    for key in ("achter_mai_2025", "siebzehnter_juni_2028"):
        assert by_key[key]["verified"] is True, key
        assert "source_todo" not in by_key[key], key
    for key, entry in by_key.items():
        if key not in ("achter_mai_2025", "siebzehnter_juni_2028"):
            assert entry["verified"] is False, key
            assert entry.get("source_todo"), key
    assert "GVBl. S. 22" in by_key["frauentag"]["source_todo"]


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert e.description.startswith("근거: "), e
        assert " ".join(by_key[e.token.removeprefix(PREFIX)]["source"].split()) in e.description
        assert "\n" not in e.description


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_be.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_be_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_be.ics"
    # 12 년 × 10 + 범위 안 일회성 3(2020·2025·2028)
    assert got["events"] == 10 * 12 + 3
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "designated_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "holidays": [
                    {
                        "key": key,
                        "name": "8. Mai 2025",
                        "date": dt.date(2025, 5, 8),
                        "verified": False,
                        "source": "test",
                    }
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("achter_mai_2025\n", id="끝 개행"),
        pytest.param("achter mai 2025", id="공백 포함"),
        pytest.param("Achter_Mai_2025", id="대문자"),
        pytest.param("mariä_himmelfahrt", id="비ASCII 움라우트"),
        pytest.param("8_mai_2025", id="서수를 숫자로"),
        pytest.param("achter_mai_25", id="연도 두 자리"),
        pytest.param("achter_mai_2025_", id="연도 뒤 꼬리"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "date")


def test_a_key_with_a_trailing_year_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "achter_mai_2025"), "date")
    assert entry["key"] == "achter_mai_2025"
