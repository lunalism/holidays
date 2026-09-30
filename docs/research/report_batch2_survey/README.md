# report_batch2_survey — 재현 기록

`docs/research/report_batch2_survey.md` 의 주별 원보고·요청 로그·교차 확인 출력이다. 보고
본문은 조사 당시 경로 `~/holidays-reports/report_batch2_survey/` 를 가리킨다. 그 폴더가 이
폴더다(아래 예외는 옮기지 않았다). 조사는 2026-09-30, `origin/main` `be1c45f` 에서 했다.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**

## 파일

| 파일 | 무엇 |
|---|---|
| `state_BB.md` … `state_TH.md` | 주별 원보고(A–F). 병렬 에이전트 일곱이 한 주씩 썼다. 보고 본문의 「주별 절」 이 이것을 제목 단계만 내려 옮긴 것이다 |
| `state_XX_fetch.log` | 주별 요청 로그(아래 「요청 로그의 한계」) |
| `state_SL_fetch_excerpt.log` | SL 요청 로그의 발췌 — `jsessionid` 값만 `[가림]` 으로 바꿨다 |
| `fapi_2026.sh` → `fapi_2026.log`·`fapi_2026_summary.txt` | G — feiertage-api 2026 일곱 주 요청과 요약(주별 항목·hinweis) |
| `spotcheck.log` | 보고 「방법과 한계」 의 교차 확인(BB·SN 조문, MV·HB 관보 자구) |

## 요청 로그의 한계 — 전수가 아니다

주별 조사 에이전트 일곱이 세션 scratchpad 하나를 함께 썼다. 한 에이전트가 만든 fetch
도우미 스크립트를 다른 에이전트가 덮어써, 요청 행이 남의 로그에 기록되거나 로그 파일이
사라졌다. 각 로그의 머리말(`#` 줄)이 그 사정을 적는다.

- `state_HB_fetch.log` — 최초 로그 파일이 사라졌다. #1–#17 은 터미널 출력에서 재구성했다.
  #16–#17 은 실제로는 다른 에이전트의 로그(`st.log`, 옮기지 않음)에 기록됐다.
- `state_MV_fetch.log` — 타 주 요청(약 45 건)이 섞여 들어와, MV 호스트 행만 남기고 지웠다.
  그 행들은 원래 주의 로그에 없을 수 있다.
- `state_SN_fetch.log` — 원래 로그가 사라져 09:29Z 이전 행은 터미널 출력에서 재구성했다.
- `state_ST_fetch.log` — 1–12 행은 터미널 출력에서 옮겨 적었다.
- `state_TH_fetch.log` — curl 행 대부분이 실행 당시 MV 로그로 기록됐다. 이 파일의 행은
  터미널 출력에서 옮겨 적었다. Wikipedia 에 대한 요청이 MV 에이전트와 1 초 간격으로 겹쳐,
  에이전트 전체로 보면 호스트당 3 초 간격이 지켜지지 않은 때가 있다.
- `state_BB_fetch.log`·`state_SL_fetch_excerpt.log` 는 머리말에 유실·재구성 기록이 없다.

따라서 이 로그들로 요청 전수를 재현할 수 없다. 다음 병렬 조사에서는 에이전트마다 scratch
디렉터리를 따로 둔다.

## 옮기지 않은 것

`docs/research/README.md` 「넣지 않는 것」 — 사이트 응답 덤프와 세션 값이 든 로그는 두지
않고, 필요한 로그는 그 값을 지운 발췌만 둔다.

- `fapi_2026_BB.json` … `fapi_2026_TH.json` — feiertage-api 응답 덤프.
  `fapi_2026_summary.txt` 가 대신한다(날짜·이름·hinweis 전부).
- `state_SL_fetch.log` — `jsessionid` 세션 값이 든 로그. `state_SL_fetch_excerpt.log` 가
  대신한다.

보고 본문은 옮기면서 고치지 않았다. 본문에 나오는 `fapi_2026_*.json`·`state_SL_fetch.log`
는 이 폴더에 없는 파일을 가리킨다. HB 의 `gsid=` 는 Transparenzportal 의 문서 식별자이고
세션 값이 아니다.
