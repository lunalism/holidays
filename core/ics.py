"""iCalendar(RFC 5545) 직렬화와 UID 생성.

국가 공통이다. 국가별 규칙은 여기 두지 않는다 — 이 모듈은 무엇이 공휴일인지,
어느 조문이 근거인지 알지 못한다. 그건 rules/<국가> 가 정해서 Event 로 넘긴다.

--------------------------------------------------------------------------
DTSTAMP 를 시계에서 읽지 않는다
--------------------------------------------------------------------------
render() 는 dtstamp 를 인자로 받는다. 안에서 datetime.now() 를 부르지 않는다.

그렇게 하면 같은 입력으로 두 번 생성한 결과가 달라진다. 결정성 테스트가
불가능해지는 것이 첫 번째 문제이고, 더 실질적인 문제는 발행이다. 이 피드는
파일로 커밋되므로 내용이 하나도 안 바뀐 재생성에도 DTSTAMP 만 달라져 매번
diff 가 뜬다. 그러면 "무엇이 실제로 바뀌었나"를 diff 로 볼 수 없게 된다.

시계는 호출자가 읽는다. __main__ 이 그 자리다.

--------------------------------------------------------------------------
UID
--------------------------------------------------------------------------
    {YYYYMMDD}-{seq}@holidays.lunalism.com

한 번 공개되면 바꿀 수 없다. UID 가 바뀌면 캘린더 앱이 같은 공휴일을 새
이벤트로 인식해 중복이 생긴다(README 의 이벤트 UID 참조).

날짜와 순번만 넣는다. kind 는 넣지 않는다 — 우리 판정 결과이기 때문이다.
지금도 확정되지 않은 것들이 있고(선거일-가지번호, 3호-귀속-불명 등)
open_questions 가 풀리면 어떤 항목의 kind 가 바뀔 수 있다. kind 가 UID 에
들어가 있으면 그 판정 변경이 구독자 캘린더에서 "이벤트 삭제 + 새 이벤트 생성"
으로 나타난다. SEQUENCE 를 올려도 수습되지 않는다 — SEQUENCE 는 같은 UID
안에서의 개정이고, UID 가 달라지면 캘린더는 애초에 다른 이벤트로 본다.

날짜는 우리 판정이 아니라 사실이고, 순번은 내용에서 유도한다.
그래서 seq 를 정하는 규칙이 중요하다. assign_uids() 의 주석을 볼 것.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from icalendar import Calendar
from icalendar import Event as VEvent

UID_DOMAIN = "holidays.lunalism.com"

VERSION = "2.0"
CALSCALE = "GREGORIAN"


class IcsError(ValueError):
    """피드를 만들 수 없다."""


@dataclass(frozen=True)
class Event:
    """직렬화 직전의 이벤트 하나. 국가 규칙은 이미 다 적용된 상태여야 한다."""

    day: date
    summary: str
    kind: str

    # 빈 문자열이면 DESCRIPTION 을 넣지 않는다. 근거가 없으면 없는 대로 둔다.
    description: str = ""

    # 규칙 개정 확인 시점 이후. STATUS:TENTATIVE 가 붙는다.
    provisional: bool = False

    # UID 의 seq 를 정하는 값. assign_uids() 참조.
    # 내용에서 유도한 값이어야 하고 표의 나열 순서에 기대면 안 된다.
    order_key: tuple = field(default_factory=tuple)


def assign_uids(events) -> list:
    """[(Event, uid)] — 파일에 실릴 순서대로.

    ----------------------------------------------------------------------
    seq 는 그 날 전체의 순번이다. kind 로 가르지 않는다
    ----------------------------------------------------------------------
    kind 별로 seq 를 매기면 UID 에 kind 가 없어도 같은 값이 두 번 나온다.
    한 날짜 안에서 1 부터 센다.

    kind 를 UID 에서 뺀 이유는 모듈 docstring 에 있다. 정렬 키에서도 뺀다 —
    정렬에 남겨 두면 kind 판정이 바뀔 때 순서가 밀려 seq 가 바뀌고, UID 에서
    뺀 의미가 없어진다.

    ----------------------------------------------------------------------
    seq 는 order_key 오름차순이다. 목록에 담겨 온 순서를 쓰지 않는다
    ----------------------------------------------------------------------
    rules.kr 의 holidays_on() 은 표를 읽은 순서대로 항목을 쌓는다
    (양력 표 → 음력 표 → 지정 표 → 대체공휴일). 그 순서는 한 번의 실행 안에서는
    물론 실행 사이에도 재현되지만, 표의 나열 순서에 매여 있다.

    그것에 seq 를 걸면 안 된다. 누가 solar_holidays.yaml 의 줄 순서를 바꾸거나
    공휴일이 표 사이를 옮겨 가면 seq 가 조용히 뒤바뀌고, UID 가 바뀐 이벤트는
    구독자 캘린더에서 중복으로 나타난다. 코드 리뷰에서 잡히지도 않는다 —
    YAML 줄 하나를 옮긴 것이 UID 변경으로 보이지 않기 때문이다.

    그래서 정렬은 내용에서 유도한 order_key 로 한다. 표를 어떻게 재배열해도,
    공휴일이 어느 표에서 오든 같은 값이 나온다.

    한 날짜 안에서 order_key 가 겹치면 seq 를 정할 수 없다. 그때는 임의로
    고르지 않고 IcsError 로 멈춘다. 임의로 고르면 그 선택이 다음 실행에서
    뒤집힐 수 있고, 뒤집히는 순간 UID 가 바뀐다.
    """
    groups = {}
    for event in events:
        groups.setdefault(event.day, []).append(event)

    out = []
    for day, members in sorted(groups.items()):
        members = sorted(members, key=lambda e: e.order_key)

        keys = [e.order_key for e in members]
        if len(set(keys)) != len(keys):
            raise IcsError(
                f"{day.isoformat()}: order_key 가 겹쳐 seq 를 정할 수 없다.\n"
                f"  {keys}\n"
                "임의로 고르면 다음 실행에서 뒤집힐 수 있고, 그때 UID 가 바뀐다."
            )

        for seq, event in enumerate(members, start=1):
            out.append((event, f"{day:%Y%m%d}-{seq}@{UID_DOMAIN}"))
    return out


def _vevent(event: Event, uid: str, dtstamp: datetime) -> VEvent:
    out = VEvent()
    out.add("uid", uid)
    out.add("dtstamp", dtstamp)

    # 종일 이벤트. DTEND 는 배타적이라 다음 날이다.
    out.add("dtstart", event.day)
    out.add("dtend", event.day + timedelta(days=1))

    # 잠정·미검증 표시를 붙이지 않는다. 구독자 캘린더에 그대로 뜨는 문자열이고,
    # 우리 내부 검증 상태는 구독자가 알 바가 아니다. 잠정은 STATUS 로 나간다.
    out.add("summary", event.summary)

    # 공휴일은 시간을 점유하지 않는다. 두 속성을 같이 넣는 이유는 표준(TRANSP)을
    # 안 보고 자체 속성만 보는 클라이언트가 있어서다.
    out.add("transp", "TRANSPARENT")
    out.add("x-microsoft-cdo-busystatus", "FREE")

    # 0 고정. 증가 로직은 이번 범위가 아니다. 이벤트 내용이 바뀌었을 때 올려야
    # 하는데, 무엇을 "바뀜"으로 볼지가 정해져 있지 않다.
    out.add("sequence", 0)

    if event.description:
        out.add("description", event.description)

    if event.provisional:
        out.add("status", "TENTATIVE")
        out.add("x-holiday-status", "PROVISIONAL")
    return out


def render(events, *, dtstamp: datetime, prodid: str, calname: str, tzid: str) -> bytes:
    """VCALENDAR 한 덩어리. 같은 인자면 같은 바이트가 나온다.

    dtstamp 를 인자로 받는 이유는 모듈 docstring 에 있다.
    """
    if dtstamp.tzinfo is None:
        raise IcsError("dtstamp 에 타임존이 없다. UTC 로 줄 것 — DTSTAMP 는 UTC 여야 한다.")

    cal = Calendar()
    cal.add("version", VERSION)
    cal.add("prodid", prodid)
    cal.add("calscale", CALSCALE)
    cal.add("x-wr-calname", calname)
    cal.add("x-wr-timezone", tzid)

    for event, uid in assign_uids(events):
        cal.add_component(_vevent(event, uid, dtstamp))
    return cal.to_ical()
