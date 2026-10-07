"""독일·브레멘 주 피드 — rules/de_hb/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_hb.ics 는 브레멘 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über die Sonn-, Gedenk- und Feiertage vom 12. November 1954
    (Brem.GBl. S. 115) § 2 Abs. 1 이다 — Buchst. a)–j) 10 건. 연 단위 구성은 고정 6 +
    부활절 이동 4 = 10 건, 전국 공통 9 건에 Reformationstag(10. 31.)가 더해진다. key 는
    전부 기존 확립값이다. 대체공휴일(이동) 규칙은 없다.

현행 자구는 Transparenzportal Bremen 통합본(Inkrafttreten 14.03.2020 판, gsid 145882)으로
읽었다. 그 판이 지금도 현행이라는 근거는 Brem.GBl. 2020 Nr. 1 – 2026 Nr. 102 의 텍스트층
전문 검색(§ 2 Abs. 1 개정 0 건)과 텍스트층이 부족한 쪽(비공백 200 자 미만) 741 개의
계정이다. 원래의 판정 기준 2(검색 불가 쪽 0)는 미충족이고, 그 계정으로 대신한다는 것은
사람의 결정이다(조사 기록은 docs/research/report_hb_fulltext.md 외 셋).

verified 는 reformationstag 1 건만 true 다 — Buchst. j 의 현행 문언은 Brem.GBl. 2018 Nr. 63
S. 302 공포본으로 읽었다. a–i 9 건은 1954 원법과 2013 이전 개정에 의존하는데 Brem.GBl. 의
온라인 공개가 2013 년부터라 공포본을 찾지 못했다 — false + source_todo.

SUMMARY 는 조문 표기에서 관사 der 를 뺀 것이고, Buchst. g 「der 3. Oktober - Tag der
deutschen Einheit -」 만 날짜부와 대시도 빼 「Tag der deutschen Einheit」(소문자 d 는 조문
그대로 — de_be·de_bb 와 같다)다. 원문은 DESCRIPTION 에.

    a. feiertage-api 2026 HB 실측 10 건(hinweis 전부 공란) == de_hb 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_hb.ics, 차집합 token 은 reformationstag 하나
    c. 연도별 10 건
    d. UID — 전 항목 de_hb- 접두사, 다른 독일 피드(rules/ 스캔)와 겹치지 않음
    e. 신규 key 없음
    f. 하니스 — python-holidays(subdiv='HB')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·SUMMARY
    h. 근거 — Buchst. 인용, 통합본과 현행성 근거, reformationstag 만 true, a–i 의
       source_todo 경계, 머리 주석의 범위 밖·사람의 결정·추론 표기

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
from rules.de_hb import feed
from rules.de_hb import status as de_hb_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_hb-"

# feiertage-api.de 2026 HB 실측(2026-09-30, ?jahr=2026&nur_land=HB). 10 건, 측정값 그대로.
# 출처: docs/research/report_batch2_survey/fapi_2026_summary.txt. hinweis 는 열 개 모두 공란.
FEIERTAGE_API_2026_HB = {
    "Neujahrstag": dt.date(2026, 1, 1),
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
FEIERTAGE_API_2026_HB_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_HB}

# § 2 Abs. 1 의 Buchst.·SUMMARY 표기·조문 자구. 날짜 순서(j 가 h·i 앞).
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", "a", "der Neujahrstag"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", "b", "der Karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", "c", "der Ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", "d", "der 1. Mai"),
    (dt.date(2026, 5, 14), "Himmelfahrtstag", "christi_himmelfahrt", "e", "der Himmelfahrtstag"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", "f", "der Pfingstmontag"),
    (dt.date(2026, 10, 3), "Tag der deutschen Einheit", "tag_der_deutschen_einheit", "g",
     "der 3. Oktober - Tag der deutschen Einheit -"),
    (dt.date(2026, 10, 31), "Reformationstag", "reformationstag", "j", "der Reformationstag"),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", "h",
     "der 1. Weihnachtstag"),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", "i",
     "der 2. Weihnachtstag"),
]
TOKENS = {PREFIX + key for _, _, key, _, _ in EXPECTED_2026}
LETTER_OF = {key: letter for _, _, key, letter, _ in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _, _ in EXPECTED_2026}
STATUTE_TEXT = {key: text for _, _, key, _, text in EXPECTED_2026}
LAND_KEYS = {"reformationstag"}
VERIFIED_KEYS = {"reformationstag"}

# reformationstag 의 공포본 서지. 낱말이 아니라 사실을 고정한다.
REFORMATIONSTAG_MUST_SAY = (
    "Brem.GBl. 2018 Nr. 63 S. 302",
    "https://www.gesetzblatt.bremen.de/fastmedia/218/2018_06_28_GBl_Nr_0063_signed.pdf",
    "e0a706281f932bd4445366e2e546b0de894f0fcfc1e5ccb1793bdcb8665e23bf",
    "2026-09-30",
    "2026-10-06",
)

# a–i 의 source_todo 가 말해야 하는 실측 경계.
TODO_MUST_SAY = (
    "1954",        # 원법
    "S. 115",
    "2013",        # 온라인 공개 하한
    "296390",      # 현행 통합본
    "500",
    "실물 Brem.GBl.",
    "Staatsarchiv",
)

# 모든 항목 source 가 들어야 하는 현행성 근거 — 검색 사실의 꼴(무엇을 찾았고 무엇을 찾지
# 못했는지, 언제). 건수·판정어가 아니라 「찾지 못함」 이다(사람의 결정 K3).
CURRENCY_MUST_SAY = (
    "145882",
    "2020 Nr. 1",
    "2026 Nr. 102",
    "텍스트층",
    "§ 2 Abs. 1",
    "§ 12 b)",
    "찾지 못함",
    "2026-10-07",
)
# source 에 두지 않는 것 — 741 쪽 계정·기준 2 의 경위·조사 기록 경로는 머리 주석과 PR 본문에만
# 둔다(K2·K3). 레포 경로 자체는 tests/test_de_source_selfcontained.py 의 FORBIDDEN 이 막는다.
CURRENCY_MUST_NOT_SAY = ("개정 0 건", "741", "557", "기준 2", "report_hb")

# 다른 독일 피드 — rules/ 스캔(tests/test_de_scope.py 와 같은 조건). 손으로 적지 않는다.
RULES_DIR = Path(__file__).resolve().parents[1] / "rules"
OTHER_GERMAN_FEEDS = {
    p.name: importlib.import_module(f"rules.{p.name}.feed")
    for p in sorted(RULES_DIR.iterdir())
    if p.is_dir()
    and (p.name == "de" or p.name.startswith("de_"))
    and p.name != "de_hb"
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
# a. 첫 단언 — feiertage-api 2026 HB 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    assert len(FEIERTAGE_API_2026_HB) == 10
    assert all(h == "" for h in FEIERTAGE_API_2026_HB_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_HB.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_ten_hb_holidays_in_date_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_hb.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_hb(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    hb = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= hb
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + k for k in LAND_KEYS}


# ---------------------------------------------------------------------------
# c. 연도별 건수
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_ten_and_the_same_token_set(events, year):
    assert len(_year(events, year)) == 10
    assert {e.token for e in _year(events, year)} == TOKENS


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
def test_the_dates_agree_with_python_holidays_hb(events, year):
    """python-holidays 의 DE(subdiv='HB') 와 날짜 집합만 대조한다. 이름은 보지 않는다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="HB", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY
