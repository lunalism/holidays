"""독일·작센 주 피드 — rules/de_sn/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_sn.ics 는 작센 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über Sonn- und Feiertage im Freistaat Sachsen (SächsSFG) vom 10. November
    1992 § 1 Abs. 1 이다 — 번호 없는 열거 12 건 중 지정 지역만의 Fronleichnam(7번째)을 뺀 11 건.
    연 단위 구성은 고정 6 + 부활절 이동 4 + Totensonntag 기준 1 = 11 건, 전국 공통 9 건에
    Reformationsfest(10. 31.)와 Buß- und Bettag 가 더해진다. 신규 key 는 buss_und_bettag 하나다
    (사람의 승인, 2026-11-18). 대체공휴일(이동) 규칙은 없다.

Buß- und Bettag 는 조문이 이름만 든다. 날짜는 Totensonntag − 4 일이다 — Totensonntag 는 같은 법
§ 2 가 「letzter Sonntag vor dem 1. Advent」 로 정의하고(대림절 첫째 주일 = 11월 27일–12월 3일의
일요일), 「am letzten Mittwoch vor dem Totensonntag」 은 작센 주의회 청원 보고서 2023 의 문장이다.
표는 그 오프셋을 totensonntag_offset 으로 둔다(사람의 결정 S2, de_sn 로더에만).

현행 자구는 REVOSax 통합본(「Fassung gültig ab: 7. Mai 2025」)으로 읽었다. 공포본(1992 원법·2002
개정)은 받지 못해 전 항목 verified: false 다(S4).

SUMMARY 는 조문 표기에서 끝의 괄호 날짜만 뺀 것이다(관사가 없다). 원문은 DESCRIPTION 에.

    a. feiertage-api 2026 SN 실측 11 건(지정 지역 Fronleichnam 제외) == de_sn 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_sn.ics, 차집합 token 은 reformationstag·buss_und_bettag
    c. 연도별 11 건
    d. UID — 전 항목 de_sn- 접두사, 다른 독일 피드(rules/ 스캔)와 겹치지 않음
    e. key — buss_und_bettag 밖은 기존 확립값
    f. 하니스 — python-holidays(subdiv='SN')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·SUMMARY
    h. 근거 — 열거 순번 인용, REVOSax 서지, Buß- und Bettag 의 날짜 근거, 전 항목 false 와
       source_todo, 머리 주석의 승인·범위 밖·일회성 공백·교차 확인
    i. Buß- und Bettag·Totensonntag 의 계산 — 1990–2100
    j. 로더 — 모르는 필드·최상위 키·중복 키 거부, totensonntag_offset 은 int 만

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

from core import ics
from rules.de import feed as de_feed
from rules.de_sn import feed
from rules.de_sn import status as de_sn_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_sn-"

# feiertage-api.de 2026 SN 실측(2026-09-30, ?jahr=2026&nur_land=SN). 12 건 중 hinweis 가 붙은
# Fronleichnam(지정 지역만 — 범위 밖)을 뺀 11 건, 측정값 그대로.
# 출처: docs/research/report_batch2_survey/fapi_2026_summary.txt.
FEIERTAGE_API_2026_SN = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Karfreitag": dt.date(2026, 4, 3),
    "Ostermontag": dt.date(2026, 4, 6),
    "Tag der Arbeit": dt.date(2026, 5, 1),
    "Christi Himmelfahrt": dt.date(2026, 5, 14),
    "Pfingstmontag": dt.date(2026, 5, 25),
    "Tag der Deutschen Einheit": dt.date(2026, 10, 3),
    "Reformationstag": dt.date(2026, 10, 31),
    "Buß- und Bettag": dt.date(2026, 11, 18),
    "1. Weihnachtstag": dt.date(2026, 12, 25),
    "2. Weihnachtstag": dt.date(2026, 12, 26),
}
FEIERTAGE_API_2026_SN_FRONLEICHNAM = dt.date(2026, 6, 4)

# § 1 Abs. 1 의 열거 순번·SUMMARY 표기·조문 자구(끝 쉼표·마침표 없이). 날짜 순서.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahr", "neujahr", 1, "Neujahr (1. Januar)"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2, "Karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 3, "Ostermontag"),
    (dt.date(2026, 5, 1), "Tag der Arbeit", "erster_mai", 4, "Tag der Arbeit (1. Mai)"),
    (dt.date(2026, 5, 14), "Christi Himmelfahrt", "christi_himmelfahrt", 5, "Christi Himmelfahrt"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 6, "Pfingstmontag"),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", 8,
     "Tag der Deutschen Einheit (3. Oktober)"),
    (dt.date(2026, 10, 31), "Reformationsfest", "reformationstag", 9,
     "Reformationsfest (31. Oktober)"),
    (dt.date(2026, 11, 18), "Buß- und Bettag", "buss_und_bettag", 10, "Buß- und Bettag"),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", 11,
     "1. Weihnachtstag (25. Dezember)"),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", 12,
     "2. Weihnachtstag (26. Dezember)"),
]
TOKENS = {PREFIX + key for _, _, key, _, _ in EXPECTED_2026}
ORDINAL_OF = {key: n for _, _, key, n, _ in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _, _ in EXPECTED_2026}
STATUTE_TEXT = {key: text for _, _, key, _, text in EXPECTED_2026}
LAND_KEYS = {"reformationstag", "buss_und_bettag"}
NEW_KEYS = {"buss_und_bettag"}

# 모든 항목 source 가 들어야 하는 REVOSax 서지.
REVOSAX_MUST_SAY = (
    "REVOSax",
    "https://www.revosax.sachsen.de/vorschrift/3997-SaechsSFG",
    "Fassung gültig ab: 7. Mai 2025",
    "2026-11-18",
)

# Buß- und Bettag 의 source 가 들어야 하는 것(S3): 이름만 든다는 사실, § 2 의 Totensonntag 정의,
# 주의회 보고서의 문장·주소·열람일.
BUSSTAG_MUST_SAY = (
    "날짜를 정하지 않는다",
    "§ 2",
    "der Totensonntag (letzter Sonntag vor dem 1. Advent)",
    "Der Landesgesetzgeber entschied sich dafür, den Buß- und Bettag als gesetzlichen Feiertag am "
    "letzten Mittwoch vor dem Totensonntag beizubehalten.",
    "https://www.landtag.sachsen.de/download/publikationen/SLT_BR_Petitionsbericht_2023_Web_PDFUA.pdf",
    "68",
    "2026-11-18",
)

# 전 항목 source_todo 가 말해야 하는 관측 사실(S4).
TODO_MUST_SAY = (
    "SächsGVBl. 1992 Nr. 35",
    "1999",
    "2002 Nr. 9",
    "유료",
    "2026-11-18",
)

# 다른 독일 피드 — rules/ 스캔(tests/test_de_scope.py 와 같은 조건). 손으로 적지 않는다.
RULES_DIR = Path(__file__).resolve().parents[1] / "rules"
OTHER_GERMAN_FEEDS = {
    p.name: importlib.import_module(f"rules.{p.name}.feed")
    for p in sorted(RULES_DIR.iterdir())
    if p.is_dir()
    and (p.name == "de" or p.name.startswith("de_"))
    and p.name != "de_sn"
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


def _last_wednesday_before_nov_23(year: int) -> dt.date:
    """「11월 23일보다 엄격히 앞선 마지막 수요일」 — 로더와 따로 센다."""
    day = dt.date(year, 11, 22)
    while day.weekday() != 2:
        day -= dt.timedelta(days=1)
    return day


# ---------------------------------------------------------------------------
# a. 첫 단언 — feiertage-api 2026 SN 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    assert len(FEIERTAGE_API_2026_SN) == 11
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_SN.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}
    assert FEIERTAGE_API_2026_SN_FRONLEICHNAM not in ours


def test_2026_has_exactly_the_eleven_sn_holidays_in_date_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_sn.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_sn(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    sn = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= sn
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + k for k in LAND_KEYS}


# ---------------------------------------------------------------------------
# c. 연도별 건수
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_eleven_and_the_same_token_set(events, year):
    assert len(_year(events, year)) == 11
    assert {e.token for e in _year(events, year)} == TOKENS


def test_a_fixed_holiday_on_a_sunday_stays_and_adds_nothing():
    """§ 1 에 이동 조항이 없다. 2021-10-03·10-31 은 일요일이고 그 해도 11 건이다."""
    year_events = feed.events(dt.date(2021, 1, 1), dt.date(2021, 12, 31))
    assert len(year_events) == 11
    for day, key in ((dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
                     (dt.date(2021, 10, 31), "reformationstag")):
        assert day.weekday() == 6
        assert [e.token for e in year_events if e.day == day] == [PREFIX + key]


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


def test_the_new_key_reaches_the_uid_as_approved(rendered):
    """S1 — buss_und_bettag 는 발행 UID 의 일부다: {날짜}-de_sn-buss_und_bettag."""
    uids = {_prop(b, "UID") for b in _blocks(rendered)}
    assert f"20261118-de_sn-buss_und_bettag@{ics.UID_DOMAIN}" in uids


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건·Reformationsfest 는 다른 피드와 같은 날 같은 key 다. 접두사가 유일한 방벽이다.
    비교 대상은 rules/ 스캔이라 새 주가 생기면 저절로 든다."""
    assert "de" in OTHER_GERMAN_FEEDS and len(OTHER_GERMAN_FEEDS) >= 2
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    assert ours
    for name, other in OTHER_GERMAN_FEEDS.items():
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{name} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), name


