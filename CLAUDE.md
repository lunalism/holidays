## 브랜치·PR (정본: `docs/branch-rules.md`)
- 접두사 4종만: `feat/` `fix/` `docs/` `data/`. 이슈 번호는 이름에 넣지 않는다.
- `data/` 포함 모든 브랜치는 PR 을 거친다. `main` 직푸시 금지, 긴급 예외 없음.
- 병합은 merge commit 고정. squash 금지 — 개별 커밋의 근거가 뭉개진다.
- 데이터 근거의 정본은 커밋 메시지가 아니라 YAML 의 `source` 필드다.

## 이 레포 고유 사항
- UID 네임스페이스: @holidays.lunalism.com (잠정, 출시 전 재확인)
- 구독 URL과 UID는 한 번 공개되면 변경 불가. 관련 값을 바꾸는 제안은 먼저 경고할 것.
- 커밋 전 반드시: API 키·인증정보가 코드에 섞이지 않았는지 확인할 것.
- 실행 명령(`uv run pytest` 등)과 키 취급 규약은 AGENTS.md 에 있다.
  거기가 원본이다. 여기 옮겨 적지 말 것 — 두 곳에 적으면 한 곳만 갱신된다.
