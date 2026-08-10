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
    {YYYYMMDD}-{token}@holidays.lunalism.com

한 번 공개되면 바꿀 수 없다. UID 가 바뀌면 캘린더 앱이 같은 공휴일을 새
이벤트로 인식해 중복이 생긴다(README 의 이벤트 UID 참조).

token 은 그 이벤트 자체에서 나온 값이다. 위치 기반 순번(seq)을 쓰지 않는다 —
같은 날 항목이 추가되거나 빠지면 그 앞뒤 항목의 순번이 밀리고, 밀리는 순간
손대지 않은 이벤트의 UID 까지 바뀐다. 임시공휴일이 기존 공휴일과 같은 날
지정되면 실제로 밟히는 경로다. token 은 형제 항목의 수나 정렬 위치와 무관하다.

kind 도 넣지 않는다. 우리 판정 결과이기 때문이다. 지금도 확정되지 않은 것들이
있고(선거일-가지번호, 3호-귀속-불명 등) open_questions 가 풀리면 어떤 항목의
kind 가 바뀔 수 있다. kind 가 UID 에 들어가 있으면 그 판정 변경이 구독자
캘린더에서 "이벤트 삭제 + 새 이벤트 생성"으로 나타난다. SEQUENCE 를 올려도
수습되지 않는다 — SEQUENCE 는 같은 UID 안에서의 개정이고, UID 가 달라지면
캘린더는 애초에 다른 이벤트로 본다.

token 을 무엇으로 할지는 국가별 결정이라 여기서 정하지 않는다. Event 를 짓는
쪽이 채워 넣는다(rules/kr/feed.py 의 _token 참조).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
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

    # UID 의 뒷부분. 그 이벤트 자체에서 나온 값이어야 하고, 같은 날 다른 항목이
    # 생기거나 없어져도 변하지 않아야 한다. assign_uids() 참조.
    token: str = ""

    # 진단 전용. token 이 겹쳐 멈출 때 무엇이 부딪혔는지 사람이 알아볼 수 있게
    # 하는 한 줄이다. 계산에도 출력에도 쓰지 않는다 — .ics 에 실리지 않는다.
    #
    # 무엇을 담을지는 Event 를 짓는 쪽이 정한다. core 는 국가별 필드 이름을
    # 알지 못하고, 알게 되면 여기에 국가 지식이 들어온다.
    origin: str = ""


def _describe(events) -> str:
    """충돌한 항목들을 사람이 읽을 수 있게 늘어놓는다.

    token 목록만 찍으면 ['sub', 'sub'] 가 되어 무엇이 부딪혔는지 알 수 없다.
    멈춘 사람이 바로 데이터를 찾아갈 수 있어야 한다.
    """
    lines = []
    for event in events:
        detail = f"    name={event.summary!r} kind={event.kind!r}"
        if event.origin:
            detail += f" {event.origin}"
        lines.append(f"  token={event.token!r}\n{detail}")
    return "\n".join(lines)


def assign_uids(events) -> list:
    """[(Event, uid)] — 파일에 실릴 순서대로.

    ----------------------------------------------------------------------
    위치 기반 순번을 쓰지 않는다
    ----------------------------------------------------------------------
    한 날짜 안에서 1, 2, 3 을 세어 붙이는 방식은 쓰지 않는다. 그렇게 하면 같은
    날에 항목이 하나 추가되거나 빠질 때 그 뒤 항목들의 번호가 전부 밀리고,
    손대지 않은 이벤트의 UID 까지 함께 바뀐다. 임시공휴일이 기존 공휴일과 같은
    날 지정되면 바로 밟히는 경로이고, 그때 구독자 캘린더에는 멀쩡하던 공휴일이
    지워졌다가 새로 생긴 것으로 나타난다.

    token 은 그 이벤트 자체에서 나온다. 옆에 무엇이 있든 없든 같은 값이다.

    ----------------------------------------------------------------------
    담겨 온 순서도 쓰지 않는다
    ----------------------------------------------------------------------
    rules.kr 의 holidays_on() 은 표를 읽은 순서대로 항목을 쌓는다
    (양력 표 → 음력 표 → 지정 표 → 대체공휴일). 실행 사이에 재현되기는 하지만
    표의 나열 순서에 매여 있어, 누가 YAML 줄 순서를 바꾸면 같이 바뀐다.

    파일에 실리는 순서는 (날짜, token) 오름차순으로 다시 정한다. UID 는 이미
    token 에서 나오므로 이 정렬은 UID 에 영향을 주지 않는다 — 출력이 실행마다
    같도록 고정하는 용도다.

    ----------------------------------------------------------------------
    같은 날 token 이 겹치면 멈춘다
    ----------------------------------------------------------------------
    UID 가 같은 이벤트가 둘 생긴다는 뜻이고, 캘린더는 뒤엣것으로 앞엣것을
    덮어쓴다. 공휴일 하나가 조용히 사라지는 것이라 임의로 접미사를 붙여
    넘기지 않는다 — 붙이는 순간 그 접미사가 다시 위치 기반이 된다.
    """
    groups = {}
    for event in events:
        groups.setdefault(event.day, []).append(event)

    out = []
    for day, members in sorted(groups.items()):
        members = sorted(members, key=lambda e: e.token)

        tokens = [e.token for e in members]
        blank = [e for e in members if not e.token]
        if blank:
            raise IcsError(
                f"{day.isoformat()}: token 이 빈 이벤트가 있다. UID 가 날짜만 남는다.\n"
                + _describe(blank)
            )

        clashing = {t for t, n in Counter(tokens).items() if n > 1}
        if clashing:
            raise IcsError(
                f"{day.isoformat()}: token 이 겹쳐 UID 가 같아진다 "
                f"— {', '.join(sorted(clashing))}\n"
                + _describe([e for e in members if e.token in clashing])
                + "\n같은 날 같은 token 은 자동 구분하지 않는다.\n"
                "데이터 입력 오류인지 확인하고, 실제로 별개 공휴일이라면\n"
                "UID 규칙을 사람이 결정해야 한다.\n"
                "임의로 접미사를 붙이지 않는다 — 그 접미사가 다시 위치 기반이 되어,\n"
                "다음에 항목이 하나 늘면 남의 UID 까지 밀려난다."
            )

        for event in members:
            out.append((event, f"{day:%Y%m%d}-{event.token}@{UID_DOMAIN}"))
    return out


