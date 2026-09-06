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

근거는 /tmp/report_de_laender.md 의 NW 절이고, 요지는 rules/de_nw/ 의 YAML
source 필드에 옮겨 적었다. 공식 경로는 전멸이다(recht.nrw.de 검색 SPA, 관보 PDF 는
JBIG2 스캔). 조문은 비공식 둘(lexmea 전문 ↔ IHK Köln 요약)로 읽었고 기준 텍스트는
lexmea 다 — 자구가 다른 호(7·8·10·11)는 source 에 차이를 기록한다. 11 건 전부
verified: false, BE 기저 9 건과 같은 관례(xfail 없음, source_todo 필수, 상태 고정
테스트 하나).

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

# Feiertagsgesetz NW § 2 Abs. 1 의 호 순서·SUMMARY 표기(lexmea 기준, 정관사·서술부·
# 괄호 제외). Nr. 5 는 조문의 하이픈 표기 "Christi-Himmelfahrts-Tag" 그대로.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 3),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 4),
    (dt.date(2026, 5, 14), "Christi-Himmelfahrts-Tag", "christi_himmelfahrt", 5),
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

# 조문 원문(lexmea)이 SUMMARY 보다 긴 네 호. source 는 이 원문을 따옴표로 담아야 한다.
STATUTE_TEXT = {
    "erster_mai": (
        "der 1. Mai als Tag des Bekenntnisses zu Freiheit und Frieden, sozialer "
        "Gerechtigkeit, Völkerversöhnung und Menschenwürde"
    ),
    "fronleichnam": "der Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis)",
    "tag_der_deutschen_einheit": "der 3. Oktober als Tag der Deutschen Einheit",
    "allerheiligen": "der Allerheiligentag (1. November)",
}

# IHK Köln 요약과 자구가 다른 호 — source 에 그 차이가 기록돼야 한다.
IHK_DIFFERS = {
    "fronleichnam", "tag_der_deutschen_einheit", "erster_weihnachtstag", "zweiter_weihnachtstag",
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
# 근거 — 항목별 호 인용(lexmea 기준, IHK 차이 병기), verified 전건 false
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_eleven_entries_each_citing_its_own_number_of_section_2():
    """호 번호가 있으므로 '§ 2 Abs. 1 Nr. n' 을 직접 인용한다. 각 source 는 자기 호
    번호와 그 호의 조문 표기(lexmea)를 따옴표로 담는다."""
    entries = _raw_entries()
    assert len(entries) == 11
    assert {e["key"] for e in entries} == set(NR_OF)
    for entry in entries:
        key = entry["key"]
        assert f"§ 2 Abs. 1 Nr. {NR_OF[key]}" in entry["source"], key
        quoted = re.findall(r"'([^']+)'", entry["source"])
        assert quoted, key
        if key in STATUTE_TEXT:
            assert STATUTE_TEXT[key] in quoted, key
        else:
            assert any(NAME_OF[key] in q for q in quoted), key
        assert "lexmea" in entry["source"], key


def test_the_lines_where_ihk_differs_record_the_difference():
    by_key = {e["key"]: e for e in _raw_entries()}
    for key in IHK_DIFFERS:
        assert "IHK" in by_key[key]["source"], key
    assert "(3. Oktober)" in by_key["tag_der_deutschen_einheit"]["source"]
    assert "(25. Dezember)" in by_key["erster_weihnachtstag"]["source"]
    assert "(26. Dezember)" in by_key["zweiter_weihnachtstag"]["source"]


def test_the_corpus_christi_source_ties_the_offset_to_the_statute_definition():
    """HE 와 달리 NW 조문은 날짜를 정의한다 — Donnerstag nach dem Sonntag Trinitatis.
    부활절 +60 이 그 정의와 등가임을 source 에 적는다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["fronleichnam"]
    assert entry["easter_offset"] == 60
    assert entry["name"] == "Fronleichnamstag"
    for word in ("Trinitatis", "+60", "등가"):
        assert word in entry["source"], word


def test_nothing_is_verified_and_every_entry_says_what_is_missing():
    """공식 경로가 전멸이므로 11 건 전부 false 다. BE 기저 9 건과 같은 관례 —
    xfail 이 아니라 source_todo 로 남기고 여기서 상태를 고정한다."""
    for entry in _raw_entries():
        assert entry["verified"] is False, entry["key"]
        todo = entry.get("source_todo") or ""
        assert "recht.nrw.de" in todo and "GV. NW" in todo, entry["key"]
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
                           "verified": False, "source": "test"}]},
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
