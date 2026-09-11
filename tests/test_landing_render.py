"""커밋된 index.html 이 지금 landing/ 으로 재현되는가.

index.html 은 landing/render.py 의 산출물이다(landing/__init__.py). 사람이
layout·locale·template 을 고치고 index.html 을 다시 만들지 않으면, 커밋된
페이지는 저장소가 말하는 것과 다른 것을 보여준다. 여기서 잡는다 —
tests/test_published_feed.py 가 feeds/*.ics 에 대해 하는 것과 같은 질문이다.

published_artifact 마커가 붙어 있다
-----------------------------------

이 테스트는 발행 워크플로(-m "not published_artifact")에서 돌지 않는다.
랜딩이 낡은 것은 사람이 보는 페이지가 뒤처진 것이지 피드가 틀린 것이 아니다.
피드는 구독자의 캘린더에 들어가는 것이고 랜딩은 그 주소를 건네주는 자리다 —
후자가 낡았다고 전자의 발행을 막으면, 막아서 얻는 것이 없다. 발행 run 은
index.html 을 스스로 다시 만들어 올리므로(publish.yml 의 "랜딩 생성" 스텝),
낡음은 다음 발행에서 닫힌다. 검사는 PR 을 보는 ci.yml 의 몫이다.

바이트 비교다. 파싱해서 feed-data 만 비교하면 템플릿의 문구 변경이 반영되지
않은 것을 놓친다. 구독자에게 나가는 것은 파싱 결과가 아니라 파일이다.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from landing import render

pytestmark = pytest.mark.published_artifact

ROOT = Path(__file__).resolve().parents[1]


# 언어마다 한 건. 목록은 render 가 locales/ 에서 스캔한 것 — 언어를 늘리면
# 그 페이지가 자동으로 검사에 든다. 한 언어 페이지만 낡아도 여기서 걸린다.
@pytest.mark.parametrize("lang", render.languages())
def test_the_committed_landing_is_reproducible_from_landing_inputs(lang):
    page = render.output_path(lang)
    assert page.is_file(), f"{page.relative_to(ROOT)} 이 없다 — 생성해서 커밋할 것"
    committed = page.read_text(encoding="utf-8")
    rebuilt = render.render(lang)
    assert rebuilt == committed, (
        f"커밋된 {page.relative_to(ROOT)} 이 지금 landing/ 으로 재현되지 않는다.\n"
        f"커밋본 {len(committed)} chars / 재생성 {len(rebuilt)} chars\n"
        "layout·locale·template 을 바꿨다면 페이지를 함께 갱신할 것:\n"
        "  uv run python -m landing.render"
    )