@dataclass(frozen=True)
class PublishedEvent:
    """이전 발행본에서 읽어 온 이벤트 하나. SEQUENCE 계산의 입력이다."""

    uid: str
    dtstart: date
    dtend: date
    sequence: int
    summary: str


def read_published(raw: bytes) -> dict:
    """이전에 발행한 .ics → {uid: PublishedEvent}.

    읽지 못하면 IcsError. 빈 결과로 넘어가지 않는다 — 그러면 모든 SEQUENCE 가
    0 으로 되돌아가고, 구독자 캘린더는 이미 올라간 개정본을 헌 것으로 보고
    되돌릴 수 있다. 읽을 수 없는 이전 발행본은 사람이 봐야 한다.
    """
    try:
        parsed = Calendar.from_ical(raw)
    except Exception as exc:  # noqa: BLE001 - 라이브러리가 무엇을 던지든 같은 처리다
        raise IcsError(
            f"이전 발행본을 읽지 못했다: {type(exc).__name__}: {exc}\n"
            "0 으로 다시 시작하지 않는다. SEQUENCE 가 되감기면 구독자 캘린더가 "
            "이미 받은 개정본을 헌 것으로 본다.\n"
            "파일을 열어 무엇이 깨졌는지 확인할 것."
        ) from None

    out = {}
    for vevent in parsed.walk("VEVENT"):
        uid = str(vevent.get("UID") or "").strip()
        if not uid:
            raise IcsError("이전 발행본에 UID 없는 VEVENT 가 있다.")
        if uid in out:
            raise IcsError(
                f"이전 발행본에 UID 가 중복이다: {uid}\n"
                "어느 쪽이 최신인지 정할 수 없다. 파일을 확인할 것."
            )

        dtstart, dtend = vevent.get("DTSTART"), vevent.get("DTEND")
        if dtstart is None or dtend is None:
            raise IcsError(f"이전 발행본의 {uid} 에 DTSTART 나 DTEND 가 없다.")

        # SEQUENCE 가 없으면 RFC 5545 기본값 0 이다. 우리 피드는 항상 쓰지만
        # 남이 손댄 파일을 받을 수도 있으므로 표준 기본값을 따른다.
        raw_seq = vevent.get("SEQUENCE")
        sequence = 0 if raw_seq is None else int(raw_seq)
        if sequence < 0:
            raise IcsError(f"이전 발행본의 {uid} 에 SEQUENCE 가 음수다: {sequence}")

        out[uid] = PublishedEvent(
            uid=uid,
            dtstart=dtstart.dt,
            dtend=dtend.dt,
            sequence=sequence,
            summary=str(vevent.get("SUMMARY") or ""),
        )
    return out


