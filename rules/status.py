"""status.json — 지금 이 저장소가 무엇을 주장하고 있는지 한 파일로.

나라별 조각을 모아 조립하고 직렬화하는 자리다. 조각은 rules/<나라>/status.py
가 낸다.

--------------------------------------------------------------------------
왜 매번 커밋하는가
--------------------------------------------------------------------------
두 가지 때문이다.

1. 갱신이 끊긴 것을 밖에서 알 수 있어야 한다.
   발행이 실패해도 이미 나가 있는 .ics 는 그대로 남는다. 구독자 쪽에서는
   아무 일도 없어 보인다. generated_at 이 밀리지 않으면 그것이 신호다.

2. GitHub Actions 는 60 일간 저장소 활동이 없으면 schedule 을 비활성화한다.
   공휴일 데이터는 몇 달씩 안 바뀌는 것이 정상이라, 피드에 변화가 없다는
   이유로 커밋이 없으면 예약 실행이 조용히 꺼진다. 꺼진 것도 조용해서
   아무도 모른다.

   status.json 은 generated_at 이 매번 바뀌므로 항상 커밋거리가 된다.
   그 커밋이 저장소를 살아 있게 유지한다.

--------------------------------------------------------------------------
자동 커밋이 근거를 대체하지 않는다
--------------------------------------------------------------------------
이 파일과 logs/build.jsonl 은 기계가 쓴다. 규칙과 데이터(rules/ 의 YAML)는
사람이 근거와 함께 쓴다. 둘을 섞지 말 것 — 자동 커밋이 데이터를 건드리기
시작하면 어느 값이 어디서 왔는지 구분되지 않는다.

--------------------------------------------------------------------------
왜 rules/ 인가
--------------------------------------------------------------------------
rules/ 아래 여러 나라를 함께 import 하는 자리는 이 파일(rules/status.py)과
교차 피드(합집합 rules/kr_jp/, 차집합 rules/kr_only/·rules/jp_only/)뿐이다.
나라별 모듈은 자기 조각만 내고 서로를 모른다 — kr 이 jp 를 import 하기
시작하면 한 나라의 문제가 다른 나라로 번지고, 나라를 하나 빼는 일이 남은
나라의 수정이 된다.

core/ 에 두지 않는다. 의존 방향이 rules → core 한 방향이기 때문이다. core 는
rules 를 부를 수 없다 — 조립자를 core 에 두면 core 가 rules.kr 을 import 하고
rules.kr 이 core.ics 를 import 하는 순환이 된다. 방향을 지키면서 여러 나라를
아는 자리는 rules/ 뿐이다.
"""

from __future__ import annotations

import json
from datetime import date

from rules.de import status as de
from rules.jp import status as jp
from rules.jp_only import status as jp_only
from rules.kr import status as kr
from rules.kr_jp import status as kr_jp
from rules.kr_only import status as kr_only


def status(*, today: date, dtstamp) -> dict:
    """지금 상태 한 덩어리. 시계는 인자로 받는다.

    dict 리터럴의 순서가 곧 status.json 의 키 순서다. render() 참조.
    """
    return {
        "generated_at": dtstamp.isoformat(),
        "feeds": {
            "kr": kr.feed_status(today=today),
            "jp": jp.feed_status(),
            "kr_jp": kr_jp.feed_status(today=today),
            "kr_only": kr_only.feed_status(today=today),
            "jp_only": jp_only.feed_status(today=today),
            "de": de.feed_status(today=today),
        },
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
