"""독일·슐레스비히홀슈타인 주 피드 — rules/de_sh/ 가 내는 .ics 가 확정 사양대로
나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_sh.ics 는 슐레스비히홀슈타인 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Gesetz über Sonn- und Feiertage (SFTG) vom 28. Juni 2004 § 2 Abs. 1
    Nr. 1~10 이다. 연 단위 구성은 고정 6 + 부활절 이동 4 = 10 건 — 전국 공통 9 건에
    Nr. 8 "31. Oktober - Reformationstag -". 일회성은 없다(§ 2 Abs. 2 의 수권에
    따른 명령이 2019~2026 공포본에 없다). 대체공휴일(이동) 규칙도 없다.

근거는 /tmp/report_sh_gesetz_chain.md 이고, 요지는 rules/de_sh/ 의 YAML source
필드에 옮겨 적었다. HH 와 달리 공포본 두 벌이 전부 손에 있다 — 제정 공포본
GVOBl. Schl.-H. 2004 Nr. 8 S. 213(15.07.2004)과 유일한 § 2 개정 공포본 2018 Nr. 6
S. 69(29.03.2018). 둘 다 Verkündungsportal 의 연도판 PDF 로 읽었고 sha256 을 남겼다.
그래서 10 건 전부 verified: true 다 — 이 레포의 첫 전건 true 주 피드. xfail 없음,
source_todo 없음.

SUMMARY 는 조문 표기에서 날짜부와 대시를 뺀 것이다(de.ics 가 BayFTG 의 "der 3.
Oktober als …" 서술부를 뺀 전례): Nr. 7 "3. Oktober - Tag der Deutschen Einheit -"
→ "Tag der Deutschen Einheit", Nr. 8 "31. Oktober - Reformationstag -" →
"Reformationstag". 조문 원문 전체는 source(DESCRIPTION)에 남는다. token 은 전부
기존 확립값(공통 9 종 + de_hh 의 reformationstag) — 신규 명명 0.

    a. feiertage-api 2026 SH 실측 10 건(hinweis 전부 공란) == de_sh 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_sh.ics, 차집합 token 은 {reformationstag} 하나
    c. 연도별 10 건 · 일요일 겹침(10-31 이 일요일인 2021·2027 포함)
    d. UID — 전 항목 de_sh- 접두사, 기존 여섯 독일 피드와 겹치지 않음
    e. 신규 token 0 — 기존 다섯 주 피드 key 합집합 대비 차집합이 공집합
    f. 하니스 — python-holidays(subdiv='SH')와 연도별 날짜 집합 대조
    g. 헤더·DTEND·범위·근거 — 관례 이식. SUMMARY 두 건의 날짜부 제외 포함
    h. 근거 — 10 건 전부 verified true, source 가 공포본 서지·URL·sha256·열람일을 든다

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS 에
de_sh 를 더해 여섯 주로 확장한다(여기 두지 않는다). scope 교차 검증도
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
from rules.de_by import feed as de_by_feed
from rules.de_he import feed as de_he_feed
from rules.de_hh import feed as de_hh_feed
from rules.de_nw import feed as de_nw_feed
from rules.de_sh import feed
from rules.de_sh import status as de_sh_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_sh-"

# feiertage-api.de 2026 SH 실측(2026-09-09, ?jahr=2026&nur_land=SH). 10 건, 측정값
# 그대로. hinweis 는 열 개 모두 빈 문자열이었다.
FEIERTAGE_API_2026_SH = {
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
FEIERTAGE_API_2026_SH_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_SH}

# SFTG § 2 Abs. 1 의 호 순서(2018 재번호 후 체계)·SUMMARY 표기. Nr. 7·8 은 조문의
# 날짜부·대시를 뺀 것이고 나머지는 조문 그대로다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr", 1),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag", 2),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag", 3),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai", 4),
    (dt.date(2026, 5, 14), "Himmelfahrtstag", "christi_himmelfahrt", 5),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag", 6),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit", 7),
    (dt.date(2026, 10, 31), "Reformationstag", "reformationstag", 8),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag", 9),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag", 10),
]
TOKENS = {PREFIX + key for _, _, key, _ in EXPECTED_2026}
NR_OF = {key: nr for _, _, key, nr in EXPECTED_2026}
NAME_OF = {key: name for _, name, key, _ in EXPECTED_2026}

# 조문 원문이 SUMMARY 보다 긴 두 호. source 는 이 원문을 따옴표로 담아야 한다.
STATUTE_TEXT = {
    "tag_der_deutschen_einheit": "3. Oktober - Tag der Deutschen Einheit -",
    "reformationstag": "31. Oktober - Reformationstag -",
}

# 공포본 두 벌 — /tmp/report_sh_gesetz_chain.md §1 표의 값 그대로. 2018 연도판은
# 구현 세션에서 재수령해 sha256 이 같음을 확인했다(2026-09-09).
GAZETTE_2004 = {
    "cite": "GVOBl. Schl.-H. 2004 Nr. 8 S. 213",
    "published": "15.07.2004",
    "url": "https://verkuendungsportal.schleswig-holstein.de/mm/gvobl_jahrgang_2004/GVOBl_2004.pdf",
    "sha256": "dba6f1a10bf991211a29d6f6c52f2e4f4dab5526c627d46f76b1df6ced26bc41",
}
GAZETTE_2018 = {
    "cite": "GVOBl. Schl.-H. 2018 Nr. 6 S. 69",
    "published": "29.03.2018",
    "url": "https://verkuendungsportal.schleswig-holstein.de/mm/gvobl_jahrgang_2018/GVOBl_2018.pdf",
    "sha256": "c50173af93e2e6a02bc33789c0e610df5d6b1c331a068fd21aa9322e7102d44b",
}
READ_ON = "2026-09-09 열람"

# 2018 개정이 번호를 건드린 호 — Nr. 8 신설, 구 Nr. 8·9 → 9·10.
RENUMBERED_2018 = {"erster_weihnachtstag", "zweiter_weihnachtstag"}


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
# a. 첫 단언 — feiertage-api 2026 SH 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 10 건이 발행 집합과 다르면 구현을 멈추고 불일치 목록을
    보고한다. hinweis 가 붙은 항목이 생겨도 멈춤이다(조사 시점엔 전부 공란)."""
    assert len(FEIERTAGE_API_2026_SH) == 10
    assert all(h == "" for h in FEIERTAGE_API_2026_SH_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_SH.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_ten_sh_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k, _ in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_sh.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_sh(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    sh = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= sh
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + "reformationstag"}
    assert dt.date(year, 10, 31) in sh


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
    """§ 2 에 이동 조항이 없다. feiertage-api SH 실측(2021 10-31 일요일 포함)에서
    보상 휴일 0 건. 일요일 항목은 그대로 실리고 그 해는 10 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 10
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 여섯 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de·다섯 주 피드와, Reformationstag 은 de_hh 와 같은 날 같은
    항목이다. 접두사가 유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for other in (de_feed, de_be_feed, de_by_feed, de_he_feed, de_hh_feed, de_nw_feed):
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


# ---------------------------------------------------------------------------
# e. 신규 token 0
# ---------------------------------------------------------------------------


def test_no_token_is_newly_coined(events):
    """token 은 전부 기존 확립값이다 — 공통 9 종은 de_be 와, reformationstag 은
    de_hh 와 key 가 같다. SH 조문에 통칭이 있어도 token 은 새로 파지 않는다."""
    end = dt.date(2026, 12, 31)
    established = set()
    for other, prefix in (
        (de_be_feed, "de_be-"),
        (de_by_feed, "de_by-"),
        (de_he_feed, "de_he-"),
        (de_hh_feed, "de_hh-"),
        (de_nw_feed, "de_nw-"),
    ):
        established |= {e.token.removeprefix(prefix) for e in other.events(TODAY, end)}
    ours = {e.token.removeprefix(PREFIX) for e in events}
    assert ours - established == set()
    assert ours == set(NR_OF)


def test_the_token_charset_has_no_digits_without_one_offs(events):
    for e in events:
        assert re.fullmatch(r"[a-z][a-z_]*", e.token.removeprefix(PREFIX)), e.token


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# f. 하니스 — python-holidays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_sh(events, year):
    """python-holidays 의 DE(subdiv='SH') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기는 우리 표기(조문)와 다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="SH", years=year).keys())


