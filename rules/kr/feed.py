"""대한민국 공휴일 → core.ics.Event.

직렬화는 하지 않는다. 그건 core/ics.py 다. 여기서 정하는 것은 무엇을 몇 년치
내보낼지, SUMMARY 에 무엇을 쓸지, DESCRIPTION 의 근거를 어디서 끌어올지다.
전부 한국 고유 결정이라 core 에 두지 않는다(core/__init__.py 참조).

--------------------------------------------------------------------------
DESCRIPTION 에 KASI 를 적지 않는다
--------------------------------------------------------------------------
KASI 특일정보는 대조 상대이지 채택 소스가 아니다. 우리는 어느 항목의 값도
KASI 에서 가져오지 않는다 — 법령과 계산으로 유도하고 KASI 와는 갈리는지만
본다(tests/test_source_agreement.py 참조). "KASI 확정" 같은 문구를 쓰면
코드가 하지 않는 주장을 하는 것이 된다.

그래서 근거는 세 갈래에서만 온다.
    법정공휴일   근거를 적지 않는다. 아래 참조
    대체공휴일   substitute_holidays.yaml 의 ruleset 호수
    지정공휴일   designated_holidays.yaml 의 항목별 source

재료가 없으면 DESCRIPTION 을 넣지 않는다. 빈칸을 추측으로 채우지 않는다.
"""

from __future__ import annotations

import re
from datetime import date

from core import ics
from rules.kr import holiday_calendar as hc

# 하한 고정. 이 이전은 내보내지 않는다. 규칙 표의 완결성 경계는 더 아래지만
# (지정 표 2015-01-01) 피드로 발행할 이유가 없는 구간이다.
RANGE_START = date(2020, 1, 1)

# 상한은 실행 시점 기준 이만큼 뒤의 12-31 이다. 미리 발행해 두어야 구독자
# 캘린더에 미래가 보인다. 이 구간의 상당 부분은 잠정이며 STATUS 로 표시된다.
YEARS_AHEAD = 5

PRODID = "-//lunalism//holidays.lunalism.com//KO"
CALNAME = "대한민국 공휴일"
TZID = "Asia/Seoul"

_WHITESPACE = re.compile(r"\s+")

# key 가 없는 항목의 UID token. 지정 표(임시공휴일·선거일)와 대체공휴일이
# 여기 해당한다. 셋 다 substitute_holidays.yaml 의 holidays 레지스트리에 없어서
# key 가 빈 문자열이다.
#
# statutory 는 여기 없다. 양력·음력 표에서 오는 항목은 전부 key 를 갖는다.
# 그런데도 key 없는 statutory 가 들어오면 _token() 이 터진다. 약어를 하나
# 지어 붙이면 그 순간 어느 공휴일인지 구분되지 않는 UID 가 생기고,
# 같은 날 statutory 가 둘이면 UID 가 충돌한다.
_KIND_ABBREV = {
    hc.KIND_SUBSTITUTE: "sub",
    "temporary": "tmp",
    "election": "elc",
}


def feed_range(today: date) -> tuple:
    """(시작일, 종료일). 종료일은 today 기준 YEARS_AHEAD 년 뒤의 12-31.

    today 를 인자로 받는다. 시계를 여기서 읽지 않는 이유는 core/ics.py 의
    DTSTAMP 설명과 같다 — 읽는 순간 같은 입력으로 같은 결과가 나오지 않는다.
    """
    return RANGE_START, date(today.year + YEARS_AHEAD, 12, 31)


def _one_line(text: str) -> str:
    return _WHITESPACE.sub(" ", (text or "").strip())


def _token(holiday) -> str:
    """UID 의 뒷부분.

    key 가 있으면 key 를 그대로 쓴다. key 는 규칙 조회용 식별자라 이미 함부로
    바꿀 수 없는 값이다 — 대체공휴일 판정이 이 값으로 호 소속을 찾고, 연휴가
    명절 당일과 같은 key 를 공유하는 것도 그 때문이다
    (holiday_calendar.py:524-526). 그래서 UID 에 쓰기 적합하다. 바꾸면 이미
    대체공휴일 유도가 깨지므로, UID 만 조용히 바뀌는 일이 생기지 않는다.

    key 가 없으면 kind 약어를 쓴다. 지정 표와 대체공휴일이 그런데, 셋 다 같은
    날 같은 kind 가 둘 있을 수 없어 그것으로 충분하다. 겹치면 assign_uids() 가
    멈춘다. 2020~2035 전수로 겹치는 자리가 없음을 확인했다.

    이름(name)은 쓰지 않는다. 표기가 흔들리는 값이라(신정 → 1월1일,
    석가탄신일 → 부처님오신날) 표기 정정이 UID 변경이 된다.
    """
    if holiday.key:
        return holiday.key
    try:
        return _KIND_ABBREV[holiday.kind]
    except KeyError:
        raise ics.IcsError(
            f"key 가 없는데 kind {holiday.kind!r} 의 UID token 규칙이 없다: {holiday.name!r}.\n"
            "약어를 지어 붙이지 말 것 — 어느 공휴일인지 구분되지 않는 UID 가 생기고, "
            "같은 날 같은 kind 가 둘이면 충돌한다. _KIND_ABBREV 를 보고 판단할 것."
        ) from None


