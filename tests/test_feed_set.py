"""피드 코드 집합은 네 지점에서 같아야 한다.

    publish.yml 의 FEEDS         발행 워크플로가 도는 목록 — 여기 없으면 자동 발행에서 빠진다   ← 허브
    rules/<코드>/feed.py         규칙 패키지 — 코드가 있어야 만들 수 있다
    rules/status.py 의 등록      status.json 에 실리는 목록 — 여기 없으면 상태가 보고되지 않는다
    feeds/<코드>.ics             발행본 — 구독자가 실제로 받는 것

넷은 손으로 따로 관리된다. 피드를 하나 늘릴 때 한 곳을 빠뜨리면 나머지는
전부 정상으로 보이면서 그 피드만 조용히 빠진다 — FEEDS 에서 빠지면 발행본은
커밋된 채로 영원히 재발행되지 않고, rules/ 에만 있으면 아무 데도 나타나지
않는다. 이 파일은 넷이 같은 집합을 드는지를 FEEDS 를 허브로 놓고 양방향으로
본다. FEEDS 가 허브인 것은 그것이 피드 목록의 단일 공급원이기 때문이다
(DESIGN.md "피드 추가" 절, publish.yml 의 env 주석). 집합 동치는 추이적이라
허브 하나면 넷이 전부 묶인다.

마커 — 둘은 없고 하나는 있다
---------------------------

rules/ 와 rules/status.py 는 발행의 **입력**이다. 발행 run 이 자기 입력의
누락을 스스로 잡으려면 그 둘의 비교가 발행 run 에서도 돌아야 한다. 그래서
마커가 없고, 그만큼 publish.yml 이 도는 테스트 집합이 넓어진다 — 둘 중 하나가
빨개지면 발행이 멈춘다. 의도한 것이다.

feeds/ 는 **산출물**이다. 그 비교는 published_artifact 마커 뒤에 둔다 —
test_landing·test_readme 의 집합 비교(feeds/ ↔ 랜딩 feed-data ↔ status.json,
feeds/ ↔ README 구독 표)가 같은 마커 뒤에 있는 것과 같은 이유다.

feeds/ 를 발행 run 검사에서 뺀 것은 성격 정리가 아니라 교착을 피하기 위해서다.
rules/·FEEDS·status.py 를 갖춘 새 피드가 발행본 없이 main 에 들어오면(커밋
스텝이 "HEAD 에 없음 = 첫 발행" 으로 다루는, 워크플로가 지원하는 경로다),
발행 run 은 테스트 스텝을 피드 생성 스텝보다 먼저 돈다. 그 자리에서
feeds/ 비교가 빨개지면 생성 스텝에 닿지 못해 그 피드는 영원히 첫 발행이
되지 않는다. 산출물 검사는 산출물이 만들어진 뒤에 도는 ci.yml 의 몫이다.

feeds/ 를 비교하지만 발행본의 내용은 읽지 않는다. 파일 이름만 센다.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import pytest

from rules import status

ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = ROOT / "rules"
FEEDS_DIR = ROOT / "feeds"
PUBLISH_YML = ROOT / ".github" / "workflows" / "publish.yml"

# FEEDS 는 publish.yml 의 jobs.<job>.env 블록에 한 줄로 산다. 공백으로 나뉜
# 코드 목록이고 셸의 for 문이 그대로 돈다. 그 줄만 잡는다 — 셸 본문에서
# $FEEDS 를 쓰는 줄은 콜론이 없어 걸리지 않는다.
FEEDS_LINE = re.compile(r"^\s*FEEDS:\s*(.+?)\s*$", re.MULTILINE)

# status() 는 시계를 인자로 받는다. 여기서 보는 것은 feeds 의 키 집합이지
# 날짜가 아니라, 값이 무엇이든 결과가 같다 — 그래서 고정값이다.
# test_pipeline 도 같은 날짜를 쓰지만 거기서는 그 날짜가 "저장소가 주장하는
# 상태" 의 기준일이라 의미가 다르다. 같은 값·다른 의미는 합치지 않는다.
TODAY = dt.date(2026, 8, 10)
DTSTAMP = dt.datetime(2026, 8, 10, 0, 0, 0, tzinfo=dt.UTC)


def _publish_feeds() -> set[str]:
    text = PUBLISH_YML.read_text(encoding="utf-8")
    matches = FEEDS_LINE.findall(text)
    assert len(matches) == 1, f"publish.yml 에 FEEDS: 줄이 {len(matches)}개다(1개여야 한다)"
    codes = matches[0].split()
    assert len(codes) == len(set(codes)), f"FEEDS 에 중복이 있다: {codes}"
    return set(codes)


def _rules_packages() -> set[str]:
    """rules/ 아래 feed.py 를 가진 패키지 이름. __pycache__ 같은 것은 feed.py
    가 없어 걸리지 않는다."""
    return {p.name for p in RULES_DIR.iterdir() if p.is_dir() and (p / "feed.py").is_file()}


def _status_feeds() -> set[str]:
    return set(status.status(today=TODAY, dtstamp=DTSTAMP)["feeds"])


def _published_feeds() -> set[str]:
    return {p.stem for p in FEEDS_DIR.glob("*.ics")}


def _explain(name: str, got: set[str], hub: set[str]) -> str:
    """양쪽 차집합을 모두 낸다. 메시지만 읽고 어느 지점에 무엇이 더 있고
    덜 있는지가 갈려야 한다."""
    return (
        f"{name} 의 피드 집합이 publish.yml FEEDS 와 다르다.\n"
        f"  {name} 에만 있음 (FEEDS 에 없음): {sorted(got - hub)}\n"
        f"  FEEDS 에만 있음 ({name} 에 없음): {sorted(hub - got)}"
    )


def test_every_rules_package_is_in_feeds_and_vice_versa():
    # rules/ 에만 있는 패키지는 고아다 — 어디에도 등록되지 않아 아무것도
    # 깨뜨리지 않고 아무것도 만들지 않는다. FEEDS 에만 있는 코드는 생성
    # 스텝이 rules.<코드>.feed 를 못 찾아 발행 전체를 깨뜨린다.
    got = _rules_packages()
    hub = _publish_feeds()
    assert got == hub, _explain("rules/", got, hub)


def test_the_status_registry_matches_feeds():
    # rules/status.py 는 나라별 status 모듈을 import 해 리터럴로 등록한다.
    # 리터럴을 읽지 않고 함수를 실행해 키를 본다 — 등록 구조가 바뀌어도
    # 이 테스트는 살아남아야 한다. 여기서 빠진 피드는 발행은 되면서
    # status.json 에 실리지 않는다.
    got = _status_feeds()
    hub = _publish_feeds()
    assert got == hub, _explain("rules/status.py", got, hub)


@pytest.mark.published_artifact
def test_the_published_feeds_match_feeds():
    # FEEDS 에서 빠진 발행본은 커밋된 채로 영원히 재발행되지 않는다. 규칙을
    # 바꿔도 낡은 파일이 그대로 서빙된다. 발행본이 없는 코드는 아직 첫 발행
    # 전이거나 발행이 깨진 것이다 — 어느 쪽이든 ci.yml 이 볼 일이고, 발행
    # run 은 보지 않는다(모듈 docstring 의 교착).
    got = _published_feeds()
    hub = _publish_feeds()
    assert got == hub, _explain("feeds/", got, hub)
