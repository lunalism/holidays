"""render 의 입력 계약 — 잘못된 입력이 막히는가.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    landing/render.py 가 든 검사들은 잘못된 locale·템플릿을 생성 시점에
    멈춘다. 그 검사가 조용히 사라지지 않는다.

검사는 여럿이고 한 자리에 모여 있지 않다 — 마커 종류별 값 계약, 복수형 매핑의
형태, 템플릿과 locale 의 양방향 일치, 치환 잔존, script 문맥 이스케이프,
state_feed.land_lang 의 닫힌 집합, 주 피드가 아닌 피드의 desc. 전부 ValueError
로 발행을 멈추는 자리이고, 멈추지 않으면 깨진 페이지가 발행된다.

이 계약들은 PR #92 에서 하나씩 손으로 확인됐다(red 재현). 손으로 한 것은
다음에 누가 리팩터하면 다시 해야 한다. 여기 옮겨 둔다.

--------------------------------------------------------------------------
왜 마커가 없는가
--------------------------------------------------------------------------
다른 두 랜딩 테스트(test_landing.py·test_landing_render.py)는 모듈 수준
published_artifact 다. 커밋된 산출물 — index.html·feeds/·status.json — 을 읽기
때문이다.

이 파일은 아무 산출물도 읽지 않는다. **발행 run 의 "랜딩 생성" 스텝이 의존하는
것이 바로 이 계약이다.** 마커를 붙이면 발행 run 이 계약을 안 보고 랜딩을 만든다.
#68 이 세운 축 그대로다 — 입력 검사는 마커 없이, 산출물 비교는 마커 뒤로.

--------------------------------------------------------------------------
왜 비공개 함수를 부르는가
--------------------------------------------------------------------------
render(lang) 전체를 태우면 **어느 검사가 잡았는지 알 수 없다.** _js_value 를
리팩터하며 타입 검사를 빼먹었는데 우연히 _fill_markers 가 다른 이유로 터지면
그 테스트는 녹색이다. 고정하려는 것은 "이 함수가 이 입력을 막는다" 이므로
검사가 사는 함수에 직접 묻는다.

_ 접두는 "밖에서 쓰지 마라" 이고 테스트는 밖이 아니다. 검사를 다른 함수로
옮기면 여기가 빨개진다 — 그것이 이 파일의 일이다(tests/test_de_scope.py 가
feed._load 를 부르는 것과 같은 자리).

--------------------------------------------------------------------------
무엇을 고정하지 않는가
--------------------------------------------------------------------------
**ui 문구의 값은 고정하지 않는다.** 무엇을 박을지가 정해지지 않았고, 값을 박으면
번역을 다듬을 때마다 깨진다. 그것은 별도 미결이다.

이스케이프 둘(_script_json·_dumps_feed_data)은 값을 단언하지만 고정하는 것은
값이 아니라 **변환**이다 — "</script> 를 넣으면 \\u003c 가 나온다" 는 문구를
바꿔도 변하지 않는다.

예외 메시지는 두 가지를 본다 — **어느 검사가 잡았는가**(match 의 짧은 어구)와
**어느 키를 가리키는가**(별도 단언). 전문을 박지는 않는다.

검사를 식별하는 어구를 잡는 것은 처음부터 그랬던 것이 아니다. 처음에는 키 이름만
봤고, 그래서 **검사를 지워도 다른 검사가 우연히 같은 키를 가리키며 터지면 녹색**
이었다 — {{p:}} 가 dict 인지 보는 검사를 지우면 문자열이 PLURAL_FORMS 검사로
흘러가 set("{n}건") 이 글자 집합이 되고, "빠진 갈래" 로 터진다. 키는 여전히
count 다. 이 파일이 막으려던 종류가 이 파일 안에서 일어났다.

어구는 문구가 아니라 **식별자**로 고른다. "복수형 매핑만 받는다" 는 그 검사가
있는 한 바뀔 이유가 없고, 바뀌었다면 검사가 바뀐 것이므로 깨지는 것이 맞다.

--------------------------------------------------------------------------
단위로 검사를 식별하고, 통과로 배선을 본다
--------------------------------------------------------------------------
순수 단위 호출은 **어느 검사가 잡았는지**를 정확히 가리키지만, **그 검사가
실제로 불리는지**는 말하지 않는다. _script_json 을 직접 불러 이스케이프를
확인해도, _js_value 가 그것을 안 부르고 json.dumps 를 부르면 여기는 녹색이다 —
변이로 확인했다. locale 문구의 "</script>" 가 스크립트를 닫는 그 사고가 그대로
돌아온다(#92).

그래서 축이 둘이다.

    단위 — 검사가 이 입력을 막는가. 어느 검사인지 match 로 식별한다.
    통과 — 그 검사와 직렬화가 실제로 사슬로 이어져 있는가. _fill_markers 로
           마커 종류 분기부터 끝까지 태운다.

통과 테스트를 _js_value 가 아니라 _fill_markers 로 태우는 것은, 분기가 바뀌어
{{p:}} 가 다른 함수로 새는 경우를 _js_value 만으로는 못 잡기 때문이다.
"""

