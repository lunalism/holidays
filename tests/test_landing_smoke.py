"""브라우저 스모크 — render() 가 낸 페이지가 브라우저에서 성립하는가.

근거는 docs/browser-smoke.md 다. 무엇을 잡고 무엇을 잡지 않는지, 상태를 어떻게
먹이는지, 로컬에 바이너리가 없으면 어떻게 되는지는 전부 그 문서가 정했고 여기는
그것을 옮긴 것이다. 여기와 문서가 어긋나면 여기가 틀린 것이다.

검사 셋(문서 「무엇을 잡는가 — 셋」)
----------------------------------
    콘솔 error 0 그리고 페이지 오류(미처리 예외) 0   — 둘은 다른 경로로 온다
    구독 행 수 == feed-data 의 피드 수
    data-pending 잔여 0                              — DOM 속성 기준

세 번째는 **DOM 속성으로 센다.** 가시성 기준 질의(:visible, state="hidden",
to_be_hidden …)는 이 모듈 어디에도 없다. 블록 하나가 예외를 내면 스크립트의
render() 가 삼키고 fail() 이 컨테이너를 숨기는데 속성은 그대로라, 보이는 것만
세면 0 이 되어 통과한다. PR #83 형이 그 경로이고 아래 메타 테스트가 그것을
고정한다.

도구
----
Playwright(Python) 동기 API 를 직접 쓴다. pytest-playwright 플러그인은 들이지
않는다 — 의존 넷이 더 붙고, 테스트 ID 에 브라우저 이름이 끼어 -k 가 바뀌고,
플러그인의 세션 픽스처와 sync_playwright() 를 한 세션에서 섞으면 "Sync API inside
the asyncio loop" 으로 깨진다. 버전은 pyproject 의 dev 그룹이 == 로 고정한다 —
브라우저 리비전이 패키지 버전에 1:1 로 묶이므로(패키지 안 browsers.json) 결과를
정하는 외부 기준이다. 브라우저는 headless shell 만 쓴다.

로컬 준비
---------
바이너리는 패키지에 들어 있지 않다. 한 번 받는다:

    uv run playwright install --only-shell chromium

없으면 이 모듈은 **실패한다.** 스킵하지 않는다(문서 「로컬에 바이너리가 없으면」).
CI 안에서 캐시 복원이 어긋나 바이너리 없이 초록이 되는 것이 가장 나쁜 결과라
스킵 경로 자체를 두지 않는다. launch 실패 메시지가 위 명령을 다시 알린다.

상태
----
테스트가 rules.status.render 로 지금 코드에서 만든다. 커밋된 status.json 은 읽지
않는다 — 발행 run 의 테스트 스텝이 status 생성 스텝보다 앞이라 스키마를 바꾸는
PR 이 교착이 된다(문서 「무엇을 대상으로 하는가」). 시계는 실제 시각이다. 검사는
값을 보지 않으므로 바이트 결정성이 필요 없다.

외부 요청
---------
알려진 외부 호스트(KNOWN_EXTERNAL_HOSTS)는 빈 성공 응답으로 대체하고, 모르는
외부는 차단한다. 차단은 콘솔에 리소스 실패로 남아 첫째 검사를 깨므로 새 외부
의존은 여기서 드러난다(문서 「외부 요청은 규칙이 안다」).
"""

from __future__ import annotations

import datetime as dt
import http.server
import json
import socketserver
import threading
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import yaml
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from landing import render
from rules import status as status_module

LANGS = render.languages()
every_page = pytest.mark.parametrize("lang", LANGS)

# data-pending 이 전부 떼일 때까지 기다리는 제한 시간(초). 정상 페이지는 로컬에서
# 1 초 안에 끝나고, 실패 페이지는 조건이 영원히 참이 되지 않아 이 값을 다 쓴다.
# 느린 러너에서 정상 페이지가 빨개지지 않을 만큼 넉넉히 두되, 값의 적정성은 CI
# 실측으로 판단한다(문서 「대가와 그 처리」 마지막 항목).
PENDING_TIMEOUT_S = 10

