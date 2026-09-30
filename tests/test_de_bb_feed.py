"""독일·브란덴부르크 주 피드 — rules/de_bb/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_bb.ics 는 브란덴부르크 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über die Sonn- und Feiertage (Feiertagsgesetz - FTG) vom
    21. März 1991 (GVBl. I S. 44) § 2 Abs. 1 이다 — 번호 없는 열거 12 건. 연 단위
    구성은 고정 6 + 부활절 이동 6 = 12 건, 전국 공통 9 건에 Ostersonntag(+0)·
    Pfingstsonntag(+49)·Reformationsfest(10. 31.)가 더해진다. 두 일요일은 이 피드에서
    처음 쓰는 key(ostersonntag·pfingstsonntag, 사람이 승인)다. 대체공휴일(이동) 규칙은
    없다.

verified 는 12 건 전건 false 다. 현행 자구는 1991 원법과 1994-12-19 개정(GVBl. I S. 514)
에 의존하는데, 두 호 모두 온라인 공포본을 찾지 못했다(BRAVORS 의 관보 목록은 1994 년에
Teil I Nr. 12·26 만 두고 1991 년 목록은 없다). 2015 개정(GVBl. I Nr. 13)은 § 2 Abs. 2 만
바꿨다. 현행 자구는 BRAVORS 통합본(2차)으로 읽었다. HH·NI·RP 전례처럼 false 로 발행하고
source_todo 에 경계를 적는다.

SUMMARY 는 조문 표기에서 관사 der/das 와 괄호만 뺀 것이다: "der Neujahrstag (1. Januar)"
→ "Neujahrstag", "der 1. Mai (Tag der Arbeit)" → "1. Mai", "der Tag der deutschen Einheit
(3. Oktober)" → "Tag der deutschen Einheit"(소문자 d 도 조문 그대로 — de_be 와 같다),
"das Reformationsfest (31. Oktober)" → "Reformationsfest"(key 는 reformationstag),
"der 1. Weihnachtsfeiertag (25. Dezember)" → "1. Weihnachtsfeiertag". 원문은 DESCRIPTION 에.

    a. feiertage-api 2026 BB 실측 12 건(hinweis 전부 공란) == de_bb 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_bb.ics, 차집합 token 은 셋
    c. 연도별 12 건, 두 일요일 항목은 늘 일요일
    d. UID — 전 항목 de_bb- 접두사, 다른 독일 피드(rules/ 스캔)와 겹치지 않음
    e. 신규 key 는 승인된 둘뿐
    f. 하니스 — python-holidays(subdiv='BB')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·SUMMARY
    h. 근거 — 열거 순번 인용, 12 건 전건 false + source_todo 의 경계, 머리 주석의 일회성
       검색 사실

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만 부른다.
시계를 읽지 않는다.

주 피드 교집합 == de.ics 와 scope 교차 검증은 tests/test_de_be_feed.py·test_de_scope.py 의
rules/ 스캔이 이 피드를 저절로 넣는다(여기 두지 않는다).
"""

from __future__ import annotations

import datetime as dt
import importlib
import re
from pathlib import Path

import pytest
import yaml
from rules.de_bb import feed
from rules.de_bb import status as de_bb_status

from core import ics
from rules.de import feed as de_feed

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_bb-"

# feiertage-api.de 2026 BB 실측(2026-09-30, ?jahr=2026&nur_land=BB). 12 건, 측정값 그대로.
# hinweis 는 열두 개 모두 빈 문자열이었다(2020~2031 열두 해 전부 같다).
FEIERTAGE_API_2026_BB = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Karfreitag": dt.date(2026, 4, 3),
    "Ostersonntag": dt.date(2026, 4, 5),
    "Ostermontag": dt.date(2026, 4, 6),
    "Tag der Arbeit": dt.date(2026, 5, 1),
    "Christi Himmelfahrt": dt.date(2026, 5, 14),
    "Pfingstsonntag": dt.date(2026, 5, 24),
    "Pfingstmontag": dt.date(2026, 5, 25),
    "Tag der Deutschen Einheit": dt.date(2026, 10, 3),
    "Reformationstag": dt.date(2026, 10, 31),
    "1. Weihnachtstag": dt.date(2026, 12, 25),
    "2. Weihnachtstag": dt.date(2026, 12, 26),
}
FEIERTAGE_API_2026_BB_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_BB}

