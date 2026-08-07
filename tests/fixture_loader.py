"""정답 픽스처 로더. 검증 상태를 파라미터화 단계에서 규칙으로 처리한다.

verified: false 인 케이스는 여기서 자동으로 xfail 마크를 받는다.
케이스마다 손으로 마크를 달지 않는다. 손으로 달면 케이스를 추가할 때
파이썬을 건드려야 하고, 다는 걸 잊으면 미검증 답이 조용히 초록불이 된다.

지금은 대부분 답이 맞아서 XPASS 로 뜬다. 그게 의도다.
"통과하지만 원문 대조는 안 됐다"는 상태가 눈에 보여야 한다.
원문을 확인해 verified: true 로 바꾸면 마크가 사라지고 평범한 통과가 된다.

xfail 은 결과의 옳고 그름을 주장하는 테스트에만 붙인다.
스키마 검증(why 가 있는가, names 와 kinds 길이가 맞는가)은 원문 대조와
무관하므로 raw 목록을 그대로 쓴다.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "kr.yaml"

_FIXTURE = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))

DAYS = _FIXTURE["days"]
SUBSTITUTE_RULES = _FIXTURE["substitute_rules"]
ALL_CASES = DAYS + SUBSTITUTE_RULES


def is_verified(case: dict) -> bool:
    return bool(case.get("verified"))


def ids(cases) -> list:
    return [case["id"] for case in cases]


def params(cases) -> list:
    """정답 대조용 파라미터. verified: false 면 xfail 을 붙인다.

    strict=False 인 이유: 지금은 전부 통과하므로 strict 였다면 XPASS 가 실패가 되어
    수트가 통째로 빨개진다. 대신 XPASS 로 드러난다.
    """
    out = []
    for case in cases:
        marks = []
        if not is_verified(case):
            marks.append(
                pytest.mark.xfail(
                    reason=f"{case['id']}: 법제처 원문 대조 전(verified: false)",
                    strict=False,
                )
            )
        out.append(pytest.param(case, id=case["id"], marks=marks))
    return out
