"""독일·니더작센 주 피드 — rules/de_ni/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_ni.ics 는 니더작센 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Niedersächsisches Gesetz über die Feiertage (NFeiertagsG) in der
    Fassung vom 7. März 1995 (Nds. GVBl. S. 50) § 2 Abs. 1 Buchst. a)~j) 이다 — 알파벳
    호 열거 10 건. 연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건, 전국 공통 9 건에
    Buchst. h "der 31. Oktober, als Reformationstag". 3. Oktober 는 열거 안에 있다
    (Buchst. g) — BW 와 달리 rules/de 를 미러하지 않고 조문이 주근거다. 일회성은
    없다(2013 개정의 2017 한시 Satz 2 는 실효, 발행 하한 밖). 대체공휴일(이동) 규칙도
    없다.

근거는 /tmp/report_ni_gesetz_chain.md 이고, 요지는 rules/de_ni/ 의 YAML source·
source_todo 에 옮겨 적었다. verified 는 **혼합**(HH 구도) — Buchst. h 만 공포본
(Nds. GVBl. 2018 Nr. 7 S. 122, 28.06.2018)으로 자구를 읽어 true, 나머지 9 건은 자구가
1995 Neufassung(S. 50)에 의존하는데 Nds. GVBl. 의 디지털 공개가 2004 년부터라 공포본
을 읽지 못해 false + source_todo. HH #56·#57 전례와 같은 형식이다: xfail 없음(주 피드
YAML 은 fixture_loader 의 자동 xfail 대상이 아니다), source_todo 필수, 상태 고정 테스트.
→ 이 피드로 xfail/xpass 수가 변하면 안 된다(기준선 4 xfailed / 29 xpassed).

SUMMARY 는 조문 표기에서 서술부를 정리한 것: Buchst. g "der 3. Oktober, als Tag der
Deutschen Einheit" → "Tag der Deutschen Einheit", Buchst. h "der 31. Oktober, als
Reformationstag" → "Reformationstag", Buchst. d "der 1. Mai" → "1. Mai". 나머지는
조문 그대로(Neujahrstag, Himmelfahrtstag, 1. Weihnachtstag …). 원문은 DESCRIPTION 에.
key 는 전부 기존 확립값(공통 9 종 + de_hh·de_sh 의 reformationstag) — 신규 명명 0.

    a. feiertage-api 2026 NI 실측 10 건(hinweis 전부 공란) == de_ni 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_ni.ics, 차집합 token 은 {reformationstag} 하나
    c. 연도별 10 건 · 일요일 겹침(10-31 이 일요일인 2021·2027 포함)
    d. UID — 전 항목 de_ni- 접두사, 기존 여덟 독일 피드와 겹치지 않음
    e. 신규 token 0
    f. 하니스 — python-holidays(subdiv='NI')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·근거 — 관례 이식. SUMMARY 세 건의 서술부 정리 포함
    h. 근거 — Buchst. 인용 형식, h 만 true(공포본 서지·URL·sha256·열람일), 9 건 false +
       source_todo 의 경계 서술 핵심 문구, 10-03 은 Buchst. g 주근거 + Einigungsvertrag 부기

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_ni 를 더해 여덟 주로 확장한다(여기 두지 않는다). scope 교차 검증도
tests/test_de_scope.py 의 STATE_FEEDS 가 맡는다.
"""

from __future__ import annotations

import datetime as dt
import re

import pytest
import yaml

from core import ics
from rules.de import feed as de_feed
from rules.de_be import feed as de_be_feed
from rules.de_bw import feed as de_bw_feed
from rules.de_by import feed as de_by_feed
from rules.de_he import feed as de_he_feed
from rules.de_hh import feed as de_hh_feed
from rules.de_ni import feed
from rules.de_ni import status as de_ni_status
from rules.de_nw import feed as de_nw_feed
from rules.de_sh import feed as de_sh_feed

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_ni-"