# ---------------------------------------------------------------------------
# g. 헤더·DTEND·범위 · SUMMARY 두 건의 날짜부 제외
# ---------------------------------------------------------------------------


def test_the_two_dated_statute_lines_are_shortened_in_the_summary_only(rendered, events):
    """날짜부와 대시는 SUMMARY 에서 빠지고 source(DESCRIPTION)에 원문 그대로 남는다.
    Nr. 8 의 SUMMARY 는 'Reformationstag' — HH('31. Oktober')와 다른 이유는 SH 조문에
    통칭이 들어 있어서다."""
    by_token = {e.token.removeprefix(PREFIX): e for e in _year(events, 2026)}
    for key, statute in STATUTE_TEXT.items():
        e = by_token[key]
        assert e.summary == NAME_OF[key], key
        assert "Oktober" not in e.summary and " - " not in e.summary, key
        assert statute in e.description, key
    summaries = [_prop(b, "SUMMARY") for b in _blocks(rendered)]
    assert "Reformationstag" in summaries
    assert "31. Oktober" not in summaries
    assert not any("Oktober" in s for s in summaries)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_sh_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·슐레스비히홀슈타인 공휴일" in head
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
# h. 근거 — 항목별 호 인용, 공포본 서지, verified 전건 true
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def test_the_tables_hold_ten_entries_each_citing_its_own_number_of_section_2():
    """호 번호가 있으므로 '§ 2 Abs. 1 Nr. n' 을 직접 인용한다. 각 source 는 자기 호
    번호와 그 호의 조문 표기(공포본)를 따옴표로 담는다. 번호는 2018 재번호 후 체계다."""
    entries = _raw_entries()
    assert len(entries) == 10
    assert {e["key"] for e in entries} == set(NR_OF)
    for entry in entries:
        key = entry["key"]
        assert f"§ 2 Abs. 1 Nr. {NR_OF[key]} '" in entry["source"], key
        quoted = re.findall(r"'([^']+)'", entry["source"])
        assert quoted, key
        if key in STATUTE_TEXT:
            assert STATUTE_TEXT[key] in quoted, key
        else:
            assert NAME_OF[key] in quoted, key
        assert "SFTG" in entry["source"], key


