"""독일·노르트라인베스트팔렌 주 피드 — rules/de_nw/ 가 내는 .ics 가 확정 사양대로
나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_nw.ics 는 노르트라인베스트팔렌 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über die Sonn- und Feiertage (Feiertagsgesetz NW) § 2 Abs. 1
    Nr. 1~11 이다. 연 단위 구성은 고정 6 + 부활절 이동 5 = 11 건 — 전국 공통 9 건에
    Nr. 7 Fronleichnamstag 와 Nr. 9 Allerheiligentag. 일회성은 없다. 대체공휴일
    (이동) 규칙도 없다.

근거는 docs/research/report_nw_feiertagsgesetz_chain.md 이고, 요지는 rules/de_nw/ 의
YAML source 필드에 옮겨 적었다. 조문은 공포본 세 호의 스캔 면을 판독해 읽었다 —
1989 Neufassung(GV. NW. 1989 Nr. 19 S. 222), 1991 개정(1991 Nr. 19 S. 200, Nr. 8),
1994 개정(1994 Nr. 88 S. 1114, Nr. 10 삭제·재번호). 11 건 전부 verified: true 이고,
각 source 는 자기 호의 서지·공포일·PDF URL·sha256·열람일을 스스로 든다(BW 전례).

SUMMARY 는 조문 표기에서 정관사·서술부·괄호를 뺀 것이다(de.ics 의 전례):
Nr. 4 "der 1. Mai als Tag des Bekenntnisses …" → "1. Mai", Nr. 7 "der
Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis)" → "Fronleichnamstag",
Nr. 8 "der 3. Oktober als Tag der Deutschen Einheit" → "Tag der Deutschen Einheit",
Nr. 9 "der Allerheiligentag (1. November)" → "Allerheiligentag". token 은 전부 기존
확립값(신규 명명 0) — Allerheiligentag 도 de_by 의 allerheiligen 을 쓴다.

    a. feiertage-api 2026 NW 실측 11 건(hinweis 전부 공란) == de_nw 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_nw.ics, 차집합 token 은 {fronleichnam, allerheiligen}
    c. 연도별 11 건 · 일요일 겹침(11-01 이 일요일인 2020·2026 포함)
    d. UID — 전 항목 de_nw- 접두사, 기존 다섯 독일 피드와 겹치지 않음
    e. 신규 token 0 — 기존 네 주 피드 key 합집합 대비 차집합이 공집합
    f. 하니스 — python-holidays(subdiv='NW')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·근거 — 관례 이식. SUMMARY 네 건의 서술부·괄호 제외 포함
    h. 근거 — 11 건 전부 verified true. 자기 공포본 호의 면·sha256·열람일,
       Nr. 8 은 1991 S. 200, Nr. 10·11 은 1994 S. 1114 재번호. source 는
       DESCRIPTION 에 그대로 실리므로 머리 주석을 가리키지 않는다

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_nw 를 더해 다섯 주로 확장한다(여기 두지 않는다).
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
from rules.de_hh import feed as de_hh_feed
from rules.de_nw import feed
from rules.de_nw import status as de_nw_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_nw-"

# feiertage-api.de 2026 NW 실측(2026-09-06, ?jahr=2026&nur_land=NW). 11 건, 측정값
# 그대로. hinweis 는 열한 개 모두 빈 문자열이었다.
FEIERTAGE_API_2026_NW = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Karfreitag": dt.date(2026, 4, 3),
    "Ostermontag": dt.date(2026, 4, 6),
    "Tag der Arbeit": dt.date(2026, 5, 1),
    "Christi Himmelfahrt": dt.date(2026, 5, 14),
    "Pfingstmontag": dt.date(2026, 5, 25),
    "Fronleichnam": dt.date(2026, 6, 4),
    "Tag der Deutschen Einheit": dt.date(2026, 10, 3),
    "Allerheiligen": dt.date(2026, 11, 1),
    "1. Weihnachtstag": dt.date(2026, 12, 25),
    "2. Weihnachtstag": dt.date(2026, 12, 26),
}
FEIERTAGE_API_2026_NW_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_NW}

# Feiertagsgesetz NW § 2 Abs. 1 의 호 순서·SUMMARY 표기(공포본 자구 기준, 정관사·서술부·
# 괄호 제외). Nr. 5 는 공포본 표기 "Christi-Himmelfahrtstag" — 비공식 현행판의 하이픈
# 표기 "Christi-Himmelfahrts-Tag" 가 아니다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 3),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 4),
    (dt.date(2026, 5, 14), "Christi-Himmelfahrtstag", "christi_himmelfahrt", 5),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 6),
    (dt.date(2026, 6, 4), "Fronleichnamstag", "fronleichnam", 7),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", 8),
    (dt.date(2026, 11, 1), "Allerheiligentag", "allerheiligen", 9),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", 10),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", 11),
]
TOKENS = {PREFIX + key for _, _, key, _ in EXPECTED_2026}
NR_OF = {key: nr for _, _, key, nr in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _ in EXPECTED_2026}

# 조문 원문(공포본)이 SUMMARY 보다 긴 네 호. source 는 이 원문을 따옴표로 담아야 한다.
# Nr. 4 의 "Gerichtigkeit" 는 1989 공고본의 인쇄 그대로이고 [sic] 로 표시한다.
STATUTE_TEXT = {
    "erster_mai": (
        "der 1. Mai als Tag des Bekenntnisses zu Freiheit und Frieden, sozialer "
        "Gerichtigkeit [sic], Völkerversöhnung und Menschenwürde"
    ),
    "fronleichnam": "der Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis)",
    "tag_der_deutschen_einheit": "der 3. Oktober als Tag der Deutschen Einheit",
    "allerheiligen": "der Allerheiligentag (1. November)",
}

# 공포본 세 호. 값의 정본은 rules/de_nw/solar_holidays.yaml 머리 주석이고 여기는 그
# 사본이다 — 각 source 가 자기 호의 이 값들을 스스로 들어야 한다.
GAZETTE = {
    1989: {
        "issue": "GV. NW. 1989 Nr. 19 S. 222",
        "proclaimed": "09.05.1989 공포",
        "url": "https://recht.nrw.de/system/files/GV_Archiv/4122-xmmgvb8919.pdf",
        "sha256": "b72dd60b57c8b59139d27313e193f13d0b0fd06fce4da727749dd9a58b780a49",
    },
    1991: {
        "issue": "GV. NW. 1991 Nr. 19 S. 200",
        "proclaimed": "03.05.1991 공포",
        "url": "https://recht.nrw.de/system/files/GV_Archiv/3762-xmmgvb9119.pdf",
        "sha256": "4c7dd3aad931ce0b5906db48681a0cdfb6cb425a1964a8a970c14a683aa2dbc5",
    },
    1994: {
        "issue": "GV. NW. 1994 Nr. 88 S. 1114",
        "proclaimed": "30.12.1994 공포",
        "url": "https://recht.nrw.de/system/files/GV_Archiv/4383-xmmgvb9488.pdf",
        "sha256": "329fd81bb58b2e9a0cb17d8e0d7df3e28ffe0de35b175648fce282359ab823f8",
    },
}
READ_ON = "2026-09-29 열람"

# 1994 이후 개정이 없다는 것은 검색 사실로 적는다 — 2021 Nr. 75a 를 직접 보지 못했고
# 정오표 탐색도 일부 호는 목차 면만 봤다. 판정어('무개정')를 구독자 문장에 쓰지 않는다.
NO_LATER_AMENDMENT = (
    "§ 2 Abs. 1 의 1994 이후 개정은 찾지 못함(GV. NRW. 2026 Nr. 27 까지, 관보 색인·포털 개정 이력)"
)

# 항목별로 근거가 되는 공포본 호. Nr. 8 은 1991 의 새 문언, Nr. 10·11 은 1989 의
# Nr. 11·12 를 1994 가 재번호한 것, 나머지는 1989 의 자구 그대로다.
OWN_ISSUES = {key: (1989,) for key in NR_OF}
OWN_ISSUES["tag_der_deutschen_einheit"] = (1991,)
OWN_ISSUES["erster_weihnachtstag"] = (1989, 1994)
OWN_ISSUES["zweiter_weihnachtstag"] = (1989, 1994)


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
# a. 첫 단언 — feiertage-api 2026 NW 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 11 건이 발행 집합과 다르면 구현을 멈추고 불일치 목록을
    보고한다. hinweis 가 붙은 항목이 생겨도 멈춤이다(조사 시점엔 전부 공란)."""
    assert len(FEIERTAGE_API_2026_NW) == 11
    assert all(h == "" for h in FEIERTAGE_API_2026_NW_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_NW.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_eleven_nrw_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_nw.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_nrw(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    nrw = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= nrw
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + "fronleichnam", PREFIX + "allerheiligen"}
    assert dt.date(year, 11, 1) in nrw


# ---------------------------------------------------------------------------
# c. 연도별 건수 · 일요일 겹침
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_eleven_and_the_same_token_set(events, year):
    assert len(_year(events, year)) == 11
    assert {e.token for e in _year(events, year)} == TOKENS


@pytest.mark.parametrize(
    "year, sunday, key",
    [
        (2020, dt.date(2020, 11, 1), "allerheiligen"),
        (2026, dt.date(2026, 11, 1), "allerheiligen"),
        (2023, dt.date(2023, 1, 1), "neujahr"),
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """§ 2 에 이동 조항이 없다. feiertage-api NW 실측(2020·2026 11-01 일요일 포함)
    에서 보상 휴일 0 건. 일요일 항목은 그대로 실리고 그 해는 11 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 11
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 다섯 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de·de_be·de_by·de_he·de_hh 와, Fronleichnam 은 de_by·de_he 와,
    Allerheiligen 은 de_by 와 같은 날 같은 항목이다. 접두사가 유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for other in (de_feed, de_be_feed, de_by_feed, de_he_feed, de_hh_feed):
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


# ---------------------------------------------------------------------------
# e. 신규 token 0
# ---------------------------------------------------------------------------


def test_no_token_is_newly_coined(events):
    """token 은 전부 기존 확립값이다 — 공통 9 종은 de_be 와, fronleichnam 은
    de_by·de_he 와, allerheiligen 은 de_by 와 key 가 같다. allerheiligentag 를 새로
    파지 않는다(token 은 내부 식별자 — reformationstag 건에서 확립된 원칙)."""
    end = dt.date(2026, 12, 31)
    established = set()
    for other, prefix in (
        (de_be_feed, "de_be-"),
        (de_by_feed, "de_by-"),
        (de_he_feed, "de_he-"),
        (de_hh_feed, "de_hh-"),
    ):
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == set()
    assert "allerheiligentag" not in ours


def test_the_token_charset_has_no_digits_without_one_offs(events):
    for e in events:
        assert re.fullmatch(r"[a-z][a-z_]*", e.token.removeprefix(PREFIX)), e.token


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# f. 하니스 — python-holidays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_nrw(events, year):
    """python-holidays 의 DE(subdiv='NW') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기는 우리 표기(조문)와 다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="NW", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY 네 건의 서술부·괄호 제외
# ---------------------------------------------------------------------------


def test_the_four_long_statute_lines_are_shortened_in_the_summary_only(rendered, events):
    """서술부·괄호는 SUMMARY 에서 빠지고 source(DESCRIPTION)에 원문 그대로 남는다."""
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        assert e.summary == NAME_OF[key], key
        assert "(" not in e.summary and " als " not in e.summary, key
        assert statute in e.description, key
    for word in ("Bekenntnisses", "Trinitatis", "(1. November)", "als Tag"):
        assert not any(word in _prop(b, "SUMMARY") for b in _blocks(rendered)), word


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_nrw_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·노르트라인베스트팔렌 공휴일" in head
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
# h. 근거 — 항목별 호 인용·공포본 서지, verified 전건 true
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def _source(entry) -> str:
    """source 를 DESCRIPTION 처럼 한 줄로 편다. YAML 접힘이 URL·sha256 을 가르지 않게."""
    return " ".join(entry["source"].split())


def test_the_tables_hold_eleven_entries_each_citing_its_own_number_of_section_2():
    """호 번호가 있으므로 '§ 2 Abs. 1 Nr. n' 을 직접 인용한다. 각 source 는 자기 호
    번호와 그 호의 조문 표기(공포본 자구)를 따옴표로 담는다."""
    entries = _raw_entries()
    assert len(entries) == 11
    assert {e["key"] for e in entries} == set(NR_OF)
    for entry in entries:
        key = entry["key"]
        source = _source(entry)
        assert f"§ 2 Abs. 1 Nr. {NR_OF[key]} '" in source, key
        quoted = re.findall(r"'([^']+)'", source)
        assert quoted, key
        if key in STATUTE_TEXT:
            assert STATUTE_TEXT[key] in quoted, key
        else:
            assert f"der {NAME_OF[key]}" in quoted, key


def test_all_eleven_are_verified_and_nothing_is_left_to_do():
    """공포본 세 호로 11 건 전부 확인했다. source_todo 는 남기지 않는다."""
    entries = _raw_entries()
    assert [e["key"] for e in entries if e["verified"] is not True] == []
    for entry in entries:
        assert "source_todo" not in entry, f"{entry['key']}: 전건 true 인데 source_todo 가 있다"
        assert "feiertage-api 2026 NW" in entry["source"], entry["key"]


def test_each_source_carries_its_own_gazette_issue_page_hash_and_reading_date():
    """source 는 DESCRIPTION 에 그대로 실리므로 서지를 스스로 들어야 한다(BW 전례).
    자기 호의 면·공포일·PDF URL·sha256 과 열람일, 그리고 남의 호 sha256 은 들지 않는다."""
    for entry in _raw_entries():
        key = entry["key"]
        source = _source(entry)
        for year in OWN_ISSUES[key]:
            for field, value in GAZETTE[year].items():
                assert value in source, (key, year, field)
        assert READ_ON in source, key
        assert "재수령 대조 일치" in source, key
        own = {GAZETTE[year]["sha256"] for year in OWN_ISSUES[key]}
        assert set(re.findall(r"\b[0-9a-f]{64}\b", source)) == own, key
        assert NO_LATER_AMENDMENT in source, key


def test_unity_day_cites_the_1991_amendment_that_replaced_the_17th_of_june():
    entry = {e["key"]: e for e in _raw_entries()}["tag_der_deutschen_einheit"]
    source = _source(entry)
    assert "GV. NW. 1991 Nr. 19 S. 200" in source
    assert "Art. I Nr. 1" in source
    assert "'der 17. Juni als Tag der deutschen Einheit'" in source  # 종전 문언
    assert "Einigungsvertrag Art. 2 Abs. 2" in source  # 연방 근거 부기


def test_both_christmas_days_cite_the_1994_renumbering():
    by_key = {e["key"]: e for e in _raw_entries()}
    for key, old_nr in (("erster_weihnachtstag", 11), ("zweiter_weihnachtstag", 12)):
        source = _source(by_key[key])
        assert "GV. NW. 1994 Nr. 88 S. 1114" in source, key
        assert f"vom 23.04.1989 의 Nr. {old_nr}," in source, key
        assert f"Nr. {NR_OF[key]} " in source and "재번호" in source, key


def test_ascension_takes_the_gazette_spelling_not_the_hyphenated_one():
    """공포본(1977·1989)은 'Christi-Himmelfahrtstag'. 비공식 현행판의 하이픈 표기는
    source 에 대조로만 남고 SUMMARY 가 되지 않는다."""
    entry = {e["key"]: e for e in _raw_entries()}["christi_himmelfahrt"]
    assert entry["name"] == "Christi-Himmelfahrtstag"
    assert "'der Christi-Himmelfahrtstag'" in _source(entry)
    assert "GV. NW. 1977 S. 98" in _source(entry)


def test_labour_day_keeps_the_misprint_as_printed_and_says_so():
    """1989 공고본의 인쇄 'Gerichtigkeit' 를 [sic] 로 옮긴다. 1977 판의 자구와 정오표를
    찾지 못했다는 사실을 짧게 든다."""
    source = _source({e["key"]: e for e in _raw_entries()}["erster_mai"])
    assert "sozialer Gerichtigkeit [sic]," in source
    assert "GV. NW. 1977 S. 98" in source and "'Gerechtigkeit'" in source
    assert "1989–1996 관보에서 S. 222 정오표를 찾지 못함(텍스트층 없는 호는 목차 면만)" in source


def test_no_source_states_the_absence_of_amendment_as_a_verdict():
    """2015 이후 무개정은 색인 검색·포털 개정 이력으로 닫았고 75a 등 한계가 있다. 구독자
    문장은 '찾지 못함' 이라는 검색 사실로 적고 '무개정' 이라는 판정어를 쓰지 않는다."""
    for entry in _raw_entries():
        assert "무개정" not in entry["source"], entry["key"]


def test_no_source_points_to_the_header_comment():
    """source 는 DESCRIPTION 의 '근거:' 뒤에 그대로 나간다. 구독자는 YAML 을 볼 수
    없으므로 머리 주석을 가리키는 문장이 있으면 안 된다."""
    for entry in _raw_entries():
        assert "머리 주석" not in entry["source"], entry["key"]
        assert "solar_holidays.yaml" not in entry["source"], entry["key"]


def test_the_corpus_christi_source_ties_the_offset_to_the_statute_definition():
    """HE 와 달리 NW 조문은 날짜를 정의한다 — Donnerstag nach dem Sonntag Trinitatis.
    부활절 +60 이 그 정의와 등가임을 source 에 적는다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["fronleichnam"]
    assert entry["easter_offset"] == 60
    assert entry["name"] == "Fronleichnamstag"
    for word in ("Trinitatis", "+60", "등가"):
        assert word in entry["source"], word


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert "\n\n근거: " in e.description, e  # 첫 줄은 tests/test_de_scope.py
        assert " ".join(by_key[e.token.removeprefix(PREFIX)]["source"].split()) in e.description
        assert e.description.split("\n")[-1].startswith("근거: "), e


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_nw.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_nw_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_nw.ics"
    assert got["events"] == 11 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (주 피드 공통 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Allerheiligentag", "month": 11, "day": 1,
                           "verified": False, "source": "test", "scope": "land"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("allerheiligen\n", id="끝 개행"),
        pytest.param("Allerheiligen", id="대문자"),
        pytest.param("1_november", id="날짜형 — 숫자 시작"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "month", "day")


def test_an_established_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "allerheiligen"), "month", "day")
    assert entry["key"] == "allerheiligen"
