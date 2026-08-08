# AGENTS.md

에이전트·자동화 도구가 이 레포에서 지켜야 할 최소 규약.

## 실행

테스트는 반드시 `uv run pytest` 로 돌린다. 시스템 python 을 쓰지 말 것.
`pytest` 를 그냥 부르면 의존성이 없어 exit 127 로 죽는다. 그 상태로 리뷰를
진행하면 테스트를 돌린 것이 아니라 읽기만 한 것이 된다.

```bash
uv sync              # 의존성
uv run pytest        # 테스트
uv run ruff check .  # 린트
```

## 인증키

- KASI 인증키는 환경변수 `KASI_SERVICE_KEY` 또는 `.env` 에서만 읽는다.
  운영에서는 GitHub Actions Secret 으로만 주입한다.
- 코드·커밋·테스트 픽스처에 키를 넣지 말 것.
- **로그와 예외 메시지에 키가 실리지 않게 할 것.** 이 API 는 인증키를 쿼리
  문자열로 받으므로, 요청 URL 이 그대로 올라가면 키가 그대로 노출된다.
  외부로 나가는 문자열은 `sources/kr/kasi_client.py` 의 `scrub()` 을 통과시킨다.

## 그 밖의 규약

`CLAUDE.md` 를 볼 것. 리뷰 절차, UID·구독 URL 불변 규칙, 데이터 표의 근거 표기
규약이 거기 있다.

설계 결정은 `DESIGN.md` 와 각 YAML 의 주석·`open_questions` 에 있다.

**이 파일에 그 내용을 옮겨 적지 말 것.** 두 곳에 적으면 한 곳만 갱신된다.