def test_every_entry_is_verified_from_the_gazette_and_nothing_is_left_todo():
    """이 레포의 첫 전건 true 주 피드. 아홉 건은 제정 공포본(2004 Nr. 8 S. 213), Nr. 8
    은 개정 공포본(2018 Nr. 6 S. 69)이 자구 근거다. 각 source 는 그 공포본의 서지·
    공포일·연도판 PDF URL·sha256·열람일을 든다(/tmp/report_sh_gesetz_chain.md §1).
    의결 전 안(Drucksache)은 공포본이 상위 근거라 적지 않는다."""
    entries = _raw_entries()
    assert [e["key"] for e in entries if not e["verified"]] == []
    for entry in entries:
        key = entry["key"]
        assert entry["verified"] is True, key
        assert "source_todo" not in entry, f"{key}: 전건 true 인데 source_todo 가 있다"
        gazette = GAZETTE_2018 if key == "reformationstag" else GAZETTE_2004
        for value in gazette.values():
            assert value in entry["source"], (key, value)
        assert READ_ON in entry["source"], key
        assert "feiertage-api 2026 SH" in entry["source"], key
        assert "Drucksache" not in entry["source"], key


def test_the_reformation_day_source_names_the_amending_act():
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["reformationstag"]
    assert entry["name"] == "Reformationstag"
    assert (entry["month"], entry["day"]) == (10, 31)
    assert entry["scope"] == "land"
    assert "Gesetz zur Änderung des Gesetzes über Sonn- und Feiertage" in entry["source"]
    assert "21.03.2018" in entry["source"]
    assert "30.03.2018" in entry["source"]  # 시행일 — 2018 년 10-31 부터 적용
    assert "2004" not in entry["source"].split("—")[0]  # 조문 인용부는 2018 호가 근거


def test_the_renumbered_christmas_entries_cite_both_gazettes():
    """Nr. 9·10 의 자구는 2004 공포본(당시 Nr. 8·9)이고 번호는 2018 개정이 매겼다.
    source 는 둘 다 같은 완전성으로 들어야 한다 — 2004 쪽은 위 테스트가, 2018 쪽은
    여기서 서지·공포일·URL·sha256 네 값과 열람일을 전부 본다(Codex 리뷰 #60 지적)."""
    by_key = {e["key"]: e for e in _raw_entries()}
    for key in RENUMBERED_2018:
        source = by_key[key]["source"]
        for value in GAZETTE_2018.values():
            assert value in source, (key, value)
        assert READ_ON in source, key
        assert "재번호" in source, key
        old_nr = NR_OF[key] - 1
        assert f"Nr. {old_nr}" in source, key


def test_the_nationwide_nine_cite_the_2004_gazette_only_for_their_wording():
    by_key = {e["key"]: e for e in _raw_entries()}
    for key in NR_OF:
        if key == "reformationstag":
            continue
        assert by_key[key]["scope"] == "bundesweit", key
        assert "28.06.2004" in by_key[key]["source"], key
        assert GAZETTE_2004["cite"] in by_key[key]["source"], key
        if key not in RENUMBERED_2018:
            assert GAZETTE_2018["url"] not in by_key[key]["source"], key


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
    target = tmp_path / "de_sh.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_sh_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_sh.ics"
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