def _sequences(pairs, published: dict) -> dict:
    """{uid: SEQUENCE}. 이전 발행본이 없으면 전부 0.

    ----------------------------------------------------------------------
    날짜가 바뀐 것만 올린다
    ----------------------------------------------------------------------
    SEQUENCE 는 "같은 이벤트의 몇 번째 개정인가"다. 캘린더 클라이언트는 이
    값으로 어느 쪽이 최신인지 정한다.

    올리는 기준은 DTSTART/DTEND 변경뿐이다. SUMMARY·DESCRIPTION·STATUS 가
    바뀌어도 올리지 않는다. 그쪽은 표기나 우리 확신도가 달라진 것이지 일정이
    달라진 것이 아니고, 구독자 입장에서 다시 알림을 받을 일이 아니다.
    잠정(STATUS:TENTATIVE)이 확정으로 바뀌는 것도 여기 해당한다 — 날짜가 그대로면
    구독자가 이미 잡아 둔 일정은 유효하다.

    ----------------------------------------------------------------------
    이전에 있던 UID 가 사라지면 멈춘다
    ----------------------------------------------------------------------
    발행된 이벤트를 그냥 빼면 구독자 캘린더에는 그대로 남는다. 없어졌다는
    사실이 전달되지 않는다. 정말 취소된 공휴일이라면 STATUS:CANCELLED 로
    내보내야 하고, 그건 아직 정하지 않은 정책이다. 그때까지는 멈춘다.
    """
    if published is None:
        return {uid: 0 for _, uid in pairs}

    current = {uid for _, uid in pairs}
    dropped = [p for uid, p in published.items() if uid not in current]
    if dropped:
        raise IcsError(
            f"이전 발행본에 있던 UID {len(dropped)} 건이 새 피드에 없다:\n"
            + "\n".join(f"  {p.uid}\n    SUMMARY={p.summary!r}" for p in sorted(
                dropped, key=lambda p: p.uid
            ))
            + "\n발행된 이벤트를 그냥 빼면 구독자 캘린더에는 그대로 남는다.\n"
            "정말 없어진 것이라면 STATUS:CANCELLED 정책을 먼저 정할 것."
        )

    out = {}
    for event, uid in pairs:
        prev = published.get(uid)
        if prev is None:
            out[uid] = 0  # 이전에 없던 이벤트. 첫 발행이다.
            continue

        moved = prev.dtstart != event.day or prev.dtend != event.day + timedelta(days=1)
        sequence = prev.sequence + 1 if moved else prev.sequence

        # 방어. 위 계산으로는 줄어들 수 없지만, 이 값이 줄어드는 순간 구독자
        # 캘린더가 이미 받은 개정본을 헌 것으로 보고 되돌린다. 되돌린 뒤에는
        # 어느 쪽이 맞는지 우리 쪽에서 알 방법이 없다. 규칙을 고칠 사람이
        # 여기서 걸리도록 남겨 둔다.
        if sequence < prev.sequence:
            raise IcsError(
                f"{uid}: SEQUENCE 가 {prev.sequence} 에서 {sequence} 로 줄어든다. "
                "SEQUENCE 는 감소할 수 없다."
            )
        out[uid] = sequence
    return out


def _vevent(event: Event, uid: str, dtstamp: datetime, sequence: int) -> VEvent:
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

    # 이전 발행본과 대조해 정한 값. _sequences() 참조.
    out.add("sequence", sequence)

    if event.description:
        out.add("description", event.description)

    if event.provisional:
        out.add("status", "TENTATIVE")
        out.add("x-holiday-status", "PROVISIONAL")
    return out


def render(
    events,
    *,
    dtstamp: datetime,
    prodid: str,
    calname: str,
    tzid: str,
    previous: bytes = None,
) -> bytes:
    """VCALENDAR 한 덩어리. 같은 인자면 같은 바이트가 나온다.

    previous 는 이전에 발행한 .ics 의 바이트다. SEQUENCE 를 정하는 데만 쓴다.
    None 이면 첫 발행으로 보고 전부 0 을 준다.

    파일을 여기서 읽지 않는 것은 dtstamp 와 같은 이유다 — 읽는 순간 같은
    인자로 같은 결과가 나온다는 보장이 사라진다. 읽는 것은 호출자의 일이다.
    다만 "읽어 봤더니 깨졌다"는 호출자가 판단할 일이 아니므로, 넘어온 바이트를
    해석하지 못하면 여기서 멈춘다.
    """
    if dtstamp.tzinfo is None:
        raise IcsError("dtstamp 에 타임존이 없다. UTC 로 줄 것 — DTSTAMP 는 UTC 여야 한다.")

    cal = Calendar()
    cal.add("version", VERSION)
    cal.add("prodid", prodid)
    cal.add("calscale", CALSCALE)
    cal.add("x-wr-calname", calname)
    cal.add("x-wr-timezone", tzid)

    pairs = assign_uids(events)
    sequences = _sequences(pairs, read_published(previous) if previous is not None else None)

    for event, uid in pairs:
        cal.add_component(_vevent(event, uid, dtstamp, sequences[uid]))
    return cal.to_ical()
