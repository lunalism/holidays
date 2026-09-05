"""독일 전국 공통 피드 — rules/de/ 가 내는 .ics 가 확정 사양대로 나오는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    de.ics 는 16 개 주 전체에서 유효한 법정 공휴일 9 건만 싣는다.
    대체공휴일(이동) 규칙은 없다 — 일요일과 겹쳐도 그 날짜 그대로다.

근거는 /tmp/report_de.md·/tmp/report_de_2.md 의 실측이고, 요지는 rules/de/
의 YAML source 필드에 옮겨 적었다. 여기서는 그 사양을 숫자와 날짜로 못 박는다.

    a. 2026 년 9 건 전수 — 날짜·SUMMARY·token
    b. 부활절 이동 4 건 — 2021·2024·2038(부활절 상한 04-25)
    c. 일요일 겹침 연도 — 건수 9 유지. 이동 규칙 부재의 회귀 픽스처
    d. 하니스 — python-holidays(subdiv 없음)와 연도별 날짜 집합 대조
    e. UID·DTEND·헤더·범위 — 기존 core 관례

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. 시계를 읽지 않는다 — today·dtstamp 를 고정값으로 준다.

--------------------------------------------------------------------------
하니스의 자리
--------------------------------------------------------------------------
python-holidays 는 대조 상대이지 채택 소스가 아니다. 우리 값은 rules/de/ 의
YAML 과 부활절 계산에서 나오고, 라이브러리와는 갈리는지만 본다. 갈리면 어느
쪽이 맞는지는 법조문으로 정한다(rules/de/*.yaml 의 source).

라이브러리는 pyproject 의 dev 그룹에 이미 고정되어 있다(holidays==0.102).
본 의존성에는 넣지 않는다 — 피드 생성이 라이브러리에 기대면 위 명제가
"라이브러리와 같다"로 퇴화한다.
"""

from __future__ import annotations

import datetime as dt
import re

import pytest
import yaml

from core import ics
from rules.de import feed
from rules.de import status as de_status

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

# /tmp/report_de_2.md §3 의 표. SUMMARY 는 법조문 표기(BayFTG Art. 1 / BW FTG § 1),
# token 은 서수를 풀어 쓴 식별자다.
EXPECTED_2026 = [
    (dt.date(2026, 1, 1), "Neujahr", "neujahr"),
    (dt.date(2026, 4, 3), "Karfreitag", "karfreitag"),
    (dt.date(2026, 4, 6), "Ostermontag", "ostermontag"),
    (dt.date(2026, 5, 1), "1. Mai", "erster_mai"),
    (dt.date(2026, 5, 14), "Christi Himmelfahrt", "christi_himmelfahrt"),
    (dt.date(2026, 5, 25), "Pfingstmontag", "pfingstmontag"),
    (dt.date(2026, 10, 3), "Tag der Deutschen Einheit", "tag_der_deutschen_einheit"),
    (dt.date(2026, 12, 25), "Erster Weihnachtstag", "erster_weihnachtstag"),
    (dt.date(2026, 12, 26), "Zweiter Weihnachtstag", "zweiter_weihnachtstag"),
]

# 부활절 기준 오프셋. /tmp/report_de.md §3 — Karfreitag −2, Ostermontag +1,
# Christi Himmelfahrt +39, Pfingstmontag +50.
EASTER_OFFSETS = {
    "karfreitag": -2,
    "ostermontag": 1,
    "christi_himmelfahrt": 39,
    "pfingstmontag": 50,
}

# 부활절 날짜의 정답. 2038-04-25 는 그레고리력 부활절의 상한이다.
EASTER = {
    2021: dt.date(2021, 4, 4),
    2024: dt.date(2024, 3, 31),
    2038: dt.date(2038, 4, 25),
}


@pytest.fixture(scope="module")
def events():
    return feed.events(*feed.feed_range(TODAY))


@pytest.fixture(scope="module")
def rendered():
    """폴딩을 푼 .ics 본문. 한 속성이 한 줄이 되게 한다(test_jp_feed.py 참조)."""
    raw = feed.build(today=TODAY, dtstamp=DTSTAMP).decode("utf-8")
    return raw.replace("\r\n ", "").replace("\r\n\t", "")


def _year(events, year: int) -> list:
    return [e for e in events if e.day.year == year]


def _blocks(rendered) -> list:
    return [b.split("END:VEVENT")[0] for b in rendered.split("BEGIN:VEVENT")[1:]]


def _prop(block: str, name: str) -> str:
    match = re.search(rf"^{name}(?:;[^:]*)?:(.*?)\r?$", block, re.MULTILINE)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# a. 2026 년 9 건 전수
# ---------------------------------------------------------------------------


def test_2026_has_exactly_the_nine_nationwide_holidays(events):
    got = [(e.day, e.summary, e.token) for e in _year(events, 2026)]
    assert got == EXPECTED_2026


@pytest.mark.parametrize("year", range(2020, 2032))
def test_every_year_in_range_has_exactly_nine_events(events, year):
    """9 건은 2026 만의 우연이 아니다. 범위 안 모든 해가 9 건이어야 한다.

    주별 항목이 새어 들어오거나(10 건 이상) 부활절 계산이 해를 건너뛰면
    (8 건 이하) 여기서 걸린다.
    """
    assert len(_year(events, year)) == 9


