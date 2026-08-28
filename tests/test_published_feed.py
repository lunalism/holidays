"""커밋된 feeds/kr.ics 가 지금 코드와 데이터로 재현되는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    커밋된 피드는 커밋된 입력으로부터 재현 가능하다.

이 저장소의 신뢰성 주장은 git 히스토리에 있다. 어느 공휴일이 왜 그 날짜인지는
YAML 의 source 필드와 커밋이 들고 있고, 발행본은 그것들로부터 유도된 것이라고
말한다. 그 "유도된 것"이 실제로 유도되는지는 아무도 확인하지 않고 있었다.
여기서 확인한다. 리팩터링 안전망이기 이전에 그 주장 자체의 검증이다.

--------------------------------------------------------------------------
기존 바이트 비교 테스트로는 부족하다
--------------------------------------------------------------------------
tests/test_ics.py 에 전체 바이트를 비교하는 테스트가 셋 있다.

    test_the_same_input_produces_byte_identical_output
    test_dtstamp_is_an_input_not_a_clock_read
    test_republishing_unchanged_content_keeps_every_sequence

셋 다 build() 의 출력끼리 비교한다. 즉 self-consistency 다. 계산이 통째로
바뀌어도 두 출력이 나란히 바뀌므로 전부 통과한다. 커밋된 발행본과 대조하는
테스트는 하나도 없었고, 그래서 "출력이 안 바뀌었다"를 주장할 근거가 없었다.

--------------------------------------------------------------------------
왜 지금 붙이는가
--------------------------------------------------------------------------
두 가지가 겹친다.

1. 다음 브랜치에서 kst_moment() 와 KST_OFFSET_DAYS 를 core/ 로 올린다.
   오프셋 값도 급수도 건드리지 않으므로 출력은 안 바뀌어야 한다. 그러나
   그건 예상이지 실측이 아니다. 음력 공휴일은 삭이 KST 자정에 가까울 때
   하루가 갈리는 자리가 있어(rules/kr/astro.py 의 모듈 docstring 참조),
   부동소수 연산 순서가 달라지는 것만으로도 날짜가 움직일 수 있다.

2. 2026-08-17 09:00 KST 에 첫 자동 발행(cron)이 돈다.
   안전망 없이 리팩터링을 머지하면, 그 실행이 실패했을 때 cron 자체의
   문제인지 리팩터링 회귀인지 구분할 방법이 없다.

--------------------------------------------------------------------------
today 를 status.json 이 아니라 피드에서 읽는 이유
--------------------------------------------------------------------------
feeds/kr.ics 와 status.json 은 서로 다른 프로세스가 만든다. 워크플로의
"피드 생성" 스텝과 "status.json 생성" 스텝이고(.github/workflows/publish.yml),
각자 자기 시계를 읽는다 — rules/kr/feed.py:361 과 rules/status.py:84.
generated_at 은 그래서 피드에 넘어간 today 와 같은 시계 읽기가 아니다.

더 큰 문제는 커밋 규칙이다. 워크플로는 DTSTAMP 말고 달라진 것이 없으면
feeds/kr.ics 를 git checkout 으로 되돌리고 status.json 만 커밋한다. 내용이
안 바뀐 주(週)에는 status.json 만 갱신되므로, 커밋된 두 파일의 시각은 몇 주씩
벌어진다. 첫 cron(2026-08-17)이 데이터 변경 없이 도는 순간 바로 그렇게 된다.

반면 DTSTAMP 는 피드 자신의 값이고, 그 피드에 넘어간 today 와 같은 _now 하나에서
나온다(rules/kr/feed.py:361 이 _now 를 읽어 :368 에서 today=_now.date(),
dtstamp=_now 로 함께 넘긴다). 그래서 DTSTAMP 의 UTC 날짜가 곧 그 피드의 today 다.
정의상 어긋날 수 없다.

status.json 안에서 today 를 가장 정확히 담은 필드는 feed.range.end 지만,
거기서 today 를 되찾으려면 end.year - YEARS_AHEAD 를 테스트가 다시 적어야 한다.
발행 범위 규칙이 두 군데 존재하게 되므로 쓰지 않는다. status.json 은 대신
아래 test_the_published_status_describes_the_published_feed 가 feed_range() 를
직접 불러 맞춰 본다.

09:00 KST 경계는 걸리지 않는다. today 는 UTC 날짜이고 cron 은 00:00 UTC 인데,
09:00 KST 와 00:00 UTC 는 같은 날짜다. 게다가 피드 출력이 today 에서 보는 것은
연도뿐이라(feed_range), 하루 어긋나도 12-31/01-01 을 건너뛸 때만 결과가 갈린다.
그 경우는 피드에 한 해가 통째로 붙어 내용이 바뀌므로 피드가 반드시 재커밋된다.

--------------------------------------------------------------------------
깨졌을 때 먼저 의심할 것
--------------------------------------------------------------------------
icalendar 버전이다. pyproject.toml 은 icalendar>=6.0 인데 uv.lock 은 7.2.2 로
고정되어 있다. 이 테스트는 라이브러리가 내놓는 속성 순서와 줄 접기(folding)까지
바이트로 못 박으므로, 버전이 올라가면 우리 코드가 멀쩡해도 깨질 수 있다.
uv run 으로 도는 한 lock 을 타서 안 깨지지만, 깨졌을 때 원인을 규칙이나
데이터에서 찾기 시작하면 한참 헤맨다. 먼저 `uv run python -c "import icalendar;
print(icalendar.__version__)"` 를 볼 것.

그 다음이 규칙·데이터 변경이다. rules/ 의 YAML 이나 계산을 건드렸으면 이
테스트는 깨지는 것이 정상이고, 고칠 곳은 코드가 아니라 발행본이다 —
`uv run python -m rules.kr.feed feeds/kr.ics` 와
`uv run python -m rules.status status.json` 을 돌려 함께 커밋할 것.
"""

