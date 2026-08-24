# Holiday_07 시작 문서

작성: 2026-08-25
기준 리비전: `1f363f5` (main)
이전 세션: Holiday_06 (PR #19, #20, #21, #22)

이 문서는 **코드에 없는 것만** 담는다. jp 피드가 무엇을 어떻게 내는지는 이제 `rules/jp/feed.py` 와 `tests/test_jp_feed.py` 가 들고 있다. 문서가 그것을 다시 서술하면 갈릴 자리만 생긴다 — Holiday_06 §11 의 `basis` 건수가 실제로 그렇게 틀렸고 §10 에 정정이 남아 있다.

그래서 여기 있는 것은 **왜 그렇게 정했는가**, **무엇을 검토했다가 버렸는가**, **다음 브랜치가 무엇을 건드리게 되는가** 셋이다. 사실은 가리키기만 한다.

---

## 0. 이 세션에서 한 일

PR 넷을 열고 닫았다.

**#19 — `docs: holiday_06.md 정정 및 feat/jp-rules 확정 사항 반영`**
Holiday_06 문서의 `basis` 건수 오류와 `PRODID` 서술의 자기모순을 고쳤다. 구현 전에 사양서를 맞춰 둔 것이다. 정정 내역은 그 문서 §10 에 있다.

**#20 — `feat: rules/jp — 일본 공휴일 피드를 만들 수 있게 한다`**
`rules/jp/` 를 신설했다. `data/jp/*.yaml` 8파일을 읽어 `core.ics.Event` 로 옮기고 ICS 를 만들 수 있다. 발행은 하지 않는다 — `feeds/jp.ics` 를 만들지 않았고 워크플로도 건드리지 않았다.

이 브랜치에서 `rules/kr/feed.py` 의 `publish()` 를 jp 쪽에 **의도적으로 복제**했다. 그 판단의 이유는 §3 에 있다.

**#21 — `refactor: publish() 를 core/feed.py 로 올린다`**
복제해 둔 `publish()` 두 벌을 `core/feed.py` 하나로 합쳤다. 순수 이동이고 발행 결과가 바뀌지 않았다 — `git diff main..HEAD -- feeds/ status.json` 이 0바이트였고 `tests/test_published_feed.py` 가 통과했다.

**#22 — `docs: 조사·검증 규약을 AGENTS.md 로 옮긴다`**
아래 §1.

---

## 1. 규약은 이제 어디에 있나

조사·검증 규약이 Holiday_06 §11 에만 있었다. 세션 문서라서 다음 문서를 열 때마다 통째로 복사되고 있었고, 그것이 이 레포가 `CLAUDE.md` 와 `AGENTS.md` 양쪽에서 금지하는 "옮겨 적기" 였다.

**정본은 `AGENTS.md` 의 「조사와 보고」 절이다.** 목록을 여기 다시 적지 않는다. 그 절을 읽으면 된다.

Holiday_06 §11 은 그대로 두었다. 이미 머지된 세션 기록이라 소급해서 고치지 않는다. 그래서 지금 같은 목록이 두 곳에 있고, 새 절이 자기가 정본임을 밝혀 다음 세션 문서가 §11 을 다시 복사하지 않게 해 두었다.

문서 넷의 정본 계층은 이렇다.

| 무엇 | 정본 |
|---|---|
| 조사·검증 방법 | `AGENTS.md` 「조사와 보고」 |
| 실행 명령·키 취급 | `AGENTS.md` 「실행」·「인증키」 |
| 브랜치·PR | `docs/branch-rules.md` (전문). `CLAUDE.md` 와 `AGENTS.md` 는 요약 |
| 설계 결정 | `DESIGN.md` 와 각 YAML 의 주석·`open_questions` |

브랜치 규약의 우선순위는 #22 에서 정리했다. `docs/branch-rules.md` 와 `AGENTS.md` 「브랜치·PR」 절에 있다.

`AGENTS.md` 가 "리뷰 절차는 `CLAUDE.md` 에 있다"고 가리키고 있었으나 레포의 `CLAUDE.md` 에는 없다. 그 항목만 뺐고, 어디에 있는지는 적지 않았다 — 전역 설정 파일에 있는 것으로 보이나 레포 안에서 확인할 수 없다.

---

## 2. jp 피드 — 무엇이 코드에 있나

아래 넷이 정답이다. 내용을 여기 옮기지 않는다.

**`rules/jp/feed.py`** — 무엇을 읽고 무엇을 내는가. 모듈 docstring 에 근거가 갈래별로 적혀 있고, `_summary()` 와 `_description()` 이 SUMMARY·DESCRIPTION 문구의 정본이다. `events()` 가 `data/jp/` 를 읽고, `build()` 가 렌더하고, `publish()` 는 `core.feed.publish()` 를 부르는 얇은 래퍼다. 발행 범위는 `sources.jp.build_data` 에서 import 한다.

**`core/feed.py`** — `publish()` 의 시그니처와 불변식. 읽기·쓰기의 순서와 원자성이 여기 있고, 왜 `core/ics.py` 가 아닌지도 모듈 docstring에 있다.

**`tests/test_jp_feed.py`** — jp 출력이 확정 사양대로 나오는지. 잠정 표시 0줄, 발행 범위, `kind` 와 `basis` 의 동치, `verified` 비노출, 괄호·구분자 코드포인트, UID 유일성, 알려진 세 건의 전문 고정.

**`tests/test_core_feed.py`** — `publish()` 의 불변식. 첫 발행의 `None`, 읽기가 쓰기보다 먼저인 것, 실패 시 원자성, 임시 파일 위치, 가드, 그리고 `core/feed.py` 가 `rules`/`sources` 를 import 하지 않는다는 것.

데이터의 건수와 스키마는 `data/jp/*.yaml` 과 `tests/test_cao_source.py` 가 들고 있다. 이 문서에 숫자를 적지 않는다.

---

## 3. 검토했다가 버린 갈래

**이 절이 이 문서의 핵심이다.** 코드는 무엇을 했는지 들고 있지만 무엇을 안 했는지는 어디에도 없다. 이것이 없으면 다음 세션이 같은 제안을 다시 하고 왜 안 되는지를 처음부터 조사한다.

### `publish(body, path)` — 읽기와 쓰기를 쪼개는 안

**버렸다.**

이미 만든 바이트를 받아 쓰기만 하는 모양이면 함수가 단순해진다. 그러나 그러면 이전 발행본을 언제 읽을지가 호출부의 몫이 된다. 호출부가 순서를 틀릴 수 있게 되고, 틀리면 이전 발행본이 사라진 뒤에야 알게 된다. SEQUENCE 의 진실 공급원이 그 파일이므로 사라진 뒤에는 어느 쪽이 맞는지 우리 쪽에서 알 방법이 없다.

읽기와 쓰기를 한 함수 안에서 순서대로 하는 것이 그 함수의 존재 이유다.

**근거가 남은 곳:** `core/feed.py` 의 `publish()` docstring 「읽기와 쓰기를 쪼개지 않는다」 절. 쪼개자는 제안이 오면 거기를 먼저 읽으면 된다. `tests/test_core_feed.py` 가 "`build_body` 가 도는 시점에 대상 파일이 아직 이전본 그대로인가"를 순서로 검사한다.

### `feed_range()` 를 두 나라가 공유하는 안

**버렸다.**

kr 의 `feed_range(today)` 는 상한을 시계에서 얻는다. jp 의 범위는 시계와 무관한 두 상수다 — 内閣府 CSV 가 담은 구간이 곧 범위이고, 그 구간은 언제 돌리든 같다. 인자 없이 답이 정해지는 것에 함수를 씌우면 시계가 관여하는 것처럼 읽힌다.

이 결정이 `core/feed.py` 의 시그니처까지 이어졌다. `publish()` 가 `today` 도 `dtstamp` 도 받지 않고 클로저가 시계를 들고 가는 것이 그 귀결이다. 두 나라의 차이는 그 클로저가 시계를 들고 가느냐 하나로 줄었다.

**근거가 남은 곳:** `rules/jp/feed.py` 의 `feed_range` 자리에 있는 주석과 `build()` docstring.

### `provisional` 을 `verified: false` 로 채우는 안

**버렸다.**

jp 데이터에 `provisional` 이 없고 `verified` 가 있으니 그 자리에 넣자는 것이었다. 두 필드는 다른 범주다. `provisional` 은 규칙 쪽 사정이고 — 정부가 아직 정하지 않았다 — `verified` 는 우리가 원문을 대조했는가다. 하나를 다른 쪽 자리에 밀어 넣으면 우리 내부 검증 상태가 구독자 캘린더에 `STATUS:TENTATIVE` 로 나간다.

jp 는 `provisional` 이 항상 `False` 다. 발행 범위의 상한이 CSV 의 마지막 날짜라서 정부가 아직 정하지 않은 날짜가 애초에 들어오지 않는다.

**근거가 남은 곳:** `core/ics.py` 의 `_vevent()` 가 SUMMARY 바로 위에 같은 구분을 적어 두었다 — 잠정·미검증 표시를 붙이지 않는다. `rules/jp/feed.py` 모듈 docstring 의 해당 절. `tests/test_jp_feed.py` 가 `verified` 와 `source_todo` 원문이 출력 어디에도 없음을 본다.

### SUMMARY 를 한국어로 옮기는 안

**버렸다.**

kr 피드가 한국어이므로 jp 도 한국어로 옮기자는 것이었다. `天皇誕生日` 같은 이름에서 이 레포가 판정할 일이 아닌 것을 판정하게 된다. 옮기는 순간 어떤 역어를 고르든 그것이 우리 입장이 된다.

SUMMARY 는 일본어 원문을 유지한다. DESCRIPTION 의 서술문은 한국어로 쓰되 축일명과 법령명은 원문을 둔다. 괄호 폭이 SUMMARY 와 DESCRIPTION 에서 갈리는 것도 같은 규칙의 결과다 — 괄호 안 내용의 언어를 따른다.

**근거가 남은 곳:** `rules/jp/feed.py` 모듈 docstring 의 「SUMMARY 는 일본어 원문을 유지한다」 절. Holiday_06 §7 의 「표기 언어」.

### `publish()` 를 복제하지 않고 바로 `core/` 로 올리는 안

**버린 것이 아니라 순서를 바꾼 것이다.** 결국 올렸다. #21 이 그것이다.

`feat/jp-rules` 에서 바로 올릴 수 있었다. 그러지 않고 jp 쪽에 한 벌 복제했다. 신규 구현과 공통화를 한 브랜치에 섞으면 무엇이 무엇을 깼는지 흐려진다는 것이 첫 이유였고, 더 실질적인 이유는 **복제해서 실측해야 차이를 알 수 있다**는 것이었다.

복제해 보니 kr 과 다른 곳이 `build(...)` 호출 한 줄, 즉 `today` 전달 하나였다. 그 사실이 #21 의 입력이 됐다 — core 로 올릴 `publish()` 는 `today` 를 받지 않고, 시계가 필요한 쪽은 `build()` 이며 그것은 국가별로 남는다. 복제 없이 올렸다면 이 판단을 추측으로 했을 것이다.

복제는 별도 커밋으로 떼어 두었고 #21 에서 그 커밋 하나만 보고 판정했다.

**근거가 남은 곳:** #20 의 `publish()` 복제 커밋 메시지와 #21 의 PR 본문. Holiday_06 §6 (4) 가 "이동과 신규 구현을 한 브랜치에 섞으면 무엇이 무엇을 깼는지 흐려진다"고 적은 것이 출발점이었다.

---

## 4. `feat/jp-publish` 의 입력

다음 브랜치는 `feeds/jp.ics` 를 실제로 발행한다. 아래는 `refactor/core-publish` 세션에서 `main` 의 파일을 직접 읽어 확인한 것이다. 문서를 인용하지 않고 파일을 열었다.

### `.github/workflows/publish.yml` — 피드가 하나뿐이라고 가정하는 자리 여섯

- 머리말이 이 워크플로가 쓰는 산출물을 셋으로 열거하고 그중 피드가 하나다
- 피드 생성 스텝이 모듈과 경로를 하나씩만 부른다
- `FEED_CHANGED` 가 값이 `0`/`1` 인 스칼라 변수 하나다. 피드별 상태를 담을 자리가 없다
- 변경 판정 블록이 `feeds/kr.ics` 를 다섯 번 직접 이름으로 쓴다. 반복문이 없다
- 이전본을 담는 임시 파일 `PREV` 도 스칼라 하나다. 피드가 둘이면 서로 덮인다
- 커밋 메시지가 `feat(kr):` 로 국가를 하드코딩한다

비교 대상이 같은 파일 안에 있다. `status.json` 과 `logs/build.jsonl` 은 `for TARGET in ...` 반복문으로 처리한다. 피드만 반복문 밖에 있다.

### `rules/kr/status.py` — 세 자리

- `status()` 가 `rules.kr` 만 import 한다. `rules.jp` 를 부르지 않는다
- 반환 dict 의 `"feed"` 키가 단수이고 값이 dict 하나다. 피드 목록이 아니다
- 그 안의 `path` 가 `feed.FEED_PATH` 를 직접 읽고, 이벤트 수와 범위도 같은 모듈의 함수 하나에서 나온다

### `status.json` — 한 자리

- `"feed"` 키가 단수 오브젝트이고 `kr.ics` 하나를 담는다. 배열이나 국가별 키가 아니다

`status.json` 스키마를 바꾸면 `tests/test_published_feed.py` 가 본다.

### `index.html`

- 구독 URL 이 문자열 하나다
- `status.json` 을 읽는 쪽이 단수 `feed` 키를 직접 참조한다
- jp 구독 링크가 없다

### `rules/jp/feed.py` 에 `__main__` 진입점이 없다

kr 에는 있다. 워크플로가 `python -m rules.kr.feed <경로>` 로 부르는 방식을 jp 에 쓰려면 그 진입점이 필요하다. `feat/jp-rules` 에서 두지 않은 것은 그 브랜치가 발행하지 않기로 했기 때문이고, 두면 `feeds/jp.ics` 를 만들 수 있는 경로가 생겨서다.

`tests/test_jp_feed.py` 가 `feeds/jp.ics` 가 존재하지 않음을 단언한다. 다음 브랜치에서 그 테스트가 걸리므로 거기서 함께 정리하면 된다.

---

## 5. 미결

- **춘분·추분 계산과 内閣府 CSV 의 대조 검사가 레포에 없다.** 이전 세션 기록의 "146/146 일치"는 현재 재현 가능한 산출물이 아니다. `tests/test_cao_source.py` 의 `test_the_equinoxes_are_not_claimed_as_verified()` 는 `verified: false` 여부만 단언하고 날짜를 대조하지 않는다. 상세는 Holiday_06 §9. 검증 하니스 항목으로 남는다
- **`core.astro` 의 실제 소비자가 `rules/kr/astro.py` 하나다.** 프로덕션 코드에서 그 파일 하나가 import 하고, 그 밖에는 `tests/test_lunar.py` 가 섭동 픽스처로 쓴다. `rules/jp/` 는 `core.astro` 를 쓰지 않는다 — jp 는 CSV 날짜를 읽고 계산하지 않는다. `feat/core-astro` 의 승격 근거 자체는 유효하나 아직 행사되지 않았다
- **`昭和41年政令第376号` 원문 미확인.** `建国記念の日` 의 `source_todo` 가 그 정령을 가리키지만 우리는 원문을 보지 않았고, 정령 번호 자체가 확인 대상이다. 확인하면 8건의 `verified: false` 가 동시에 닫힌다. 춘분·추분과 성격이 다르다 — 그쪽은 연도별 관보 고시라 8번 확인해야 하고, 이쪽은 정령 하나가 날짜를 고정했으므로 한 번이면 된다
- **GitHub 레포 설정에서 `Allow squash merging` 과 `Allow rebase merging` 이 켜져 있다.** 이 레포는 머지 커밋만 쓰기로 했고(`docs/branch-rules.md`), 지금은 규율로만 지켜진다. 설정으로 막을지는 정하지 않았다

Holiday_06 §9 의 이월 항목들은 그대로 열려 있다. 여기 다시 적지 않는다.

---

## 6. 레포 밖에서 확인된 것

레포 파일에는 없고 GitHub 저장소 설정에 있는 값이다. 이 문서를 쓰면서 `gh api` 로 다시 확인했다.

- **GitHub Pages 는 `Deploy from a branch` / `main` / `/(root)` 로 서빙한다.** 커스텀 도메인은 `holidays.lunalism.com` 이다. `index.html` 의 "Pages 가 브랜치 루트를 서빙하므로 `feeds/kr.ics` 가 그대로 이 경로가 된다"는 주석이 사실로 확인됐다. Holiday_06 §8 이 미확인으로 남긴 항목이 닫힌다
- **`Automatically delete head branches` 가 켜져 있다.** Holiday_06 §8 이 미확인으로 남긴 다른 한 항목이다. 이번 세션의 브랜치 넷이 머지 후 원격에서 자동으로 사라진 것이 그 결과다

---

## 7. 이번 세션의 교훈

규약이 된 것은 `AGENTS.md` 로 갔다. 여기 남는 것은 아직 규약이 아닌 것들이다.

- **긴 텍스트는 파일 경로로 주고받는다.** PR 본문은 `/tmp` 에 쓰고 `--body-file` 로 올린다. 채팅으로 붙여넣는 방식은 이번 세션에서 세 번 실패했다
- **PR 본문은 만들기 전에 초안을 확인한다.** 만든 뒤에 고치면 이미 알림이 나간 뒤다
- **보고가 길면 `/tmp` 에 쓰고 경로만 알린다.** 화면에 전문을 쏟으면 정작 판단해야 할 항목이 묻힌다

셋 다 이번 세션에서 반복적으로 유효했으나, 규약으로 올릴지는 다음 세션에서 판단한다. 한 세션의 경험으로 `AGENTS.md` 를 늘리면 그 파일이 "최소 규약"이라는 자기 선언을 잃는다.
