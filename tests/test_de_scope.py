"""독일 계열 아홉 피드 — scope 필드와 DESCRIPTION 첫 줄.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    주 피드 여덟(de_be·de_bw·de_by·de_he·de_hh·de_ni·de_nw·de_sh)의 YAML 전 항목에는 scope 가
    있고 값은 {bundesweit, land} 뿐이다. bundesweit 인 key 집합은 전국 피드
    rules/de/ 의 key 집합과 같다(9 건). 전국 피드 YAML 에는 scope 를 두지
    않는다 — 정의상 전부 bundesweit 라 필드가 있으면 오히려 오류다.

    DESCRIPTION 은 세 줄이다: 구독자용 문장 / 빈 줄 / "근거: …".
        bundesweit  "독일 전국 공휴일입니다."
        land        "{주명} 주 공휴일입니다."
    전국 피드는 필드 없이 첫 줄을 "독일 전국 공휴일입니다." 로 고정한다.

bundesweit 9 건의 근거는 /tmp/report_bundesweit.md — feiertage-api 2025·2026
16 주 교집합이 API 의 NATIONAL 키·rules/de YAML 과 삼중 일치했다. 여기서는
그 결과를 데이터끼리 교차 검증으로 고정한다: 주 피드에서 bundesweit 로 표시된
key 집합이 rules/de 의 key 집합과 다르면(전국 항목을 land 로, 주 항목을
bundesweit 로 잘못 적으면) 어느 쪽이든 집합이 어긋나 깨진다.

    a. 교차 검증 — 여덟 피드 각각의 bundesweit key 집합 == rules/de key 집합
    b. 로더 — scope 누락·미정의 값은 여덟 로더 전부에서 실패, de 는 scope 존재가 실패
    c. DESCRIPTION — 첫 줄 문장·빈 줄·"근거: " 유지, 직렬화(\\n 이스케이프·75 옥텟
       접기)가 한글에서 깨지지 않음

발행하지 않는다. build() 로 메모리에서 만들어 보고, 로더는 tmp_path 의 표로
부른다. 시계를 읽지 않는다.
"""

from __future__ import annotations

import datetime as dt

import icalendar
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
from rules.de_sh import feed as de_sh_feed

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
TODAY = dt.date(2026, 1, 1)

STATE_FEEDS = {
    "de_be": de_be_feed,
    "de_bw": de_bw_feed,
    "de_by": de_by_feed,
    "de_he": de_he_feed,
    "de_hh": de_hh_feed,
    "de_ni": de_ni_feed,
    "de_nw": de_nw_feed,
    "de_sh": de_sh_feed,
}

# 주명은 여기서 고정한다. feed.py 의 상수가 바뀌면 여기가 먼저 깨진다.
LAND_NAMES = {
    "de_be": "베를린",
    "de_bw": "바덴뷔르템베르크",
    "de_by": "바이에른",
    "de_he": "헤센",
    "de_hh": "함부르크",
    "de_ni": "니더작센",
    "de_nw": "노르트라인베스트팔렌",
    "de_sh": "슐레스비히홀슈타인",
}

BUNDESWEIT_SENTENCE = "독일 전국 공휴일입니다."


def _tables(feed) -> list:
    """피드 모듈이 읽는 YAML 경로 전부. designated 표는 있는 피드만."""
    paths = [feed.SOLAR_PATH, feed.EASTER_PATH]
    designated = getattr(feed, "DESIGNATED_PATH", None)
    if designated is not None:
        paths.append(designated)
    return paths


def _raw_entries(feed) -> list:
    out = []
    for path in _tables(feed):
        out.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"])
    return out


def _events(feed) -> list:
    start, end = feed.feed_range(TODAY)
    return feed.events(start, end)


def _rendered(feed) -> bytes:
    return feed.build(today=TODAY, dtstamp=DTSTAMP)


# ---------------------------------------------------------------------------
# a. 교차 검증 — bundesweit key 집합 == rules/de key 집합
# ---------------------------------------------------------------------------


def test_the_nationwide_tables_hold_nine_keys_and_no_scope():
    entries = _raw_entries(de_feed)
    assert len(entries) == 9
    assert all("scope" not in e for e in entries), "전국 피드 YAML 에 scope 가 있다"


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
def test_every_state_entry_has_a_scope_from_the_closed_set(name):
    entries = _raw_entries(STATE_FEEDS[name])
    assert entries, name
    for e in entries:
        assert e.get("scope") in ("bundesweit", "land"), (name, e.get("key"), e.get("scope"))


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
def test_bundesweit_keys_equal_the_nationwide_keys(name):
    """오분류를 양방향으로 잡는다 — 전국 항목을 land 로 적으면 왼쪽이 모자라고,
    주 항목을 bundesweit 로 적으면 왼쪽이 넘친다."""
    nationwide = {e["key"] for e in _raw_entries(de_feed)}
    marked = {e["key"] for e in _raw_entries(STATE_FEEDS[name]) if e.get("scope") == "bundesweit"}
    assert marked == nationwide, f"{name}: 차집합 {sorted(marked ^ nationwide)}"


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
def test_land_keys_never_overlap_the_nationwide_keys(name):
    nationwide = {e["key"] for e in _raw_entries(de_feed)}
    land = {e["key"] for e in _raw_entries(STATE_FEEDS[name]) if e.get("scope") == "land"}
    assert land & nationwide == set(), name
    assert land, f"{name}: 주 고유 항목이 하나도 없다 — 표가 잘못 읽혔다"


