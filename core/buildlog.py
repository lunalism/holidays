"""발행 기록. logs/build.jsonl 에 한 줄씩 쌓는다.

--------------------------------------------------------------------------
왜 성공만이 아니라 실패도 적는가
--------------------------------------------------------------------------
이 파이프라인의 실패는 조용하다. 발행이 실패해도 이미 나가 있는 .ics 는
그대로 남아서, 구독자 쪽에서는 아무 일도 없어 보인다. 갱신이 언제 끊겼는지는
저장소를 봐야 알 수 있고, 성공만 적으면 "마지막 성공" 이후에 무슨 일이
있었는지가 남지 않는다.

그래서 실패도 같은 줄로 적는다. 무엇이 언제부터 안 되는지를 이 파일 하나로
읽을 수 있어야 한다.

--------------------------------------------------------------------------
JSONL 인 이유
--------------------------------------------------------------------------
append 만 하면 되고 병합 충돌이 줄 단위로 끝난다. 하나의 JSON 배열로 두면
매번 전체를 다시 써야 하고, 두 실행이 겹치면 파일이 통째로 깨진다.

기록은 지우지 않는다. 커지면 연 단위로 잘라 보관할 것 — 지금 규모로는
주 1 회 한 줄이라 문제가 되지 않는다.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# 실패 시 로그에 남길 오류 문자열의 최대 길이. 스택 전체를 넣으면 한 줄이
# 수천 자가 되어 파일을 사람이 읽을 수 없게 된다. 원문은 Actions 로그에 있다.
MAX_ERROR_CHARS = 2000


def append(path: Path, record: dict) -> Path:
    """레코드 한 줄 추가. 디렉터리가 없으면 만든다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    with path.open("a", encoding="utf-8") as fp:
        fp.write(line + "\n")
    return path


def tail_error(log_path: Path, limit: int = MAX_ERROR_CHARS) -> str:
    """빌드 로그 끝부분. 실패 원인을 한 줄에 담기 위한 것이다."""
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""
    return text[-limit:]


def record_from_env(env: dict = None) -> dict:
    """환경변수 → 레코드.

    GitHub Actions 에서 값을 넘기는 자연스러운 통로가 환경변수라 그것에 맞춘다.
    result 는 job.status 를 그대로 받는다(success / failure / cancelled).
    """
    env = os.environ if env is None else env

    result = (env.get("BUILD_RESULT") or "unknown").strip()
    record = {
        "at": (env.get("BUILD_AT") or "").strip(),
        "result": "success" if result == "success" else "failed",
        "job_status": result,
        "run_id": (env.get("GITHUB_RUN_ID") or "").strip(),
        "sha": (env.get("GITHUB_SHA") or "").strip(),
        "trigger": (env.get("GITHUB_EVENT_NAME") or "").strip(),
    }

    if record["result"] != "success":
        log_path = (env.get("BUILD_LOG_PATH") or "").strip()
        error = tail_error(Path(log_path)) if log_path else ""
        record["error"] = error or (env.get("BUILD_ERROR") or "").strip() or "원인 미상"
    return record


def read(path: Path) -> list:
    """기록 전체. 읽지 못하는 줄은 건너뛴다.

    깨진 줄 하나 때문에 기록 전체를 못 읽으면 안 된다. 이 파일은 판단의
    근거가 아니라 관측 기록이고, 남은 줄만으로도 쓸모가 있다.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def consecutive_failures(path: Path) -> int:
    """마지막부터 세어 연속 실패 횟수. 성공을 만나면 멈춘다."""
    count = 0
    for record in reversed(read(path)):
        if record.get("result") == "success":
            break
        count += 1
    return count


if __name__ == "__main__":  # pragma: no cover
    import sys

    target = Path(os.environ.get("BUILD_LOG_JSONL") or "logs/build.jsonl")

    if "--consecutive-failures" in sys.argv:
        print(consecutive_failures(target))
    else:
        print(f"[buildlog] {append(target, record_from_env())}")
