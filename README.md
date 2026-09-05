# holidays

대한민국과 일본의 공휴일을 캘린더 앱에서 구독할 수 있는 iCalendar(`.ics`)
피드로 발행합니다. 피드는 여섯입니다 — 대한민국(`kr`), 일본(`jp`), 독일 전국
공통(`de`), 두 나라를 한 캘린더로 합친 `kr_jp`, 한쪽만 쉬는 날만 모은
`kr_only`·`jp_only`. 매주 월요일에 자동 갱신됩니다.

수록 기간·항목 수·마지막 갱신 시각은
[holidays.lunalism.com](https://holidays.lunalism.com) 에 표시됩니다.

## 구독

캘린더 앱에 아래 주소를 넣습니다. Google 캘린더는 "URL로 추가", Apple
캘린더는 "새로운 캘린더 구독"입니다. `webcal://` 로도 같은 경로입니다.

| 묶음 | 피드 | 구독 주소 |
|---|---|---|
| 나라별 전체 | 대한민국 | `https://holidays.lunalism.com/feeds/kr.ics` |
| | 일본 | `https://holidays.lunalism.com/feeds/jp.ics` |
| | 독일 — 전국 공통(주별 공휴일 제외) | `https://holidays.lunalism.com/feeds/de.ics` |
| 한 피드로 합침 | 대한민국·일본 | `https://holidays.lunalism.com/feeds/kr_jp.ics` |
| 겹치지 않는 날만 | 대한민국만 | `https://holidays.lunalism.com/feeds/kr_only.ics` |
| | 일본만 | `https://holidays.lunalism.com/feeds/jp_only.ics` |

- 일본 피드의 항목 이름은 일본어 원문(元日, 休日（元日） 등)으로 표기됩니다.
- 독일 피드는 16개 주 전체에서 유효한 법정 공휴일(연 9건)만 싣습니다. 주별
  공휴일(Fronleichnam, Reformationstag 등)은 들어 있지 않습니다. 항목 이름은
  법조문 표기(Neujahr, 1. Mai 등)입니다.
- 합집합 피드는 항목 이름 앞의 `[KR]`·`[JP]` 로 어느 나라의 공휴일인지
  표시합니다. 수록 기간은 두 나라 피드 중 짧은 쪽까지입니다 — 한쪽만 있는
  구간을 실으면 다른 나라의 공휴일이 없는 것처럼 읽히기 때문입니다.

## 날짜가 어디서 오는가

**대한민국** — 날짜를 외부 목록에서 받아 적지 않고, 법령 규칙표
(`rules/kr/*.yaml`)와 천문 계산(음력 환산)으로 유도합니다. 한국천문연구원
특일정보 API 는 채택 소스가 아니라 대조 상대입니다 — 유도한 값이 API 응답과
갈리는지를 테스트가 확인합니다. 실제로 갈린 사례가 있습니다: 2015년 8월 14일
임시공휴일은 API 응답에 없지만, 2015년 8월 4일 국무회의 의결로 확인해
수록했습니다. 항목별 근거는 각 YAML 의 `source` 필드에 있습니다.

아직 확정 발표 전인 미래 구간은 현행 규칙으로 계산한 잠정값으로 싣습니다.
임시공휴일이 지정되거나 규칙이 개정되면 달라집니다. 확정·잠정의 경계는
`status.json` 과 랜딩 페이지에 있습니다.

**일본** — 内閣府가 발표하는 `syukujitsu.csv` 가 1차 소스입니다. 정부가 아직
고시하지 않은 미래 날짜를 계산으로 채우지 않으므로, 피드의 상한은 CSV 의
마지막 날짜이고 잠정 구간이 없습니다.

법령·관보 원문까지 확인하는 대조 작업은 규칙표 항목 단위로 진행 중이며,
그 건수는 `status.json` 의 `verification` 에 집계되고 랜딩 페이지에
표시됩니다.

## 구조

```
sources/       원천 데이터 수집 (kr: KASI API, jp: 内閣府 CSV). 수집만 하고
               해석은 하지 않는다.
sources/*/cache/  원시 응답을 받은 그대로. 커밋 대상이다 — 변화를 diff 로
               추적하기 위한 관측 기록이며, 테스트가 이 파일들을 입력으로 쓴다.
rules/         나라별 공휴일 규칙과 피드 조립 (kr, jp, de, kr_jp, kr_only, jp_only).
               status.py 가 status.json 을 조립한다.
core/          국가 공통 로직 (날짜 모델, UID 생성, iCalendar 직렬화, 피드 쓰기)
data/          jp: 캐시된 CSV 에서 생성한 연도별 YAML. kr: 비어 있다 —
               rules/kr/*.yaml 규칙표에서 날짜를 유도하므로 중간 산출물을
               두지 않는다.
feeds/         발행되는 .ics 파일 (kr, jp, de, kr_jp, kr_only, jp_only 의 .ics)
tests/         테스트
docs/          브랜치 운영 규칙, 작업 세션 기록
logs/          build.jsonl — 발행 시도 기록. 실패도 남는다.
status.json    지금 저장소가 주장하는 상태. 랜딩 페이지가 읽는다.
index.html     랜딩 페이지. CNAME 이 holidays.lunalism.com 을 이 저장소에 붙인다.
```

국가를 추가할 때 반드시 늘리는 것은 `sources/<코드>/` 와 `rules/<코드>/`
입니다. `data/<코드>/` 는 필수가 아니라 그 나라의 소스 사정에 따릅니다 —
kr 은 비어 있고(국가별 디렉터리 대칭을 위해 `.gitkeep` 으로 자리만 유지)
jp 는 있습니다. 이 둘을 늘리고 `core/` 는 국가 중립으로 유지합니다.

피드 단위 범위 결정은 [`DESIGN.md`](DESIGN.md) 에 있습니다. 규칙 하나에 붙는
결정은 해당 YAML 의 주석과 `open_questions` 에 있습니다.

## 발행

`.github/workflows/publish.yml` 이 피드를 만들고 커밋합니다.
**매주 월요일 00:00 UTC(09:00 KST)로 예약되어 있습니다.** 실제 실행 시각은
GitHub 스케줄러 사정으로 몇 시간 지연될 수 있습니다. 수동
실행(`workflow_dispatch`)도 그대로 됩니다.

산출물 세 가지는 갱신 주기가 다릅니다 — `feeds/*.ics` 는 내용이 실제로 바뀔
때만, `status.json` 은 매 실행, `logs/build.jsonl` 은 실패를 포함해 매 실행
한 줄씩 커밋됩니다. 각각의 이유는 [`DESIGN.md`](DESIGN.md) 의 "발행 파이프라인"
절에 있습니다. 피드 파일에 커밋이 몇 달 없는 것은 정상 상태입니다.

UID 네임스페이스를 `holidays.lunalism.com` 으로 확정하면서 발행을 열었습니다.
`core/ics.py` 의 `UID_DOMAIN_CONFIRMED` 가 `False` 로 돌아가면 `publish()` 가
다시 거부하고 워크플로는 "피드 생성" 스텝에서 실패합니다 — 가드는 확정 후에도
그대로 남아 있습니다.

## 개발 환경

Python 3.12 이상, 패키지 관리는 [uv](https://docs.astral.sh/uv/).

```bash
uv run pytest        # 테스트 — 시스템 python 이 아니라 반드시 uv 로 실행합니다
```

전체 명령과 에이전트 규약은 [`AGENTS.md`](AGENTS.md) 에 있습니다 —
한 곳에만 둡니다.

## 외부 데이터 출처

### 대한민국 — 한국천문연구원 특일정보 API

공공데이터포털 `SpcdeInfoService/getRestDeInfo` 로 대조합니다(채택 소스가
아니라 대조 상대 — 위 "날짜가 어디서 오는가" 참조). 인증키는
`KASI_SERVICE_KEY` 환경변수로만 주입합니다.

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

内閣府 「国民の祝日」 페이지의
`https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv` 를 받아
`sources/jp/cache/` 에 원본 바이트(CP932) 그대로 커밋합니다. 인증키가
필요 없습니다. 원본은 연 1회(전년 2월) 한 해씩 늘어나며, 수집·캐싱 규약은
`sources/jp/cao_client.py` 의 주석에 있습니다.

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

워크플로 권한이 필요한 이유는 산출물(`feeds/*.ics` 여섯 벌, `status.json`,
`logs/build.jsonl`)을 커밋해야 하기
때문입니다. `publish.yml` 이 `permissions: contents: write` 를 선언하지만,
저장소 기본 설정이 read-only 면 그 선언도 무시됩니다.

## 호환성 원칙

한 번 공개된 값은 되돌릴 수 없습니다. 아래 두 가지는 특히 주의합니다.

- **구독 URL** — `https://holidays.lunalism.com/feeds/kr.ics` 와
  `https://holidays.lunalism.com/feeds/jp.ics`, 그리고 합집합 피드
  `https://holidays.lunalism.com/feeds/kr_jp.ics`. `webcal://` 로도 같은
  경로입니다. 구독자의 캘린더 앱에 그대로 박히므로 경로를 바꾸면 전부
  끊깁니다.
- **이벤트 UID** — 네임스페이스는 `@holidays.lunalism.com` 으로 **확정**
  되었습니다. UID 가 바뀌면 캘린더 앱이 같은 공휴일을 새 이벤트로 인식해
  중복이 생깁니다.

두 값은 확정되었습니다. 바꾸는 제안은 구독자 영향을 먼저 확인해야 합니다.

## 라이선스

코드는 MIT. `data/` 및 발행 피드의 라이선스는 원천 데이터의 이용허락범위를
확인한 뒤 확정합니다(미확인). 출처 표기 요건은 제공처 정책을 따릅니다.
