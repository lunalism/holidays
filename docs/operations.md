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
