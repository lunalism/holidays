"""内閣府 syukujitsu.csv 수집과 캐싱.

이 모듈은 받아서 캐시에 넣기만 한다. 무엇이 정상인지는 cao_parser 가 안다.

--------------------------------------------------------------------------
원본 바이트를 그대로 보존한다
--------------------------------------------------------------------------
캐시는 CP932 바이트를 그대로 쓴다. 디코드한 텍스트를 저장하지 않는다.

디코드한 것을 저장하면 그 시점의 디코드 판단이 기록에 섞인다. 나중에 인코딩
가정이 틀렸다는 것을 알아도 원본이 없어 되돌릴 수 없고, 우리가 무엇을 받았는지
다시 물을 수 없다. 캐시는 관측 기록이므로 받은 그대로여야 한다.

--------------------------------------------------------------------------
조건부 GET 을 우리가 들고 있어야 한다
--------------------------------------------------------------------------
응답에 ETag 와 Last-Modified 가 둘 다 온다. 그런데 함께 오는 것이
`cache-control: no-store` 라 중개 캐시는 아무것도 들고 있지 않는다.
그래서 검증자를 우리가 파일로 저장하고 다음 요청에 직접 실어 보낸다.

원본은 연 1 회(전년 2 월) 한 해씩 늘어난다. 매번 21KB 를 다시 받을 이유가 없고,
304 를 받으면 "그 시점에 안 바뀌었다"는 관측이 하나 더 쌓인다.

다만 304 를 기대하지 말 것. 실측한 결과는 이렇다(2026-08-11).

    If-Modified-Since 만       5 회 전부 200. 서버가 이 헤더를 보지 않는다.
    If-None-Match 만           8 회 중 304 가 4 회.
    같은 URL 을 5 회 HEAD      ETag 가 3 종류로 갈렸다.

ETag 가 요청마다 다른 것은 로드밸런서 뒤의 서버들이 각자 값을 내기 때문으로
보인다. 그래서 같은 파일인데도 붙은 서버에 따라 200 이 온다.

이건 우리가 고칠 수 있는 것이 아니므로 200 을 정상 경로로 다룬다 — 304 는
받으면 이득이고 못 받아도 손해가 없다. 두 헤더를 다 보내는 것은 서버가
언젠가 고쳐질 때를 위해서다(RFC 9110 상 ETag 가 있으면 그쪽이 우선한다).

--------------------------------------------------------------------------
줄어드는 응답이 캐시를 덮지 못하게 한다
--------------------------------------------------------------------------
한국 쪽 CacheWouldLoseData 와 같은 원칙이다. 다만 판정 기준이 다르다.

    한국  연도별 파일이고, 빈 응답(0 건)만 거부한다. 5 → 3 은 지정 취소로
          실제 일어날 수 있어 막을 근거가 없다.
    일본  파일 하나에 1955 년부터 전부 들어 있다. 과거는 확정된 사실이라
          줄어들 이유가 없다. 한 건이라도 줄면 그건 데이터가 아니라 사고다.

그래서 이쪽은 `새 행 수 < 기존 행 수` 를 전부 거부한다. 같은 원칙이 소스의
성질에 따라 다른 임계값으로 나타나는 것이라, 지금 공통 코드로 묶지 않았다
(docs 는 없다 — 아래 CacheWouldLoseData 주석 참조).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from sources.jp import cao_parser

log = logging.getLogger(__name__)

URL = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_PATH = CACHE_DIR / "syukujitsu.csv"
META_PATH = CACHE_DIR / "syukujitsu.meta.json"

TIMEOUT = 30.0

# 사람이 알아볼 수 있는 요청자. 정부 사이트를 익명으로 긁지 않는다.
USER_AGENT = "holidays.lunalism.com feed builder (+https://github.com/lunalism/holidays)"


class CaoError(RuntimeError):
    """내각부 CSV 를 받지 못했다."""


class CacheWouldLoseData(CaoError):
    """새 응답이 기존 캐시보다 적다. 덮지 않았다.

    한국 kasi_client 의 같은 이름 예외와 같은 목적이고 구현은 따로 둔다.
    묶으려면 "무엇을 세는가"(XML 항목 / CSV 행)와 "얼마나 줄면 사고인가"
    (0 건만 / 한 건이라도)를 둘 다 인자로 빼야 하는데, 그러면 남는 공통
    코드가 `if new < old: raise` 한 줄이다. 그 한 줄을 공유하려고 두 소스의
    판단 기준을 한 자리에 모으면, 다음 소스가 또 다른 기준을 들고 올 때
    그 자리가 국가별 지식의 집합소가 된다. core/ 는 그런 곳이 아니다.
    """


def _read_meta() -> dict:
    try:
        return json.loads(META_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # 메타가 없거나 깨졌으면 조건부 GET 을 포기하고 전체를 받는다.
        # 메타는 편의이지 진실이 아니다. 진실은 캐시된 바이트다.
        return {}


def _write_meta(response_headers, raw: bytes) -> None:
    META_PATH.write_text(
        json.dumps(
            {
                "url": URL,
                "etag": response_headers.get("etag", ""),
                "last_modified": response_headers.get("last-modified", ""),
                "bytes": len(raw),
                "rows": cao_parser.row_count(raw),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def cached() -> bytes:
    """캐시된 원본 바이트. 없으면 CaoError."""
    try:
        return CACHE_PATH.read_bytes()
    except OSError as exc:
        raise CaoError(
            f"캐시가 없다: {CACHE_PATH}\n"
            "먼저 받아 둘 것 — python -m sources.jp.cao_client"
        ) from exc


def fetch(*, force: bool = False, client=None) -> bytes:
    """원본을 받아 캐시에 넣고 바이트를 돌려준다.

    캐시가 있으면 조건부 GET 을 보낸다. 304 면 캐시를 그대로 쓴다.
    force=True 는 검증자를 보내지 않고 전체를 다시 받는다 — 그래도 아래
    검사와 행 수 가드는 그대로 걸린다.
    """
    headers = {"User-Agent": USER_AGENT}
    meta = {} if force else _read_meta()
    have_cache = CACHE_PATH.exists()

    if have_cache and not force:
        if meta.get("etag"):
            headers["If-None-Match"] = meta["etag"]
        if meta.get("last_modified"):
            headers["If-Modified-Since"] = meta["last_modified"]

    owns = client is None
    client = client or httpx.Client(timeout=TIMEOUT, follow_redirects=True)
    try:
        response = client.get(URL, headers=headers)
    except httpx.HTTPError as exc:
        raise CaoError(f"요청이 실패했다: {type(exc).__name__}: {exc}") from None
    finally:
        if owns:
            client.close()

    if response.status_code == 304:
        if not have_cache:
            # 캐시가 없는데 304 가 오면 우리가 보낸 검증자가 잘못된 것이다.
            raise CaoError(
                "304 를 받았는데 캐시가 없다. 검증자만 남고 본문이 사라진 상태다.\n"
                f"{META_PATH} 를 지우고 다시 받을 것."
            )
        log.info("변경 없음 (304). 캐시 사용 %s", CACHE_PATH.name)
        return cached()

    if response.status_code != 200:
        raise CaoError(f"예상치 못한 응답: HTTP {response.status_code}")

    raw = response.content

    # 캐시에 쓰기 전에 읽을 수 있는지 확인한다. 검사 없이 쓰면 오류 페이지가
    # 정상 캐시로 굳고, 다음 실행은 파일이 있다는 이유로 그것을 쓴다.
    try:
        cao_parser.check(raw)
    except cao_parser.CaoParseError as exc:
        raise CaoError(f"응답이 정상 CSV 가 아니다. 캐시에 쓰지 않았다.\n  {exc}") from None

    new_rows = cao_parser.row_count(raw)
    if have_cache:
        old_rows = cao_parser.row_count(cached())
        if new_rows < old_rows:
            raise CacheWouldLoseData(
                f"새 응답이 {new_rows} 행인데 기존 캐시는 {old_rows} 행이다. "
                "캐시에 쓰지 않았다.\n"
                f"  {CACHE_PATH}\n"
                "이 표는 1955 년부터 전부 들어 있고 과거는 확정된 사실이라 줄어들 "
                "이유가 없다. 줄었다면 데이터가 아니라 사고다.\n"
                "응답을 먼저 확인할 것. 그래도 덮어써야 한다면 파일을 직접 지우고 "
                "다시 받을 것 — 지우는 것은 사람이 판단할 일이다."
            )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_bytes(raw)
    _write_meta(response.headers, raw)
    log.info("캐시 저장 %s (%d bytes, %d 행)", CACHE_PATH.name, len(raw), new_rows)
    return raw


if __name__ == "__main__":  # pragma: no cover
    import sys

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    body = fetch(force="--force" in sys.argv)
    rows = cao_parser.check(body)
    print(f"[cao] {len(rows)} 행  {rows[0].day} ~ {rows[-1].day}")
