"""발행 파이프라인 — 키 만료 확인 / status.json / build.jsonl.

셋 다 CI 가 부르는 것들이다. 워크플로 YAML 은 테스트가 닿지 않으므로,
그 안에서 부르는 파이썬 쪽만이라도 여기서 잡아 둔다.

시계는 전부 인자로 넘긴다. core/ics.py 의 DTSTAMP 와 같은 이유다.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from core import buildlog, ics, secrets
from rules.kr import status
from sources.kr import kasi_parser, key_expiry

TODAY = dt.date(2026, 8, 10)
DTSTAMP = dt.datetime(2026, 8, 10, 0, 0, 0, tzinfo=dt.UTC)


# ---------------------------------------------------------------------------
# KASI 인증키 만료
# ---------------------------------------------------------------------------


def test_the_expiry_date_is_a_structured_field_not_prose():
    """만료일이 기계가 읽을 수 있는 값으로 있는지.

    전에는 kasi_names.yaml 의 open_questions 본문과 README 에 문장으로만
    있었다. 문장은 CI 가 읽지 못하므로 만료가 사람의 기억에 걸려 있었고,
    그 open_question 이 경계한 것이 정확히 그 상태다.
    """
    service = kasi_parser.load_service()
    assert service["operation"] == "getRestDeInfo"
    assert isinstance(service["expires_on"], dt.date)
    assert key_expiry.expires_on() == dt.date(2028, 8, 8)


def test_a_comfortable_margin_passes_and_returns_days_left():
    assert key_expiry.check(dt.date(2026, 8, 10)) == 729


@pytest.mark.parametrize(
    "today,left",
    [
        (dt.date(2028, 6, 10), 59),  # 경계 바로 안쪽
        (dt.date(2028, 8, 8), 0),  # 만료 당일
        (dt.date(2028, 9, 1), -24),  # 이미 지남
    ],
)
def test_a_short_margin_stops_the_build(today, left):
    """만료가 가까우면 발행하지 않고 멈춘다. 남은 일수를 메시지에 싣는다.

    만료 뒤에 실패하면 늦다. 그때는 이미 갱신이 끊긴 뒤이고, 이미 나가 있는
    .ics 는 그대로라 구독자 쪽에서는 아무 일도 없어 보인다.
    """
    with pytest.raises(key_expiry.KeyExpiring) as exc:
        key_expiry.check(today)

    message = str(exc.value)
    assert f"{left}일 남았다" in message
    assert "2028-08-08" in message
    assert "발행하지 않았다" in message


def test_the_boundary_is_exactly_min_days():
    """60 일 남은 날은 통과, 59 일은 멈춘다. 경계를 못 박는다."""
    assert key_expiry.check(dt.date(2028, 6, 9)) == 60
    with pytest.raises(key_expiry.KeyExpiring):
        key_expiry.check(dt.date(2028, 6, 10))


# ---------------------------------------------------------------------------
# status.json
# ---------------------------------------------------------------------------


def test_status_reports_what_the_repository_currently_claims():
    got = status.status(today=TODAY, dtstamp=DTSTAMP)

    assert got["generated_at"] == "2026-08-10T00:00:00+00:00"
    assert got["feed"]["range"] == {"start": "2020-01-01", "end": "2031-12-31"}
    assert got["feed"]["events"] > 0
    assert got["feed"]["provisional_events"] > 0
    assert got["coverage"]["confirmed_through"] == "2028-12-31"
    assert got["coverage"]["designated_last_synced_at"] == "2026-08-08"
    assert got["kasi_key"] == {
        "expires_on": "2028-08-08",
        "days_left": 729,
        "min_days": 60,
    }


def test_status_exposes_whether_the_uid_domain_is_confirmed():
    """확정 여부가 밖에서도 보여야 한다. 아직 발행 전이라는 사실의 근거다."""
    got = status.status(today=TODAY, dtstamp=DTSTAMP)
    assert got["uid"]["domain"] == ics.UID_DOMAIN
    assert got["uid"]["confirmed"] is ics.UID_DOMAIN_CONFIRMED


def test_status_renders_stable_json():
    """같은 입력이면 같은 문자열. generated_at 만 실행마다 달라져야 한다."""
    once = status.render(today=TODAY, dtstamp=DTSTAMP)
    twice = status.render(today=TODAY, dtstamp=DTSTAMP)
    assert once == twice
    assert once.endswith("\n")
    assert json.loads(once)["generated_at"] == "2026-08-10T00:00:00+00:00"

    later = status.render(today=TODAY, dtstamp=dt.datetime(2026, 9, 1, tzinfo=dt.UTC))
    assert later != once, "generated_at 이 반영되지 않았다"


# ---------------------------------------------------------------------------
# logs/build.jsonl
# ---------------------------------------------------------------------------


def test_append_writes_one_line_per_record(tmp_path):
    target = tmp_path / "logs" / "build.jsonl"
    buildlog.append(target, {"result": "success", "at": "1"})
    buildlog.append(target, {"result": "failed", "at": "2"})

    lines = target.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["at"] == "1"
    assert json.loads(lines[1])["result"] == "failed"


def test_a_success_record_carries_no_error_field():
    record = buildlog.record_from_env(
        {"BUILD_RESULT": "success", "BUILD_AT": "2026-08-10T00:00:00Z", "GITHUB_RUN_ID": "7"}
    )
    assert record["result"] == "success"
    assert record["run_id"] == "7"
    assert "error" not in record


def test_a_failure_record_carries_the_tail_of_the_build_log(tmp_path):
    """실패는 원인과 함께 남아야 한다.

    이 파이프라인의 실패는 조용하다. 이미 나가 있는 .ics 가 그대로 남아서
    구독자 쪽에서는 아무 일도 없어 보인다. 무엇이 언제부터 안 되는지는 이
    파일로만 읽을 수 있다.
    """
    log = tmp_path / "build.log"
    log.write_text("앞부분\nKeyExpiring: 만료까지 3일 남았다\n", encoding="utf-8")

    record = buildlog.record_from_env(
        {"BUILD_RESULT": "failure", "BUILD_LOG_PATH": str(log), "BUILD_AT": "t"}
    )
    assert record["result"] == "failed"
    assert record["job_status"] == "failure"
    assert "만료까지 3일 남았다" in record["error"]


def test_a_failure_without_a_log_still_records_something():
    record = buildlog.record_from_env({"BUILD_RESULT": "failure"})
    assert record["error"] == "원인 미상"


def test_the_error_field_is_truncated(tmp_path):
    """스택 전체를 넣으면 한 줄이 수천 자가 되어 파일을 읽을 수 없다."""
    log = tmp_path / "build.log"
    log.write_text("x" * 5000, encoding="utf-8")
    record = buildlog.record_from_env({"BUILD_RESULT": "failure", "BUILD_LOG_PATH": str(log)})
    assert len(record["error"]) == buildlog.MAX_ERROR_CHARS


def test_consecutive_failures_counts_back_to_the_last_success(tmp_path):
    """마지막 성공 이후의 실패만 센다. 2 회 이상이면 워크플로가 이슈를 연다."""
    target = tmp_path / "build.jsonl"
    for result in ("failed", "success", "failed", "failed"):
        buildlog.append(target, {"result": result})

    assert buildlog.consecutive_failures(target) == 2


def test_consecutive_failures_is_zero_when_the_last_run_succeeded(tmp_path):
    target = tmp_path / "build.jsonl"
    buildlog.append(target, {"result": "failed"})
    buildlog.append(target, {"result": "success"})
    assert buildlog.consecutive_failures(target) == 0


def test_consecutive_failures_on_a_missing_file_is_zero(tmp_path):
    assert buildlog.consecutive_failures(tmp_path / "없다.jsonl") == 0


def test_a_broken_line_does_not_hide_the_rest(tmp_path):
    """깨진 줄 하나 때문에 기록 전체를 못 읽으면 안 된다."""
    target = tmp_path / "build.jsonl"
    buildlog.append(target, {"result": "failed"})
    with target.open("a", encoding="utf-8") as fp:
        fp.write("{깨진 줄\n")
    buildlog.append(target, {"result": "failed"})

    assert len(buildlog.read(target)) == 2
    assert buildlog.consecutive_failures(target) == 2


# ---------------------------------------------------------------------------
# 커밋 메시지에 쓰는 변경 요약
# ---------------------------------------------------------------------------


def test_summarize_change_reports_nothing_when_only_dtstamp_differs():
    """DTSTAMP 만 다른 재발행은 "변경 없음"이다. 워크플로가 이걸로 원복을 정한다."""
    from rules.kr import feed

    same = feed.build(today=TODAY, dtstamp=DTSTAMP)
    later = feed.build(today=TODAY, dtstamp=dt.datetime(2026, 9, 1, tzinfo=dt.UTC))

    assert same != later  # DTSTAMP 는 다르다
    assert ics.summarize_change(same, later) == "내용 변경 없음"


def test_summarize_change_counts_added_years():
    from rules.kr import feed

    before = feed.build(today=TODAY, dtstamp=DTSTAMP)
    after = feed.build(today=dt.date(2027, 8, 10), dtstamp=DTSTAMP, previous=before)

    summary = ics.summarize_change(before, after)
    assert summary.startswith("추가 ")
    assert "2032" in summary


# ---------------------------------------------------------------------------
# build.jsonl 의 error 는 공개된다고 보고 쓴다
#
# 이 파일은 저장소에 커밋되고 Pages 를 붙이면 공개 URL 로 서빙된다.
# error 에는 빌드 로그 끝부분이 실리므로 무엇이 들어올지 알 수 없다.
# ---------------------------------------------------------------------------

# 진짜처럼 생긴 가짜 키. 실제 키는 테스트에 절대 들이지 않는다.
FAKE_KEY = "aB3%2FxQ9zK1pL7mN4vR8t%2BwY6uE0sD5fG2hJ"


def _record(log_text, env_extra=None, tmp_path=None):
    log = tmp_path / "build.log"
    log.write_text(log_text, encoding="utf-8")
    env = {"BUILD_RESULT": "failure", "BUILD_LOG_PATH": str(log)}
    env.update(env_extra or {})
    return buildlog.record_from_env(env)


def test_a_key_in_the_build_log_is_masked_in_the_record(tmp_path):
    """빌드 로그에 키가 섞여 들어와도 기록에는 마스킹돼 남는다."""
    leaked = f"KasiError: HTTPStatusError 403 for url ...?serviceKey={FAKE_KEY}&solYear=2026"
    record = _record(leaked, {"KASI_SERVICE_KEY": FAKE_KEY}, tmp_path)

    assert FAKE_KEY not in record["error"]
    assert "aB3%...G2hJ" in record["error"]
    # 무엇이 실패했는지는 남아야 한다. 통째로 지우는 것이 목적이 아니다.
    assert "403" in record["error"]
    assert "solYear=2026" in record["error"]


@pytest.mark.parametrize(
    "form",
    [
        "raw",  # 원본 그대로
        "once",  # 한 번 인코딩
        "twice",  # 이중 인코딩 — 라이브러리가 인코딩 키를 또 인코딩한 형태
        "decoded",  # 디코딩된 형태
    ],
)
def test_every_encoding_of_the_key_is_masked(form, tmp_path):
    """키가 어떤 형태로 나타나든 지워지는지.

    이중 인코딩이 특히 중요하다. params 모드의 403 메시지에 '%2B' 가
    '%252B' 로 바뀐 형태로 키가 통째로 들어 있던 것이 실제로 관측됐다
    (sources/kr/kasi_client.py 의 key_forms 주석).
    """
    from urllib.parse import quote, unquote

    variants = {
        "raw": FAKE_KEY,
        "once": quote(FAKE_KEY, safe=""),
        "twice": quote(quote(FAKE_KEY, safe=""), safe=""),
        "decoded": unquote(FAKE_KEY),
    }
    appearing = variants[form]

    record = _record(f"오류: {appearing} 끝", {"KASI_SERVICE_KEY": FAKE_KEY}, tmp_path)
    assert appearing not in record["error"], f"{form} 형태가 남았다"


def test_a_secret_is_found_by_the_name_of_its_env_var(tmp_path):
    """환경변수 이름으로 비밀값을 찾는지. 목록을 따로 관리하지 않는다.

    목록 방식이면 새 비밀값을 스텝에 추가하면서 갱신을 잊고, 잊었다는 사실은
    유출된 뒤에야 드러난다.
    """
    for name in ("SOME_API_KEY", "MY_TOKEN", "X_SECRET", "DB_PASSWORD", "A_CREDENTIAL"):
        value = f"{name.lower()}-abcdefghijklmnop"
        record = _record(f"터졌다: {value}", {name: value}, tmp_path)
        assert value not in record["error"], name


def test_a_value_that_is_not_secret_shaped_is_left_alone(tmp_path):
    """이름에 힌트가 없으면 지우지 않는다. 오류 메시지가 읽혀야 한다."""
    record = _record("경로: /home/runner/work/holidays", {"HOME": "/home/runner"}, tmp_path)
    assert "/home/runner/work/holidays" in record["error"]


def test_a_short_value_is_left_alone_even_with_a_secret_name(tmp_path):
    """짧은 값은 이름이 걸려도 지우지 않는다.

    'true' 나 '1' 같은 값까지 마스킹하면 오류 메시지가 읽히지 않게 된다.
    """
    record = _record("설정: DEBUG_TOKEN=1 이라서 실패", {"DEBUG_TOKEN": "1"}, tmp_path)
    assert "DEBUG_TOKEN=1" in record["error"]


def test_the_github_token_is_masked_too(tmp_path):
    """GITHUB_TOKEN 도 이름 규칙에 걸린다. 별도로 적어 두지 않아도 걸러진다."""
    token = "ghs_" + "x" * 36
    record = _record(f"remote: {token} rejected", {"GITHUB_TOKEN": token}, tmp_path)
    assert token not in record["error"]


def test_a_success_record_has_no_error_to_scrub():
    """성공에는 error 자체가 없다. 스크럽할 것도 없다."""
    record = buildlog.record_from_env({"BUILD_RESULT": "success", "KASI_SERVICE_KEY": FAKE_KEY})
    assert "error" not in record
    assert FAKE_KEY not in json.dumps(record, ensure_ascii=False)


def test_scrub_moved_to_core_but_the_kasi_names_still_work():
    """kasi_client 의 이름들이 그대로 도는지. AGENTS.md 와 호출부가 가리킨다."""
    from sources.kr import kasi_client as kc

    assert kc.scrub(f"url?serviceKey={FAKE_KEY}", FAKE_KEY) == (
        f"url?serviceKey={secrets.mask(FAKE_KEY)}"
    )
    assert kc.mask(FAKE_KEY) == secrets.mask(FAKE_KEY) == f"aB3%...G2hJ({len(FAKE_KEY)}자)"
    assert kc.key_forms(FAKE_KEY) == secrets.forms(FAKE_KEY)
