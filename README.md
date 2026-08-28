# holidays

공휴일 데이터를 수집·정규화해서 캘린더 앱에서 바로 구독할 수 있는
iCalendar(`.ics`) 피드로 발행하는 프로젝트입니다. v1 대상 국가는 대한민국(`kr`)입니다.

> **상태: v1 스켈레톤.** 디렉터리 구조와 설정만 잡혀 있고 로직은 아직 없습니다.

```bash
uv run pytest        # 테스트 — 시스템 python 이 아니라 반드시 uv 로 실행합니다
```

전체 명령과 규약은 [`AGENTS.md`](AGENTS.md) 에 있습니다.

## 구독 URL

준비 중입니다.

## 구조

```
sources/kr/   원천 데이터 수집 (외부 API 조회). 수집만 하고 해석은 하지 않는다.
sources/kr/cache/  API 원시 응답. 커밋 대상이다 — 응답 변화를 diff 로 추적하기 위한
              원본 관측 기록이며, 테스트가 이 파일들을 입력으로 쓴다.
rules/kr/     공휴일 규칙 (대체공휴일, 임시공휴일, 음력 환산 등)
core/         국가 공통 로직 (날짜 모델, UID 생성, iCalendar 직렬화, 피드 쓰기)
data/kr/      비어 있다. 한국은 rules/kr/*.yaml 규칙표에서 날짜를 유도하므로 중간
              산출물을 두지 않는다. 국가별 디렉터리 대칭을 위해 자리만 유지한다.
feeds/        발행되는 .ics 파일
tests/        테스트
```

국가를 추가할 때 반드시 늘리는 것은 `sources/<코드>/` 와 `rules/<코드>/` 입니다.
`data/<코드>/` 는 필수가 아니라 그 나라의 소스 사정에 따릅니다. 이 둘을 늘리고
`core/` 는 국가 중립으로 유지합니다.

피드 단위 범위 결정은 [`DESIGN.md`](DESIGN.md) 에 있습니다. 규칙 하나에 붙는
결정은 해당 YAML 의 주석과 `open_questions` 에 있습니다.

## 개발 환경

Python 3.12 이상, 패키지 관리는 [uv](https://docs.astral.sh/uv/).
명령 목록은 [`AGENTS.md`](AGENTS.md) 에 있습니다 — 한 곳에만 둡니다.

`pyproject.toml` 의 런타임 의존성은 잠정값이며 구현 착수 시 재확인합니다.

## 외부 데이터 출처

대한민국 공휴일은 한국천문연구원 특일 정보 API(공공데이터포털
`SpcdeInfoService/getRestDeInfo`)로 확인합니다. 인증키는 `KASI_SERVICE_KEY`
환경변수로만 주입합니다.

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
403 이 납니다. `sources/kr/kasi_client.py` 의 `try_key_modes()` 가 이 확인을 합니다.

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

워크플로 권한이 필요한 이유는 산출물(`feeds/kr.ics`, `feeds/jp.ics`,
`status.json`, `logs/build.jsonl`)을 커밋해야 하기 때문입니다. `publish.yml` 이
`permissions: contents: write` 를 선언하지만, 저장소 기본 설정이 read-only 면
그 선언도 무시됩니다.

## 발행

`.github/workflows/publish.yml` 이 피드를 만들고 커밋합니다.

**매주 월요일 09:00 KST 에 자동 실행됩니다.** 수동 실행(`workflow_dispatch`)도
그대로 됩니다.

UID 네임스페이스를 `holidays.lunalism.com` 으로 확정하면서 발행을 열었습니다.
`core/ics.py` 의 `UID_DOMAIN_CONFIRMED` 가 `False` 로 돌아가면 `publish()` 가
다시 거부하고 워크플로는 "피드 생성" 스텝에서 실패합니다 — 가드는 확정 후에도
그대로 남아 있습니다.

파이프라인이 쓰는 세 파일의 성격과 갱신 시점은
[`DESIGN.md`](DESIGN.md) 의 "발행 파이프라인" 절에 있습니다.

## 호환성 원칙

한 번 공개된 값은 되돌릴 수 없습니다. 아래 두 가지는 특히 주의합니다.

- **구독 URL** — `https://holidays.lunalism.com/feeds/kr.ics` 와
  `https://holidays.lunalism.com/feeds/jp.ics`. `webcal://` 로도 같은 경로입니다.
  구독자의 캘린더 앱에 그대로 박히므로 경로를 바꾸면 전부 끊깁니다.
- **이벤트 UID** — 네임스페이스는 `@holidays.lunalism.com` 으로 **확정**되었습니다.
  UID가 바뀌면 캘린더 앱이 같은 공휴일을 새 이벤트로 인식해 중복이 생깁니다.

두 값은 확정되었습니다. 바꾸는 제안은 구독자 영향을 먼저 확인해야 합니다.

## 라이선스

코드는 MIT. `data/` 및 발행 피드의 라이선스는 원천 데이터의 이용허락범위를
확인한 뒤 확정합니다(미확인). 출처 표기 요건은 제공처 정책을 따릅니다.