def test_the_token_set_is_the_same_every_year(events):
    """token 은 연도와 무관하게 같은 9 개다. UID 의 뒷부분이 해마다 흔들리면
    안 된다."""
    by_year = {}
    for e in events:
        by_year.setdefault(e.day.year, set()).add(e.token)
    expected = {token for _, _, token in EXPECTED_2026}
    assert all(tokens == expected for tokens in by_year.values()), by_year


# ---------------------------------------------------------------------------
# b. 부활절 이동 4 건
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", sorted(EASTER))
@pytest.mark.parametrize("token", sorted(EASTER_OFFSETS))
def test_easter_based_holidays_land_on_the_right_day(token, year):
    """부활절 + 오프셋. 부활절 자체는 EASTER 표의 정답과 대조한다 —
    계산기가 정답을 내는지, 오프셋이 맞는지 둘 다 여기서 본다."""
    start, end = dt.date(year, 1, 1), dt.date(year, 12, 31)
    found = [e for e in feed.events(start, end) if e.token == token]
    assert len(found) == 1, found
    assert found[0].day == EASTER[year] + dt.timedelta(days=EASTER_OFFSETS[token])


def test_easter_sunday_itself_is_not_an_event(events):
    """부활절 일요일(Ostersonntag)은 브란덴부르크만의 공휴일이라 전국 공통이
    아니다. 오프셋 0 이 새어 들어오면 안 된다."""
    for year, easter in EASTER.items():
        found = [e for e in feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))]
        assert easter not in {e.day for e in found}
    assert "ostersonntag" not in {e.token for e in events}


# ---------------------------------------------------------------------------
# c. 일요일 겹침 — 이동 규칙 부재의 회귀 픽스처
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "year, sunday, token",
    [
        (2021, dt.date(2021, 10, 3), "tag_der_deutschen_einheit"),
        (2022, dt.date(2022, 12, 25), "erster_weihnachtstag"),
    ],
)
def test_a_holiday_on_a_sunday_stays_on_the_sunday_and_adds_nothing(year, sunday, token):
    """/tmp/report_de_2.md §2 — BayFTG 전문에 이동 조항이 없고, feiertage-api
    의 2021·2022 실측도 보상 휴일 0 건이다. 일요일에 놓인 항목은 그대로 실리고,
    건수는 9 그대로다.
    """
    assert sunday.weekday() == 6, "픽스처 날짜가 일요일이 아니다"
    year_events = feed.events(dt.date(year, 1, 1), dt.date(year, 12, 31))
    assert len(year_events) == 9
    on_sunday = [e for e in year_events if e.day == sunday]
    assert [e.token for e in on_sunday] == [token]
    assert not any("sub" in e.token or "ersatz" in e.token for e in year_events)


# ---------------------------------------------------------------------------
# d. 하니스 — python-holidays 와 날짜 집합 대조
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("year", range(2020, 2032))
def test_the_dates_agree_with_python_holidays_nationwide(events, year):
    """python-holidays 의 subdiv 없는 DE 는 전국 공통 9 건을 낸다
    (/tmp/report_de.md §4). 날짜 집합이 같아야 한다.

    이름은 비교하지 않는다 — 라이브러리 표기(Erster Mai 등)는 우리 표기
    (법조문)와 다르고, 그 차이는 사양이다(/tmp/report_de_2.md §3).
    """
    holidays = pytest.importorskip("holidays")
    ours = {e.day for e in _year(events, year)}
    theirs = set(holidays.DE(years=year).keys())
    assert ours == theirs


# ---------------------------------------------------------------------------
# e. UID·DTEND·헤더·범위 — 기존 core 관례
# ---------------------------------------------------------------------------


def test_every_uid_is_date_plus_token(rendered, events):
    uids = [_prop(b, "UID") for b in _blocks(rendered)]
    assert len(uids) == len(events) > 0
    assert len(set(uids)) == len(uids)
    expected = {f"{e.day:%Y%m%d}-{e.token}@{ics.UID_DOMAIN}" for e in events}
    assert set(uids) == expected


def test_the_same_input_produces_byte_identical_output():
    assert feed.build(today=TODAY, dtstamp=DTSTAMP) == feed.build(today=TODAY, dtstamp=DTSTAMP)


def test_dtend_is_the_exclusive_next_day(rendered):
    for block in _blocks(rendered):
        start = dt.datetime.strptime(_prop(block, "DTSTART"), "%Y%m%d").date()
        end = dt.datetime.strptime(_prop(block, "DTEND"), "%Y%m%d").date()
        assert end == start + dt.timedelta(days=1)


def test_the_token_charset_is_ascii_lowercase_without_ordinals(events):
    """서수는 풀어 쓰고(erster_mai) 움라우트는 ae/oe/ue/ss 로 옮긴다. 이번 9 건에
    움라우트는 없지만 규약은 charset 으로 강제한다."""
    for e in events:
        assert re.fullmatch(r"[a-z][a-z_]*", e.token), e.token


