"""독일·함부르크 주 피드 — rules/de_hh/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_hh.ics 는 함부르크 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über Sonntage, Feiertage, Gedenktage und Trauertage
    (Feiertagsgesetz, HH) § 1 Nr. 1~10 이다. 연 단위 구성은 고정 6 + 부활절 이동
    4 = 10 건 — 전국 공통 9 건에 Nr. 8 "31. Oktober" 하나. 일회성은 없다(§ 2 의
    Sonderfeiertag 명령이 조사에서 확인된 것 없음). 대체공휴일(이동) 규칙도 없다.

근거는 /tmp/report_de_laender.md 의 HH 절이고, 요지는 rules/de_hh/ 의 YAML
source 필드에 옮겨 적었다. 공식 포털(landesrecht-hamburg)은 열람에 실패해 10 건
전부 verified: false 다 — BE 기저 9 건과 같은 관례(xfail 없음, source_todo 필수,
상태를 고정하는 테스트 하나). 31. Oktober 만 2018 개정안(의회 Drucksache
21/12153)을 봤지만 의결 전 안이라 승격하지 않는다.

Nr. 8 은 조문에 이름이 없고 날짜뿐이다. SUMMARY 는 조문 표기 "31. Oktober"
그대로, token 은 통칭 reformationstag — key charset 이 날짜형을 허용하지 않아
통칭을 식별자로 채택했다(승인 완료). 이 피드의 신규 명명은 이 하나뿐이다.

    a. feiertage-api 2026 HH 실측 10 건(hinweis 전부 공란) == de_hh 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_hh.ics, 차집합 token 은 {reformationstag} 하나
    c. 연도별 10 건 · 일요일 겹침(10-31 이 일요일인 2021·2027 포함)
    d. UID — 전 항목 de_hh- 접두사, 기존 네 독일 피드와 겹치지 않음
    e. 신규 token 고정 — reformationstag 외 신규 명명 0
    f. 하니스 — python-holidays(subdiv='HH')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·근거 — 관례 이식. "31. Oktober" 가 발행본에 그대로인지 포함

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_hh 를 더해 네 주로 확장한다(여기 두지 않는다).
"""

from __future__ import annotations

import datetime as dt
import re

import pytest
import yaml

from core import ics
from rules.de import feed as de_feed
from rules.de_be import feed as de_be_feed
from rules.de_by import feed as de_by_feed
from rules.de_he import feed as de_he_feed
from rules.de_hh import feed
from rules.de_hh import status as de_hh_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_hh-"

# feiertage-api.de 2026 HH 실측(2026-09-06, ?jahr=2026&nur_land=HH). 10 건, 측정값
# 그대로. hinweis 는 열 개 모두 빈 문자열이었다.
FEIERTAGE_API_2026_HH = {
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
FEIERTAGE_API_2026_HH_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_HH}

# Feiertagsgesetz(HH) § 1 의 호 순서·조문 표기(umwelt-online 현행판). Nr. 7 의
# 괄호 날짜 "(3. Oktober)" 는 SUMMARY 에서 뺐다(de.ics 의 서술부 제외 전례).
# Nr. 8 은 조문 표기가 날짜 "31. Oktober" 뿐이다 — 그대로 싣는다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 3),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 4),
    (dt.date(2026, 5, 14), "Himmelfahrtstag", "christi_himmelfahrt", 5),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 6),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", 7),
    (dt.date(2026, 10, 31), "31. Oktober", "reformationstag", 8),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", 9),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", 10),
]
TOKENS = {PREFIX + key for _, _, key, _ in EXPECTED_2026}
NR_OF = {key: nr for _, _, key, nr in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _ in EXPECTED_2026}

# 이 피드에서 처음 명명한 token. 승인된 신규 명명은 이 하나뿐이다.
NEWLY_COINED = {"reformationstag"}


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
# a. 첫 단언 — feiertage-api 2026 HH 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 10 건이 발행 집합과 다르면 구현을 멈추고 불일치 목록을
    보고한다. hinweis 가 붙은 항목이 생겨도 멈춤이다(조사 시점엔 전부 공란)."""
    assert len(FEIERTAGE_API_2026_HH) == 10
    assert all(h == "" for h in FEIERTAGE_API_2026_HH_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_HH.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_ten_hamburg_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_hh.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_hamburg(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    hamburg = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= hamburg
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + "reformationstag"}
    assert dt.date(year, 10, 31) in hamburg


# ---------------------------------------------------------------------------
# c. 연도별 건수 · 일요일 겹침
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_ten_and_the_same_token_set(events, year):
    assert len(_year(events, year)) == 10
    assert {e.token for e in _year(events, year)} == TOKENS


@pytest.mark.parametrize(
    "year, sunday, key",
    [
        (2021, dt.date(2021, 10, 31), "reformationstag"),
        (2027, dt.date(2027, 10, 31), "reformationstag"),
        (2023, dt.date(2023, 1, 1), "neujahr"),
        (2022, dt.date(2022, 5, 1), "erster_mai"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """§ 1 에 이동 조항이 없다. feiertage-api HH 실측(2021·2027 10-31 일요일 포함)
    에서 보상 휴일 0 건. 일요일 항목은 그대로 실리고 그 해는 10 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 10
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 네 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de·de_be·de_by·de_he 와 같은 날 같은 항목이다. 접두사가
    유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for other in (de_feed, de_be_feed, de_by_feed, de_he_feed):
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