# feiertage-api.de 2026 NI 실측(2026-09-09, ?jahr=2026&nur_land=NI). 10 건, 측정값
# 그대로. hinweis 는 열 개 모두 빈 문자열이었다.
FEIERTAGE_API_2026_NI = {
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
FEIERTAGE_API_2026_NI_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_NI}

# § 2 Abs. 1 의 Buchstabe 순서(2018 재번호 후 체계)·SUMMARY 표기.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", "a"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", "b"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", "c"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", "d"),
    (dt.date(2026, 5, 14), "Himmelfahrtstag", "christi_himmelfahrt", "e"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", "f"),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", "g"),
    (dt.date(2026, 10, 31), "Reformationstag", "reformationstag", "h"),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", "i"),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", "j"),
]
TOKENS = {PREFIX + key for _, _, key, _ in EXPECTED_2026}
LETTER_OF = {key: b for _, _, key, b in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _ in EXPECTED_2026}

# 조문 자구(VORIS 현행판·schure.de 일치; Buchst. h 는 2018 S. 122 공포본).
STATUTE_TEXT = {
    "neujahr": "Neujahrstag",
    "karfreitag": "Karfreitag",
    "ostermontag": "Ostermontag",
    "erster_mai": "der 1. Mai",
    "christi_himmelfahrt": "Himmelfahrtstag",
    "pfingstmontag": "Pfingstmontag",
    "tag_der_deutschen_einheit": "der 3. Oktober, als Tag der Deutschen Einheit",
    "reformationstag": "der 31. Oktober, als Reformationstag",
    "erster_weihnachtstag": "1. Weihnachtstag",
    "zweiter_weihnachtstag": "2. Weihnachtstag",
}
SHORTENED = {"erster_mai", "tag_der_deutschen_einheit", "reformationstag"}  # 서술부 정리
RENUMBERED_2018 = {"erster_weihnachtstag": "h", "zweiter_weihnachtstag": "i"}  # 2018 전 Buchstabe

# 공포본 — /tmp/report_ni_gesetz_chain.md §2 표의 값 그대로. 구현 세션에서 재수령해
# sha256 이 같음을 확인했다(2026-09-09). Wayback 사본도 같은 sha256.
GAZETTE_2018 = {
    "cite": "Nds. GVBl. 2018 Nr. 7 S. 122",
    "published": "28.06.2018",
    "url": "https://www.niedersachsen.de/download/132379/Nds._GVBl._Nr._7_2018_vom_28.06.2018_S._111-154.pdf",
    "sha256": "99d4848d3b86f2bd5b7af9e33af05b75fdee7098b8cdcdd16e07a378bd378b3d",
}
READ_ON = "2026-09-09 열람"
EINIGUNGSVERTRAG = "Einigungsvertrag Art. 2 Abs. 2"

# source_todo 가 말해야 하는 실측 경계(HH #57 형식). 낱말이 아니라 사실을 고정한다.
TODO_MUST_SAY = (
    "1995",       # 자구가 의존하는 Neufassung
    "S. 50",
    "2004",       # 디지털 공개 하한(포털)
    "2002",       # 공포본으로 못 읽은 유일한 개정
    "S. 17",
    "2005",       # 2005 공포본 인용이 1995~2005 사이를 닫는다
    "2018",       # 2018 지시문의 구조 전제
    "S. 122",
    "2026 Nr. 76",  # 순방향 확인 최신 호
    "[2차]",      # 2002 의 내용만 2차에 남는다
)


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
# a. 첫 단언 — feiertage-api 2026 NI 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 10 건이 발행 집합과 다르면 구현을 멈추고 불일치 목록을
    보고한다. hinweis 가 붙은 항목이 생겨도 멈춤이다(조사 시점엔 전부 공란)."""
    assert len(FEIERTAGE_API_2026_NI) == 10
    assert all(h == "" for h in FEIERTAGE_API_2026_NI_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_NI.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_ten_ni_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_ni.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_ni(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    ni = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= ni
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + "reformationstag"}
    assert dt.date(year, 10, 31) in ni


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
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """§ 2 에 이동 조항이 없다. python-holidays NI 도 보상 휴일 0 건. 일요일 항목은
    그대로 실리고 그 해는 10 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 10
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 여덟 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de·일곱 주 피드와, Reformationstag 은 de_hh·de_sh 와 같은 날 같은
    항목이다. 접두사가 유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    others = (de_feed, de_be_feed, de_bw_feed, de_by_feed, de_he_feed, de_hh_feed,
              de_nw_feed, de_sh_feed)
    for other in others:
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