# § 2 Abs. 1 의 열거 순서·SUMMARY 표기·조문 자구. 열거 순서가 곧 날짜 순서다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1, "der Neujahrstag (1. Januar)"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2, "der Karfreitag"),
    (dt.date(2026, 4, 5), "Ostersonntag", "ostersonntag", 3, "der Ostersonntag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 4, "der Ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 5, "der 1. Mai (Tag der Arbeit)"),
    (dt.date(2026, 5, 14), "Christi Himmelfahrtstag", "christi_himmelfahrt", 6,
     "der Christi Himmelfahrtstag"),
    (dt.date(2026, 5, 24), "Pfingstsonntag", "pfingstsonntag", 7, "der Pfingstsonntag"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 8, "der Pfingstmontag"),
    (dt.date(2026, 10, 3), "Tag der deutschen Einheit", "tag_der_deutschen_einheit", 9,
     "der Tag der deutschen Einheit (3. Oktober)"),
    (dt.date(2026, 10, 31), "Reformationsfest", "reformationstag", 10,
     "das Reformationsfest (31. Oktober)"),
    (dt.date(2026, 12, 25), "1. Weihnachtsfeiertag", "erster_weihnachtstag", 11,
     "der 1. Weihnachtsfeiertag (25. Dezember)"),
    (dt.date(2026, 12, 26), "2. Weihnachtsfeiertag", "zweiter_weihnachtstag", 12,
     "der 2. Weihnachtsfeiertag (26. Dezember)"),
]
TOKENS = {PREFIX + key for _, _, key, _, _ in EXPECTED_2026}
ORDINAL_OF = {key: n for _, _, key, n, _ in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _, _ in EXPECTED_2026}
STATUTE_TEXT = {key: text for _, _, key, _, text in EXPECTED_2026}
LAND_KEYS = {"ostersonntag", "pfingstsonntag", "reformationstag"}
# 사람이 승인한 신규 key(이 피드에서 처음 쓴다). 그 밖의 key 는 기존 확립값이어야 한다.
APPROVED_NEW_KEYS = {"ostersonntag", "pfingstsonntag"}

# source_todo 가 말해야 하는 실측 경계. 낱말이 아니라 사실을 고정한다.
TODO_MUST_SAY = (
    "1991",        # 원법
    "S. 44",
    "S. 514",      # 1994-12-19 개정
    "Nr. 12·26",   # BRAVORS 1994 목록에 있는 것
    "2015",        # 마지막 개정 — Abs. 2 만
    "Abs. 2",
    "실물",        # 잔존 경로
)

