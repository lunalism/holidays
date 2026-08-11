"""일본 소스 — 内閣府 CSV 의 파싱·캐시 가드·data/jp 생성.

네트워크를 타지 않는다. 캐시된 원본 바이트(sources/jp/cache/syukujitsu.csv)를
읽어 검사하고, 수집 경로는 가짜 클라이언트로 돌린다. 진짜 요청을 넣으면
테스트가 정부 사이트의 가동 여부에 매이고, 실패했을 때 그것이 우리 버그인지
저쪽 사정인지 구분되지 않는다.
"""

from __future__ import annotations

import datetime as dt

import pytest
import yaml

from sources.jp import build_data, cao_client, cao_parser

RAW = cao_client.CACHE_PATH.read_bytes()


class FakeResponse:
    def __init__(self, status_code, content=b"", headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}


class FakeClient:
    """마지막 요청 헤더를 들고 있는 가짜 httpx.Client."""

    def __init__(self, response):
        self.response = response
        self.headers = None

    def get(self, url, headers=None):
        self.headers = headers or {}
        return self.response

    def close(self):
        pass


# ---------------------------------------------------------------------------
# 파싱 — 원본이 우리가 아는 그 파일인가
# ---------------------------------------------------------------------------


def test_the_cache_is_cp932_not_utf8():
    """인코딩을 실제 바이트로 확인한다. Content-Type 에 charset 이 없다."""
    with pytest.raises(UnicodeDecodeError):
        RAW.decode("utf-8")
    assert cao_parser.decode(RAW).startswith("国民の祝日・休日月日")


def test_a_utf8_bom_is_rejected():
    """인코딩이 바뀌면 조용히 넘어가지 않는다."""
    with pytest.raises(cao_parser.CaoParseError, match="BOM"):
        cao_parser.decode(b"\xef\xbb\xbf" + RAW)


def test_the_header_must_match_exactly():
    """컬럼 표기가 바뀌면 의미도 바뀌었을 수 있다."""
    broken = RAW.replace("国民の祝日・休日名称".encode("cp932"), "名前".encode("cp932"), 1)
    with pytest.raises(cao_parser.CaoParseError, match="헤더가 예상과 다르다"):
        cao_parser.parse(broken)


def test_the_table_is_sorted_and_unique():
    rows = cao_parser.check(RAW)
    days = [r.day for r in rows]
    assert days == sorted(days)
    assert len(days) == len(set(days))
    assert rows[0].day == dt.date(1955, 1, 1)


def test_dates_have_no_zero_padding():
    """YYYY/M/D 다. strptime 을 쓰면 1955/1/1 에서 깨진다."""
    assert "1955/1/1," in cao_parser.decode(RAW)
    assert "1955/01/01," not in cao_parser.decode(RAW)


# ---------------------------------------------------------------------------
# 캐시 — 줄어드는 응답이 관측 기록을 덮지 못하게
# ---------------------------------------------------------------------------


def test_a_shorter_response_does_not_overwrite_the_cache(monkeypatch, tmp_path):
    """행이 줄어든 응답을 거부하는지.

    이 표는 1955 년부터 전부 들고 있고 과거는 확정된 사실이라 줄어들 이유가
    없다. 줄어든 응답을 그대로 쓰면 관측 기록이 사라지고, 되돌리려면 git 을
    뒤지는 수밖에 없다.
    """
    cache = tmp_path / "syukujitsu.csv"
    cache.write_bytes(RAW)
    monkeypatch.setattr(cao_client, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cao_client, "CACHE_PATH", cache)
    monkeypatch.setattr(cao_client, "META_PATH", tmp_path / "meta.json")

    text = cao_parser.decode(RAW)
    head, body = text.split("\r\n", 1)
    shorter = (head + "\r\n" + "\r\n".join(body.splitlines()[:100]) + "\r\n").encode("cp932")

    with pytest.raises(cao_client.CacheWouldLoseData, match="줄어들"):
        cao_client.fetch(client=FakeClient(FakeResponse(200, shorter)))

    assert cache.read_bytes() == RAW, "거부했는데 캐시가 바뀌었다"


def test_a_broken_response_does_not_overwrite_the_cache(monkeypatch, tmp_path):
    """오류 페이지가 정상 캐시로 굳지 않는지."""
    cache = tmp_path / "syukujitsu.csv"
    cache.write_bytes(RAW)
    monkeypatch.setattr(cao_client, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cao_client, "CACHE_PATH", cache)
    monkeypatch.setattr(cao_client, "META_PATH", tmp_path / "meta.json")

    with pytest.raises(cao_client.CaoError, match="정상 CSV 가 아니다"):
        cao_client.fetch(client=FakeClient(FakeResponse(200, b"<html>error</html>")))

    assert cache.read_bytes() == RAW


