"""규칙 테이블을 일부러 망가뜨렸을 때 테스트가 실제로 잡아내는지 확인한다.

test_substitute_rules.py 가 "표가 맞는가"를 본다면, 이 파일은 "그 테스트가
틀린 표를 알아채기는 하는가"를 본다. 통과하는 테스트는 아무것도 증명하지 않는다.
잡아내지 못하는 변이가 있다면 그건 픽스처의 구멍이고, 여기서 드러나야 한다.

변이는 문자열 치환이 아니라 파싱된 구조를 고쳐 다시 쓴다. YAML 들여쓰기에
의존하지 않으므로 표를 정리해도 깨지지 않는다.

탐지 결과는 세 가지로 구분한다.

    로드 거부   : 로더의 구조 검증에 걸려 표가 아예 안 읽힌다 (RuleTableError).
                  잘못된 표가 배포에 도달하지 못한다는 뜻이다.
    결과 불일치 : 표는 읽히지만 유도 결과가 정답 픽스처와 어긋나 테스트가 깨진다.
    미탐지      : 아무 일도 일어나지 않는다. 픽스처에 구멍이 있다는 뜻이다.

미탐지가 예상되는 변이는 xfail 로 둔다. 나중에 그 구멍이 메워지면 xpass 로
바뀌면서 여기를 갱신하라고 알려준다.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
TABLE_PATH = REPO_ROOT / "rules" / "kr" / "substitute_holidays.yaml"
TARGET = "tests/test_substitute_rules.py"

REJECTED = "로드 거부"
MISMATCH = "결과 불일치"
UNDETECTED = "미탐지"


# ---------------------------------------------------------------------------
# 변이들
# ---------------------------------------------------------------------------


def _no_change(data):
    """대조군. 변이 없이 돌려서 러너 자체가 멀쩡한지 확인한다."""


def _add_saturday_to_sunday_only_clause(data):
    """제1항제2호에 토요일을 넣는다. 설·추석 비대칭이 무너진다."""
    for rs in data["rulesets"]:
        for c in rs["clauses"]:
            if c["overlaps"] == ["sunday"]:
                c["overlaps"].append("saturday")


def _add_saturday_to_weekly_holidays(data):
    """토요일을 공휴일로 만든다. 유도 전체의 전제가 무너진다."""
    data["weekly_holidays"].append("saturday")


def _effective_from_as_year(data):
    """연중 개정을 연 단위로 되돌린다. 2021년 답을 표현할 수 없게 된다."""
    for rs in data["rulesets"]:
        if rs["id"] == "제31930호":
            rs["effective_from"] = 2021


def _typo_in_applies_to(data):
    """레지스트리에 없는 키를 넣는다. 조용히 적용 대상에서 빠지는 사고.

    applies_to 가 없는 호(제36290호처럼 제2조 호 번호로만 규정된 것)는 건너뛴다.
    """
    for rs in data["rulesets"]:
        for c in rs["clauses"]:
            if "applies_to" not in c:
                continue
            c["applies_to"] = ["chusoek" if h == "chuseok" else h for h in c["applies_to"]]


def _reverse_ruleset_order(data):
    """시간 순서를 뒤집는다. ruleset_on 이 엉뚱한 규칙을 고르게 된다."""
    data["rulesets"].reverse()


def _delete_clause_3(data):
    """제1항제3호를 지운다. 공휴일끼리 겹치는 경로가 통째로 사라진다."""
    for rs in data["rulesets"]:
        rs["clauses"] = [c for c in rs["clauses"] if c["overlaps"] != ["other_holiday_on_weekday"]]


def _invent_the_article2_mapping(data):
    """미확인 매핑을 지어내서 채운다.

    제36290호의 각 호는 적용 대상이 제2조 호 번호로만 규정되어 있고 그 배열이
    미확인이라 applies_to 가 비어 있다. 그럴듯한 값을 넣으면 2026-05-11 이후가
    갑자기 답을 내기 시작한다. 그 답이 맞는지는 아무도 모른다.
    이 변이는 "모르는 것을 채워 넣으면 테스트가 알아채는가"를 본다.
    """
    for rs in data["rulesets"]:
        if rs["id"] != "제36290호":
            continue
        for c in rs["clauses"]:
            if "applies_to" in c:
                continue
            c["applies_to"] = ["seollal", "chuseok"] if c["overlaps"] == ["sunday"] else [
                "samiljeol", "childrens_day", "gwangbokjeol", "gaecheonjeol",
                "hangeul_day", "buddhas_birthday", "christmas", "constitution_day",
            ]


def _delete_placement_paragraph_3(data):
    """제3항(대체공휴일이 토요일이면 재배치)을 지운다."""
    data["placement_rules"] = [p for p in data["placement_rules"] if p["id"] != "제3조제3항"]


MUTATIONS = [
    pytest.param(
        ("대조군-변이없음", _no_change, UNDETECTED),
        id="대조군-변이없음",
    ),
    pytest.param(
        ("1항2호에-토요일-추가", _add_saturday_to_sunday_only_clause, MISMATCH),
        id="1항2호에-토요일-추가",
    ),
    pytest.param(
        ("weekly_holidays에-토요일-추가", _add_saturday_to_weekly_holidays, REJECTED),
        id="weekly_holidays에-토요일-추가",
    ),
    pytest.param(
        ("effective_from을-연도로", _effective_from_as_year, REJECTED),
        id="effective_from을-연도로",
    ),
    pytest.param(
        ("applies_to-키-오타", _typo_in_applies_to, REJECTED),
        id="applies_to-키-오타",
    ),
    pytest.param(
        ("ruleset-순서-뒤집기", _reverse_ruleset_order, REJECTED),
        id="ruleset-순서-뒤집기",
    ),
    # 한때 미탐지였다. 2025-05-05 겹침 케이스와 3호 경로 테스트를 넣어 메웠다.
    # 3호는 토·일 판정에 기여하지 않으므로 eligibility 결과로는 존재가 드러나지 않는다.
    # test_substitute_rules.py 의 test_clause_3_covers_* 가 경로 자체를 본다.
    pytest.param(
        ("1항3호-삭제", _delete_clause_3, MISMATCH),
        id="1항3호-삭제",
    ),
    # 지어낸 매핑은 test_constitution_day_enforcement_boundary 가 잡는다.
    # 그 테스트가 2026-05-11 에서 MappingUnresolved 를 요구하기 때문이다.
    # 정답 픽스처는 그 구간의 답을 모르므로 여기서는 도움이 되지 않는다.
    # "모른다"를 테스트로 고정해 두지 않았다면 이 변이는 조용히 통과했을 것이다.
    pytest.param(
        ("제2조-매핑-지어내기", _invent_the_article2_mapping, MISMATCH),
        id="제2조-매핑-지어내기",
    ),
    pytest.param(
        ("3항-토요일-재배치-삭제", _delete_placement_paragraph_3, MISMATCH),
        id="3항-토요일-재배치-삭제",
        marks=pytest.mark.xfail(
            reason=(
                "픽스처 구멍: 배치 규칙을 쓰는 코드가 아직 없다. 로더는 placement_rules 를 "
                "읽어 두기만 하고 계산하지 않으므로 지워도 결과가 변하지 않는다. "
                "검증 케이스는 배치 계산 구현 후 스캔으로 뽑아 원문 확인을 거쳐 넣는다. "
                "open_questions 의 픽스처구멍-배치규칙-미검증 참조."
            ),
            strict=True,
        ),
    ),
]


# ---------------------------------------------------------------------------
# 러너
# ---------------------------------------------------------------------------


def _mutate_to(mutate, dest: Path) -> None:
    data = yaml.safe_load(TABLE_PATH.read_text(encoding="utf-8"))
    mutate(data)
    dest.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def _classify(mutant: Path) -> tuple:
    env = dict(os.environ, KR_RULE_TABLE=str(mutant))
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", TARGET],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr
    if "RuleTableError" in output:
        return REJECTED, output
    if proc.returncode != 0:
        return MISMATCH, output
    return UNDETECTED, output


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_mutation_is_detected(mutation, tmp_path):
    name, mutate, expected = mutation
    mutant = tmp_path / "mutant.yaml"
    _mutate_to(mutate, mutant)
    actual, output = _classify(mutant)

    if name == "대조군-변이없음":
        assert actual == UNDETECTED, (
            "변이를 넣지 않았는데 테스트가 깨진다. 변이 러너 자체가 고장 났거나 "
            f"표가 이미 어긋나 있다.\n{output[-2000:]}"
        )
        return

    assert actual != UNDETECTED, (
        f"[{name}] 표를 망가뜨렸는데 아무 테스트도 깨지지 않았다. 픽스처 구멍이다."
    )
    assert actual == expected, (
        f"[{name}] 탐지 방식이 예상과 다르다. 예상={expected} 실제={actual}\n"
        "표가 바뀌면 이 기대값도 갱신할 것."
    )
