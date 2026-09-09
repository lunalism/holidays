"""독일·라인란트팔츠 주 피드 — rules/de_rp/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_rp.ics 는 라인란트팔츠 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Landesgesetz über den Schutz der Sonn- und Feiertage (Feiertagsgesetz –
    LFtG) vom 15. Juli 1970 (GVBl. S. 225, BS 113-10) § 2 Abs. 1 Nr. 1~10 이다 — 번호
    열거 10 호, 그중 Nr. 10 "der 1. und 2. Weihnachtstag (25. und 26. Dezember)" 이 두
    공휴일을 한 번호에 병렬로 묶고 있어 항목은 11 건이다. 연 단위 구성은 고정 6 +
    부활절 이동 5 = 11 건, 전국 공통 9 건에 Nr. 7 "der Fronleichnamstag" 와 Nr. 9 "der
    Allerheiligentag (1. November)". 3. Oktober 는 열거 안에 있다(Nr. 8) — BW 와 달리
    rules/de 를 미러하지 않고 조문이 주근거다. § 2 Abs. 2 의 일회성 수권은 있으나 수록
    항목은 없다(발동은 2015 LVO 의 2017-10-31 한 건, 발행 하한 밖). 대체공휴일(이동)
    규칙도 없다.

근거는 /tmp/report_rp_gesetz_chain.md 이고, 요지는 rules/de_rp/ 의 YAML source·
source_todo 에 옮겨 적었다. verified 는 **11 건 전건 false** — true 항목이 없는 첫
주 피드다. 현행 § 2 Abs. 1 자구는 1970 원법에 1990 S. 289·1993 S. 314·1994 S. 474
개정이 얹힌 것인데 GVBl. Rheinland-Pfalz 의 디지털 공개가 2004 년부터라 넷 다 공포본을
읽지 못했고, 2004~2026 전 호 스캔으로 확인된 유일한 LFtG 개정(2009 S. 358, § 10 만)은
어떤 항목의 자구도 세우지 못한다. 현행 자구는 2차 소스 넷의 글자 단위 일치에 의존한다.
HH #56·#57·NI #62 전례와 같은 형식이다: xfail 없음(주 피드 YAML 은 fixture_loader 의
자동 xfail 대상이 아니다), source_todo 필수, 상태 고정 테스트.
→ 이 피드로 xfail/xpass 수가 변하면 안 된다(기준선 4 xfailed / 29 xpassed).

SUMMARY 는 조문 표기에서 관사 "der" 와 괄호 날짜만 정리한 것: Nr. 5 "der Tag Christi
Himmelfahrt" → "Tag Christi Himmelfahrt", Nr. 7 → "Fronleichnamstag", Nr. 8 → "Tag der
Deutschen Einheit", Nr. 9 → "Allerheiligentag", Nr. 10 → "1. Weihnachtstag" / "2.
Weihnachtstag". BW 의 "Fronleichnam"·"Allerheiligen"·"Christi Himmelfahrt" 와 갈리는
것은 의도된 결과 — 각 피드는 자기 근거 조문의 표기를 쓴다. 원문은 DESCRIPTION 에.
key 는 전부 기존 확립값(공통 9 종 + de_bw·de_by·de_nw 의 fronleichnam·allerheiligen) —
신규 명명 0.

    a. feiertage-api 2026 RP 실측 11 건(hinweis 전부 공란) == de_rp 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_rp.ics, 차집합 token 은 {fronleichnam, allerheiligen}
       둘. 10-31 은 어느 해에도 없다(§ 2 Abs. 2 수권이 있으니 음성 단언을 둔다)
    c. 연도별 11 건 · 일요일 겹침(11-01 이 일요일인 2026 포함)
    d. UID — 전 항목 de_rp- 접두사, 기존 아홉 독일 피드와 겹치지 않음
    e. 신규 token 0
    f. 하니스 — python-holidays(subdiv='RP')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·근거 — 관례 이식. SUMMARY 의 관사·괄호 정리 전건
    h. 근거 — Nr. 인용 형식, 11 건 전건 false + source_todo 의 경계 서술(공포본으로
       닫힌 구간과 [2차] 로만 닫힌 것의 구분), Nr. 10 병렬 분해 서술이 두 항목에,
       10-03 은 Nr. 8 주근거 + Einigungsvertrag 부기, 2009 S. 358 호의 sha256 기록

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_rp 를 더해 아홉 주로 확장한다(여기 두지 않는다). scope 교차 검증도
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
from rules.de_ni import feed as de_ni_feed
from rules.de_nw import feed as de_nw_feed
from rules.de_rp import feed
from rules.de_rp import status as de_rp_status
from rules.de_sh import feed as de_sh_feed

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_rp-"

# feiertage-api.de 2026 RP 실측(2026-09-09, ?jahr=2026&nur_land=RP). 11 건, 측정값
# 그대로. hinweis 는 열한 개 모두 빈 문자열이었다(2020~2031 열두 해 전부 같다).
FEIERTAGE_API_2026_RP = {
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
FEIERTAGE_API_2026_RP_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_RP}

# § 2 Abs. 1 의 번호 순서·SUMMARY 표기. Nr. 10 은 두 항목이 같은 번호를 인용한다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 3),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 4),
    (dt.date(2026, 5, 14), "Tag Christi Himmelfahrt", "christi_himmelfahrt", 5),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 6),
    (dt.date(2026, 6, 4), "Fronleichnamstag", "fronleichnam", 7),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", 8),
    (dt.date(2026, 11, 1), "Allerheiligentag", "allerheiligen", 9),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", 10),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", 10),
]
TOKENS = {PREFIX + key for _, _, key, _ in EXPECTED_2026}
NUMBER_OF = {key: n for _, _, key, n in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _ in EXPECTED_2026}
LAND_KEYS = {"fronleichnam", "allerheiligen"}

# 조문 자구(2차 소스 넷 일치 — datumsrechner.de·Bistum Speyer OVB 2007/08 Beilage·
# kirchenrecht-ekhn.de 19575·kirchenrecht-evpfalz.de 14462). 전 호가 관사 "der" 로
# 시작하고 Nr. 8·9·10 은 괄호 날짜를 단다.
CHRISTMAS_TEXT = "der 1. und 2. Weihnachtstag (25. und 26. Dezember)"
STATUTE_TEXT = {
    "neujahr": "der Neujahrstag",
    "karfreitag": "der Karfreitag",
    "ostermontag": "der Ostermontag",
    "erster_mai": "der 1. Mai",
    "christi_himmelfahrt": "der Tag Christi Himmelfahrt",
    "pfingstmontag": "der Pfingstmontag",
    "fronleichnam": "der Fronleichnamstag",
    "tag_der_deutschen_einheit": "der Tag der Deutschen Einheit (3. Oktober)",
    "allerheiligen": "der Allerheiligentag (1. November)",
    "erster_weihnachtstag": CHRISTMAS_TEXT,
    "zweiter_weihnachtstag": CHRISTMAS_TEXT,
}
CHRISTMAS_SHARE = {
    "erster_weihnachtstag": "1. Weihnachtstag",
    "zweiter_weihnachtstag": "2. Weihnachtstag",
}
SECONDARY_SOURCES = ("datumsrechner", "Bistum Speyer", "kirchenrecht-ekhn", "kirchenrecht-evpfalz")

# 공포본 인용 체인의 요석 — /tmp/report_rp_gesetz_chain.md §2 표의 값 그대로. 구현
# 세션에서 재수령해 sha256 이 같음을 확인했다(2026-09-09). 어떤 항목도 true 로 만들지
# 못하지만(§ 10 만 개정) 2003 → 2009 구간을 공포본으로 닫는 호라 YAML 머리에 기록한다.
GAZETTE_2009 = {
    "cite": "GVBl. 2009 Nr. 17 S. 358",
    "published": "30.10.2009",
    "url": "https://gvbl.rlp.de/fileadmin/gvbl/2009/GVBl._Nr._17_vom_30.10.2009.pdf",
    "sha256": "d0937bbf14fe656d8f22773e2b986869248fb8b515b90b6404ac33ae943a8c6a",
}
EINIGUNGSVERTRAG = "Einigungsvertrag Art. 2 Abs. 2"

# source_todo 가 말해야 하는 실측 경계(HH #57·NI #62 형식). 낱말이 아니라 사실을 고정한다.
TODO_MUST_SAY = (
    "1970",              # 원법
    "S. 225",
    "S. 289",            # 1990 — 내용 미확인
    "S. 314",            # 1993 — 내용 미확인
    "S. 474",            # 1994 — § 2 지시문은 Drs. 로만
    "12/5573",
    "2004",              # 디지털 공개 하한
    "S. 396",            # 2003 — [2차]
    "S. 358",            # 2009 — 공포본, § 10 만
    "S. 433",            # 2015 LVO — 발행 범위 밖
    "2026 Nr. 22",       # 순방향 확인 최신 호
    "[2차]",             # 자구는 2차 넷 일치에 의존
    "공포본으로 닫힌",   # 구간 구분 — 2003→2009→현재
    "[2차] 로만 닫힌",   # 구간 구분 — 1994→2003, 2003 의 § 2 무관
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
# a. 첫 단언 — feiertage-api 2026 RP 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 11 건이 발행 집합과 다르면 구현을 멈추고 불일치 목록을
    보고한다. hinweis 가 붙은 항목이 생겨도 멈춤이다(조사 시점엔 전부 공란)."""
    assert len(FEIERTAGE_API_2026_RP) == 11
    assert all(h == "" for h in FEIERTAGE_API_2026_RP_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_RP.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_eleven_rp_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_rp.ics · 10-31 음성
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_rp(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    rp = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= rp
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + k for k in LAND_KEYS}
    assert dt.date(year, 11, 1) in rp


@pytest.mark.parametrize("year", range(2020, 2032))
def test_reformation_day_is_never_in_the_feed(events, year):
    """§ 2 Abs. 2 의 일회성 수권은 있지만 발행 범위 안에 발동된 LVO 가 없다(유일한
    발동은 2015 LVO 의 2017-10-31, 하한 밖). SH·NI 와 달리 10-31 은 어느 해에도
    없어야 하고, 그런 token 도 없어야 한다."""
    assert dt.date(year, 10, 31) not in _days(events, year)
    assert not any("reformation" in e.token for e in _year(events, year))


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
        (2026, dt.date(2026, 11, 1), "allerheiligen"),
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
        (2023, dt.date(2023, 1, 1), "neujahr"),
        (2027, dt.date(2027, 12, 26), "zweiter_weihnachtstag"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """§ 2 에 이동 조항이 없다. python-holidays RP 도 보상 휴일 0 건. 일요일 항목은
    그대로 실리고 그 해는 11 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 11
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 아홉 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de·여덟 주 피드와, Fronleichnam·Allerheiligen 은 de_bw·de_by·
    de_nw 와 같은 날 같은 항목이다. 접두사가 유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    others = (de_feed, de_be_feed, de_bw_feed, de_by_feed, de_he_feed, de_hh_feed,
              de_ni_feed, de_nw_feed, de_sh_feed)
    for other in others:
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


# ---------------------------------------------------------------------------
# e. 신규 token 0
# ---------------------------------------------------------------------------


def test_no_token_is_newly_coined(events):
    """token 은 전부 기존 확립값이다 — 공통 9 종은 de_be 와, fronleichnam·allerheiligen 은
    de_bw·de_by·de_nw 와 key 가 같다. Nr. 10 을 둘로 나눠도 새 key 는 생기지 않는다."""
    end = dt.date(2026, 12, 31)
    established = set()
    for other, prefix in (
        (de_be_feed, "de_be-"),
        (de_bw_feed, "de_bw-"),
        (de_by_feed, "de_by-"),
        (de_he_feed, "de_he-"),
        (de_hh_feed, "de_hh-"),
        (de_ni_feed, "de_ni-"),
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
def test_the_dates_agree_with_python_holidays_rp(events, year):
    """python-holidays 의 DE(subdiv='RP') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기는 우리 표기(조문)와 다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="RP", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY 의 관사·괄호 정리
# ---------------------------------------------------------------------------


def test_summaries_drop_only_the_article_and_the_bracketed_date(rendered, events):
    """조문 전 호가 "der …" 로 시작하고 Nr. 8·9·10 은 괄호 날짜를 단다. SUMMARY 는
    그 둘만 정리하고 나머지 자구는 그대로다(Fronleichnamstag·Allerheiligentag·Tag
    Christi Himmelfahrt — BW 표기와 갈리는 것은 의도). Nr. 10 은 자기 몫만 싣는다.
    원문은 DESCRIPTION 에 그대로 남는다."""
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        assert e.summary == NAME_OF[key], key
        assert statute in e.description, key
        if key in CHRISTMAS_SHARE:
            assert e.summary == CHRISTMAS_SHARE[key], key
        else:
            stripped = re.sub(r"\s*\(.*\)$", "", statute.removeprefix("der "))
            assert e.summary == stripped, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert not any(s.startswith("der ") or "(" in s for s in summaries)
    assert not any(m in s for s in summaries for m in ("Oktober", "November", "Dezember"))
    assert {"Fronleichnamstag", "Allerheiligentag", "Tag Christi Himmelfahrt"} <= set(summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    """Nr. 10 의 이틀도 하루짜리 이벤트 둘이다 — 25 일과 26 일 각각 DTEND = 다음 날."""
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_rp_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·라인란트팔츠 공휴일" in head
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
# h. 근거 — Nr. 인용, verified 전건 false, source_todo 의 경계 서술
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_eleven_entries_each_citing_its_own_number_of_section_2():
    """열거가 번호이므로 '§ 2 Abs. 1 Nr. n' 을 직접 인용한다. 각 source 는 자기 번호와
    그 호의 조문 자구 전체를 따옴표로 담는다 — Nr. 10 은 두 항목이 같은 자구를 인용한다.
    source 는 DESCRIPTION 으로 나가므로 [2차] 표기·Drucksache 인용은 source_todo 에만."""
    entries = _raw_entries()
    assert len(entries) == 11
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        assert f"LFtG § 2 Abs. 1 Nr. {NUMBER_OF[key]} '{STATUTE_TEXT[key]}'" in entry["source"], key
        assert "feiertage-api 2026 RP" in entry["source"], key
        assert "[2차]" not in entry["source"], key
        assert "Drucksache" not in entry["source"] and "Drs." not in entry["source"], key
        assert all(s in entry["source"] for s in SECONDARY_SOURCES), key  # 현행 자구를 읽은 넷


def test_the_scopes_split_nine_nationwide_from_two_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == LAND_KEYS
    bundesweit = {k for k, e in by_key.items() if e["scope"] == "bundesweit"}
    assert bundesweit == set(NAME_OF) - LAND_KEYS


def test_all_eleven_are_false_and_their_todo_states_the_measured_boundary():
    """11 false, true 0 — 첫 사례. 열한 건의 source_todo 는 막연한 "포털 열람" 이 아니라
    실측된 경계를 말해야 한다: 자구는 1970 원법(S. 225)+1990(S. 289)+1993(S. 314)+1994
    (S. 474)에 의존하고 디지털 공개는 2004 부터라 넷 다 못 읽었다; 현행 자구는 [2차]
    넷의 일치에 의존한다; 1994 의 § 2 지시문은 Drs. 12/5573 [2차]뿐. 구간은 둘로
    나눠 적는다 — 공포본으로 닫힌 구간(2003 S. 396 → 2009 S. 358 은 2009 공포본 인용문,
    2009 → 현재는 2004~2026 전 호 스캔, LVO 는 2015 S. 433 하나, 2026 Nr. 22 까지)과
    [2차] 로만 닫힌 것(1994 → 2003 사이 무개정, 2003 개정의 § 2 무관). 잔존 경로도 적는다."""
    entries = _raw_entries()
    assert [e["key"] for e in entries if e["verified"]] == []
    for entry in entries:
        assert entry["verified"] is False, entry["key"]
        assert entry.get("source_todo"), entry["key"]
        todo = entry["source_todo"]
        for must in TODO_MUST_SAY:
            assert must in todo, (entry["key"], must)
        assert todo.index("공포본으로 닫힌") < todo.index("[2차] 로만 닫힌"), entry["key"]
        assert "Landtagsbibliothek" in todo or "juris" in todo, entry["key"]  # 잔존 경로


def test_the_bundled_christmas_number_is_split_into_two_entries_that_say_so():
    """Nr. 10 "der 1. und 2. Weihnachtstag (25. und 26. Dezember)" 은 이름 있는 두
    공휴일의 병렬이지 이틀짜리 하나가 아니다. 두 항목이 같은 Nr. 10 자구를 인용하고,
    각자 자기 몫('1. Weihnachtstag' / '2. Weihnachtstag')과 병렬 분해임을 적는다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    for key, share in CHRISTMAS_SHARE.items():
        entry = by_key[key]
        source = entry["source"]
        assert f"Nr. 10 '{CHRISTMAS_TEXT}'" in source, key
        assert f"'{share}'" in source, key
        assert "병렬" in source, key
        assert entry["name"] == share
        assert (entry["month"], entry["day"]) == (12, 25 if key == "erster_weihnachtstag" else 26)
        assert entry["scope"] == "bundesweit"


def test_unity_day_is_grounded_in_number_8_with_the_treaty_as_a_side_note():
    """BW 와 달리 3. Oktober 는 조문 열거 안에 있다 → 주근거는 Nr. 8, verified 는 자구
    1970~1994 의존이라 false. Einigungsvertrag 는 부기다(rules/de 미러 아님)."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["tag_der_deutschen_einheit"]
    assert entry["scope"] == "bundesweit"
    assert entry["name"] == "Tag der Deutschen Einheit"
    assert entry["verified"] is False
    source = entry["source"]
    assert source.startswith("LFtG § 2 Abs. 1 Nr. 8 '")
    assert EINIGUNGSVERTRAG in source
    assert source.index("Nr. 8") < source.index(EINIGUNGSVERTRAG)
    assert "gesetze-im-internet" not in source.split("—")[0]


def test_the_land_entries_cite_numbers_7_and_9_with_their_full_wording():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert by_key["fronleichnam"]["name"] == "Fronleichnamstag"
    assert by_key["fronleichnam"]["easter_offset"] == 60
    assert by_key["allerheiligen"]["name"] == "Allerheiligentag"
    assert (by_key["allerheiligen"]["month"], by_key["allerheiligen"]["day"]) == (11, 1)
    for key in LAND_KEYS:
        assert by_key[key]["scope"] == "land"
        assert by_key[key]["verified"] is False


def test_the_table_header_records_the_2009_keystone_and_the_one_off_power():
    """머리 주석에 (1) 2003 → 2009 구간을 공포본으로 닫는 GVBl. 2009 Nr. 17 S. 358 의
    URL·sha256, (2) § 2 Abs. 2 일회성 수권의 존재와 유일한 발동(2015 LVO, 2017-10-31,
    발행 범위 밖)을 기록한다 — 수록 항목이 없어도 수권 자체는 남긴다."""
    header = feed.SOLAR_PATH.read_text(encoding="utf-8").split("holidays:")[0]
    for value in GAZETTE_2009.values():
        assert value in header, value
    assert "재수령" in header
    assert "§ 2 Abs. 2" in header
    assert "2017-10-31" in header or "31. Oktober 2017" in header
    assert "S. 433" in header


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert "\n\n근거: " in e.description, e  # 첫 줄은 tests/test_de_scope.py
        assert " ".join(by_key[e.token.removeprefix(PREFIX)]["source"].split()) in e.description
        assert e.description.split("\n")[-1].startswith("근거: "), e


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "미검증", "확인 대기", "[2차]", "Drucksache"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de_rp.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_rp_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_rp.ics"
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