from __future__ import annotations

import datetime as dt
import json
import re

import pytest

from rules.jp import feed as jp_feed
from rules.kr import feed

# 이 파일은 통째로 커밋된 산출물을 읽는다. 발행 워크플로는 이 마커를 빼고
# 돈다 — 이유는 pyproject.toml 의 markers 설명에 있다.
pytestmark = pytest.mark.published_artifact

# 저장소 뿌리. 여기서 새로 계산하지 않고 feed 쪽 정의를 그대로 쓴다.
# rules/kr/status.py:22 도 같은 식으로 뿌리를 잡는다.
ROOT = feed.FEED_PATH.parents[1]
STATUS_PATH = ROOT / "status.json"

# DTSTAMP 는 UTC 이고 접히지 않는다. 접힌 줄(RFC 5545 의 folding)은 다음 줄이
# 공백으로 시작하는데, 이 속성값은 그 길이에 닿지 않는다.
_DTSTAMP = re.compile(rb"(?m)^DTSTAMP:(\d{8}T\d{6}Z)\r?$")


def _published_feed() -> bytes:
    """커밋된 발행본. 사본을 만들지 않는다 — 이 파일 자체가 골든이다.

    tests/fixtures/ 에 복사본을 두면 골든이 둘이 되고, 발행 워크플로는
    feeds/kr.ics 만 갱신하므로 사본은 반드시 뒤처진다.
    """
    return feed.FEED_PATH.read_bytes()


def _published_status() -> dict:
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))


def _feed_dtstamp(raw: bytes) -> dt.datetime:
    """발행본이 실린 시각. 그 피드를 만든 실행의 시계값이다."""
    stamps = set(_DTSTAMP.findall(raw))
    assert len(stamps) == 1, f"DTSTAMP 가 한 값이 아니다: {sorted(stamps)}"
    value = stamps.pop().decode()
    return dt.datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.UTC)


def test_the_published_feed_carries_one_dtstamp_for_the_whole_run():
    """VEVENT 마다 DTSTAMP 가 있지만 값은 하나여야 한다.

    render() 가 dtstamp 하나를 전 이벤트에 그대로 박기 때문에 성립한다
    (core/ics.py:457-458). 이 성질이 깨지면 아래 두 테스트가 "그 피드의 today"
    를 정할 수 없다 — 어느 DTSTAMP 를 골라야 하는지 알 수 없어진다.

    그래서 여기서 먼저 확인한다. 아래 테스트가 애매한 값으로 통과하는 것보다
    이 자리에서 멈추는 편이 낫다.
    """
    raw = _published_feed()
    assert raw.count(b"BEGIN:VEVENT") == len(_DTSTAMP.findall(raw)), (
        "VEVENT 수와 DTSTAMP 수가 다르다. 접혔거나 빠진 것이 있다."
    )
    _feed_dtstamp(raw)  # 값이 하나인지는 여기서 단언한다