def test_the_cache_keeps_the_original_bytes(monkeypatch, tmp_path):
    """디코드한 텍스트가 아니라 받은 바이트 그대로 저장하는지."""
    cache = tmp_path / "syukujitsu.csv"
    monkeypatch.setattr(cao_client, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cao_client, "CACHE_PATH", cache)
    monkeypatch.setattr(cao_client, "META_PATH", tmp_path / "meta.json")

    headers = {"etag": '"abc"', "last-modified": "Mon, 02 Feb 2026 00:30:17 GMT"}
    cao_client.fetch(client=FakeClient(FakeResponse(200, RAW, headers)))

    assert cache.read_bytes() == RAW
    assert cache.read_bytes()[:4] == b"\x8d\x91\x96\xaf"  # CP932 「国民」


def test_a_conditional_request_carries_both_validators(monkeypatch, tmp_path):
    """캐시가 있으면 검증자를 실어 보내는지. no-store 라 우리가 들고 있어야 한다."""
    cache = tmp_path / "syukujitsu.csv"
    cache.write_bytes(RAW)
    meta = tmp_path / "meta.json"
    meta.write_text('{"etag": "\\"tag\\"", "last_modified": "Mon, 02 Feb 2026 00:30:17 GMT"}')
    monkeypatch.setattr(cao_client, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cao_client, "CACHE_PATH", cache)
    monkeypatch.setattr(cao_client, "META_PATH", meta)

    client = FakeClient(FakeResponse(304))
    assert cao_client.fetch(client=client) == RAW
    assert client.headers["If-None-Match"] == '"tag"'
    assert client.headers["If-Modified-Since"] == "Mon, 02 Feb 2026 00:30:17 GMT"


# ---------------------------------------------------------------------------
# data/jp — 범위와 판정
# ---------------------------------------------------------------------------


def test_only_the_publish_range_is_written():
    built = build_data.build(RAW)
    days = [e["date"] for entries in built.values() for e in entries]
    assert min(days) >= build_data.RANGE_START
    assert max(days) <= build_data.RANGE_END
    assert sorted(built) == list(range(2020, 2028))


def test_the_files_on_disk_match_a_fresh_build():
    """커밋된 data/jp 가 지금 캐시에서 다시 만든 것과 같은지.

    시계를 읽지 않으므로 같은 캐시면 같은 바이트가 나와야 한다. 어긋나면
    누가 손으로 고쳤거나 캐시가 바뀐 채 다시 만들지 않은 것이다.
    """
    meta = cao_client._read_meta()
    for year, entries in build_data.build(RAW).items():
        path = build_data.DATA_DIR / f"{year}.yaml"
        assert path.read_text(encoding="utf-8") == build_data._dump(year, entries, meta)


def test_kyujitsu_is_classified_by_rule_with_its_basis_recorded():
    """休日 이 어느 조문으로 판정됐는지 근거가 남는지."""
    entries = {e["date"]: e for es in build_data.build(RAW).values() for e in es}

    sub = entries[dt.date(2025, 5, 6)]
    assert sub["kind"] == build_data.KIND_SUBSTITUTE
    assert sub["basis"]["rule"] == "第3条第2項"
    # 연휴가 겹쳐 원인일과 휴일이 이틀 떨어진 자리다. "다음날"이 아니다.
    assert sub["basis"]["trigger_date"] == dt.date(2025, 5, 4)

    bridge = entries[dt.date(2026, 9, 22)]
    assert bridge["kind"] == build_data.KIND_BRIDGE
    assert bridge["basis"]["rule"] == "第3条第3項"
    assert bridge["basis"]["prev_date"] == dt.date(2026, 9, 21)
    assert bridge["basis"]["next_date"] == dt.date(2026, 9, 23)


def test_the_uid_token_does_not_encode_our_classification():
    """振替 든 国民の休日 이든 token 이 같아야 한다.

    두 규칙이 같은 날짜를 내는 해가 있어(1987-05-04) 재분류가 실제로 일어날 수
    있다. token 에 kind 가 들어 있으면 그 정정이 곧 UID 변경이 된다.
    """
    entries = [e for es in build_data.build(RAW).values() for e in es]
    kyujitsu = [e for e in entries if e["name"] == cao_parser.NAME_KYUJITSU]
    # 두 kind 가 다 나와야 이 테스트가 의미를 갖는다.
    assert {e["kind"] for e in kyujitsu} == {"substitute", "bridge"}
    assert {e["uid_token"] for e in kyujitsu} == {"kyujitsu"}

    for entry in entries:
        assert entry["kind"] not in entry["uid_token"]