def _substitute_description(day: date, holiday) -> str:
    """대체공휴일의 근거. ruleset 호수까지만 적는다.

    조문(제3조제1항제n호)은 적지 않는다. substitute_eligibility() 가 돌려주는
    clauses 는 "이 공휴일이 대체공휴일 대상이 되는 근거 조항들"이지 "이 날짜의
    대체공휴일을 실제로 발생시킨 호"가 아니다. 둘을 같은 것으로 적으면 겹침
    사례에서 틀린다 — 2025-05-06 이 그 경우이고, 어느 호가 트리거인지는
    substitute_holidays.yaml 의 open_questions 3호-귀속-불명 으로 남아 있다.

    원인 공휴일 이름도 적지 않는다. 같은 이유다. source_key 는 겹침 사례에서
    "대상인 것 중 하나"일 뿐 확정된 트리거가 아니다.

    호수는 대체공휴일이 놓인 날짜로 찾는다. 원래 공휴일 날짜와 다를 수 있으나
    (대체공휴일은 며칠 뒤로 밀린다) 지금 표의 시행일은 2013-11-05 · 2021-08-04 ·
    2023-05-04 · 2026-05-01 이라 그 사이에 밀린 대체공휴일이 걸치는 자리가 없다.
    시행일이 추가되면 여기를 다시 볼 것.
    """
    if not holiday.source_key:
        return ""
    try:
        ruleset = hc.substitute_eligibility(holiday.source_key, day)["ruleset"]
    except (hc.CalendarError, hc.MappingUnresolved):
        # 답할 수 없으면 비운다. 모르는 근거를 지어내지 않는다.
        return ""
    if not ruleset:
        return ""
    return f"「관공서의 공휴일에 관한 규정」(대통령령 {ruleset})에 따른 대체공휴일."


def _designated_description(day: date, holiday) -> str:
    """임시공휴일·선거일의 근거. designated_holidays.yaml 의 항목별 source 뿐이다.

    note 와 source_todo 는 쓰지 않는다. note 에는 KASI 대조 결과가 들어 있고
    (2015-08-14 이 그렇다) source_todo 는 미확인 사항이라 둘 다 구독자에게
    나갈 것이 아니다. verified 도 마찬가지다 — 우리 내부 검증 상태다.
    """
    for entry in hc._designated()["by_date"].get(day, ()):
        if entry["name"] == holiday.name and entry["kind"] == holiday.kind:
            source = _one_line(entry.get("source") or "")
            return f"근거: {source}" if source else ""
    return ""


def _description(day: date, holiday) -> str:
    if holiday.kind == hc.KIND_STATUTORY:
        # 법정공휴일에는 근거를 적지 않는다. 지금 표에 조문 번호가 없다 —
        # substitute_holidays.yaml 의 holidays 레지스트리가 들고 있는 것은
        # 이름과 group(국경일/명절/기타)뿐이고 제2조 각 호와의 대응은 없다.
        # 없는 것을 적을 수 없고, group 을 근거처럼 내보내면 근거가 아닌 것이
        # 근거로 읽힌다.
        return ""
    if holiday.kind == hc.KIND_SUBSTITUTE:
        return _substitute_description(day, holiday)
    return _designated_description(day, holiday)


def events(start: date, end: date) -> list:
    """구간 안의 모든 이벤트. 날짜 오름차순.

    holidays_on() 이 예외를 던지면 잡지 않는다. UnsupportedYear 나
    MappingUnresolved 는 "답할 수 없다"는 뜻이고, 그 상태로 피드를 내면
    구독자 캘린더에서 공휴일이 조용히 사라진다. 멈추는 편이 낫다.
    """
    out = []
    day = start
    while day <= end:
        provisional = hc.is_provisional(day)
        for holiday in hc.holidays_on(day):
            out.append(
                ics.Event(
                    day=day,
                    # SUMMARY 는 Holiday.name 그대로다. 대체공휴일은 "대체공휴일"
                    # 이고 원인 공휴일명을 붙이지 않는다(위 3호-귀속-불명).
                    summary=holiday.name,
                    kind=holiday.kind,
                    description=_description(day, holiday),
                    # 항목의 provisional 과 같은 값이지만 날짜 축에서 직접 묻는다.
                    # holidays_on() 은 확정 구간 안에서는 플래그를 찍지 않고
                    # 그대로 돌려주므로, 항목 쪽만 보면 두 경로가 생긴다.
                    provisional=provisional,
                    # UID 의 뒷부분. 항목 자체에서 나오므로 같은 날 다른 항목이
                    # 생기거나 없어져도 변하지 않는다. _token() 참조.
                    token=_token(holiday),
                )
            )
        day = day.fromordinal(day.toordinal() + 1)
    return out


def build(*, today: date, dtstamp) -> bytes:
    """피드 한 벌. 같은 (today, dtstamp) 면 같은 바이트가 나온다."""
    start, end = feed_range(today)
    return ics.render(
        events(start, end),
        dtstamp=dtstamp,
        prodid=PRODID,
        calname=CALNAME,
        tzid=TZID,
    )


if __name__ == "__main__":  # pragma: no cover
    import datetime as _dt
    import sys

    # 시계를 읽는 곳은 여기 하나다. 모듈 안에서는 읽지 않는다.
    now = _dt.datetime.now(_dt.UTC)
    sys.stdout.buffer.write(build(today=now.date(), dtstamp=now))
