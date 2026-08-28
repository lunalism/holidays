"""status.json 조립 — 나라별 조각을 모아 한 파일로 만든다.

--------------------------------------------------------------------------
왜 rules/ 인가
--------------------------------------------------------------------------
이 파일은 rules/ 아래 여러 나라를 함께 import 하는 유일한 자리다. 나라별
모듈은 자기 조각만 내고 서로를 모른다 — kr 이 jp 를 import 하기 시작하면 한
나라의 문제가 다른 나라로 번지고, 나라를 하나 빼는 일이 남은 나라의 수정이
된다.

core/ 에 두지 않는다. 의존 방향이 rules → core 한 방향이기 때문이다. core 는
rules 를 부를 수 없다 — 조립자를 core 에 두면 core 가 rules.kr 을 import 하고
rules.kr 이 core.ics 를 import 하는 순환이 된다. 방향을 지키면서 여러 나라를
아는 자리는 rules/ 뿐이다.

status.json 을 왜 매번 커밋하는지는 rules/kr/status.py 의 모듈 docstring 에
적혀 있다.
"""

from __future__ import annotations

import json
from datetime import date

from rules.kr import status as kr


def status(*, today: date, dtstamp) -> dict:
    """지금 상태 한 덩어리. 시계는 인자로 받는다.

    dict 리터럴의 순서가 곧 status.json 의 키 순서다. render() 참조.
    """
    return {
        "generated_at": dtstamp.isoformat(),
        "feeds": {"kr": kr.feed_status(today=today)},
        **kr.top_level_sections(today=today),
    }


def render(*, today: date, dtstamp) -> str:
    """파일에 쓸 문자열.

    sort_keys 를 쓰지 않는다. 키 순서는 status() 의 dict 리터럴 순서 그대로이고,
    그 순서가 코드에 고정되어 있어 diff 는 값 변화만 보여준다. 정렬로 얻는 것이
    아니라 리터럴이 고정이라 얻는 성질이다.

    지금 와서 sort_keys 를 켜면 안 된다. 커밋된 status.json 은 리터럴 순서로
    쓰여 있어(generated_at, feeds, coverage, uid, verification, kasi_key —
    알파벳순이 아니다) 켜는 순간 전 파일이 한 번 재정렬되고, 값이 하나도 바뀌지
    않은 발행에서 diff 가 통째로 튄다.
    """
    return json.dumps(status(today=today, dtstamp=dtstamp), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":  # pragma: no cover
    import datetime as _dt
    import sys
    from pathlib import Path

    _now = _dt.datetime.now(_dt.UTC)
    _target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("status.json")
    _target.write_text(render(today=_now.date(), dtstamp=_now), encoding="utf-8")
    print(f"[status] {_target}")
