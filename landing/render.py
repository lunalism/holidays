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
    UI 문구            locales/<언어>.yaml 의 ui — 템플릿의 {{t:키}}·{{j:키}}
                       마커 자리에 들어간다. 템플릿은 구조만 들고 문구는 전부
                       locale 이 든다. 언어별 템플릿을 두지 않는다 — 마크업을
                       고칠 때 언어 수만큼 고치게 되는 종류의 중복이다.

--------------------------------------------------------------------------
마커 — 문맥은 템플릿이 말한다
--------------------------------------------------------------------------
    {{t:키}}   HTML 텍스트·속성값. html.escape 로 이스케이프한다.
    {{j:키}}   JS 문자열 리터럴. json.dumps 로 따옴표까지 만든다 — 문구에
               따옴표·백슬래시가 있어도 스크립트가 깨지지 않는다.
    {{FEED_DATA}}  구독 절 JSON 블록. 제3의 문맥이라 따로 채운다.

locale 은 문맥을 모른다. 같은 키를 t 와 j 양쪽에서 써도 된다.

문구 안의 {이름} 자리는 둘로 갈린다. {item_count}·{unverified_count} 는
status.json 을 못 읽었을 때의 폴백 숫자라 render 가 <span data-*> 로 채운다 —
스크립트가 그 셀렉터로 덮어쓴다. {n}·{date} 는 실행 시 값이라 스크립트의
fmt() 가 채운다. render 는 그 둘을 건드리지 않고 그대로 낸다.

양방향 검사 — 템플릿의 모든 키가 locale 에 있고, locale ui 의 모든 키가
템플릿에 쓰여야 한다. 키가 수십 개라 한쪽만 보면 누락이 조용히 지나간다.
어긋나면 ValueError 다.

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

import html
import importlib
import json
import re
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
MARKER = re.compile(r"\{\{([tj]):(\w+)\}\}")

# 원문 대조 절의 폴백 숫자. status.json 이 덮어쓰기 전의 초기값이고, status 를
# 못 읽으면 이 값이 그대로 보인다. status 에서 유도하지 않는다 — 그러면 매
# 발행마다 index.html 이 바뀐다(DESIGN.md 발행 파이프라인).
FALLBACK_COUNTS = {"item_count": 48, "unverified_count": 32}


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


def _ui_strings(locale: dict) -> dict[str, str]:
    """마커가 참조할 수 있는 키 전부 — ui 아래와 최상위 lang·locale."""
    strings = dict(locale["ui"])
    for key in ("lang", "locale"):
        if key in strings:
            raise ValueError(f"locale ui 에 예약된 키가 있다: {key}")
        strings[key] = locale[key]
    return strings


def _html_text(value: str, column: int) -> str:
    """HTML 텍스트·속성값. 여러 줄 문구는 마커가 선 열에 맞춰 이어 붙여 원문의
    줄 나눔과 들여쓰기를 되살린다 — 그래야 생성물 diff 가 문구 변경만 보인다."""
    escaped = html.escape(value, quote=True)
    for name, number in FALLBACK_COUNTS.items():
        escaped = escaped.replace(
            "{" + name + "}", f'<span data-{name.replace("_", "-")}>{number}</span>'
        )
    return escaped.replace("\n", "\n" + " " * column)


def _js_string(value: str) -> str:
    """JS 문자열 리터럴 — 따옴표까지. {n}·{date} 는 그대로 남긴다(스크립트 몫).

    json.dumps 만으로는 JS 문자열 리터럴로서 안전하지 않다. 이 리터럴은
    <script> 안에 놓이는데, HTML 파서는 문자열 안이든 밖이든 "</script>" 를
    보면 블록을 닫는다 — JSON 은 "<" 를 이스케이프하지 않는다. U+2028·U+2029
    는 JSON 문자열에서 유효하지만 옛 JS 파서가 줄바꿈으로 읽는다. 셋 다
    유니코드 이스케이프(\\uXXXX)로 바꾼다. ko 문구에는 해당 문자가 없어 지금 드러나지 않을 뿐이고,
    이것은 미래 대비가 아니라 함수 계약의 구멍을 메우는 것이다.
    """
    literal = json.dumps(value, ensure_ascii=False)
    return literal.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _fill_markers(template: str, strings: dict[str, str]) -> str:
    used: set[str] = set()

    def sub(match: re.Match) -> str:
        kind, key = match.group(1), match.group(2)
        if key not in strings:
            raise ValueError(f"템플릿의 {{{{{kind}:{key}}}}} 가 locale 에 없다")
        used.add(key)
        value = strings[key]
        if kind == "j":
            return _js_string(value)
        column = match.start() - template.rfind("\n", 0, match.start()) - 1
        return _html_text(value, column)

    out = MARKER.sub(sub, template)
    unused = sorted(set(strings) - used)
    if unused:
        raise ValueError(f"locale 에 있는데 템플릿이 쓰지 않는 키: {unused}")
    leftover = [m for m in re.findall(r"\{\{[^}]*\}\}", out) if m != PLACEHOLDER]
    if leftover:
        raise ValueError(f"치환되지 않은 마커: {sorted(set(leftover))}")
    return out


def render(lang: str = "ko") -> str:
    """파일에 쓸 문자열. 템플릿에 FEED_DATA 플레이스홀더가 정확히 하나여야 한다."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise ValueError(f"template.html 에 {PLACEHOLDER} 가 {template.count(PLACEHOLDER)}개다")
    locale = _load_yaml(LOCALES_DIR / f"{lang}.yaml")
    # 문구 마커를 먼저 채우고 feed-data 를 넣는다. 잔존 마커 검사가 JSON 의
    # 중괄호를 보지 않게 하기 위해서다(FEED_DATA 자체는 검사에서 뺀다).
    page = _fill_markers(template, _ui_strings(locale))
    return page.replace(PLACEHOLDER, _dumps_feed_data(feed_data(lang)))


if __name__ == "__main__":  # pragma: no cover
    import sys

    _target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "index.html"
    _target.write_text(render(), encoding="utf-8")
    print(f"[landing] {_target}")