from __future__ import annotations

import importlib

import pytest

from landing import render

# ---------------------------------------------------------------------------
# 마커 종류별 값 계약 — {{j:}} 는 문자열, {{p:}} 는 복수형 매핑, {{t:}} 는 문자열
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [["a", "b"], 7, None, 3.5, True],
    ids=["리스트", "정수", "None", "실수", "불리언"],
)
def test_a_js_marker_refuses_a_non_string(value):
    # json.dumps 는 이것들을 전부 통과시킨다. 그 값이 textContent 에 들어가면
    # 빈 라벨이나 "7" 이 되어 나가고, 양방향 검사도 복수형 검사도 타입을 보지
    # 않는다. 생성 시점에 막는 자리는 여기뿐이다.
    with pytest.raises(ValueError, match="문자열만 받는다") as caught:
        render._js_value(value, key="copy_button", plural=False)
    assert "copy_button" in str(caught.value)


def test_a_js_marker_refuses_a_plural_mapping():
    # 갈래를 고르는 것은 스크립트의 fmt 이고 그 자리는 {{p:}} 다. {{j:}} 자리에
    # 매핑이 가면 값이 그대로 쓰여 "[object Object]" 가 찍힌다 — 복사 버튼
    # 열다섯 개에 그것이 나간 것을 #92 에서 실측했다.
    with pytest.raises(ValueError, match="문자열만 받는다") as caught:
        render._js_value({"one": "오늘", "other": "오늘"}, key="today", plural=False)
    assert "today" in str(caught.value)


def test_a_plural_marker_refuses_a_string():
    with pytest.raises(ValueError, match="복수형 매핑만 받는다") as caught:
        render._js_value("{n}건", key="count", plural=True)
    assert "count" in str(caught.value)


@pytest.mark.parametrize(
    "mapping",
    [{"one": "{n}건"}, {"other": "{n}건"}, {}],
    ids=["other 없음", "one 없음", "빈 매핑"],
)
def test_a_plural_mapping_needs_both_forms(mapping):
    # 갈래 하나를 빠뜨린 locale 은 render 를 멈추지 않고 생성물도 정상으로
    # 보이는데, 브라우저에서 fmt 가 undefined 에 걸려 그 블록이 실패로 넘어간다.
    # CI 가 녹색인데 구독자는 숫자를 못 보는 꼴이다(#83).
    with pytest.raises(ValueError, match="정확히 들어야 한다") as caught:
        render._js_value(mapping, key="count", plural=True)
    assert "count" in str(caught.value)


def test_a_plural_mapping_refuses_an_unknown_form():
    # few·many 가 필요해지면 그때 연다. 지금 통과시키면 오타(othre)가 생성물까지
    # 간다.
    with pytest.raises(ValueError, match="정확히 들어야 한다") as caught:
        render._js_value(
            {"one": "{n}건", "other": "{n}건", "few": "{n}건"}, key="count", plural=True
        )
    assert "few" in str(caught.value)


def test_a_plural_mapping_needs_string_values():
    with pytest.raises(ValueError, match="값은 문자열이어야 한다") as caught:
        render._js_value({"one": "{n}건", "other": 7}, key="count", plural=True)
    assert "count" in str(caught.value)


