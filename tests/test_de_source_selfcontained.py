"""독일 계열 피드의 source 는 스스로 읽혀야 한다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    source 는 DESCRIPTION 의 "근거:" 뒤에 그대로 나간다(각 feed.py 의
    description= 한 곳). 구독자는 레포도 YAML 머리 주석도 다른 피드도 볼 수
    없다. 그러니 source 는 그것들을 가리키지 않고, "무개정" 같은 판정어 대신
    "… 찾지 못함(범위)" 이라는 검색 사실을 적는다.

nw·he·be 의 테스트가 같은 단언을 자기 피드에 대해 이미 든다. 여기는 그것을
독일 규칙 YAML 전부로 넓힌 것이다 — rules/de/ 와 rules/de_*/ 아래 모든 *.yaml
(designated 포함)의 모든 항목. 목록을 손으로 적지 않고 rules/ 를 스캔한다.
새 주를 더하면 그 주의 표가 자동으로 검사에 든다.

금지 문자열과 그 까닭:
    rules/ .yaml .py       레포 경로
    머리 주석 이 파일        YAML 머리 주석을 가리키는 말
    .ics 전례 미러          다른 피드(발행본)를 가리키는 말
    key 는 token 은         UID token 부기 — 내부 식별자
    무개정                  판정어. 검색 사실로 적는다
    _weihnachtstag         다른 항목의 내부 key 이름
    docs/research          레포의 조사 보고 경로 — 구독자는 레포를 볼 수 없다
    lunalism/holidays      레포 자체를 가리키는 말 — 같은 까닭

대소문자를 가리지 않고 찾는다(AGENTS.md — 소스가 소문자인데 대문자로 찾아 0 건으로
믿은 사례가 있다). 금지 목록 밖의 자기완결성(예: SUMMARY 라는 필드명, 한 개정법과의
"… 뒤에도 그대로" 대조)은 여기서 보지 않는다 — 규칙으로 정한 것만 고정한다.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = ROOT / "rules"

FORBIDDEN = (
    "rules/",
    ".yaml",
    ".py",
    "머리 주석",
    "이 파일",
    ".ics",
    "전례",
    "미러",
    "key 는",
    "token 은",
    "무개정",
    "_weihnachtstag",
    "docs/research",
    "lunalism/holidays",
)

# 독일 계열 표 전수 — rules/de/ 와 rules/de_*/ 의 *.yaml. feed.py 가 있는 패키지만 센다
# (tests/test_de_scope.py 의 STATE_CODES 와 같은 조건 + 전국 피드 de).
GERMAN_TABLES = sorted(
    path
    for pkg in RULES_DIR.iterdir()
    if pkg.is_dir()
    and (pkg.name == "de" or pkg.name.startswith("de_"))
    and (pkg / "feed.py").is_file()
    for path in pkg.glob("*.yaml")
)
assert GERMAN_TABLES, "rules/ 에서 독일 계열 표를 하나도 찾지 못했다"


def _entries():
    for path in GERMAN_TABLES:
        for entry in yaml.safe_load(path.read_text(encoding="utf-8"))["holidays"]:
            yield pytest.param(entry, id=f"{path.parent.name}/{path.name}::{entry['key']}")


def test_the_scan_covers_every_german_package_and_the_one_off_table():
    packages = {p.parent.name for p in GERMAN_TABLES}
    assert "de" in packages
    states = {
        p.name
        for p in RULES_DIR.iterdir()
        if p.name.startswith("de_") and (p / "feed.py").is_file()
    }
    assert states <= packages
    assert any(p.name == "designated_holidays.yaml" for p in GERMAN_TABLES)


@pytest.mark.parametrize("entry", list(_entries()))
def test_no_source_points_into_the_repo_or_states_a_verdict(entry):
    source = " ".join((entry.get("source") or "").split())
    folded = source.casefold()
    hits = [s for s in FORBIDDEN if s in source or s.casefold() in folded]
    assert not hits, hits
