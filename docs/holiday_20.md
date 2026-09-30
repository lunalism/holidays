# Holiday_20 시작 문서

작성: 2026-09-30
기준 리비전: dc92151 (main, #120 머지 커밋)
이전 세션: Holiday_19 문서(#112–#115, 문서 자체는 #116). 이 문서는 그 이후(#117–#120)를
담는다. 이 문서 자체가 그다음 PR 이다.

코드와 상설 문서에 있는 것은 옮겨 적지 않는다 — 가리킨다. 이 구간의 조사 보고는 전부
`docs/research/` 로 옮겨졌다:

- `docs/research/report_noscript_duplication.md` 와 폴더 — 랜딩 이중 적재 측정(#118)
- `docs/research/report_source_selfcontain.md` 와 폴더 — 독일 source 자기완결성·HH 서지(#119)
- `docs/research/report_batch2_survey.md` 와 폴더 — 2차 배치 7 주 얕은 조사(#120)
- `docs/research/report_hb_bb_prep.md` 와 폴더 — HB·BB 구현 준비(#120)
- `docs/research/report_de_bb_impl/` — de_bb 일회성 지정 검색 기록(#120, 보고서 없이 폴더만)

---

## 0. 이 세션에서 한 일

PR 넷(#117–#120), 커밋 18(1·2·6·9). 셋이 문서·정리이고 하나가 새 주 피드다.

- **#117 — 옮긴 보고의 정정 흐름 (커밋 1).** `docs/research/README.md` 「이차 기록이다」의
  마지막 문장을 바꿨다.
  - 정정은 옮긴 보고가 아니라 같은 이름 폴더의 README 에 절로 둔다.
  - 예외는 공개 레포에 둘 수 없는 값의 가림뿐이다(#114).
  - 첫 사례로 #115 의 `be_2019/README.md` 를 든다. AGENTS.md 에는 이 문장이 없어 동기화가 필요 없었다.
  - PR 본문은 머지 뒤 한 번 고쳤다. 근거로 적은 「Holiday_19 판단 요청 4」 는 레포에 없는 이름이었고, 요청은 #116 본문의 「판단 요청」에 있다(§1-2).
- **#118 — noscript/JSON 이중 적재의 값 (커밋 2).** 사람이 둘 다 두는 쪽(선택지 1)을 골랐다.
  - `DESIGN.md` 「JS 없는 쪽은 사람이 아니라 기계다」 절에 측정값을 적었다: JSON 블록의 서빙(gzip) 몫은 면당 약 0.5 KB(15 피드, 3.3–3.6%), 주 피드 7 개 투영에서 약 0.6 KB(4.1–4.4%).
  - 재측정 조건도 같은 절에 있다.
  - 보고를 옮기면서 스크립트 둘에 파일 머리 `# ruff: noqa` 만 더했다(§1-1, §6).
- **#119 — 독일 source 자기완결성 26 항목 + HH 31. Oktober 서지 (커밋 6).**
  - 공통 안전망 `tests/test_de_source_selfcontained.py` 를 첫 커밋에 두고, 반대 방향 단언 셋을 뒤집었다(`test_de_feed.py` 통일의 날, `test_de_bw_feed.py` 미러·1월 6일).
  - 데이터는 8 피드 324 이벤트의 DESCRIPTION 만 바뀌었다.
  - HH 31. Oktober 는 luewu 호 PDF 의 URL·sha256·재수령 대조를 든다. 2026-09-07 첫 열람본이 같은 파일임은 `3af0ead` 커밋 메시지(크기·sha256)로 확인해 적었다(§1-2).
  - Codex 지적으로 `rules/de_hh/__init__.py` 의 낡은 「공포 관보 미열람 … 10 건 전부 false」 를 고쳤다.
  - **사람이 머지했다.**
- **#120 — 브란덴부르크 주 피드 de_bb (커밋 9).**
  - 12 건, 전건 `verified: false` 다(1991·1994 공포본 온라인 없음).
  - 신규 key `ostersonntag`·`pfingstsonntag` 는 사람이 승인했다.
  - `tests/test_de_be_feed.py` 의 `STATE_FEEDS` 를 `rules/` 스캔으로 바꿨다(#90 의 test_de_scope 와 같은 조건). 두 스캔 일치 테스트가 있다.
  - § 2 Abs. 3 일회성 지정은 BRAVORS 공개 검색(현행 + außer Kraft 문서의 Archiv)으로 찾았고 「찾지 못함(범위)」 으로 적었다 — `rules/de_bb/solar_holidays.yaml` 머리 주석, `docs/research/report_de_bb_impl/`.
  - 이 PR 이 낡게 만든 주 수 서술을 수 없이 고쳤다.
  - 새 파일의 죽은 `/tmp` 참조는 `tests/test_de_scope.py` 로 돌렸다.
  - 체크리스트는 `docs/operations.md` 항목 12 에 반영했다.
  - **사람이 머지했다.**

머지는 #117·#118 을 CC 가, #119·#120 을 사람이 했다(규칙 데이터·발행본 변경).

테스트 1535 → **1753** 통과(#117·#118 +0, #119 +110, #120 +108). xfail 4·xpass 29 는
그대로다. 신설 테스트 파일은 `tests/test_de_source_selfcontained.py`·`tests/test_de_bb_feed.py`
둘이다.

닫힌 결정 — 각 한 줄, 근거는 문서·주석의 절:

- 이중 적재는 **둘 다 둔다**. 면당 1 KB 를 넘으면 다시 본다 — `DESIGN.md` 같은 절.
- source 는 **레포 경로·머리 주석·다른 피드·key/token 부기·판정어 없이** 쓴다 — 공통 안전망이 전 독일 표를 스캔한다.
- 해시 정의는 source 가 **머리 주석의 용어 그대로** 든다(복호화는 PDF 에) — `rules/de/solar_holidays.yaml` 머리 주석.
- 1월 6일 key 재사용 근거는 **머리 주석**에 둔다 — `test_de_bw_feed.py` 의 해당 테스트.
- de_bb 는 **12 건 false 로 첫 발행**한다 — `rules/de_bb/__init__.py`.

## 1. 판단이 갈린 지점

### 1-1. 선행 실측이 멈춘 자리

- **#118 린트 대 "그대로 옮긴다".** 옮긴 스크립트 둘이 ruff 에 걸렸다(CI·발행 run 이 `ruff check .` 로 `docs/research/` 를 덮는다). 멈췄고, 사람이 #113·#114 전례(파일 머리 `# ruff: noqa`)를 골랐다.
- **#119 해시 정의의 용어.** CC 보고의 짧은 정의가 머리 주석과 용어가 달랐다(「이미지 객체」·「빈 비밀번호」, 복호화를 이미지에 붙임). 멈췄고, 사람이 머리 주석 용어로 문면을 고정했다.
- **#119 셋째 반대 단언.** 데이터 편집 뒤 `test_de_bw_feed.py` 의 1월 6일 테스트(`"heilige_drei_koenige" in source`)가 드러났다. 멈췄고, 사람이 의도(key 재사용 근거의 기록)를 머리 주석 단언으로 옮기게 했다.
- **#119 빨강 수 29.** 지시는 30 이었다. 옮긴 단언이 머리 주석을 보므로 테스트 커밋에서도 녹색이라 29 다. 멈췄고, 사람이 29 를 받아들였다.
- **#119 「같은 파일인지 확인할 수 없다」.** HH 머리 주석에 이 문장을 넣은 뒤 `git show 3af0ead` 가 09-07 열람본의 크기·sha256 을 적고 있음을 찾았다. 거짓 문장이라 따로 커밋으로 고쳤다(`bc08781`).
- **#120 연도별 관보 목록에 제목이 없다.** BRAVORS 연도 목록은 호 번호만 적어 제목 검색이 성립하지 않았다. 멈췄고, 사람이 공개 검색(선택지 d)을 골랐다. 조건은 만료 문서 포함 여부를 먼저 확인하는 것이었고, Archiv 도움말로 확인했다.
- **#120 Codex 플러그인.** 세 번 모두 시작 단계에서 실패했다(§4). 표시하지 않고 멈췄다.

### 1-2. 프롬프트·보고의 전제가 틀렸고 실측이 잡은 자리

- **「Holiday_19 판단 요청 4」** — #117 PR 본문에 쓴 이름. `docs/holiday_19.md` 에 번호 붙은 판단 요청이 없다. 요청은 #116 본문의 「판단 요청」에 있었고, 본문을 고쳤다.
- **source 자기완결성 보고의 테스트 탐색.** C5(판정어)를 **요구하는** 테스트만 찾았다. C1–C4 문면을 요구하는 단언(`test_de_bw_feed.py` 1월 6일)을 놓쳤다. 뒤에 「테스트가 source 에 요구하는 리터럴이 편집으로 줄었는가」 로 다시 찾아 셋으로 확정했다.
- **「그때 URL·해시를 적지 않았다」** — 같은 보고의 D-3. YAML 만 보고 git 이력을 보지 않았다. 근거의 정본은 YAML 이지만 감사 기록은 커밋 메시지에도 있다(§6).
- **#120 CC 자기 검토의 과장 넷** — 모두 CC 가 쓴 머리 주석·PR 본문:
  - 「적중 제목 전부를 봤다」 — 실제는 610 중 175
  - 검색어 '§ 2 Abs. 3 FTG' 의 0 건 — 실행 증거 없음
  - 1994 Nr. 12 「무관」 — 읽지 않음
  - 「두 일요일은 16 주 중 BB 뿐」 — 근거 없음
  - 넷 다 문구로 고치거나 뺐다(`3e59032`·`17aef11`).
- **feiertage-api 는 BE 2020 의 8. Mai 를 싣지 않는다.** BE 2025 의 8. Mai 는 hinweis 를 달아 싣는다(`docs/research/report_de_bb_impl/fapi_crosscheck.txt`). 일회성 대조원으로는 보조다.

### 1-3. 리뷰

- **#119 Codex(플러그인, 1 회)** 지적 둘:
  - HH `__init__` 의 낡은 서술 — CC [뺌](후속)에서 사람이 [대체](이 PR 안에서)로 바꿨고, `346bccd` 로 고쳤다.
  - 새 안전망이 빈 source 를 통과시킴 — [남김]. 독일 로더 10 개의 `_checked()` 가 빈 source 를 이미 막는다.
- **#120 CC 자기 검토** — Codex 가 아니다. PR 본문에 「CC 자기 검토」 로 따로 적었다(§1-2 의 넷 + 어간 검색 사실).
- **#120 Codex(터미널 CLI, 1 회, `3e59032` 대상)** 지적 하나: python-holidays 대조 서술에 기록이 없음 — [대체]. 결과 파일을 두지 않고 고정 버전과 테스트를 가리키게 했다(`b82ba99`).

## 2. 검토했다가 버린 갈래

- **noscript 선택지 2·3a–3d**(JSON 블록 제거, 정적 목록 + 덧칠, JSON 슬림화, data 속성, 별도 파일) — #118 에서 선택지 1. 값과 재측정 조건만 적었다.
- **옮긴 스크립트의 린트 수정·`pyproject` 제외** — 조사 때 돌린 그대로 둔다(§6).
- **안전망을 허용 목록으로 먼저 머지** — #119 에서 같은 PR 의 테스트 커밋을 먼저 두는 쪽을 골랐다.
- **BW 2014·2015 GBl. 전 호 새 검색** — #119 에서 기록된 범위만 적는 쪽(§5 에 공백으로).
- **HH source 에 「찾지 못함」 절** — #119 결정 5 로 넣지 않았다.
- **C5b(「… 뒤에도 그대로」 23 행)·SUMMARY 필드명(24 행) 정리** — #119 범위 밖(§5).
- **BB GVBl. Teil II 약 900 호 본문 읽기** — #120 에서 공개 검색(d)을 먼저 했고, (a)는 자동으로 잇지 않았다.

## 3. 레포 밖에서 확인된 것

### 3-1. publish cron — 하나 더, 지연이 범위를 벗어났다

run 36650896470(schedule): 예정 2026-09-29(화) 21:23Z, createdAt 2026-09-30T00:33:17Z(`gh run view`), 지연 약 190 분, success.
- 발행 커밋 `e33c6ee` 는 `status.json`·`logs/build.jsonl` 만 바꿨다.
- Holiday_19 §3-1 의 관측 범위(110–152 분) 밖이다. 누락은 여전히 0 이다.

### 3-2. GitHub Pages 의 압축

- Pages 는 gzip 으로 서빙한다. `br` 만 요청하면 비압축으로 준다.
- 서빙 바이트 수가 세 면 모두 zlib 레벨 5 출력과 정확히 같다(`docs/research/report_noscript_duplication.md` A 절).

### 3-3. 2차 배치 포털·관보 접근

주별 사실은 `docs/research/report_batch2_survey.md`(요약 표)와 주별 `state_XX.md` 에 있다.
- 요약: SL·ST·TH 는 공식 통합본이 JS 셸이다.
- HB 현행판(Transparenzportal 296390)은 500 「db-connection failed」 가 되풀이됐다.
- BB·HB 관보는 정적 PDF 로 열린다.
- 준비 보고(`report_hb_bb_prep.md`) HB-1 은 2025 판들이 관할 공고(Brem.GBl. 2025 Nr. 98, § 11)에 따른 것임을 적는다.

### 3-4. Codex — 플러그인 경로 실패, CLI 는 된다

- 플러그인(`codex-companion.mjs task`)은 #120 에서 세 번 모두 같은 출력으로 끝났다: `[codex] Starting Codex task thread.` / `failed to load configuration: No such file or directory (os error 2)`.
- `~/.codex/config.toml` 은 있고, 같은 세션의 #119 리뷰는 플러그인으로 돌았다.
- 레포 안 터미널의 `codex exec` 는 동작했다. [추론] 플러그인의 호출 경로 문제다.

## 4. 리뷰의 자리

- **#119** Codex(플러그인) 1 회 — 분류와 처리는 §1-3, 표는 PR 본문.
- **#120** Codex(터미널 CLI) 1 회와 CC 자기 검토 — 둘을 PR 본문의 다른 절에 적었다.
- **#117·#118** Codex 없음(문서·측정값 기록).
- 이력은 이번에도 PR 본문에만 남았다(§5).

## 5. 미결

**이 세션에서 새로 선 것**

- **HB 피드.** 준비 보고의 초안(`docs/research/report_hb_bb_prep/drafts/`)이 있다.
  - reformationstag 는 Brem.GBl. 2018 Nr. 63 으로 true 후보다.
  - 현행 § 2 Abs. 1 은 공식 포털의 2020-03-14 판과 관보 **제목** 검색에 기댄다.
  - 사람의 결정(이 문서 작성 지시): 구현 전에 2020–2025 연간본 **전문** 검색을 조건으로 한다.
- **MV 피드.** Frauentag 가 2023 부터라 연도 경계(유효 시작) 설계가 필요하다 — 새 규칙 유형(`report_batch2_survey.md` 판단 요청 2).
- **SN 피드.** Buß- und Bettag 는 요일 계산이 필요하다 — 새 규칙 유형. 조문은 이름만 든다(날짜 정의 없음).
  - 사람의 방향(이 문서 작성 지시): source 는 조문의 이름과 날짜 관행을 적는다(부활절 오프셋과 같은 꼴).
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
- **Codex 플러그인 실패**(§3-4) — 고칠 때까지 터미널 `codex exec`.
- **병렬 에이전트는 scratch 디렉터리를 따로** — `docs/research/report_batch2_survey/README.md` 「요청 로그의 한계」.

**Holiday_19 에서 이월** — 닫힌 것: noscript 중복(#118), source 자기완결성·HH 서지(#119), 2차 배치 조사(#120 에 포함, BB 구현).

- 2026-10-19 뒤 첫 발행 run 의 「Runner Image」 확인, 26.04 이행 — Holiday_19 §5 그대로.
- 실물 관보가 필요한 승격(BE 기저 9, HH, NI, RP), HE·BE 포털 — 그대로.
- setup-uv·SEO·README·이슈 #40 등 — Holiday_19 §5 「Holiday_18 에서 이월」 그대로.
- Codex 리뷰 이력이 레포에 남지 않는다.

**다음 세션 큐 — 사람이 정한 순서**

1. **HB** — 위 조건(전문 검색) 먼저.
2. **MV** — 연도 경계 설계.
3. **SN** — 요일 규칙.
4. **묶음 피드 설계 조사** — 코드 없음. 볼 것: 중복, 합친 이벤트의 UID 방식, 정적·동적 생성, git 로 감사할 수 있는지, 기존 구독자.

## 6. 규약

- **신규: 옮긴 보고의 정정은 폴더 README 에(#117).** `docs/research/README.md` 「이차 기록이다」. 보고 본문은 고치지 않는다. 예외는 공개할 수 없는 값의 가림(#114).
- **신규: 옮긴 스크립트가 린트에 걸리면 파일 머리 `# ruff: noqa` 한 줄만(#118·#119·#120).** 조사 때 돌린 그대로가 기록이다. 폴더 README 에 그 사실을 적는다(`report_noscript_duplication/README.md` 등).
- **신규: 새 파일에 죽은 `/tmp` 참조를 두지 않는다(#120).** 사실이 지금 레포에 있는 자리를 가리킨다(`647bb41`).
- **신규: 안전망 커밋을 먼저, 빨강 수를 기록한다(#119·#120).** AGENTS.md 「안전망은 … 먼저」의 PR 안 형태다. 빨강 수와 그 구성은 PR 본문에 적는다.
- **신규: 「기록이 없다」 고 쓰기 전에 git 이력과 테스트를 찾는다(#119·#120).** `3af0ead` 커밋 메시지(HH 열람본 해시), 고정 의존과 테스트(python-holidays 대조)가 그 예다.
- **신규: CC 자기 검토는 Codex 라고 적지 않는다(#120).** PR 본문에 따로 둔다.
- **신규: 승인된 key — `ostersonntag`·`pfingstsonntag`(#120).** `rules/de_bb/easter_holidays.yaml` 머리 주석.
- **확인: 주 추가는 `docs/operations.md` 「피드 추가」 표를 따른다.** 교집합 검사도 이제 `rules/` 스캔이다(항목 12).
- 유지: Holiday_19 §6 전부.
