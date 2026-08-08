"""한국천문연구원 특일 정보(SpcdeInfoService) 조회 클라이언트.

    getRestDeInfo — 공휴일 정보 조회

이 모듈은 조회와 캐싱만 한다. 파싱·모델링은 실제 응답 구조를 보고 정한다.
지금은 원시 XML 을 그대로 돌려준다.

--------------------------------------------------------------------------
인증키
--------------------------------------------------------------------------
키는 환경변수 KASI_SERVICE_KEY 에서만 읽는다. 코드에 넣지 않는다.
없으면 같은 이름으로 .env 를 본다(.env 는 gitignore 대상).

공공데이터포털은 인증키를 두 형태로 준다.

    Encoding 키   퍼센트 인코딩된 문자열. '%' 가 들어 있다.
    Decoding 키   원본. '+', '/', '=' 가 들어 있을 수 있다.

어느 쪽을 받았느냐에 따라 보내는 방법이 달라진다. Encoding 키를 일반적인 params
전달로 보내면 '%' 가 다시 '%25' 로 인코딩되어 인증에 실패한다. 반대로 Decoding
키를 인코딩 없이 그대로 붙이면 '+' 가 공백으로 해석되어 실패한다.

그래서 두 방식을 다 준비해 두고 실제로 어느 쪽이 통하는지 확인한다.
추측하지 않는다. try_key_modes() 가 그 확인을 한다.

--------------------------------------------------------------------------
호출 제한
--------------------------------------------------------------------------
일일 트래픽은 10000 이지만 루프 사고 한 번이면 다 태운다.
호출할 때마다 세어서 로그로 남기고, 한 프로세스에서 MAX_CALLS_PER_RUN 을 넘으면
예외를 던진다. 정상적인 사용은 연도당 한 번이므로 이 상한에 닿을 일이 없다.

캐시가 있으면 호출하지 않는다. 같은 연도를 다시 부르려면 force=True 를 줘야 한다.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import quote, unquote

import httpx

log = logging.getLogger(__name__)

# httpx 는 INFO 레벨에서 요청 URL 을 통째로 찍는다. 이 API 는 인증키를 쿼리
# 문자열로 받으므로 그 로그에 키가 그대로 남는다. CI 로그·터미널 스크롤백에
# 남으면 키가 유출된 것과 같다. 모듈을 import 하는 시점에 막는다.
# 이 모듈은 자체 로그에 마스킹한 URL 만 남긴다.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

BASE_URL = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"
OPERATION = "getRestDeInfo"
ENV_VAR = "KASI_SERVICE_KEY"

CACHE_DIR = Path(__file__).parent / "cache"
REPO_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = REPO_ROOT / ".env"

# 한 해 공휴일은 넉넉히 잡아도 100 건을 넘지 않는다. 페이지네이션을 피한다.
NUM_OF_ROWS = 100

# 한 프로세스에서 허용하는 최대 호출 수. 루프 사고 방지용 안전핀이며
# 일일 할당량(10000)과는 다른 층위다. 연도당 1회가 정상이다.
MAX_CALLS_PER_RUN = 20

_call_count = 0


class KasiError(RuntimeError):
    """조회에 실패했다."""


class MissingServiceKey(KasiError):
    """인증키가 없다."""


class CallBudgetExceeded(KasiError):
    """한 프로세스에서 너무 많이 불렀다. 루프를 의심할 것."""


# ---------------------------------------------------------------------------
# 인증키
# ---------------------------------------------------------------------------


def _read_dotenv(path: Path) -> dict:
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def load_service_key() -> str:
    """환경변수 우선, 없으면 .env. 값은 절대 로그에 그대로 남기지 않는다."""
    value = os.environ.get(ENV_VAR) or _read_dotenv(DOTENV_PATH).get(ENV_VAR)
    if not value:
        raise MissingServiceKey(
            f"{ENV_VAR} 가 없다. 환경변수로 넣거나 .env 에 적을 것.\n"
            "키를 코드나 커밋에 넣지 말 것. 운영에서는 Actions Secret 으로만 주입한다."
        )
    return value


def mask(key: str) -> str:
    """로그용. 앞뒤 4자만 남긴다."""
    if len(key) <= 12:
        return "*" * len(key)
    return f"{key[:4]}...{key[-4:]}({len(key)}자)"


def looks_percent_encoded(key: str) -> bool:
    """'%' 가 있으면 Encoding 키로 본다. 확정이 아니라 힌트일 뿐이다."""
    return "%" in key


# ---------------------------------------------------------------------------
# 호출
# ---------------------------------------------------------------------------


def call_count() -> int:
    return _call_count


def reset_call_count() -> None:
    global _call_count
    _call_count = 0


def _build_url(key: str, key_mode: str, year: int, month: int = None) -> str:
    """쿼리 문자열을 직접 만든다.

    params= 로 넘기면 라이브러리가 키를 한 번 더 인코딩해서 Encoding 키가 깨진다.
    어느 형태로 보낼지 이 함수가 통제한다.

        raw      키를 그대로 붙인다. Encoding 키용.
        decoded  키를 한 번 풀고 다시 인코딩한다. Decoding 키용.
    """
    if key_mode == "raw":
        service_key = key
    elif key_mode == "decoded":
        service_key = quote(unquote(key), safe="")
    else:
        raise ValueError(f"모르는 key_mode: {key_mode!r}")

    query = [
        f"serviceKey={service_key}",
        f"solYear={year}",
        f"numOfRows={NUM_OF_ROWS}",
        "pageNo=1",
    ]
    if month is not None:
        query.append(f"solMonth={month:02d}")
    return f"{BASE_URL}/{OPERATION}?" + "&".join(query)


def key_forms(key: str) -> set:
    """이 키가 문자열에 나타날 수 있는 모든 형태.

    이중 인코딩까지 포함해야 한다. 라이브러리가 인코딩 키를 한 번 더 인코딩하면
    '%2B' 가 '%252B' 가 되는데, 그 형태가 예외 메시지에 실려 나온다.
    실제로 params 모드의 403 메시지에 그 형태로 키가 통째로 들어 있었다.
    """
    raw = key
    once = quote(key, safe="")
    return {
        raw,
        once,
        quote(once, safe=""),
        unquote(key),
        quote(unquote(key), safe=""),
    }


def scrub(text: str, key: str) -> str:
    """키가 어떤 형태로 들어 있든 지운다.

    로그·출력·예외 메시지에 넣기 전에 반드시 통과시킬 것.
    긴 형태부터 지워야 짧은 형태가 먼저 걸려 부분 치환되는 일이 없다.
    """
    masked = mask(key)
    for form in sorted(key_forms(key), key=len, reverse=True):
        if form:
            text = text.replace(form, masked)
    return text


def _request(url: str, key: str, timeout: float = 20.0, params: dict = None) -> str:
    global _call_count
    if _call_count >= MAX_CALLS_PER_RUN:
        raise CallBudgetExceeded(
            f"한 프로세스에서 {MAX_CALLS_PER_RUN}회를 넘겼다. 루프를 의심할 것. "
            "정상적인 사용은 연도당 1회다."
        )
    _call_count += 1
    log.info("호출 #%d/%d %s", _call_count, MAX_CALLS_PER_RUN, scrub(url, key))

    response = httpx.get(url, params=params, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return response.text


# ---------------------------------------------------------------------------
# 키 형태 확인
# ---------------------------------------------------------------------------


def try_key_modes(year: int = 2026) -> dict:
    """어떤 전달 방식이 통하는지 실제로 확인한다. 추측하지 않는다.

        raw      쿼리 문자열에 키를 그대로 붙인다
        decoded  한 번 풀고 다시 인코딩해서 붙인다
        params   httpx params= 에 넘겨 라이브러리가 인코딩하게 둔다

    주의 — Encoding 키를 쓰는 경우 raw 와 decoded 는 같은 URL 이 된다.
    이미 퍼센트 인코딩된 문자열을 unquote 했다가 quote 하면 원래대로 돌아오기
    때문이다. 즉 그 조합에서 두 모드가 같이 성공하는 것은 "둘 다 된다"가 아니라
    "구분되지 않는다"는 뜻이다. 실제로 갈리는 것은 params 다.
    아래 결과의 url_identical 이 그 사실을 알려 준다.

    호출을 3회 쓴다. 결과를 기억해 두고 반복하지 말 것.
    """
    key = load_service_key()
    results = {}

    for mode in ("raw", "decoded"):
        url = _build_url(key, mode, year)
        try:
            body = _request(url, key)
            ok = "<resultCode>00</resultCode>" in body
        except Exception as exc:  # noqa: BLE001 - 어떤 실패든 그대로 기록한다
            # 예외 메시지에 URL 이 실려 오고 그 안에 키가 들어 있다. 반드시 지운다.
            results[mode] = {
                "ok": False,
                "error": scrub(f"{type(exc).__name__}: {exc}", key),
                "body": "",
            }
            continue
        results[mode] = {"ok": ok, "error": None, "body": body}

    # 라이브러리에 인코딩을 맡기는 경우. Encoding 키라면 '%' 가 '%25' 가 되어 깨진다.
    try:
        body = _request(
            f"{BASE_URL}/{OPERATION}",
            key,
            params={
                "serviceKey": key,
                "solYear": year,
                "numOfRows": NUM_OF_ROWS,
                "pageNo": 1,
            },
        )
        ok = "<resultCode>00</resultCode>" in body
    except Exception as exc:  # noqa: BLE001
        results["params"] = {
            "ok": False,
            "error": scrub(f"{type(exc).__name__}: {exc}", key),
            "body": "",
        }
    else:
        results["params"] = {"ok": ok, "error": None, "body": body}

    results["url_identical"] = _build_url(key, "raw", year) == _build_url(key, "decoded", year)
    return results


# ---------------------------------------------------------------------------
# 캐시
# ---------------------------------------------------------------------------


def cache_path(year: int) -> Path:
    return CACHE_DIR / f"{OPERATION}_{year}.xml"


def fetch_year(year: int, *, key_mode: str = None, force: bool = False) -> str:
    """그 해 공휴일 원시 XML. 캐시가 있으면 호출하지 않는다.

    key_mode 를 주지 않으면 키 모양으로 고른다('%' 가 있으면 raw).
    그 추정이 틀렸는지는 응답으로 드러난다. try_key_modes() 로 먼저 확인할 것.
    """
    path = cache_path(year)
    if path.exists() and not force:
        log.info("캐시 사용 %s (호출 없음)", path.name)
        return path.read_text(encoding="utf-8")

    key = load_service_key()
    if key_mode is None:
        key_mode = "raw" if looks_percent_encoded(key) else "decoded"

    body = _request(_build_url(key, key_mode, year), key)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    log.info("캐시 저장 %s (%d bytes)", path.name, len(body))
    return body


if __name__ == "__main__":  # pragma: no cover
    import sys

    logging.basicConfig(level=logging.INFO, format="[kasi] %(message)s")
    target_year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    print(fetch_year(target_year))
    log.info("총 호출 %d회", call_count())