# 다른 독일 피드 — rules/ 스캔(tests/test_de_scope.py 와 같은 조건). 손으로 적지 않는다.
RULES_DIR = Path(__file__).resolve().parents[1] / "rules"
OTHER_GERMAN_FEEDS = {
    p.name: importlib.import_module(f"rules.{p.name}.feed")
    for p in sorted(RULES_DIR.iterdir())
    if p.is_dir()
    and (p.name == "de" or p.name.startswith("de_"))
    and p.name != "de_bb"
    and (p / "feed.py").is_file()
}


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
# a. 첫 단언 — feiertage-api 2026 BB 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    assert len(FEIERTAGE_API_2026_BB) == 12
    assert all(h == "" for h in FEIERTAGE_API_2026_BB_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_BB.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_twelve_bb_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_bb.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_bb(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    bb = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= bb
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + k for k in LAND_KEYS}


# ---------------------------------------------------------------------------
# c. 연도별 건수 · 두 일요일
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_twelve_and_the_same_token_set(events, year):
    assert len(_year(events, year)) == 12
    assert {e.token for e in _year(events, year)} == TOKENS


@pytest.mark.parametrize("year", range(2020, 2032))
def test_easter_and_whit_sunday_are_sundays_seven_weeks_apart(events, year):
    by_token = {e.token.removeprefix(PREFIX): e.day for e in _year(events, year)}
    assert by_token["ostersonntag"].weekday() == 6
    assert by_token["pfingstsonntag"].weekday() == 6
    assert by_token["pfingstsonntag"] - by_token["ostersonntag"] == dt.timedelta(days=49)
    assert by_token["ostermontag"] - by_token["ostersonntag"] == dt.timedelta(days=1)


def test_a_fixed_holiday_on_a_sunday_stays_and_adds_nothing():
    """§ 2 에 이동 조항이 없다. 2021-10-03 은 일요일이고 그 해도 12 건이다."""
    sunday = dt.date(2021, 10, 3)
    assert sunday.weekday() == 6
    year_events = feed.events(dt.date(2021, 1, 1), dt.date(2021, 12, 31))
    assert len(year_events) == 12
    on_sunday = [e.token for e in year_events if e.day == sunday]
    assert on_sunday == [PREFIX + "tag_der_deutschen_einheit"]


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 다른 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건과 Reformationstag 는 다른 피드와 같은 날 같은 항목이다. 접두사가
    유일한 방벽이다. 비교 대상은 rules/ 스캔이라 새 주가 생기면 저절로 든다."""
    assert "de" in OTHER_GERMAN_FEEDS and len(OTHER_GERMAN_FEEDS) >= 2
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for name, other in OTHER_GERMAN_FEEDS.items():
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{name} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), name


# ---------------------------------------------------------------------------
# e. 신규 key 는 승인된 둘뿐
# ---------------------------------------------------------------------------


def test_only_the_two_approved_keys_are_new(events):
    end = dt.date(2026, 12, 31)
    established = set()
    for name, other in OTHER_GERMAN_FEEDS.items():
        prefix = "" if name == "de" else f"{name}-"
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == APPROVED_NEW_KEYS
    assert ours == set(NAME_OF)


def test_the_token_charset_has_no_digits_without_one_offs(events):
    for e in events:
        assert re.fullmatch(r"[a-z][a-z_]*", e.token.removeprefix(PREFIX)), e.token


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# f. 하니스 — python-holidays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_bb(events, year):
    """python-holidays 의 DE(subdiv='BB') 와 날짜 집합만 대조한다. 이름은 보지 않는다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="BB", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY
# ---------------------------------------------------------------------------


def test_summaries_drop_only_the_article_and_the_brackets(rendered, events):
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        stripped = re.sub(r"\s*\(.*\)$", "", re.sub(r"^(der|das) ", "", statute))
        assert e.summary == NAME_OF[key] == stripped, key
        assert statute in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert not any(s.startswith(("der ", "das ")) or "(" in s for s in summaries)
    expected = {"Reformationsfest", "Tag der deutschen Einheit", "Christi Himmelfahrtstag"}
    assert expected <= set(summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_bb_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·브란덴부르크 공휴일" in head
    assert "X-WR-TIMEZONE:Europe/Berlin" in head
    assert "PRODID:-//lunalism//holidays.lunalism.com//KO" in head


def test_every_event_is_transparent_free_and_first_sequence(rendered):
    for block in _blocks(rendered):
        assert _prop(block, "TRANSP") == "TRANSPARENT"
        assert _prop(block, "X-MICROSOFT-CDO-BUSYSTATUS") == "FREE"
        assert _prop(block, "SEQUENCE") in ("", "0")


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
# h. 근거 — 열거 순번 인용, verified 전건 false, 경계 서술, 일회성 검색 사실
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def _source(entry) -> str:
    return " ".join(entry["source"].split())


def test_the_tables_hold_twelve_entries_each_citing_its_ordinal_and_wording():
    """§ 2 Abs. 1 에 번호가 없으므로 '열거 n번째' 로 지시하고(BW 전례) 그 자구를 따옴표로
    담는다. 현행 자구를 읽은 통합본과 날짜 대조원을 든다."""
    entries = _raw_entries()
    assert len(entries) == 12
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        source = _source(entry)
        cite = f"Feiertagsgesetz(BB) § 2 Abs. 1, 열거 {ORDINAL_OF[key]}번째 '{STATUTE_TEXT[key]}'"
        assert cite in source, key
        assert "BRAVORS" in source, key
        assert "feiertage-api 2026 BB" in source, key
        assert entry["name"] == NAME_OF[key], key


def test_the_scopes_split_nine_nationwide_from_three_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == LAND_KEYS
    assert {k for k, e in by_key.items() if e["scope"] == "bundesweit"} == set(NAME_OF) - LAND_KEYS


def test_all_twelve_are_false_and_their_todo_states_the_measured_boundary():
    entries = _raw_entries()
    assert [e["key"] for e in entries if e["verified"]] == []
    for entry in entries:
        assert entry["verified"] is False, entry["key"]
        todo = " ".join((entry.get("source_todo") or "").split())
        assert todo, entry["key"]
        for must in TODO_MUST_SAY:
            assert must in todo, (entry["key"], must)


def test_the_table_header_records_the_one_off_search_as_a_search_fact():
    """§ 2 Abs. 3 은 주 정부가 명령으로 일회성 공휴일을 정할 수 있게 한다. 발행 범위 안에
    그런 명령이 있는지는 검색 사실로 적는다 — 판정어가 아니라 '찾지 못함(범위)'. 검색한
    화면(현행·Archiv)·검색어·교차 대조를 든다."""
    header = feed.SOLAR_PATH.read_text(encoding="utf-8").split("holidays:")[0]
    assert "§ 2 Abs. 3" in header
    assert "찾지 못함" in header
    assert "Archiv" in header and "außer Kraft" in header
    for word in ("Feiertag", "Feiertage", "Feiertagsgesetz", "einmalig"):
        assert f"'{word}'" in header, word
    assert "feiertage-api" in header
    assert "무개정" not in header


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert "\n\n근거: " in e.description, e
        assert _source(by_key[e.token.removeprefix(PREFIX)]) in e.description
        assert e.description.split("\n")[-1].startswith("근거: "), e


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_bb.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_bb_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_bb.ics"
    assert got["events"] == 12 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (주 피드 공통 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "easter_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Ostersonntag", "easter_offset": 0,
                           "verified": False, "source": "test", "scope": "land"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("ostersonntag\n", id="끝 개행"),
        pytest.param("Ostersonntag", id="대문자"),
        pytest.param("0_ostern", id="숫자 시작"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "easter_offset")


def test_an_approved_new_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "ostersonntag"), "easter_offset")
    assert entry["key"] == "ostersonntag"