# 페이지가 로컬 서버 밖으로 보내는 요청 중 **알려진** 것. 지금은 template.html 의
# 폰트 CDN(<link rel="stylesheet" href="https://cdn.jsdelivr.net/…">) 하나다.
# 여기 있는 호스트는 빈 성공 응답으로 대체된다 — 배포처 장애가 빨간 신호가 되지
# 않게. 여기 없는 외부 호스트는 차단되고, 차단은 콘솔 error 로 남아 첫째 검사를
# 깬다. 새 외부 의존을 들이려면 이 목록에 적어야 하고, 그것이 의도다.
KNOWN_EXTERNAL_HOSTS = frozenset({"cdn.jsdelivr.net"})

INSTALL_COMMAND = "uv run playwright install --only-shell chromium"

# 스크립트가 세운 구독 행. noscript 안에도 같은 class 의 마크업이 있지만 JS 가 켜진
# 브라우저는 noscript 내용을 요소로 세우지 않으므로 여기에 잡히지 않는다.
ROW_SELECTOR = "#feed-groups .feed-row"


# ---------------------------------------------------------------------------
# 서빙
# ---------------------------------------------------------------------------


def feed_count(lang: str) -> int:
    """feed-data 블록이 드는 피드 수 — 묶음의 feeds 와 아코디언의 feeds 를 합친 것.

    스크립트는 그 둘을 각각 buildRow 로 한 줄씩 세운다."""
    total = 0
    for group in render.feed_data(lang)["groups"]:
        total += len(group["feeds"])
        if "accordion" in group:
            total += len(group["accordion"]["feeds"])
    return total