def test_the_published_feed_is_reproducible_from_the_committed_inputs():
    """커밋된 feeds/kr.ics 가 지금 코드·데이터로 바이트까지 다시 나오는가.

    입력을 셋 다 발행본 자신에게서 얻는다. 날짜나 시각을 상수로 적지 않는다 —
    적으면 연도가 넘어가는 순간 이 테스트만 깨지고, 그건 회귀가 아니라 테스트가
    낡은 것이다.

        today     DTSTAMP 의 UTC 날짜. 그 피드를 만든 실행의 today 와 같은
                  _now 에서 나온다(rules/kr/feed.py:361, :368).
        dtstamp   DTSTAMP 그대로.
        previous  발행본 자신. 다음 발행이 읽을 이전본이 바로 이 파일이므로
                  (rules/kr/feed.py:346), "다시 발행해도 그대로"까지 함께
                  못 박힌다. SEQUENCE 가 움직이면 여기서 걸린다.

    previous 로 골든 자신을 넘기므로, SEQUENCE 에 대해 여기서 확인되는 것은
    "무변경 재발행이 이전 값을 보존하는가" 까지다. 신규 이벤트의 최초 값이나
    날짜가 바뀌었을 때의 증가 규칙은 이 테스트가 덮지 않는다 — 그쪽은
    tests/test_ics.py 의 _sequences 계열이 이전본을 손으로 지어 확인한다.
    이 테스트가 통과한다고 SEQUENCE 규칙 전체가 확인된 것으로 읽지 말 것.

    바이트 비교인 것이 요점이다. 파싱해서 이벤트 집합을 비교하면 UID·SUMMARY 가
    같기만 하면 통과하는데, 구독자에게 나가는 것은 파싱 결과가 아니라 바이트다.
    """
    raw = _published_feed()
    stamp = _feed_dtstamp(raw)

    rebuilt = feed.build(today=stamp.date(), dtstamp=stamp, previous=raw)

    assert rebuilt == raw, (
        "커밋된 feeds/kr.ics 가 지금 코드로 재현되지 않는다.\n"
        f"발행본 {len(raw)} bytes / 재생성 {len(rebuilt)} bytes\n"
        "규칙이나 데이터를 바꿨다면 발행본을 함께 갱신할 것:\n"
        "  uv run python -m rules.kr.feed feeds/kr.ics\n"
        "  uv run python -m rules.status status.json\n"
        "아무것도 안 바꿨는데 깨졌다면 icalendar 버전을 먼저 볼 것 "
        "(이 파일의 모듈 docstring 참조)."
    )


def test_the_published_jp_feed_is_reproducible_from_the_committed_inputs():
    """커밋된 feeds/jp.ics 가 지금 코드·데이터로 바이트까지 다시 나오는가.

    kr 재현 테스트와 같은 구조인데 입력이 하나 적다 — jp 의 build() 는 today
    를 받지 않는다. 발행 범위가 상수라 시계가 관여하지 않기 때문이다
    (rules/jp/feed.py 의 publish() docstring). 그래서 DTSTAMP 에서 꺼내는
    것은 dtstamp 하나다.

    previous 로 골든 자신을 넘기는 의미와 바이트 비교인 이유는 위 kr 테스트의
    docstring 에 있다 — 같은 논리가 그대로 적용된다.
    """
    raw = jp_feed.FEED_PATH.read_bytes()
    stamp = _feed_dtstamp(raw)

    rebuilt = jp_feed.build(dtstamp=stamp, previous=raw)

    assert rebuilt == raw, (
        "커밋된 feeds/jp.ics 가 지금 코드로 재현되지 않는다.\n"
        f"발행본 {len(raw)} bytes / 재생성 {len(rebuilt)} bytes\n"
        "규칙이나 데이터를 바꿨다면 발행본을 함께 갱신할 것:\n"
        "  uv run python -m rules.jp.feed feeds/jp.ics\n"
        "아무것도 안 바꿨는데 깨졌다면 icalendar 버전을 먼저 볼 것 "
        "(이 파일의 모듈 docstring 참조)."
    )


