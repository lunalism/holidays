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

import os
import re
from datetime import date
from pathlib import Path

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

# 대체공휴일의 UID token. kind 에서 나오는 유일한 token 이고, 여기 남아 있는
# 이유는 대체공휴일이 데이터가 아니라 규칙에서 유도되는 항목이라 표에 적어 둘
# 자리가 없어서다.
#
# 지정 공휴일(임시공휴일·선거일)에는 전에 tmp/elc 를 썼다. 지웠다.
# 그건 우리 판정 결과라서 kind 가 정정되면 UID 가 함께 바뀌었다. 지금은
# designated_holidays.yaml 의 uid_token 을 쓴다.
#
# substitute 는 그 문제가 없다. 대체공휴일이 대체공휴일이 아니게 되는 정정은
# 항목이 사라지는 것이지 kind 가 옮겨가는 것이 아니다.
#
# statutory 는 여기 없다. 양력·음력 표에서 오는 항목은 전부 key 를 갖는다.
# 그런데도 key 없는 statutory 가 들어오면 _token() 이 터진다. 약어를 하나
# 지어 붙이면 그 순간 어느 공휴일인지 구분되지 않는 UID 가 생기고,
# 같은 날 statutory 가 둘이면 UID 가 충돌한다.
_KIND_ABBREV = {
    hc.KIND_SUBSTITUTE: "sub",
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

    key 가 없으면 uid_token 을 본다. 지정 공휴일(임시공휴일·선거일)이 그렇고,
    designated_holidays.yaml 이 항목마다 들고 있다. kind 에서 유도하지 않는
    것이 요점이다 — 전에는 tmp/elc 를 썼는데, kind 는 우리 판정이라
    선거일-kind-판정 이 풀려 temporary 가 election 으로 옮겨가면 UID 가 함께
    바뀌었다. 2025-06-03 이 실제로 그 후보다.

    대체공휴일만 kind 에서 나온다(sub). 규칙에서 유도되는 항목이라 표에 적어
    둘 자리가 없고, 대체공휴일이 다른 kind 로 옮겨가는 정정은 없다.

    이름(name)은 쓰지 않는다. 표기가 흔들리는 값이라(신정 → 1월1일,
    석가탄신일 → 부처님오신날) 표기 정정이 UID 변경이 된다.
    """
    if holiday.key:
        return holiday.key
    if getattr(holiday, "uid_token", ""):
        return holiday.uid_token
    if holiday.kind in _KIND_ABBREV:
        return _KIND_ABBREV[holiday.kind]
    raise ics.IcsError(
        f"UID token 을 정할 수 없다: {holiday.name!r} (kind={holiday.kind!r}).\n"
        "key 도 uid_token 도 없다. 지정 공휴일이면 designated_holidays.yaml 에 "
        "uid_token 을 넣을 것.\n"
        "약어를 지어 붙이지 말 것 — 어느 공휴일인지 구분되지 않는 UID 가 생기고, "
        "같은 날 같은 kind 가 둘이면 충돌한다."
    )


# 대체공휴일 SUMMARY 에 넣을 원인 공휴일 이름.
#
# 기본은 공휴일 레지스트리의 이름(hc.holiday_name)이고, 여기 적힌 것만 다르게
# 쓴다. 연휴 중 하루가 주말에 걸려 생긴 대체공휴일이라도 사람이 부르는 이름은
# 명절 이름이다 — "대체공휴일(설날 연휴)" 는 어색하다.
#
# aliases 를 자동으로 쓰지 않는 이유: 그쪽을 따르면 기독탄신일 → 성탄절,
# 노동절 → 근로자의 날 로 바뀌어 같은 피드 안에서 표기가 갈린다. 바꿀 항목만
# 손으로 적는다.
#
# new_years_day 는 레지스트리 이름이 "1월 1일" 이라 "대체공휴일(1월 1일)" 이
# 된다. 그것도 어색해서 넣었다. 다만 그 날 자체의 SUMMARY 는 여전히 "1월 1일"
# 이므로 이 한 건은 표기가 갈린다. 지금 발행 범위에는 이 원인의 대체공휴일이
# 없고, 생기면 그때 그 날의 이름과 함께 다시 볼 것.
SUBSTITUTE_ORIGIN_NAMES = {
    "seollal": "설날",
    "chuseok": "추석",
    "new_years_day": "신정",
}

# 원인이 둘 이상일 때의 구분자.
#
# 가운뎃점은 이미 공휴일 이름 안에 쓰인다(3·1절). 그래서 3·1절이 다른 공휴일과
# 평일에 겹치면 "대체공휴일(3·1절·어린이날)" 이 되어 원인이 셋처럼 읽힌다.
# 지금 겹침 2 건에는 3·1절이 없어 실제로 밟히지 않는다. 밟히면 구분자를 바꿀 것.
SUBSTITUTE_ORIGIN_SEPARATOR = "·"


def _origin_name(key: str) -> str:
    return SUBSTITUTE_ORIGIN_NAMES.get(key) or hc.holiday_name(key)


def _substitute_origin(holiday) -> str:
    """대체공휴일 SUMMARY 의 괄호 안. 원인이 없으면 빈 문자열.

    ----------------------------------------------------------------------
    겹침이면 둘 다 적는다
    ----------------------------------------------------------------------
    제3조제1항제3호로 생긴 대체공휴일은 그 날 겹친 공휴일 중 어느 쪽이
    트리거인지 법이 정하지 않았다(3호-귀속-불명). 하나를 골라 적으면 우리가
    고른 것이 확인된 사실처럼 읽힌다. 실제로 2028-10-05 는 KASI 가 추석으로,
    우리 코드의 대표값은 개천절로 갈린다.

    둘 다 적으면 그 날의 실제 상태를 그대로 쓰는 것이 된다. 법이 귀속을 정하지
    않았다는 사실 자체가 정보이고, 표기가 둘을 포함하므로 위 불일치도 사라진다.

    source_key(대표값)가 아니라 source_keys(관측)를 쓰는 것이 요점이다.
    """
    keys = tuple(getattr(holiday, "source_keys", ()) or ())
    if not keys and holiday.source_key:
        keys = (holiday.source_key,)
    if not keys:
        return ""
    return SUBSTITUTE_ORIGIN_SEPARATOR.join(_origin_name(k) for k in keys)


def _substitute_description(day: date, holiday) -> str:
    """대체공휴일의 근거. ruleset 호수까지만 적는다.

    조문(제3조제1항제n호)은 적지 않는다. substitute_eligibility() 가 돌려주는
    clauses 는 "이 공휴일이 대체공휴일 대상이 되는 근거 조항들"이지 "이 날짜의
    대체공휴일을 실제로 발생시킨 호"가 아니다. 둘을 같은 것으로 적으면 겹침
    사례에서 틀린다. 발행 범위(2020~2031) 안의 겹침은 2 건이다 —
    2025-05-06(어린이날+부처님오신날)과 2028-10-05(개천절+추석)이고, 어느 호가
    트리거인지는 substitute_holidays.yaml 의 open_questions 3호-귀속-불명 으로
    남아 있다.

    여기서 source_key 를 쓰는 것은 호수 조회에 키가 하나 필요해서다. 그 값은
    겹침에서 "대상인 것 중 하나"일 뿐이고, 지금 두 사례는 어느 쪽을 넣어도
    ruleset 이 같아 결과가 갈리지 않는다. 갈리는 표가 생기면 여기를 다시 볼 것.

    SUMMARY 쪽은 다르게 간다. 원인을 적되 겹침이면 둘 다 적는다 —
    _substitute_origin() 참조.

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


def _summary(holiday) -> str:
    """SUMMARY. 대체공휴일만 원인을 괄호로 덧붙인다.

    "대체공휴일" 만으로는 구독자가 어느 공휴일 때문에 쉬는지 알 수 없다.
    같은 이름이 한 해에 여러 번 나오므로 캘린더에서 구분도 되지 않는다.

    UID 에는 들어가지 않는다. token 은 'sub' 하나이고 원인이 정정되어도
    UID 가 바뀌지 않는다(_token() 참조).
    """
    if holiday.kind != hc.KIND_SUBSTITUTE:
        return holiday.name
    origin = _substitute_origin(holiday)
    return f"{holiday.name}({origin})" if origin else holiday.name


def _event(day: date, holiday, provisional: bool) -> ics.Event:
    """Holiday 하나 → Event 하나."""
    return ics.Event(
        day=day,
        summary=_summary(holiday),
        kind=holiday.kind,
        description=_description(day, holiday),
        provisional=provisional,
        # UID 의 뒷부분. 항목 자체에서 나오므로 같은 날 다른 항목이
        # 생기거나 없어져도 변하지 않는다. _token() 참조.
        token=_token(holiday),
        # 진단 전용. token 이 겹쳐 멈출 때 어느 데이터를 봐야 하는지 알려 준다.
        # 두 대체공휴일이 부딪히면 name·kind 는 똑같고 source_key 만 다르므로,
        # 이 줄이 없으면 무엇이 부딪혔는지 구분되지 않는다.
        origin=(
            f"key={holiday.key!r} uid_token={getattr(holiday, 'uid_token', '')!r} "
            f"source_key={holiday.source_key!r}"
        ),
    )


def events(start: date, end: date) -> list:
    """구간 안의 모든 이벤트. 날짜 오름차순.

    holidays_on() 이 예외를 던지면 잡지 않는다. UnsupportedYear 나
    MappingUnresolved 는 "답할 수 없다"는 뜻이고, 그 상태로 피드를 내면
    구독자 캘린더에서 공휴일이 조용히 사라진다. 멈추는 편이 낫다.
    """
    out = []
    day = start
    while day <= end:
        # 항목의 provisional 과 같은 값이지만 날짜 축에서 직접 묻는다.
        # holidays_on() 은 확정 구간 안에서는 플래그를 찍지 않고 그대로
        # 돌려주므로, 항목 쪽만 보면 두 경로가 생긴다.
        provisional = hc.is_provisional(day)
        for holiday in hc.holidays_on(day):
            out.append(_event(day, holiday, provisional))
        day = day.fromordinal(day.toordinal() + 1)
    return out


def build(*, today: date, dtstamp, previous: bytes = None) -> bytes:
    """피드 한 벌. 같은 (today, dtstamp, previous) 면 같은 바이트가 나온다.

    previous 는 직전에 발행한 .ics 의 바이트다. SEQUENCE 를 정하는 데만 쓴다.
    None 이면 첫 발행으로 보고 전부 0 이 나간다.
    """
    start, end = feed_range(today)
    return ics.render(
        events(start, end),
        dtstamp=dtstamp,
        prodid=PRODID,
        calname=CALNAME,
        tzid=TZID,
        previous=previous,
    )


# 발행 위치. SEQUENCE 의 진실 공급원은 여기 있는 직전 발행본이다.
# 상태 파일을 따로 두지 않는다 — 두면 파일과 발행본이 어긋날 수 있고,
# 어긋났을 때 어느 쪽이 맞는지 정할 근거가 없다. 발행본이 사실이다.
FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "kr.ics"


def publish(*, today: date, dtstamp, path: Path = None) -> Path:
    """피드를 파일로 낸다. 이전 발행본을 읽고, 새로 만들고, 원자적으로 바꾼다.

    ----------------------------------------------------------------------
    왜 stdout 리다이렉션을 쓰지 않는가
    ----------------------------------------------------------------------
    이 피드는 자기 자신의 직전 판을 입력으로 받는다. 그래서

        python -m rules.kr.feed > feeds/kr.ics

    는 쓸 수 없다. 셸이 프로세스를 띄우기 전에 feeds/kr.ics 를 먼저 비우므로,
    읽을 이전 발행본이 사라진 뒤에 프로그램이 시작한다. 지금 구현에서는 빈
    파일이 파싱에 실패해 빌드가 멈추지만, 그때는 이미 발행본이 지워진 뒤라
    git 말고는 되돌릴 방법이 없다.

    읽기와 쓰기를 한 함수 안에서 순서대로 하고, 쓰기는 같은 디렉터리의 임시
    파일에 한 뒤 os.replace 로 바꾼다. 같은 파일시스템 안의 replace 는
    원자적이라 중간에 죽어도 반쪽짜리 피드가 남지 않는다.

    임시 파일을 같은 디렉터리에 두는 것도 그 때문이다. /tmp 에 만들면 파일
    시스템이 달라질 수 있고, 그러면 replace 가 복사로 떨어져 원자성이 깨진다.
    """
    if not ics.UID_DOMAIN_CONFIRMED:
        raise ics.IcsError(
            f"UID 네임스페이스 {ics.UID_DOMAIN!r} 가 확정되지 않아 발행하지 않는다.\n"
            "한 번 발행하면 UID 를 바꿀 수 없다. 바꾸면 구독자 캘린더에서 모든 "
            "공휴일이 삭제 + 재생성으로 나타난다.\n"
            "확정했다면 core/ics.py 의 UID_DOMAIN_CONFIRMED 를 True 로 둘 것. "
            "그 커밋이 곧 확정 기록이다.\n"
            "발행 없이 내용만 보려면 build() 를 쓸 것 — 그쪽은 막지 않는다."
        )

    path = path or FEED_PATH
    previous = path.read_bytes() if path.exists() else None
    body = build(today=today, dtstamp=dtstamp, previous=previous)

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_bytes(body)
    os.replace(tmp, path)
    return path


if __name__ == "__main__":  # pragma: no cover
    import datetime as _dt
    import sys as _sys

    # 시계를 읽는 곳은 여기 하나다. 모듈 안에서는 읽지 않는다.
    _now = _dt.datetime.now(_dt.UTC)

    # 경로를 인자로 받는다. 없으면 FEED_PATH.
    # 리다이렉션(> feeds/kr.ics)을 쓸 수 없어서 필요한 자리다 — 셸이 프로세스
    # 시작 전에 이전 발행본을 비운다. publish() 의 docstring 참조.
    # 테스트가 진짜 진입점을 밟을 수 있게 하는 효과도 있다.
    _target = Path(_sys.argv[1]) if len(_sys.argv) > 1 else FEED_PATH
    print(f"발행: {publish(today=_now.date(), dtstamp=_now, path=_target)}")
