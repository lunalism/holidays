# KASI 오류 응답 실물

data.go.kr 이 실제로 돌려준 오류 봉투다. 지어낸 것이 아니라 관측한 것이다.
2026-08-08 에 `SpcdeInfoService/getRestDeInfo` 를 일부러 잘못된 키로 호출해 받았다.
실제 인증키는 쓰지 않았고 할당량도 소모하지 않았다.

| 파일 | 보낸 키 | HTTP | errMsg |
|---|---|---|---|
| `service_key_is_not_registered.xml` | 등록되지 않은 문자열 | **403** | `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` |
| `service_key_is_null.xml` | 빈 값 | **401** | `SERVICE_KEY_IS_NULL` |

## 관측 결과가 리뷰 지적과 어긋나는 부분

Codex 리뷰(P2)는 "data.go.kr 이 인증 오류를 HTTP 200 봉투로 준다"고 적었다.
이 엔드포인트에서 관측된 인증 오류는 **401·403 이었다**. 200 이 아니다.

그래서 이 두 파일은 다음을 증명한다.

- `OpenAPI_ServiceResponse` 봉투가 실재한다는 것 (파서가 그 형태를 다루는 근거)
- 오류가 4xx 로 온다는 것 → `raise_for_status()` 가 예외를 던지고,
  그 메시지에 `serviceKey` 가 실린다. **P1(키 유출)이 실제로 밟히는 경로임을 확인한다.**

증명하지 **않는** 것:

- HTTP 200 + `resultCode != 00` 형태. 이 형태는 여기 없다.
  할당량 초과 등에서 그렇게 온다고 알려져 있으나 **확인하지 못했다.**
  확인하려면 실제로 할당량을 태워야 해서 하지 않았다.

  그럼에도 캐시 쓰기 전 검사는 그대로 둔다. HTTP 상태에 기대는 판정은
  200 으로 오는 오류를 놓치고, 그때 오염된 파일이 캐시에 굳는다.
  검사 비용은 XML 파싱 한 번이고 잃을 것이 없다.

## 다시 받으려면

```bash
uv run python - <<'PY'
import httpx
URL = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
print(httpx.get(f"{URL}?serviceKey=THIS_IS_NOT_A_REAL_KEY_0000&solYear=2026", timeout=15).text)
PY
```

응답 형식이 바뀌면 `tests/test_kasi_client.py` 가 먼저 깨진다.
그때 이 파일을 갱신하고 위 표의 HTTP 상태도 함께 고칠 것.
