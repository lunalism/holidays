# MV(메클렌부르크포어포메른) 피드 — 출처 확보와 유효 시작일 설계 (조사만)

- 측정 시점: 2026-10-07(UTC, 요청 01:14:40Z–01:15:51Z).
- 범위: 조사만 했다. 레포 변경·브랜치·커밋·PR 없음. Codex 호출 없음. 병렬화하지 않았다(scratch 하나).
- 재현 기록: `~/holidays-reports/report_mv_prep/`(README 참조). 렌더 HTML 은 scratch 에 남겨 두었다.
- 표기: 명령 출력·원문에서 바로 읽은 것은 태그 없이 적는다. 거기서 유도한 문장에는 **[추론]** 을 붙인다.
- **결과 요약: Part A 는 A1 에서 멈췄다.**
  - 공식 포털 렌더가 문서 대신 「Das Laden des Dokumentes jlr-FeiertGMVrahmen ist fehlgeschlagen.」 을 냈다. 포털의 문서 API 가 500 이다.
  - 지시(「If the text cannot be obtained, record what was returned and stop Part A」)대로 A2–A4 는 하지 않았다.
- Part B 는 수행했다.

---

## 기준 SHA

- `origin/main` = `887a2984d00bf2280857eeb14f879fd381b80cc7`(Merge pull request #122). 기대값 887a298 과 같다.
- 로컬 `main` 도 같은 커밋이다. 레포 파일은 고치지 않았다.

---

## Part A — 출처

### A0 — 사전 확인 (성립)

| 확인 | 관측 |
|---|---|
| 평문 HTTP 요청이 JS 셸인가 | 2026-10-07T01:14:40Z, 200, `text/html`, 5,559 B(조사 때와 같은 바이트 수). 「Feiertag」 0 회, 「Aktivieren Sie bitte JavaScript, um den Bürgerservice zu nutzen.」 — **여전히 JS 셸** |
| playwright·chromium | `pyproject.toml` 에 `playwright==1.62.0` 고정. `uv run playwright install --only-shell chromium` 은 출력 없이 끝났다(이미 설치: `chromium_headless_shell-1234`). 실행해 본 브라우저 버전 **151.0.7922.34** |

### A1 — 헤드리스 렌더 (**본문 못 얻음 → Part A 중단**)

- 렌더 두 번: 01:15:05Z, 01:15:51Z(앞 렌더가 끝나고 10 초 뒤). 문서 URL 응답은 둘 다 200 이다.
  - 문서 URL 한 줄씩을 `fetch.log` 에 적었다(렌더 HTML 13,797 B·13,794 B).
- 화면 본문(innerText, 393 자)은 머리·검색 틀과 「Das Laden des Dokumentes jlr-FeiertGMVrahmen ist fehlgeschlagen.」 뿐이다. 「Frauentag」 0 회.
- 브라우저가 받은 응답 44 건씩 중 실패는 두 렌더 모두 같다(`render/r1.net.tsv`·`r2.net.tsv`):
  - `https://www.landesrecht-mv.de/jportal/wsrest/recherche3/document` → **500** `application/json`
  - `https://www.landesrecht-mv.de/jportal/wsrest/recherche3/toc` → **500** `application/json`
  - 나머지(`init`·`search`·`documentZone`·`cmsContent` 등)는 200.
- 해시(`render_hashes.txt`):
  - innerText: 두 렌더 같음 — `9d2b2f37d746c32aa012c9b132778f7e5ed0fefee739ff476b7d9954f49851b2`.
  - HTML: 다르다(`f47970e3…` / `6caed9d9…`). 차이는 편집기 placeholder id 와 「Zur Suche」 단축 링크(`/bsmv/sYqE6` ↔ `/bsmv/PSuEc`)다.
  - [추론] 본문을 얻더라도 렌더 HTML 은 바이트 안정이 아니다. 비교 기준은 추출한 조문 텍스트여야 한다(HB 145882 의 교훈과 같다).
- Stand/Fassung 날짜, § 2 Abs. 1 Nr. 1–11 자구: **얻지 못함.**
- 비공식 출처로 대신하지 않았다. 포털의 검색 화면·다른 문서 id 로 우회하지도 않았다(범위를 넓히는 일이라 판단 요청 1).

### A2 · A3 · A4 — **하지 않음**

지시에 따라 A1 실패에서 Part A 를 멈췄다. 하지 않은 것과 그 상태:
- **A2** — GVOBl. M-V 2022 Nr. 31 S. 427 재수령·해시 대조·시행 조항 인용.
  - 조사(2026-09-30)는 바이트 수(263,235 B, `state_MV_fetch.log`·`spotcheck.log` 두 번)만 기록했고 sha256 은 없다.
  - 시행 조항 인용 「Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.」 과 공포일(ausgegeben 12. Juli 2022)은 그 조사의 관찰이다. 이번에 다시 확인하지 않았다.
- **A3** — 포털 자구와 조사의 비공식 명칭 대조. A1 자구가 없어 대조할 것이 없다.
- **A4** — 2020 이후 일회성 지정(GVOBl. M-V 목록 제목 검색, de_bb 전례 방식). 하지 않았다.
  - 조사가 기록한 관보 포털(regierung-mv.de, 2014–2026 PDF 목록, 정적 HTML)은 그때 닿았다. 이번에는 요청하지 않았다.

---

## Part B — 유효 시작일 설계

### B1 — 레포가 이미 쓰는 「날짜·연도부터(까지)」 장치

| # | 장치 | 자리 | 단위·경계 |
|---|---|---|---|
| 1 | 항목별 `effective_from`·`effective_until` | `rules/kr/solar_holidays.yaml`(예: `labor_day` `effective_from: 2026-05-01`, `constitution_day` `effective_from: 2026-05-11`), 판정은 `rules/kr/holiday_calendar.py:_active()` | **날짜**, 시작·끝 모두 **포함** |
| 2 | ruleset 의 `effective_from`(대체공휴일 개정) | `rules/kr/substitute_holidays.yaml`·`rules/kr/substitute_rules.py` | **날짜**, 포함. 연도는 로더가 거부 |
| 3 | 제2조 배열 구간 `arrangements[].effective_from`/`effective_until` | `rules/kr/substitute_rules.py` | 날짜, 양끝 포함 |
| 4 | 표 단위 `coverage.from`·`confirmed_through`·`last_synced_at` | `rules/kr/solar_holidays.yaml`·`designated_holidays.yaml` | 날짜. 항목이 아니라 표의 완결성 경계 — `from` 이전은 조회 거부, 이후는 provisional/may_grow |
| 5 | 일회성 `designated` 표(날짜 하나) | `rules/kr/designated_holidays.yaml`, `rules/de_be/designated_holidays.yaml` | 항목마다 `date` 하나. de_be 는 key 에 연도 접미사 `_YYYY` 를 강제 |
| 6 | jp — 규칙 필드 없음 | `rules/jp/feed.py`·`sources/jp/build_data.py`·`data/jp/<연도>.yaml` | 内閣府 CSV 의 날짜별 자료를 그대로 옮긴다. 법 개정은 자료 자체에 반영되고 규칙 표에 경계 필드가 없다 |

코드 인용:

`rules/kr/holiday_calendar.py`
```python
def _active(entry: dict, day: date) -> bool:
    start = entry.get("effective_from")
    end = entry.get("effective_until")
    if start and day < start:
        return False
    if end and day > end:
        return False
    return True
```
- `rules/kr/solar_holidays.yaml` 머리 주석: 「effective_from / effective_until 은 공휴일 지위의 시작·끝이다. 비어 있으면 "이 표가 다루는 기간 내내 공휴일"이라는 뜻」.

`rules/kr/substitute_rules.py`
```python
    def ruleset_on(self, day: date):
        """그 날짜에 유효했던 ruleset. 제도 도입 전이면 None."""
        active = None
        for rs in self.rulesets:
            if rs.effective_from <= day:
                active = rs
...
    if not isinstance(effective_from, date):
        raise RuleTableError(
            f"{raw['id']}: effective_from 이 날짜가 아니다({effective_from!r}). "
            "연 단위로 두면 2021-08-04 같은 연중 개정을 표현할 수 없다."
        )
```

**연도를 날짜 대신 쓰지 않는다는 결정이 테스트로 고정돼 있다:**
- `tests/test_substitute_rules.py::test_effective_from_is_a_date_not_a_year`(「연 단위로는 2021-08-04 같은 연중 개정을 표현할 수 없다」)
- `test_rules_are_not_applied_retroactively`(2021-08-03 과 08-04 의 답이 갈린다)
- `tests/test_rule_table_mutations.py` 의 변이 `effective_from을-연도로` 가 기대하는 결과는 「로드 거부」.

`rules/de_be/feed.py`(일회성):
```python
    out += [_event(e["date"], e) for e in _designated() if e["date"].year == year]
```

### B2 — 독일 주 로더의 필드 집합과 모르는 필드

- **닫힌 필드 집합은 없다.** 각 주 `feed.py`(주마다 복제본)의 `_checked()` 는 필수 필드가 비었는지만 본다:
  ```python
  for field in ("key", "name", "source", "scope", *fields):
      if entry.get(field) in (None, ""):
          raise ics.IcsError(f"{where}: {field} 가 비었다.")
  ```
  scope 닫힌 집합·key 정규식·verified bool 은 검사한다. 그 밖의 키는 보지 않는다(`rules/de_bb/feed.py:108` 외 열 주 같은 꼴).
- 테스트에도 닫힌 필드 집합 단언은 없다(`tests/` 에서 필드 집합 비교 검색 0 건).
- 실험(`unknown_field.py`, 레포 무변경 — de_bb 표 복사본에 `valid_from: 2023-01-01` 인 Frauentag 를 더함):
  - 로드: 통과. 항목 키에 `valid_from` 이 그대로 남는다.
  - 발행 이벤트: **2020-03-08, 2022-03-08, 2023-03-08 모두 생긴다** — 필드가 조용히 무시된다.
- [추론] 경계 필드를 들이면서 로더가 그 필드를 모르면, 오류 없이 2020–2022 에 없는 공휴일이 나간다. 새 필드는 로더 변경과 함께여야 하고, 모르는 필드 거부가 그 사고를 막는다(판단 요청 3).

### B3 — 설계안

공통 사실:
- MV 는 새 피드라 이미 나간 UID·SEQUENCE 가 없다. UID 는 `{날짜}-de_mv-frauentag@…` 꼴이 될 것이다. 경계 이전 해에는 그 이벤트 자체가 생기지 않는다. 처음 발행본의 SEQUENCE 는 0.
- **de.ics 교집합 검사**(`tests/test_de_be_feed.py` 의 주 피드 교집합 == de.ics, `rules/` 스캔): Frauentag 는 `land` 라 교집합에 들지 않는다. 경계가 있든 없든 MV 의 전국 9 건만 교집합에 기여한다. 영향 없음.
- `tests/test_de_scope.py` 의 bundesweit key == rules/de key 검사: 영향 없음(land).
- **이미 발행된 피드**: 독일 주 로더는 공유 모듈이 아니라 주마다 `feed.py` 복제본이다. 변경을 `rules/de_mv/feed.py` 에만 두면 다른 피드의 코드 경로가 바뀌지 않는다.
  - 고정하는 테스트는 이미 있다: `tests/test_published_feed.py::test_the_published_feed_is_reproducible_from_the_committed_inputs`. `rules/` 스캔으로 전 피드를 돌고, 발행본의 DTSTAMP·today 로 다시 만들어 **바이트 비교**한다(CI 의 `published_artifact`).
  - 다른 주에도 같은 필드를 들이는 경우: 그 주들의 YAML 에 필드가 없으면 이 테스트가 바이트 동일을 보장한다.
- **status.json**: `feeds.de_mv.events` 는 발행 범위 2020–2031(오늘 2026) 기준. 경계를 바르게 표현하면 3 × 10 + 9 × 11 = **129**(시뮬레이션 실측 `simulate_effective_from.out`). 경계가 없으면 132.
- **DESCRIPTION**: 필드 자체는 피드에 나가지 않는다(verified·source_todo 와 같은 처리). 경계는 `source` 의 문장으로만 나간다.

| | (i) 새 날짜 필드(예: `valid_from`) | (ii) 연도 필드(예: `from_year`) | (iii) kr 의 `effective_from` 을 같은 뜻으로 |
|---|---|---|---|
| 로더 변경 | `_checked` 에 「있으면 `date` 형」 검사, `_year()` 에서 `day >= valid_from` 인 항목만 | 「있으면 int」 검사, `year >= from_year` | (i) 과 같은 코드. 판정을 kr `_active()` 와 같은 뜻으로(포함 경계, date 아니면 거부) |
| Frauentag YAML | `valid_from: 2022-07-13` | `from_year: 2023` | `effective_from: 2022-07-13` |
| 경계값이 담는 것 | 시행일 그 자체(관보의 「am Tag nach der Verkündung」 → 2022-07-13). 첫 해 2023 은 계산 결과 | 첫 해 2023 — 2022-03-08 이 시행 전이라는 **추론**을 표에 굳힌다 | (i) 과 같다 |
| source 의 경계 서술(자기완결) | 「… GVOBl. M-V 2022 Nr. 31 S. 427 … 'Dieses Gesetz tritt am Tag nach der Verkündung in Kraft' — 2022-07-13 부터 공휴일이라 2022-03-08 은 공휴일이 아니었다」 | 같은 문장 + 「그래서 2023 부터」 | (i) 과 같다 |
| 레포의 기존 결정과 | 새 이름 — kr 과 같은 뜻을 다른 이름으로 둔다 | `test_effective_from_is_a_date_not_a_year` 의 결정(연 단위는 연중 개정을 표현 못 한다)과 반대 | kr 과 이름·단위·경계가 같다 |
| 끝 필드 여지 | `valid_until` 로 짝이 맞는다 | `to_year` 등 — 연 단위 한계가 그대로 | kr 에 이미 `effective_until` 이 있어 이름이 정해져 있다 |
| status·DESCRIPTION·UID·교집합·기존 피드 | 위 공통 사실 그대로(129 건) | 같다(129 건) | 같다(129 건) |

- 일회성 표(designated)를 해마다 나열하는 안은 조사(state_MV D)가 이미 부적합으로 적었다. 끝없는 반복을 일회성 표로 다루게 되고, key 가 연도마다 갈려 UID token 이 해마다 바뀐다. B1-5 의 de_be 규약이 `_YYYY` 접미사를 강제한다. 표에 넣지 않았다.

### B4 — python-holidays(고정 0.102) DE(subdiv='MV')

- `pyholidays_mv.out`: 2020·2021·2022 는 10 건(3월 8일 없음), **2023–2031 은 11 건이고 2023-03-08 부터 「Frauentag」**.
- 라이브러리 코드(`holidays/countries/germany.py`):
  ```python
      def _populate_subdiv_mv_public_holidays(self):
          if self._year >= 2023:
              # Women's Day.
              self._add_womens_day(tr("Frauentag"))
  ```
  연 단위 조건이다. 같은 파일의 BE 는 `if self._year >= 2019:`.
- de_bb 식 대조 테스트(`test_the_dates_agree_with_python_holidays_bb` — 연도별 날짜 집합 == `holidays.DE(subdiv=…)`, 2020–2031) 는 MV 에 그대로 쓸 수 있다.
  - 시뮬레이션(설계안 iii + 초안 표)은 2020–2031 열두 해 모두 python-holidays 와 날짜 집합이 같았다.
  - 그래서 그 테스트가 2022/2023 경계를 해마다 잡는다 — 경계를 빠뜨리면 2020–2022 세 해가 실패한다.
  - [추론] 라이브러리가 연 단위라 경계를 날짜로 두든 연도로 두든 이 대조는 같은 답이다. 이 대조로는 (i)·(iii) 과 (ii) 를 가를 수 없다.

---

## 권고안 — (iii) kr 의 `effective_from` 을 같은 이름·같은 뜻으로

1. **레포가 이미 이 결정을 했다.** 공휴일 지위의 시작을 날짜로 두고(포함 경계), 연도를 거부하는 것이 테스트·변이 테스트로 고정돼 있다(B1). 같은 개념에 새 이름(i)이나 반대 단위(ii)를 두면 두 나라 표가 같은 일을 다르게 적는다.
2. **경계값이 추론이 아니라 관보의 사실이 된다.** 날짜는 시행일 그 자체다. 「2023 부터」 는 계산 결과로 나온다. 연도를 쓰면 「3월 8일이 7월 13일보다 앞」 이라는 추론을 표에 박는다.
3. **끝 필드의 이름이 이미 있다**(`effective_until`, kr). 이번에 설계하지 않지만 이름 충돌이 없다.
4. **기존 피드에 닿지 않는다.** 독일 로더는 주마다 복제본이라 `rules/de_mv/feed.py` 만 바뀐다. 바이트 동일은 기존 재현성 테스트가 지킨다.
5. 안전망에 넣을 것(구현 PR):
   - `effective_from` 이 date 가 아니면 로드 거부(kr `_ruleset` 과 같은 메시지 꼴).
   - 2022-03-08 이 없고 2023-03-08 이 있음.
   - status 129 건.
   - python-holidays MV 2020–2031 대조.
   - 모르는 필드 거부 — 판단 요청 3.

## MV 초안 (적용하지 않음)

`report_mv_prep/drafts/de_mv_solar_holidays.yaml`(7 건)·`de_mv_easter_holidays.yaml`(4 건).
- 구조만 보이는 초안이다.
  - Frauentag 만 근거 문장이 있다(조사 2026-09-30 의 관보 관찰. 이번 A2 재확인 없음).
  - 나머지 10 건의 name·source 는 「[미확보]」 다 — § 2 Abs. 1 자구를 얻지 못했다.
- Frauentag 항목(초안):
  ```yaml
  - key: frauentag
    name: Frauentag
    scope: land
    month: 3
    day: 8
    effective_from: 2022-07-13
    verified: false
    source: >-
      Feiertagsgesetz Mecklenburg-Vorpommern (FTG M-V) § 2 Abs. 1 Nr. 2 'der Frauentag (8. März)'
      — Viertes Gesetz zur Änderung des Feiertagsgesetzes Mecklenburg-Vorpommern vom 7. Juli
      2022, Nr. 1 a) 'Nach Nummer 1 wird folgende Nummer 2 eingefügt', GVOBl. M-V 2022 Nr. 31
      S. 427 (ausgegeben 12.07.2022). 시행 조항 'Dieses Gesetz tritt am Tag nach der Verkündung
      in Kraft' — 2022-07-13 부터 공휴일이라 2022-03-08 은 공휴일이 아니었고 첫 날은 2023-03-08
  ```
- [추론] 「2022-07-13」 은 공포(ausgegeben)일 12.07.2022 다음 날로 읽은 것이다. A2 에서 관보 원문으로 확인해야 한다.
- key 는 전부 기존 확립값이다(`frauentag` 는 de_be). 신규 0.

---

## 사람의 판단 요청

1. **현행 자구를 어디서 얻을지.** 공식 포털의 문서 API 가 두 렌더 모두 500 이다. 선택지:
   - (a) 날을 바꿔 같은 렌더를 다시 한다(HB 296390 처럼 지속 500 일 수 있다).
   - (b) 포털의 검색 화면에서 문서를 찾아 연다 — 다른 문서 id·경로를 쓰는 것이라 이번 범위 밖이었다.
   - (c) 관보 체인만 쓴다 — 2002 재공포본(GVOBl. 4/02)은 온라인 목록(2014–) 밖이다.
2. **A2·A4 를 A1 과 떼어 돌릴지.**
   - 지시대로 A1 실패에서 Part A 전체를 멈췄다.
   - A2(2022 Nr. 31 재수령·시행 조항)와 A4(관보 목록 제목 검색)는 포털과 별개 출처(regierung-mv.de, 정적)다.
   - 다음 차례에 따로 돌릴지 정한다.
3. **모르는 필드 거부.** 독일 주 로더는 모르는 필드를 조용히 무시한다(B2 — `valid_from` 이 있어도 2020–2022 에 Frauentag 가 나간다). 선택지:
   - (a) de_mv 의 로더에만 닫힌 필드 집합을 둔다.
   - (b) 모든 주 로더에 둔다(별 PR — 기존 표가 쓰는 필드 전수 확인이 먼저).
   - (c) 두지 않는다.
4. **경계값의 단위·값.** 권고는 (iii) `effective_from: 2022-07-13`(시행일, 날짜, 포함 경계)이다. 연도(2023)를 원하면 (ii) 이고, 그러면 레포의 연 단위 거부 결정과 갈린다.
5. **MV 구현의 선행 조건.**
   - § 2 Abs. 1 자구 없이 MV 를 구현할 수 없다 — 11 건 모두 name·source 근거가 없다.
   - 1 이 풀릴 때까지 구현을 미룰지 정한다. 아니면 조문 대신 다른 1차 자료를 쓸지 정한다(예: 관보 색인의 개정 이력과 개정법 원문만).