# ---------------------------------------------------------------------------
# e. 신규 token 0
# ---------------------------------------------------------------------------


def test_no_token_is_newly_coined(events):
    """token 은 전부 기존 확립값이다 — 공통 9 종은 de_be 와, reformationstag 은
    de_hh·de_sh 와 key 가 같다."""
    end = dt.date(2026, 12, 31)
    established = set()
    for other, prefix in (
        (de_be_feed, "de_be-"),
        (de_bw_feed, "de_bw-"),
        (de_by_feed, "de_by-"),
        (de_he_feed, "de_he-"),
        (de_hh_feed, "de_hh-"),
        (de_nw_feed, "de_nw-"),
        (de_sh_feed, "de_sh-"),
    ):
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
def test_the_dates_agree_with_python_holidays_ni(events, year):
    """python-holidays 의 DE(subdiv='NI') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기는 우리 표기(조문)와 다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="NI", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY 세 건의 서술부 정리
# ---------------------------------------------------------------------------


def test_the_three_descriptive_statute_lines_are_shortened_in_the_summary_only(rendered, events):
    """"der …, als …" 서술부는 SUMMARY 에서 빠지고 source(DESCRIPTION)에 원문 그대로
    남는다. Nr. h 의 SUMMARY 는 'Reformationstag' — 조문에 통칭이 들어 있다(SH 와 같음)."""
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key in SHORTENED:
        e = by_token[key]
        assert e.summary == NAME_OF[key], key
        assert not e.summary.startswith("der ") and ", als " not in e.summary, key
        assert STATUTE_TEXT[key] in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert "Reformationstag" in summaries and "Tag der Deutschen Einheit" in summaries
    assert not any(s.startswith("der ") or "Oktober" in s for s in summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_ni_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·니더작센 공휴일" in head
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
# h. 근거 — Buchst. 인용, verified 경계(h 만 true), source_todo 의 경계 서술
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_ten_entries_each_citing_its_own_letter_of_section_2():
    """열거가 Buchstaben 이므로 '§ 2 Abs. 1 Buchst. x' 를 직접 인용한다(공포본도
    "Buchstabe h" 로 지시). 각 source 는 자기 Buchstabe 와 그 조문 자구를 따옴표로 담는다."""
    entries = _raw_entries()
    assert len(entries) == 10
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        assert f"§ 2 Abs. 1 Buchst. {LETTER_OF[key]} '{STATUTE_TEXT[key]}'" in entry["source"], key
        assert "NFeiertagsG" in entry["source"], key
        assert "feiertage-api 2026 NI" in entry["source"], key
        assert "Drucksache" not in entry["source"], key


def test_the_scopes_split_nine_nationwide_from_one_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == {"reformationstag"}
    bundesweit = {k for k, e in by_key.items() if e["scope"] == "bundesweit"}
    assert bundesweit == set(NAME_OF) - {"reformationstag"}


def test_reformation_day_is_the_only_verified_entry_and_cites_the_gazette():
    """de_ni 의 유일한 true. 근거는 공포 관보 원문 — Gesetz zur Änderung des NFeiertagsG
    vom 22. Juni 2018, Nds. GVBl. 2018 Nr. 7 S. 122(28.06.2018 공포, 29.06.2018 시행).
    포털 직접 수신본과 Wayback 사본의 sha256 이 같다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["reformationstag"]
    assert entry["name"] == "Reformationstag"
    assert (entry["month"], entry["day"]) == (10, 31)
    assert entry["scope"] == "land"
    assert entry["verified"] is True
    assert "source_todo" not in entry, "해소된 항목에 source_todo 가 남아 있다"
    for value in GAZETTE_2018.values():
        assert value in entry["source"], value
    assert "22.06.2018" in entry["source"]
    assert "29.06.2018" in entry["source"]
    assert READ_ON in entry["source"]
    assert "Wayback" in entry["source"]


