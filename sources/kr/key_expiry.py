"""KASI 인증키 활용기간 만료 확인.

kasi_names.yaml 의 open_questions 에 있는 api-활용기간-만료 가 요구한 장치다.
그 질문의 요점은 만료 자체가 아니라 **조용히 멈춘다**는 것이었다 —

    피드 생성이 실패해도 이미 발행된 .ics 는 그대로 남아 있어서, 구독자
    쪽에서는 아무 일도 없어 보인다. 갱신이 끊긴 것을 아무도 모른 채 시간이 간다.

그래서 만료된 뒤가 아니라 만료 **전에** 시끄러워야 한다. CI 가 매 발행마다
이 검사를 먼저 돌리고, 남은 기간이 모자라면 발행하지 않고 실패한다.
실패한 워크플로는 눈에 띄고, 연속 실패하면 이슈가 생긴다.

만료를 지나서 실패하면 늦다. 그때는 이미 갱신이 끊긴 뒤이고, 키를 다시 받는
데 걸리는 시간만큼 피드가 낡는다.
"""

from __future__ import annotations

import sys
from datetime import date

from sources.kr import kasi_parser

# 만료까지 이만큼 안 남으면 발행을 멈춘다.
#
# 60 일인 이유는 연장 절차가 얼마나 걸리는지 모르기 때문이다. 공공데이터포털
# 활용신청 연장의 소요 기간을 확인하지 않았다. 확인하면 근거 있는 값으로
# 조정할 것 — 지금은 "두 달이면 사람이 알아채고 처리할 수 있다"는 짐작이다.
MIN_DAYS = 60


class KeyExpiring(RuntimeError):
    """활용기간이 얼마 남지 않았다. 발행하지 않는다."""


def expires_on() -> date:
    """활용기간 만료일. kasi_names.yaml 의 service 블록에서 읽는다."""
    raw = kasi_parser.load_service()
    value = raw.get("expires_on")
    if not isinstance(value, date):
        raise KeyExpiring(
            f"kasi_names.yaml 의 service.expires_on 이 날짜가 아니다: {value!r}\n"
            "만료를 확인할 수 없으면 발행하지 않는다."
        )
    return value


def days_left(today: date) -> int:
    return (expires_on() - today).days


def check(today: date, min_days: int = MIN_DAYS) -> int:
    """남은 일수. 모자라면 KeyExpiring.

    today 를 인자로 받는다. 시계를 여기서 읽으면 같은 입력에 같은 답이
    나온다는 보장이 없어 테스트할 수 없다. core/ics.py 의 DTSTAMP 와 같다.
    """
    remaining = days_left(today)
    if remaining < min_days:
        raise KeyExpiring(
            f"KASI 활용기간 만료까지 {remaining}일 남았다 (만료일 {expires_on()}, "
            f"기준 {min_days}일).\n"
            "발행하지 않았다. 만료되면 인증이 거부되고 갱신이 끊기는데, 이미 발행된 "
            ".ics 는 그대로 남아 있어 구독자 쪽에서는 아무 일도 없어 보인다.\n"
            "공공데이터포털에서 활용기간을 연장하고 kasi_names.yaml 의 "
            "service.expires_on 을 갱신할 것."
        )
    return remaining


if __name__ == "__main__":  # pragma: no cover
    import datetime as _dt

    # 시계를 읽는 곳은 여기 하나다.
    _today = _dt.datetime.now(_dt.UTC).date()
    try:
        _left = check(_today)
    except KeyExpiring as exc:
        print(f"[key-expiry] {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"[key-expiry] 만료까지 {_left}일 (만료일 {expires_on()})")
