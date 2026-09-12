"""index.html 을 만든다 — 구독 절의 feed-data 블록을 채운다.

--------------------------------------------------------------------------
무엇이 어디서 오는가
--------------------------------------------------------------------------
    피드 목록          rules/ 아래 feed.py 를 가진 패키지. FEEDS 가 단일
                       공급원이지만 워크플로를 파싱하지 않는다 — 둘이 같은
                       집합인 것은 tests/test_feed_set.py 가 고정한다.
    file · site_base   각 feed.py 의 FEED_PATH 이름, CNAME.
    주 피드 label·desc locale 의 state_feed 틀에 rules/de_<주>/feed.py 의 주
                       이름을 넣은 것. 어느 표기를 쓸지는 locale 의 land_lang 이
                       고른다(ko→LAND_NAME, de→LAND_NAME_DE). tests/test_landing.py
                       의 결속 테스트와 같은 식이다.
    그 밖의 label·desc·그룹 제목
                       locales/<언어>.yaml — 유도할 데가 없어 사람이 적는다.
    그룹 소속·순서     layout.yaml — 언어와 무관하다.
    UI 문구            locales/<언어>.yaml 의 ui — 템플릿의 {{t:키}}·{{j:키}}
                       마커 자리에 들어간다. 템플릿은 구조만 들고 문구는 전부
                       locale 이 든다. 언어별 템플릿을 두지 않는다 — 마크업을
                       고칠 때 언어 수만큼 고치게 되는 종류의 중복이다.

--------------------------------------------------------------------------
언어 — locale 파일 하나가 페이지 하나다
--------------------------------------------------------------------------
locales/<lang>.yaml 이 있는 언어마다 페이지를 만든다. 목록은 디렉터리
스캔이다(rules/ 스캔과 같은 꼴) — 언어를 늘리는 것은 파일 하나를 더하는
일이어야 한다.

경로는 lang 에서 유도한다. ROOT_LANG(ko)은 "/" 에 남고 — 루트 URL 은 이미
발행돼 있고 발행된 것은 바꾸지 않는다 — 그 밖은 "/<lang>/" 이다. og:url 과
언어 전환 링크가 이 경로에서 나온다. 전환 링크는 <a href> 다: JS 없이
동작해야 하고, 현재 언어는 aria-current 로 표시한다. 표시명은 각 locale 의
name(자기 언어로 적은 자기 이름)이라 번역 대상이 아니다.

--------------------------------------------------------------------------
마커 — 문맥은 템플릿이 말한다
--------------------------------------------------------------------------
    {{t:키}}   HTML 텍스트·속성값. html.escape 로 이스케이프한다.
    {{j:키}}   JS 문자열 리터럴. json.dumps 로 따옴표까지 만든다 — 문구에
               따옴표·백슬래시가 있어도 스크립트가 깨지지 않는다.
    {{FEED_DATA}}  구독 절 JSON 블록. 제3의 문맥이라 따로 채운다.
    {{LANG_LINKS}} 언어 전환 링크 마크업. render 가 만든다.

render 가 계산해 넣는 문구 키가 있다 — og_url(이 페이지의 절대 URL). locale 에
적지 않고, 템플릿은 반드시 써야 한다(양방향 검사에 든다).

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
LINKS_PLACEHOLDER = "{{LANG_LINKS}}"
NOSCRIPT_PLACEHOLDER = "{{NOSCRIPT}}"

# 루트("/")에 남는 언어. 처음 발행된 페이지이고 그 URL 은 바꾸지 않는다.
ROOT_LANG = "ko"
MARKER = re.compile(r"\{\{([tj]):(\w+)\}\}")

# fmt() 의 첫 인자로 선 {{j:키}}. 복수형 매핑을 받을 수 있는 마커는 이 자리뿐이라
# 템플릿에서 유도한다 — 목록을 손으로 들지 않는다(열거하면 그 자리가 낡는다).
# 그룹 1 이 마커 자체다. 잡는 것은 키 이름이 아니라 그 마커가 선 위치다.
FMT_CALL = re.compile(r"\bfmt\(\s*(\{\{j:\w+\}\})")

# 원문 대조 절의 폴백 숫자. status.json 이 덮어쓰기 전의 초기값이고, status 를
# 못 읽으면 이 값이 그대로 보인다. status 에서 유도하지 않는다 — 그러면 매
# 발행마다 index.html 이 바뀐다(DESIGN.md 발행 파이프라인).
FALLBACK_COUNTS = {"item_count": 48, "unverified_count": 32}

# 복수형 갈래. 매핑으로 적은 문구는 이 둘을 **정확히** 들어야 한다. 스크립트의
# fmt() 가 n === 1 이면 one, 아니면 other 를 고르므로 하나만 있으면 나머지 자리에서
# undefined 를 쓰고, 그 블록이 런타임에 죽는다 — 생성물은 정상이고 테스트도 녹색인데
# 구독자만 숫자를 못 보는 꼴이다. few·many 가 필요해지면 그때 연다. 지금 모르는
# 갈래를 통과시키면 오타(othre)가 생성물까지 간다.
PLURAL_FORMS = frozenset({"one", "other"})


def feed_codes() -> list[str]:
    """rules/ 아래 feed.py 를 가진 패키지 이름. tests/test_feed_set.py 와 같은 조건."""
    return sorted(p.name for p in RULES_DIR.iterdir() if p.is_dir() and (p / "feed.py").is_file())


def _module(code: str):
    return importlib.import_module(f"rules.{code}.feed")


def languages() -> list[str]:
    """locales/*.yaml 의 언어 코드. ROOT_LANG 이 앞, 나머지는 코드순."""
    langs = sorted(p.stem for p in LOCALES_DIR.glob("*.yaml"))
    if ROOT_LANG not in langs:
        raise ValueError(f"locales/ 에 {ROOT_LANG}.yaml 이 없다")
    return [ROOT_LANG] + [lang for lang in langs if lang != ROOT_LANG]


def page_path(lang: str) -> str:
    """사이트 안에서 이 언어 페이지가 사는 경로. 루트 언어만 '/' 다."""
    return "/" if lang == ROOT_LANG else f"/{lang}/"


def output_path(lang: str) -> Path:
    """저장소 안의 출력 파일. page_path 와 같은 모양이다."""
    return ROOT / "index.html" if lang == ROOT_LANG else ROOT / lang / "index.html"


def _site_base() -> str:
    return f"https://{CNAME_PATH.read_text(encoding='utf-8').strip()}/"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# state_feed.land_lang 이 고르는 것 — 주 이름을 어느 표기에서 가져올지. 값은
# 언어 코드가 아니라 표기 이름이고, 그래서 언어가 늘어도 이 표는 늘지 않는다
# (언어를 늘리는 것은 locales/ 에 파일 하나를 더하는 일이어야 한다 — 위 언어 절).
# 늘어나는 경우는 주 이름의 새 표기가 생길 때뿐이고, 그때는 아홉 모듈에 상수를
# 더하는 일이 먼저다.
LAND_NAME_ATTR = {"ko": "LAND_NAME", "de": "LAND_NAME_DE"}


def _land_name(module, locale: dict) -> str:
    """주 피드 label·desc 의 {land} 에 들어갈 주 이름."""
    tag = locale["state_feed"]["land_lang"]
    if tag not in LAND_NAME_ATTR:
        raise ValueError(
            f"state_feed.land_lang 이 닫힌 집합 밖이다: {tag!r} — "
            f"{sorted(LAND_NAME_ATTR)} 중 하나여야 한다"
        )
    return getattr(module, LAND_NAME_ATTR[tag])


def _row(code: str, locale: dict, *, state: bool) -> dict:
    module = _module(code)
    suffix = locale["state_feed"]["label_suffix"]
    if state:
        # label 도 desc 와 같은 {land} 로 만든다. CALNAME 에서 접미를 떼는 방식은
        # CALNAME 이 한국어여서 한국어 label 만 낼 수 있었다. 두 방식이 ko 에서
        # 같은 값인 것은 tests/test_de_scope.py 가 고정한다.
        land = _land_name(module, locale)
        label = locale["state_feed"]["label"].format(land=land)
        desc = locale["state_feed"]["desc"].format(land=land)
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

    return {"site_base": _site_base(), "groups": groups}


def _script_json(value) -> str:
    """<script> 안에 놓을 JSON 한 조각. 이 페이지에 script 문맥이 **둘** 있고
    둘 다 이 함수를 타야 한다.

        {{j:키}}        스크립트 안의 JS 리터럴
        {{FEED_DATA}}   <script type="application/json"> 블록

    둘을 한 함수로 묶은 것은 갈라졌던 적이 있기 때문이다. json.dumps 만으로는
    script 문맥에서 안전하지 않은데 — HTML 파서는 문자열 안이든 밖이든
    "</script>" 를 보면 블록을 닫고, JSON 은 "<" 를 이스케이프하지 않는다 —
    그 사실을 알아채고 메운 것은 {{j:}} 쪽 하나뿐이었다. feed-data 블록은
    그대로 남아, locale 문구에 "</script>" 가 들어오면 JSON 블록이 일찍 닫히고
    JSON.parse 가 실패해 **구독 절이 빈다.** 같은 문구가 noscript 쪽은 HTML
    이스케이프를 타므로 멀쩡하다 — JS 를 쓰는 쪽만 잃는다.

    U+2028·U+2029 는 JSON 문자열에서 유효하지만 옛 JS 파서가 줄바꿈으로 읽는다.
    셋 다 유니코드 이스케이프로 바꾼다. 지금 문구에 해당 문자가 없어 드러나지
    않을 뿐이고, 이것은 미래 대비가 아니라 문맥의 요구다."""
    literal = json.dumps(value, ensure_ascii=False)
    return (
        literal.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _dumps_feed_data(data: dict) -> str:
    """사람이 쓰던 모양 그대로 — 피드 한 줄에 하나. json.dumps 의 indent 는
    피드 dict 를 네 줄로 펴서 블록이 세 배로 길어진다. 읽는 쪽은 json.loads
    라 모양은 의미가 없지만, diff 를 보는 것은 사람이다."""

    def s(v: str) -> str:
        return _script_json(v)

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


def _ui_strings(locale: dict, lang: str) -> dict:
    """마커가 참조할 수 있는 키 전부 — ui 아래, 최상위 lang·locale, 그리고
    render 가 계산하는 og_url.

    값은 문자열이거나 복수형 매핑(one·other)이다. 후자는 {{j:}} 마커에서만
    쓸 수 있고, 그 검사는 _js_string·_html_text 가 한다."""
    strings = dict(locale["ui"])
    computed = {"lang": locale["lang"], "locale": locale["locale"],
                "og_url": _site_base().rstrip("/") + page_path(lang)}
    for key, value in computed.items():
        if key in strings:
            raise ValueError(f"locale ui 에 예약된 키가 있다: {key}")
        strings[key] = value
    if locale["lang"] != lang:
        raise ValueError(f"locales/{lang}.yaml 의 lang 이 {locale['lang']!r} 다")
    return strings


def _lang_links(current: str) -> str:
    """언어 전환 링크. <a href> 라 JS 없이 동작하고, 현재 언어는 aria-current 다."""
    items = []
    for lang in languages():
        name = html.escape(_load_yaml(LOCALES_DIR / f"{lang}.yaml")["name"], quote=True)
        current_attr = ' aria-current="page"' if lang == current else ""
        items.append(
            f'<a href="{page_path(lang)}" lang="{lang}" hreflang="{lang}"{current_attr}>{name}</a>'
        )
    return "\n".join(items)


def _noscript(lang: str, column: int) -> str:
    """JS 를 실행하지 않는 클라이언트가 읽을 피드 목록.

    구독 절의 줄은 스크립트가 feed-data JSON 으로 그린다. 그 JSON 은 페이지에
    있지만 스크립트를 돌리지 않는 쪽 — 크롤러·SNS 프리뷰·리더 모드·번역기 —
    에게는 없는 것과 같다. 사람 브라우저에서 JS 가 꺼진 경우를 위한 것이 아니다.

    같은 feed_data() 에서 나오므로 목록이 두 곳이 되지 않는다. 사람이 두 번
    적는 것이 아니라 render 가 두 번 낸다 — 언어가 늘어도 같다.

    복사 버튼은 넣지 않는다. navigator.clipboard 를 쓰는 핸들러라 JS 없이는
    죽은 버튼이 되고, 죽은 버튼은 거짓말이다(이슈 #64 가 옛 마크업의 href="#"
    을 같은 이유로 지적했다). 주소는 텍스트로 둔다 — 링크로 만들면 .ics 클릭이
    다운로드가 되어 구독과 다른 동작이 된다. webcal 링크는 지금도 <a href> 라
    JS 없이 동작하므로 그대로 낸다.

    아코디언은 <details>/<summary> 다 — 스크립트가 만들던 것과 같은 요소이고
    네이티브라 JS 없이 열린다. 마커(chevron)만 스크립트 몫이라 빠진다.
    """
    data = feed_data(lang)
    locale = _load_yaml(LOCALES_DIR / f"{lang}.yaml")
    open_in_app = locale["ui"]["open_in_app"]
    base = data["site_base"]

    def esc(value: str) -> str:
        return html.escape(value, quote=True)

    def row(feed: dict, depth: int) -> list[str]:
        pad = "  " * depth
        url = f'{base}feeds/{feed["file"]}'
        return [
            f'{pad}<div class="feed-row">',
            f'{pad}  <div class="feed-head">',
            f'{pad}    <p class="feed-label">{esc(feed["label"])}</p>',
            f'{pad}    <p class="feed-desc">{esc(feed["desc"])}</p>',
            f'{pad}  </div>',
            f'{pad}  <div class="feed-controls">',
            f'{pad}    <code class="url">{esc(url)}</code>',
            f'{pad}    <a class="btn" href="{esc(url.replace("https:", "webcal:", 1))}">'
            f'{esc(open_in_app)}</a>',
            f'{pad}  </div>',
            f'{pad}</div>',
        ]

    lines = ["<noscript>"]
    for group in data["groups"]:
        lines.append('  <div class="feed-group">')
        lines.append(f'    <p class="feed-group-title">{esc(group["title"])}</p>')
        for feed in group["feeds"]:
            lines += row(feed, 2)
        if "accordion" in group:
            acc = group["accordion"]
            lines.append('    <details class="feed-accordion">')
            # 개수를 적지 않는다. 스크립트 쪽 summary 는 "제목 (9)" 로 세어 넣지만
            # 그것은 DOM 에서 만들어지고 내려가는 HTML 에는 없다. 여기 숫자를 적으면
            # 내려가는 HTML 에 개수가 박히고, test_the_feed_list_is_read_from_the_data_block
            # 이 그것을 잡는다 — render 가 세더라도 마크업에 박힌 숫자는 같은 위험
            # (피드를 늘릴 때 숫자만 남는 것)의 자리라는 것이 그 테스트의 명제다.
            lines.append(f'      <summary>{esc(acc["title"])}</summary>')
            lines.append('      <div class="feed-accordion-body">')
            for feed in acc["feeds"]:
                lines += row(feed, 4)
            lines.append('      </div>')
            lines.append('    </details>')
        lines.append('  </div>')
    lines.append("</noscript>")
    return ("\n" + " " * column).join(lines)


def _html_text(value, column: int, *, key: str) -> str:
    """HTML 텍스트·속성값. 여러 줄 문구는 마커가 선 열에 맞춰 이어 붙여 원문의
    줄 나눔과 들여쓰기를 되살린다 — 그래야 생성물 diff 가 문구 변경만 보인다.

    복수형 매핑(one·other)은 받지 않는다. 고르는 일을 하는 것은 스크립트의
    fmt() 이고 그쪽으로 가는 길은 {{j:}} 마커뿐이다. 여기로 매핑이 오면 문구를
    쓴 사람이 마커를 잘못 골랐거나 조립기가 아닌 키를 매핑으로 바꾼 것이다 —
    어느 키인지 말하고 죽는다. 그냥 두면 html.escape 가 AttributeError 로 죽어
    locale 의 어디가 문제인지 알려주지 않는다."""
    if isinstance(value, dict):
        raise ValueError(
            f"t 마커는 매핑을 받지 않는다 — 키 {key!r}. 복수형 매핑은 "
            "{{j:}} 마커로만 쓸 수 있다(스크립트의 fmt 가 고른다)"
        )
    escaped = html.escape(value, quote=True)
    for name, number in FALLBACK_COUNTS.items():
        escaped = escaped.replace(
            "{" + name + "}", f'<span data-{name.replace("_", "-")}>{number}</span>'
        )
    return escaped.replace("\n", "\n" + " " * column)


def _fmt_marker_spans(template: str) -> frozenset[int]:
    """복수형 매핑을 받을 수 있는 {{j:}} 마커가 선 **자리**. 템플릿이 이미 알고
    있는 사실이라 유도한다 — fmt() 의 첫 인자로 선 마커의 시작 오프셋이다.

    자리로 판정하는 이유
    --------------------
    처음에는 키 이름 집합("이 키는 fmt 를 탄다")으로 판정했다. **그것은 대리
    지표였고 한 자리가 다른 자리를 승인했다.** 같은 키를 fmt 밖에서 한 번 더
    쓰면 — `set("de-events", {{j:count}})` — 그 자리도 통과해 객체 리터럴이
    textContent 에 들어가고 "[object Object]" 가 나갔다. 실측으로 재현됐다.
    키 이름은 "어딘가에서 fmt 를 탄다" 만 말한다. 물어야 하는 것은 **지금 이
    자리가 fmt 호출 안이냐** 하나뿐이고, 그 답은 자리로만 나온다.

    "키 집합이 간단한데" 로 되돌리지 말 것. 간단한 쪽이 조용히 샌다.

    이 판정이 template.html 문면에 결합한다는 것
    -------------------------------------------
    정규식이 보는 것은 `fmt(` 바로 뒤에 선 마커뿐이다. 어긋남은 두 방향인데
    **둘 다 조용하지 않다.**

        놓치는 쪽 — 호출 방식이 바뀌면(변수에 담아 넘기거나, 이름을 바꾸거나,
        인자 순서를 뒤집으면) 그 자리가 집합에서 빠진다. 매핑이 거부되어
        render 가 멈춘다.
        남는 쪽 — 이제 없다. 자리로 보므로 한 자리가 다른 자리를 승인하지
        못한다. 주석이나 죽은 문자열 안의 `fmt(` 도 자기 자리만 허용한다.

    주석인지 아닌지는 보지 않는다. 판별하려 들면 JS 파서를 만들게 되고, 그
    비용은 이 파일이 질 것이 아니다. 근거는 "그 자리가 fmt 호출 안이냐" 하나로
    충분하다 — 주석 안 자리가 무해한 것은 그 규칙의 **결과이지 근거가 아니다.**

    스캔이 빈손이면 가드로 멈춘다. 조립기가 하나도 안 잡히는 것은 템플릿이
    fmt 를 안 쓴다는 뜻이거나 이 정규식이 낡았다는 뜻인데, 둘 다 조용히
    지나가면 복수형 검사 전체가 무력해진다(tests/test_de_scope.py 의
    assert STATE_CODES 와 같은 형태)."""
    spans = frozenset(m.start(1) for m in FMT_CALL.finditer(template))
    if not spans:
        raise ValueError(
            "템플릿에서 fmt() 를 타는 {{j:}} 마커를 하나도 찾지 못했다 — "
            "fmt 호출 방식이 바뀌었거나 FMT_CALL 이 낡았다"
        )
    return spans


def _js_string(value, *, key: str, at_fmt: bool) -> str:
    """JS 문자열 리터럴 — 따옴표까지. {n}·{date} 는 그대로 남긴다(스크립트 몫).

    받는 것은 문자열과 복수형 매핑(one·other) 둘뿐이다. 그 밖의 타입은 거부한다 —
    json.dumps 는 리스트도 숫자도 통과시키고, 그 값이 textContent 에 들어가면
    빈 라벨이나 "7" 이 되어 나간다. 양방향 검사도 PLURAL_FORMS 도 그것을 보지
    않으므로 생성 시점에 여기서 막는다.

    매핑은 fmt() 안에 선 마커에만 허용한다(at_fmt — _fmt_marker_spans 가 자리로
    판정한다). 갈래를 고르는 것은 fmt 뿐이고, 그 밖의 자리는 값을 그대로 쓰므로
    매핑이 가면 "[object Object]" 가 찍힌다 — 복사 버튼 열다섯 개에 그것이 나간
    것을 실측했다.

    형태를 보는 이유는 잘못된 형태가 조용히 지나가기 때문이다. 갈래 하나를
    빠뜨린 locale 은 render 를 멈추지 않고, 생성물도 정상으로 보이고, 테스트도
    녹색이다(ui 문구를 검사하는 테스트가 없다). 깨지는 것은 브라우저에서 그
    블록 하나이고, 그때는 이미 발행된 뒤다.

    script 문맥의 이스케이프는 _script_json 이 든다 — 이 페이지의 다른 script
    문맥(feed-data 블록)과 같은 함수를 타야 해서 그쪽으로 옮겼다.
    """
    if not isinstance(value, (str, dict)):
        raise ValueError(
            f"{{{{j:}}}} 마커는 문자열이나 복수형 매핑만 받는다 — "
            f"키 {key!r} 이 {type(value).__name__} 이다"
        )
    if isinstance(value, dict):
        if not at_fmt:
            raise ValueError(
                f"복수형 매핑은 fmt() 안에 선 마커에만 쓸 수 있다 — 키 {key!r} 이 "
                "쓰인 이 자리는 값이 그대로 들어가는 자리라 매핑이 가면 "
                '"[object Object]" 가 찍힌다'
            )
        missing = sorted(PLURAL_FORMS - set(value))
        unknown = sorted(set(value) - PLURAL_FORMS)
        if missing or unknown:
            raise ValueError(
                f"복수형 매핑은 {sorted(PLURAL_FORMS)} 를 정확히 들어야 한다 — "
                f"키 {key!r}: 빠진 갈래 {missing}, 모르는 갈래 {unknown}"
            )
        bad = sorted(k for k, v in value.items() if not isinstance(v, str))
        if bad:
            raise ValueError(
                f"복수형 매핑의 값은 문자열이어야 한다 — 키 {key!r} 의 {bad}"
            )
    return _script_json(value)


def _fill_markers(template: str, strings: dict) -> str:
    used: set[str] = set()
    fmt_spans = _fmt_marker_spans(template)

    def sub(match: re.Match) -> str:
        kind, key = match.group(1), match.group(2)
        if key not in strings:
            raise ValueError(f"템플릿의 {{{{{kind}:{key}}}}} 가 locale 에 없다")
        used.add(key)
        value = strings[key]
        if kind == "j":
            return _js_string(value, key=key, at_fmt=match.start() in fmt_spans)
        column = match.start() - template.rfind("\n", 0, match.start()) - 1
        return _html_text(value, column, key=key)

    out = MARKER.sub(sub, template)
    unused = sorted(set(strings) - used)
    if unused:
        raise ValueError(f"locale 에 있는데 템플릿이 쓰지 않는 키: {unused}")
    leftover = [
        m
        for m in re.findall(r"\{\{[^}]*\}\}", out)
        if m not in (PLACEHOLDER, LINKS_PLACEHOLDER, NOSCRIPT_PLACEHOLDER)
    ]
    if leftover:
        raise ValueError(f"치환되지 않은 마커: {sorted(set(leftover))}")
    return out


def render(lang: str = ROOT_LANG) -> str:
    """파일에 쓸 문자열. 템플릿에 두 플레이스홀더가 정확히 하나씩 있어야 한다."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for placeholder in (PLACEHOLDER, LINKS_PLACEHOLDER, NOSCRIPT_PLACEHOLDER):
        if template.count(placeholder) != 1:
            raise ValueError(f"template.html 에 {placeholder} 가 {template.count(placeholder)}개다")
    locale = _load_yaml(LOCALES_DIR / f"{lang}.yaml")
    # 문구 마커를 먼저 채우고 feed-data·링크를 넣는다. 잔존 마커 검사가 JSON 의
    # 중괄호를 보지 않게 하기 위해서다(두 플레이스홀더는 검사에서 뺀다).
    page = _fill_markers(template, _ui_strings(locale, lang))
    at = page.index(LINKS_PLACEHOLDER)
    column = at - page.rfind("\n", 0, at) - 1
    page = page.replace(LINKS_PLACEHOLDER, _lang_links(lang).replace("\n", "\n" + " " * column))
    at = page.index(NOSCRIPT_PLACEHOLDER)
    column = at - page.rfind("\n", 0, at) - 1
    page = page.replace(NOSCRIPT_PLACEHOLDER, _noscript(lang, column))
    return page.replace(PLACEHOLDER, _dumps_feed_data(feed_data(lang)))


if __name__ == "__main__":  # pragma: no cover
    import sys

    # 인자 없이 돌면 locales/ 의 언어 전부를 각자 경로에 쓴다. 인자는 언어
    # 코드다 — 경로가 아니다. 경로는 언어에서 유도되므로 사람이 정하지 않는다.
    for _lang in sys.argv[1:] or languages():
        _target = output_path(_lang)
        _target.parent.mkdir(parents=True, exist_ok=True)
        _target.write_text(render(_lang), encoding="utf-8")
        print(f"[landing] {_lang} → {_target.relative_to(ROOT)}")
