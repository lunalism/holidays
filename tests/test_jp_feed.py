"""일본 피드 — data/jp/ 를 읽어 만든 .ics 가 확정 사양대로 나오는가.

발행하지 않는다. build() 로 메모리에서 만들어 보고, publish() 는 tmp_path 로만
부른다. feeds/ 아래에 쓰지 않는다 — 이 브랜치는 "만들 수 있다"까지이고,
발행은 다음 브랜치다.

시계를 읽지 않는다. dtstamp 를 고정값으로 준다(core/ics.py 의 DTSTAMP 절).
"""

from __future__ import annotations

import datetime as dt
import re

import pytest
import yaml

from core import ics
from rules.jp import feed
from sources.jp import build_data

DTSTAMP = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)

# 데이터 총량. docs/holiday_06.md §1 의 표와 같은 수다.
TOTAL = 143


def _raw_entries() -> list:
    """YAML 을 직접 읽은 원자료. feed 를 거치지 않는다 — 대조 상대여야 한다."""
    out = []
    for path in sorted(build_data.DATA_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        out.extend(doc["holidays"])
    return out


@pytest.fixture(scope="module")
def events():
    return feed.events()


@pytest.fixture(scope="module")
def rendered():
    """폴딩을 푼 .ics 본문. 한 속성이 한 줄이 되게 한다.

    RFC 5545 는 긴 줄을 75 옥텟에서 접고 다음 줄을 공백으로 시작한다. 접힌
    채로 grep 하면 SUMMARY 한복판에서 끊긴 줄을 보게 된다.
    """
    raw = feed.build(dtstamp=DTSTAMP).decode("utf-8")
    return raw.replace("\r\n ", "").replace("\r\n\t", "")


def _blocks(rendered) -> dict:
    """{DTSTART 날짜: VEVENT 한 덩어리}."""
    out = {}
    for block in rendered.split("BEGIN:VEVENT")[1:]:
        block = block.split("END:VEVENT")[0]
        stamp = re.search(r"^DTSTART;VALUE=DATE:(\d{8})\r?$", block, re.MULTILINE).group(1)
        out[dt.date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))] = block
    return out


