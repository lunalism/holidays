"""rules/kr/designated_holidays.yaml 의 근거 필드가 채워져 있는가.

지정 공휴일은 규칙으로 유도할 수 없어 날짜를 하나씩 적어 둔 표다. 유도가
없으니 값이 틀려도 다른 계산과 어긋나지 않는다 — 표에 적힌 것이 곧 답이다.
그래서 이 표에서 근거를 잃으면 되짚을 방법이 없다.

`source` 는 내부 메모가 아니라 발행물의 일부이기도 하다. rules/kr/feed.py 의
_designated_description() 이 이 필드를 읽어 .ics 의 DESCRIPTION 으로 내보낸다.
비어 있으면 구독자에게 근거 없는 공휴일이 나간다.

검사 대상은 `holidays:` 목록이다. `kinds:` 블록에도 source 가 있지만 그쪽은
날짜가 아니라 분류의 근거이고, 예외 목록이 날짜 집합이라 같은 자리에서 다룰 수
없다. 그쪽 미확인 사항은 해당 항목의 source_todo 와 open_questions 가 들고 있다.

같은 검사를 다른 표로 넓히지 않았다. 이유는 docs/branch-rules.md 가 아니라
아래 주석에 적어 둔다 — 표를 열어 확인한 결과이기 때문이다.

    substitute_holidays.yaml  rulesets·clauses·placement_rules·arrangements 의
                              source 가 전부 채워져 있다. holidays: 는 이름과
                              group 을 담은 레지스트리라 source 필드 자체가
                              스키마에 없다. 근거를 붙일 대상이 아니다.
    solar_holidays.yaml       10 건 전부 채워져 있다.
    lunar_holidays.yaml       3 건 전부 채워져 있다.
    tests/fixtures/kr.yaml    tests/test_kr_fixtures.py 의
                              test_every_case_has_a_source 가 이미 추적한다
                              (strict xfail). 두 곳에서 같은 것을 검사하면
                              한 곳만 갱신된다.

빈칸이 생기면 그때 이 파일에 넣는 것이 아니라, 애초에 빈칸으로 병합되지 않게
하는 것이 목적이다.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

TABLE_PATH = Path(__file__).parent.parent / "rules" / "kr" / "designated_holidays.yaml"

# 근거를 아직 확인하지 못한 항목. 전부 국무회의 의결일·관보 게재일 미확인이다
# (각 항목의 source_todo 참조).
#
# --- 이 목록은 늘리지 않는다 ---
# 신규 항목은 source 없이 추가할 수 없다. 여기에 날짜를 더하는 것으로 통과시키지
# 말 것. 새로 넣는 항목은 근거를 확인한 뒤에 넣는 것이지, 넣어 두고 나중에
# 확인하는 것이 아니다. 넣어 두면 확인되지 않는다 — 이 표가 그 증거다.
#
# 줄어드는 방향으로만 움직인다. source 를 채우면 여기서 지워야 통과한다
# (test_source_pending_has_no_stale_entries).
#
# 추정으로 채우지 말 것. 관보 원문 대조는 designated_holidays.yaml 의
# open_questions 관보-일괄대조 로 남아 있고, 첫 발행 전에 일괄로 처리한다.
SOURCE_PENDING = frozenset(
    {
        date(2017, 5, 9),
        date(2017, 10, 2),
        date(2020, 8, 17),
        date(2023, 10, 2),
        date(2024, 10, 1),
        date(2025, 1, 27),
        date(2028, 4, 12),
    }
)


def _holidays() -> list:
    """표의 지정 내역. 로더를 거치지 않고 YAML 을 직접 읽는다.

    rules/kr/holiday_calendar.py 를 거치면 로더가 통과시킨 것만 보게 된다.
    여기서 보려는 것은 파일에 무엇이 적혀 있는가이지 로더가 무엇을 읽어냈는가가
    아니다.
    """
    return yaml.safe_load(TABLE_PATH.read_text(encoding="utf-8"))["holidays"]


def _has_source(entry: dict) -> bool:
    return bool((entry.get("source") or "").strip())


def _label(entry: dict) -> str:
    return f"{entry['date']} {entry.get('name', '?')} (kind={entry.get('kind', '?')})"


def test_every_designated_holiday_has_a_source():
    """근거 없는 지정 공휴일이 있으면 실패한다.

    SOURCE_PENDING 에 적힌 것만 예외다. 새 항목을 그 목록에 더해 통과시키지 말 것 —
    위 주석 참조.
    """
    missing = [
        entry
        for entry in _holidays()
        if not _has_source(entry) and entry["date"] not in SOURCE_PENDING
    ]
    assert not missing, (
        "source 가 비어 있다:\n"
        + "\n".join(f"  - {_label(e)}" for e in missing)
        + "\n\n확인한 근거(관보 호수 / 고시 번호 / 국무회의 일자)를 source 에 적을 것.\n"
        "추정해서 채우지 말 것. SOURCE_PENDING 에 날짜를 더해 통과시키지도 말 것 —\n"
        "그 목록은 줄어드는 방향으로만 움직인다."
    )


def test_source_pending_has_no_stale_entries():
    """source 를 채웠는데 SOURCE_PENDING 에 그대로 남아 있으면 실패한다.

    목록이 줄어드는 방향으로만 움직이게 하려면 이쪽도 필요하다. 이 검사가 없으면
    채운 항목이 목록에 남고, 목록은 실제 미확인 건수보다 길어진 채로 굳는다.
    그러면 "아직 이만큼 남았다"는 신호가 사실과 어긋나고, 위 테스트의 예외 범위도
    필요 이상으로 넓어진다.
    """
    filled = [
        entry
        for entry in _holidays()
        if _has_source(entry) and entry["date"] in SOURCE_PENDING
    ]
    assert not filled, (
        "source 가 채워졌는데 SOURCE_PENDING 에 남아 있다:\n"
        + "\n".join(f"  - {_label(e)}" for e in filled)
        + f"\n\n{TABLE_PATH.name} 의 근거를 확인했다면 "
        f"{Path(__file__).name} 의 SOURCE_PENDING 에서 그 날짜를 지울 것."
    )
