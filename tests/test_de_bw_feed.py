"""독일·바덴뷔르템베르크 주 피드 — rules/de_bw/ 가 내는 .ics 가 확정 사양대로
나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_bw.ics 는 바덴뷔르템베르크 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über die Sonntage und Feiertage (Feiertagsgesetz – FTG) in der
    Fassung vom 8. Mai 1995 § 1 이다 — 호 번호 없는 열거 11 건. 여기에 § 1 에 없는
    3. Oktober(Einigungsvertrag Art. 2 Abs. 2)를 더해 연 단위 12 건: 고정 7 + 부활절
    이동 5. 전국 공통 9 건에 Erscheinungsfest(1. 6.)·Fronleichnam(+60)·Allerheiligen
    (1. 11.)이 더해진다. 일회성은 없다(§ 1a 의 2017 Reformationsfest 는 실효, 발행
    하한 밖). 대체공휴일(이동) 규칙도 없다.

근거는 /tmp/report_bw_gesetz_chain.md 이고, 요지는 rules/de_bw/ 의 YAML source
필드에 옮겨 적었다. 현행 § 1 자구는 Neufassung 인쇄본(GBl. 1995 Nr. 17 S. 450,
30.06.1995 공포)이고, 그 입법 뿌리 세 벌(1970 Neufassung GBl. 1971 S. 1 / 1994-12-12
GBl. S. 631 / 1995-03-23 GBl. S. 293)도 Landtag BW 아카이브 PDF 로 읽었다. § 1 은
그 뒤 무개정(2014 § 1a·2015 §§ 8·10·11·13 만, 최신 호 GBl. 2026 Nr. 79 까지). 그래서
§ 1 의 11 건은 verified: true 다. 12 번째 3. Oktober 는 rules/de 의 같은 항목을
미러한다(Einigungsvertrag, verified true) — FTG § 1 을 근거로 적지 않는다.

BW 특유의 결정(닫힘):
- § 1 에 호 번호가 없다 → 조문 인용은 "§ 1, 열거 n번째" 병기(de_by 전례). 이 파일도
  Nr. 단언 대신 열거 순번·자구를 단언한다.
- 1월 6일 조문 자구는 'Erscheinungsfest (6. Januar)'. key 는 de_by 의
  heilige_drei_koenige 를 재사용(신규 명명 0), SUMMARY 는 괄호 날짜를 뺀
  'Erscheinungsfest', 원문은 DESCRIPTION 근거에.
- SUMMARY 는 조문 표기에서 괄호 날짜만 뺀 것: 'Allerheiligen (1. November)' →
  'Allerheiligen'. 나머지는 조문 그대로('Neujahr', 'Erster Weihnachtstag' …).

    a. feiertage-api 2026 BW 실측 12 건(hinweis 공란) == de_bw 2026 발행 집합.
       API 의 13 번째 항목 'Reformationstag' 은 hinweis(§ 4 Abs. 3 schulfrei) 가
       붙은 비공휴일 — 알려진 특이점, 대조에서 제외한다.
    b. 상위집합 — de.ics 9 건 ⊂ de_bw.ics, 차집합 token 은 셋
    c. 연도별 12 건 · 일요일 겹침(01-06 이 일요일인 2030 포함)
    d. UID — 전 항목 de_bw- 접두사, 기존 일곱 독일 피드와 겹치지 않음(특히 de_by 와
       key 셋을 공유)
    e. 신규 token 0 — 기존 여섯 주 피드 key 합집합 대비 차집합이 공집합
    f. 하니스 — python-holidays(subdiv='BW')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·근거 — 관례 이식. SUMMARY 두 건의 괄호 날짜 제외 포함
    h. 근거 — 12 건 전부 verified true. 11 건은 Neufassung 서지·URL·sha256·열람일,
       10-03 은 Einigungsvertrag 인용

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_bw 를 더해 일곱 주로 확장한다(여기 두지 않는다). scope 교차 검증도
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
from rules.de_bw import feed
from rules.de_bw import status as de_bw_status
from rules.de_by import feed as de_by_feed
from rules.de_he import feed as de_he_feed
from rules.de_hh import feed as de_hh_feed
from rules.de_nw import feed as de_nw_feed
from rules.de_sh import feed as de_sh_feed

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_bw-"

# feiertage-api.de 2026 BW 실측(2026-09-09, ?jahr=2026&nur_land=BW). 13 건 중 hinweis
# 공란 12 건. 13 번째 'Reformationstag'(2026-10-31)은 hinweis "Gemäß § 4 Abs. 3 des
# Feiertagsgesetzes … haben Schüler am Gründonnerstag und am Reformationstag schulfrei"
# 가 붙은 비공휴일 항목이라 여기 두지 않는다.
FEIERTAGE_API_2026_BW = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Heilige Drei Könige": dt.date(2026, 1, 6),
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
FEIERTAGE_API_2026_BW_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_BW}
FEIERTAGE_API_2026_BW_EXCLUDED = {"Reformationstag": dt.date(2026, 10, 31)}  # hinweis 부착

# 2026 발행 순서(날짜순). 넷째 열은 FTG § 1 의 열거 순번(1~11), 3. Oktober 는 § 1 밖이라
# None. 셋째 열은 SUMMARY — 조문 표기에서 괄호 날짜만 뺀 것.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahr", "neujahr", 1),
    (dt.date(2026, 1, 6), "Erscheinungsfest", "heilige_drei_koenige", 2),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 3),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 4),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 5),
    (dt.date(2026, 5, 14), "Christi Himmelfahrt", "christi_himmelfahrt", 6),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 7),
    (dt.date(2026, 6, 4), "Fronleichnam", "fronleichnam", 8),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", None),
    (dt.date(2026, 11, 1), "Allerheiligen", "allerheiligen", 9),
    (dt.date(2026, 12, 25), "Erster Weihnachtstag", "erster_weihnachtstag", 10),
    (dt.date(2026, 12, 26), "Zweiter Weihnachtstag", "zweiter_weihnachtstag", 11),
]
TOKENS = {PREFIX + key for _, _, key, _ in EXPECTED_2026}
ORDINAL_OF = {key: n for _, _, key, n in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _ in EXPECTED_2026}
LAND_KEYS = {"heilige_drei_koenige", "fronleichnam", "allerheiligen"}

# § 1 의 조문 자구(Neufassung 1995 S. 450 인쇄본). SUMMARY 와 다른 두 호는 괄호 날짜.
STATUTE_TEXT = {
    "neujahr": "Neujahr",
    "heilige_drei_koenige": "Erscheinungsfest (6. Januar)",
    "karfreitag": "Karfreitag",
    "ostermontag": "Ostermontag",
    "erster_mai": "1. Mai",
    "christi_himmelfahrt": "Christi Himmelfahrt",
    "pfingstmontag": "Pfingstmontag",
    "fronleichnam": "Fronleichnam",
    "allerheiligen": "Allerheiligen (1. November)",
    "erster_weihnachtstag": "Erster Weihnachtstag",
    "zweiter_weihnachtstag": "Zweiter Weihnachtstag",
}
PARENTHESISED = {"heilige_drei_koenige", "allerheiligen"}

# 공포본 — /tmp/report_bw_gesetz_chain.md §1 표의 값 그대로. Neufassung 은 구현
# 세션에서 재수령해 sha256 이 같음을 확인했다(2026-09-09).
NEUFASSUNG_1995 = {
    "cite": "GBl. 1995 Nr. 17 S. 450",
    "published": "30.06.1995",
    "url": "https://www.landtag-bw.de/resource/blob/75054/19739a8ea1fb5eee00898b30364b0f93/GBl199517.pdf",
    "sha256": "98f68c3039ac0a2df4f9ffc2417aa3f3ef25669c19a6b72e08c15f8f85d4fb94",
}
ROOTS = ("GBl. 1971 S. 1", "GBl. S. 631", "GBl. S. 293")  # 1970 Neufassung / 1994 / 1995 개정
READ_ON = "2026-09-09 열람"
EINIGUNGSVERTRAG = "Einigungsvertrag Art. 2 Abs. 2"


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
# a. 첫 단언 — feiertage-api 2026 BW(hinweis 공란 12 건) 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 의 hinweis 공란 12 건이 발행 집합과 다르면 구현을 멈추고
    불일치 목록을 보고한다. 13 번째 Reformationstag 은 hinweis 부착 비공휴일 —
    발행 집합에 있어서는 안 된다."""
    assert len(FEIERTAGE_API_2026_BW) == 12
    assert all(h == "" for h in FEIERTAGE_API_2026_BW_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_BW.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}
    assert not (ours & set(FEIERTAGE_API_2026_BW_EXCLUDED.values()))


