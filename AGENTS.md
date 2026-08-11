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

- KASI 인증키는 환경변수 `KASI_SERVICE_KEY` 에서 읽는다.
  로컬에서는 `.env` 로 대신할 수 있다(`.env` 는 gitignore 대상).
  CI 에서는 GitHub Actions Secret `KASI_SERVICE_KEY` 로 주입한다 —
  `.github/workflows/publish.yml` 의 "피드 생성" 스텝이 그 자리다.
  설정 방법은 README 의 "발행" 절에 있다.
- 발행 워크플로는 아직 `schedule` 이 비활성이다. UID 네임스페이스가 잠정이라
  첫 발행을 보류했다. 자세한 것은 `DESIGN.md` 의 발행 파이프라인 참조.
- 코드·커밋·테스트 픽스처에 키를 넣지 말 것.
- **로그와 예외 메시지에 키가 실리지 않게 할 것.** 이 API 는 인증키를 쿼리
  문자열로 받으므로, 요청 URL 이 그대로 올라가면 키가 그대로 노출된다.
  외부로 나가는 문자열은 `core/secrets.py` 의 `scrub()` 을 통과시킨다.
  (`sources/kr/kasi_client.py` 의 `scrub()`·`mask()`·`key_forms()` 는 그것을
  KASI 키에 맞춰 부르는 얇은 껍데기다.)
- **저장소에 커밋되는 산출물도 "외부로 나가는 문자열"이다.**
  `logs/build.jsonl` 의 `error` 필드가 그렇다. 이 파일은 커밋되고 Pages 를
  붙이면 공개 URL 로 서빙되므로, `core/buildlog.py` 가 기록 직전에 `scrub()`
  을 건다. 지울 대상은 환경변수 **이름**으로 찾는다(`KEY`·`TOKEN`·`SECRET`·
  `PASSWORD`·`CREDENTIAL` 포함). 목록으로 관리하면 새 비밀값을 넣을 때 갱신을
  잊고, 잊은 것은 유출된 뒤에야 드러난다.
  산출물을 늘릴 때는 그것도 공개된다고 보고 같은 규약을 적용할 것.

## 브랜치·PR

정본은 `CLAUDE.md` 의 같은 절이고, 전문은 `docs/branch-rules.md` 에 있다.
아래 네 줄은 **의도한 중복**이다 — 이 파일만 읽고 `CLAUDE.md` 는 읽지 않는
도구가 있을 수 있어서 요약만 둔다. 어긋나면 `CLAUDE.md` 가 맞다.
늘리지 말 것. 늘어나면 아래 "옮겨 적지 말 것"이 무너진다.

- 접두사 4종만: `feat/` `fix/` `docs/` `data/`. 이슈 번호는 이름에 넣지 않는다.
- `data/` 포함 모든 브랜치는 PR 을 거친다. `main` 직푸시 금지, 긴급 예외 없음.
- 병합은 merge commit 고정. squash 금지 — 개별 커밋의 근거가 뭉개진다.
- 데이터 근거의 정본은 커밋 메시지가 아니라 YAML 의 `source` 필드다.

## 그 밖의 규약

`CLAUDE.md` 를 볼 것. 리뷰 절차, UID·구독 URL 불변 규칙, 데이터 표의 근거 표기
규약이 거기 있다.

설계 결정은 `DESIGN.md` 와 각 YAML 의 주석·`open_questions` 에 있다.

**이 파일에 그 내용을 옮겨 적지 말 것.** 두 곳에 적으면 한 곳만 갱신된다.