def test_a_plural_mapping_passes_when_it_is_well_formed():
    # 양성 대조. 위 검사들이 매핑을 통째로 막는 것이 아니라 형태를 보는 것임을
    # 못 박는다.
    assert render._js_value({"one": "{n}건", "other": "{n}건"}, key="count", plural=True)


def test_a_text_marker_refuses_a_plural_mapping():
    # {{t:}} 는 HTML 자리라 fmt 가 닿지 않는다. 그냥 두면 html.escape 가
    # AttributeError 로 죽어 locale 의 어디가 문제인지 알려주지 않는다.
    #
    # **한계 — 매핑만 본다.** _html_text 는 dict 만 키 있는 ValueError 로 막고
    # 나머지 비문자열(int·list·None·float·bool)은 html.escape 까지 흘러가
    # AttributeError 로 죽는다. 키를 안 가리키는 예외다. {{j:}} 쪽(_js_value)은
    # 다섯 타입을 전부 키 있는 ValueError 로 막으므로 **두 마커의 계약이
    # 비대칭**이다.
    #
    # 여기서 "매핑만 막힌다" 를 고정하지 않는 것은 의도다 — 고정하면 _html_text 를
    # 대칭으로 고칠 때 이 테스트가 걸림돌이 된다. 고치는 것은 프로덕션 변경이라
    # 별도 PR 이고, 그때 이 테스트가 {{j:}} 쪽과 같은 모양으로 넓어져야 한다.
    with pytest.raises(ValueError, match="매핑을 받지 않는다") as caught:
        render._html_text({"one": "a", "other": "b"}, 0, key="verify_stat")
    assert "verify_stat" in str(caught.value)


# ---------------------------------------------------------------------------
# 템플릿 ↔ locale 양방향, 그리고 치환 잔존
# ---------------------------------------------------------------------------


def test_a_marker_without_a_locale_key_stops():
    with pytest.raises(ValueError, match="locale 에 없다") as caught:
        render._fill_markers("{{t:title}}", {})
    assert "title" in str(caught.value)


def test_a_locale_key_no_marker_uses_stops():
    # 키가 수십 개라 한쪽만 보면 누락이 조용히 지나간다. 양방향이라야 잡힌다.
    with pytest.raises(ValueError, match="템플릿이 쓰지 않는 키") as caught:
        render._fill_markers("{{t:title}}", {"title": "x", "unused_one": "y"})
    assert "unused_one" in str(caught.value)


def test_a_leftover_marker_stops():
    # 마커 문법을 틀리게 적으면(종류 글자를 빼거나 오타) MARKER 가 못 잡고
    # 그대로 생성물에 남는다. 잔존 검사가 그것을 본다.
    with pytest.raises(ValueError, match="치환되지 않은 마커") as caught:
        render._fill_markers("{{t:title}} {{zzz}}", {"title": "x"})
    assert "zzz" in str(caught.value)


def test_marker_kinds_dispatch_to_their_own_contract():
    # 세 종류가 한 템플릿에 있을 때 각자의 계약으로 간다. p 자리에 문자열을 두면
    # 그 키를 가리키며 멈춘다 — 다른 종류가 먼저 통과해도 마찬가지다.
    strings = {"title": "제목", "copy": "복사", "count": "{n}건"}
    with pytest.raises(ValueError, match="복수형 매핑만 받는다") as caught:
        render._fill_markers("{{t:title}} {{j:copy}} {{p:count}}", strings)
    assert "count" in str(caught.value)