def test_2026_has_exactly_the_twelve_bw_holidays_in_date_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_bw.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_bw(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    bw = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= bw
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + k for k in LAND_KEYS}
    assert dt.date(year, 10, 3) in bw  # § 1 밖이지만 반드시 있어야 한다(교차 검증의 전제)


# ---------------------------------------------------------------------------
# c. 연도별 건수 · 일요일 겹침
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_has_twelve_and_the_same_token_set(events, year):
    assert len(_year(events, year)) == 12
    assert {e.token for e in _year(events, year)} == TOKENS


@pytest.mark.parametrize(
    "year, sunday, key",
    [
        (2030, dt.date(2030, 1, 6), "heilige_drei_koenige"),
        (2026, dt.date(2026, 11, 1), "allerheiligen"),
        (2023, dt.date(2023, 1, 1), "neujahr"),
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """§ 1 에 이동 조항이 없다. python-holidays BW 2020–2031 도 보상 휴일 0 건.
    일요일 항목은 그대로 실리고 그 해는 12 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 12
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 일곱 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de·여섯 주 피드와, Erscheinungsfest·Fronleichnam·Allerheiligen
    은 de_by 와(Fronleichnam 은 de_he·de_nw, Allerheiligen 은 de_nw 와도) 같은 날 같은
    항목이다. 접두사가 유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for other in (de_feed, de_be_feed, de_by_feed, de_he_feed, de_hh_feed, de_nw_feed, de_sh_feed):
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


def test_the_three_keys_shared_with_bavaria_collide_without_the_prefix(events):
    """접두사를 벗기면 de_by 와 같은 날 같은 token 이 된다 — 접두사가 실제로 갈라놓는
    것을 양쪽에서 확인한다(붙이면 무충돌, 벗기면 충돌)."""
    end = dt.date(2026, 12, 31)
    by = {(e.day, e.token.removeprefix("de_by-")) for e in de_by_feed.events(TODAY, end)}
    ours = {(e.day, e.token.removeprefix(PREFIX)) for e in events if e.day <= end}
    shared_keys = {k for _, k in ours & by}
    assert LAND_KEYS <= shared_keys
    by_prefixed = {(e.day, e.token) for e in de_by_feed.events(TODAY, end)}
    ours_prefixed = {(e.day, e.token) for e in events if e.day <= end}
    assert ours_prefixed & by_prefixed == set()


# ---------------------------------------------------------------------------
# e. 신규 token 0
# ---------------------------------------------------------------------------


def test_no_token_is_newly_coined(events):
    """token 은 전부 기존 확립값이다 — 공통 9 종은 de_be 와, heilige_drei_koenige·
    fronleichnam·allerheiligen 은 de_by 와 key 가 같다. 조문 표기 Erscheinungsfest 를
    따라 새로 파지 않는다(token 은 내부 식별자 — reformationstag 건에서 확립된 원칙)."""
    end = dt.date(2026, 12, 31)
    established = set()
    for other, prefix in (
        (de_be_feed, "de_be-"),
        (de_by_feed, "de_by-"),
        (de_he_feed, "de_he-"),
        (de_hh_feed, "de_hh-"),
        (de_nw_feed, "de_nw-"),
        (de_sh_feed, "de_sh-"),
    ):
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == set()
    assert "erscheinungsfest" not in ours
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
def test_the_dates_agree_with_python_holidays_bw(events, year):
    """python-holidays 의 DE(subdiv='BW') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기는 우리 표기(조문)와 다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="BW", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY 두 건의 괄호 날짜 제외
# ---------------------------------------------------------------------------


def test_the_two_parenthesised_statute_lines_are_shortened_in_the_summary_only(rendered, events):
    """괄호 날짜는 SUMMARY 에서 빠지고 source(DESCRIPTION)에 원문 그대로 남는다.
    1월 6일의 SUMMARY 는 조문 표기 'Erscheinungsfest' — 통칭 Heilige Drei Könige 는
    조문에 없다."""
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key in PARENTHESISED:
        e = by_token[key]
        assert e.summary == NAME_OF[key], key
        assert "(" not in e.summary, key
        assert STATUTE_TEXT[key] in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert "Erscheinungsfest" in summaries
    assert not any("Könige" in s or "(" in s for s in summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_bw_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·바덴뷔르템베르크 공휴일" in head
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
# h. 근거 — 열거 순번·자구 인용, 공포본 서지, verified 전건 true
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_twelve_entries_and_the_eleven_statute_lines_cite_their_ordinal():
    """§ 1 에 호 번호가 없으므로 '§ 1, 열거 n번째' 로 지시하고(de_by 전례) 그 자구를
    따옴표로 담는다. 10-03 은 § 1 밖이라 이 인용을 가지면 안 된다."""
    entries = _raw_entries()
    assert len(entries) == 12
    assert {e["key"] for e in entries} == set(NAME_OF)
    for entry in entries:
        key = entry["key"]
        source = entry["source"]
        quoted = re.findall(r"'([^']+)'", source)
        if key == "tag_der_deutschen_einheit":
            # § 1 밖 — "§ 1, 열거 n번째" 인용을 가지면 안 된다. "§ 1 열거에는 없고" 라는
            # 부기는 허용한다(닫힌 결정: 전제 조항 수준의 부기만).
            assert "FTG(BW) § 1," not in source, key
            assert not re.search(r"열거 \d+번째", source), key
            continue
        assert f"FTG(BW) § 1, 열거 {ORDINAL_OF[key]}번째 '{STATUTE_TEXT[key]}'" in source, key
        assert STATUTE_TEXT[key] in quoted, key


def test_the_scopes_split_nine_nationwide_from_three_land():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert {k for k, e in by_key.items() if e["scope"] == "land"} == LAND_KEYS
    assert {k for k, e in by_key.items() if e["scope"] == "bundesweit"} == set(NAME_OF) - LAND_KEYS


def test_the_eleven_statute_entries_are_verified_from_the_neufassung_gazette():
    """11 건 전부 true. source 는 Neufassung 의 서지·공포일·연도판 PDF URL·sha256·
    열람일과 입법 뿌리 세 벌의 서지를 든다(/tmp/report_bw_gesetz_chain.md §1)."""
    entries = _raw_entries()
    assert [e["key"] for e in entries if not e["verified"]] == []
    for entry in entries:
        key = entry["key"]
        assert entry["verified"] is True, key
        assert "source_todo" not in entry, f"{key}: 전건 true 인데 source_todo 가 있다"
        assert "feiertage-api 2026 BW" in entry["source"], key
        assert "Drucksache" not in entry["source"], key
        if key == "tag_der_deutschen_einheit":
            continue
        for value in NEUFASSUNG_1995.values():
            assert value in entry["source"], (key, value)
        assert READ_ON in entry["source"], key
        for root in ROOTS:
            assert root in entry["source"], (key, root)


def test_unity_day_is_grounded_in_the_unification_treaty_not_in_section_1():
    """3. Oktober 는 § 1 에 없다. rules/de 의 같은 항목을 미러한다 — Einigungsvertrag
    Art. 2 Abs. 2 인용과 그 자구. FTG 는 § 7 Abs. 2 등에서 전제만 한다는 부기는 허용."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["tag_der_deutschen_einheit"]
    de_entry = {e["key"]: e for e in _de_raw_entries()}["tag_der_deutschen_einheit"]
    assert entry["scope"] == "bundesweit"
    assert entry["name"] == de_entry["name"] == "Tag der Deutschen Einheit"
    assert (entry["month"], entry["day"]) == (10, 3)
    assert EINIGUNGSVERTRAG in entry["source"]
    quote = "'Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag.'"
    assert quote in entry["source"]
    assert EINIGUNGSVERTRAG in de_entry["source"]
    assert entry["verified"] is True and de_entry["verified"] is True
    assert "§ 7 Abs. 2" in entry["source"]  # 전제 조항 부기


def _de_raw_entries() -> list:
    out = []
    for path in (de_feed.SOLAR_PATH, de_feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_epiphany_entry_reuses_the_bavarian_key_and_keeps_the_statute_wording():
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["heilige_drei_koenige"]
    assert entry["name"] == "Erscheinungsfest"
    assert (entry["month"], entry["day"]) == (1, 6)
    assert entry["scope"] == "land"
    assert "'Erscheinungsfest (6. Januar)'" in entry["source"]
    assert "heilige_drei_koenige" in entry["source"]  # key 재사용 근거를 적는다


def test_corpus_christi_is_easter_plus_sixty():
    by_key = {e["key"]: e for e in _raw_entries()}
    assert by_key["fronleichnam"]["easter_offset"] == 60
    assert by_key["fronleichnam"]["name"] == "Fronleichnam"
    assert by_key["fronleichnam"]["scope"] == "land"


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
    target = tmp_path / "de_bw.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_bw_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_bw.ics"
    assert got["events"] == 12 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (주 피드 공통 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Erscheinungsfest", "month": 1, "day": 6,
                           "verified": True, "source": "test", "scope": "land"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("heilige_drei_koenige\n", id="끝 개행"),
        pytest.param("Erscheinungsfest", id="대문자"),
        pytest.param("6_januar", id="날짜형 — 숫자 시작"),
        pytest.param("heilige_drei_könige", id="움라우트"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "month", "day")


def test_an_established_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "heilige_drei_koenige"), "month", "day")
    assert entry["key"] == "heilige_drei_koenige"
