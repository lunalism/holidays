# 운영 문서

이 저장소를 직접 돌리는 사람을 위한 문서입니다. 구독자에게 필요한 내용은
[`README.md`](../README.md) 에 있습니다.

## 개발 환경

Python 3.12 이상, 패키지 관리는 [uv](https://docs.astral.sh/uv/).

```bash
uv run pytest        # 테스트 — 시스템 python 이 아니라 반드시 uv 로 실행합니다
```

전체 명령과 에이전트 규약은 [`AGENTS.md`](../AGENTS.md) 에 있습니다 —
한 곳에만 둡니다.

## 설정과 시크릿

API 키는 **코드에 절대 두지 않습니다.** 로컬에서는 `.env.example` 을 `.env` 로
복사해서 사용하고(`.env` 는 gitignore 대상), 운영 환경에서는 GitHub Actions
Secret 으로만 주입합니다. 커밋 전에 인증정보가 섞이지 않았는지 확인하세요.

### 필요한 GitHub 설정

| 항목 | 값 | 위치 |
|---|---|---|
| Secret | `KASI_SERVICE_KEY` | Settings → Secrets and variables → Actions → New repository secret |
| 워크플로 권한 | Read and write permissions | Settings → Actions → General → Workflow permissions |

Secret 값은 공공데이터포털의 **Encoding 키**(퍼센트 인코딩된 형태)를 그대로
붙여 넣습니다. Decoding 키를 넣으면 `+` 가 공백으로 해석되어 인증에 실패합니다.

워크플로 권한이 필요한 이유는 산출물(`feeds/*.ics` 열다섯 벌, `status.json`,
`logs/build.jsonl`)을 커밋해야 하기 때문입니다. `publish.yml` 이 `permissions: contents: write` 를 선언하지만,
저장소 기본 설정이 read-only 면 그 선언도 무시됩니다.

## 외부 데이터 출처의 운영 세부

출처가 무엇이고 왜 그것을 쓰는지는 [`README.md`](../README.md) 의 "무엇을
구독하나" 절에 있습니다. 여기에는 키·인코딩·수집 규약만 둡니다.

### 대한민국 — 한국천문연구원 특일정보 API

인증키는 `KASI_SERVICE_KEY` 환경변수로만 주입합니다.

> **활용기간 만료: 2028-08-08**
>
> 만료되면 인증이 거부되고 갱신 파이프라인이 멈춥니다. 문제는 조용히 멈춘다는
> 점입니다 — 이미 발행된 `.ics` 는 그대로 남아 있어서 구독자 쪽에서는 아무 일도
> 없어 보입니다.
>
> 만료를 사람의 기억에 맡기지 않습니다. 만료일은
> `sources/kr/kasi_names.yaml` 의 `service.expires_on` 에 값으로 있고,
> 발행 워크플로가 매번 `sources/kr/key_expiry.py` 로 확인합니다.
> **남은 기간이 60일 미만이면 발행하지 않고 실패합니다.** 연장한 뒤
> `service.expires_on` 을 갱신하세요.

인증키는 Encoding 키(퍼센트 인코딩된 형태)를 씁니다. 쿼리 문자열을 직접 조립해
그대로 붙여야 하며, HTTP 클라이언트의 `params` 인자로 넘기면 이중 인코딩되어
403 이 납니다. `sources/kr/kasi_client.py` 의 `try_key_modes()` 가 이 확인을
합니다.

### 일본 — 内閣府 syukujitsu.csv

수집·캐싱 규약은 `sources/jp/cao_client.py` 의 주석에 있습니다.

## 피드 추가 — 손대는 순서와 빠뜨리면 무엇이 잡는지

피드 하나를 늘릴 때 손대는 지점을 순서대로 둡니다. 왜 그렇게 갈랐는지는
[`DESIGN.md`](../DESIGN.md) 의 "피드 추가" 절에 있고, 여기는 절차만 둡니다.

항목마다 "빠뜨리면 무엇이 잡는가" 를 적었습니다. 잡는 테스트가 있는 항목은
외울 필요가 없고, 없는 항목은 사람이 챙겨야 합니다. 그 구분이 이 절의 목적입니다.

"발행 run" 은 `publish.yml` 의 테스트 스텝(`-m "not published_artifact"`)이고,
"CI" 는 `ci.yml` 의 전체 실행입니다. 마커가 붙은 테스트는 CI 에서만 돕니다.

### 1. 발행 run 과 CI 가 모두 잡는 것 — `tests/test_feed_set.py` 와 랜딩 생성 스텝

| 순서 | 무엇을 | 빠뜨리면 |
|---|---|---|
| 1 | `rules/<코드>/` 패키지 — `feed.py`(`__main__` 포함)·`status.py` | 패키지 없이 3 을 하면 `rules/status.py` 의 import 가 깨져 `test_feed_set.py` 가 수집 단계에서 실패합니다(`ModuleNotFoundError`). 반대로 패키지만 만들고 2 를 안 하면(고아) `test_every_rules_package_is_in_feeds_and_vice_versa` 가 실패합니다 |
| 2 | `.github/workflows/publish.yml` 의 `FEEDS` 에 코드 추가 | `test_every_rules_package_is_in_feeds_and_vice_versa` 와 `test_the_status_registry_matches_feeds` 가 실패합니다 |
| 3 | `rules/status.py` — import 와 `"feeds"` 리터럴 등록 | `test_the_status_registry_matches_feeds` 가 실패합니다 |
| 4 | `landing/layout.yaml` 에 자리 — 어느 묶음에 설지. 독일 주 피드(`de_*`)는 접두사 규칙으로 자동 편입되므로 손댈 것이 없습니다 | 테스트가 아니라 생성 스텝이 잡습니다 — `landing/render.py` 가 `ValueError: rules/ 에 있는데 layout 에 자리가 없는 피드` 로 죽어 발행 run 의 "랜딩 생성" 스텝이 실패합니다. CI 에서는 `test_landing_render.py` 가 같은 예외로 실패합니다 |
| 5 | 주 피드가 아니면 `landing/locales/` **전 언어**의 `feeds` 에 desc(필요하면 label). 언어 목록은 그 디렉터리가 듭니다 — 여기 적지 않습니다 | 4 와 같은 경로입니다. 한 언어라도 빠지면 그 언어를 만들 때 `landing/render.py` 가 `ValueError: locale 에 <코드> 의 desc 가 없다` 로 죽어 "랜딩 생성" 스텝이 실패합니다. ko 만 적고 끝내는 것이 흔한 빠뜨림입니다 |
| 6 | (독일 주 피드) `rules/de_<주>/feed.py` 에 `LAND_NAME_DE` — 독일어 주 이름. 표기 근거는 `rules/de/feed.py` 의 같은 이름 절(기본법 전문) | 4 와 같은 경로입니다. 독일어 표기를 쓰는 언어(`land_lang: de` — 지금은 ja)를 만들 때 render 가 `AttributeError: … has no attribute 'LAND_NAME_DE'` 로 죽습니다 |

`sources/<코드>/`·`data/<코드>/` 는 조건부입니다 — 조건은 `DESIGN.md` 에 있습니다.

### 2. CI 만 잡는 것 — `published_artifact` 마커

| 순서 | 무엇을 | 빠뜨리면 |
|---|---|---|
| 7 | `feeds/<코드>.ics` — `uv run python -m rules.<코드>.feed feeds/<코드>.ics` 로 생성해 커밋 | `test_feed_set.py::test_the_published_feeds_match_feeds`, `test_landing.py::test_every_published_feed_has_a_row_and_vice_versa`, `test_readme.py::test_every_published_feed_is_in_the_table_and_vice_versa` 가 실패합니다 |
| 8 | `status.json` — `uv run python -m rules.status status.json` 으로 재생성해 커밋 | `test_landing.py::test_feed_rows_match_status_json_feed_keys` 가 실패합니다 |
| 9 | `index.html` 과 언어 디렉터리의 `index.html` — `uv run python -m landing.render` 로 전 언어를 재생성해 커밋. 경로는 `landing/render.py` 가 언어에서 유도하고, 발행 워크플로의 스테이징도 `*/index.html` 로 받습니다 — 여기 목록을 적지 않습니다 | `test_landing_render.py::test_the_committed_landing_is_reproducible_from_landing_inputs` 가 **언어마다 한 건** 실패하고, `test_landing.py::test_every_published_feed_has_a_row_and_vice_versa`·`test_feed_rows_match_status_json_feed_keys` 도 실패합니다. 입력(층 1 의 5·6)이 비어 있으면 여기까지 오지 못하고 생성 자체가 죽습니다 |
| 10 | (독일 주 피드) `tests/test_landing.py` 의 `LAND_NAMES_DE` 표에 주 추가 | `test_german_land_names_are_fixed[<코드>]` 가 `KeyError` 로 실패합니다. 이 표는 `rules/` 스캔이 parametrize 를 이끌고 표는 조회 대상이라 새 주가 조용히 빠지지 않습니다 — 아래 12 의 `LAND_NAMES` 도 #90 이후 같은 모양입니다 |
| 11 | `README.md` "구독" 절 표에 행 추가 | `test_readme.py::test_every_published_feed_is_in_the_table_and_vice_versa` 가 실패합니다 |
| 12 | (독일 주 피드) `tests/test_de_scope.py` 의 `LAND_NAMES` 표에 주 추가 | `test_state_land_names_are_fixed[<코드>]` 와 `test_state_descriptions_are_sentence_blank_source[<코드>]` 가 `KeyError` 로 실패합니다. 주 목록은 `rules/` 스캔이 이끌므로 새 주는 scope·DESCRIPTION 검사에 저절로 듭니다 — 사람이 적을 것은 주명뿐입니다 |

7 이 발행 run 에서 잡히지 않는 것은 의도입니다 — 발행본 없이 1~6 만 main 에
들어온 상태에서 발행 run 이 첫 발행을 만들 수 있어야 하기 때문입니다.
9 도 발행 run 에서 잡지 않습니다 — 랜딩이 낡은 것은 피드가 틀린 것이 아니고,
발행 run 이 index.html 을 스스로 다시 만들어 올립니다.

### 3. 아무것도 잡지 않는 것 — 사람 몫

| 순서 | 무엇을 | 빠뜨리면 |
|---|---|---|
| 13 | `README.md` "구조" 절 — `rules/` 줄의 피드 열거 | 잡는 테스트가 없습니다. 문장이 낡은 채로 남습니다 |
| 14 | `tests/test_published_feed.py` — 잠정 건수가 사양상 0 인 피드면 `test_the_status_publishes_no_provisional_events` 의 리터럴 목록에 코드 추가. 재현성·status 서술·UID 배타는 `rules/` 스캔으로 자동 편입되므로 손댈 것이 없습니다 | 잡는 테스트가 없습니다. 그 피드의 잠정 건수가 0 이라는 사양이 검사되지 않습니다 |

## 언어 추가 — 파일 하나

사람이 하는 일은 `landing/locales/<lang>.yaml` 을 두고 `uv run python -m landing.render`
를 돌리는 것뿐입니다. 워크플로·테스트·문서를 손대지 않습니다 — 언어 목록은
`landing/render.py` 가 `locales/` 를 스캔해 얻고, 발행 워크플로는 인자 없이 render 를
돌리며 스테이징을 `*/index.html` 로 받습니다. 테스트도 같은 스캔에 실려 자동으로
편입됩니다(영어를 더한 #84 에서 `test_landing` 9 건 + `test_landing_render` 1 건이
테스트 수정 없이 늘었습니다).

새 locale 에서 사람이 틀릴 수 있는 것 여섯은 **전부 render 가 생성 시점에 멈춥니다** —
피드 추가의 층 1(항목 4~6)과 같은 경로입니다. 발행 run 의 "랜딩 생성" 스텝이 실패하고
CI 에서는 `test_landing_render.py` 가 같은 예외로 실패합니다.

| 틀린 것 | 멈추는 메시지 |
|---|---|
| `ui` 키 누락·잉여(템플릿 ↔ locale 양방향) | `템플릿의 {{t:키}} 가 locale 에 없다` / `locale 에 있는데 템플릿이 쓰지 않는 키: […]` |
| `lang` 값이 파일명과 다름 | `locales/<lang>.yaml 의 lang 이 … 다` |
| 복수형 매핑의 갈래 빠짐·모르는 갈래 | `복수형 매핑은 ['one', 'other'] 를 정확히 들어야 한다 — 키 …: 빠진 갈래 […], 모르는 갈래 […]` |
| 복수형 매핑 값이 문자열이 아님 | `복수형 매핑의 값은 문자열이어야 한다 — 키 … 의 […]` |
| 매핑을 `{{t:}}` 마커 키에 씀 | `t 마커는 매핑을 받지 않는다 — 키 …` |
| `state_feed.land_lang` 이 닫힌 집합 밖 | `state_feed.land_lang 이 닫힌 집합 밖이다 … 중 하나여야 한다` |

주 피드가 아닌 피드의 `desc` 누락도 같은 경로입니다(`locale 에 <코드> 의 desc 가
없다` — 위 피드 추가 항목 5).

**잡히지 않는 것 하나는 생성물 커밋입니다.** 새 언어의 `<lang>/index.html` 을 만들어
커밋하지 않으면 render 는 조용히 성공합니다 — 그것은 피드 추가의 항목 9 가 덮는
자리이고(CI 의 `test_landing_render`), 발행 run 은 스스로 다시 만들어 올립니다.

## 커밋 전

`uv run pytest` 가 녹색이어도 CI 의 린트(`ruff`)에서 빨갈 수 있습니다 — docstring
한 줄이 100자를 넘어 CI 에서만 걸린 일이 있습니다. 명령은
[`AGENTS.md`](../AGENTS.md) 에 있습니다. 인증정보가 섞이지 않았는지도 함께 봅니다.