# ---------------------------------------------------------------------------


def test_summaries_drop_only_the_article_and_g_also_drops_its_date(rendered, events):
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        stripped = re.sub(r"^der ", "", statute)
        if key == "tag_der_deutschen_einheit":
            stripped = re.sub(r"^3\. Oktober - (.*) -$", r"\1", stripped)
        assert e.summary == NAME_OF[key] == stripped, key
        assert statute in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert not any(s.startswith("der ") or " - " in s for s in summaries)
    assert {"Tag der deutschen Einheit", "Himmelfahrtstag", "Reformationstag"} <= set(summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_hb_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·브레멘 공휴일" in head
    assert "X-WR-TIMEZONE:Europe/Berlin" in head
    assert "PRODID:-//lunalism//holidays.lunalism.com//KO" in head


def test_the_land_names(rendered):
    assert feed.LAND_NAME == "브레멘"
    assert feed.LAND_NAME_DE == "Bremen"


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
# h. 근거 — Buchst. 인용, 현행성 근거, verified, 경계 서술, 머리 주석
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


def test_the_tables_hold_ten_entries_each_citing_its_letter_and_wording():
    """§ 2 Abs. 1 은 Buchst. a)–j) 로 나뉜다. 그 자구를 따옴표로 담고, 현행 자구를 읽은
    통합본과 그 판이 현행이라는 근거를 검색 사실로 든다 — 찾은 범위(관보 호·텍스트층)와 찾지
    못한 것(§ 2 Abs. 1 을 바꾸는 지시, § 12 b) 를 포함한 일회성 지정)과 날짜."""
    entries = _raw_entries()
    assert len(entries) == 10
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        source = _source(entry)
        cite = (f"Gesetz über die Sonn-, Gedenk- und Feiertage (HB) § 2 Abs. 1 Buchst. "
                f"{LETTER_OF[key]} '{STATUTE_TEXT[key]}'")
        assert cite in source, key
        assert "Transparenzportal Bremen" in source, key
        for must in CURRENCY_MUST_SAY:
            assert must in source, (key, must)
        for banned in CURRENCY_MUST_NOT_SAY:
            assert banned not in source, (key, banned)
        assert "feiertage-api 2026 HB" in source, key
        assert entry["name"] == NAME_OF[key], key


def test_the_scopes_split_nine_nationwide_from_one_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == LAND_KEYS
    assert {k for k, e in by_key.items() if e["scope"] == "bundesweit"} == set(NAME_OF) - LAND_KEYS


def test_only_reformationstag_is_verified_and_it_cites_the_promulgated_text():
    entries = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in entries.items() if e["verified"] is True} == VERIFIED_KEYS
    entry = entries["reformationstag"]
    source = _source(entry)
    for must in REFORMATIONSTAG_MUST_SAY:
        assert must in source, must
    assert "§ 2 Absatz 1j wird wie folgt neu gefasst: der Reformationstag" in source
    assert not entry.get("source_todo")


