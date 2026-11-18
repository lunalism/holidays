"""독일·메클렌부르크포어포메른 주 피드 — rules/de_mv/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_mv.ics 는 메클렌부르크포어포메른 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über Sonn- und Feiertage (Feiertagsgesetz Mecklenburg-Vorpommern -
    FTG M-V -) in der Fassung der Bekanntmachung vom 8. März 2002 § 2 Abs. 1 이다 — Nr. 1–11.
    연 단위 구성은 고정 7 + 부활절 이동 4 = 11 건, 전국 공통 9 건에 Frauentag(3. 8.)와
    Reformationstag(10. 31.)가 더해진다. key 는 전부 기존 확립값이다. 대체공휴일(이동) 규칙은 없다.

Frauentag 는 2022-07-13 부터다. 공식 법령 포털의 § 2 조문 단위 문서가 「Gültig ab: 13.07.2022」 를
적고, 표는 그 값을 effective_from 으로 둔다 — 날짜, 포함 경계, kr 의 항목별 effective_from 과
같은 뜻이다.
그래서 2020–2022 는 10 건, 2023 부터 11 건이다.

현행 자구는 공식 법령 포털 Landesrecht M-V 의 § 2 조문 단위 문서(jlr-NNLMV00007A2FNN00000000003)로
읽었다. 그것을 전 항목 자구의 공식 현행 조문으로 삼은 것은 사람의 결정이다(M1). 공포본은 해시와 함께
받지 못해 전 항목 verified: false 다(M3) — 관보 화면은 2026 년 호만 싣고 GVOBl. M-V 2014–2025
는 E-Mail 로 요청하라고 적는다(같은 사이트의 다른 화면은 2020–2025 가 온라인에 있다고 적는다).

SUMMARY 는 조문 표기에서 관사 der 와 괄호의 날짜를 뺀 것이다. 원문은 DESCRIPTION 에.

    a. feiertage-api 2026 MV 실측 11 건(hinweis 전부 공란) == de_mv 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_mv.ics, 차집합 token 은 2022 까지 reformationstag, 2023 부터
       frauentag·reformationstag
    c. 연도별 건수 — 2020–2022 10 건, 2023–2031 11 건
    d. UID — 전 항목 de_mv- 접두사, 다른 독일 피드(rules/ 스캔)와 겹치지 않음
    e. 신규 key 없음
    f. 하니스 — python-holidays(subdiv='MV')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·SUMMARY
    h. 근거 — Nr. 인용, 포털 서지, Frauentag 의 「Gültig ab」, 전 항목 false 와 source_todo 경계,
       머리 주석의 범위 밖·관보 공백·포털 검색
    i. 로더 — 모르는 필드 거부, effective_from 은 date 만(연도·문자열·datetime 거부), 포함 경계,
       kr 과 같은 판정, 끝 필드 없음

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
from rules.de_mv import feed
from rules.de_mv import status as de_mv_status
from rules.kr import holiday_calendar as kr_calendar

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_mv-"

# feiertage-api.de 2026 MV 실측(2026-09-30, ?jahr=2026&nur_land=MV). 11 건, 측정값 그대로.
# 출처: docs/research/report_batch2_survey/fapi_2026_summary.txt. hinweis 는 열한 개 모두 공란.
FEIERTAGE_API_2026_MV = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Frauentag": dt.date(2026, 3, 8),
    "Karfreitag": dt.date(2026, 4, 3),
    "Ostermontag": dt.date(2026, 4, 6),
    "Tag der Arbeit": dt.date(2026, 5, 1),
    "Christi Himmelfahrt": dt.date(2026, 5, 14),
    "Pfingstmontag": dt.date(2026, 5, 25),
    "Tag der Deutschen Einheit": dt.date(2026, 10, 3),
    "Reformationstag": dt.date(2026, 10, 31),
    "1. Weihnachtstag": dt.date(2026, 12, 25),
    "2. Weihnachtstag": dt.date(2026, 12, 26),
}
FEIERTAGE_API_2026_MV_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_MV}

# § 2 Abs. 1 의 Nr.·SUMMARY 표기·조문 자구. 날짜 순서.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1, "der Neujahrstag (1. Januar)"),
    (dt.date(2026, 3, 8), "Frauentag", "frauentag", 2, "der Frauentag (8. März)"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 3, "der Karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 4, "der Ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 5, "der 1. Mai"),
    (dt.date(2026, 5, 14), "Christi-Himmelfahrtstag", "christi_himmelfahrt", 6,
     "der Christi-Himmelfahrtstag"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 7, "der Pfingstmontag"),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", 8,
     "der Tag der Deutschen Einheit (3. Oktober)"),
    (dt.date(2026, 10, 31), "Reformationstag", "reformationstag", 9,
     "der Reformationstag (31. Oktober)"),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", 10,
     "der 1. Weihnachtstag (25. Dezember)"),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", 11,
     "der 2. Weihnachtstag (26. Dezember)"),
]
TOKENS = {PREFIX + key for _, _, key, _, _ in EXPECTED_2026}
NR_OF = {key: nr for _, _, key, nr, _ in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _, _ in EXPECTED_2026}
STATUTE_TEXT = {key: text for _, _, key, _, text in EXPECTED_2026}
LAND_KEYS = {"frauentag", "reformationstag"}

# Frauentag 의 시작. 포털 § 2 의 「Gültig ab: 13.07.2022」 그대로(사람의 결정 M2).
FRAUENTAG_FROM = dt.date(2022, 7, 13)
YEARS_WITHOUT_FRAUENTAG = (2020, 2021, 2022)

# 모든 항목 source 가 들어야 하는 포털 서지 — URL·조문 단위 id·Fassung/Gültig ab·Stand·열람일.
PORTAL_MUST_SAY = (
    "Landesrecht Mecklenburg-Vorpommern",
    "https://www.landesrecht-mv.de/bsmv/document/jlr-NNLMV00007A2FNN00000000003",
    "jlr-NNLMV00007A2F",
    "Fassung vom: 07.07.2022",
    "Gültig ab: 13.07.2022",
    "zuletzt geändert durch Gesetz vom 7. Juli 2022 (GVOBl. M-V S. 427)",
    "2026-11-18",
)

# 전 항목 source_todo 가 말해야 하는 관측 사실(M3).
TODO_MUST_SAY = (
    "https://land-mv.de/landeregierung/jm/gesetz-verordnungsblaetter",
    "2014-2025",
    "E-Mail",
    "2026-11-18",
    "2022 Nr. 31 S. 427",
    "263,235",
    "2026-09-30",
)

# 다른 독일 피드 — rules/ 스캔(tests/test_de_scope.py 와 같은 조건). 손으로 적지 않는다.
RULES_DIR = Path(__file__).resolve().parents[1] / "rules"
OTHER_GERMAN_FEEDS = {
    p.name: importlib.import_module(f"rules.{p.name}.feed")
    for p in sorted(RULES_DIR.iterdir())
    if p.is_dir()
    and (p.name == "de" or p.name.startswith("de_"))
    and p.name != "de_mv"
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


def _tokens_for(year: int) -> set:
    if year in YEARS_WITHOUT_FRAUENTAG:
        return TOKENS - {PREFIX + "frauentag"}
    return TOKENS


# ---------------------------------------------------------------------------
# a. 첫 단언 — feiertage-api 2026 MV 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    assert len(FEIERTAGE_API_2026_MV) == 11
    assert all(h == "" for h in FEIERTAGE_API_2026_MV_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_MV.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_eleven_mv_holidays_in_date_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_mv.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_mv(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    mv = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= mv
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    expected = {PREFIX + k for k in LAND_KEYS}
    if year in YEARS_WITHOUT_FRAUENTAG:
        expected -= {PREFIX + "frauentag"}
    assert extra_tokens == expected


# ---------------------------------------------------------------------------
# c. 연도별 건수 — Frauentag 의 경계
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_its_count_and_token_set(events, year):
    expected = 10 if year in YEARS_WITHOUT_FRAUENTAG else 11
    assert len(_year(events, year)) == expected
    assert {e.token for e in _year(events, year)} == _tokens_for(year)


@pytest.mark.parametrize("year", YEARS_WITHOUT_FRAUENTAG)
def test_frauentag_is_absent_before_its_start(events, year):
    assert dt.date(year, 3, 8) not in _days(events, year)
    assert PREFIX + "frauentag" not in {e.token for e in _year(events, year)}


@pytest.mark.parametrize("year", range(2023, 2032))
def test_frauentag_is_present_from_2023(events, year):
    [e] = [e for e in _year(events, year) if e.token == PREFIX + "frauentag"]
    assert e.day == dt.date(year, 3, 8)
    assert e.summary == "Frauentag"


def test_a_fixed_holiday_on_a_sunday_stays_and_adds_nothing():
    """§ 2 에 이동 조항이 없다. 2021-10-03·10-31 은 일요일이고 그 해도 10 건이다."""
    year_events = feed.events(dt.date(2021, 1, 1), dt.date(2021, 12, 31))
    assert len(year_events) == 10
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


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건·Frauentag(de_be)·Reformationstag 는 다른 피드와 같은 날 같은 항목이다.
    접두사가 유일한 방벽이다. 비교 대상은 rules/ 스캔이라 새 주가 생기면 저절로 든다."""
    assert "de" in OTHER_GERMAN_FEEDS and len(OTHER_GERMAN_FEEDS) >= 2
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for name, other in OTHER_GERMAN_FEEDS.items():
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{name} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), name


