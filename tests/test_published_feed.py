"""커밋된 feeds/*.ics 가 지금 코드와 데이터로 재현되는가.

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

KST 날짜 경계는 걸리지 않는다. cron 은 일·화·목 21:23 UTC 라 KST 로는 다음 날
06:23 이고 UTC 날짜와 KST 날짜가 다르지만, 발행 경로는 KST 를 읽지 않는다 —
today 는 UTC 시계(각 feed.py __main__ 의 datetime.now(UTC))의 날짜이고 이
테스트도 DTSTAMP 의 UTC 날짜를 today 로 쓴다. 같은 UTC 값끼리 맞춘다. 게다가
피드 출력이 today 에서 보는 것은 연도뿐이라(feed_range), 12-31/01-01 을 건너뛸
때만 결과가 갈린다. 그 경우는 피드에 한 해가 통째로 붙어 내용이 바뀌므로
피드가 반드시 재커밋된다.

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

--------------------------------------------------------------------------
피드 목록은 rules/ 스캔에서 온다
--------------------------------------------------------------------------
피드마다 함수를 손으로 복제하던 구조에서는 새 피드를 여기 안 더해도 아무것도
빨개지지 않았다 — 그 피드만 재현성·status 서술·UID 배타 검사에서 조용히
빠졌다(docs/holiday_15.md §5). 그래서 피드 목록을 rules/ 아래 feed.py 를 가진
패키지에서 뽑아 parametrize 한다. 피드를 늘리면 이 파일을 손대지 않아도
검사에 들어온다.

목록의 단일 공급원은 publish.yml 의 FEEDS 다(DESIGN.md "피드 추가" 절). 그래도
여기서 워크플로를 파싱하지 않는 것은 rules/ 스캔이 더 단순하고, 둘이 같은
집합이라는 것은 tests/test_feed_set.py 가 이미 고정하기 때문이다 — 어긋나면
저쪽이 빨개진다.

피드마다 다른 것은 리터럴로 적지 않고 모듈이 말하게 한다. build() 가 today 를
받는지는 시그니처에서, 발행 범위가 feed_range() 인지 상수인지는 속성 유무에서
읽는다. 리터럴로 남긴 것은 셋뿐이다 — kr 의 잠정 건수가 0 이 아니라는 것,
jp 의 잠정 건수가 0 이라는 것, 독일 계열의 잠정 건수가 0 이라는 것. 잠정
유무는 피드의 데이터 성격이지 피드를 늘릴 때 따라 늘려야 할 것이 아니라서
이름 접두사로 자동 판별하지 않는다(해당 테스트의 주석).
"""

from __future__ import annotations

import datetime as dt
import importlib
import inspect
import json
import re
from pathlib import Path

import pytest

from rules.kr import feed

# 이 파일은 통째로 커밋된 산출물을 읽는다. 발행 워크플로는 이 마커를 빼고
# 돈다 — 이유는 pyproject.toml 의 markers 설명에 있다.
pytestmark = pytest.mark.published_artifact

# 저장소 뿌리. 여기서 새로 계산하지 않고 feed 쪽 정의를 그대로 쓴다.
# rules/kr/status.py:22 도 같은 식으로 뿌리를 잡는다.
ROOT = feed.FEED_PATH.parents[1]
STATUS_PATH = ROOT / "status.json"
RULES_DIR = ROOT / "rules"

# 피드 코드 전수. tests/test_feed_set.py 의 _rules_packages 와 같은 조건이다 —
# 저쪽은 집합이 FEEDS 와 같은지를, 여기는 그 집합의 각 발행본을 본다.
FEED_CODES = sorted(
    p.name for p in RULES_DIR.iterdir() if p.is_dir() and (p / "feed.py").is_file()
)
assert FEED_CODES, "rules/ 에서 피드 패키지를 하나도 찾지 못했다"

# DTSTAMP 는 UTC 이고 접히지 않는다. 접힌 줄(RFC 5545 의 folding)은 다음 줄이
# 공백으로 시작하는데, 이 속성값은 그 길이에 닿지 않는다.
_DTSTAMP = re.compile(rb"(?m)^DTSTAMP:(\d{8}T\d{6}Z)\r?$")


def _module(code: str):
    return importlib.import_module(f"rules.{code}.feed")