def test_renamed_holidays_keep_one_token():
    """体育の日 → スポーツの日 는 개칭이지 새 축일이 아니다."""
    assert build_data.UID_TOKENS["体育の日"] == build_data.UID_TOKENS["スポーツの日"]


def test_an_ambiguous_kyujitsu_stops_the_build():
    """두 조문으로 다 설명되는 날은 코드가 고르지 않는다.

    1987-05-04 이 그 경우다. 지금 발행 범위 밖이라 산출물에는 없지만, 범위를
    넓히면 걸린다. 그때 임의로 하나를 고르면 근거 필드가 거짓을 말한다.
    """
    statutory = {r.day for r in cao_parser.check(RAW) if r.name != cao_parser.NAME_KYUJITSU}
    with pytest.raises(build_data.BuildError, match="둘 다로 설명된다"):
        build_data._classify(dt.date(1987, 5, 4), statutory)


def test_an_unknown_name_stops_the_build():
    """새 축일이 생기면 멈춘다. 개칭인지 신설인지는 사람이 정한다."""
    row = cao_parser.Row(day=dt.date(2027, 1, 1), name="新しい祝日")
    with pytest.raises(build_data.BuildError, match="모르는 名称"):
        build_data._entry(row, set())


# ---------------------------------------------------------------------------
# 올림픽 이동 — 조문 대조
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("day", "name", "article"),
    [
        (dt.date(2020, 7, 23), "海の日", "第32条第1項"),
        (dt.date(2020, 8, 10), "山の日", "第32条第1項"),
        (dt.date(2020, 7, 24), "スポーツの日", "第32条第1項"),
        (dt.date(2021, 7, 22), "海の日", "第32条第2項"),
        (dt.date(2021, 8, 8), "山の日", "第32条第2項"),
        (dt.date(2021, 7, 23), "スポーツの日", "第32条第2項"),
    ],
)
def test_the_olympic_moves_cite_the_article(day, name, article):
    """2020·2021 이동분이 특별조치법 조문을 근거로 달고 있는지."""
    entries = {(e["date"], e["name"]): e for es in build_data.build(RAW).values() for e in es}
    entry = entries[(day, name)]
    assert entry["verified"] is True
    assert article in entry["source"]
    assert "特別措置法" in entry["source"]


def test_a_move_that_disagrees_with_the_article_stops_the_build():
    """조문과 원본이 어긋나면 멈춘다. 조문을 원본에 맞춰 고치지 않는다."""
    row = cao_parser.Row(day=dt.date(2020, 7, 20), name="海の日")
    with pytest.raises(build_data.BuildError, match="어긋난다"):
        build_data._entry(row, set())


# ---------------------------------------------------------------------------
# verified — 확인하지 않은 것을 확인했다고 적지 않는다
# ---------------------------------------------------------------------------


def test_the_equinoxes_are_not_claimed_as_verified():
    """제2조는 「春分日」이라고만 한다. 날짜는 관보 고시이고 우리는 안 봤다."""
    for entries in build_data.build(RAW).values():
        for entry in entries:
            if entry["name"] in ("春分の日", "秋分の日"):
                assert entry["verified"] is False
                assert "官報" in entry["source_todo"]


def test_national_foundation_day_is_not_claimed_as_verified():
    """제2조가 「政令で定める日」이고 그 정령을 확인하지 않았다."""
    entries = [e for es in build_data.build(RAW).values() for e in es]
    founding = [e for e in entries if e["name"] == "建国記念の日"]
    assert founding
    assert all(e["verified"] is False for e in founding)
    assert all("政令" in e["source_todo"] for e in founding)


def test_every_entry_carries_a_source():
    for entries in build_data.build(RAW).values():
        for entry in entries:
            assert entry["source"].strip(), entry


def test_the_written_yaml_parses():
    for path in sorted(build_data.DATA_DIR.glob("*.yaml")):
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert loaded["country"] == "jp"
        assert loaded["holidays"]
        for entry in loaded["holidays"]:
            assert isinstance(entry["date"], dt.date)
            assert entry["kind"] in ("statutory", "substitute", "bridge")
