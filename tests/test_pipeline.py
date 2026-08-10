"""발행 파이프라인 — 키 만료 확인 / status.json / build.jsonl.

셋 다 CI 가 부르는 것들이다. 워크플로 YAML 은 테스트가 닿지 않으므로,
그 안에서 부르는 파이썬 쪽만이라도 여기서 잡아 둔다.

시계는 전부 인자로 넘긴다. core/ics.py 의 DTSTAMP 와 같은 이유다.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from core import buildlog, ics
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
