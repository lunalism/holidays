# Holiday_13 시작 문서

작성: 2026-09-06
기준 리비전: 3d32587 (main, #52 머지 커밋)
이전 세션: Holiday_12 문서 (#45–#52)

코드에 없는 것만 담는다. 주 피드 다섯의 사양은 rules/de_*/ 와 tests/ 가 들고
있고, 4주 법령 조사는 /tmp/report_de_laender.md 가 들고 있다(레포 밖 — 조사분
5주는 전부 소화됐으므로 다음 세션 첨부는 verified 승격 작업 때만
필요하다).

---

## 0. 이 세션에서 한 일

PR 여덟. #45 holiday_12 문서, #46 holiday_11 개행 정리(내용 불변), #47 랜딩
de_be 줄, #48 de_by.ics(12건 — verified 12/12 true, 첫 전건 true 피드),
#49 de_he.ics(10건), #50 de_hh.ics(10건), #51 de_nw.ics(11건), #52 랜딩
아코디언 + 소개문. 피드 일곱 → 열하나. 조사분 5주 완주. 방 공지
발송(de.ics·
de_be 공개, 베를린 실기기 검증·바이에른 사례 질문 — 레포 밖). 프로젝트
지침
구판 교체(시점 종속 서술 제거, 피드 열거는 세션 문서로 위임 — 레포 밖
파일).

닫힌 결정(각 PR 의 판단 목록·커밋에 상세):
- **SUMMARY 는 각 주 조문 표기.** 주 간 불일치(Fronleichnam/Fronleichnamstag,
  Allerheiligen/Allerheiligentag, Himmelfahrtstag/Christi-Himmelfahrts-Tag,
  "31. Oktober")는 통일하지 않는다 — 입법 사실의 반영. #49 에서 멈춤 조건
  (de_by 와 표기 상이) 발동 후 확인으로 확정.
- **token 은 내부 식별자** — SUMMARY 원칙의 적용 대상이 아니다. 기존 확립값
  재사용이 원칙이고 신규 명명은 reformationstag 하나(HH Nr. 8 "31. Oktober",
  charset 이 날짜형 불허). NW 의 Allerheiligentag 도 allerheiligen 을 쓴다.
  신규 명명 0 은 차집합 테스트로 고정한다.
- **verified: BY 12/12 true**(gesetze-bayern.de 가 정적 HTML 로 원문 반환),
  **HE 10·HH 10·NW 11 전건 false**(공식 경로 실패). HH 의 31. Oktober 는 의회
  문서(Drucksache 21/12153, 의결 전 안)가 있어도 false — 공포 관보만 true
  근거. 조문에 항목별 호 번호가 없으면(BayFTG) 열거 순번 + 따옴표 표기로,
  있으면(HE·HH·NW) Nr. n 직접 인용으로 개별 인용한다.
- **커밋 메시지 Claude-Session 트레일러 금지.** #49 에서 rebase 로 제거(트리
  불변 확인), main 의 기존분(#48 까지)은 소급하지 않는다. 같은 브랜치 내
  커밋
  SHA 참조도 금지(rebase 로 무효화됨). push 전 `git log --format=%B
  origin/main..HEAD | grep -c "Claude-Session"` == 0 을 보고에 포함.
- **랜딩 주 피드는 네이티브 details 아코디언**, 라벨 "독일 주별 피드 (5)",
  기본 접힘, 높이 슬라이드 없음. 소개문은 주 이름·개수 없이("썩지 않는
  문구").
  데이터 주도 렌더링 리팩터링은 다음 랜딩 PR — #52 가 마크업 수동 추가의
  마지막이다.

## 1. 정정

- **"13건" 오기가 두 단계 전파됐다.** holiday_12 §5("13건 분해") → 시작
  프롬프트 → BY 구현 지시. 실측(feiertage-api 2026 BY 15건 − 지자체 한정 3건 =
  12건, BayFTG Art. 1 Abs. 1 Nr. 1 열거 12건)이 끊었다. "즉석 계산 금지 +
  API 기준" 지시가 방벽으로 작동했고, 사용자가 같은 curl 을 직접 재실행해
  확인했다. 유입 경로는 세간의 "바이에른 13개" 통념(Mariä Himmelfahrt 포함
  셈)으로 추정 — §3.
- **"xfail 처리는 BE 관례" 는 서술 오류였다.** BE 실제 관례에 xfail 마크가
  없다 — verified false + source_todo 필수 + 상태를 고정하는 테스트 하나.
  자동 xfail 은 kr 픽스처 로더에만 있다. CC 실측 보고 후 실제 관례로 확정,
  HE·HH·NW 에 그대로 이식.
- **공지 초안의 피드 URL 에 /feeds/ 경로가 빠져 있었다** — 랜딩 스크린샷
  실측이 잡았다(레포 밖, 사용자 기록). URL 은 항상 실측한 값을 복사할 것.
- **선행 PR(#50) 머지 확인 전에 후속(NW) 구현 프롬프트를 냈다.** CC 가
  feat/de-hh 위에 스택(base 를 feat/de-hh 로 PR 생성, #50 머지 후 자동
  재지정)으로 정합을 유지했으나 순서 원칙은 "머지 확인 후 후속
  프롬프트"다.
- (부수) BE 승격 백로그는 "기저 9건 + frauentag" 이 아니라 **11건** — 2020
  일회성(achter_mai_2020)도 2019 개정 관보를 보지 못해 false 다. holiday_12
  §5 의 셈이 하나 모자랐다.

## 2. 검토했다가 버린 갈래

- **kr 식 xfail 도입**(verified false 항목의 정답 대조를 xfail 로): 주 피드에
  첫 도입이 되어 신규 로더·마킹 코드가 생긴다. BE 관례로 충분 — 기각.
- **Fronleichnam SUMMARY 를 de_by("Fronleichnam")에 맞추는 안**: "각 피드는
  자기 조문 표기" 원칙(de_be 의 Himmelfahrtstag 전례)에 어긋난다 — 기각,
  HE 는 "Fronleichnamstag".
- **allerheiligentag 신규 token**(NW): token 은 내부 식별자라 조문 표기를
  따를 이유가 없고 de_by 의 allerheiligen 이 있다 — 기각.
- **아코디언 높이 슬라이드·div+JS 재구현**: 네이티브 details 는 열리는 순간
  높이가 정해져 슬라이드는 JS 높이 측정이 필요하고 그 순간 네이티브가
  아니다 — 마커 회전 + fade-in 만.
- **de_nw 를 main 에서 따는 안**: #50 미머지라 main 에 de_hh 가 없어 5주
  교집합·열 피드 무영향 단언이 성립하지 않는다 — feat/de-hh 스택으로.
- **31. Oktober 의 verified 승격**(의회 문서 근거): 의결 전 안은 공포본이
  아니다 — 병기만.

## 3. 레포 밖에서 확인된 것

- **gesetze-bayern.de 가 4주 중 유일하게 열린 공식 포털이다.** 정적 HTML
  19KB 로 Art. 1 전문 반환("Text gilt ab 01.08.2013"). juris 계열(BE·HE·HH)과
  NRW 검색 SPA 는 이번에도 셸만 — verified 2단계의 실증이 5주로 늘었다.
- **feiertage-api 의 지자체 한정 표시는 hinweis 필드다.** BY 15건 중 셋에만
  붙고, HE·HH·NW 는 전부 공란. "13건" 통념은 이 hinweis 를 무시한 셈으로
  보인다 — [추론].
- **합성 KeyboardEvent 는 details/summary 를 토글하지 못한다.** 네이티브 활성
  동작은 trusted 입력에만 반응한다. CDP Input.dispatchKeyEvent 로 실측(Tab
  → summary 포커스, Enter 열림, Space 닫힘). 또 Chrome 은 닫힌 details 를
  content-visibility 로 숨겨 getClientRects 가 접힌 상태에서도 사각형을
  돌려준다 — 가시성은 checkVisibility() 로 잴 것.
- **Codex 리뷰어는 read-only 샌드박스라 pytest 를 못 돌린다**(uv 캐시 초기화
  실패). 다섯 번 모두 "사람이 pytest 확인" 단서를 남겼고, 본 세션 실측 +
  CI 가 그 자리를 채웠다. 리뷰 판정은 정적 검토임을 전제로 읽을 것.
- **status.json 의 kasi_key.days_left 는 시계 파생값이다.** main 의 status 가
  전날 UTC 에 생성돼 있으면 발행 시 하루 줄어 diff 에 뜬다(#50 에서 703→702).
  무영향 단언에서 generated_at 과 같은 급으로 취급.
- **세션 밖 편집기 덮어쓰기 3회**(07:04·07:08·07:10 KST): Holiday_12 초안
  버퍼가 holiday_11.md·holiday_12.md 위에 차례로 저장됐다. 원인 미확인,
  이후 재발 없음. 작업 전 git status 확인이 방벽.
- auto 모드 분류기가 "파이썬 heredoc 편집 + 커밋" 복합 명령을 한 번
  차단했다. 편집(Edit 도구)과 커밋을 나누어 실행하니 통과했다(차단
  요인은 미확인).

## 4. Codex 리뷰의 자리

다섯 번(#48~#52) 전부 approve, 지적 0. #47 은 판박이 확장으로 생략 — §6 의
생략 기준이 양방향으로 적용된 첫 세션이다. 확인 항목을 프롬프트에
번호로
명시하고(①~⑤) 리뷰어가 항목별로 확인 서술을 남기게 한 방식이 자리
잡았다 —
approve 가 "못 찾음" 이 아니라 "이 다섯을 봤다" 가 된다. 단언은 전부 테스트
커밋에 선행 포함됐고(4벌 연속), 리뷰 대기 중 CC 가 추가한 회귀는 없었다
(holiday_12 §4 의 순서 지적이 이번엔 해당 없음).

## 5. 미결

- **9/7(월) 09:00 KST schedule — 열한 피드 체제 첫 자동 실행.** holiday_12
  시점 "일곱"에서 네 번 이동했다. 관찰 항목(지연 여부)은 불변. 지연
  2회째면
  분 오프셋 + 원복 피드별 로그 chore 명분.
- **방·Issues 회신** — 베를린 실기기 검증 결과, 바이에른 임시 공휴일
  사례.
  사례가 오면 판정, 없으면 실측대로 designated 없이 유지.
- **랜딩 데이터 주도 렌더링 리팩터링** — 다음 랜딩 PR. 검증 계약: 렌더
  결과
  DOM 이 리팩터링 전과 동일(dump-dom 전후 비교, data-pending 잔여 3 포함).
- **verified 승격 백로그**: BE 11(기저 9 + frauentag + 2020 일회성), HE 10,
  HH 10(31. Oktober 가 최근접 — HmbGVBl. 2018 S. 63), NW 11(관보 스캔 OCR
  경로). 착수 5주 중 공식 원문 확인은 BY 하나, 미착수 주법 11벌.
- **attribution 설정** — ~/.claude/settings.json 에 `attribution.commit/pr` 을
  빈 문자열로 둔 상태. 이 세션에는 듣지 않았다(하네스가 트레일러 지침을
  계속 보냈고 CC 가 규약으로 제외). 다음 브랜치 첫 커밋에서 실제 효과
  확인.
- **머지된 로컬 브랜치 19개** — `git branch --merged origin/main` 실측.
  holiday_12 의 13개 + 이번 세션 6개(feat/landing-de-be, feat/de-by,
  feat/de-he, feat/de-hh, feat/de-nw, feat/landing-state-feeds. docs 둘은
  머지 때 지웠다). git branch -d 일괄.
- 이월: README 2차(로고 선행), 프랑스·스페인·US·UK·이탈리아(방 요청 — 주
  피드 완료로 재개 가능 상태, 착수 판단은 별도), top_level_sections,
  pyproject 주석, data/kr/.gitkeep, Node 20, 저장소 설정, 로고, 政令 원문,
  krx·jp/tse(후순위), xpassed 29건(이번 세션 내내 29 로 불변), __main__ 인자
  파싱.

## 6. 규약

- **승격 확정: 커밋 트레일러·attribution 푸터·브랜치 내 SHA 참조 금지 +
  push 전 grep 확인 보고** — #49 rebase 이후 세 브랜치(#50·#51·#52) 연속
  이행. 프롬프트 상비 문구로.
- **승격 확정: 테스트 커밋 선행** — de_by·de_he·de_hh·de_nw 4벌 연속. 테스트
  커밋 시점의 수집 오류(패키지 부재)는 정상으로 취급하고 커밋 메시지에
  적는다.
- **승격 확정: Codex 확인 항목 명시 후 항목별 판정** — 5회 연속. 생략 기준
  (신규 로직 있으면 실행, n 벌째 판박이면 생략)은 #47 생략·#48~#52 실행으로
  양방향 적용 확인.
- 유지: **[남김]/[뺌]/[대체]** — 4세션째. 이번 세션 [대체]는 브랜치 이름
  (landing/ → feat/), 브랜치 기점(main → feat/de-hh 스택), 13→12 건 셋 —
  전부 규약·실측 근거. **수용에도 재현** — 13→12 건에서 재적용(사용자
  직접
  curl). **신규 파일 무영향 단언은 전후 비교로** — 여섯 PR 전부 이행.
- 신규 후보(1세션): **멈춤 조건은 지시문에 명시** — SUMMARY 표기 상이(#49),
  API hinweis 출현, 피드 URL 비 200(#47·#52) 처럼 "실측 후 다르면 멈추고
  보고" 를 구현 전 단계로 두는 것. 이번 세션 발동 1회(#49), 미발동 5회.
- Holiday_07 §7 셋·다섯 줄 규칙 — 6세션째. 승격 판단은 다음 세션 몫
  (이 문장을 복사하지 말고 다시 판단할 것).
