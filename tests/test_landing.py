"""랜딩(index.html) 구독 절의 피드 목록은 데이터가 이끈다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    피드를 하나 늘릴 때 랜딩에서 손대는 곳은 feed-data 블록의 한 줄뿐이다.

구독 절의 피드 줄은 마크업을 손으로 반복해 만들어졌다. 피드마다 HTML 세
조각(라벨·설명·조작줄), FEED_URL 상수 하나, wireFeed 호출 하나 — 독일 주별
피드가 다섯 줄이 되는 시점(#52)에 이 구조는 확장 부담이 됐고, holiday_14 §5
는 11피드를 넘는 확장 앞에 데이터 주도 렌더링을 필수로 남겼다. SH 가 그 다음
순서다.

이제 피드 목록은 index.html 안의 JSON 블록(id="feed-data") 이 정의하고
스크립트가 그린다. 여기서는 그 블록이 저장소의 다른 두 목록 — 발행본
feeds/*.ics 와 status.json 의 feeds 키 — 과 어긋나지 않는지를 본다. 피드를
rules/ 에 추가하고 발행본을 커밋하면서 랜딩 줄을 빠뜨리면 여기서 걸린다.

--------------------------------------------------------------------------
왜 바깥 두 목록과 비교하는가
--------------------------------------------------------------------------
피드의 정체는 세 곳이 갖고 있었다: rules/<피드>/ 패키지, feeds/<피드>.ics
발행본, 랜딩의 마크업. 앞의 둘은 rules/status.py 와 tests/test_published_feed.py
가 이미 서로 묶고 있다. 랜딩만 아무것과 묶여 있지 않았다 — 마크업이 맞는지
확인하는 방법이 눈으로 읽는 것뿐이었다. 세 번째 목록을 앞의 둘에 묶는 것이
이 테스트다.

--------------------------------------------------------------------------
주명은 왜 feed.py 에서 가져오는가
--------------------------------------------------------------------------
목록만 묶으면 줄의 존재는 보장되지만 줄에 적힌 글자는 보장되지 않는다. 주명은
이미 rules/de_<주>/feed.py 의 CALNAME·LAND_NAME 이 갖고 있고, 발행본의
X-WR-CALNAME 과 DESCRIPTION 첫 줄이 거기서 나온다. 랜딩의 label·desc 는 그
세 번째 사본이다.

사본인 이상 어긋날 수 있고, 어긋나면 구독 버튼에 적힌 이름과 구독한 뒤
캘린더에 뜨는 이름이 달라진다. 그래서 여기서는 문구의 존재가 아니라 유도식을
못 박는다 — 진실 공급원은 feed.py 다.

--------------------------------------------------------------------------
published_artifact 마커
--------------------------------------------------------------------------
이 테스트는 커밋된 산출물(index.html, status.json, feeds/)을 읽는다. 규칙을
바꾸고 발행본·랜딩을 갱신하기 전의 찰나에 깨지는 것이 정상이다. 마커의
정의 그대로라 발행 워크플로에서는 제외되고 PR 워크플로(ci.yml)가 전부
돌린다.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

import pytest

from landing import render as landing_render

pytestmark = pytest.mark.published_artifact

ROOT = Path(__file__).resolve().parents[1]

# 언어별 페이지. 목록은 landing/render.py 가 locales/ 에서 스캔한 것과 같다 —
# 언어를 늘리면 여기 손대지 않아도 그 페이지가 검사에 든다.
LANGS = landing_render.languages()
ROOT_LANG = landing_render.ROOT_LANG

# 언어와 무관한 검사는 페이지 전부를 본다. 문구를 보는 검사는 ko 만 본다 —
# 각 함수의 docstring 참조.
every_page = pytest.mark.parametrize("lang", LANGS)
FEEDS_DIR = ROOT / "feeds"
STATUS = ROOT / "status.json"
CNAME = ROOT / "CNAME"

# 구독 절의 피드 목록. 스크립트(type 을 붙였으므로 실행되지 않는다) 안의
# JSON 이라 regex 로 뽑는다.
DATA_BLOCK = re.compile(
    r'<script type="application/json" id="feed-data">\s*(.*?)\s*</script>',
    re.DOTALL,
)

# CLAUDE.md·DESIGN.md 이 약속한 영구 구독 주소. site_base 조립 규칙의 기준점.
CANONICAL_KR_URL = "https://holidays.lunalism.com/feeds/kr.ics"


def _html_and_data(lang: str = ROOT_LANG):
    page = landing_render.output_path(lang)
    html = page.read_text(encoding="utf-8")
    m = DATA_BLOCK.search(html)
    assert m, f'{page.relative_to(ROOT)} 에 id="feed-data" JSON 블록이 없다'
    return html, json.loads(m.group(1))


def _rows(data):
    """그룹과 아코디언을 펴서 (피드 dict, 아코디언 안인가) 를 순서대로."""
    for group in data["groups"]:
        for feed in group["feeds"]:
            yield feed, False
        for feed in group.get("accordion", {}).get("feeds", []):
            yield feed, True


@every_page
def test_the_page_still_reads_status_json(lang):
    # 이 리팩터링이 건드리는 것은 구독 절뿐이어야 한다. 상태 영역의 fetch 가
    # 그대로 있는지를 같이 못 박는다.
    html, _ = _html_and_data(lang)
    assert 'fetch("/status.json"' in html


@every_page
def test_every_published_feed_has_a_row_and_vice_versa(lang):
    # 양방향으로 잡는다. 발행본이 있는데 줄이 없으면 구독 주소를 건네주는
    # 페이지가 거짓말을 하는 것이고, 줄이 있는데 발행본이 없으면 죽은 주소를
    # 건네주는 것이다.
    _, data = _html_and_data(lang)
    listed = {feed["file"] for feed, _ in _rows(data)}
    published = {path.name for path in FEEDS_DIR.glob("*.ics")}
    assert listed == published


@every_page
def test_feed_rows_match_status_json_feed_keys(lang):
    _, data = _html_and_data(lang)
    keys = [feed["key"] for feed, _ in _rows(data)]
    assert len(keys) == len(set(keys)), "피드 키가 중복된다"
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    assert set(keys) == set(status["feeds"])


@every_page
def test_the_kr_subscription_url_is_derived_from_the_cname(lang):
    # URL 은 페이지 안에서 site_base + "feeds/" + file 로 조립된다. 그 규칙이
    # CNAME(서빙 도메인) 과 어긋나면 절반의 구독자에게 죽은 주소를 준다.
    # 기준점은 kr — CLAUDE.md·DESIGN.md 이 약속한 영구값과 글자 하나까지
    # 같아야 한다.
    _, data = _html_and_data(lang)
    assert data["site_base"] == f"https://{CNAME.read_text(encoding='utf-8').strip()}/"
    kr = next(feed for feed, _ in _rows(data) if feed["key"] == "kr")
    assert data["site_base"] + "feeds/" + kr["file"] == CANONICAL_KR_URL


@every_page
def test_state_feeds_live_in_the_accordion_and_de_does_not(lang):
    # de_ 접두사 피드는 아코디언 안에만, 전국 피드 de 는 아코디언 밖 나라별
    # 그룹의 한 줄로만 선다. SH 를 추가할 때 이 구조가 스스로 유지된다.
    _, data = _html_and_data(lang)
    rows = list(_rows(data))
    de_state_keys = {feed["key"] for feed, _ in rows if feed["key"].startswith("de_")}
    in_accordion = {feed["key"] for feed, accordion in rows if accordion}
    assert in_accordion == de_state_keys
    de_rows = [(feed, accordion) for feed, accordion in rows if feed["key"] == "de"]
    assert len(de_rows) == 1
    assert de_rows[0][1] is False


@every_page
def test_labels_and_descriptions_are_present(lang):
    _, data = _html_and_data(lang)
    for feed, _ in _rows(data):
        assert feed["file"].endswith(".ics"), feed
        assert isinstance(feed["label"], str) and feed["label"].strip(), feed
        assert isinstance(feed["desc"], str) and feed["desc"].strip(), feed


def test_state_labels_and_descs_are_derived_from_the_feed_modules():
    """ko 만 본다. 유도식 자체는 이제 언어 중립이다 — locale 의 label·desc 틀에
    land_lang 이 고른 주 이름을 넣는다(ko→LAND_NAME, de→LAND_NAME_DE). ko 전용인
    이유는 유도식이 아니라 **기대값**이다: 아래 두 리터럴이 한국어라서 ja 에
    그대로 쓸 수 없다.

    ja 의 기대값을 locale 에서 만들어 every_page 로 옮기지 않는다. 그러면 locale
    을 locale 로 검사하는 동어반복이 되고, 이 테스트가 지키려는 명제 — 주 이름은
    feed.py 에서 온다 — 를 오히려 놓친다. ja 쪽은 그 명제를 다른 각도로 지킨다:
    locale 의 ko label 틀이 CALNAME 과 같은 값을 내는 관계를
    test_the_korean_label_template_matches_the_calname 이 고정한다."""
    # 위 테스트는 문구가 비어 있지 않은지만 본다. 여기서는 그 문구가 어디서
    # 왔는지를 본다 — 주 피드의 label·desc 는 지어내는 것이 아니라
    # rules/de_<주>/feed.py 에서 유도되는 것이다.
    #
    #     label == CALNAME 에서 " 공휴일" 을 뗀 것
    #     desc  == "전국 공통에 {LAND_NAME} 주법 공휴일을 더한 상위집합"
    #
    # 주를 늘릴 때 블록에 새 줄을 쓰는 사람이 주명을 옮겨 적다 틀리면 여기서
    # 걸린다. 목록 일치(위 두 테스트)는 줄이 있는지를, 이 테스트는 줄에 뭐라고
    # 적혀 있는지를 맡는다.
    _, data = _html_and_data()
    state_rows = [feed for feed, _ in _rows(data) if feed["key"].startswith("de_")]
    assert state_rows, "주 피드 줄이 하나도 없다"
    for feed in state_rows:
        module = importlib.import_module(f"rules.{feed['key']}.feed")
        assert feed["label"] == module.CALNAME.removesuffix(" 공휴일"), feed["key"]
        expected_desc = f"전국 공통에 {module.LAND_NAME} 주법 공휴일을 더한 상위집합"
        assert feed["desc"] == expected_desc, feed["key"]


DE_STATE_CODES = sorted(c for c in landing_render.feed_codes() if c.startswith("de_"))

# 독일어 주 이름을 여기서 고정한다. feed.py 의 LAND_NAME_DE 가 바뀌면 여기가 먼저
# 깨진다 — tests/test_de_scope.py 의 LAND_NAMES 와 같은 방식이고, 자리만 다르다.
# 그 파일의 명제는 "피드에 나가는 것"(scope·DESCRIPTION)이고 LAND_NAME_DE 는 피드에
# 나가지 않는다. 소비처가 랜딩이므로 랜딩 테스트가 든다.
#
# 표기 근거는 독일 기본법 전문(rules/de/feed.py 의 LAND_NAME_DE 절). 아홉 모듈에
# 손으로 옮겨 적은 값이라 오타가 그대로 랜딩에 나간다 — Nordrhein-Westphalen 처럼
# 한 글자 틀린 것을 잡는 것이 여기의 일이다.
LAND_NAMES_DE = {
    "de_be": "Berlin",
    "de_bw": "Baden-Württemberg",
    "de_by": "Bayern",
    "de_he": "Hessen",
    "de_hh": "Hamburg",
    "de_ni": "Niedersachsen",
    "de_nw": "Nordrhein-Westfalen",
    "de_rp": "Rheinland-Pfalz",
    "de_sh": "Schleswig-Holstein",
}


@pytest.mark.parametrize("code", DE_STATE_CODES)
def test_german_land_names_are_fixed(code):
    module = importlib.import_module(f"rules.{code}.feed")
    assert module.LAND_NAME_DE == LAND_NAMES_DE[code]



@pytest.mark.parametrize("code", DE_STATE_CODES)
def test_the_korean_label_template_matches_the_calname(code):
    """랜딩의 ko label 이 CALNAME 에서 갈라지지 않게 못 박는다.

    label 은 CALNAME 에서 " 공휴일" 을 떼어 만들던 것이다. 그 방식으로는 한국어
    label 만 낼 수 있어(CALNAME 이 한국어다) locale 의 "독일·{land}" 틀로 바뀌었고,
    그 순간 랜딩 label 과 CALNAME 을 잇는 끈이 끊어졌다 — 둘이 갈라져도 아무
    테스트가 깨지지 않는다. 갈라지면 구독 버튼의 이름과 구독 뒤 캘린더에 뜨는
    X-WR-CALNAME 이 달라진다(이 파일 머리의 "주명은 왜 feed.py 에서" 절).

    지금 아홉 주 전부 참인 관계라 그대로 단언한다. 새 주를 더하면서 CALNAME 을
    다른 모양으로 적으면(예: "독일 베를린 공휴일") 여기서 걸린다. 리터럴 둘은
    ko.yaml 의 label 틀·label_suffix 와 같은 값이어야 하고, 그 일치는 위
    test_state_labels_and_descs_are_derived_from_the_feed_modules 가 본다."""
    module = importlib.import_module(f"rules.{code}.feed")
    assert module.CALNAME.removesuffix(" 공휴일") == f"독일·{module.LAND_NAME}"


@every_page
def test_the_accordion_is_sorted_by_key(lang):
    # 표시 순서는 등록순이 아니라 key 알파벳순이다. status.json 의 feeds 키
    # 순서(rules/status.py 의 리터럴 = 등록순)와 일부러 갈라 둔 값이라, 아무도
    # 지키지 않으면 다음 주가 그냥 끝에 붙는다. 기계가 읽는 순서와 사람이 훑는
    # 순서는 목적이 다르다 — 등록순은 "언제 추가됐나"를 말할 뿐이다.
    #
    # 멤버십은 test_state_feeds_live_in_the_accordion_and_de_does_not 이 집합으로
    # 본다. 집합은 순서를 잃는다. 순서는 여기서 맡는다.
    _, data = _html_and_data(lang)
    keys = [feed["key"] for feed in data["groups"][0]["accordion"]["feeds"]]
    assert keys == sorted(keys), keys


def test_groups_keep_their_titles():
    """ko 만 본다. 제목 문자열 자체가 한국어 리터럴이라 다른 언어에서는 다른
    문자열이 정상이다. 묶음의 순서(용도별 위계, holiday_10 §5)는 언어 무관이지만
    그것은 landing/layout.yaml 이 들고 있고, 여기서는 ko 문구로 그 순서를 못
    박는다."""
    # 묶음 셋의 순서는 용도별 위계다(holiday_10 §5). 데이터가 이끌게 바뀌어도
    # 이 순서만은 바뀌지 않는다고 못 박는다.
    _, data = _html_and_data()
    assert [group["title"] for group in data["groups"]] == [
        "나라별 전체",
        "한 피드로 합침",
        "겹치지 않는 날만",
    ]
    assert data["groups"][0]["accordion"]["title"] == "독일 주별 피드"


@every_page
def test_no_per_feed_markup_remains(lang):
    # 줄마다 id 를 붙이고 상수·호출을 하나씩 쓰던 이전 구조가 돌아오면
    # 피드를 늘릴 때 다시 여섯 군데를 손대게 된다. 대소문자 무시 검색까지
    # 돌린다(AGENTS.md — 소스가 소문자인데 대문자로 찾아 0건으로 믿은
    # 사례가 있다).
    html, _ = _html_and_data(lang)
    assert re.search(r'id="feed-url', html, re.IGNORECASE) is None
    assert "FEED_URL" not in html


@every_page
def test_the_feed_list_is_read_from_the_data_block(lang):
    # 목록이 데이터 블록에서 읽히는지. 블록(script 태그) 도, 읽는 쪽
    # (getElementById) 도 있어야 한다.
    html, data = _html_and_data(lang)
    assert 'id="feed-data"' in html
    assert '$("feed-data")' in html
    # 주별 피드 개수가 마크업에 박혀 있으면 피드를 늘릴 때 그 숫자만 남는다.
    # 개수는 데이터에서 세져야 한다.
    assert re.search(r"주별 피드\s*\(\s*\d", html) is None
    accordion = data["groups"][0]["accordion"]["feeds"]
    assert all(feed["key"].startswith("de_") for feed in accordion)