# ---------------------------------------------------------------------------
# e. 신규 key 없음
# ---------------------------------------------------------------------------


def test_no_key_is_new(events):
    end = dt.date(2026, 12, 31)
    established = set()
    for name, other in OTHER_GERMAN_FEEDS.items():
        prefix = "" if name == "de" else f"{name}-"
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == set()
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
def test_the_dates_agree_with_python_holidays_mv(events, year):
    """python-holidays 의 DE(subdiv='MV') 와 날짜 집합만 대조한다. 이름은 보지 않는다.
    라이브러리는 Frauentag 를 연 단위(2023 부터)로 둔다 — 2020–2022 가 경계를 해마다 잡는다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="MV", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY
# ---------------------------------------------------------------------------


def test_summaries_drop_the_article_and_the_parenthesised_date(rendered, events):
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        stripped = re.sub(r" \([^)]*\)$", "", re.sub(r"^der ", "", statute))
        assert e.summary == NAME_OF[key] == stripped, key
        assert statute in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert not any(s.startswith("der ") or "(" in s for s in summaries)
    assert {"Christi-Himmelfahrtstag", "Tag der Deutschen Einheit", "Frauentag"} <= set(summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_mv_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·메클렌부르크포어포메른 공휴일" in head
    assert "X-WR-TIMEZONE:Europe/Berlin" in head
    assert "PRODID:-//lunalism//holidays.lunalism.com//KO" in head


def test_the_land_names(rendered):
    assert feed.LAND_NAME == "메클렌부르크포어포메른"
    assert feed.LAND_NAME_DE == "Mecklenburg-Vorpommern"


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
# h. 근거 — Nr. 인용, 포털 서지, verified, 경계 서술, 머리 주석
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def _source(entry) -> str:
    return " ".join(entry["source"].split())


def _header(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("holidays:")[0]


def test_the_tables_hold_eleven_entries_each_citing_its_number_and_wording():
    """§ 2 Abs. 1 은 Nr. 1–11 로 나뉜다. 그 자구를 따옴표로 담고, 자구를 읽은 공식 포털 문서의
    서지(URL·조문 단위 id·Fassung/Gültig ab·법 전체의 Stand·열람일)를 든다."""
    entries = _raw_entries()
    assert len(entries) == 11
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        source = _source(entry)
        cite = (f"Feiertagsgesetz Mecklenburg-Vorpommern (FTG M-V) § 2 Abs. 1 Nr. {NR_OF[key]} "
                f"'{STATUTE_TEXT[key]}'")
        assert cite in source, key
        for must in PORTAL_MUST_SAY:
            assert must in source, (key, must)
        assert "feiertage-api 2026 MV" in source, key
        assert entry["name"] == NAME_OF[key], key


def test_only_frauentag_has_a_start_and_its_source_quotes_the_portal_basis():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if "effective_from" in e} == {"frauentag"}
    entry = by_key["frauentag"]
    assert type(entry["effective_from"]) is dt.date
    assert entry["effective_from"] == FRAUENTAG_FROM
    source = _source(entry)
    assert "Gültig ab: 13.07.2022" in source
    assert "2022-07-13" in source


def test_the_scopes_split_nine_nationwide_from_two_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == LAND_KEYS
    assert {k for k, e in by_key.items() if e["scope"] == "bundesweit"} == set(NAME_OF) - LAND_KEYS


def test_every_entry_is_false_and_its_todo_states_the_observed_gazette_gap():
    for entry in _raw_entries():
        assert entry["verified"] is False, entry["key"]
        todo = " ".join((entry.get("source_todo") or "").split())
        assert todo, entry["key"]
        for must in TODO_MUST_SAY:
            assert must in todo, (entry["key"], must)


def test_the_header_records_scope_the_gazette_gap_and_the_portal_search():
    """범위 밖(§ 2 Abs. 2 의 Gedenktag), 관보 공백(사이트의 두 서술을 판단 없이 인용), E-Mail 요청을
    하지 않았다는 것, § 2 Abs. 3 일회성 지정 확인이 포털 검색에 기댄다는 것을 적는다."""
    header = _header(feed.SOLAR_PATH)
    for must in (
        "§ 2 Abs. 2", "Gedenktag", "8. Mai",
        "§ 2 Abs. 3",
        "https://land-mv.de/thema/buergerservices-und-digitale-verwaltung",
        "Sämtliche Jahrgänge von 2020 bis 2025 stehen vollständig online zum Abruf bereit.",
        "https://land-mv.de/landeregierung/jm/gesetz-verordnungsblaetter",
        "aus den Jahren 2014-2025",
        "E-Mail",
        "2026-11-18",
        "Gültig ab: 13.07.2022",
        "jlr-NNLMV00007A2FNN00000000003",
        "[추론]",
    ):
        assert must in header, must
    for word in ("통과", "충족했다", "무개정"):
        assert word not in header, word


def test_the_package_points_at_no_dead_or_private_path():
    for path in sorted((RULES_DIR / "de_mv").iterdir()):
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
    for word in ("verified", "source_todo", "effective_from", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_mv.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    """2020–2031: Frauentag 없는 세 해 10 건 + 아홉 해 11 건 = 129."""
    got = de_mv_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_mv.ics"
    assert got["events"] == 3 * 10 + 9 * 11 == 129
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# i. 로더 — 필드 집합과 effective_from (de_mv 로더에만 있는 규약, 사람의 결정 M6)
# ---------------------------------------------------------------------------


def _write(tmp_path, name: str, entries: list) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump({"holidays": entries}, allow_unicode=True), encoding="utf-8")
    return path


def _easter_entry(**extra) -> dict:
    entry = {"key": "karfreitag", "name": "Karfreitag", "easter_offset": -2,
             "verified": False, "source": "test", "scope": "bundesweit"}
    entry.update(extra)
    return entry


def _solar_entry(**extra) -> dict:
    entry = {"key": "frauentag", "name": "Frauentag", "month": 3, "day": 8,
             "verified": False, "source": "test", "scope": "land"}
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


def test_an_established_key_loads(tmp_path):
    [entry] = feed._load(_write(tmp_path, "easter_holidays.yaml", [_easter_entry()]),
                         "easter_offset")
    assert entry["key"] == "karfreitag"


@pytest.mark.parametrize(
    "field",
    [
        pytest.param("valid_from", id="valid_from"),
        pytest.param("valid_until", id="valid_until — 끝 필드는 두지 않는다"),
        pytest.param("effective_until", id="effective_until — kr 에는 있지만 de_mv 에는 없다"),
        pytest.param("from_year", id="from_year"),
        pytest.param("sourc", id="오타"),
    ],
)
def test_an_unknown_field_stops_the_load(tmp_path, field):
    """모르는 필드를 조용히 무시하면 경계 필드가 있는데도 2020–2022 에 Frauentag 가 나간다.
    report_mv_prep B2 의 실험이 다른 주 로더에서 그것을 보였다."""
    path = _write(tmp_path, "solar_holidays.yaml", [_solar_entry(**{field: dt.date(2023, 1, 1)})])
    with pytest.raises(ics.IcsError, match="모르는 필드"):
        feed._load(path, "month", "day")


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(2023, id="연도(int)"),
        pytest.param("2022-07-13", id="문자열"),
        pytest.param(dt.datetime(2022, 7, 13, 0, 0), id="datetime"),
        pytest.param(True, id="bool"),
    ],
)
def test_effective_from_must_be_a_date(tmp_path, value):
    """연 단위로는 연중 시행일(2022-07-13)을 표현할 수 없다 — kr 의 같은 결정
    (tests/test_substitute_rules.py::test_effective_from_is_a_date_not_a_year)."""
    path = _write(tmp_path, "solar_holidays.yaml", [_solar_entry(effective_from=value)])
    with pytest.raises(ics.IcsError, match="effective_from"):
        feed._load(path, "month", "day")


def test_a_date_effective_from_loads(tmp_path):
    path = _write(tmp_path, "solar_holidays.yaml",
                  [_solar_entry(effective_from=dt.date(2022, 7, 13))])
    [entry] = feed._load(path, "month", "day")
    assert entry["effective_from"] == dt.date(2022, 7, 13)


@pytest.mark.parametrize(
    ("start", "present_2023"),
    [
        pytest.param(dt.date(2023, 3, 8), True, id="경계 당일 — 포함"),
        pytest.param(dt.date(2023, 3, 9), False, id="경계 다음 날"),
        pytest.param(dt.date(2023, 3, 7), True, id="경계 전날"),
    ],
)
def test_the_start_is_an_inclusive_bound(tmp_path, monkeypatch, start, present_2023):
    path = _write(tmp_path, "solar_holidays.yaml", [_solar_entry(effective_from=start)])
    monkeypatch.setattr(feed, "SOLAR_PATH", path)
    got = feed.events(dt.date(2022, 1, 1), dt.date(2024, 12, 31))
    days = {e.day for e in got}
    assert dt.date(2022, 3, 8) not in days
    assert (dt.date(2023, 3, 8) in days) is present_2023
    assert dt.date(2024, 3, 8) in days


@pytest.mark.parametrize(
    "day",
    [dt.date(2022, 7, 12), dt.date(2022, 7, 13), dt.date(2022, 7, 14),
     dt.date(2022, 3, 8), dt.date(2023, 3, 8)],
)
def test_the_start_means_what_kr_effective_from_means(day):
    """kr 의 항목별 effective_from(rules/kr/holiday_calendar.py 의 _active)과 같은 판정이다."""
    entry = {"effective_from": FRAUENTAG_FROM}
    assert feed._active(entry, day) is kr_calendar._active(entry, day)
    assert feed._active({}, day) is kr_calendar._active({}, day) is True


def test_an_unknown_top_level_key_stops_the_load(tmp_path):
    """로더가 holidays 만 읽으면 최상위의 effective_until 은 조용히 무시된다(Codex 지적 1)."""
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump({"effective_until": dt.date(2025, 12, 31), "holidays": [_solar_entry()]},
                       allow_unicode=True),
        encoding="utf-8",
    )
    with pytest.raises(ics.IcsError, match="최상위의 모르는 키"):
        feed._load(path, "month", "day")


def test_a_duplicate_key_stops_the_load(tmp_path):
    """safe_load 는 뒤의 값을 남긴다. effective_from 을 두 번 적으면 뒤의 2020-01-01 만 검사를
    지나 2020–2022 에도 Frauentag 가 나간다(Codex 지적 2)."""
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        "holidays:\n"
        "  - key: frauentag\n    name: Frauentag\n    scope: land\n    month: 3\n    day: 8\n"
        "    verified: false\n    source: test\n"
        "    effective_from: 2022-07-13\n    effective_from: 2020-01-01\n",
        encoding="utf-8",
    )
    with pytest.raises(ics.IcsError, match="중복 키"):
        feed._load(path, "month", "day")
