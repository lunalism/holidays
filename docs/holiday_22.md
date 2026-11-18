# Holiday_22 시작 문서

작성: 2026-11-18
기준 리비전: c44da09 (main, 「Merge pull request #125」). 이 리비전이 마지막 PR 머지이고, 그 뒤 main 에
발행 커밋은 없다(§0 「머지 뒤 main」).
이전 세션: Holiday_21 문서(#122 와 PR 없는 MV 준비 조사, 문서 자체는 #123). 이 문서는 그 이후(#123–#125 와
PR 없는 조사 둘)를 담는다. 이 문서 자체가 그다음 PR 이다.

코드와 상설 문서에 있는 것은 옮겨 적지 않는다 — 가리킨다. 이 구간의 조사 보고는 전부 구현 PR 이
`docs/research/` 로 옮겼다:

- `docs/research/report_mv_prep.md` 와 폴더 — MV 준비(2026-10-07). #124 가 옮겼다
- `docs/research/report_mv_retry.md` 와 폴더 — MV 한 번의 재시도(2026-11-18). #124 가 옮겼다
- `docs/research/report_de_mv_impl/` — de_mv 구현 때의 확인(P1·P3·P4, P3 판정표 87 건)
- `docs/research/report_sn_prep.md` 와 폴더 — SN 준비(2026-11-18). #125 가 옮겼다
- `docs/research/report_de_sn_impl/` — de_sn 구현 때의 확인(P1·P3)

---

## 0. 이 세션에서 한 일

PR 셋(#123–#125), 커밋 22 + 병합 커밋 3. 그 사이에 PR 없는 조사 둘(MV 재시도, SN 준비)이 있다.

- **#123 — Holiday_20 마감 문서**(`docs/holiday_21.md`, 커밋 1). CI 녹색 뒤 CC 가 사람의 `gh` 자격 증명으로 머지했다(`399a374`). GitHub 는 사람의 계정을 머지한 사람으로
  기록한다.
  - **빠뜨린 단계:** 그 작성 지시에 AGENTS.md 의 「PR 본문은 만들기 전에 초안을 확인한다」 가 없었고,
    초안을 사람에게 보이지 않고 PR 을 열었다. 이 문서부터 문서 PR 도 초안을 먼저 보인다(§6).
- **MV 한 번의 재시도(PR 없음).** `report_mv_retry` 를 2026-11-18 에 돌렸다. 사실은 §1-1.
- **#124 — 메클렌부르크포어포메른 주 피드 de_mv (커밋 10).** 사람이 머지했다(`38c8db2`, M7).
  - 11 건, `feeds/de_mv.ics` 129 이벤트(2020–2022 10 건, 2023–2031 11 건). Frauentag 는
    `effective_from: 2022-07-13`. verified 는 11 건 전부 false.
  - 로더: de_mv 만 `effective_from`(date, 포함 경계)을 받고 닫힌 필드 집합·최상위 키·중복 키를 거부한다.
  - 커밋 4 `420e95c` 가 Holiday_21 §5 의 README 「독일 피드 열 벌」 을 닫았다.
  - 사람의 결정 M1–M7 은 #124 본문에 있다.
- **SN 준비 조사(PR 없음).** `report_sn_prep` 을 2026-11-18 에 돌렸다.
- **#125 — 작센 주 피드 de_sn (커밋 11).** 사람이 머지했다(`c44da09`, S9).
  - 11 건, `feeds/de_sn.ics` 132 이벤트. 고정 6 + 부활절 이동 4 + Totensonntag 기준 1. verified 는
    11 건 전부 false.
  - 새 표 `rules/de_sn/totensonntag_holidays.yaml` 과 정수 전용 필드 `totensonntag_offset`(de_sn 로더만).
  - 새 key `buss_und_bettag`. 사람의 결정 S1–S9 는 #125 본문에 있다.

테스트는 1850(#124 시작) → 1979(#124 끝) → **2095** 통과다. xfail 4·xpass 29 는 그대로다. 신설 테스트 파일은
`tests/test_de_mv_feed.py`·`tests/test_de_sn_feed.py` 둘이다. 이 문서를 쓴 환경에서 c44da09 기준으로 다시
돌렸다(2095 passed, 4 xfailed, 29 xpassed. `ruff check --no-cache .` 통과).

**머지 뒤 main(사전 측정, c44da09 기준)**

- `38c8db2..c44da09` 의 first-parent 커밋은 #125 병합 하나다. 발행 커밋은 **0 개**다.
- `feeds/de_mv.ics`(129)·`feeds/de_sn.ics`(132)는 각 PR 의 판과 **DTSTAMP 까지 바이트가 같다** — de_mv 는
  `cc97616`·`5ea6b75`, de_sn 은 `1f831ab`·`0f03630` 의 판. 그 뒤 발행 run 이 없었다(§3-4).
- 피드 수 서술은 모두 맞는다: `README.md:114` 「독일 피드 열네 벌」, `README.md:151` 「.ics 파일 열아홉 벌」,
  `README.md:4–5`(열아홉, 주별 열셋), `README.md:144`(열셋), `README.md:218`(열아홉 주소), `README.md:228`
  (열네 피드), `docs/operations.md:33`(열아홉 벌), `DESIGN.md:279`(열아홉), `DESIGN.md:422–423`(열셋·열세).
  실물은 `feeds/*.ics` 19, `feeds/de*.ics` 14, `status.json` 피드 19, publish.yml FEEDS 19 다.

닫힌 결정 — 각 한 줄, 근거는 문서·주석의 절:

- MV 는 **보류를 벗어났다** — #124 M1, `rules/de_mv/solar_holidays.yaml` 머리 주석.
- SN 의 날짜 규칙은 **(iii) Totensonntag − 4** — #125 S2, `rules/de_sn/feed.py` docstring.
- 두 피드 모두 **verified 전건 false** — #124 M3, #125 S4, 각 `source_todo`.
- MV 관보 **E-Mail 요청은 하지 않는다** — #124 M4.

## 1. 판단이 갈린 지점

### 1-1. MV

`report_mv_retry`(2026-11-18, 요청 04:51:39Z–05:00:35Z)의 사실:

- 공식 포털이 § 2 를 조문 단위 id `jlr-NNLMV00007A2FNN00000000003` 으로 냈다 — 「Fassung vom: 07.07.2022 /
  Gültig ab: 13.07.2022」. 원래 법 전체 id `jlr-FeiertGMVrahmen` 은 이번에도 실패했다(문서 API·toc 500).
- GVOBl. M-V 2022 Nr. 31 은 받지 못했다. 2026-09-30 의 PDF 주소가 `land-mv.de` 첫 화면으로 넘어간다.
- 2020–2025 관보 목록에는 닿지 못했다. 닿은 2026 목록은 링크 글자에 제목이 없다.

**사람의 결정**

- **MV 는 보류를 벗어난다.** 보류 이유는 공식 현행 조문이 없다는 것이었고, 포털의 조문 단위 자구가 그것을
  풀었다(#124 M1).
- **관보 E-Mail 요청은 하지 않는다** — 실행할 만하지 않다고 보았다(M4).
- **일회성 지정 확인은 구현의 P3 으로 옮겼다** — 포털 검색, 제목만, 결과 87 건(#124 본문 「P3 — 포털 검색」).
- M1–M7 전부: #124 본문.

**HB 와의 일관성.** HB 는 구현 전에 관보 전문 검색을 요구했고 MV 는 요구하지 않았다. 사람은 이것을
받아들였다. HB 의 조건은 § 2 Abs. 1 의 현행성에 관한 것이었고, MV 는 공식 통합본이 그 현행성에 답한다. 남은 공백은 일회성 확인 하나이고, 그 공백의 위험은 날짜가 틀리는 것이 아니라 빠뜨리는
것이다.

### 1-2. SN

`report_sn_prep`(2026-11-18) 뒤 #125. 사람의 결정은 S1–S9(#125 본문).

- **key `buss_und_bettag`** — 2026-11-18 승인(S1, `rules/de_sn/totensonntag_holidays.yaml` 머리 주석).
- **규칙 꼴 (iii) Totensonntag − 4** — 조사의 권고 (ii) 대림절 첫째 주일 − 11(`advent_offset: -11`,
  `report_sn_prep.md` D2)을 두고 골랐다(S2).
  - 두 꼴은 1990–2100 의 111 해에서 날짜가 같다(`report_sn_prep/c3_compare.tsv`, (i)(ii)(iii) 111/111 일치).
  - 고른 까닭은 감사의 추적성이다. 기준일은 같은 법 § 2 가 정의하는 날(「letzter Sonntag vor dem
    1. Advent」)이고, 오프셋은 주의회 보고서의 문장(「am letzten Mittwoch vor dem Totensonntag」)이다.
  - 정확성은 꼴이 아니라 테스트가 지킨다 — `tests/test_de_sn_feed.py` 의 1990–2100 검사(로더와 독립인
    「11월 23일 앞 마지막 수요일」 계산)와 python-holidays SN 2020–2031 대조.
- **Buß- und Bettag 의 DESCRIPTION 은 다른 항목보다 길다** — 2026 이벤트에서 접힘 이어짐 줄 13(다른 열 건은
  4–5). 날짜의 근거가 주의회 문장 하나뿐이라 사람이 그대로 두었다(S3).
- **#125 Codex** — 지적 14: 고침 3, [대체] 적용 3, [남김] 7, 기각 1(§4).

### 1-3. 프롬프트·보고의 전제가 틀렸고 실측이 잡은 자리

- **「1992 원법은 온라인에 없다」**(#125 커밋 2 의 문구) — 관측은 「발행사 판매 사이트에서 찾지 못했다」 였다.
  CC 자기 검토가 고쳤다(`1e0dcb2`). 같은 종류를 #124 Codex 지적 4 가 MV 에서 잡았다(`e209827`).
- **「2002 Nr. 9 는 유료 보관 상품 안에만 있다」**(S4 의 문구) — 관측은 검색 실패와 보관 상품의 연도
  범위다. 사람이 [대체] 로 정했다(`2de477f`).
- **SN 일회성 공백 목록** — 첫 판에서 2023 Nr. 2 Anlageband 가 빠졌다. Codex 가 잡았다(`3abd96a`).
- **`tests/test_de_scope.py::_tables()`** — 표 이름을 손으로 나열해 세 번째 표의 key 를 몰랐다
  (`KeyError: 'buss_und_bettag'`). `docs/operations.md` 「피드 추가」 1–14 에 없는 배선 지점이다(#125 본문).

## 2. 검토했다가 버린 갈래

- **SN (ii) 대림절 첫째 주일 − 11** — 조사의 권고. 같은 날짜지만 기준일이 법이 정의한 날이 아니다(§1-2).
- **SN (i) 요일 + 배타 경계(11월 23일 앞 마지막 수요일)** — 공식 문서에서 이 꼴의 서술을 찾지 못했다
  (`report_sn_prep.md` D2). 테스트의 독립 계산으로만 쓴다.
- **Hessen GVBl. 1971 을 SN `source` 의 근거로** — 머리 주석의 교차 확인 한 줄로만 둔다(S3).
- **SächsGVBl. 2002 Nr. 9 구매** — 사지 않는다(S4).
- **MV 관보 E-Mail 요청** — M4.
- **de_bb 식 관보 목록 제목 검색(MV)** — 관보 화면에 2020–2025 목록이 없어 하지 못했다. 포털 검색으로
  대신했다(#124 본문 P3).
- **이 PR 들에서 전 로더 값 검증** — 별 PR 로 묶는다(§5).

## 3. 레포 밖에서 확인된 것

### 3-1. 작업 환경

- 사람의 작업 레포는 이제 `<local>/holidays` 다. `<local>` 은 작업 기계의 볼륨 경로를 가린 표지다(#124 의
  `<local>/holidays-reports` 와 같은 규약).
- `~/holidays-reports` 는 `<local>/holidays-reports` 로 가는 심볼릭 링크다.
- 2026-11-18 에 uv(0.13.9)·chromium headless shell(151.0.7922.34, playwright 1.62.0)·Codex CLI
  (codex-cli 0.170.0)를 세웠다. Holiday_21 문서를 쓴 환경에는 `uv` 가 없었다(holiday_21 §0).
- SSH 접속이 실패해서 git 원격을 HTTPS 로 바꿨다 — 자격 증명 도우미 `gh auth git-credential`. 원격 주소는
  `https://github.com/lunalism/holidays.git` 이다.
- 2026-11-18 의 main 커밋 22 개(`4bc443a` … `0f03630`, #123–#125 의 커밋)는 작성자 주소가 개인 주소였다.
  이 PR 부터 레포 로컬 작성자 주소를 GitHub 의 noreply 주소로 둔다. 이미 main 에 있는 커밋은 고치지 않는다.

### 3-2. `codex exec` 와 stdin

`codex exec` 는 stdin 이 열려 있으면 「Reading additional input from stdin...」 에서 끝없이 기다린다. #125 의
첫 Codex run 은 백그라운드에서 80 분 동안 멈춰 있었고, stdin 을 닫고(`</dev/null`) 다시 돌려 끝났다(§6).

### 3-3. 포털·관보

- **MV 포털** — 법 전체 문서 `jlr-FeiertGMVrahmen` 과 그 문서·toc API 는 500 이다. 조문 단위 id 와 다른 id
  `jlr-NNLMV00007A2F`(#124 P1 의 「Aktuelle Gesamtausgabe」 렌더)는 열린다.
- **MV 관보 사이트** — 두 화면이 2020–2025 의 공개를 다르게 적는다. #124 처럼 판단 없이 둘 다 옮긴다
  (`rules/de_mv/solar_holidays.yaml` 머리 주석, 2026-11-18):
  - `https://land-mv.de/thema/buergerservices-und-digitale-verwaltung` — 「Sämtliche Jahrgänge von 2020 bis
    2025 stehen vollständig online zum Abruf bereit.」
  - `https://land-mv.de/landeregierung/jm/gesetz-verordnungsblaetter` — 2026 년 호(Nr. 1–31)만 싣고 「Sie haben
    Interesse an Gesetz- und Verordnungsblättern, am Amtsblatt oder dem Amtlichen Anzeiger aus den Jahren
    2014-2025? Bitte schreiben Sie eine E-Mail unter Angabe der gewünschten Publikation an: …」.
- **SN 관보** — SächsGVBl. 1992 Nr. 35 는 발행사 판매 사이트에서 찾지 못했다(「Heft 35/1992」 검색 결과 없음,
  보관 상품은 1999 년부터). 2002 Nr. 9 는 그 사이트에서 유료 보관 상품(1999–2018)으로만 찾았다
  (`rules/de_sn/*.yaml` 의 `source_todo`).

### 3-4. publish run 의 지연

Holiday_21 §3-1 뒤로 새 publish run 은 없다. 마지막 run 은 그 문서가 이미 센 44226978367(createdAt
2026-11-18T02:57:31Z)이다. 그래서 이번에는 지연을 재지 않았다.

## 4. 리뷰의 자리

- **#123** — 문서 PR. Codex 없음.
- **#124** — CC 자기 검토 2(커밋 6). Codex(`codex exec -s read-only`) 1 회 — 지적 8: 고침 4(커밋 8·9·10),
  [남김] 4(값 검사·hinweis 단언·UID 교집합·발행 교체 테스트). 사람이 [남김] 을 받아들였다.
- **#125** — CC 자기 검토 1(커밋 6). Codex 1 회(stdin 을 닫은 재실행) — 지적 14: 고침 3(커밋 7·8·9),
  [대체] 3(커밋 10·11 — 사람의 결정), [남김] 7, 기각 1(옮긴 README 의 원래 위치 서술).
- **MV 재시도·SN 준비** — Codex 없음. 조사 보고의 판단 요청을 사람이 닫았다.
- 이력은 이번에도 PR 본문에만 남았다. Codex 원문은 레포 밖 `holidays-reports/` 에 있다.

## 5. 미결과 다음 세션 큐

**이 세션에서 닫힌 것**: MV 피드(#124), SN 피드(#125), README 「독일 피드 열 벌」(#124 `420e95c`).

**이 세션에서 새로 선 것 — 「전 로더 검증」 PR 하나로 묶는다**

- **모르는 필드 거부** — de_mv·de_sn 만 한다. 나머지 독일 로더는 Holiday_21 §0 의 상태 그대로다(Holiday_21 §5,
  #124 M6).
- **값 검사**
  - `easter_offset` 의 bool — `true`(#124 Codex 3), `false`(#125 Codex 판단 1)
  - `easter_offset` 의 실수 — `-2.5`(#125 판단 1)
  - `month: 13`(#124 Codex 3)
  - 오프셋의 범위 없음 — `totensonntag_offset: -400` 이면 그 해의 항목이 빠진다(#125 판단 2)
  - 여러 행의 같은 `key`(#125 판단 3)
  - 빈 `source`·문자열 아닌 `source`, `verified: false` 인데 `source_todo` 없음(#125 판단 4)
- **테스트의 약점**
  - hinweis 상수 단언이 테스트 안에서 만든 공란을 검사한다(#124 Codex 5)
  - UID 교집합 테스트가 빈 피드에서도 통과한다(#124 Codex 6). 단독 검사들의 공허 통과도 같은 종류다
    (#125 판단 10)
  - 발행 교체 테스트가 같은 입력을 두 번 쓴다(#124 Codex 7, #125 판단 7)

**그 밖의 것**

- **MV·SN verified 전건 false.** 승격 경로는 각 `source_todo` 에 적은 대로다 — MV 는 공포본(2002 재공포본,
  2022 Nr. 31), SN 은 1992 Nr. 35 와 2002 Nr. 9.
- **MV 일회성 확인** — 제목만, 포털에 한정(#124 P3).
- **SN 일회성 공백** — 2020 Nr. 1–40·38a·39a, 2021 Nr. 1–14, 2023 Nr. 2 Anlageband 의 목차를 얻지 못했다
  (`rules/de_sn/solar_holidays.yaml` 머리 주석).

**Holiday_21 에서 이월** — 닫힌 것: README 「독일 피드 열 벌」. MV·SN 은 위로 옮겼다. 「모든 독일 로더의
모르는 필드 거부」 는 위 묶음으로 옮겼다.

- **145882 텍스트층 지문.** 바이트 해시는 지문이 될 수 없다(Holiday_21 K1). 텍스트층 지문을 쓰려면 추출기를
  고정해야 한다.
- **가리지 않은 로컬 경로** — 모두 #120(`491352e`)에서 들어왔다.
  - `docs/research/report_hb_bb_prep/fetch.log:19–20`
  - `docs/research/report_batch2_survey.md:712`
  - `docs/research/report_batch2_survey/state_SN.md:4`
- **publish 지연 추이** — 조치 없이 관측만(§3-4).
- **SL·ST·TH 보류** — 공식 현행 조문 없음.
- **`weltkindertag`(TH) key** 승인 대기.
- **주석 정리 묶음.**
  - 기존 파일의 죽은 `/tmp/report_*.md` 참조
  - 모든 주 표의 scope 절 「feiertage-api 2025·2026 16 주 교집합 실측」(결과가 레포에 없음)
  - #120 전부터 낡은 주 수 서술(목록: #120 PR 본문 「이번 차례에 정한 것」 2)
  - `rules/de_bb/solar_holidays.yaml:15` 의 재수령 대조(요청만 기록, 비교 출력 없음)
- **`tests/test_landing.py:6`** 「피드를 하나 늘릴 때 랜딩에서 손대는 곳은 feed-data 블록의 한 줄뿐이다」 — 랜딩 생성(#59 이후) 뒤로 맞지 않는다.
- **BW 2014·2015 공백** — source 가 그 두 해를 「FTG 개정 두 건 § 1 무관」 으로만 적는다(#119).
- **C5b·SUMMARY 필드명 문면** — #119 범위 밖.
- **Codex 플러그인 실패**(Holiday_20 §3-4) — 고칠 때까지 터미널 `codex exec`. #124·#125 도 CLI 로 돌았다.
- **병렬 에이전트는 scratch 디렉터리를 따로** — `docs/research/report_batch2_survey/README.md` 「요청 로그의 한계」.

**Holiday_19 에서 이월**

- 26.04 이행 — Holiday_19 §5 그대로.
- 실물 관보가 필요한 승격(BE 기저 9, HH, NI, RP), HE·BE 포털 — 그대로. HB a–i 9 건도 같은 처지다.
- setup-uv·SEO·README·이슈 #40 등 — Holiday_19 §5 「Holiday_18 에서 이월」 그대로.
- Codex 리뷰 이력이 레포에 남지 않는다.

**다음 세션 큐 — 사람이 정한 순서**

1. **묶음 피드 설계 조사.**
   - 첫 입력: 사람의 Threads 글에 달린 답글(레포 밖에서 모은 것). 세션을 시작할 때 사람에게 지금까지 모은
     것을 받는다.
   - 서버 쪽 조합 생성 선택지는 보류다. 조사는 그래도 그 선택지를 함께 다룬다.
   - Holiday_20 §5·Holiday_21 §5 의 볼 것(중복, 합친 이벤트의 UID 방식, 정적·동적 생성, git 로 감사할 수
     있는지, 기존 구독자)은 그대로다.
2. **전 로더 검증 PR** — 위 묶음.
3. **SL·ST·TH** — 여전히 보류. 공식 현행 조문이 없다.

## 6. 규약

- **신규: `codex exec` 는 stdin 을 닫고 돌린다**(`</dev/null`). 백그라운드에서는 특히 그렇다(§3-2).
- **신규: 문서만 바꾸는 PR 도 열기 전에 PR 본문 초안을 사람에게 보인다**(AGENTS.md). CI 녹색 뒤의 자체
  머지는 그다음이다(#123 에서 빠뜨림, §0).
- **신규: 날짜 규칙을 법이 정의하지 않으면 `source` 는 법이 날의 이름만 든다고 적고, 관행을 주는 공식의
  비법령 문장을 인용한다**(SN — 주의회 청원 보고서). 다른 주 법의 교차 확인은 머리 주석에만 둔다.
- **신규: 새 규칙의 기준일은 법이 스스로 정의하는 날을 고른다**(SN — 대림절이 아니라 Totensonntag).
- **신규: 「한 번의 재시도」 결정은 외부 출처로 가는 요청을 한정한다. 로컬 환경 준비는 시도에 들지
  않는다**(MV 재시도).
- **신규: 이 레포의 커밋에는 `Co-Authored-By: Claude …` 트레일러와 「Generated with」 줄을 달지 않고, PR 본문에는
  「Generated with」 줄을 달지 않는다**(사람의 결정, `CLAUDE.md` 「브랜치·PR」). 이미 main 에 있는 커밋은
  고치지 않는다(트레일러가 달린 main 커밋 137 개). 남아 있던 PR 본문·댓글의 「Generated with」 줄은 이 PR 과
  함께 지웠다(목록은 이 PR 본문).
- 유지: Holiday_21 §6 전부.
