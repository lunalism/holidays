# Holiday_06 시작 문서

작성: 2026-08-21
기준 리비전: `10cc8b7` (main)
이전 세션: Holiday_05 (PR #16, #17, #18)

이 문서는 **`feat/jp-rules` 사전 조사 결과**다. 다음 세션은 이 문서를 읽고 **설계 논의부터** 시작한다. 조사를 다시 돌리지 않는다.

---

## 0. 이 세션(Holiday_05 말미)에 한 일

`feat/jp-rules` 사전 조사만 했다. 코드 변경 없음.

부수로 원격 브랜치 3건을 정리했다. `docs/data-dir-roles`, `test/perturb-reach`, `feat/core-astro` 가 GitHub 에 살아 있었다.

**Holiday_05 인계 문서의 「작업 브랜치 셋은 로컬·원격 모두 정리됨」이 틀렸다.** `git fetch --prune` 을 돌렸으나 결과를 확인하지 않고 문서에 적었다. prune 은 *원격에서 이미 사라진* 참조만 지우는데, 이 레포는 머지 시 자동 삭제가 꺼져 있어 원격에 그대로 있었다.

`git push origin --delete <셋>` 으로 정리했다. **GitHub Settings → General → Pull Requests → `Automatically delete head branches` 를 켰는지 확인할 것** (이 세션에서 확인 안 함).

발행 cron 은 `0 0 * * 1` — 매주 월요일 00:00 UTC (KST 월 09:00). 8/18~8/21 사이 커밋이 없는 것은 정상이다.

---

## 1. `data/jp/*.yaml` 스키마 (확정)

### 형태

```yaml
version: 1
country: jp
year: 2027
holidays:
  - date: 2027-01-01
    name: 元日
    uid_token: new_years_day
    kind: statutory
    verified: true
    source: 「国民の祝日に関する法律」(昭和23年法律第178号) 第2条
```

키는 3층 18종. 최상위 4종(`version`, `country`, `year`, `holidays`) / 항목 필수 6종(`date`, `name`, `uid_token`, `kind`, `verified`, `source`) / 항목 선택 2종(`source_todo`, `basis`) / `basis` 하위 6종(`rule`, `trigger_date`, `trigger_weekday`, `note`, `prev_date`, `next_date`).

### 총량

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | 2027 | 계 |
|---|---|---|---|---|---|---|---|---|---|
| statutory | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 128 |
| substitute | 2 | 1 | 0 | 1 | 5 | 3 | 1 | 1 | 14 |
| bridge | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| **계** | 18 | 17 | 16 | 17 | 21 | 19 | 18 | 17 | **143** |

### `basis` 는 세 형태로만 나타난다

1. `rule` + `trigger_date` + `trigger_weekday` — `kind: substitute` (振替休日, 第3条第2項). **14건**
2. `rule` + `note` — 올림픽 특별조치법 이동 축일. 2020·2021 각 3건, **6건**
3. `rule` + `prev_date` + `next_date` — `kind: bridge` (国民の休日, 第3条第3項). **전 파일 통틀어 1건**

합계는 `basis` 를 가진 항목 21건 / 없는 항목 122건 / 전체 143건이다.

`kind: substitute` ⟺ `basis.trigger_date` 존재 는 143건 전체에서 반례 0건의 양방향 동치다. 다만 분기는 `basis` 키 모양이 아니라 `kind` 로 한다.

bridge 유일 사례 (`data/jp/2026.yaml:102-111`):

```yaml
  - date: 2026-09-22
    name: 休日
    uid_token: kyujitsu
    kind: bridge
    verified: true
    source: 「国民の祝日に関する法律」(昭和23年法律第178号) 第3条第3項
    basis:
      rule: 第3条第3項
      prev_date: 2026-09-21
      next_date: 2026-09-23
```

### `verified: false` 24건 = 8파일 × 3항목

매년 같은 3개다. `source_todo` 문구도 두 종류뿐.

| 항목 | 건수 | `source_todo` |
|---|---|---|
| 建国記念の日 (2/11) | 8 | 第2条は「政令で定める日」とする。当該政令(昭和41年政令第376号)を未確認。 |
| 春分の日 | 8 | 国立天文台が前年2月1日に官報で告示する日。当該年の官報を未確認。 |
| 秋分の日 | 8 | 国立天文台が前年2月1日に官報で告示する日。当該年の官報を未確認。 |

24건 모두 `kind: statutory`, `source: 「国民の祝日に関する法律」…第2条`, `basis` 없음.

**중요:** 이 3종이 미검증인 이유는 `sources/jp/build_data.py:90-101` 의 `UNVERIFIED` 테이블에 **상수로 박혀 있기 때문**이다. 항목별 조사 결과가 아니라 생성기가 문구를 찍어낸 것이다.

### jp 에 없는 키

`provisional`, `key`, `source_key`, `source_keys`, `aliases`, `group`. kr 의 `Holiday` 가 들고 있는 필드 중 jp 에 대응이 없는 것들이다.

---

## 2. `rules/kr/` 구조

```
rules/kr/__init__.py                  1
rules/kr/astro.py                   265
rules/kr/designated_holidays.yaml   366
rules/kr/feed.py                    368
rules/kr/holiday_calendar.py        950
rules/kr/lunar_holidays.yaml        191
rules/kr/lunar.py                   209
rules/kr/solar_holidays.yaml        147
rules/kr/status.py                  109
rules/kr/substitute_holidays.yaml   566
rules/kr/substitute_rules.py        438
                              합계 3610
```

### `feed.py` 공개 API

| 줄 | 시그니처 | docstring 첫 줄 |
|---|---|---|
| 67 | `feed_range(today: date) -> tuple` | (시작일, 종료일). 종료일은 today 기준 YEARS_AHEAD 년 뒤의 12-31. |
| 270 | `events(start: date, end: date) -> list` | 구간 안의 모든 이벤트. 날짜 오름차순. |
| 290 | `build(*, today, dtstamp, previous=None) -> bytes` | 피드 한 벌. 같은 인자면 같은 바이트가 나온다. |
| 313 | `publish(*, today, dtstamp, path=None) -> Path` | 피드를 파일로 낸다. 이전 발행본을 읽고, 새로 만들고, 원자적으로 바꾼다. |

비공개 9개: `_one_line`(76), `_token`(80), `_origin_name`(144), `_substitute_origin`(148), `_substitute_description`(172), `_designated_description`(207), `_description`(221), `_summary`(234), `_event`(249).

모듈 상수: `PRODID = "-//lunalism//holidays.lunalism.com//KO"`(41), `CALNAME = "대한민국 공휴일"`(42), `TZID = "Asia/Seoul"`(43), `RANGE_START = date(2020,1,1)`(36), `YEARS_AHEAD = 5`(39), `FEED_PATH`(310).

### 진입점

`rules/kr/feed.py:356-368` 의 `if __name__ == "__main__":` 블록 하나. `__main__.py` 파일도 콘솔 스크립트도 없다 (`pyproject.toml` 에 `[project.scripts]` 없고 `package = false`).

호출자:

| 호출자 | 위치 | 형태 |
|---|---|---|
| 발행 워크플로 | `publish.yml:111` | `uv run python -m rules.kr.feed feeds/kr.ics` |
| CI 워크플로 | `ci.yml:23` | 주석뿐. 실행 안 함 |
| 테스트 | `tests/test_ics.py:1097-1098` | `runpy.run_module('rules.kr.feed', run_name='__main__')` |

`publish()` 를 부르는 프로덕션 코드는 `__main__` 블록 하나뿐이다.

---

## 3. kr 과 jp 의 구조 차이 — **설계의 핵심**

### 3-1. `events()` 의 축이 뒤집힌다

kr 은 **날짜 축을 훑으며 매일 규칙에 묻는다** (`feed.py:270-287`):

```python
def events(start: date, end: date) -> list:
    out = []
    day = start
    while day <= end:
        provisional = hc.is_provisional(day)
        for holiday in hc.holidays_on(day):
            out.append(_event(day, holiday, provisional))
        day = day.fromordinal(day.toordinal() + 1)
    return out
```

날짜가 입력이고 공휴일 여부가 출력이다. `hc.holidays_on(day)` 뒤에는 `holiday_calendar.py` 950줄 → 음력 환산(`lunar.py` 209줄, `astro.py` 265줄) → 지정표 → 대체공휴일 판정(`substitute_rules.py` 438줄)이 매달려 있다.

**jp 는 `data/jp/*.yaml` 의 `holidays:` 리스트가 곧 답이다.** 날짜를 순회할 이유가 없고, 파일을 읽어 항목을 그대로 펼치면 된다. 143건이 전부다.

### 3-2. 갈리는 지점 세 곳

**(a) `events()` 의 루프 형태**
kr: `while day <= end` + 규칙 조회. jp: YAML 로더 + 항목 순회.
`holiday_calendar` 같은 중간 계층이 jp 에는 존재하지 않아도 되고 지금 없다. `sources/jp/__init__.py:7` 이 명시한다: 규칙 유도(달력 조회·대체휴일 판정)는 여기 없다.

**(b) `feed_range()` 의 상한**
kr: `date(today.year + YEARS_AHEAD, 12, 31)` — **시계에서 유도** (`feed.py:73`).
jp: **데이터가 상한을 정한다** — `sources/jp/build_data.py:52` 의 `RANGE_END = date(2027, 11, 23)`.

이유는 같은 파일 21-24행에 있다. CSV 는 연 1회(전년 2월) 한 해씩만 늘고, 특히 **春分の日·秋分の日은 전년 2월 1일 관보 고시로 확정되기 전까지 공식 날짜가 존재하지 않는다.** 계산으로 미래를 채우면 정부가 아직 정하지 않은 날짜를 우리가 발표하는 것이 된다.

kr 의 `feed_range(today)` 는 `today` 를 받는데 jp 에서는 `today` 가 상한에 영향을 주지 않는다. **같은 시그니처를 쓸 수 있느냐가 설계 판단이다.**

**(c) `provisional` 의 출처 — 가장 조심할 자리**

kr 은 `hc.is_provisional(day)` 로 날짜 축에서 직접 묻는다(`feed.py:283`). 그 값이 `ics.Event.provisional` 로 가고 `STATUS:TENTATIVE` 가 된다(`core/ics.py:91-92`).

**jp 데이터에는 `provisional` 키가 없다.** jp 가 들고 있는 것은 `verified`(불리언)와 `source_todo`(문자열)인데, **이 둘은 성격이 다르다.** `feed.py:210-212` 의 `_designated_description()` docstring 이 명시한다:

> `note` 와 `source_todo` 는 쓰지 않는다. `note` 에는 KASI 대조 결과가 들어 있고 `source_todo` 는 미확인 사항이라 둘 다 구독자에게 나갈 것이 아니다. `verified` 도 마찬가지다 — 우리 내부 검증 상태다.

**즉 jp 는 `provisional` 을 채울 재료를 데이터에서 받지 못하고, `verified: false` 를 그 자리에 밀어 넣는 것은 위 규약과 충돌한다.** 확인된 사실은 여기까지다. 어떻게 할지는 다음 세션의 설계 결정이다.

### 3-3. 무엇이 재사용 가능한가

판정 기준: `hc`(= `rules.kr.holiday_calendar`)를 참조하는가 / kr 고유 값이 상수로 박혀 있는가.

**`core/` 는 그대로 재사용 가능.** `core/ics.py` 는 스스로 국가 무관을 선언한다(모듈 docstring 1-4행): 국가별 규칙은 여기 두지 않고, `rules/<국가>` 가 정해서 `Event` 로 넘긴다. 37-39행이 확장 지점을 명시한다 — `token` 을 무엇으로 할지는 국가별 결정이라 여기서 정하지 않는다. `core/ics.py` 500줄 전체에서 kr 을 언급하는 곳은 주석의 참조 문구뿐이고 코드는 없다.

`core/ics.py:57-59` 의 `UID_DOMAIN_CONFIRMED` 주석이 **다음 국가 피드를 미리 지목하고 있다** — `False` 인 동안은 발행이 거부되고, 확정 후에도 그대로 남긴다. 현재 `True`(`core/ics.py:70`).

**`feed.py` 안에서:**

| 대상 | 줄 | 판정 |
|---|---|---|
| `PRODID`/`CALNAME`/`TZID` | 41-43 | **값만 kr.** `ics.render()` 가 셋 다 인자로 받으므로 구조는 그대로 |
| `_one_line()` | 76-77 | 국가 무관 |
| `build()` | 290-304 | **구조 그대로.** 본문이 `feed_range()` + `ics.render(...)` 뿐 |
| `FEED_PATH` | 310 | 값만 kr |
| `publish()` | 313-353 | **국가 무관.** `hc` 참조 없음, kr 값 없음 |
| `__main__` 블록 | 356-368 | 국가 무관 (시계 읽기 + argv 경로) |

**kr 전용 — `hc` 에 묶여 jp 로 옮길 수 없음:**

| 대상 | 줄 | 근거 |
|---|---|---|
| `_KIND_ABBREV` | 62-64 | `hc.KIND_SUBSTITUTE` 상수 |
| `_token()` | 80-113 | `holiday.key` → `holiday.uid_token` → `_KIND_ABBREV[kind]` 3단 우선순위. **jp 에는 `key` 가 없고 `uid_token` 이 143건 전부에 있어 3단 우선순위 자체가 필요 없다** |
| `SUBSTITUTE_ORIGIN_NAMES` | 130-134 | `{"seollal": "설날", "chuseok": "추석", "new_years_day": "신정"}` |
| `SUBSTITUTE_ORIGIN_SEPARATOR` | 141 | `"·"`. 선택 이유가 한국어 고유 (가운뎃점이 이미 공휴일 이름 안에 쓰인다 — 3·1절) |
| `_origin_name()` | 144-145 | `hc.holiday_name(key)` |
| `_substitute_origin()` | 148-169 | `holiday.source_keys` / `source_key`. jp 에 없는 필드 |
| `_substitute_description()` | 172-204 | `hc.substitute_eligibility(...)["ruleset"]`, `hc.CalendarError`, `hc.MappingUnresolved` |
| `_designated_description()` | 207-218 | `hc._designated()["by_date"]` — 비공개 함수를 직접 호출 |
| `_description()` | 221-231 | `hc.KIND_STATUTORY`/`KIND_SUBSTITUTE` 분기. **`bridge` 분기가 없다** |
| `_summary()` | 234-246 | `hc.KIND_SUBSTITUTE` 분기 |
| `_event()` | 249-267 | `origin=` 에 `key=…uid_token=…source_key=…` — kr 필드 이름 3개를 문자열로 박는다 |
| `events()` | 270-287 | `hc.is_provisional(day)`, `hc.holidays_on(day)` |
| `feed_range()`/`RANGE_START`/`YEARS_AHEAD` | 36-39, 67-73 | `hc` 참조는 없으나 상한 산출 방식이 kr 전용 (§3-2(b)) |

**정리: `feed.py` 368줄 중 62-287행(약 226줄, 62%)이 `hc` 또는 kr 고유 값에 묶여 있다. `hc` 참조가 전혀 없는 것은 `_one_line`(76-77), `feed_range`(67-73), `build`(290-304), `publish`(313-353), `__main__`(356-368) — 약 90줄이다.**

### 3-4. 데이터 모델 대응표

`rules/kr/holiday_calendar.py:88-119` 의 `Holiday` 와 jp YAML 항목 키의 대응:

| kr `Holiday` | jp 항목 키 | 비고 |
|---|---|---|
| `name` | `name` | 대응 |
| `kind` | `kind` | **값 집합이 다르다.** kr: `statutory`/`substitute` + YAML 정의 `temporary`/`election`. jp: `statutory`/`substitute`/`bridge`. **`bridge` 는 kr 에 대응이 없다** |
| `key` | — | jp 에 없음 |
| `source_key` | — | jp 에 없음. `basis.trigger_date` 가 날짜로는 대응하나 키가 아니라 날짜다 |
| `source_keys` | — | jp 에 없음 |
| `uid_token` | `uid_token` | 대응. **kr 은 지정공휴일에만 있고 jp 는 전 항목에 있다** |
| `provisional` | — | **jp 에 없음** (§3-2(c)) |
| `lunar_boundary_risk` | — | jp 무관 (음력 없음) |
| — | `date` | kr 은 `Holiday` 가 날짜를 안 들고 `holidays_on(day)` 의 인자로 온다 |
| — | `verified`/`source`/`source_todo` | kr 에서는 YAML 표에만 있고 `Holiday` 로 올라오지 않는다 |
| — | `basis.*` | kr 대응 없음. kr 은 대체공휴일 근거를 데이터가 아니라 `hc.substitute_eligibility()` 계산으로 얻는다 |

---

## 4. 발행 경로 — 새 피드를 넣으려면 건드릴 곳

### 현재 `feeds/`

```
feeds/.gitkeep   0 bytes
feeds/kr.ics     64175 bytes  (2025-08-11 15:02)
```

둘뿐이다.

### 발행 워크플로 (`publish.yml`, 297줄)

| 무엇 | 파일:줄 |
|---|---|
| 예약 실행 | `36-38` — `cron: "0 0 * * 1"` + `workflow_dispatch` |
| 린트 관문 | `76-77` — `uv run ruff check .` |
| 테스트 관문 | `91-92` — `uv run pytest -m "not published_artifact"` |
| 피드 생성 | `108-111` — `uv run python -m rules.kr.feed feeds/kr.ics` |
| status 생성 | `113-116` — `uv run python -m rules.kr.status status.json` |
| 발행 기록 | `121-128` — `uv run python -m core.buildlog` (`if: always()`) |
| 커밋·푸시 | `130-239` — DTSTAMP 제외 diff, `stage_one()`, 커밋 메시지 결정 |
| 변경 요약 | `207` — `uv run python -m core.ics "$PREV" feeds/kr.ics` |
| 연속 실패 이슈 | `244-297` — 2회 연속이면 `gh issue create` |

### 새 피드 추가 시 건드릴 위치 (**위치 보고이며 수정하지 않았다**)

**A. 생성 코드 — 지금 kr 에만 있는 것**

| 위치 | 지금 상태 |
|---|---|
| `rules/kr/feed.py:41-43` | `PRODID`/`CALNAME`/`TZID`. jp 는 `//KO` 가 아닌 값이 필요 |
| `rules/kr/feed.py:310` | `FEED_PATH = parents[2] / "feeds" / "kr.ics"` — 파일명이 박혀 있다 |
| `rules/kr/feed.py:313-353` | `publish()`. `core/` 가 아니라 `rules/kr/` 에 있다 |
| `rules/kr/feed.py:356-368` | `__main__` 진입점. 국가마다 하나씩 필요한 구조 |
| `rules/kr/status.py:39-93` | `status()` 가 feed 단수를 가정한다. `"feed": {…}` 키가 하나이고 `feed.FEED_PATH` 를 직접 참조(49) |
| `rules/kr/status.py:88-92` | `kasi_key` — kr 소스 전용 블록 |

**B. 워크플로 — `feeds/kr.ics` 가 하드코딩된 곳**

`publish.yml`: `108-111`(생성), `113-116`(status), `140-165`(DTSTAMP 제외 비교 — `feeds/kr.ics` 5회, `FEED_CHANGED` 가 단수 변수), `194-208`(`stage_one`, `core.ics "$PREV"`), `220-232`(커밋 메시지 `feat(kr): 피드 갱신 — …`), `19-21`(산출물 3개 나열 주석), `99-102`(`sources.kr.key_expiry` — kr 전용 스텝), `292-294`(이슈 본문 "자주 걸리는 것" 목록). `ci.yml:23-24`(갱신 명령 안내 주석).

**C. 발행면**

`index.html:395` — `var FEED_URL = "https://holidays.lunalism.com/feeds/kr.ics";` 단수 상수. `index.html:386` 주석 — 루트를 서빙하므로 `feeds/kr.ics` 가 그대로 이 경로가 된다. `CNAME` — `holidays.lunalism.com`.

**D. 검사·산출물**

`tests/test_published_feed.py` — 파일 전체가 `feeds/kr.ics` 재현 검사. 82, 114, 149, 177, 180행에 경로·명령이 박혀 있다. `pyproject.toml:48-59` — `published_artifact` 마커 정의. `status.json:4` — `"path": "feeds/kr.ics"`.

**E. 문서**

`README.md:28, 84, 108`, `DESIGN.md:94, 150, 154`, `CLAUDE.md:8`, `docs/branch-rules.md:41`.

---

## 5. `core/ics.py` (500줄)

### 공개 API

| 줄 | 시그니처 | docstring 첫 줄 |
|---|---|---|
| 76 | `class IcsError(ValueError)` | 피드를 만들 수 없다. |
| 80-81 | `@dataclass(frozen=True) class Event` | 직렬화 직전의 이벤트 하나. 국가 규칙은 이미 다 적용된 상태여야 한다. |
| 121 | `assign_uids(events) -> list` | `[(Event, uid)]` — 파일에 실릴 순서대로. |
| 187-188 | `@dataclass(frozen=True) class PublishedEvent` | 이전 발행본에서 읽어 온 이벤트 하나. SEQUENCE 계산의 입력이다. |
| 198 | `read_published(raw: bytes) -> dict` | 이전에 발행한 `.ics` → `{uid: PublishedEvent}`. |
| 425-433 | `render(events, *, dtstamp, prodid, calname, tzid, previous=None) -> bytes` | VCALENDAR 한 덩어리. 같은 인자면 같은 바이트가 나온다. |
| 462 | `summarize_change(previous, current) -> str` | 두 발행본의 차이를 커밋 제목 한 줄로. |

`Event` 필드(84-103): `day: date`, `summary: str`, `kind: str`, `description: str = ""`, `provisional: bool = False`, `token: str = ""`, `origin: str = ""`.

`PublishedEvent` 필드(191-195): `uid`, `dtstart`, `dtend`, `sequence`, `summary`.

모듈 상수: `UID_DOMAIN = "holidays.lunalism.com"`(51), `UID_DOMAIN_CONFIRMED = True`(70), `VERSION = "2.0"`(72), `CALSCALE = "GREGORIAN"`(73).

### UID 조립

`core/ics.py:183` 한 줄이 전부다:

```python
out.append((event, f"{day:%Y%m%d}-{event.token}@{UID_DOMAIN}"))
```

형식은 모듈 docstring `core/ics.py:21` 에 명시: `{YYYYMMDD}-{token}@holidays.lunalism.com`.

`assign_uids()`(153-184)는 같은 날 같은 token 이 겹치면 `IcsError` 를 낸다 — **자동으로 접미사를 붙이지 않는다.** 이유가 코드에 적혀 있다(175-179): 접미사가 위치 기반이 되어 다음에 항목이 하나 늘면 남의 UID 까지 밀린다. token 이 빈 이벤트도 거부한다(163-167).

**`token` 자체는 `core` 가 만들지 않는다.** `rules/kr/feed.py:259` 가 `_token(holiday)` 로 채워 넣는다. **jp 데이터는 `uid_token` 을 143건 전부에 이미 들고 있고**, 그 값이 名称에서 나온다는 규약은 `sources/jp/build_data.py:26-38` 에 적혀 있다.

### `STATUS` 와 `X-HOLIDAY-STATUS`

`_vevent()` 의 `if event.provisional:` 블록(`core/ics.py:419-421`)이 두 속성을 함께 넣는다. 따로 붙는 경로가 없어 항상 같이 나간다.

```python
    if event.provisional:
        out.add("status", "TENTATIVE")
        out.add("x-holiday-status", "PROVISIONAL")
```

**소스의 리터럴은 소문자 `x-holiday-status` 이고 직렬화 시 대문자로 나간다.** `grep 'X-HOLIDAY-STATUS' core/ics.py` 는 0건을 낸다 — 미구현으로 읽기 쉬운 자리다. 이 문서가 §5 를 쓰면서 `X-HOLIDAY-STATUS` 를 한 번도 언급하지 않은 것이 그 예다.

커밋된 `feeds/kr.ics` 에 이미 나가 있다.

| 속성 | 줄 수 |
|---|---|
| `STATUS:TENTATIVE` | 57 |
| `X-HOLIDAY-STATUS:PROVISIONAL` | 57 |

두 수가 같은 것은 위 블록의 귀결이다. 해당 이벤트의 `DTSTART` 는 최소 `20290101`, 최대 `20311225` 이고 2028 년 이전은 0건이다. 확정 구간이 `2028-12-31`(kr YAML 3종의 `confirmed_through`)이므로 `provisional` 은 그 바깥에만 붙는다.

`provisional` 과 `verified` 는 다른 범주다. `core/ics.py:91` 은 `provisional` 을 "규칙 개정 확인 시점 이후"로 정의한다 — 우리가 아니라 규칙 쪽 사정이다. `verified` 는 `rules/kr/feed.py:210-212` 가 명시하듯 우리 내부 검증 상태이고 구독자에게 나가지 않는다. 한쪽을 다른 쪽 자리에 밀어 넣을 수 없다(§3-2(c)).

**두 범주의 분리는 `core/ics.py` 안에도 이미 적혀 있다.** `_vevent()`(395) 의 `out.add("summary", ...)`(406) 바로 위 주석(404-405)이 한 자리에서 둘을 다 말한다:

```python
    # 잠정·미검증 표시를 붙이지 않는다. 구독자 캘린더에 그대로 뜨는 문자열이고,
    # 우리 내부 검증 상태는 구독자가 알 바가 아니다. 잠정은 STATUS 로 나간다.
    out.add("summary", event.summary)
```

즉 `core` 는 국가별 규칙을 모르면서도 이 구분만은 알고 있다 — 미검증은 SUMMARY 에 실리지 않고, 잠정은 `STATUS` 로 나간다. jp 가 `verified: false` 를 `provisional` 자리에 밀어 넣으면 이 주석이 금지하는 것을 하게 된다.

---

## 6. 다음 세션에서 결정해야 할 것

조사는 끝났다. 아래는 **설계 판단**이며 사람이 정한다.

### (1) `provisional` 을 어떻게 할 것인가 — 최우선

jp 데이터에 `provisional` 이 없다. `verified: false` 를 그 자리에 쓰는 것은 `feed.py:210-212` 의 규약(내부 검증 상태는 구독자에게 나가지 않는다)과 충돌한다.

생각해 볼 갈래 (전부 미결):
- jp 피드에 `STATUS:TENTATIVE` 를 아예 쓰지 않는다
- `verified: false` 3종(建国記念の日/春分の日/秋分の日)의 성격을 다시 본다 — 이들은 "우리가 확인 못 했다"이지 "정부가 확정 안 했다"가 아니다. `UNVERIFIED` 테이블이 상수로 박혀 있다는 점(§1)이 판단 재료다. **다만 3종을 한 덩어리로 다루면 안 된다** — 아래 갈래를 참조
- 위 3종의 성격 차이: 春分の日·秋分の日 은 매년 전년 2월 1일 관보 고시로 확정된다. 연도별 확정 절차가 실재하고, 8년치를 닫으려면 8번 확인해야 한다. 建国記念の日 은 政令이 2월 11일로 한 번 고정했고 연도별 확정 절차가 없다 — 8건이 전부 같은 政令 하나를 가리키므로 그 政令 원문을 한 번 확인하면 8건이 동시에 닫힌다. 데이터의 `source_todo` 는 그 政令을 `昭和41年政令第376号` 로 적고 있으나 **우리는 그 원문을 확인하지 않았다.** 政令 번호 자체가 확인 대상이다
- 발행 범위(`RANGE_END = 2027-11-23`)가 이미 미확정 연도를 잘라내고 있으므로 `provisional` 이 필요 없을 수 있다

### (2) `feed_range()` 를 공유할 것인가

kr 은 시계에서, jp 는 데이터에서 상한을 얻는다. 같은 시그니처(`today` 인자)를 유지할지, jp 는 다른 모양으로 갈지.

### (3) `bridge` 를 어떻게 표현할 것인가

`kind: bridge` 가 kr 에 대응이 없다. 143건 중 1건(`2026-09-22`). `_description()`/`_summary()` 의 분기가 kr 에는 없다.

Holiday_05 이전 결정: **`kyujitsu` 를 振替/国民 구분 없이 단일 UID 토큰으로 쓴다.** 데이터가 이미 그렇게 되어 있다(`kind` 는 다르지만 `uid_token` 은 둘 다 `kyujitsu`). UID 충돌 위험을 확인할 것 — 같은 날 두 건이 있으면 `assign_uids()` 가 거부한다.

### (4) `publish()` 를 `core/` 로 올릴 것인가

`publish()`(313-353)와 `build()`(290-304)는 `hc` 참조가 없고 kr 값도 없다. jp 가 그대로 쓸 수 있는 90줄이다.

다만 **이것은 `feat/jp-rules` 와 별개 브랜치여야 할 수 있다** — `feat/core-astro` 와 같은 순수 이동이고, 같은 판정(`git diff origin/main -- feeds/ status.json` 이 0바이트)을 적용할 수 있다. 이동과 신규 구현을 한 브랜치에 섞으면 무엇이 무엇을 깼는지 흐려진다.

### (5) `status.py` 의 단수 가정

`status()`(39-93)가 피드 하나를 가정한다. `"feed": {…}` 키가 단수이고 `feed.FEED_PATH` 를 직접 참조한다(49). jp 피드가 생기면 스키마가 바뀐다. **`status.json` 스키마 변경은 구독자에게 나가는 것이 아니지만 `tests/test_published_feed.py` 가 본다.**

### (6) 워크플로 다중 피드화

`publish.yml` 의 `FEED_CHANGED` 가 단수 변수이고 `feeds/kr.ics` 가 5회 하드코딩돼 있다(140-165). 두 피드가 되면 "무엇이 바뀌었나" 판정이 피드별로 갈린다.

**이것은 `feat/jp-rules` 범위 밖일 가능성이 높다.** 규칙 구현과 발행 파이프라인 개조는 다른 일이다.

---

## 7. `feat/jp-rules` 확정 사항

§6 이 아직 열려 있는 것이라면 여기는 이번 조사로 닫힌 것이다.

| 항목 | 값 |
|---|---|
| `PRODID` | `-//lunalism//holidays.lunalism.com//KO` |
| `CALNAME` | `일본 공휴일` |
| `TZID` | `Asia/Tokyo` |
| 발행 범위 | `sources.jp.build_data` 의 `RANGE_START` / `RANGE_END` 를 import |
| `feed_range()` | jp 에는 두지 않는다 |
| `provisional` | 항상 `False`. `STATUS:TENTATIVE` · `X-HOLIDAY-STATUS` 둘 다 0줄 |
| `publish()` | `feat/jp-rules` 에서는 jp 쪽에 복제. core 승격은 이후 별도 브랜치 |
| SUMMARY (statutory) | `name` 그대로 (예: `元日`) |
| SUMMARY (substitute) | `休日（建国記念の日）` |
| SUMMARY (bridge) | `休日（敬老の日・秋分の日）` |
| 괄호 · 구분자 | 전각 `（）` · 전각 `・`(U+30FB) |
| DESCRIPTION (statutory) | `근거: ` + 데이터의 `source` 원문 |
| DESCRIPTION (substitute/bridge) | 유래 문장(한국어 서술) + 근거 줄 |
| 분기 기준 | `kind`. `basis` 키 모양이 아니다 |

SUMMARY 예시의 출처: substitute 는 `data/jp/2024.yaml` 의 `2024-02-12`(`basis.trigger_date: 2024-02-11` = 建国記念の日), bridge 는 `data/jp/2026.yaml` 의 `2026-09-22`(`basis.prev_date: 2026-09-21` = 敬老の日, `basis.next_date: 2026-09-23` = 秋分の日).

**표기 언어.** SUMMARY 는 일본어 원문을 유지한다. 한국어로 옮기면 `天皇誕生日` 등에서 우리가 정치적 판정을 하게 되고, 이 레포가 판정할 사안이 아니다. DESCRIPTION 의 서술문은 한국어로 쓰되 축일명과 법령명은 원문을 유지한다.

**statutory 에도 DESCRIPTION 을 붙이는 이유.** `rules/kr/feed.py` 의 statutory 는 DESCRIPTION 이 비어 있으나, 그 이유는 정책이 아니라 결핍이다 — `_description()`(221-231) 주석이 "지금 표에 조문 번호가 없다"고 적는다. jp 는 143건 전부 `source` 를 갖고 있고 `tests/test_cao_source.py` 의 `test_every_entry_carries_a_source()` 가 그것을 강제한다. kr 의 공백을 따라 할 이유가 없다.

**`source` 원문 보존.** 데이터의 `source` 안 괄호는 반각이다(`sources/jp/build_data.py:58` 의 `LAW` 상수). 우리가 조립하는 SUMMARY 괄호는 전각이지만, `source` 는 데이터 원문이므로 손대지 않는다. `_one_line()` 만 통과시킨다.

**레이어 방향.** `rules/` → `sources/` import 는 이미 실재한다 — `rules/kr/status.py:36` 의 `from sources.kr import key_expiry`. 문서에 이 방향을 금지하는 문장은 없고, 명시적으로 금지된 것은 `core/` → 바깥 하나뿐이다(`core/__init__.py:3`, `README.md:34`, `sources/kr/kasi_client.py:184-186`). `sources.jp.build_data` 는 모듈 최상위가 docstring · import · 상수 대입 · 클래스와 함수 정의 · `__main__` 블록뿐이라 import 부수 효과가 없다.

---

## 8. 확인 안 한 것

- **GitHub Pages 설정** — 어느 브랜치·디렉터리를 서빙하는지. 레포에 Pages 워크플로 파일이 없고(`.github/workflows/` 에 `ci.yml`, `publish.yml` 뿐) 저장소 설정은 코드에서 볼 수 없다. `CNAME` 과 `index.html:386` 주석("루트를 서빙하므로")이 근거의 전부다
- **`Automatically delete head branches` 설정** — 이 세션에서 켰는지 확인 안 함
- `.env` / GitHub Secrets 실제 내용 — 열지 않았다
- `rules/kr/holiday_calendar.py` 950줄 전체 — 공개 API 목록과 `Holiday` 정의(88-119), `_designated()`(214-234)만 읽었다. §3 의 재사용 판정은 `feed.py` 전문과 이 범위에 근거한다
- `sources/jp/cao_client.py` / `cao_parser.py` — 읽지 않았다. `build_data.py` 는 docstring(1-39)과 상수부(48-117), 함수 목록만 읽었다
- `data/jp/2020~2026.yaml` 전문 — 키 집계·`kind` 분포·`verified: false` 항목·`note`/`prev_date`/`next_date` 주변만 인용했다. 전문은 2027 만 읽었다
- 태양 황경 임계점 재측정 — Holiday_05 에서 `a172b6c` 기준으로 기록했고 이후 두 커밋(`f619d16`, `09c0946`)이 들어갔다. 현재 리비전 기준 재측정 안 함

---

## 9. 이어지는 미결

Holiday_05 에서 이월된 것:

- **`data/jp/*.yaml` 의 `source:` 에 law_id 를 넣을 것인가** — 넣으면 `sources/jp/build_data.py:58`(`LAW`)/`59-62`(`OLYMPIC_LAW`) → `_entry()`(193/207/213) → `_dump()`(262) → 8파일 전부 재생성. `tests/test_cao_source.py:176` 이 바이트 동일성을 본다. **`feat/jp-rules` 이전에는 하지 않는다** (정답지가 움직이면 안 된다)
- **`363AC0000000091`** (行政機関の休日に関する法律) 미검증. 祝日法에서 `AC0` 이 404, `AC1` 이 200이었으므로 같은 의심 대상. 실측으로 닫는다. 경로: `https://laws.e-gov.go.jp/api/2/law_data/<law_id>?response_format=xml`
- `cross/kr-jp.ics` 는 두 나라 피드의 **합집합**이다 (대칭차 아님)
- `ci.yml` 의 `push: branches: [main]` 트리거 — 같은 커밋을 두 번 검증한다. 일본 작업 이후로 미룸
- `data/jp/` 의 최종 위치 (`sources/jp/` 로 이동 검토). 정해지면 `data/kr/` 존치 여부도 함께
- `tests/test_astro.py` 분리 — core 테스트가 늘어나면

이번 세션에서 추가된 것:

- **춘분·추분 계산과 内閣府 CSV 의 대조 검사가 레포에 없다.** 이전 세션 기록에 "146/146 일치"라는 수치가 있으나, 레포 전체에서 그 대조를 수행하는 코드는 0줄이다. `sources/jp/` 3파일은 `core` 도 `astro` 도 import 하지 않고(import 문 전수 확인), 춘분·추분 관련 줄은 전부 문자열 매핑(`build_data.py:74, 82`)과 주석·`source_todo` 문구(`22, 92, 98, 99`)다. `tests/test_cao_source.py:272` 의 `test_the_equinoxes_are_not_claimed_as_verified()` 는 `verified: false` 여부만 단언하고 날짜를 대조하지 않는다. **현재 상태에서 그 수치는 재현 가능한 산출물이 아니다.** 검증 하니스 항목으로 남긴다
- **`core.astro` 의 실제 소비자는 하나뿐이다.** 실제 import 는 `rules/kr/astro.py:84` 한 곳이고, 그중 `apparent_solar_longitude` 는 그 파일에서 호출되지 않는 재수출 전용 이름이다(`astro.py:82-83` 주석이 그렇게 적는다). `rules/jp/` 는 `feat/jp-rules` 범위에서 `core.astro` 를 쓰지 않는다 — jp 는 CSV 날짜를 읽고 계산하지 않는다. `feat/core-astro` 의 승격 근거 자체는 유효하나 아직 행사되지 않았다

---

## 10. 정정 기록

**§1 의 `basis` 형태 1 을 16건으로 적었다. 실측은 14건이다.**

16 이라는 수는 데이터 안에 실재한다 — 파일당 `statutory` 항목 수가 16이고 `statutory` 의 `name` 종류도 16종이다. 문서가 그 16을 잘못 끌어온 것으로 보인다.

발견 경로는 문서 안의 모순이었다. §1 의 `kind` 표는 `substitute` 합계를 14로 적는데 같은 절의 `basis` 형태 1 은 16을 적었다. `kind: substitute` ⟺ `basis.trigger_date` 가 동치이므로 두 수는 같아야 한다. 실측으로 14 가 맞음이 확인되었다.

같은 검토에서 §1 의 YAML 인용 3곳(`source` 2건 · `source_todo` 1건)이 괄호를 전각 `（）` 으로 적고 있는 것이 드러났다. `data/jp/` 에 전각 괄호는 0건이고 실제 데이터는 반각 `()` 이며 `第2条` 앞에 공백이 있다. 인용을 데이터와 일치시켰다.

---

## 11. 작업 규약 (변함없음)

- 조사 프롬프트와 구현 프롬프트를 분리한다
- 안전망은 그것이 지킬 변경보다 **먼저** 머지한다
- "통과했다"가 아니라 "몇 번 불렸는지"를 본다
- 지정한 검토 항목은 Codex 응답과 무관하게 직접 닫는다
- 줄번호·건수·인용은 사람이 grep 으로 재확인한다. 특히 "0건" 보고
- `git branch -a` 전에 `git fetch --prune`, **그리고 prune 결과를 확인한다**
- 커밋 메시지와 PR 본문을 혼동하지 않는다 (Holiday_05 `09c0946` 사례)
- `data/jp/` 8파일은 `feat/jp-rules` 의 **입력이자 정답지**다. 진행 중에 흔들지 않는다