# ---------------------------------------------------------------------------
# script 문맥 이스케이프 — 값이 아니라 변환을 본다
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "escaped"),
    [("</script>", "\\u003c/script>"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")],
    ids=["script 닫기", "U+2028", "U+2029"],
)
def test_the_script_serializer_neutralizes_context_breakers(raw, escaped):
    # HTML 파서는 문자열 안이든 밖이든 "</script>" 를 보면 블록을 닫는다.
    # U+2028·U+2029 는 JSON 에서 유효하지만 옛 JS 파서가 줄바꿈으로 읽는다.
    out = render._script_json(f"앞{raw}뒤")
    assert raw not in out
    assert escaped in out


@pytest.mark.parametrize(
    ("raw", "escaped"),
    [("</script>", "\\u003c/script>"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")],
    ids=["script 닫기", "U+2028", "U+2029"],
)
def test_the_feed_data_block_takes_the_same_escaping(raw, escaped):
    # script 문맥이 둘이다 — {{j:}}·{{p:}} 의 JS 리터럴과 feed-data 의 JSON
    # 블록. 한쪽만 메워 두면 갈라진다. #92 이전에는 이 블록이 json.dumps 그대로
    # 라, locale 문구에 "</script>" 가 들어오면 JSON 이 일찍 닫혀 구독 절이
    # 비었다(JS 경로 15줄 → 0줄). noscript 쪽은 HTML 이스케이프를 타 멀쩡했다.
    data = {
        "site_base": "https://example.test/",
        "groups": [
            {
                "title": "묶음",
                "feeds": [{"key": "kr", "file": "kr.ics", "label": f"라벨{raw}", "desc": "설명"}],
            }
        ],
    }
    out = render._dumps_feed_data(data)
    assert raw not in out
    assert escaped in out


# ---------------------------------------------------------------------------
# feed-data 를 만드는 자리 — land_lang 과 desc
# ---------------------------------------------------------------------------


def _module():
    return importlib.import_module("rules.de_be.feed")


@pytest.mark.parametrize("tag", ["ko", "de"], ids=["ko", "de"])
def test_a_known_land_lang_picks_a_name(tag):
    # 양성 대조. 닫힌 집합 안의 태그는 각자의 상수로 간다.
    assert render._land_name(_module(), {"state_feed": {"land_lang": tag}})


def test_an_unknown_land_lang_stops():
    # 열어 둔 집합이 아니다. 오타나 아직 없는 표기를 적으면 그 자리에서 멈춘다 —
    # 통과시키면 getattr 이 AttributeError 로 죽어 무엇이 문제인지 안 보인다.
    with pytest.raises(ValueError, match="닫힌 집합 밖이다") as caught:
        render._land_name(_module(), {"state_feed": {"land_lang": "en"}})
    assert "land_lang" in str(caught.value)


def test_a_non_state_feed_without_a_desc_stops():
    # 주 피드는 label·desc 를 모듈에서 유도하지만 나머지는 유도할 데가 없다.
    # 빠뜨리면 그 줄이 빈 채로 나가는 것이 아니라 발행이 멈춘다.
    with pytest.raises(ValueError, match="desc 가 없다") as caught:
        render._row("kr", {"state_feed": {"label_suffix": " 공휴일"}, "feeds": {}}, state=False)
    assert "kr" in str(caught.value)


# ---------------------------------------------------------------------------
# 마커가 참조할 수 있는 이름 — 예약 키와 lang 일치
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("reserved", ["lang", "locale", "og_url"], ids=["lang", "locale", "og_url"])
def test_a_locale_may_not_shadow_a_computed_key(reserved):
    # render 가 계산해 넣는 이름 셋이다. locale 의 ui 가 같은 이름을 쓰면 어느
    # 쪽이 이기는지가 dict 갱신 순서에 달리게 된다 — 조용히 덮이는 자리라
    # 겹치는 것 자체를 막는다.
    locale = {"lang": "ko", "locale": "ko-KR", "ui": {reserved: "x"}}
    with pytest.raises(ValueError, match="예약된 키가 있다") as caught:
        render._ui_strings(locale, "ko")
    assert reserved in str(caught.value)


def test_a_locale_lang_must_match_the_requested_language():
    # 파일 이름이 언어를 정하고 lang 필드가 그것을 되받는다. 어긋나면 ja.yaml 이
    # ko 페이지로 발행되는 식이 되고, 그 페이지는 html lang 과 내용이 다르다.
    with pytest.raises(ValueError, match="의 lang 이") as caught:
        render._ui_strings({"lang": "ja", "locale": "ja-JP", "ui": {}}, "ko")
    assert "ja" in str(caught.value)


def test_a_well_formed_locale_yields_the_computed_keys():
    # 양성 대조. 위 검사들이 계산 키를 막는 것이 아니라 겹침을 막는 것임을
    # 못 박는다.
    strings = render._ui_strings({"lang": "ko", "locale": "ko-KR", "ui": {"a": "x"}}, "ko")
    assert {"a", "lang", "locale", "og_url"} <= set(strings)


# ---------------------------------------------------------------------------
# 마커가 아닌 세 자리 — 각각 정확히 하나
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "placeholder",
    [render.PLACEHOLDER, render.LINKS_PLACEHOLDER, render.NOSCRIPT_PLACEHOLDER],
    ids=["FEED_DATA", "LANG_LINKS", "NOSCRIPT"],
)
@pytest.mark.parametrize("count", [0, 2], ids=["없음", "둘"])
def test_each_placeholder_must_appear_exactly_once(placeholder, count):
    # 없으면 그 블록이 통째로 빠진 페이지가 나가고, 둘 이상이면 str.replace 가
    # 전부 채워 같은 블록이 두 번 실린 페이지가 나간다. 마커와 달리 이 자리들은
    # 양방향 검사에 들지 않아 둘 다 조용하다.
    others = [
        p
        for p in (render.PLACEHOLDER, render.LINKS_PLACEHOLDER, render.NOSCRIPT_PLACEHOLDER)
        if p != placeholder
    ]
    template = " ".join(others) + " " + (placeholder + " ") * count
    with pytest.raises(ValueError, match="개다") as caught:
        render._check_placeholders(template)
    assert placeholder in str(caught.value)


def test_all_three_placeholders_present_once_pass():
    # 양성 대조. 셋이 하나씩이면 통과한다 — 실제 템플릿이 그 상태다.
    template = " ".join(
        (render.PLACEHOLDER, render.LINKS_PLACEHOLDER, render.NOSCRIPT_PLACEHOLDER)
    )
    assert render._check_placeholders(template) is None


# ---------------------------------------------------------------------------
# 배선 — 마커 값이 직렬화를 실제로 타는가
# ---------------------------------------------------------------------------
#
# 위의 이스케이프 테스트는 _script_json 을 직접 부른다. 그것만으로는 _js_value 가
# 그 함수를 부르는지 알 수 없다 — json.dumps 로 바꿔치기해도 녹색이었다(변이 확인).
# 여기서는 마커 종류 분기부터 직렬화까지 사슬 전체를 태운다.

BREAKERS = [
    ("</script>", "\\u003c/script>"),
    ("\u2028", "\\u2028"),
    ("\u2029", "\\u2029"),
]
BREAKER_IDS = ["script 닫기", "U+2028", "U+2029"]


@pytest.mark.parametrize(("raw", "escaped"), BREAKERS, ids=BREAKER_IDS)
def test_a_js_marker_value_goes_through_the_script_serializer(raw, escaped):
    out = render._js_value(f"앞{raw}뒤", key="copy_button", plural=False)
    assert raw not in out
    assert escaped in out


@pytest.mark.parametrize(("raw", "escaped"), BREAKERS, ids=BREAKER_IDS)
def test_a_plural_marker_value_goes_through_the_script_serializer(raw, escaped):
    # 갈래 값 **안에** 넣는다. 매핑이 객체 리터럴로 직렬화될 때 그 안의 문자열도
    # 같은 이스케이프를 타야 한다.
    out = render._js_value({"one": f"하나{raw}", "other": f"여럿{raw}"}, key="count", plural=True)
    assert raw not in out
    assert out.count(escaped) == 2


@pytest.mark.parametrize(("raw", "escaped"), BREAKERS, ids=BREAKER_IDS)
def test_filling_markers_escapes_both_js_kinds(raw, escaped):
    # 마커 종류 분기까지 포함한다 — {{p:}} 가 다른 함수로 새면 여기서 걸린다.
    out = render._fill_markers(
        "{{j:copy}} {{p:count}}",
        {"copy": f"복사{raw}", "count": {"one": f"하나{raw}", "other": f"여럿{raw}"}},
    )
    assert raw not in out
    assert out.count(escaped) == 3
