"""sources/kr/kasi_client.py — 인증키가 새지 않는가, 오류가 캐시에 굳지 않는가.

두 가지 다 Codex 리뷰(2026-08-08)에서 나온 지적이고, 둘 다 실제로 밟히는
경로다. 오류 봉투 실물은 tests/fixtures/kasi_errors/ 에 있다. 지어낸 것이
아니라 관측한 것이며, 어디까지 확인했고 어디부터 확인 못 했는지는 그쪽
README 에 적어 두었다.

네트워크를 쓰지 않는다. httpx.get 을 갈아 끼워 응답을 만든다.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from sources.kr import kasi_client as kc
from sources.kr import kasi_parser as kp

ERROR_DIR = Path(__file__).parent / "fixtures" / "kasi_errors"

# 진짜처럼 생긴 가짜 키. 실제 키는 테스트에 절대 들이지 않는다.
FAKE_KEY = "aB3%2FxQ9zK1pL7mN4vR8t%2BwY6uE0sD5fG2hJ"

NORMAL_BODY = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<response><header><resultCode>00</resultCode>"
    "<resultMsg>NORMAL SERVICE.</resultMsg></header>"
    "<body><items/><numOfRows>100</numOfRows><pageNo>1</pageNo>"
    "<totalCount>0</totalCount></body></response>"
)


def _error_bodies() -> list:
    return sorted(ERROR_DIR.glob("*.xml"))


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """캐시 디렉터리와 호출 카운터를 테스트마다 격리한다.

    진짜 sources/kr/cache/ 를 건드리면 관측 기록이 오염된다.
    """
    monkeypatch.setattr(kc, "CACHE_DIR", tmp_path)
    kc.reset_call_count()
    yield
    kc.reset_call_count()


def _respond(monkeypatch, *, status: int, body: str):
    """httpx.get 을 갈아 끼운다. 요청 URL 을 그대로 실은 응답을 만든다."""

    def fake_get(url, **kwargs):
        request = httpx.Request("GET", url)
        return httpx.Response(status_code=status, text=body, request=request)

    monkeypatch.setattr(kc.httpx, "get", fake_get)


# ---------------------------------------------------------------------------
# 오류 봉투 실물
# ---------------------------------------------------------------------------


def test_env_example_names_the_variable_the_code_reads():
    """.env.example 의 변수명이 코드가 읽는 이름과 같아야 한다.

    어긋나면 예시대로 채워도 MissingServiceKey 가 난다. 실제로 어긋나 있었다
    (KR_DATA_GO_KR_SERVICE_KEY vs KASI_SERVICE_KEY). 키 이름은 조용히 틀리기
    쉬운 자리다 — 틀려도 코드는 멀쩡하고 새로 온 사람만 막힌다.
    """
    example = Path(__file__).parent.parent / ".env.example"
    names = {
        line.split("=", 1)[0].strip()
        for line in example.read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.strip().startswith("#")
    }
    assert kc.ENV_VAR in names, (
        f".env.example 에 {kc.ENV_VAR} 가 없다. 있는 것: {sorted(names)}\n"
        "코드가 읽는 이름은 sources/kr/kasi_client.py 의 ENV_VAR 이다."
    )


def test_error_fixtures_exist():
    """실물이 없으면 아래 테스트들이 조용히 비어 버린다."""
    assert _error_bodies(), (
        f"{ERROR_DIR} 에 오류 봉투 실물이 없다. "
        "지어내지 말고 README 의 재현 방법으로 다시 받을 것."
    )


@pytest.mark.parametrize("path", _error_bodies(), ids=lambda p: p.stem)
def test_error_envelopes_are_rejected_by_the_parser(path):
    """관측된 오류 봉투를 파서가 거부하는지.

    이 봉투는 header/resultCode 가 없는 형태(OpenAPI_ServiceResponse)다.
    errMsg 를 메시지에 실어 무엇이 잘못됐는지 보이게 한다.
    """
    body = path.read_text(encoding="utf-8")
    with pytest.raises(kp.KasiParseError) as exc:
        kp.check_envelope(body)
    assert "resultCode 가 없다" in str(exc.value)
    assert "SERVICE_KEY" in str(exc.value), f"errMsg 가 메시지에 실리지 않았다: {exc.value}"


def test_normal_envelope_passes():
    """정상 봉투는 통과해야 한다. 전부 거부하면 검사가 아니라 고장이다."""
    assert kp.check_envelope(NORMAL_BODY) is not None


def test_result_code_other_than_zero_is_rejected():
    """HTTP 200 인데 resultCode 가 00 이 아닌 형태.

    이 형태의 실물은 확보하지 못했다(할당량을 태워야 나온다).
    tests/fixtures/kasi_errors/README.md 에 그 사실을 적어 두었다.
    여기 쓰는 XML 은 정상 봉투의 코드만 바꾼 것이며, 관측된 실물이 아니다.
    검사하는 것은 봉투 구조가 아니라 "코드가 00 이 아니면 거부한다"는 분기다.
    """
    body = NORMAL_BODY.replace(
        "<resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg>",
        "<resultCode>22</resultCode><resultMsg>LIMITED NUMBER OF SERVICE REQUESTS "
        "EXCEEDS ERROR.</resultMsg>",
    )
    with pytest.raises(kp.KasiParseError) as exc:
        kp.check_envelope(body)
    assert "resultCode=22" in str(exc.value)


# ---------------------------------------------------------------------------
# P1 — 인증키가 예외로 새지 않는가
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", [401, 403, 500])
def test_http_error_never_carries_the_service_key(monkeypatch, status):
    """실패 응답의 예외 메시지에 키가 남지 않아야 한다.

    이 API 는 키를 쿼리 문자열로 받고, httpx 의 HTTPStatusError 메시지에는
    요청 URL 이 통째로 들어간다. 그대로 올라가면 터미널 스크롤백과 CI 로그에
    키가 남는다. 로그에 남은 키는 유출된 키다.

    관측된 실물이 401·403 이라 이 경로는 이론이 아니다.
    """
    body = _error_bodies()[0].read_text(encoding="utf-8")
    _respond(monkeypatch, status=status, body=body)

    with pytest.raises(kc.KasiError) as exc:
        kc._request(kc._build_url(FAKE_KEY, "raw", 2026), FAKE_KEY)

    message = str(exc.value)
    for form in kc.key_forms(FAKE_KEY):
        if form:
            assert form not in message, f"키가 {form!r} 형태로 남았다:\n{message}"
    assert str(status) in message, "무엇이 실패했는지는 남아야 한다"


def test_the_original_exception_is_not_chained(monkeypatch):
    """원본 예외를 물고 가면 트레이스백에 URL 이 다시 찍힌다.

    'During handling of the above exception' 아래로 원본이 그대로 나오면
    스크럽이 무의미해진다. raise ... from None 이 그것을 막는다.
    """
    body = _error_bodies()[0].read_text(encoding="utf-8")
    _respond(monkeypatch, status=403, body=body)

    with pytest.raises(kc.KasiError) as exc:
        kc._request(kc._build_url(FAKE_KEY, "raw", 2026), FAKE_KEY)

    assert exc.value.__cause__ is None
    assert exc.value.__suppress_context__ is True


def test_fetch_year_does_not_leak_the_key_either(monkeypatch):
    """fetch_year 경로도 막혔는지. 원래 여기만 빠져 있었다."""
    monkeypatch.setenv(kc.ENV_VAR, FAKE_KEY)
    _respond(monkeypatch, status=403, body=_error_bodies()[0].read_text(encoding="utf-8"))

    with pytest.raises(kc.KasiError) as exc:
        kc.fetch_year(2026)

    for form in kc.key_forms(FAKE_KEY):
        if form:
            assert form not in str(exc.value)


# ---------------------------------------------------------------------------
# P2 — 오류 응답이 캐시에 굳지 않는가
# ---------------------------------------------------------------------------


def test_a_200_error_envelope_is_not_written_to_the_cache(monkeypatch):
    """HTTP 200 으로 온 오류 봉투를 캐시에 쓰면 안 된다.

    쓰면 그 파일이 정상 캐시로 굳는다. fetch_year 는 파일 존재만 보고
    재사용하므로 force=True 없이는 영원히 복구되지 않는다.
    """
    monkeypatch.setenv(kc.ENV_VAR, FAKE_KEY)
    body = _error_bodies()[0].read_text(encoding="utf-8")
    _respond(monkeypatch, status=200, body=body)  # 상태는 정상, 본문은 오류

    with pytest.raises(kc.KasiError) as exc:
        kc.fetch_year(2026)

    assert "캐시에 쓰지 않았다" in str(exc.value)
    assert not kc.cache_path(2026).exists(), "오류 응답이 캐시에 저장됐다"


def test_a_normal_response_is_cached_and_reused(monkeypatch):
    """정상 응답은 저장되고 다음부터는 호출하지 않는다."""
    monkeypatch.setenv(kc.ENV_VAR, FAKE_KEY)
    _respond(monkeypatch, status=200, body=NORMAL_BODY)

    assert kc.fetch_year(2026) == NORMAL_BODY
    assert kc.cache_path(2026).exists()
    assert kc.call_count() == 1

    assert kc.fetch_year(2026) == NORMAL_BODY
    assert kc.call_count() == 1, "캐시가 있는데 다시 불렀다"


def test_the_key_is_never_written_into_the_cache(monkeypatch):
    """저장되는 것은 응답 본문뿐이다. URL 이 섞이면 커밋에 키가 실린다."""
    monkeypatch.setenv(kc.ENV_VAR, FAKE_KEY)
    _respond(monkeypatch, status=200, body=NORMAL_BODY)
    kc.fetch_year(2026)

    saved = kc.cache_path(2026).read_text(encoding="utf-8")
    for form in kc.key_forms(FAKE_KEY):
        if form:
            assert form not in saved


# ---------------------------------------------------------------------------
# 저장된 캐시 일괄 점검
# ---------------------------------------------------------------------------


def test_audit_reports_broken_files_without_deleting_them(tmp_path):
    """오염된 파일을 목록으로만 낸다. 지우지 않는다.

    오염된 파일도 관측 기록이다. 자동으로 지우면 다시 받는 동안 무엇이
    사라졌는지 아무도 모른다.
    """
    broken = tmp_path / f"{kc.OPERATION}_2099.xml"
    broken.write_text(_error_bodies()[0].read_text(encoding="utf-8"), encoding="utf-8")
    healthy = tmp_path / f"{kc.OPERATION}_2098.xml"
    healthy.write_text(NORMAL_BODY, encoding="utf-8")

    found = kc.audit_cache()
    assert [path.name for path, _ in found] == [broken.name]
    assert broken.exists(), "점검이 파일을 지웠다"
    assert "지우지 않았다" in kc.audit_cache_report()


def test_the_committed_cache_is_clean():
    """레포에 커밋된 캐시 17 개가 전부 정상 봉투인지.

    이 파일들은 오류 검사가 없던 시절에 저장된 것이다. 그때 오류 응답이
    섞여 들어갔을 수 있어 일괄 확인한다.

    통과한다고 내용이 맞다는 뜻은 아니다. '오류 응답이 저장되지 않았다'까지다.
    내용 대조는 tests/test_source_agreement.py 가 한다.
    """
    real_cache = Path(__file__).parent.parent / "sources" / "kr" / "cache"
    paths = sorted(real_cache.glob(f"{kc.OPERATION}_*.xml"))
    if not paths:
        pytest.skip("커밋된 캐시가 없다.")

    broken = []
    for path in paths:
        try:
            kp.check_envelope(path.read_text(encoding="utf-8"))
        except kp.KasiParseError as exc:
            broken.append(f"  {path.name}: {exc}")

    assert not broken, (
        f"커밋된 캐시 {len(broken)}/{len(paths)} 개가 정상 봉투가 아니다:\n"
        + "\n".join(broken)
        + "\n자동으로 지우지 말 것. 파일을 열어 무엇이 저장됐는지 확인할 것."
    )