# ---------------------------------------------------------------------------
# e. 신규 token 고정 — reformationstag 하나뿐
# ---------------------------------------------------------------------------


def test_the_only_newly_coined_token_is_reformationstag(events):
    """token 은 기존 확립값 재사용이 원칙이다(de_he 의 같은 테스트). 이 피드의
    허용 목록은 reformationstag 하나 — 조문에 이름이 없는 Nr. 8 을 위해 통칭을
    식별자로 채택했다. 둘째 신규 명명이 생기면 여기서 빨개진다."""
    end = dt.date(2026, 12, 31)
    established = set()
    for other, prefix in ((de_be_feed, "de_be-"), (de_by_feed, "de_by-"), (de_he_feed, "de_he-")):
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == NEWLY_COINED
    assert "reformationstag" not in established


def test_the_token_charset_has_no_digits_without_one_offs(events):
    for e in events:
        assert re.fullmatch(r"[a-z][a-z_]*", e.token.removeprefix(PREFIX)), e.token


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# f. 하니스 — python-holidays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_hamburg(events, year):
    """python-holidays 의 DE(subdiv='HH') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기(Reformationstag)는 우리 표기(조문 "31. Oktober")와
    다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="HH", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · "31. Oktober" 가 발행본에 그대로
# ---------------------------------------------------------------------------


def test_the_31st_of_october_is_summarised_as_the_statute_writes_it(rendered, events):
    """Nr. 8 은 조문에 이름이 없다. SUMMARY 는 '31. Oktober' 그대로이고 통칭
    Reformationstag 는 SUMMARY 어디에도 없다 — source(DESCRIPTION)에만 있다."""
    [e] = [e for e in events if e.day == dt.date(2026, 10, 31)]
    assert e.summary == "31. Oktober"
    assert e.token == PREFIX + "reformationstag"
    assert "SUMMARY:31. Oktober" in rendered
    assert not any(_prop(b, "SUMMARY").startswith("Reformationstag") for b in _blocks(rendered))
    assert "Reformationstag" in e.description


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_hamburg_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·함부르크 공휴일" in head
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
# 근거 — 항목별 호 인용, verified 전건 false (BE 기저 9 건 관례)
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_ten_entries_each_citing_its_own_number_of_section_1():
    """HH 는 호 번호가 있으므로 열거 순번이 아니라 'Nr. n' 을 직접 인용한다. 각
    source 는 자기 호 번호와 그 호의 조문 표기를 따옴표로 담는다."""
    entries = _raw_entries()
    assert len(entries) == 10
    assert {e["key"] for e in entries} == set(NR_OF)
    for entry in entries:
        key = entry["key"]
        assert f"§ 1 Nr. {NR_OF[key]}" in entry["source"], key
        quoted = re.findall(r"'([^']+)'", entry["source"])
        assert quoted and any(NAME_OF[key] in q for q in quoted), key


def test_the_unity_day_source_quotes_the_parenthesised_date_but_the_summary_drops_it():
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["tag_der_deutschen_einheit"]
    assert "'Tag der Deutschen Einheit (3. Oktober)'" in entry["source"]
    assert entry["name"] == "Tag der Deutschen Einheit"


def test_the_31st_of_october_entry_documents_the_coined_token_and_the_bill():
    """조문 표기·통칭·식별자 채택 근거·개정 문서·미열람 관보가 모두 한 항목에
    남아야 한다. true 승격은 하지 않는다 — Drucksache 는 의결 전 안이다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["reformationstag"]
    assert entry["name"] == "31. Oktober"
    assert (entry["month"], entry["day"]) == (10, 31)
    assert "'31. Oktober'" in entry["source"]
    assert "Reformationstag" in entry["source"]
    assert "Drucksache 21/12153" in entry["source"]
    assert "charset" in entry["source"] or "날짜형" in entry["source"]
    assert entry["verified"] is False
    assert "HmbGVBl. 2018 S. 63" in entry["source_todo"]


def test_nothing_is_verified_and_every_entry_says_what_is_missing():
    """공식 포털(landesrecht-hamburg)을 열람하지 못했으므로 10 건 전부 false 다.
    BE 기저 9 건과 같은 관례 — xfail 이 아니라 source_todo 로 남기고 여기서 상태를
    고정한다."""
    for entry in _raw_entries():
        assert entry["verified"] is False, entry["key"]
        assert entry.get("source_todo"), entry["key"]
        todo = entry["source_todo"]
        assert "landesrecht-hamburg" in todo or "HmbGVBl" in todo, entry["key"]
        assert "umwelt-online" in entry["source"], entry["key"]
        assert "feiertage-api" in entry["source"], entry["key"]


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
    target = tmp_path / "de_hh.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_hh_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_hh.ics"
    assert got["events"] == 10 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다. 날짜형 key 가 막히는 것이 여기서 보인다.
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "31. Oktober", "month": 10, "day": 31,
                           "verified": False, "source": "test"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("31_oktober", id="날짜형 — 숫자 시작"),
        pytest.param("oktober_31", id="날짜형 — 두 자리 숫자 접미"),
        pytest.param("reformationstag\n", id="끝 개행"),
        pytest.param("Reformationstag", id="대문자"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    """날짜형 key 가 charset 밖인 것이 reformationstag 를 채택한 이유다."""
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "month", "day")


def test_the_coined_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "reformationstag"), "month", "day")
    assert entry["key"] == "reformationstag"
