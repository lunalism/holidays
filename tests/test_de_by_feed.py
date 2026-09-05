"""독일·바이에른 주 피드 — rules/de_by/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_by.ics 는 바이에른 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über den Schutz der Sonn- und Feiertage (Feiertagsgesetz –
    FTG, BayFTG) Art. 1 Abs. 1 Nr. 1 이다 — "im ganzen Staatsgebiet" 의 열거 12 건.
    연 단위 구성은 고정 7 + 부활절 이동 5 = 12 건이고 일회성은 (아직) 없다.
    지자체·집단 한정 3 건(Art. 1 Abs. 1 Nr. 2 Mariä Himmelfahrt, Art. 1 Abs. 2
    Friedensfest, Art. 4 의 Buß- und Bettag)은 범위 밖이다.
    대체공휴일(이동) 규칙은 없다 — 일요일과 겹쳐도 그 날짜 그대로다.

여기서는 그 사양을 숫자와 날짜로 못 박는다. 첫 단언은 feiertage-api 와의
전수 대조다 — 12 건의 분해(고정/오프셋)는 즉석 계산이 아니라 API 실측값이
기준이고, 어긋나면 사양부터 다시 본다.

    a. feiertage-api 2026 BY 실측 15 건 − 지자체 한정 3 건 == de_by 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_by.ics, 차집합은 세 건(Heilige Drei Könige,
       Fronleichnam, Allerheiligen)뿐
    c. 일요일 겹침·연도별 건수 — de_be 관례 이식
    d. UID — 전 항목 de_by- 접두사, de.ics·de_be.ics 와 겹치지 않음
    e. 하니스 — python-holidays(subdiv='BY')와 연도별 날짜 집합 대조
    f. 헤더·DTEND·범위·근거 — de_be 관례 이식

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_by 를 더해 켠다(여기 두지 않는다 — 한 자리에서 주 피드를 센다).
"""

from __future__ import annotations

import datetime as dt
import re

import pytest
import yaml

from core import ics
from rules.de import feed as de_feed
from rules.de_be import feed as de_be_feed
from rules.de_by import feed
from rules.de_by import status as de_by_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_by-"

# feiertage-api.de 2026 BY 실측(2026-09-06, ?jahr=2026&nur_land=BY). 15 건, 측정값
# 그대로. hinweis 가 붙은 셋이 지자체·집단 한정이다.
FEIERTAGE_API_2026_BY = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Heilige Drei Könige": dt.date(2026, 1, 6),
    "Karfreitag": dt.date(2026, 4, 3),
    "Ostermontag": dt.date(2026, 4, 6),
    "Tag der Arbeit": dt.date(2026, 5, 1),
    "Christi Himmelfahrt": dt.date(2026, 5, 14),
    "Pfingstmontag": dt.date(2026, 5, 25),
    "Fronleichnam": dt.date(2026, 6, 4),
    "Augsburger Friedensfest": dt.date(2026, 8, 8),
    "Mariä Himmelfahrt": dt.date(2026, 8, 15),
    "Tag der Deutschen Einheit": dt.date(2026, 10, 3),
    "Allerheiligen": dt.date(2026, 11, 1),
    "Buß- und Bettag": dt.date(2026, 11, 18),
    "1. Weihnachtstag": dt.date(2026, 12, 25),
    "2. Weihnachtstag": dt.date(2026, 12, 26),
}
LOCAL_ONLY = {"Augsburger Friedensfest", "Mariä Himmelfahrt", "Buß- und Bettag"}
API_STATEWIDE_2026 = {d for n, d in FEIERTAGE_API_2026_BY.items() if n not in LOCAL_ONLY}

# BayFTG Art. 1 Abs. 1 Nr. 1 의 열거 순서·조문 표기(gesetze-bayern.de BayFTG-1,
# 2026-09-06 열람). "Heilige Drei Könige (Epiphanias)" 의 괄호 별칭과 "der 3.
# Oktober als Tag der Deutschen Einheit" 의 서술부는 SUMMARY 에서 뺐다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahr", "neujahr"),
    (dt.date(2026, 1, 6), "Heilige Drei Könige", "heilige_drei_koenige"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai"),
    (dt.date(2026, 5, 14), "Christi Himmelfahrt", "christi_himmelfahrt"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag"),
    (dt.date(2026, 6, 4), "Fronleichnam", "fronleichnam"),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit"),
    (dt.date(2026, 11, 1), "Allerheiligen", "allerheiligen"),
    (dt.date(2026, 12, 25), "Erster Weihnachtstag", "erster_weihnachtstag"),
    (dt.date(2026, 12, 26), "Zweiter Weihnachtstag", "zweiter_weihnachtstag"),
]
TOKENS = {PREFIX + key for _, _, key in EXPECTED_2026}


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
# a. 첫 단언 — feiertage-api 2026 BY 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api_minus_the_three_local_holidays(events):
    """멈춤 조건. API 15 건에서 지자체 한정 3 건을 뺀 12 건이 발행 집합과 다르면
    구현을 멈추고 불일치 목록을 보고한다."""
    assert len(FEIERTAGE_API_2026_BY) == 15
    assert len(API_STATEWIDE_2026) == 12
    ours = _days(events, 2026)
    assert ours == API_STATEWIDE_2026, {
        "api_only": sorted(API_STATEWIDE_2026 - ours),
        "ours_only": sorted(ours - API_STATEWIDE_2026),
    }


def test_2026_has_exactly_the_twelve_bavarian_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k in EXPECTED_2026]