def _published_feed() -> bytes:
    """커밋된 kr 발행본. 사본을 만들지 않는다 — 이 파일 자체가 골든이다.

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
    (core/ics.py:457-458). 이 성질이 깨지면 아래 테스트가 "그 피드의 today"
    를 정할 수 없다 — 어느 DTSTAMP 를 골라야 하는지 알 수 없어진다.

    그래서 여기서 먼저 확인한다. 아래 테스트가 애매한 값으로 통과하는 것보다
    이 자리에서 멈추는 편이 낫다. kr 로 본다 — 다른 피드도 같은 render()
    를 타고, _feed_dtstamp 가 피드마다 값이 하나인지는 따로 단언한다.
    """
    raw = _published_feed()
    assert raw.count(b"BEGIN:VEVENT") == len(_DTSTAMP.findall(raw)), (
        "VEVENT 수와 DTSTAMP 수가 다르다. 접혔거나 빠진 것이 있다."
    )
    _feed_dtstamp(raw)  # 값이 하나인지는 여기서 단언한다


@pytest.mark.parametrize("code", FEED_CODES)
def test_the_published_feed_is_reproducible_from_the_committed_inputs(code):
    """커밋된 feeds/<code>.ics 가 지금 코드·데이터로 바이트까지 다시 나오는가.

    입력을 발행본 자신에게서 얻는다. 날짜나 시각을 상수로 적지 않는다 —
    적으면 연도가 넘어가는 순간 이 테스트만 깨지고, 그건 회귀가 아니라 테스트가
    낡은 것이다.

        today     DTSTAMP 의 UTC 날짜. 그 피드를 만든 실행의 today 와 같은
                  _now 에서 나온다(rules/kr/feed.py:361, :368). build() 가
                  today 를 받지 않는 피드(jp — 발행 범위가 상수라 시계가
                  관여하지 않는다)에는 넘기지 않는다. 받는지는 시그니처가
                  말한다.
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
    module = _module(code)
    raw = module.FEED_PATH.read_bytes()
    stamp = _feed_dtstamp(raw)

    kwargs = {"dtstamp": stamp, "previous": raw}
    if "today" in inspect.signature(module.build).parameters:
        kwargs["today"] = stamp.date()
    rebuilt = module.build(**kwargs)

    assert rebuilt == raw, (
        f"커밋된 feeds/{code}.ics 가 지금 코드로 재현되지 않는다.\n"
        f"발행본 {len(raw)} bytes / 재생성 {len(rebuilt)} bytes\n"
        "규칙이나 데이터를 바꿨다면 발행본을 함께 갱신할 것:\n"
        f"  uv run python -m rules.{code}.feed feeds/{code}.ics\n"
        "  uv run python -m rules.status status.json\n"
        "아무것도 안 바꿨는데 깨졌다면 icalendar 버전을 먼저 볼 것 "
        "(이 파일의 모듈 docstring 참조)."
    )


def _expected_range(module, today: dt.date) -> dict:
    """status.json 의 range 가 어디서 와야 하는가 — 모듈이 말한다.

    feed_range(today) 가 있으면 그것이고(kr 형), 없으면 상수 RANGE_START·
    RANGE_END 다(jp 형). 범위 규칙을 여기서 다시 적지 않는다 — today.year +
    YEARS_AHEAD 를 테스트가 계산하면 규칙이 두 군데 존재하게 되고, 규칙을 바꿀
    때 한 쪽만 고쳐도 통과한다.
    """
    if hasattr(module, "feed_range"):
        start, end = module.feed_range(today)
    else:
        start, end = module.RANGE_START, module.RANGE_END
    return {"start": start.isoformat(), "end": end.isoformat()}


@pytest.mark.parametrize("code", FEED_CODES)
def test_the_published_status_describes_the_published_feed(code):
    """status.json 의 feeds.<code> 가 그 옆의 feeds/<code>.ics 를 실제로
    설명하고 있는가.

    status.json 은 랜딩 페이지가 읽고 밖으로 나가는 값이다. 피드와 어긋나면
    저장소가 자기 산출물에 대해 틀린 말을 하고 있는 것이 된다.

    generated_at 과 DTSTAMP 는 비교하지 않는다. 내용이 안 바뀐 발행에서
    워크플로가 피드를 되돌리고 status.json 만 커밋하므로, 둘의 시각은 몇 주씩
    벌어지는 것이 설계대로다(모듈 docstring). 벌어져도 어긋나지 않는 것만
    본다 — 발행 범위는 today 에서 연도만 보고, 이벤트 수와 잠정 건수는
    규칙·데이터에서 나온다.

    events > 0 은 전 피드에 건다. 피드가 비었거나 카운트 문자열이 바뀌면
    양쪽이 나란히 0 이 되어 어긋남이 안 보인다.
    """
    module = _module(code)
    raw = module.FEED_PATH.read_bytes()
    status = _published_status()["feeds"][code]
    today = _feed_dtstamp(raw).date()

    assert status["range"] == _expected_range(module, today), (
        f"status.json 의 {code} 발행 범위가 피드의 것과 다르다. "
        "둘이 서로 다른 해에 만들어졌는지 확인할 것."
    )
    assert status["path"] == str(module.FEED_PATH.relative_to(ROOT))
    assert status["events"] == raw.count(b"BEGIN:VEVENT")
    assert status["provisional_events"] == raw.count(b"STATUS:TENTATIVE")
    assert status["events"] > 0, f"{code} 의 events 가 0 이다 — 비교가 공허하다"


# 잠정 건수의 사양은 피드마다 다르고, 그것은 데이터의 성격이지 피드를 늘릴 때
# 따라 늘려야 할 것이 아니다. 그래서 위 parametrize 에 넣지 않고 리터럴로
# 남긴다 — 이름 접두사(de_)로 자동 판별하면 독일 계열이 아닌 새 피드의
# 잠정 유무를 아무도 안 보게 된다. 잘못된 자동보다 명시적 수동이 낫다.
# 새 피드의 잠정 사양이 정해지면 여기에 한 줄을 더한다.


def test_the_kr_status_has_provisional_events():
    """kr 의 0 == 0 방지 — 잠정 건수가 실제로 있어야 한다."""
    assert _published_status()["feeds"]["kr"]["provisional_events"] > 0


@pytest.mark.parametrize("code", ["jp", "de", "de_be", "de_bw", "de_by", "de_he", "de_hh",
                                  "de_ni", "de_nw", "de_rp", "de_sh"])
def test_the_status_publishes_no_provisional_events(code):
    """잠정 표시가 사양상 없는 피드 — 위 비교가 0 == 0 으로 통과하는 것이 맞고,
    여기서 그 0 이 사양임을 못 박는다. jp 는 tests/test_jp_feed.py 의 잠정 표시
    절, 독일 계열은 관보 확정분만 싣는다."""
    assert _published_status()["feeds"][code]["provisional_events"] == 0


# UID 값만 본다. 줄 끝이 CRLF 라 $ 앞에 \r 이 남는다.
_UID = re.compile(rb"(?m)^UID:(.+?)\r?$")


def _published_uids(path: Path) -> set:
    uids = set(_UID.findall(path.read_bytes()))
    assert uids, f"{path.name} 에서 UID 를 하나도 읽지 못했다"
    return uids


# kr.ics 와 jp.ics 의 겹침(신정·어린이날 16건)은 의도된 것이다 —
# tests/test_kr_jp_feed.py 의 docstring. 이 한 쌍만 배타에서 뺀다. 그 밖의
# 쌍은 전부 검사 대상이다 — kr_jp 도 포함한다. 겹치면 그때 빨개지는 것이 맞다.
_ALLOWED_OVERLAP = frozenset({frozenset({"kr", "jp"})})


@pytest.mark.parametrize("code", FEED_CODES)
def test_the_published_feed_shares_no_uid_with_the_other_published_feeds(code):
    """발행된 feeds/<code>.ics 의 UID 가 다른 발행본의 어떤 UID 와도 겹치지
    않는가.

    UID 는 영구값이다. 여러 피드를 함께 구독한 캘린더에서 같은 UID 는 서로를
    덮어쓴다. build() 가 지금 내놓는 값이 아니라 양쪽 다 커밋된 실파일을
    읽는다 — 구독자에게 나간 것은 build() 결과가 아니라 파일이다.

    독일 주 피드는 de.ics 와 전국 공통 9 건이 같은 날 같은 항목이라, token
    접두사(de_be- 등)가 없으면 반드시 겹친다. 그 접두사가 유일한 방벽이다.
    """
    ours = _published_uids(_module(code).FEED_PATH)
    for other in FEED_CODES:
        if other == code or frozenset({code, other}) in _ALLOWED_OVERLAP:
            continue
        shared = ours & _published_uids(_module(other).FEED_PATH)
        assert not shared, (
            f"feeds/{code}.ics 와 feeds/{other}.ics 가 UID 를 공유한다 "
            f"({len(shared)}건): {sorted(u.decode() for u in shared)[:5]}"
        )
