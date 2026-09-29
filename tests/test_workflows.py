"""두 워크플로는 같은 러너 이미지에서 돈다.

ci.yml 의 초록이 발행의 관문이다 — 규칙·데이터를 바꾸는 PR 은 ci 가 초록일
때 머지되고, 머지된 것을 publish.yml 이 발행한다. 둘이 다른 이미지에서 돌면
ci 가 확인한 것(브라우저 스모크의 launch, uv 가 고르는 파이썬)이 발행 run 에서
성립한다는 보장이 없다. ci 가 초록인데 발행이 빨개지거나, 그 반대가 된다.
그래서 모든 job 의 runs-on 이 같은 값이어야 한다.

워크플로 YAML 을 그대로 읽는다. job 이 하나도 안 잡히면 "모두 같다" 는
빈 집합에서 참이 되므로, 워크플로마다 runs-on 을 가진 job 이 하나 이상인지
먼저 본다.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CI_YML = WORKFLOWS / "ci.yml"
PUBLISH_YML = WORKFLOWS / "publish.yml"


def _runs_on(path: Path) -> dict[str, str]:
    """job 이름 → runs-on. runs-on 이 없는 job(재사용 워크플로 호출 등)은 뺀다."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    jobs = doc.get("jobs") or {}
    return {name: job["runs-on"] for name, job in jobs.items() if "runs-on" in job}


def _all_runs_on() -> dict[str, str]:
    """'<파일>:<job>' → runs-on. 워크플로마다 하나 이상 있어야 한다."""
    found: dict[str, str] = {}
    for path in (CI_YML, PUBLISH_YML):
        per_file = _runs_on(path)
        assert per_file, f"{path.name} 에 runs-on 을 가진 job 이 없다"
        found.update({f"{path.name}:{job}": value for job, value in per_file.items()})
    return found


def test_every_job_in_both_workflows_uses_the_same_runner():
    found = _all_runs_on()
    assert len(set(found.values())) == 1, f"runs-on 이 job 마다 다르다: {found}"