# ---------------------------------------------------------------------------
# e. key — buss_und_bettag 밖은 기존 확립값
# ---------------------------------------------------------------------------


def test_only_the_approved_key_is_new(events):
    end = dt.date(2026, 12, 31)
    established = set()
    for name, other in OTHER_GERMAN_FEEDS.items():
        prefix = "" if name == "de" else f"{name}-"
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == NEW_KEYS
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
def test_the_dates_agree_with_python_holidays_sn(events, year):
    """python-holidays 의 DE(subdiv='SN') 와 날짜 집합만 대조한다. 이름은 보지 않는다.
    라이브러리의 기본 범주에 Fronleichnam 은 없다(지정 지역 — 이 피드도 싣지 않는다)."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="SN", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY
# ---------------------------------------------------------------------------


def test_summaries_drop_only_the_parenthesised_date(rendered, events):
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        stripped = re.sub(r" \([^)]*\)$", "", statute)
        assert e.summary == NAME_OF[key] == stripped, key
        assert statute in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert not any("(" in s for s in summaries)
    assert {"Reformationsfest", "Buß- und Bettag", "Neujahr"} <= set(summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_sn_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·작센 공휴일" in head
    assert "X-WR-TIMEZONE:Europe/Berlin" in head
    assert "PRODID:-//lunalism//holidays.lunalism.com//KO" in head


def test_the_land_names(rendered):
    assert feed.LAND_NAME == "작센"
    assert feed.LAND_NAME_DE == "Sachsen"


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
# h. 근거 — 열거 순번 인용, 서지, verified, 경계 서술, 머리 주석
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH, feed.TOTENSONNTAG_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def _source(entry) -> str:
    return " ".join(entry["source"].split())


def _header(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("holidays:")[0]


def test_the_tables_hold_eleven_entries_each_citing_its_position_and_wording():
    """§ 1 Abs. 1 에 번호가 없으므로 '열거 n번째' 로 지시하고(BB 전례) 그 자구를 따옴표로 담는다.
    REVOSax 통합본의 서지를 든다."""
    entries = _raw_entries()
    assert len(entries) == 11
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        source = _source(entry)
        cite = f"SächsSFG § 1 Abs. 1, 열거 {ORDINAL_OF[key]}번째 '{STATUTE_TEXT[key]}'"
        assert cite in source, key
        for must in REVOSAX_MUST_SAY:
            assert must in source, (key, must)
        assert "feiertage-api 2026 SN" in source, key
        assert entry["name"] == NAME_OF[key], key


def test_the_busstag_source_states_the_gap_and_the_date_basis():
    """S3 — 조문은 이름만 든다. 날짜 관행은 주의회 보고서의 문장에서 온다. § 2 의 Totensonntag
    정의를 따옴표로 든다. Hessen 1971 은 source 에 두지 않는다(머리 주석의 교차 확인 한 줄)."""
    entry = {e["key"]: e for e in _raw_entries()}["buss_und_bettag"]
    source = _source(entry)
    for must in BUSSTAG_MUST_SAY:
        assert must in source, must
    for banned in ("Hessen", "1971", "Trinitatis"):
        assert banned not in source, banned
    assert entry["totensonntag_offset"] == -4


def test_only_busstag_has_the_offset_field():
    tables = {
        path.name: yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"]
        for path in (feed.SOLAR_PATH, feed.EASTER_PATH, feed.TOTENSONNTAG_PATH)
    }
    offsets = [e["key"] for es in tables.values() for e in es if "totensonntag_offset" in e]
    assert offsets == ["buss_und_bettag"]
    assert [e["key"] for e in tables[feed.TOTENSONNTAG_PATH.name]] == ["buss_und_bettag"]


def test_the_scopes_split_nine_nationwide_from_two_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == LAND_KEYS
    assert {k for k, e in by_key.items() if e["scope"] == "bundesweit"} == set(NAME_OF) - LAND_KEYS


def test_every_entry_is_false_and_its_todo_states_the_observed_gazette_access():
    for entry in _raw_entries():
        assert entry["verified"] is False, entry["key"]
        todo = " ".join((entry.get("source_todo") or "").split())
        assert todo, entry["key"]
        for must in TODO_MUST_SAY:
            assert must in todo, (entry["key"], must)


def test_the_sources_stay_short():
    """S8 — source 는 자구·서지·날짜 근거만. 조사 경위는 머리 주석과 PR 본문에 둔다."""
    for entry in _raw_entries():
        source = _source(entry)
        limit = 1100 if entry["key"] == "buss_und_bettag" else 400
        assert len(source) <= limit, (entry["key"], len(source))
        for banned in ("Archiv", "recht-sachsen", "Heizkosten", "valid_day", "[추론]"):
            assert banned not in source, (entry["key"], banned)


def test_the_header_records_the_approval_scope_the_gap_and_the_cross_check():
    """S1 승인(날짜), S5 일회성 공백(사실), S7 범위 밖, Hessen 교차 확인 한 줄, 추론 표기."""
    header = _header(feed.SOLAR_PATH) + _header(feed.TOTENSONNTAG_PATH)
    for must in (
        "buss_und_bettag", "승인", "2026-11-18",
        "Fronleichnam", "§ 2a", "§ 3", "8. Mai",
        "2020", "Nr. 1–40", "38a", "39a", "2021 Nr. 1–14", "valid_day",
        "einmalig", "[추론]",
        "Hessen GVBl. 1971", "S. 344",
        "totensonntag_offset",
    ):
        assert must in header, must
    hessen = [ln for ln in header.splitlines() if "Hessen GVBl. 1971" in ln]
    assert len(hessen) == 1, hessen
    for word in ("통과", "충족했다", "무개정"):
        assert word not in header, word


def test_the_package_points_at_no_dead_or_private_path():
    for path in sorted((RULES_DIR / "de_sn").iterdir()):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert "/tmp/" not in text, path.name
            assert "holidays-reports" not in text, path.name


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert "\n\n근거: " in e.description, e
        assert _source(by_key[e.token.removeprefix(PREFIX)]) in e.description
        assert e.description.split("\n")[-1].startswith("근거: "), e


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "totensonntag_offset", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_sn.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_sn_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_sn.ics"
    assert got["events"] == 11 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# i. Buß- und Bettag·Totensonntag 의 계산 — 1990–2100
# ---------------------------------------------------------------------------

LONG_RANGE = range(1990, 2101)


@pytest.fixture(scope="module")
def busstage():
    out = {}
    for e in feed.events(dt.date(1990, 1, 1), dt.date(2100, 12, 31)):
        if e.token == PREFIX + "buss_und_bettag":
            out[e.day.year] = e.day
    return out


def test_totensonntag_is_a_sunday_from_20_to_26_november():
    for year in LONG_RANGE:
        day = feed._totensonntag(year)
        assert day.weekday() == 6, year
        assert dt.date(year, 11, 20) <= day <= dt.date(year, 11, 26), (year, day)
        assert day + dt.timedelta(days=7) == feed._advent1(year), year


def test_advent1_is_the_sunday_from_27_november_to_3_december():
    for year in LONG_RANGE:
        day = feed._advent1(year)
        assert day.weekday() == 6, year
        assert dt.date(year, 11, 27) <= day <= dt.date(year, 12, 3), (year, day)


def test_busstag_is_a_wednesday_from_16_to_22_november_every_year(busstage):
    assert sorted(busstage) == list(LONG_RANGE)
    for year, day in busstage.items():
        assert day.weekday() == 2, year
        assert dt.date(year, 11, 16) <= day <= dt.date(year, 11, 22), (year, day)


def test_busstag_equals_the_last_wednesday_strictly_before_23_november(busstage):
    """다른 꼴로 센 같은 날 — 로더(Totensonntag − 4)와 독립인 계산."""
    for year, day in busstage.items():
        assert day == _last_wednesday_before_nov_23(year), year


def test_busstag_dates_2026_to_2031(busstage):
    assert [busstage[y] for y in range(2026, 2032)] == [
        dt.date(2026, 11, 18), dt.date(2027, 11, 17), dt.date(2028, 11, 22),
        dt.date(2029, 11, 21), dt.date(2030, 11, 20), dt.date(2031, 11, 19),
    ]


# ---------------------------------------------------------------------------
# j. 로더 — 필드 집합과 totensonntag_offset (de_sn 로더에만 있는 규약)
# ---------------------------------------------------------------------------


def _write(tmp_path, name: str, entries: list) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump({"holidays": entries}, allow_unicode=True), encoding="utf-8")
    return path


def _busstag_entry(**extra) -> dict:
    entry = {"key": "buss_und_bettag", "name": "Buß- und Bettag", "totensonntag_offset": -4,
             "verified": False, "source": "test", "scope": "land"}
    entry.update(extra)
    return entry


def _easter_entry(**extra) -> dict:
    entry = {"key": "karfreitag", "name": "Karfreitag", "easter_offset": -2,
             "verified": False, "source": "test", "scope": "bundesweit"}
    entry.update(extra)
    return entry


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("karfreitag\n", id="끝 개행"),
        pytest.param("Karfreitag", id="대문자"),
        pytest.param("0_karfreitag", id="숫자 시작"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    path = _write(tmp_path, "easter_holidays.yaml", [_easter_entry(key=bad_key)])
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(path, "easter_offset")


def test_a_valid_offset_table_loads(tmp_path):
    path = _write(tmp_path, "totensonntag_holidays.yaml", [_busstag_entry()])
    [entry] = feed._load(path, "totensonntag_offset")
    assert entry["totensonntag_offset"] == -4


@pytest.mark.parametrize(
    "field",
    [
        pytest.param("weekday", id="weekday"),
        pytest.param("advent_offset", id="advent_offset — 고르지 않은 꼴"),
        pytest.param("effective_from", id="effective_from — de_mv 의 필드"),
        pytest.param("easter_offset", id="다른 표의 날짜 필드"),
        pytest.param("sourc", id="오타"),
    ],
)
def test_an_unknown_field_stops_the_load(tmp_path, field):
    path = _write(tmp_path, "totensonntag_holidays.yaml", [_busstag_entry(**{field: 1})])
    with pytest.raises(ics.IcsError, match="모르는 필드"):
        feed._load(path, "totensonntag_offset")


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("-4", id="문자열"),
        pytest.param(-4.0, id="실수"),
        pytest.param(True, id="bool"),
        pytest.param(None, id="빈 값"),
    ],
)
def test_the_offset_must_be_an_int(tmp_path, value):
    entry = _busstag_entry(totensonntag_offset=value)
    path = _write(tmp_path, "totensonntag_holidays.yaml", [entry])
    with pytest.raises(ics.IcsError, match="totensonntag_offset"):
        feed._load(path, "totensonntag_offset")


def test_an_unknown_top_level_key_stops_the_load(tmp_path):
    path = tmp_path / "totensonntag_holidays.yaml"
    path.write_text(
        yaml.safe_dump({"weekday_rule": "wednesday", "holidays": [_busstag_entry()]},
                       allow_unicode=True),
        encoding="utf-8",
    )
    with pytest.raises(ics.IcsError, match="최상위의 모르는 키"):
        feed._load(path, "totensonntag_offset")


def test_a_duplicate_key_stops_the_load(tmp_path):
    path = tmp_path / "totensonntag_holidays.yaml"
    path.write_text(
        "holidays:\n"
        "  - key: buss_und_bettag\n    name: Buß- und Bettag\n    scope: land\n"
        "    verified: false\n    source: test\n"
        "    totensonntag_offset: -4\n    totensonntag_offset: -3\n",
        encoding="utf-8",
    )
    with pytest.raises(ics.IcsError, match="중복 키"):
        feed._load(path, "totensonntag_offset")