def test_the_three_local_holidays_are_absent_in_every_year(events):
    """Friedensfest(8. 8.)·Mariä Himmelfahrt(15. 8.)·Buß- und Bettag 는 주 전역이
    아니라 싣지 않는다. 날짜·이름·token 어느 축으로도 없어야 한다."""
    for year in range(2020, 2032):
        days = _days(events, year)
        assert dt.date(year, 8, 8) not in days, year
        assert dt.date(year, 8, 15) not in days, year
        assert not {d for d in days if d.month == 11 and 16 <= d.day <= 22}, year
    for e in events:
        for word in ("friedensfest", "mariae", "buss"):
            assert word not in e.token, e.token
        for word in ("Friedensfest", "Mariä", "Buß"):
            assert word not in e.summary, e.summary


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_by.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_bavaria(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    bavaria = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= bavaria
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {
        PREFIX + "heilige_drei_koenige", PREFIX + "fronleichnam", PREFIX + "allerheiligen",
    }


# ---------------------------------------------------------------------------
# c. 연도별 건수 · 일요일 겹침
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_twelve_and_the_same_token_set(events, year):
    """일회성이 없으므로 해마다 12 건, token 집합은 해마다 같다."""
    assert len(_year(events, year)) == 12
    assert {e.token for e in _year(events, year)} == TOKENS


@pytest.mark.parametrize(
    "year, sunday, key",
    [
        (2026, dt.date(2026, 11, 1), "allerheiligen"),
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
        (2023, dt.date(2023, 1, 1), "neujahr"),
        (2030, dt.date(2030, 1, 6), "heilige_drei_koenige"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """BayFTG 전문에 이동 조항이 없고(rules/de/solar_holidays.yaml), feiertage-api
    BY 2020–2031 실측에서 일요일 겹침 연도(2020·2021·2022·2023·2026·2027·2030)에도
    보상 휴일 0 건. 일요일 항목은 그대로 실리고 그 해는 12 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 12
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, de.ics·de_be.ics 와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_nationwide_or_berlin_feed(rendered):
    """전국 공통 9 건은 de.ics·de_be.ics 와 같은 날 같은 항목이다. 접두사가 유일한
    방벽이다 — 함께 구독한 캘린더에서 같은 UID 는 서로를 덮어쓴다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for other in (de_feed, de_be_feed):
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


def test_the_umlaut_is_transliterated_in_the_token_and_kept_in_the_summary(events):
    """ö→oe 의 첫 실적용. token 은 ASCII, SUMMARY 는 조문 표기 그대로다."""
    [e] = [e for e in events if e.day == dt.date(2026, 1, 6)]
    assert e.token == PREFIX + "heilige_drei_koenige"
    assert e.summary == "Heilige Drei Könige"
    assert all(e.token.isascii() for e in events)


def test_the_token_charset_has_no_digits_without_one_offs(events):
    for e in events:
        key = e.token.removeprefix(PREFIX)
        assert re.fullmatch(r"[a-z][a-z_]*", key), e.token


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# e. 하니스 — python-holidays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_bavaria(events, year):
    """python-holidays 의 DE(subdiv='BY') 와 날짜 집합만 대조한다. 0.102 는 지자체
    한정 3 건을 싣지 않아 등호가 성립한다 — 차집합 허용 목록은 두지 않는다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="BY", years=year).keys())


# ---------------------------------------------------------------------------
# f. 헤더·DTEND·범위 — de_be 관례 이식
# ---------------------------------------------------------------------------


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_bavaria_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·바이에른 공휴일" in head
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
# 근거 — 항목별 조문 인용, verified 는 나가지 않는다
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_twelve_entries_each_citing_its_own_line_of_art_1(events):
    """조 단위 일괄 인용이 아니라 항목별 인용이다. 각 source 는 Art. 1 Abs. 1 Nr. 1
    을 대고 자기 항목의 조문 표기(정관사·서술부 포함 가능)를 따옴표로 담는다."""
    entries = _raw_entries()
    assert len(entries) == 12
    assert {e["key"] for e in entries} == {key for _, _, key in EXPECTED_2026}
    name_of = {key: name for _, name, key in EXPECTED_2026}
    for entry in entries:
        assert "Art. 1 Abs. 1 Nr. 1" in entry["source"], entry["key"]
        quoted = re.findall(r"'([^']+)'", entry["source"])
        assert quoted and any(name_of[entry["key"]] in q for q in quoted), entry["key"]


def test_every_entry_is_verified_against_the_official_portal_and_says_where():
    """공식 포털(gesetze-bayern.de) 원문을 읽었으므로 12 건 전부 true 다. 근거
    필드에 확인 경로가 남아야 한다 — true 만 적고 어디서 봤는지 없으면 검증이
    아니라 주장이다."""
    for entry in _raw_entries():
        assert entry["verified"] is True, entry["key"]
        assert "gesetze-bayern.de" in entry["source"], entry["key"]
        assert "source_todo" not in entry, entry["key"]


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
    target = tmp_path / "de_by.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_by_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_by.ics"
    assert got["events"] == 12 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (de_be 와 같은 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Heilige Drei Könige", "month": 1, "day": 6,
                           "verified": True, "source": "test"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("heilige_drei_koenige\n", id="끝 개행"),
        pytest.param("heilige_drei_könige", id="비ASCII 움라우트"),
        pytest.param("Heilige_Drei_Koenige", id="대문자"),
        pytest.param("3_koenige", id="숫자 시작"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "month", "day")


def test_a_transliterated_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "heilige_drei_koenige"), "month", "day")
    assert entry["key"] == "heilige_drei_koenige"