def _text(block: str, name: str) -> str:
    """VEVENT 한 덩어리에서 TEXT 속성 하나의 값.

    RFC 5545 의 TEXT 이스케이프를 되돌린다. 쉼표는 \\, 로 나가므로 되돌리지
    않으면 bridge 의 DESCRIPTION 이 원문과 다르게 읽힌다.
    """
    match = re.search(rf"^{name}:(.*)$", block, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    for escaped, plain in ((r"\,", ","), (r"\;", ";"), (r"\\", "\\")):
        value = value.replace(escaped, plain)
    return value


# ---------------------------------------------------------------------------
# 잠정 표시 — jp 에는 없다
# ---------------------------------------------------------------------------


def test_nothing_is_marked_tentative(rendered):
    """STATUS:TENTATIVE 도 X-HOLIDAY-STATUS 도 0 줄이다.

    대소문자를 무시하고 센다. core/ics.py 의 리터럴은 소문자
    x-holiday-status 이고 직렬화되면서 대문자가 된다 — 소스를 대문자로
    grep 하면 0 건이 나와 미구현으로 읽히는 자리다.
    """
    lowered = rendered.lower()
    assert lowered.count("status:tentative") == 0
    assert lowered.count("x-holiday-status") == 0


def test_no_event_carries_the_provisional_flag(events):
    """출력만이 아니라 Event 쪽도 본다. 항상 False 가 사양이다."""
    assert [e for e in events if e.provisional] == []


# ---------------------------------------------------------------------------
# 발행 범위
# ---------------------------------------------------------------------------


def test_every_event_falls_inside_the_publish_range(events):
    assert len(events) == TOTAL
    outside = [e for e in events if not (feed.RANGE_START <= e.day <= feed.RANGE_END)]
    assert outside == []


def test_the_range_comes_from_the_source_module():
    """상수를 새로 정의하지 않았다. 두 곳에 적으면 갈린다."""
    assert feed.RANGE_START is build_data.RANGE_START
    assert feed.RANGE_END is build_data.RANGE_END


def test_an_entry_outside_the_range_stops_the_build(tmp_path, monkeypatch):
    """조용히 거르지 않는다. 범위 밖은 예외다."""
    path = tmp_path / "9999.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "country": "jp",
                "year": 9999,
                "holidays": [
                    {
                        "date": dt.date(9999, 1, 1),
                        "name": "元日",
                        "uid_token": "new_years_day",
                        "kind": "statutory",
                        "verified": True,
                        "source": "…",
                    }
                ],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(feed, "DATA_DIR", tmp_path)
    with pytest.raises(ics.IcsError, match="발행 범위"):
        feed.events()


# ---------------------------------------------------------------------------
# 읽는 경로와 쓰는 경로
# ---------------------------------------------------------------------------


def test_the_read_path_and_the_write_path_agree():
    """feed 는 build_data.DATA_DIR 을 import 하지 않는다. 같은 곳인지만 본다.

    묶어 두지 않는 이유는 feed.DATA_DIR 주석에 있다. 대신 갈라지면 여기서
    걸리게 한다.
    """
    assert feed.DATA_DIR.resolve() == build_data.DATA_DIR.resolve()
    assert len(sorted(feed.DATA_DIR.glob("*.yaml"))) == 8


# ---------------------------------------------------------------------------
# kind 와 basis 의 대응 — 분기 기준의 전제
# ---------------------------------------------------------------------------


def test_substitute_and_trigger_date_imply_each_other():
    """kind: substitute ⟺ basis.trigger_date 존재. 양방향 반례 0 건.

    _summary()/_description() 이 kind 로 갈래를 정하는 근거가 이 동치다.
    다만 코드는 이 동치에 기대지 않는다 — 이것은 관측이지 규약이 아니라서,
    깨지는 순간 여기서 먼저 걸려야 한다.
    """
    entries = _raw_entries()
    assert len(entries) == TOTAL

    substitute = {e["date"] for e in entries if e["kind"] == "substitute"}
    triggered = {e["date"] for e in entries if (e.get("basis") or {}).get("trigger_date")}

    assert sorted(substitute - triggered) == []
    assert sorted(triggered - substitute) == []
    assert len(substitute) == 14


# ---------------------------------------------------------------------------
# verified 는 나가지 않는다
# ---------------------------------------------------------------------------


def test_our_verification_state_never_reaches_the_feed(rendered, events):
    """verified 도 source_todo 도 SUMMARY·DESCRIPTION 어디에도 없다."""
    for token in ("verified", "source_todo", "未確認", "官報を"):
        assert token not in rendered

    entries = _raw_entries()
    todo = {e["source_todo"] for e in entries if e.get("source_todo")}
    assert todo, "source_todo 가 하나도 없다 — 대조 상대가 사라졌다"
    for text in todo:
        assert text not in rendered


def test_verified_and_unverified_entries_are_formatted_alike(events):
    """verified: false 인 항목의 출력 형식이 true 인 항목과 같다.

    같은 kind 안에서 형식이 갈리면 우리 내부 상태가 새어 나간 것이다.
    """
    by_day = {e.day: e for e in events}
    entries = {e["date"]: e for e in _raw_entries()}

    unverified = [d for d, e in entries.items() if not e["verified"]]
    assert len(unverified) == 24

    for day in unverified:
        event = by_day[day]
        # 미검증 3 종은 전부 statutory 다. statutory 의 형식은 하나뿐이다.
        assert entries[day]["kind"] == "statutory"
        assert event.summary == entries[day]["name"]
        assert event.description.startswith("근거: ")

    # 같은 이름의 검증된 항목과 나란히 놓아도 다르지 않다.
    verified_statutory = [
        by_day[d] for d, e in entries.items() if e["verified"] and e["kind"] == "statutory"
    ]
    shapes = {
        (e.summary.startswith("근거"), e.description.startswith("근거: "))
        for e in verified_statutory + [by_day[d] for d in unverified]
    }
    assert shapes == {(False, True)}


# ---------------------------------------------------------------------------
# 문자 — 눈으로 보면 구분되지 않는다
# ---------------------------------------------------------------------------


def test_the_summary_brackets_are_fullwidth_by_codepoint(events):
    """괄호가 U+FF08/U+FF09, 구분자가 U+30FB 다. 코드포인트로 검사한다.

    （ 와 ( , ・ 와 · 는 폰트에 따라 거의 같아 보인다. 문자를 눈으로 비교하면
    틀린 것을 통과시킨다.
    """
    bracketed = [e for e in events if "（" in e.summary]
    assert len(bracketed) == 15  # substitute 14 + bridge 1

    for event in bracketed:
        assert event.summary.endswith("）")
        assert "(" not in event.summary
        assert ")" not in event.summary
        assert "·" not in event.summary

    separated = [e for e in events if "・" in e.summary]
    assert [e.day for e in separated] == [dt.date(2026, 9, 22)]
    assert ord(feed._SEPARATOR) == 0x30FB
    assert (ord(feed._OPEN), ord(feed._CLOSE)) == (0xFF08, 0xFF09)


# ---------------------------------------------------------------------------
# UID
# ---------------------------------------------------------------------------


def test_every_uid_is_unique(rendered):
    # 줄 끝이 CRLF 라 $ 앞에 \r 이 남는다. 값만 본다.
    uids = [u.strip() for u in re.findall(r"^UID:(.+)$", rendered, re.MULTILINE)]
    assert len(uids) == TOTAL
    assert len(set(uids)) == TOTAL
    assert all(u.endswith("@holidays.lunalism.com") for u in uids)


def test_the_uid_token_is_the_one_in_the_data(events):
    """token 을 우리가 짓지 않는다. YAML 의 uid_token 을 그대로 쓴다."""
    entries = {e["date"]: e["uid_token"] for e in _raw_entries()}
    assert {e.day: e.token for e in events} == entries


# ---------------------------------------------------------------------------
# 알려진 항목 — 전문 고정
# ---------------------------------------------------------------------------

LAW = "「国民の祝日に関する法律」(昭和23年法律第178号)"

KNOWN = [
    (
        dt.date(2025, 1, 1),
        "元日",
        f"근거: {LAW} 第2条",
    ),
    (
        dt.date(2024, 2, 12),
        "休日（建国記念の日）",
        f"2024-02-11 建国記念の日(일요일)의 대체 휴일입니다. 근거: {LAW} 第3条第2項",
    ),
    (
        dt.date(2026, 9, 22),
        "休日（敬老の日・秋分の日）",
        "2026-09-21 敬老の日, 2026-09-23 秋分の日 사이의 휴일입니다. "
        f"근거: {LAW} 第3条第3項",
    ),
]


@pytest.mark.parametrize(
    ("day", "summary", "description"), KNOWN, ids=[str(k[0]) for k in KNOWN]
)
def test_known_entries_render_exactly(events, day, summary, description):
    (event,) = [e for e in events if e.day == day]
    assert event.summary == summary
    assert event.description == description
    assert "\n" not in event.description


@pytest.mark.parametrize(
    ("day", "summary", "description"), KNOWN, ids=[str(k[0]) for k in KNOWN]
)
def test_known_entries_survive_serialisation(rendered, day, summary, description):
    """Event 가 아니라 실제 .ics 본문에서 확인한다.

    폴딩과 이스케이프를 거친 뒤에도 같은 문자열인지가 구독자가 보는 것이다.
    """
    block = _blocks(rendered)[day]
    assert _text(block, "SUMMARY") == summary
    assert _text(block, "DESCRIPTION") == description


def test_the_description_is_always_one_line(events):
    assert [e for e in events if "\n" in e.description or "\r" in e.description] == []
    assert all(e.description for e in events)


# ---------------------------------------------------------------------------
# 조회 실패는 예외다
# ---------------------------------------------------------------------------


def test_a_missing_trigger_stops_the_build(monkeypatch):
    """괄호 안의 이름을 지어내지 않는다. 못 찾으면 멈춘다."""
    entry = {
        "_file": "2024.yaml",
        "date": dt.date(2024, 2, 12),
        "name": "休日",
        "uid_token": "kyujitsu",
        "kind": "substitute",
        "source": "…",
        "basis": {"trigger_date": dt.date(2024, 2, 11), "trigger_weekday": "日"},
    }
    with pytest.raises(ics.IcsError, match="항목이 없다"):
        feed._summary(entry, {})


def test_an_unknown_weekday_stops_the_build():
    """매핑 테이블에 없는 값은 조용히 통과하지 않는다."""
    entry = {
        "_file": "2024.yaml",
        "date": dt.date(2024, 2, 12),
        "name": "休日",
        "uid_token": "kyujitsu",
        "kind": "substitute",
        "source": "…",
        "basis": {"trigger_date": dt.date(2024, 2, 11), "trigger_weekday": "Sun"},
    }
    by_date = {dt.date(2024, 2, 11): {"name": "建国記念の日"}}
    with pytest.raises(ics.IcsError, match="trigger_weekday"):
        feed._description(entry, by_date)


# ---------------------------------------------------------------------------
# 발행
# ---------------------------------------------------------------------------


def test_publish_writes_and_replaces(tmp_path):
    """tmp_path 에서만 돈다. feeds/ 아래에 쓰지 않는다."""
    target = tmp_path / "jp.ics"

    first = feed.publish(dtstamp=DTSTAMP, path=target)
    assert first == target
    body = target.read_bytes()
    assert body.startswith(b"BEGIN:VCALENDAR")
    assert b"X-WR-CALNAME:\xec\x9d\xbc\xeb\xb3\xb8" in body  # 일본…

    # 두 번째는 자기 직전 판을 이전 발행본으로 읽는다. 내용이 같으니 바이트도 같다.
    feed.publish(dtstamp=DTSTAMP, path=target)
    assert target.read_bytes() == body
    assert list(tmp_path.iterdir()) == [target]  # 임시 파일이 남지 않았다

    assert ics.summarize_change(body, target.read_bytes()) == "내용 변경 없음"


def test_publish_does_not_touch_the_repo_feeds_dir():
    """기본 경로가 feeds/jp.ics 를 가리키되, 이 브랜치는 그 파일을 만들지 않는다."""
    assert feed.FEED_PATH.name == "jp.ics"
    assert not feed.FEED_PATH.exists()


# ---------------------------------------------------------------------------
# 헤더
# ---------------------------------------------------------------------------


def test_the_calendar_header_matches_the_decision(rendered):
    assert f"PRODID:{feed.PRODID}" in rendered
    assert f"X-WR-CALNAME:{feed.CALNAME}" in rendered
    assert f"X-WR-TIMEZONE:{feed.TZID}" in rendered

    # PRODID 가 kr 과 같은 값인 것은 의도한 것이다. feed.py 의 주석 참조.
    from rules.kr import feed as kr_feed

    assert feed.PRODID == kr_feed.PRODID


def test_the_build_is_deterministic():
    assert feed.build(dtstamp=DTSTAMP) == feed.build(dtstamp=DTSTAMP)