def test_the_other_nine_are_false_and_their_todo_states_the_measured_boundary():
    for entry in _raw_entries():
        if entry["key"] in VERIFIED_KEYS:
            continue
        assert entry["verified"] is False, entry["key"]
        todo = " ".join((entry.get("source_todo") or "").split())
        assert todo, entry["key"]
        for must in TODO_MUST_SAY:
            assert must in todo, (entry["key"], must)


def test_the_header_records_scope_the_human_decision_and_the_inference():
    """범위 밖(§ 8 종교 축일·§ 7a 기념일), 기준 2 는 미충족이고 계정으로 대신한 것은 사람의
    결정이라는 것, 구조 검사로 닫은 557 쪽이 추론이라는 것을 적는다. 판정어로 바꾸지 않는다."""
    header = _header(feed.SOLAR_PATH)
    for must in ("§ 8", "§ 7a", "기준 2", "미충족", "사람의 결정", "557", "[추론]"):
        assert must in header, must
    for word in ("통과", "충족했다", "무개정"):
        assert word not in header, word


def test_the_school_regulation_is_at_most_one_header_line_and_never_a_source():
    """Brem.GBl. 2022 Nr. 142 § 4(학교 방학 규정의 열거)는 교차 확인일 뿐 근거가 아니다."""
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        lines = [ln for ln in _header(path).splitlines() if "2022 Nr. 142" in ln]
        assert len(lines) <= 1, path.name
    for entry in _raw_entries():
        assert "2022 Nr. 142" not in _source(entry), entry["key"]


def test_the_package_points_at_no_dead_or_private_path():
    for path in sorted((RULES_DIR / "de_hb").iterdir()):
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
    for word in ("verified", "source_todo", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_hb.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_hb_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_hb.ics"
    assert got["events"] == 10 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (주 피드 공통 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "easter_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Karfreitag", "easter_offset": -2,
                           "verified": False, "source": "test", "scope": "bundesweit"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("karfreitag\n", id="끝 개행"),
        pytest.param("Karfreitag", id="대문자"),
        pytest.param("0_karfreitag", id="숫자 시작"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "easter_offset")


def test_an_established_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "karfreitag"), "easter_offset")
    assert entry["key"] == "karfreitag"
