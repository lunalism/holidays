"""독일·헤센 주 피드 — rules/de_he/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de_he.ics 는 헤센 주 전역의 법정 공휴일을 싣는다.
    근거 법령은 Hessisches Feiertagsgesetz (HFeiertagsG) § 1 Abs. 1 이다 —
    Nr. 1~9 의 열거, Nr. 9 "der 1. und 2. Weihnachtstag" 가 한 호에 이틀이라
    연 단위 구성은 고정 5 + 부활절 이동 5 = 10 건이다. 피드 범위(2020~) 안에
    일회성은 없다(§ 2 명령의 2017-10-31 은 범위 밖). 대체공휴일(이동) 규칙도 없다.

근거는 docs/research/report_he_be_gazette_access.md 이고, 요지는 rules/de_he/ 의
YAML source 필드에 옮겨 적었다. 조문은 공포본 두 호의 스캔 면을 판독해 읽었다 —
1971 Neufassung(GVBl. 1971 I Nr. 36 S. 343, § 1 은 S. 344)과 1994 개정(1994 I
Nr. 25 S. 596, Nr. 8 새 문언·Nr. 9·10 을 새 Nr. 9 로). 10 건 전부 verified: true
이고, 각 source 는 자기 호의 서지·공포일·PDF URL·sha256·열람일을 스스로 든다
(NW·BW 전례).

    a. feiertage-api 2026 HE 실측 10 건(hinweis 전부 공란) == de_he 2026 발행 집합
    b. 상위집합 — de.ics 9 건 ⊂ de_he.ics, 차집합 token 은 {fronleichnam} 하나
    c. 연도별 10 건 · 일요일 겹침 — 관례 이식
    d. UID — 전 항목 de_he- 접두사, de.ics·de_be.ics·de_by.ics 와 겹치지 않음
    e. 하니스 — python-holidays(subdiv='HE')와 연도별 날짜 집합 대조
    f. 헤더·DTEND·범위·근거 — 관례 이식. Nr. 9 한 호 이틀의 인용 처리 포함
    g. 근거 — 10 건 전부 verified true. 자기 공포본 호의 면·sha256·열람일,
       Nr. 8 은 1994 S. 596, Nr. 9 는 1994 새 문언 + 1971 종전 Nr. 10. source 는
       DESCRIPTION 에 그대로 실리므로 머리 주석을 가리키지 않고 '무개정' 판정어를
       쓰지 않는다

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

주 피드 교집합 == de.ics 테스트는 tests/test_de_be_feed.py 의 STATE_FEEDS(rules/ 스캔)가
이 주를 저절로 넣는다(여기 두지 않는다).
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
from rules.de_he import feed
from rules.de_he import status as de_he_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# UID token 의 접두사. 주 피드 규약 {피드토큰}-{key} (docs/holiday_12.md §6).
PREFIX = "de_he-"

# feiertage-api.de 2026 HE 실측(2026-09-06, ?jahr=2026&nur_land=HE). 10 건, 측정값
# 그대로. hinweis 는 열 개 모두 빈 문자열이었다 — 지자체·집단 한정 항목 없음.
FEIERTAGE_API_2026_HE = {
    "Neujahrstag": dt.date(2026, 1, 1),
    "Karfreitag": dt.date(2026, 4, 3),
    "Ostermontag": dt.date(2026, 4, 6),
    "Tag der Arbeit": dt.date(2026, 5, 1),
    "Christi Himmelfahrt": dt.date(2026, 5, 14),
    "Pfingstmontag": dt.date(2026, 5, 25),
    "Fronleichnam": dt.date(2026, 6, 4),
    "Tag der Deutschen Einheit": dt.date(2026, 10, 3),
    "1. Weihnachtstag": dt.date(2026, 12, 25),
    "2. Weihnachtstag": dt.date(2026, 12, 26),
}
FEIERTAGE_API_2026_HE_HINWEIS = {name: "" for name in FEIERTAGE_API_2026_HE}

# HFeiertagsG § 1 Abs. 1 의 열거 순서·조문 표기(공포본 1971 S. 344 + 1994 S. 596
# 적용 자구, 정관사 der 제외). Nr. 9 "der 1. und 2. Weihnachtstag" 는 두 항목으로 갈라
# 각자의 표기를 쓴다.
# token 은 전부 기존 확립값(de_be 의 9 종 + de_by 의 fronleichnam) — 신규 명명 0.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahrstag", "neujahr"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai"),
    (dt.date(2026, 5, 14), "Himmelfahrtstag", "christi_himmelfahrt"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag"),
    (dt.date(2026, 6, 4), "Fronleichnamstag", "fronleichnam"),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit"),
    (dt.date(2026, 12, 25), "1. Weihnachtstag", "erster_weihnachtstag"),
    (dt.date(2026, 12, 26), "2. Weihnachtstag", "zweiter_weihnachtstag"),
]
TOKENS = {PREFIX + key for _, _, key in EXPECTED_2026}

# 조문 호 번호. Nr. 9 가 이틀이라 key 둘이 같은 호를 가리킨다.
NR_OF = {
    "neujahr": 1, "karfreitag": 2, "ostermontag": 3, "erster_mai": 4,
    "christi_himmelfahrt": 5, "pfingstmontag": 6, "fronleichnam": 7,
    "tag_der_deutschen_einheit": 8, "erster_weihnachtstag": 9, "zweiter_weihnachtstag": 9,
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
# a. 첫 단언 — feiertage-api 2026 HE 전수 일치
# ---------------------------------------------------------------------------


def test_2026_dates_equal_feiertage_api(events):
    """멈춤 조건. API 10 건이 발행 집합과 다르면 구현을 멈추고 불일치 목록을
    보고한다. hinweis 가 붙은 항목이 생겨도 멈춤이다(조사 시점엔 전부 공란)."""
    assert len(FEIERTAGE_API_2026_HE) == 10
    assert all(h == "" for h in FEIERTAGE_API_2026_HE_HINWEIS.values())
    ours = _days(events, 2026)
    api = set(FEIERTAGE_API_2026_HE.values())
    assert ours == api, {"api_only": sorted(api - ours), "ours_only": sorted(ours - api)}


def test_2026_has_exactly_the_ten_hessian_holidays_in_statute_order(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == [(d, s, PREFIX + k) for d, s, k in EXPECTED_2026]


# ---------------------------------------------------------------------------
# b. 상위집합 — de.ics ⊂ de_he.ics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_nationwide_nine_are_a_subset_of_hesse(events, year):
    nationwide = {e.day for e in de_feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))}
    hesse = _days(events, year)
    assert len(nationwide) == 9
    assert nationwide <= hesse
    extra_tokens = {e.token for e in _year(events, year) if e.day not in nationwide}
    assert extra_tokens == {PREFIX + "fronleichnam"}


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
        (2023, dt.date(2023, 1, 1), "neujahr"),
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
        (2022, dt.date(2022, 5, 1), "erster_mai"),
        (2027, dt.date(2027, 12, 26), "zweiter_weihnachtstag"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, key):
    """§ 1 Abs. 1 은 "die Sonntage sowie …" 로 일요일 자체를 공휴일로 두고 이동
    조항이 없다. feiertage-api HE 실측에서도 보상 휴일 0 건. 일요일 항목은 그대로
    실리고 그 해는 10 건 그대로다."""
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 10
    assert [e.token for e in year_events if e.day == sunday] == [PREFIX + key]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. UID — 접두사 전수, 기존 세 독일 피드와 겹치지 않음
# ---------------------------------------------------------------------------


def test_every_token_starts_with_the_prefix_and_every_uid_is_date_plus_token(rendered, events):
    assert events and all(e.token.startswith(PREFIX) for e in events)
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    assert set(uids) == {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert all(uid.split("-", 1)[1].startswith(PREFIX) for uid in uids)


def test_no_uid_is_shared_with_the_other_german_feeds(rendered):
    """전국 공통 9 건은 de.ics·de_be.ics·de_by.ics 와, Fronleichnam 은 de_by.ics 와
    같은 날 같은 항목이다. 접두사가 유일한 방벽이다."""
    ours = {_prop(b, "UID") for b in _blocks(rendered)}
    for other in (de_feed, de_be_feed, de_by_feed):
        raw = other.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
        theirs = {_prop(b, "UID") for b in _blocks(raw.replace("\r\n ", ""))}
        assert theirs, f"{other.__name__} 발행본이 비었다 — 비교가 공허하다"
        assert ours & theirs == set(), other.__name__


def test_no_token_is_newly_coined(events):
    """token 은 전부 기존 확립값이다 — 공통 9 종은 de_be 와, fronleichnam 은
    de_by 와 key 가 같다. 신규 명명 0."""
    end = dt.date(2026, 12, 31)
    established = {e.token.removeprefix("de_be-") for e in de_be_feed.events(TODAY, end)}
    established |= {e.token.removeprefix("de_by-") for e in de_by_feed.events(TODAY, end)}
    assert {e.token.removeprefix(PREFIX) for e in events} <= established


def test_the_token_charset_has_no_digits_without_one_offs(events):
    for e in events:
        assert re.fullmatch(r"[a-z][a-z_]*", e.token.removeprefix(PREFIX)), e.token


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# e. 하니스 — python-holidays
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_hesse(events, year):
    """python-holidays 의 DE(subdiv='HE') 와 날짜 집합만 대조한다. 이름은 보지
    않는다 — 라이브러리 표기는 우리 표기(조문)와 다르고 그 차이는 사양이다."""
    holidays = pytest.importorskip("holidays")
    assert _days(events, year) == set(holidays.DE(subdiv="HE", years=year).keys())


# ---------------------------------------------------------------------------
# f. 헤더·DTEND·범위 — 관례 이식
# ---------------------------------------------------------------------------


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_header_names_hesse_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일·헤센 공휴일" in head
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
# g. 근거 — 항목별 호 인용·공포본 서지, verified 전건 true
# ---------------------------------------------------------------------------

# 공포본 두 호. 값의 정본은 rules/de_he/solar_holidays.yaml 머리 주석이고 여기는 그
# 사본이다 — 각 source 가 자기 호의 이 값들을 스스로 들어야 한다.
GAZETTE = {
    1971: {
        "issue": "GVBl. 1971 I Nr. 36 S. 343, § 1 은 S. 344",
        "proclaimed": "30.12.1971 공포",
        "url": "https://starweb.hessen.de/cache/GVBL/1971/00036.pdf",
        "sha256": "fc2067c2778f3db8a8b7295c72d25f7df020b1b18e512fb2b648432f9ec21f55",
    },
    1994: {
        "issue": "GVBl. 1994 I Nr. 25 S. 596",
        "proclaimed": "19.10.1994 공포",
        "url": "https://starweb.hessen.de/cache/GVBL/1994/00025.pdf",
        "sha256": "a16fbf4cc3298d219e56cc8e0d1f7354d3d33c822058f41b3c07153ef0ef8ff5",
    },
}
READ_ON = "2026-09-29 열람"

# 1994 이후 개정이 없다는 것은 검색 사실로 적는다(NW 전례). 판정어 '무개정' 을 구독자
# 문장에 쓰지 않는다.
NO_LATER_AMENDMENT = (
    "§ 1 Abs. 1 의 1994 이후 개정은 찾지 못함(GVBl. 2026 Nr. 65 까지, "
    "공포본 자기 인용·연간 색인·전 호 검색)"
)

# 항목별로 근거가 되는 공포본 호. Nr. 8 은 1994 의 새 문언, Nr. 9 는 1994 의 새 Nr. 9 에
# 1971 종전 Nr. 10 을 곁들이고, 나머지는 1971 의 자구 그대로다.
OWN_ISSUES = {key: (1971,) for key in NR_OF}
OWN_ISSUES["tag_der_deutschen_einheit"] = (1994,)
OWN_ISSUES["erster_weihnachtstag"] = (1994, 1971)
OWN_ISSUES["zweiter_weihnachtstag"] = (1994, 1971)


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def _source(entry) -> str:
    """source 를 DESCRIPTION 처럼 한 줄로 편다. YAML 접힘이 URL·sha256 을 가르지 않게."""
    return " ".join(entry["source"].split())


def test_the_tables_hold_ten_entries_each_citing_its_own_number_of_section_1():
    """조 단위 일괄 인용이 아니라 항목별 호 인용이다. 각 source 는 § 1 Abs. 1 의
    자기 호 번호를 대고 그 호의 조문 표기를 따옴표로 담는다."""
    entries = _raw_entries()
    assert len(entries) == 10
    assert {e["key"] for e in entries} == set(NR_OF)
    name_of = {key: name for _, name, key in EXPECTED_2026}
    for entry in entries:
        key = entry["key"]
        assert f"§ 1 Abs. 1 Nr. {NR_OF[key]}" in entry["source"], key
        quoted = re.findall(r"'([^']+)'", entry["source"])
        assert quoted, key
        if NR_OF[key] == 9:
            # 한 호 이틀 — 인용은 호의 원문 그대로, 표기는 각자의 것.
            assert "der 1. und 2. Weihnachtstag" in quoted, key
            assert entry["name"] == name_of[key], key
        else:
            assert any(name_of[key] in q for q in quoted), key


def test_the_two_christmas_days_share_number_nine_but_keep_their_own_names():
    by_key = {e["key"]: e for e in _raw_entries()}
    first, second = by_key["erster_weihnachtstag"], by_key["zweiter_weihnachtstag"]
    assert first["name"] == "1. Weihnachtstag" and second["name"] == "2. Weihnachtstag"
    assert (first["month"], first["day"]) == (12, 25)
    assert (second["month"], second["day"]) == (12, 26)
    assert "Nr. 9" in first["source"] and "Nr. 9" in second["source"]


def test_all_ten_are_verified_and_nothing_is_left_to_do():
    """공포본 두 호로 10 건 전부 확인했다. source_todo 는 남기지 않는다."""
    entries = _raw_entries()
    assert [e["key"] for e in entries if e["verified"] is not True] == []
    for entry in entries:
        assert "source_todo" not in entry, f"{entry['key']}: 전건 true 인데 source_todo 가 있다"
        assert "feiertage-api" in entry["source"], entry["key"]


def test_each_source_carries_its_own_gazette_issue_page_hash_and_reading_date():
    """source 는 DESCRIPTION 에 그대로 실리므로 서지를 스스로 들어야 한다(NW·BW 전례).
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


