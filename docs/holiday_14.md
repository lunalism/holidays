# Holiday_14 시작 문서

작성: 2026-09-07
기준 리비전: 4ff0c39 (main, #57 머지 커밋)
이전 세션: Holiday_13 문서 (#53–#57)

코드에 없는 것만 담는다. scope 필드·DESCRIPTION 첫 줄·publish cron 의 사양은
rules/·tests/·.github/ 가 들고 있고, 이 세션의 조사 보고 다섯 벌은 /tmp 에 있다
(레포 밖 — /tmp/report_publish_delay.md, report_description_audit.md,
report_bundesweit.md, report_hh_gesetz_chain.md + report_hh_chain_forward.md,
report_de_batch2.md. 다음 세션 첨부는 확장 구현·승격 작업 때 각각 필요하다).

---

## 0. 이 세션에서 한 일

PR 넷. #54 publish cron 주 3회(월·수·금 06:23 KST, `"23 21 * * 0,2,4"`) +
서술 문구 4곳(publish.yml 주석·AGENTS.md·README 2곳) + 테스트 docstring —
주 3회는 상시 결정, cron 효과는 schedule 6건 관측 후 지연 폭 재판정.
#55 주 피드 YAML 56항목 scope 필드(bundesweit|land) + de 계열 여섯 피드
DESCRIPTION 사용자 첫 줄("독일 전국 공휴일입니다." / "{주명} 주
공휴일입니다.") — 방 피드백(근거 날것 노출, 전국/주 구분 요청)이 발단,
전국 9건은 feiertage-api 2025·2026 16주 교집합·API NATIONAL·rules/de YAML
삼중 일치로 확정. #56 de_hh 31. Oktober verified true — 승격 전례 1호(관보
PDF 실측 → source 재작성 → 테스트 상태 갱신 → 전후 비교). #57 de_hh 아홉
항목 source_todo 를 실측 경계 서술로 정확화. 그 외: 브랜치 청소(머지된
로컬 19 일괄 + docs/holiday-13 + 세션 브랜치 3, 원격 fix/landing-layout),
publish 지연 전수 실측(schedule 4/4회 98~292분, startedAt==createdAt — run
생성 지연).

닫힌 결정(각 PR 의 본문·커밋에 상세):
- **주 3회 발행 상시.** 발행 빈도와 지연 측정을 분리하지 않고 실제 run 이
  측정 데이터를 겸한다.
- **scope 는 주 피드 YAML 필수 필드, de(전국)는 금지 단언.** 교차 검증
  테스트(다섯 피드 bundesweit key 집합 == de 9 key)가 안전망 — 전국 항목을
  land 로, 주 항목을 bundesweit 로 적는 오분류를 양방향으로 잡는다.
- **DESCRIPTION 구조: 사용자 문장 / 빈 줄 / 기존 근거.** SEQUENCE 는
  DTSTART/DTEND 변경만 올린다는 기존 결정(DESIGN.md)이 이 작업을 가볍게
  만들었다 — 여섯 발행본 재생성에서 UID·날짜·SEQUENCE 전건 불변.
- **HH 통칭 "(통칭 Reformationstag)" 는 DESCRIPTION 에 유지** — 기존 테스트가
  프롬프트 지정 문구의 누락을 잡았다(안전망 작동 사례).
- **verified 기준 확장((b)안: 공포법이 인용하는 공식 정비집 Sammlung 을 true
  근거로 인정)은 보류** — 실물 열람 경로가 없는 한 결정 실익 없음. HH
  아홉은 false 유지가 정직한 종착.

## 1. 정정

- **"피드별 로그 원복" 은 원복이 아니라 신규 설계다.** holiday_10 등록 자체가
  "(신규)" — 세션 전파 중 와전. git 이력에 제거된 로그 줄이 없음을 실측하고
  멈췄다. holiday_12 "13건" 과 같은 문서 간 전파 패턴 2회째.
- **#54 프롬프트의 branch 접두사 chore/ 는 레포 4종 밖** — feat/ 로 정정
  (브랜치는 rename, 첫 커밋 메시지의 `chore(publish):` 접두사는 그대로
  머지됐다 — 브랜치 규약은 접두사 4종을 브랜치 이름에만 건다).
- **#56 지정 source 문구가 기존 DESCRIPTION 통칭 계약을 누락** — CC 가
  테스트로 잡았다. 프롬프트가 기존 계약을 대조하지 않은 오류.
- **순방향 체인(2018 이후) 미조사는 역방향 프롬프트의 설계 공백** — 별도
  조사로 마감(2019·2021 개정 존재, 둘 다 § 2a, § 1 무관).
- (부수) 검증 스크립트의 마지막 단언을 잘못 써서(전국 항목의 첫 줄을 함부르크
  줄로 검사) 한 번 실패했고, 셸 `set -e` 가 그 실패에서 멈추지 않아 커밋·push 가
  그대로 진행됐다(#56). 올바른 기준으로 재검사해 결과는 정상 — §6.

## 2. 검토했다가 버린 갈래

- **DESCRIPTION 재설계의 kr·jp 확장**: 형태·규약이 다르고 문제(근거 노출·구분
  부재)가 de 에만 있다 — de 계열만.
- **scope 파생 방식**(key ∈ de 9 로 판정, 필드 없이): rules/ 간 결합·무소음
  재분류 위험으로 기각, 관찰은 교차 검증 테스트로 전환.
- **SUMMARY 한국어화**: SUMMARY 는 법조문 원문 원칙 — 한국어는 DESCRIPTION.
- **한국어 명칭 번역**(통일의 날 류): 출전 문제가 열린다 — 범위 제외.
- **`근거: ` 리터럴 8곳 통합 리팩터링**: 범위 팽창 — 기각.
- **발행 고빈도 프로브 워크플로**(cron 2벌 대조군): 발행 자체를 주 3회로
  올리는 결정으로 대체.
- **verified 승격 HH 9건 일괄**: 1994 이전 공포본 부재로 불가 확정 —
  source_todo 정확화(#57)로 전환.

## 3. 레포 밖에서 확인된 것

- **luewu.de(출판사 Lütcke & Wulff)가 HmbGVBl. 공식 발행처** — 1995~ 전 호
  PDF 무료(2014~ 는 /gvbl/YYYY, 1995~2013 은 archiv-…-jahrgang-YYYY 경로).
  juris 셸과 별개 경로. Transparenzportal 도 1995~ 이고 내용 검색을 luewu 로
  위임(CKAN 실측: temporal_coverage_from 1995-01-01, 리소스는 luewu 링크) —
  함부르크 디지털 공개의 1995 경계는 이중 확인.
- **Feiertagsgesetz(HH) 개정 체인 완성**: 1994 S.441(범위 밖) → 2000 S.358
  (§2a) → 2013 S.304(§3a) → 2017 S.386,388(§2a) → 2018 S.63(§1 유일 개정) →
  2019 S.516(§2a) → 2021 S.75,77(§2a) → 2022 S.581 시행령. § 1 은 2018 후
  2026 Nr.26(28.08)까지 무변경 — 공포본만으로 성립. 각 호 PDF sha256 은
  /tmp/report_hh_gesetz_chain.md·report_hh_chain_forward.md(레포 밖 — 다음
  승격 작업 때 재수령 가능, URL 패턴은 rules/de_hh YAML 주석·source_todo 에).
- **recht.nrw.de 가 GV. NRW 1946(창간)~현재 전 호 무료 공개** — NW 백로그
  11건 전건이 승격 잠재 대상으로 재지형(이 세션 실측 아님 — 사용자 확인).
- **Berlin: berlin.de 법무행정이 연도별 GVBl. 호 PDF 호스팅**(2018 확인, 커버
  하한 미확인 — 사용자 확인). BE 백로그 중 2018 이후 개정분(frauentag·
  일회성들)은 공개 범위 안 전망.
- **확장 1차 배치 4주 실측**(/tmp/report_de_batch2.md): BW 전건 true 가능
  (1995 Neufassung 이 § 1 전문 — Landtag BW 아카이브 1952~2023 호별 스캔),
  SH 전건 true 가능(2004 제정 + 2018 개정, Verkündungsportal 1947~2024
  연도판 — 2004 연도판은 506MB 라 Range 분할 수신), NI 는 HH 구도(2018 개정만
  관보 안, 관보 2006~2018 + 2019~ 접근 미확인), RP 전건 false(자구 근거
  ≤2003, gvbl.rlp.de 2004~; 1970 은 DDB·dilibri JS 차단). feiertage-api 대조
  4주 모두 불일치 0. 조사 축 신설: 통합본 포털과 관보 아카이브는 별개 —
  juris 계열(BW·RP·SH)은 이번에도 셸, NI-VORIS 만 정적.
- **방 교차 확인**: "연방 지정은 통독일, 나머지는 주법" — 우리 구조
  (Einigungsvertrag 1건 + 주법 16벌)와 일치. 데이터 영향 없음.
- 방 피드백이 #55 의 발단: DESCRIPTION 근거 날것 노출 + 전국/주 구분 요청.
  새 DESCRIPTION 은 다음 발행부터 자동 반영.

## 4. Codex 리뷰의 자리

#55 실행(load 경로 신규 로직, adversarial-review) — 확인 항목 ①~⑤ 명시,
항목별 판정, approve 지적 0. ③ "양방향 오분류 검출" 서술이 원하던 형태.
#54·#56·#57 생략(로직 무변경) — 생략 근거를 PR 본문에 명시하는 관행 지속.
리뷰어의 read-only 전제(pytest 미실행)는 이번에도 본 세션 실측(963 passed)
+ CI 가 채웠다.

## 5. 미결

- **수요일 9/9 06:23 KST 첫 run** — 새 cron 첫 실측 + 새 DESCRIPTION 첫 자동
  발행. 재판정은 schedule 6건(9/21경).
- **확장 구현, 순서 SH → BW → NI → RP**: SH 가 기존 관례에 전부 들어맞아
  scope 이후 첫 신규 피드 + Codex 실행 1회 자리. BW 는 신규 판단 셋(호 번호
  없는 열거 → BY 식 순번 인용, Erscheinungsfest vs heilige_drei_koenige
  token, 3. Oktober 조문 밖 — Einigungsvertrag 근거의 주 피드 첫 사례). RP 는
  Nr.10 이틀 묶음 분해 + Abs.2 일회성 수권. NI 는 알파벳 호 + 관보 2019~ 접근
  미해결. 구현 브랜치마다 개정 체인 마감(HH [0]·[1] 방식)을 선행 단계로.
- **승격 백로그 재지형**: NW 11(recht.nrw.de — 최우선 후보), BE(커버 하한
  확인 후), HE(관보 미조사 — 유일한 공백), HH 9(오프라인만).
- 2차 배치 조사(BB·HB·MV·SL·SN·ST·TH) — 관보 아카이브 축 포함.
- 랜딩 데이터 주도 렌더링 — 11피드 확장 전 필수(수동 마크업 반복 방지).
- 방·Issues 회신 대기(베를린 실기기·바이에른 사례), attribution 판정 보류
  (grep 0 이 규약 효과와 안 갈라짐), rules/de → 주 피드 다섯 결합
  (BUNDESWEIT_SENTENCE import — SH 구현 시 여섯째), 이월 잔여(README 2차에
  "발표는 어디서" 방 문답 반영 후보 추가, xpassed 29 불변, 기타 holiday_13
  §5).

## 6. 규약

- 승격 후보(1세션): **CC 독립 재실측** — 프롬프트 지정 문구 속 미실측 사실
  (Transparenzportal 1995~)을 CC 가 받아 적지 않고 CKAN 실측 후 반영.
  "수용에도 재현"의 역방향(나→CC) 첫 사례.
- 신규 후보(1세션): **검증 스크립트 실패 시 push 중단 배선** — `set -e`
  미정지로 실패가 push 를 막지 못한 사례(#56). 결과는 재검사로 닫힘.
- 신규 후보(1세션): **조사 보고의 원본 병기**(계산값·지연값에 원본 createdAt
  병기) — 이차 소스 재확인 요건의 표준형으로.
- 유지: 테스트 커밋 선행(#55·#56·#57), 멈춤 조건 명시(발동 1회 — #56 통칭
  판단 요청), Codex 항목 명시·생략 근거 명시, [남김]/[뺌]/[대체], grep 0
  확인.
- Holiday_07 §7 셋·다섯 줄 규칙 — 7세션째. 승격 판단은 다음 세션 몫
  (이 문장을 복사하지 말고 다시 판단할 것).
