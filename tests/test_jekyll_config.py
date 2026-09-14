"""_config.yml 의 exclude 목록은 의도한 값에서 벗어나지 않는다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    Jekyll 발행에서 제외되는 경로는 정확히 `landing/` 하나다.
    더 늘지도, 빠지지도 않는다.

GitHub Pages 는 main 브랜치 루트를 Jekyll 로 통째로 낸다. `_config.yml` 의
`exclude` 는 그 발행 대상에서 경로를 빼는 유일한 수단이고, 빠진 경로는 404 가
된다. 발행된 URL 은 계약이라(docs/seo.md) 이 목록은 두 방향 모두 위험하다 —
항목이 빠지면 치환 전 마커가 남은 `/landing/template.html` 이 다시 열리고,
항목이 늘면 누군가 안내받았을 수 있는 주소가 404 가 된다. 그래서 목록을
통째로 고정한다. 바꾸려면 여기도 같이 바꿔야 하고, 그때 docs/seo.md 의
기준("공개 웹 주소였던 적이 없는 경로에만")을 다시 밟게 된다.

--------------------------------------------------------------------------
왜 마커가 없는가
--------------------------------------------------------------------------
published_artifact 마커는 발행 파이프라인이 재생성하는 커밋된 산출물
(feeds/·status.json·index.html)을 읽는 테스트에 붙는다. 규칙을 바꾸고
발행본을 갱신하기 전에는 깨지는 것이 정상이라 발행 run 에서 빼는 것이다.

`_config.yml` 은 그 산출물이 아니다. 손으로 쓰는 소스이고, 어떤 워크플로도
이 파일을 생성하거나 갱신하지 않는다. 낡은 발행본 때문에 깨질 일이 없으므로
발행 run 에서 빼야 할 이유도 없다 — tests/test_landing_contract.py 와 같은
자리다. 네트워크로 발행본을 확인하지도 않는다.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "_config.yml"

# 이 목록을 바꾸는 것은 발행 파일 집합을 바꾸는 것이다. docs/seo.md 참조.
EXPECTED_EXCLUDE = ["landing/"]


def test_exclude_is_exactly_landing() -> None:
    assert CONFIG.is_file(), "_config.yml 이 레포 루트에 없다"
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert isinstance(config, dict), "_config.yml 최상위가 매핑이 아니다"
    assert config.get("exclude") == EXPECTED_EXCLUDE
