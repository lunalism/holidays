"""index.html 을 만든다 — 구독 절의 feed-data 블록을 채운다.

--------------------------------------------------------------------------
무엇이 어디서 오는가
--------------------------------------------------------------------------
    피드 목록          rules/ 아래 feed.py 를 가진 패키지. FEEDS 가 단일
                       공급원이지만 워크플로를 파싱하지 않는다 — 둘이 같은
                       집합인 것은 tests/test_feed_set.py 가 고정한다.
    file · site_base   각 feed.py 의 FEED_PATH 이름, CNAME.
    주 피드 label·desc rules/de_<주>/feed.py 의 CALNAME·LAND_NAME 에서 유도.
                       tests/test_landing.py 의 결속 테스트와 같은 식이다.
    그 밖의 label·desc·그룹 제목
                       locales/<언어>.yaml — 유도할 데가 없어 사람이 적는다.
    그룹 소속·순서     layout.yaml — 언어와 무관하다.

layout 과 locale 을 가른 것은 언어를 늘릴 때 구조가 언어 수만큼 복제되지
않게 하기 위해서다. 언어를 늘리는 것은 locales/ 에 파일 하나를 더하는 일이어야
한다.

--------------------------------------------------------------------------
rules/status.py 와 같은 꼴이다
--------------------------------------------------------------------------
feed_data() 가 dict 를, render() 가 파일에 쓸 문자열을 낸다. 이전 발행본을
입력으로 받지 않으므로 core/feed.py::publish() 형이 아니다 — 같은 입력이면
같은 출력이고, 시계를 읽지 않는다.

--------------------------------------------------------------------------
멈추는 것
--------------------------------------------------------------------------
rules/ 에 있는데 layout 에 자리가 없는 피드, layout 에 있는데 rules/ 에 없는
피드, 주 피드가 아닌데 locale 에 desc 가 없는 피드 — 전부 ValueError 다.
새 피드가 어느 묶음에 설지는 사람이 정한다. 접두사로 넘겨짚지 않는다(아코디언
하나만 예외이고 그것은 layout 이 명시한 규칙이다).
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RULES_DIR = ROOT / "rules"
CNAME_PATH = ROOT / "CNAME"
TEMPLATE_PATH = HERE / "template.html"
LAYOUT_PATH = HERE / "layout.yaml"
LOCALES_DIR = HERE / "locales"

PLACEHOLDER = "{{FEED_DATA}}"


def feed_codes() -> list[str]:
    """rules/ 아래 feed.py 를 가진 패키지 이름. tests/test_feed_set.py 와 같은 조건."""
    return sorted(p.name for p in RULES_DIR.iterdir() if p.is_dir() and (p / "feed.py").is_file())


def _module(code: str):
    return importlib.import_module(f"rules.{code}.feed")


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _row(code: str, locale: dict, *, state: bool) -> dict:
    module = _module(code)
    suffix = locale["state_feed"]["label_suffix"]
    if state:
        label = module.CALNAME.removesuffix(suffix)
        desc = locale["state_feed"]["desc"].format(land=module.LAND_NAME)
    else:
        entry = locale["feeds"].get(code)
        if not entry or "desc" not in entry:
            raise ValueError(f"locale 에 {code} 의 desc 가 없다 — 유도할 데가 없으니 적어야 한다")
        label = entry.get("label") or module.CALNAME.removesuffix(suffix)
        desc = entry["desc"]
    return {"key": code, "file": module.FEED_PATH.name, "label": label, "desc": desc}


def feed_data(lang: str = "ko") -> dict:
    """구독 절의 feed-data 블록. 키 순서가 곧 출력 순서다."""
    layout = _load_yaml(LAYOUT_PATH)
    locale = _load_yaml(LOCALES_DIR / f"{lang}.yaml")
    codes = feed_codes()
    placed: list[str] = []

    groups = []
    for group in layout["groups"]:
        rows = []
        for code in group["feeds"]:
            if code not in codes:
                raise ValueError(f"layout 의 {code} 가 rules/ 에 없다")
            rows.append(_row(code, locale, state=False))
            placed.append(code)
        out = {"title": locale["groups"][group["id"]]["title"], "feeds": rows}
        if "accordion" in group:
            acc = group["accordion"]
            members = [c for c in codes if c.startswith(acc["prefix"])]
            out["accordion"] = {
                "title": locale["groups"][acc["id"]]["title"],
                "feeds": [_row(c, locale, state=True) for c in members],
            }
            placed.extend(members)
        groups.append(out)

    if len(placed) != len(set(placed)):
        dup = sorted({c for c in placed if placed.count(c) > 1})
        raise ValueError(f"layout 에 두 번 놓인 피드: {dup}")
    missing = sorted(set(codes) - set(placed))
    if missing:
        raise ValueError(f"rules/ 에 있는데 layout 에 자리가 없는 피드: {missing}")

    site_base = f"https://{CNAME_PATH.read_text(encoding='utf-8').strip()}/"
    return {"site_base": site_base, "groups": groups}


def _dumps_feed_data(data: dict) -> str:
    """사람이 쓰던 모양 그대로 — 피드 한 줄에 하나. json.dumps 의 indent 는
    피드 dict 를 네 줄로 펴서 블록이 세 배로 길어진다. 읽는 쪽은 json.loads
    라 모양은 의미가 없지만, diff 를 보는 것은 사람이다."""

    def s(v: str) -> str:
        return json.dumps(v, ensure_ascii=False)

    def row(feed: dict, indent: str) -> str:
        return (
            f'{indent}{{ "key": {s(feed["key"])}, "file": {s(feed["file"])}, '
            f'"label": {s(feed["label"])}, "desc": {s(feed["desc"])} }}'
        )

    lines = ["{", f'  "site_base": {s(data["site_base"])},', '  "groups": [']
    for gi, group in enumerate(data["groups"]):
        lines.append("    {")
        lines.append(f'      "title": {s(group["title"])},')
        rows = ",\n".join(row(f, "        ") for f in group["feeds"])
        has_acc = "accordion" in group
        lines.append(f'      "feeds": [\n{rows}\n      ]{"," if has_acc else ""}')
        if has_acc:
            acc = group["accordion"]
            arows = ",\n".join(row(f, "          ") for f in acc["feeds"])
            lines.append('      "accordion": {')
            lines.append(f'        "title": {s(acc["title"])},')
            lines.append(f'        "feeds": [\n{arows}\n        ]')
            lines.append("      }")
        lines.append("    }" + ("," if gi < len(data["groups"]) - 1 else ""))
    lines.append("  ]")
    lines.append("}")
    return "\n".join(lines)


def render(lang: str = "ko") -> str:
    """파일에 쓸 문자열. 템플릿에 플레이스홀더가 정확히 하나여야 한다."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise ValueError(f"template.html 에 {PLACEHOLDER} 가 {template.count(PLACEHOLDER)}개다")
    return template.replace(PLACEHOLDER, _dumps_feed_data(feed_data(lang)))


if __name__ == "__main__":  # pragma: no cover
    import sys

    _target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "index.html"
    _target.write_text(render(), encoding="utf-8")
    print(f"[landing] {_target}")
