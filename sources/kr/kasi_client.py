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
force=True 라도 빈 응답이 항목 있는 캐시를 덮는 것은 막는다(CacheWouldLoseData).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import quote, unquote

import httpx

from sources.kr import kasi_parser

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


class CacheWouldLoseData(KasiError):
    """빈 응답이 항목 있는 캐시를 덮으려 했다. 쓰지 않았다.

    resultCode 00 에 항목만 0 건인 응답은 봉투 검사를 통과한다. 그래서
    check_envelope 로는 걸리지 않는다. 관측 기록이 조용히 지워지는 것을
    막는 것은 이 예외의 몫이다.
    """


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
    """한 번 호출한다. 실패하면 키를 지운 KasiError 로 바꿔 던진다.

    스크럽을 여기 두는 것이 요점이다. 호출자마다 넣으면 다음에 생기는 호출자가
    반드시 빠뜨린다. 실제로 try_key_modes() 는 감싸고 있었는데 fetch_year() 는
    빠져 있었다.

    왜 필요한가. 이 API 는 인증키를 쿼리 문자열로 받고, httpx 의
    HTTPStatusError 메시지에는 요청 URL 이 통째로 들어간다. 그대로 올라가면
    터미널 스크롤백과 CI 로그에 키가 남는다. 로그에 남은 키는 유출된 키다.

    관측된 실물(조사 2026-08-08): 등록되지 않은 키는 403, 빈 키는 401 이 온다.
    즉 이 경로는 이론이 아니라 실제로 밟히는 경로다.
    """
    global _call_count
    if _call_count >= MAX_CALLS_PER_RUN:
        raise CallBudgetExceeded(
            f"한 프로세스에서 {MAX_CALLS_PER_RUN}회를 넘겼다. 루프를 의심할 것. "
            "정상적인 사용은 연도당 1회다."
        )
    _call_count += 1
    log.info("호출 #%d/%d %s", _call_count, MAX_CALLS_PER_RUN, scrub(url, key))

    try:
        response = httpx.get(url, params=params, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        # 예외 본문뿐 아니라 타입 이름까지 함께 실어 보낸다. 스크럽을 거치므로
        # 키는 남지 않고, 무엇이 실패했는지는 그대로 남는다.
        raise KasiError(scrub(f"{type(exc).__name__}: {exc}", key)) from None
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


def _cached_item_count(path: Path) -> int:
    """기존 캐시의 항목 수. 셀 수 없으면 None.

    None 은 "비교할 수 없다"는 뜻이고, 그때 가드는 비켜선다. 깨진 캐시를
    force=True 로 덮어써 복구하는 경로가 있고(audit_cache_report 참조),
    읽히지도 않는 파일을 지키느라 그 경로를 막으면 안 된다.

    0 과 None 을 구분해 둘 필요는 없다. 둘 다 덮어쓰기를 허용하는 쪽이다.
    호출부에서 truthy 검사 하나로 처리한다.
    """
    try:
        return kasi_parser.item_count(path.read_text(encoding="utf-8"))
    except (OSError, kasi_parser.KasiParseError):
        return None


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

    # 캐시에 쓰기 전에 봉투를 확인한다. 검사는 kasi_parser 가 한다 — 응답 구조를
    # 아는 곳은 거기 하나여야 한다. 여기서 XML 을 뜯으면 검사가 두 벌이 되고,
    # 한쪽만 고쳐 놓으면 저장은 되는데 읽지 못하는 파일이 생긴다.
    #
    # 검사 없이 쓰면 오류 응답이 정상 캐시로 굳는다. fetch_year 는 파일 존재만
    # 보고 재사용하므로 force=True 없이는 영원히 복구되지 않고, 그 파일이
    # sources/kr/cache/ 에 커밋되면 관측 기록 자체가 오염된다.
    try:
        kasi_parser.check_envelope(body)
    except kasi_parser.KasiParseError as exc:
        raise KasiError(
            f"{year} 년 응답이 정상 봉투가 아니다. 캐시에 쓰지 않았다.\n  {exc}"
        ) from exc

    # 봉투는 멀쩡한데 항목만 0 건인 응답이 있다. 2029~2031 이 실제로 그렇다
    # (resultCode 00 / NORMAL SERVICE / totalCount 0). 아직 발표되지 않은
    # 구간에서는 그것이 정상이므로 빈 응답 자체를 거부할 수는 없다.
    #
    # 거부해야 하는 것은 그 빈 응답이 "항목이 있던 캐시"를 덮는 경우다.
    # 그 순간 관측 기록이 사라지고, 남는 것은 다른 해의 빈 캐시와 구분되지 않는
    # 249 바이트짜리 파일뿐이다. "원래 없었다"와 "받아 왔는데 없어졌다"가
    # 합쳐져 버리고, 되돌리려면 git 을 뒤지는 수밖에 없다.
    #
    # 실제로 밟힐 수 있는 경로다. 특일정보 활용기간 만료일이 2028-08-08 이고
    # (kasi_names.yaml 참조), 만료 후 응답이 어떤 모양인지는 확인되지 않았다.
    #
    # 하향은 막지 않는다. 5 → 3 은 지정 취소나 표기 변경으로 실제로 일어날 수
    # 있는 일이고, 어디까지가 정상인지 정할 근거가 없다. 0 만 다르다 —
    # 한 해에 공휴일이 하나도 없는 일은 없으므로 그건 데이터가 아니라 부재다.
    new_count = kasi_parser.item_count(body)
    if new_count == 0:
        old_count = _cached_item_count(path) if path.exists() else None
        if old_count:
            raise CacheWouldLoseData(
                f"{year} 년 새 응답이 0 건인데 기존 캐시에는 {old_count} 건이 있다. "
                f"캐시에 쓰지 않았다 (기존 {old_count} 건 → 새 응답 {new_count} 건).\n"
                f"  {path}\n"
                "빈 응답이 관측 기록을 덮는 것을 막았다. 응답을 먼저 확인할 것 — "
                "활용기간 만료나 키 문제라면 다시 받아도 같은 것이 온다.\n"
                "그래도 덮어써야 한다면 파일을 직접 지우고 다시 받을 것. "
                "지우는 것은 사람이 판단할 일이다."
            )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    log.info("캐시 저장 %s (%d bytes)", path.name, len(body))
    return body


def audit_cache() -> list:
    """저장된 캐시 파일을 전부 검사한다. (경로, 오류) 목록. 정상이면 빈 목록.

    지우지 않는다. 오염된 파일도 관측 기록이고, 무엇이 어떻게 오염됐는지는
    사람이 봐야 한다. 자동으로 지우면 다시 받아 오는 동안 무엇이 사라졌는지
    아무도 모른다.
    """
    broken = []
    for path in sorted(CACHE_DIR.glob(f"{OPERATION}_*.xml")):
        try:
            kasi_parser.check_envelope(path.read_text(encoding="utf-8"))
        except kasi_parser.KasiParseError as exc:
            broken.append((path, str(exc)))
    return broken


def audit_cache_report() -> str:
    """사람이 읽는 캐시 점검 요약."""
    paths = sorted(CACHE_DIR.glob(f"{OPERATION}_*.xml"))
    broken = audit_cache()
    lines = [f"캐시 점검 — {CACHE_DIR}", f"파일 {len(paths)} 개", ""]
    if not paths:
        return "\n".join(lines + ["  캐시가 비어 있다."])
    if not broken:
        return "\n".join(
            lines
            + [
                "  전부 정상 봉투(resultCode 00).",
                "",
                "  주의: 이것은 '오류 응답이 저장되지 않았다'는 뜻이지 '내용이 맞다'는",
                "  뜻이 아니다. 내용 대조는 tests/test_source_agreement.py 가 한다.",
            ]
        )
    lines += [f"  깨진 파일 {len(broken)} 개:", ""]
    lines += [f"  {path.name}\n    {error}" for path, error in broken]
    lines += [
        "",
        "  지우지 않았다. 각 파일을 열어 무엇이 저장됐는지 확인할 것.",
        "  다시 받으려면 fetch_year(연도, force=True). 그 전에 키부터 확인할 것 —",
        "  인증 실패가 저장된 것이라면 다시 받아도 같은 것이 저장된다.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    import sys

    logging.basicConfig(level=logging.INFO, format="[kasi] %(message)s")
    target_year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    print(fetch_year(target_year))
    log.info("총 호출 %d회", call_count())