def test_the_published_status_describes_the_published_feed():
    """status.json 이 그 옆의 feeds/kr.ics 를 실제로 설명하고 있는가.

    status.json 은 랜딩 페이지가 읽고 밖으로 나가는 값이다. 피드와 어긋나면
    저장소가 자기 산출물에 대해 틀린 말을 하고 있는 것이 된다.

    ----------------------------------------------------------------------
    두 파일의 시각이 벌어지는 것은 정상이다
    ----------------------------------------------------------------------
    generated_at 과 DTSTAMP 를 비교하지 않는다. 내용이 안 바뀐 발행에서
    워크플로가 피드를 되돌리고 status.json 만 커밋하므로, 둘의 시각은 몇 주씩
    벌어지는 것이 설계대로다(모듈 docstring 참조).

    벌어져도 어긋나지 않는 것만 본다. 발행 범위는 today 에서 연도만 보고,
    이벤트 수와 잠정 건수는 규칙·데이터에서 나온다. 그래서 같은 해 안에서는
    시각이 얼마나 벌어지든 값이 같아야 한다.

    ----------------------------------------------------------------------
    범위 규칙을 여기서 다시 적지 않는다
    ----------------------------------------------------------------------
    feed_range() 를 직접 부른다. today.year + YEARS_AHEAD 를 테스트가 계산하면
    규칙이 두 군데 존재하게 되고, 규칙을 바꿀 때 한 쪽만 고쳐도 통과한다.
    """
    raw = _published_feed()
    status = _published_status()
    today = _feed_dtstamp(raw).date()

    start, end = feed.feed_range(today)
    assert status["feeds"]["kr"]["range"] == {"start": start.isoformat(), "end": end.isoformat()}, (
        "status.json 의 발행 범위가 피드의 것과 다르다. "
        "둘이 서로 다른 해에 만들어졌는지 확인할 것."
    )

    assert status["feeds"]["kr"]["path"] == str(feed.FEED_PATH.relative_to(ROOT))
    assert status["feeds"]["kr"]["events"] == raw.count(b"BEGIN:VEVENT")
    assert status["feeds"]["kr"]["provisional_events"] == raw.count(b"STATUS:TENTATIVE")


@pytest.mark.parametrize("field", ["events", "provisional_events"])
def test_the_status_counts_are_not_trivially_zero(field):
    """위 비교가 0 == 0 으로 통과하는 것을 막는다.

    피드가 비었거나 카운트 문자열이 바뀌면 양쪽이 나란히 0 이 되어 어긋남이
    안 보인다. 실제 값이 있다는 것을 따로 못 박는다.
    """
    assert _published_status()["feeds"]["kr"][field] > 0


def test_the_published_status_describes_the_published_jp_feed():
    """status.json 의 feeds.jp 가 그 옆의 feeds/jp.ics 를 실제로 설명하는가.

    kr 검사와 같은 단언인데 범위만 다르게 얻는다 — jp 의 발행 범위는
    feed_range(today) 가 아니라 상수다. 상수를 여기 다시 적지 않고 소스
    모듈의 값을 그대로 쓴다(범위 규칙을 두 군데 만들지 않는다는 원칙은
    kr 검사의 docstring 과 같다).
    """
    raw = jp_feed.FEED_PATH.read_bytes()
    status = _published_status()

    assert status["feeds"]["jp"]["range"] == {
        "start": jp_feed.RANGE_START.isoformat(),
        "end": jp_feed.RANGE_END.isoformat(),
    }
    assert status["feeds"]["jp"]["path"] == str(jp_feed.FEED_PATH.relative_to(ROOT))
    assert status["feeds"]["jp"]["events"] == raw.count(b"BEGIN:VEVENT")
    assert status["feeds"]["jp"]["provisional_events"] == raw.count(b"STATUS:TENTATIVE")


def test_the_jp_status_counts_match_the_spec():
    """jp 의 0 == 0 방지는 kr 과 반씩 다르다.

    events 는 kr 처럼 실제 값이 있어야 한다. provisional_events 는 반대로
    0 이 사양이다(tests/test_jp_feed.py 의 잠정 표시 절) — 위 비교가 0 == 0
    으로 통과하는 것이 맞고, 여기서는 그 0 이 사양임을 못 박는다.
    """
    jp = _published_status()["feeds"]["jp"]
    assert jp["events"] > 0
    assert jp["provisional_events"] == 0