def write_site(site: Path, pages: dict[str, str] | None = None) -> None:
    """면들과 status.json 을 site/ 아래 발행 배치 그대로 쓴다.

    페이지 경로는 output_path(lang) 을 ROOT 기준 상대경로로 빌린 것 — 루트 언어는
    index.html, 나머지는 <lang>/index.html. pages 를 주면 그 언어들만 그 HTML 로 쓴다
    (메타 테스트가 render 를 monkeypatch 한 ko 하나를 넣는 자리); 없으면 세 면 전부를
    지금 render 로 만든다."""
    for lang in pages or LANGS:
        html = pages[lang] if pages else render.render(lang)
        target = site / render.output_path(lang).relative_to(render.ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
    now = dt.datetime.now(dt.UTC)
    (site / "status.json").write_text(
        status_module.render(today=now.date(), dtstamp=now), encoding="utf-8"
    )


class _SilentHandler(http.server.SimpleHTTPRequestHandler):
    """임시 루트에 없는 경로는 기본 동작대로 404 — 브라우저 콘솔에 리소스 실패로
    남아 첫째 검사에 걸린다. 요청 로그는 pytest 출력에 섞이지 않게 죽인다."""

    def log_message(self, *args) -> None:  # noqa: D401 — 표준 시그니처
        pass


def serve(site: Path) -> tuple[socketserver.TCPServer, str]:
    def handler(*args, **kwargs):
        return _SilentHandler(*args, directory=str(site), **kwargs)

    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    host, port = httpd.server_address[:2]
    return httpd, f"http://{host}:{port}"


@pytest.fixture(scope="module")
def site_url(tmp_path_factory):
    site = tmp_path_factory.mktemp("site")
    write_site(site)
    httpd, url = serve(site)
    yield url
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        try:
            launched = playwright.chromium.launch()
        except PlaywrightError as exc:
            # 바이너리 부재만 준비 명령으로 바꿔 알린다. 그 밖의 launch 오류는
            # 환경 문제가 아니라 진짜 오류라 그대로 올린다.
            if "Executable doesn't exist" not in str(exc):
                raise
            pytest.fail(
                "브라우저 바이너리가 없다. 스킵하지 않는다(docs/browser-smoke.md "
                "「로컬에 바이너리가 없으면」). 한 번 받을 것:\n"
                f"    {INSTALL_COMMAND}\n"
                f"원인: {str(exc).splitlines()[0]}"
            )
        yield launched
        launched.close()


# ---------------------------------------------------------------------------
# 관찰
# ---------------------------------------------------------------------------


@dataclass
class Observation:
    lang: str
    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    rows: int = -1
    feeds: int = -1
    pending: int = -1
    wait: str = ""  # "cleared" 또는 "timeout"

    def describe(self) -> str:
        return (
            f"[{self.lang}] wait={self.wait} rows={self.rows} feeds={self.feeds} "
            f"pending(DOM)={self.pending}\n"
            f"  console errors: {self.console_errors}\n"
            f"  page errors:    {self.page_errors}"
        )


def _route(site_url: str):
    """컨텍스트 수준 라우팅 — 로컬은 통과, 알려진 외부는 빈 200, 그 밖은 차단."""
    local = urlsplit(site_url).netloc

    def handle(route):
        parts = urlsplit(route.request.url)
        if parts.netloc == local:
            route.continue_()
        elif parts.hostname in KNOWN_EXTERNAL_HOSTS:
            # 스타일시트 자리에는 text/css 여야 한다 — 다른 MIME 이면 Chromium 이
            # "Refused to apply style" 을 콘솔 error 로 남긴다.
            content_type = "text/css" if parts.path.endswith(".css") else "application/octet-stream"
            route.fulfill(status=200, body="", content_type=content_type)
        else:
            route.abort()

    return handle


def observe(browser, site_url: str, lang: str, timeout_s: float = PENDING_TIMEOUT_S) -> Observation:
    """면 하나를 열어 검사 셋의 재료를 전부 모아 돌려준다. 단언은 하지 않는다.

    제한 시간에 닿아도 예외로 끝내지 않는다 — 그때의 잔여 수와 오류 목록이 실패
    메시지의 내용이다."""
    obs = Observation(lang=lang)
    context = browser.new_context()
    try:
        context.route("**/*", _route(site_url))
        page = context.new_page()
        page.on(
            "console",
            lambda message: (
                obs.console_errors.append(message.text) if message.type == "error" else None
            ),
        )
        page.on("pageerror", lambda error: obs.page_errors.append(str(error)))
        page.goto(site_url + render.page_path(lang), wait_until="load")
        try:
            # DOM 속성 기준. 숨겨진 컨테이너 안의 속성도 센다 — 이 함수의 요점이다.
            page.wait_for_function(
                "document.querySelectorAll('[data-pending]').length === 0",
                timeout=timeout_s * 1000,
            )
            obs.wait = "cleared"
        except PlaywrightTimeoutError:
            obs.wait = "timeout"
        obs.pending = page.evaluate("document.querySelectorAll('[data-pending]').length")
        obs.rows = page.locator(ROW_SELECTOR).count()
        obs.feeds = feed_count(lang)
    finally:
        context.close()
    return obs


# ---------------------------------------------------------------------------
# 스모크 — 문서의 셋
# ---------------------------------------------------------------------------


@every_page
def test_the_page_runs_without_errors_and_settles(browser, site_url, lang):
    obs = observe(browser, site_url, lang)
    assert obs.console_errors == [] and obs.page_errors == [], obs.describe()
    assert obs.rows == obs.feeds, obs.describe()
    assert obs.pending == 0, obs.describe()


# ---------------------------------------------------------------------------
# 검출기의 안전망 — 두 사고를 재현해 관찰 함수가 그 신호를 내는지 본다
# ---------------------------------------------------------------------------

# 실패 페이지는 잔여가 영원히 남아 대기가 제한 시간을 다 쓴다. 재현이 목적이라
# 정상 대기만큼 기다릴 이유가 없다 — 로컬에서 정상 페이지가 0.3 초 안에 끝나므로
# 2 초면 "끝내 안 떼인다" 를 말하기에 충분하고, 둘을 합쳐 4 초로 막는다.
INCIDENT_TIMEOUT_S = 2


def _poisoned_locales(tmp_path: Path, mutate) -> Path:
    """실제 ko.yaml 을 읽어 한 곳만 바꾼 사본 디렉터리. test_landing_contract.py 의
    poisoned_landing 과 같은 관례 — locale 을 손으로 짓지 않는다."""
    locale = yaml.safe_load((render.LOCALES_DIR / "ko.yaml").read_text(encoding="utf-8"))
    mutate(locale)
    locales = tmp_path / "locales"
    locales.mkdir()
    (locales / "ko.yaml").write_text(
        yaml.safe_dump(locale, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return locales


def _serve_ko(tmp_path: Path, page_html: str):
    site = tmp_path / "site"
    site.mkdir()
    write_site(site, pages={"ko": page_html})
    return serve(site)


def test_a_script_terminator_in_the_feed_data_surfaces_as_a_page_error(
    browser, tmp_path, monkeypatch
):
    """PR #92 형. 문구의 </script> 가 feed-data 블록을 일찍 닫아 JSON.parse 가
    던지고 스크립트가 첫 줄에서 죽는다. 지금은 _script_json 이 '<' 를 이스케이프해
    막는다 — d9805d3 의 역으로 json.dumps 로 되돌려 그 상태를 만든다.

    단언은 "검사가 실패했다" 가 아니라 이 사고의 신호다: 미처리 예외가 있고, 행이
    0 이고, 속성이 남는다. 콘솔 error 는 0 이었다 — 그래서 pageerror 를 따로 듣는다."""
    monkeypatch.setattr(
        render,
        "LOCALES_DIR",
        _poisoned_locales(
            tmp_path,
            lambda loc: loc["feeds"]["kr"].__setitem__(
                "desc", loc["feeds"]["kr"]["desc"] + " </script>"
            ),
        ),
    )
    monkeypatch.setattr(render, "_script_json", lambda value: json.dumps(value, ensure_ascii=False))
    httpd, url = _serve_ko(tmp_path, render.render("ko"))
    try:
        obs = observe(browser, url, "ko", timeout_s=INCIDENT_TIMEOUT_S)
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert len(obs.page_errors) >= 1, obs.describe()
    assert obs.rows == 0, obs.describe()
    assert obs.pending > 0, obs.describe()


def test_a_missing_plural_branch_leaves_pending_attributes_behind_hidden_containers(
    browser, tmp_path, monkeypatch
):
    """PR #83 형. 복수형 매핑에서 갈래 하나가 빠지면 fmt 가 undefined.replace 에서
    던지고, 스크립트의 render() 가 그것을 삼켜 fail() 로 넘긴다. 지금은 _js_value
    의 형태 검사가 render 에서 막는다 — 588a4a7 이전처럼 그 검사만 건너뛴다.

    콘솔 error 도, 페이지 오류도, 행 수도 전부 정상이다. 잡는 것은 **DOM 기준
    잔여 하나뿐**이고, 그것이 이 테스트의 존재 이유다: 관찰 함수가 가시성으로 세는
    순간 마지막 단언이 0 을 받아 빨개진다."""
    monkeypatch.setattr(
        render,
        "LOCALES_DIR",
        _poisoned_locales(tmp_path, lambda loc: loc["ui"]["count"].pop("other")),
    )
    strict_js_value = render._js_value

    def lax_js_value(value, *, key, plural):
        if plural and isinstance(value, dict):
            return render._script_json(value)  # 형태 검사 없이 통과 — 옛 상태
        return strict_js_value(value, key=key, plural=plural)

    monkeypatch.setattr(render, "_js_value", lax_js_value)
    httpd, url = _serve_ko(tmp_path, render.render("ko"))
    try:
        obs = observe(browser, url, "ko", timeout_s=INCIDENT_TIMEOUT_S)
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert obs.console_errors == [], obs.describe()
    assert obs.page_errors == [], obs.describe()
    assert obs.rows == obs.feeds, obs.describe()
    # 이 줄이 이 테스트의 존재 이유다. 위 셋이 전부 정상인 사고를 잡는 유일한 그물.
    assert obs.pending > 0, obs.describe()
