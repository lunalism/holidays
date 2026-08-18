# Holiday_05 세션 인계

작성: 2026-08-18
기준 리비전: `1a2a600` (main)
이전 세션: Holiday_04 (PR #14, #15)

---

## 이 세션에서 한 일

PR 세 건을 머지했다. 전부 merge commit, squash 없음.

| PR | 브랜치 | 내용 |
|---|---|---|
| #16 | `docs/data-dir-roles` | `README.md` 의 `data/` 역할 서술을 실제와 맞춤 |
| #17 | `test/perturb-reach` | `perturb` 섭동이 파이프라인에 도달하는지를 테스트가 단언 |
| #18 | `feat/core-astro` | 태양 황경 급수를 `core/astro.py` 로 이동 |

커밋 순서:

```
1a2a600 Merge pull request #18 from lunalism/feat/core-astro
09c0946 (feat/core-astro 본체)
d406a11 Merge pull request #17 from lunalism/test/perturb-reach
f619d16 test: 섭동이 파이프라인에 도달하는지를 테스트가 단언하게 한다
a172b6c Merge pull request #16 from lunalism/docs/data-dir-roles
e81a284 docs: data/ 디렉터리 역할 서술을 실제와 맞춤
```

---

## 이 세션의 핵심 사건

### `{'sun': 0, 'moon': 2031}` — 안전망을 먼저 깐 것이 값을 했다

`feat/core-astro` 로 `apparent_solar_longitude` 와 `solar_term_jde` 를 `core/` 로 옮기자, `tests/test_lunar.py` 의 `perturb` 픽스처가 끊겼다.

원인: `rules/kr/astro.py:278` 이 `apparent_solar_longitude(jde)` 를 **비수식으로** 부른다. 이동 전에는 `monkeypatch.setattr(astro, ...)` 가 `rules.kr.astro.__dict__` 를 갈아끼우고 `solar_term_jde.__globals__` 가 곧 그 dict 이라 도달했다. 이동 후에는 `solar_term_jde.__globals__` 가 `core.astro.__dict__` 가 된다. **재수출은 이름 조회를 살리지 함수의 전역 사전을 공유시키지 않는다.**

여기서 중요한 것은 **깨지는 방식**이다.

```
기존 assert not changed  → 통과 (조용히)
```

섭동이 안 걸리니 결과가 안 흔들리고, 안 흔들리니 `assert not changed` 가 통과한다. **아무것도 검증하지 않는 초록불**이 된다. 이동 브랜치 하나만 떴다면 4건이 영원히 공허하게 초록이 됐을 것이다.

이 세션에서는 PR #17 을 먼저 넣었기 때문에 즉시 빨개졌다:

```
FAILED test_holidays_survive_perturbing_the_series[0.05-0]
FAILED test_holidays_survive_perturbing_the_series[-0.05-0]
FAILED test_a_large_solar_perturbation_does_move_dates[5.0]
FAILED test_a_large_solar_perturbation_does_move_dates[-5.0]

calls = {'sun': 0, 'moon': 2031}
E  AssertionError: 태양 황경 섭동이 파이프라인에 물리지 않았다
```

`moon` 은 2031회 그대로. 태양 축만 죽었다는 것이 숫자로 나왔다.

**교훈: 안전망은 그것이 지킬 변경보다 먼저 머지되어야 한다.** 같은 브랜치에 넣으면 안전망이 변경 *전에* 통과하는 것을 볼 수 없고, 이미 끊긴 배선을 정상으로 기록하게 된다.

### 대응 — 패치 대상만 옮겼다

`perturb` 픽스처의 태양 패치 대상을 `core.astro` 로 옮겼다. `new_moon_jde` 는 `rules.kr.astro` 에 그대로 뒀다 (kr 에 남았고 `lunar.py:146` 이 속성 조회로 부르므로 도달하고 있다). 양쪽 중복 패치는 하지 않았다 — 중복하면 재수출이 사라져도 통과해 검사가 무뎌진다.

이것이 "테스트를 고쳐 통과시킨 것"이 아닌 이유: monkeypatch 의 원칙은 정의된 곳이 아니라 **쓰이는 곳**을 패치하는 것이다. 쓰이는 곳이 옮겨갔으므로 패치 대상도 따라간다. `assert` 는 하나도 바꾸지 않았다.

수정 후 실측:

| solar_degrees | lunar_seconds | calls |
|---|---|---|
| 0.05 | 0 | `{'sun': 8766, 'moon': 2031}` |
| −0.05 | 0 | `{'sun': 8766, 'moon': 2031}` |
| 0 | 300 | `{'sun': 8766, 'moon': 2031}` |
| 0 | −300 | `{'sun': 8766, 'moon': 2031}` |
| 5.0 | 0 | `{'sun': 8892, 'moon': 2025}` |
| −5.0 | 0 | `{'sun': 8982, 'moon': 2016}` |

카나리아 두 줄의 수가 다른 것은 정상이다 — 5° 를 흔들면 뉴턴법 걸음 수와 세(歲)의 달 수가 실제로 달라진다. 섭동이 계산에 물려 있다는 증거다.

---

## 신뢰할 수 없는 것 — 이 세션에서 확인된 것

### 인계 문서의 "할 일" 자체가 검증 대상이다

Holiday_04 인계 문서가 1번 작업으로 「문서 오기 2건 수정」을 지시했다:

- (a) 일본 祝日法 law_id 가 `323AC0000000178` 로 적혀 있다 (실제는 `323AC1000000178`)
- (b) 구 e-Gov 경로 `elaws.e-gov.go.jp/api/1/`
- (c) `data/{kr,jp}/YYYY.json` 형태 서술

조사 결과, 이 세 문자열은 **`docs/holiday_05.md` 안에만 있었고 그것도 전부 "고쳐야 한다"는 지시문이거나 정확한 사실 서술이었다.** 실제로 잘못 적힌 자리는 레포 전체에 0건이었다.

지금까지 다섯 번은 **문서가 코드보다 오래된** 경우였다. 이번은 성격이 다르다 — **문서가 자기 자신을 가리키는 할 일을 남겼고, 그것이 레포의 문제인 것처럼 읽혔다.**

### Claude Code 의 보고도 2차 소스다

이 세션에서 Claude Code 의 조사 보고가 검증 가능한 자리에서 틀렸다.

| 보고 | 실제 |
|---|---|
| `grep -rn '323AC0000000178' .` → 0건 | `docs/holiday_05.md:130` 에 실재 |
| `docs/holiday_05.md:467` 에 `427AC0000000033` | 그 ID 는 파일 전체에 0건. 467행은 다른 내용 |
| `docs/holiday_05.md:519` 에 `363AC0000000091` | 실제로는 626행 |
| AC/CO 형식 ID 2건 | 실제 8건 |

grep 은 git 추적 여부를 보지 않는다. untracked 파일이라도 워킹트리에 있으면 잡힌다. 즉 "0건" 보고는 성립할 수 없었다.

**그리고 이 보고를 근거로 이 세션에서 두 번 잘못된 결론을 냈다:**

1. 「law_id 오기는 레포에 0건, 대화 로그의 오류였다」 — 결론 자체는 우연히 맞았으나 근거가 무너졌다. **값이 같아도 이유가 다르면 같은 것이 아니다** (이 레포가 `core/` 승격 판정에 쓰는 바로 그 기준)
2. 「레포의 `docs/holiday_05.md` 가 더 진행된 판본이다」 — 검증하지 않은 전제 위에 세운 단언. 실제로는 업로드본과 바이트 동일 (md5 `76db8aa6759e2cdcb83c2daf8ffe7a6e`)

**대응: 줄번호·건수·인용은 사람이 직접 grep 으로 재확인한다.** 특히 "0건"은 반증이 쉬우므로 항상 재확인 대상이다.

### Codex 리뷰가 지정 항목을 침묵할 수 있다

두 번 모두 명시적으로 지정한 검토 항목을 언급하지 않았다. 없다고 판정한 것인지 보지 않은 것인지 구분되지 않는다.

| 지정 항목 | 처리 |
|---|---|
| `apply()` 이중 호출 시 원본 캡처 문제 | `grep -n 'perturb(' tests/test_lunar.py` → 호출 2곳, 서로 다른 테스트. 문제 없음 |
| `AstroError` 클래스 동일성 | `c.AstroError is k.AstroError` → `True`. mro `(core.astro.AstroError, ValueError)` |

**대응: 지정 항목은 Codex 응답과 무관하게 한 줄 명령으로 직접 닫는다.**

---

## `feat/core-astro` 배치 결정

| 대상 | 위치 | 근거 |
|---|---|---|
| `apparent_solar_longitude`, `solar_term_jde` | core 이동 | 나라와 무관한 천문 계산 |
| `J2000`, `SOLAR_DEGREES_PER_DAY`, `_TERM_TOLERANCE_DEG` | core 이동 | 사용처가 이동 대상뿐 |
| `AstroError` | core 정의 + kr 재수출 | 아래 |
| `_TERM_MAX_ITER` | **가른다** | 아래 |
| `winter_solstice_jde` | kr 잔류 | 하는 일이 천문이 아니라 역법. 270°를 고른 근거가 무중치윤법의 전제이지 천문 사실이 아니다 |
| `_MID_TERM_INTERVAL_DAYS`, 삭 관련 일체 | kr 잔류 | 결정 완료 사항 |

### `AstroError` — 클래스 객체가 하나여야 한다

`new_moon_jde`(kr 잔류), `month_start_k`(kr 잔류), `solar_term_jde`(core 이동) 세 곳에서 raise 된다. core 와 kr 이 각자 정의하면 `except AstroError` 가 core 에서 올라온 예외를 못 잡고 **조용히 의미가 바뀐다.** `tests/test_astro.py:62` 의 `pytest.raises(astro.AstroError)` 도 같다.

### `_TERM_MAX_ITER` — 값이 같아도 이유가 다르면 가른다

| 위치 | 이름 | 세는 것 |
|---|---|---|
| `core/astro.py` | `_TERM_MAX_ITER` | 뉴턴법 수렴 반복 상한 |
| `rules/kr/astro.py` | `_MONTH_WALK_MAX_STEPS` | 삭망월을 걸어 찾는 걸음 상한 |

둘 다 값은 30. 재수출로 공유하지 않았다. 한쪽만 옮기고 공유하면 "왜 이 두 반복이 같은 수여야 하는가"라는 없는 제약이 생긴다.

이것은 Holiday_04 의 `KST_OFFSET_DAYS` / `JST_OFFSET_DAYS` 판정과 같은 기준이다 — **"같은 값"이 아니라 "같은 이유로 같은가".**

---

## 현재 상태 (기준 `1a2a600`)

### 브랜치

로컬 `main` 하나. `HEAD` 와 `origin/main` 이 같은 커밋 (`git rev-list --left-right --count HEAD...origin/main` → `0 0`). 작업 브랜치 셋은 로컬·원격 모두 정리됨.

**주의:** `git fetch --prune` 을 돌리기 전에는 `git branch -a` 에 삭제된 원격 브랜치가 그대로 보인다. 이 세션에서도 Holiday_04 인계 문서의 「로컬·원격 모두 정리됨」 서술이 실제와 달라, prune 시 remote-tracking 3건이 지워졌다. **브랜치 목록을 신뢰하기 전에 prune 을 먼저 돌린다.**

### 워킹트리

`docs/holiday_05.md` 외에 깨끗함.

### 검증

```
uv run pytest        → 398 passed, 4 xfailed, 29 xpassed
uv run ruff check .  → All checks passed
```

`398 / 4 / 29` 는 PR #17 머지 시점(`d406a11`)과 **정확히 같은 숫자**다. `feat/core-astro` 가 순수 이동이라는 근거 중 하나.

`29 xpassed` 는 이 세션 이전부터 있던 상태다.

### 발행물

```
uv run pytest tests/test_published_feed.py -v  → 5 passed
```

`feeds/`·`status.json` 을 건드린 마지막 커밋은 `e940810`(8/17 자동 발행). 이 세션의 세 PR 중 어느 것도 발행물을 건드리지 않았다. `feeds/kr.ics` 자체가 바뀐 마지막 커밋은 `93ab9ff`(8/11).

`test_the_published_feed_is_reproducible_from_the_committed_inputs` 통과가 요점이다 — core 이동 후에도 커밋된 발행본이 커밋된 입력으로 그대로 재현된다.

### `core/` 현황

```
core/__init__.py  astro.py  buildlog.py  ics.py  secrets.py  timekeeping.py
```

`core/astro.py` 공개 표면:

```
37: J2000 = 2451545.0
41: SOLAR_DEGREES_PER_DAY = 0.98565
43: _TERM_TOLERANCE_DEG = 1e-7
46: _TERM_MAX_ITER = 30
49: class AstroError(ValueError)
53: def apparent_solar_longitude(jde)
67: def solar_term_jde(longitude, guess)
```

`rules/` → `core/` 방향 import 만 존재:

```
rules/kr/astro.py:84   from core.astro import (
rules/kr/astro.py:89   from core.timekeeping import julian_day, moment_at_offset
rules/kr/feed.py:30    from core import ics
rules/kr/status.py:33  from core import ics
```

역방향(`core/` → `rules/`) 없음. **`feat/jp-rules` 의 선행 조건 성립.**

### jp 자산 (다음 세션 입력)

```
data/jp/     2020~2027.yaml 8파일. 2027.yaml 은 126줄
sources/jp/  __init__.py  build_data.py  cache  cao_client.py  cao_parser.py
rules/       __init__.py  kr        ← rules/jp/ 없음
```

`verified: false` 24건. Holiday_04 조사 기록(`verified: true` 119 / `false` 24)과 일치.

---

## 다음 세션에서 할 일

### 1. `feat/jp-rules` — 일본 규칙 구현

이 세션의 `feat/core-astro` 가 이것을 위한 것이었다. `rules/jp/` 는 `rules/kr/` 를 import 하지 않는다. 태양 황경이 필요하면 `core/astro.py` 에서 가져온다.

착수 전 확인할 것:

- `data/jp/` 8파일은 **입력이자 정답지**다. `feat/jp-rules` 진행 중에 `data/jp/` 를 흔들면 정답지가 움직이는 상태에서 규칙을 짜게 된다. 데이터 변경이 필요하면 별도 `data/` 브랜치로 분리
- `verified: false` 24건을 확정 취급하지 않는다

### 2. `data/jp/*.yaml` 의 `source:` 에 law_id 를 넣을 것인가 (미결)

현재 `source:` 는 「国民の祝日に関する法律」（昭和23年法律第178号）第2条 형태로, **숫자 ID 를 쓰지 않는다.**

넣기로 결정하면 이것은 문서 수정이 아니라 **데이터 변경**이다. 데이터 흐름:

```
sources/jp/build_data.py:58     LAW = "「国民の祝日に関する法律」（昭和23年法律第178号）"
sources/jp/build_data.py:59-62  OLYMPIC_LAW = (...)
      ↓
sources/jp/build_data.py:193    out["source"] = f"{LAW} {basis['rule']}"     ← 休日
sources/jp/build_data.py:207    out["source"] = f"{OLYMPIC_LAW} {article} — {phrase}"
sources/jp/build_data.py:213    out["source"] = f"{LAW} 第2条"                ← 통상 축일
      ↓
sources/jp/build_data.py:262    lines.append(f"    source: {e['source']}")
sources/jp/build_data.py:283    path.write_text(_dump(year, entries, meta))
      ↓
data/jp/*.yaml  8파일 전부
```

`tests/test_cao_source.py:176` 이 바이트 단위 동일성을 본다:

```python
assert path.read_text(encoding="utf-8") == build_data._dump(year, entries, meta)
```

즉 `LAW`/`OLYMPIC_LAW` 를 한 글자라도 고치면 **같은 커밋에서 8파일 전부 재생성**해야 한다. `data/` 브랜치 + 근거 병기가 필수다.

**`feat/jp-rules` 이전에는 하지 않는다** (정답지가 움직이면 안 된다).

### 3. 미검증 law_id (미결)

`docs/holiday_05.md:626` 의 `363AC0000000091` (行政機関の休日に関する法律, 昭和63年法律第91号). e-Gov 실측으로 확인하지 않았다.

祝日法에서 `323AC0000000178`(AC0)이 404, `323AC1000000178`(AC1)이 200이었다. 같은 자리에 `0` 이 박힌 위 ID 도 같은 의심 대상이다. **문서로 닫지 말고 실측으로 닫는다.**

살아 있는 경로: `https://laws.e-gov.go.jp/api/2/law_data/<law_id>?response_format=xml`

### 4. 태양 황경 임계점 (관측만, 조사 안 함)

`tests/test_lunar.py` 의 임계점 주석은 `a172b6c` 기준으로 갱신했다:

```
태양 황경  -0.058° / +0.18° 까지 무변화. -0.06° 와 +0.19° 에서 첫 변화
삭 시각    -740 초 / +1200 초까지 무변화. -750 초와 +1300 초에서 첫 변화
```

이전 기록(2026-08-08, 리비전 미기재)은 「±0.1° 까지 무변화」였다. 마이너스 쪽 임계점이 −0.1° → −0.06° 로 좁아졌다.

- `SOLAR_PERTURBATION_DEGREES` 는 0.05 이므로 여유가 **1.2배**다 (옛 기록 시점에는 2배)
- **값을 낮추지 않았다.** 낮추면 테스트를 고쳐 통과시키는 것이 된다. 현재 통과하고 있다
- 임계에서 바뀌는 것은 `(2033, chuseok)` 하나로, `2033-09-08` → `2033-10-07` 한 달이 움직인다. 윤달 판정이 뒤집히는 자리다
- **이것은 인위적 섭동 하의 민감도이지 발행값이 아니다.** 골든 테스트가 발행물 무변경을 보증한다
- 현재 리비전(`1a2a600`) 기준 재측정은 하지 않았다. `f619d16`·`09c0946` 두 커밋이 들어간 뒤다

### 5. 열린 질문 (이월)

- `cross/kr-jp.ics` 는 두 나라 피드의 **합집합**이다 (대칭차가 아니다)
- `ci.yml` 의 `push: branches: [main]` 트리거 — 같은 커밋을 PR 과 머지 후 두 번 검증한다. 일본 작업 이후로 미룸
- `data/jp/` 의 최종 위치 (`sources/jp/` 로 이동 검토). 정해지면 `data/kr/` 존치 여부도 함께 본다
- `tests/test_astro.py` 분리 — 현재 kr 테스트와 core 테스트가 한 파일에 있다. core 테스트가 늘어나면 그때 볼 사안

---

## 닫힌 항목

- **GitHub Pages DNS check 배너** — 닫음. 배너 상태와 무관하게 서빙과 인증서가 확인됐다 (`Enforce HTTPS` 활성 = 인증서 발급 완료, 사이트 라이브). 배너를 지우려면 도메인 재등록이 필요한데 그러면 인증서 재발급 대기가 걸린다. 얻는 것보다 잃는 것이 크다
- **Holiday_04 1번 작업 (문서 오기 2건)** — 완료. 실질 오기 0건이었다. 위 「신뢰할 수 없는 것」 참조
- **`README.md` 의 `data/` 서술** — PR #16 으로 정정

---

## 이 세션에서 기록할 Claude 오류

| # | 내용 |
|---|---|
| 1 | 「law_id 오기는 레포에 0건」을 Claude Code 보고 하나에 근거해 확정 진술. 결론은 우연히 맞았으나 근거가 틀렸다 |
| 2 | 「레포 파일이 더 진행된 판본이다」를 검증 없이 단언. 실제로는 바이트 동일 |
| 3 | `docs/` 접두사를 「새 접두사인가?」라고 물음. `docs/branch-source-and-codex`, `docs/permission-correction` 전례가 이미 있었다 |
| 4 | `feat/core-astro` 프롬프트에 「`perturb` 관련 코드는 손대지 마라」로 적음. 의도는 "단언을 고쳐 통과시키지 마라"였는데 문장이 정당한 수정까지 막았다. Claude Code 가 멈추고 보고한 것이 옳았다 |
| 5 | `core/astro.py` 상수 확인용 grep 패턴 `^[A-Z_]* =` 로 `J2000` 을 놓침 (숫자가 든 이름) |
| 6 | 커밋 메시지와 PR 본문을 다른 형식(채팅/파일)으로 연달아 전달해, `09c0946` 커밋 메시지에 PR 본문이 통째로 들어갔다. 제목에 `feat:` 접두사가 없고 마크다운 표·코드펜스가 그대로 들어가 있다. **머지된 커밋이므로 고치지 않는다** — 히스토리 재작성이 규약 위반보다 비싸다 |

---

## 작업 방식 — 이 세션에서 확인된 것

- **조사 프롬프트와 구현 프롬프트를 분리한다.** 이 세션에서 조사가 결론을 세 번 뒤집었다: 「고칠 것 있음」 → 「레포에 0건」 → 「문서에 있음」 → 「전부 지시문이라 고칠 것 없음」
- **안전망은 그것이 지킬 변경보다 먼저 머지한다.** PR #17 → #18 순서가 이 세션의 핵심
- **"통과했다"가 아니라 "몇 번 불렸는지"를 본다.** 초록불은 검증의 증거가 아니다
- **지정한 검토 항목은 Codex 응답과 무관하게 직접 닫는다**
- **줄번호·건수·인용은 사람이 grep 으로 재확인한다.** 특히 "0건" 보고
- **`git branch -a` 전에 `git fetch --prune`**