def test_the_header_names_germany_and_berlin_time(rendered):
    head = rendered.split("BEGIN:VEVENT")[0]
    assert "X-WR-CALNAME:독일 공휴일 (전국 공통)" in head
    assert "X-WR-TIMEZONE:Europe/Berlin" in head
    assert "PRODID:-//lunalism//holidays.lunalism.com//KO" in head


def test_every_event_is_transparent_and_free(rendered):
    for block in _blocks(rendered):
        assert _prop(block, "TRANSP") == "TRANSPARENT"
        assert _prop(block, "X-MICROSOFT-CDO-BUSYSTATUS") == "FREE"


def test_nothing_is_marked_tentative(rendered, events):
    """de 는 provisional 이 없다. 규칙이 개정 확인 시점에 매이지 않는다 —
    9 건 전부 고정 날짜이거나 부활절 계산이다."""
    assert "STATUS:TENTATIVE" not in rendered
    assert not any(e.provisional for e in events)


def test_the_range_follows_the_kr_policy():
    """하한 2020-01-01 고정, 상한은 today 기준 YEARS_AHEAD 년 뒤 12-31."""
    assert feed.feed_range(dt.date(2026, 1, 1)) == (dt.date(2020, 1, 1), dt.date(2031, 12, 31))
    assert feed.feed_range(dt.date(2020, 6, 1)) == (dt.date(2020, 1, 1), dt.date(2025, 12, 31))


def test_every_event_falls_inside_the_range(events):
    start, end = feed.feed_range(TODAY)
    assert all(start <= e.day <= end for e in events)


# ---------------------------------------------------------------------------
# 근거 — source 는 나가고 verified·source_todo 는 나가지 않는다
# ---------------------------------------------------------------------------


def _raw_entries() -> list:
    out = []
    for path in (feed.SOLAR_PATH, feed.EASTER_PATH):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        out.extend(doc["holidays"])
    return out


def test_the_tables_hold_exactly_nine_entries_with_sources():
    entries = _raw_entries()
    assert len(entries) == 9
    assert {e["key"] for e in entries} == {token for _, _, token in EXPECTED_2026}
    for entry in entries:
        assert entry.get("source"), entry["key"]
        assert isinstance(entry.get("verified"), bool), entry["key"]


def test_only_the_unity_day_is_verified():
    """Einigungsvertrag Art. 2 Abs. 2 원문을 본 것은 통일의 날 하나다. 나머지
    8 건은 주법 16 벌 중 BayFTG 하나만 원문 대조라 verified: false 다."""
    by_key = {e["key"]: e for e in _raw_entries()}
    assert by_key["tag_der_deutschen_einheit"]["verified"] is True
    assert "source_todo" not in by_key["tag_der_deutschen_einheit"]
    for key, entry in by_key.items():
        if key != "tag_der_deutschen_einheit":
            assert entry["verified"] is False, key
            assert entry.get("source_todo"), key


def test_every_description_carries_the_source(events):
    by_key = {e["key"]: e for e in _raw_entries()}
    for e in events:
        assert e.description.startswith("근거: "), e
        assert " ".join(by_key[e.token]["source"].split()) in e.description
        assert "\n" not in e.description


def test_our_verification_state_never_reaches_the_feed(rendered):
    for word in ("verified", "source_todo", "미검증", "확인 대기"):
        assert word not in rendered


# ---------------------------------------------------------------------------
# 발행과 status 조각
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    target = tmp_path / "de.ics"
    first = feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert first == target and target.exists()
    before = target.read_bytes()
    feed.publish(today=TODAY, dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp*")), "임시 파일이 남았다"


def test_the_status_piece_follows_the_kr_contract():
    got = de_status.feed_status(today=TODAY)
    assert got["path"] == "feeds/de.ics"
    assert got["events"] == 9 * 12
    assert got["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["provisional_events"] == 0


# ---------------------------------------------------------------------------
# key 경계 — 로드 시점에 거부한다 (Codex 지적: $ 앵커가 끝 개행을 허용했다)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_key",
    [
        pytest.param("neujahr\n", id="끝 개행"),
        pytest.param("neu jahr", id="공백 포함"),
        pytest.param("Neujahr", id="대문자"),
        pytest.param("mariä_himmelfahrt", id="비ASCII 움라우트"),
    ],
)
def test_a_key_outside_the_charset_stops_the_load(tmp_path, bad_key):
    """key 는 UID token 이 된다. 규약 밖 값은 _load() 에서 멈춰야 한다 —
    발행까지 가면 잘못된 영구 식별자가 나간다.

    끝 개행 케이스가 핵심이다. `^...$` 와 match() 는 문자열 끝의 개행 하나를
    통과시킨다. fullmatch() 여야 한다.
    """
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "holidays": [
                    {
                        "key": bad_key,
                        "name": "Neujahr",
                        "month": 1,
                        "day": 1,
                        "verified": False,
                        "source": "test",
                    }
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ics.IcsError, match="key 가 규약 밖"):
        feed._load(path, "month", "day")
