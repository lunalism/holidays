# holidays

대한민국·일본·독일의 공휴일을 캘린더 앱에서 구독할 수 있는 iCalendar(`.ics`)
피드로 발행합니다. 피드는 열다섯입니다 — 나라별 전체 셋(`kr`·`jp`·`de`),
독일 주별 아홉, 두 나라를 한 캘린더로 합친 `kr_jp`, 한쪽만 쉬는 날만 모은
`kr_only`·`jp_only`. 매주 월·수·금 06:23 KST 에 자동 갱신됩니다.

수록 기간·항목 수·마지막 갱신 시각은
[holidays.lunalism.com](https://holidays.lunalism.com) 에 표시됩니다.

## 구독

캘린더 앱에 아래 주소를 넣습니다. Google 캘린더는 "URL로 추가", Apple
캘린더는 "새로운 캘린더 구독"입니다. `webcal://` 로도 같은 경로입니다.

| 묶음 | 피드 | 구독 주소 |
|---|---|---|
| 나라별 전체 | 대한민국 | `https://holidays.lunalism.com/feeds/kr.ics` |
|  | 일본 | `https://holidays.lunalism.com/feeds/jp.ics` |
|  | 독일 — 전국 공통(16개 주 교집합) | `https://holidays.lunalism.com/feeds/de.ics` |
| 독일 주별 | 독일·베를린 | `https://holidays.lunalism.com/feeds/de_be.ics` |
|  | 독일·바덴뷔르템베르크 | `https://holidays.lunalism.com/feeds/de_bw.ics` |
|  | 독일·바이에른 | `https://holidays.lunalism.com/feeds/de_by.ics` |
|  | 독일·헤센 | `https://holidays.lunalism.com/feeds/de_he.ics` |
|  | 독일·함부르크 | `https://holidays.lunalism.com/feeds/de_hh.ics` |
|  | 독일·니더작센 | `https://holidays.lunalism.com/feeds/de_ni.ics` |
|  | 독일·노르트라인베스트팔렌 | `https://holidays.lunalism.com/feeds/de_nw.ics` |
|  | 독일·라인란트팔츠 | `https://holidays.lunalism.com/feeds/de_rp.ics` |
|  | 독일·슐레스비히홀슈타인 | `https://holidays.lunalism.com/feeds/de_sh.ics` |
| 한 피드로 합침 | 대한민국·일본 | `https://holidays.lunalism.com/feeds/kr_jp.ics` |
| 겹치지 않는 날만 | 대한민국만 | `https://holidays.lunalism.com/feeds/kr_only.ics` |
|  | 일본만 | `https://holidays.lunalism.com/feeds/jp_only.ics` |

## 무엇을 구독하나

### 대한민국

관공서의 공휴일에 관한 규정과 국경일에 관한 법률이 정한 날, 그리고 음력에
기대는 설날·추석·부처님오신날이 들어갑니다. 대체공휴일과 임시공휴일도
포함합니다.

**날짜를 외부 목록에서 받아 적지 않습니다.** 법령 규칙표(`rules/kr/*.yaml`)와
천문 계산(음력 환산)으로 유도합니다. 한국천문연구원 특일정보 API 는 채택
소스가 아니라 대조 상대입니다 — 유도한 값이 API 응답과 갈리는지를 테스트가
확인하고, 갈리면 목록으로 냅니다. 어느 쪽도 자동으로 정답이 되지 않습니다.
실제로 양방향의 사례가 있습니다: 2015년 8월 14일 임시공휴일은 API 응답에
없지만 2015년 8월 4일 국무회의 의결로 확인해 수록했고, 2024년 10월 1일
임시공휴일은 우리 표에 없던 것을 API 가 알려 주었습니다.

아직 확정 발표 전인 미래 구간은 현행 규칙으로 계산한 잠정값으로 싣습니다.
임시공휴일이 지정되거나 규칙이 개정되면 달라집니다.

### 일본

内閣府가 발표하는 `syukujitsu.csv` 가 1차 소스입니다. 항목 이름은 일본어
원문(元日, 休日（元日） 등)으로 표기합니다.

**정부가 아직 고시하지 않은 미래 날짜를 계산으로 채우지 않습니다.** 그래서
피드의 상한은 CSV 의 마지막 날짜이고, 잠정 구간이 없습니다. 대신 다른
피드보다 먼저 끝납니다.

### 독일

독일에는 전국 공휴일법이 없습니다. 연방이 정한 것은 통일의 날(10월 3일)
한 건뿐이고(Einigungsvertrag Art. 2 Abs. 2), 나머지는 **16개 주가 각자의
주법으로 정합니다.** 그래서 "독일 공휴일"이라는 하나의 목록이 존재하지
않습니다.

이 구조를 피드 두 종류로 옮겼습니다.

- `de.ics` — **16개 주 모두에서 유효한 날만.** 열여섯 주법의 교집합이고
  연 9건입니다. 주별 공휴일(Fronleichnam, Reformationstag 등)은 들어 있지
  않습니다.
- `de_<주>.ics` — **전국 공통에 그 주 전역에서 유효한 주법 공휴일을 더한
  상위집합.** `de.ics` 의 9건을 전부 포함합니다. 얹히는 날이 그 주에만 있는
  것은 아닙니다 — Fronleichnam 은 다섯 주 피드(바덴뷔르템베르크·바이에른·
  헤센·노르트라인베스트팔렌·라인란트팔츠)에 함께 들어갑니다.

**어느 걸 고르나.** 해당 주가 목록에 있으면 주 피드를 쓰십시오 — 그 주
전역에서 유효한 날이 들어 있습니다. **다만 주 전역이 아니라 일부 지자체에서만
유효한 날은 싣지 않습니다** — 바이에른의 Mariä Himmelfahrt(가톨릭 다수
지자체)와 아우크스부르크의 Friedensfest 가 그런 경우입니다. 주가 목록에
없거나 전국 어디서나 유효한 날만 필요하면 `de.ics` 를 쓰십시오. 둘을 같이
구독하면 9건이 중복됩니다.

항목 이름은 법조문 표기(Neujahr, 1. Mai 등)입니다. 같은 축일이라도 주법이
다르게 적으면 다르게 표기합니다 — 바덴뷔르템베르크의 Fronleichnam 과
라인란트팔츠의 Fronleichnamstag 는 같은 날이지만 조문이 다릅니다.

근거는 각 주 관보의 공포본입니다. 항목마다 `verified` 필드가 그 상태를
표시합니다(아래 "데이터를 믿을 수 있는 근거" 참조).

### 합집합·차집합 피드

`kr_jp` 는 항목 이름 앞의 `[KR]`·`[JP]` 로 어느 나라의 공휴일인지 표시합니다.
`kr_only`·`jp_only` 는 한쪽만 쉬는 날만 모읍니다. 셋 다 수록 기간은 두 나라
피드 중 짧은 쪽까지입니다 — 한쪽만 있는 구간을 실으면 다른 나라의 공휴일이
없는 것처럼 읽히기 때문입니다.

## 데이터를 믿을 수 있는 근거

**그 해에 유효했던 규칙으로 계산합니다.** 규칙이 개정되면 개정 시점부터
적용하고 과거로 소급하지 않습니다. 2020년 날짜는 2020년에 유효했던 조문으로
계산된 값입니다.

**확정과 잠정을 구분합니다.** 잠정 항목에는 `.ics` 안에
`X-HOLIDAY-STATUS:PROVISIONAL` 이 붙습니다. 피드별 잠정 건수는
`status.json` 의 `provisional_events` 와 랜딩 페이지에 있습니다.

**다른 구현과 대조합니다.** 독일 피드 열 벌은 `python-holidays` 의
`DE(subdiv=...)` 와 발행 범위 전 연도의 날짜 집합을 대조하는 테스트를
매번 돌립니다. feiertage-api 와의 대조는 조사 시점에 받은 응답을 측정값으로
테스트에 박아 두고 비교합니다 — 테스트는 네트워크를 타지 않습니다.

**git 히스토리가 감사 로그입니다.** 데이터가 바뀐 커밋에는 무엇을 근거로
바꿨는지 적습니다. 다만 근거의 정본은 커밋 메시지가 아니라 각 규칙 YAML 의
`source` 필드입니다 — 커밋은 언제 바뀌었는지를, `source` 는 무엇에
근거하는지를 답합니다.

**`verified` 가 뜻하는 것.** 그 항목의 근거로 공포본을 직접 확인했다는
표시입니다. **정확성 보증이 아닙니다** — `verified: false` 는 틀렸다는 뜻이
아니라 공포본을 아직 확인하지 못했다는 뜻이고, 그 경우 무엇이 막고 있는지를
`source_todo` 에 적습니다. 관보가 온라인에 없는 구간이 대표적입니다.

이름이 비슷한 값이 하나 더 있습니다. `status.json` 의 `verification` 은
**한국 규칙표의 대조 진행 집계**입니다 — 집계 대상이
`solar_holidays.yaml`·`lunar_holidays.yaml`·`designated_holidays.yaml`·
`substitute_holidays.yaml` 로 전부 `rules/kr/` 의 표입니다. 독일의
`verified` 는 각 규칙 YAML 항목의 필드이고 `status.json` 에 집계되지
않습니다. 둘은 이름이 비슷하나 다른 것입니다.

## 구조

```
sources/       외부에서 갱신되는 원천 수집 (kr: KASI API, jp: 内閣府 CSV).
               수집만 하고 해석은 하지 않는다.
sources/*/cache/  원시 응답을 받은 그대로. 커밋 대상이다 — 변화를 diff 로
               추적하기 위한 관측 기록이며, 테스트가 이 파일들을 입력으로 쓴다.
rules/         피드별 공휴일 규칙과 조립. 나라별 전체(kr, jp, de), 독일 주별
               아홉(de_be, de_bw, de_by, de_he, de_hh, de_ni, de_nw, de_rp,
               de_sh), 교차 피드(kr_jp, kr_only, jp_only).
               status.py 가 status.json 을 조립한다.
core/          국가 공통 로직 (날짜 모델, UID 생성, iCalendar 직렬화, 피드 쓰기)
data/          jp: 캐시된 CSV 에서 생성한 연도별 YAML. kr: 비어 있다 —
               rules/kr/*.yaml 규칙표에서 날짜를 유도하므로 중간 산출물을
               두지 않는다.
feeds/         발행되는 .ics 파일 열다섯 벌
tests/         테스트
docs/          운영 문서, 브랜치 운영 규칙, 작업 세션 기록
logs/          build.jsonl — 발행 시도 기록. 실패도 남는다.
status.json    지금 저장소가 주장하는 상태. 랜딩 페이지가 읽는다.
index.html     랜딩 페이지. CNAME 이 holidays.lunalism.com 을 이 저장소에 붙인다.
```

피드를 추가할 때 반드시 늘리는 것은 `rules/<코드>/` 이고, `sources/<코드>/` 는
외부에서 갱신되는 원천이 있을 때만 둡니다(kr: KASI API, jp: 内閣府 CSV).
독일은 근거가 관보 공포본이라 수집 대상이 아니며, 서지는 각 규칙 항목의
`source` 필드에 있습니다. `data/<코드>/` 도 필수가 아니라 그 나라의 소스
사정에 따릅니다 — kr 은 비어 있고(디렉터리 대칭을 위해 `.gitkeep` 으로 자리만
유지) jp 는 있습니다. `core/` 는 국가 중립으로 유지합니다.

피드 단위 범위 결정은 [`DESIGN.md`](DESIGN.md) 에 있습니다. 규칙 하나에 붙는
결정은 해당 YAML 의 주석과 `open_questions` 에 있습니다.

## 발행

`.github/workflows/publish.yml` 이 피드를 만들고 커밋합니다.
**매주 월·수·금 06:23 KST(일·화·목 21:23 UTC)로 예약되어 있습니다.** 실제 실행
시각은 GitHub 스케줄러 사정으로 몇 시간 지연될 수 있습니다. 수동
실행(`workflow_dispatch`)도 그대로 됩니다.

산출물 세 가지는 갱신 주기가 다릅니다 — `feeds/*.ics` 는 내용이 실제로 바뀔
때만, `status.json` 은 매 실행, `logs/build.jsonl` 은 실패를 포함해 매 실행
한 줄씩 커밋됩니다. 각각의 이유는 [`DESIGN.md`](DESIGN.md) 의 "발행 파이프라인"
절에 있습니다. 피드 파일에 커밋이 몇 달 없는 것은 정상 상태입니다.

UID 네임스페이스를 `holidays.lunalism.com` 으로 확정하면서 발행을 열었습니다.
`core/ics.py` 의 `UID_DOMAIN_CONFIRMED` 가 `False` 로 돌아가면 `publish()` 가
다시 거부하고 워크플로는 "피드 생성" 스텝에서 실패합니다 — 가드는 확정 후에도
그대로 남아 있습니다.

## 외부 데이터 출처

### 대한민국 — 한국천문연구원 특일정보 API

공공데이터포털 `SpcdeInfoService/getRestDeInfo` 로 대조합니다(채택 소스가
아니라 대조 상대 — 위 "무엇을 구독하나" 참조).

### 일본 — 内閣府 syukujitsu.csv

内閣府 「国民の祝日」 페이지의
`https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv` 를 받아
`sources/jp/cache/` 에 원본 바이트(CP932) 그대로 커밋합니다. 인증키가
필요 없습니다. 원본은 연 1회(전년 2월) 한 해씩 늘어납니다.

### 독일 — 각 주 관보

수집 대상이 아닙니다. 각 항목의 근거는 그 주 관보의 공포본이고, 서지(관보
호수·면·공포일·sha256)는 규칙 YAML 의 `source` 필드에 있습니다.

## 호환성 원칙

한 번 공개된 값은 되돌릴 수 없습니다. 아래 두 가지는 특히 주의합니다.

- **구독 URL** — 위 구독 표의 열다섯 주소 전부입니다. `webcal://` 로도 같은
  경로입니다. 구독자의 캘린더 앱에 그대로 박히므로 경로를 바꾸면 전부
  끊깁니다.
- **이벤트 UID** — 네임스페이스는 `@holidays.lunalism.com` 으로 **확정**
  되었습니다. UID 가 바뀌면 캘린더 앱이 같은 공휴일을 새 이벤트로 인식해
  중복이 생깁니다.

UID 는 `<날짜>-<토큰>@holidays.lunalism.com` 형태이고, 토큰에 피드를 가르는
접두사가 붙습니다. 독일 주 피드는 `de_<주>-` 를 앞에 답니다 —
`20200101-de_sh-neujahr@holidays.lunalism.com` 처럼입니다. 접두사가 없으면
같은 날 같은 공휴일이 열 피드에서 같은 UID 를 갖게 되어, 전국 피드와 주
피드를 같이 구독한 캘린더에서 한쪽이 다른 쪽을 덮어씁니다.

두 값은 확정되었습니다. 바꾸는 제안은 구독자 영향을 먼저 확인해야 합니다.

## 라이선스

코드는 MIT. `data/` 및 발행 피드의 라이선스는 원천 데이터의 이용허락범위를
확인한 뒤 확정합니다(미확인). 출처 표기 요건은 제공처 정책을 따릅니다.

## 운영자용 문서

이 저장소를 직접 돌리는 데 필요한 것 — 개발 환경, 설정과 시크릿, 필요한
GitHub 설정, 외부 데이터 출처의 운영 세부 — 은
[`docs/operations.md`](docs/operations.md) 에 있습니다.

작업 규약은 [`AGENTS.md`](AGENTS.md), 설계 결정은 [`DESIGN.md`](DESIGN.md) 에
있습니다.