def test_unity_day_cites_the_1994_wording_that_replaced_the_17th_of_june():
    source = _source({e["key"]: e for e in _raw_entries()}["tag_der_deutschen_einheit"])
    assert "Art. 1 Nr. 1 a)" in source
    assert "'der Tag der Deutschen Einheit'" in source
    assert "'der Tag der deutschen Einheit (17. Juni)'" in source  # 종전 문언


def test_both_christmas_days_cite_the_new_number_nine_and_the_old_number_ten():
    by_key = {e["key"]: e for e in _raw_entries()}
    for key in ("erster_weihnachtstag", "zweiter_weihnachtstag"):
        source = _source(by_key[key])
        assert "Art. 1 Nr. 1 b)" in source, key
        assert "'der 1. und 2. Weihnachtstag'" in source, key
        assert "'der 1. und 2. Weihnachtsfeiertag'" in source, key  # 1971 종전 Nr. 10


def test_no_source_points_to_the_header_comment_or_states_a_verdict():
    """source 는 DESCRIPTION 의 '근거:' 뒤에 그대로 나간다. 구독자는 YAML 을 볼 수 없으므로
    머리 주석을 가리키면 안 되고, 1994 이후는 '찾지 못함' 이라는 검색 사실로 적는다."""
    for entry in _raw_entries():
        assert "머리 주석" not in entry["source"], entry["key"]
        assert "solar_holidays.yaml" not in entry["source"], entry["key"]
        assert "무개정" not in entry["source"], entry["key"]


def test_the_corpus_christi_source_says_the_offset_is_customary():
    by_key = {e["key"]: e for e in _raw_entries()}
    entry = by_key["fronleichnam"]
    assert entry["easter_offset"] == 60
    assert entry["name"] == "Fronleichnamstag"
    assert "관습" in entry["source"] and "+60" in entry["source"]


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
    target = tmp_path / "de_he.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_he_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de_he.ics"
    assert got["events"] == 10 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (de_be·de_by 와 같은 규약)
# ---------------------------------------------------------------------------


def _table(tmp_path, key: str):
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {"holidays": [{"key": key, "name": "Neujahrstag", "month": 1, "day": 1,
                           "verified": False, "source": "test", "scope": "land"}]},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("neujahr\n", id="끝 개행"),
        pytest.param("Neujahr", id="대문자"),
        pytest.param("1_weihnachtstag", id="서수를 숫자로"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(_table(tmp_path, bad_key), "month", "day")


def test_an_established_key_loads(tmp_path):
    [entry] = feed._load(_table(tmp_path, "neujahr"), "month", "day")
    assert entry["key"] == "neujahr"