# ---------------------------------------------------------------------------
# b. 로더 — 여덟 로더의 scope 검증, de 의 금지 단언
# ---------------------------------------------------------------------------


def _table(tmp_path, **entry):
    base = {"key": "neujahr", "name": "Neujahrstag", "month": 1, "day": 1,
            "verified": False, "source": "test"}
    base.update(entry)
    path = tmp_path / "solar_holidays.yaml"
    path.write_text(yaml.safe_dump({"holidays": [base]}, allow_unicode=True), encoding="utf-8")
    return path


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
def test_a_missing_scope_stops_the_state_load(tmp_path, name):
    with pytest.raises(ics.IcsError, match="scope"):
        STATE_FEEDS[name]._load(_table(tmp_path), "month", "day")


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
@pytest.mark.parametrize(
    "bad",
    [
        pytest.param("Bundesweit", id="대문자"),
        pytest.param("national", id="다른 낱말"),
        pytest.param("land\n", id="끝 개행"),
        pytest.param("", id="빈 문자열"),
        pytest.param(True, id="불리언"),
    ],
)
def test_an_undefined_scope_stops_the_state_load(tmp_path, name, bad):
    with pytest.raises(ics.IcsError, match="scope"):
        STATE_FEEDS[name]._load(_table(tmp_path, scope=bad), "month", "day")


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
@pytest.mark.parametrize("good", ["bundesweit", "land"])
def test_a_defined_scope_loads(tmp_path, name, good):
    [entry] = STATE_FEEDS[name]._load(_table(tmp_path, scope=good), "month", "day")
    assert entry["scope"] == good


@pytest.mark.parametrize("scope", ["bundesweit", "land"])
def test_a_scope_key_stops_the_nationwide_load(tmp_path, scope):
    """전국 피드는 정의상 전부 bundesweit 라 필드를 두지 않는다. 값이 맞아도 막는다."""
    with pytest.raises(ics.IcsError, match="scope"):
        de_feed._load(_table(tmp_path, scope=scope), "month", "day")


def test_the_nationwide_load_without_scope_succeeds(tmp_path):
    [entry] = de_feed._load(_table(tmp_path), "month", "day")
    assert "scope" not in entry


# ---------------------------------------------------------------------------
# c. DESCRIPTION — 문장 / 빈 줄 / 근거
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
def test_state_land_names_are_fixed(name):
    assert STATE_FEEDS[name].LAND_NAME == LAND_NAMES[name]


@pytest.mark.parametrize("name", sorted(STATE_FEEDS))
def test_state_descriptions_are_sentence_blank_source(name):
    feed = STATE_FEEDS[name]
    scope_of = {e["key"]: e["scope"] for e in _raw_entries(feed)}
    source_of = {e["key"]: " ".join(e["source"].split()) for e in _raw_entries(feed)}
    expected = {
        "bundesweit": BUNDESWEIT_SENTENCE,
        "land": f"{LAND_NAMES[name]} 주 공휴일입니다.",
    }
    events = _events(feed)
    assert events
    for e in events:
        key = e.token.removeprefix(feed.TOKEN_PREFIX)
        lines = e.description.split("\n")
        assert len(lines) == 3, (name, key, lines)
        assert lines[0] == expected[scope_of[key]], (name, key, lines[0])
        assert lines[1] == "", (name, key)
        assert lines[2] == f"근거: {source_of[key]}", (name, key)


def test_nationwide_descriptions_start_with_the_nationwide_sentence():
    source_of = {e["key"]: " ".join(e["source"].split()) for e in _raw_entries(de_feed)}
    events = _events(de_feed)
    assert events
    for e in events:
        lines = e.description.split("\n")
        assert lines == [BUNDESWEIT_SENTENCE, "", f"근거: {source_of[e.token]}"], e.token


ALL_FEEDS = {"de": de_feed, **STATE_FEEDS}


@pytest.mark.parametrize("name", sorted(ALL_FEEDS))
def test_the_serialized_description_escapes_newlines_and_folds_safely(name):
    """RFC 5545: 값 안의 개행은 \\n 으로 이스케이프되고 줄은 75 옥텟에서 접힌다.
    한글은 한 글자가 3 옥텟이라 접힘 자리가 글자 중간에 떨어지면 안 된다 —
    물리 줄마다 따로 UTF-8 로 풀리는지, 풀어서 파싱한 값이 원본과 같은지 본다."""
    feed = ALL_FEEDS[name]
    raw = _rendered(feed)
    assert b"\\n\\n\xea\xb7\xbc\xea\xb1\xb0: " in raw  # "\n\n근거: " 이스케이프 형태
    for line in raw.split(b"\r\n"):
        assert len(line) <= 75, line
        line.decode("utf-8")  # 글자 중간에서 접혔으면 여기서 죽는다
    expected = {e.token: e.description for e in _events(feed)}
    parsed = icalendar.Calendar.from_ical(raw)
    got = {}
    for vevent in parsed.walk("VEVENT"):
        token = str(vevent["UID"]).split("-", 1)[1].split("@", 1)[0]
        got[token] = str(vevent["DESCRIPTION"])
    assert got == expected
