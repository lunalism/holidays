"""_config.yml 의 exclude 목록은 의도한 값에서 벗어나지 않는다.

--------------------------------------------------------------------------
이 파일이 지키는 명제
--------------------------------------------------------------------------
    Jekyll 발행에서 제외되는 경로는 `landing/` 과 Jekyll 3.10 의 기본 제외
    목록의 합집합, 정확히 그것이다. 더 늘지도, 빠지지도 않는다.

GitHub Pages 는 main 브랜치 루트를 Jekyll 로 통째로 낸다. `_config.yml` 의
`exclude` 는 그 발행 대상에서 경로를 빼는 유일한 수단이고, 빠진 경로는 404 가
된다. 발행된 URL 은 계약이라(docs/seo.md) 이 목록은 두 방향 모두 위험하다 —
항목이 빠지면 치환 전 마커가 남은 `/landing/template.html` 이 다시 열리고,
항목이 늘면 누군가 안내받았을 수 있는 주소가 404 가 된다. 그래서 목록을
통째로 고정한다. 바꾸려면 여기도 같이 바꿔야 하고, 그때 docs/seo.md 의
기준("공개 웹 주소였던 적이 없는 경로에만")을 다시 밟게 된다.

--------------------------------------------------------------------------
왜 기본 제외 목록이 들어 있는가
--------------------------------------------------------------------------
GitHub Pages 는 Jekyll 3.10.0 에 고정돼 있다(pages.github.com/versions.json).
Jekyll 3 은 사용자가 `exclude` 를 적으면 기본 목록을 **대체**한다 —
configuration.rb `from` 이 `deep_merge_hashes(DEFAULTS, user)` 를 하고, 그
병합은 Hash 만 합치고 배열은 덮어쓴다. Jekyll 4 는 `add_default_excludes` 로
이어붙이므로 거기서는 이 문제가 없다. 그래서 `landing/` 만 적으면 `Gemfile`·
`node_modules`·`vendor/…` 가 발행 대상으로 돌아온다. 지금은 그중 추적되는
것이 없어 무해하지만, 의존성 디렉터리가 생기는 순간 `_config.yml` 을 다시
볼 계기 없이 조용히 공개된다. 그래서 기본 목록을 명시해 되살린다.

값은 jekyll v3.10.0 lib/jekyll/configuration.rb 의 DEFAULTS["exclude"] 를
그대로 옮긴 것이다. Pages 의 Jekyll 이 4 로 올라가면 이 목록은 중복이 될
뿐 해롭지 않다.

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

# jekyll v3.10.0 lib/jekyll/configuration.rb DEFAULTS["exclude"]. 순서까지 그대로.
JEKYLL_3_10_DEFAULT_EXCLUDE = [
    "Gemfile",
    "Gemfile.lock",
    "node_modules",
    "vendor/bundle/",
    "vendor/cache/",
    "vendor/gems/",
    "vendor/ruby/",
]

# 이 레포가 더하는 것. 늘리는 것은 발행 파일 집합을 바꾸는 것이다. docs/seo.md 참조.
REPO_EXCLUDE = ["landing/"]

EXPECTED_EXCLUDE = REPO_EXCLUDE + JEKYLL_3_10_DEFAULT_EXCLUDE


def test_exclude_is_landing_plus_jekyll_defaults() -> None:
    assert CONFIG.is_file(), "_config.yml 이 레포 루트에 없다"
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert isinstance(config, dict), "_config.yml 최상위가 매핑이 아니다"
    assert config.get("exclude") == EXPECTED_EXCLUDE