def test_the_other_nine_are_false_and_their_todo_states_the_measured_boundary():
    """9 false + 1 true — HH #57 형식. 아홉 건의 source_todo 는 막연한 "포털 열람" 이
    아니라 실측된 경계를 말해야 한다: 자구는 1995 Neufassung(S. 50)에 의존하고 디지털
    공개는 2004 부터라 1995·2002(S. 17) 공포본을 못 읽었다; 1995~2005 사이 개정이 2002
    하나뿐임은 2005 공포본의 인용문이 닫고, [2차] 에 남는 것은 2002 의 내용(§ 2 무관)뿐;
    2018 지시문(S. 122)이 당시 열거 a)~i)와 말미 성탄절 둘을 전제한다; 순방향은 2026
    Nr. 76 까지 공포본으로 닫혔다. 잔존 경로도 적는다."""
    entries = _raw_entries()
    assert [e["key"] for e in entries if e["verified"]] == ["reformationstag"]
    for entry in entries:
        if entry["key"] == "reformationstag":
            continue
        assert entry["verified"] is False, entry["key"]
        assert entry.get("source_todo"), entry["key"]
        todo = entry["source_todo"]
        for must in TODO_MUST_SAY:
            assert must in todo, (entry["key"], must)
        assert "Landtagsbibliothek" in todo or "GWLB" in todo, entry["key"]  # 잔존 경로
        assert "VORIS" in entry["source"], entry["key"]  # 현행 자구를 읽은 2차 소스
        assert "schure" in entry["source"], entry["key"]  # 2차 소스 둘의 일치


def test_the_renumbered_christmas_entries_split_wording_from_letter():
    """Buchst. i·j 의 자구는 1995 Neufassung, Buchstabe 는 2018 S. 122 의 재번호
    ("Die bisherigen Buchstaben h und i werden Buchstaben i und j"). source 가 둘을
    나눠 적는다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    for key, old in RENUMBERED_2018.items():
        source = by_key[key]["source"]
        assert f"Buchst. {LETTER_OF[key]}" in source, key
        assert f"Buchst. {old}" in source, key  # 2018 이전 자리
        assert "재번호" in source and GAZETTE_2018["cite"] in source, key


def test_unity_day_is_grounded_in_letter_g_with_the_treaty_as_a_side_note():
    """BW 와 달리 3. Oktober 는 조문 열거 안에 있다 → 주근거는 Buchst. g, verified 는
    자구 1995 의존이라 false. Einigungsvertrag 는 부기다(rules/de 미러 아님)."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["tag_der_deutschen_einheit"]
    assert entry["scope"] == "bundesweit"
    assert entry["name"] == "Tag der Deutschen Einheit"
    assert entry["verified"] is False
    source = entry["source"]
    assert source.startswith("NFeiertagsG § 2 Abs. 1 Buchst. g '")
    assert EINIGUNGSVERTRAG in source
    assert source.index("Buchst. g") < source.index(EINIGUNGSVERTRAG)
    assert "gesetze-im-internet" not in source.split("—")[0]


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert "\n\n근거: " in e.description, e  # 첫 줄은 tests/test_de_scope.py
        assert " ".join(by_key[e.token.removeprefix(PREFIX)]["source"].split()) in e.description
        assert e.description.split("\n")[-1].startswith("근거: "), e


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "미검증", "확인 대기", "[2차]"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_ni.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_ni_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_ni.ics"
    assert got["events"] == 10 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (주 피드 공통 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Reformationstag", "month": 10, "day": 31,
                           "verified": True, "source": "test", "scope": "land"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("reformationstag\n", id="끝 개행"),
        pytest.param("Reformationstag", id="대문자"),
        pytest.param("31_oktober", id="날짜형 — 숫자 시작"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "month", "day")


def test_an_established_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "reformationstag"), "month", "day")
    assert entry["key"] == "reformationstag"
