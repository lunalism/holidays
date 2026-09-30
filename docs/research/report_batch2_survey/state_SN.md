# Sachsen (SN) — 공휴일 법령 조사 (batch2 survey)

- 조사일: 2026-09-30 (요청 시각은 `state_SN_fetch.log` 참조, UTC)
- 범위: 조사만. 레포(/Volumes/Data/dev/holidays)는 수정하지 않음.
- 표기: 직접 관측한 내용은 태그 없이, 관측에서 끌어낸 판단은 **[추론]** 으로 표시.
- 로그 관련 주의: 공유 scratchpad 충돌로 최초 로그 파일이 유실되어, 09:29Z 이전 항목은 각 요청 직후 터미널에 찍힌 같은 행으로 재구성함(로그 머리말에 명시).

---

## A. 법령 (Statute)

- 공식 명칭(포털 표기): „Gesetz über Sonn- und Feiertage im Freistaat Sachsen (SächsSFG)“, „Vom 10. November 1992“.
  - 과제 설명의 „Sächsisches Sonn- und Feiertagsgesetz“는 통칭이고, REVOSax 표제는 위와 같음.
- 원 공포 출처(포털 기재): „SächsGVBl. 1992 Nr. 35, S. 536“, Fsn-Nr. 114-2.
- 현행 통합본(consolidated): REVOSax (Recht und Vorschriftenverwaltung Sachsen, 발행 Sächsische Staatskanzlei)
  - URL: https://www.revosax.sachsen.de/vorschrift/3997-SaechsSFG (HTTP 200, 2026-09-30 접속)
  - PDF 판: https://www.revosax.sachsen.de/vorschrift_gesamt/3997/48138.pdf (HTTP 200, application/pdf, 53,502 B, 4쪽)
  - 페이지 표기: „Rechtsbereinigt mit Stand vom 7. Mai 2025“, „Fassung gültig ab: 7. Mai 2025“
  - Vollzitat: „…zuletzt durch das Gesetz vom 23. April 2025 (SächsGVBl. S. 146) geändert…“
  - 역사적 판(Historische Fassungen) 목록: 21.11.1992–02.07.2002 / 03.07.2002–26.04.2008 / 27.04.2008–20.12.2010 / 21.12.2010–09.02.2013 / 10.02.2013–06.05.2025 / 07.05.2025–.
- **이 레포 기준에서 통합본은 2차 출처다.** REVOSax 통합본은 편집된 현행 텍스트이며, 법적 정본은 SächsGVBl.에 공포된 원 법률·개정법이다. 아래 B–E는 전부 통합본에서 읽은 것이다.
- 참고(발견 경로): REVOSax 검색은 POST 폼(CSRF 토큰 포함)이라 사용하지 않았음(로컬 권한 정책으로 전송 전 차단). 첫 시도한 ID 추측 URL(`/vorschrift/3853-…`)은 무관한 문서로 연결됨. 정확한 REVOSax URL은 de.wikipedia „Gesetzliche Feiertage in Deutschland“ 문서의 참고 링크에서 얻었고, 내용은 모두 REVOSax에서 직접 확인함(위키 내용은 근거로 쓰지 않음).

## B. 공휴일 목록 (현행 § 1 Abs. 1)

§ 1 Abs. 1 도입부: „Gesetzliche Feiertage sind:“ (전체 12개 항목)

| # | 법문 표현(인용) | 적용 범위 | 비고 |
|---|---|---|---|
| 1 | „Neujahr (1. Januar)“ | 주 전역 | |
| 2 | „Karfreitag“ | 주 전역 | |
| 3 | „Ostermontag“ | 주 전역 | |
| 4 | „Tag der Arbeit (1. Mai)“ | 주 전역 | |
| 5 | „Christi Himmelfahrt“ | 주 전역 | |
| 6 | „Pfingstmontag“ | 주 전역 | |
| 7 | „Fronleichnam (nur in den … durch Rechtsverordnung bestimmten Regionen)“ (생략부: 내무부 Staatsministerium des Innern) | **지역 한정** | **범위 밖** |
| 8 | „Tag der Deutschen Einheit (3. Oktober)“ | 주 전역 | |
| 9 | „Reformationsfest (31. Oktober)“ | 주 전역 | 법문 명칭은 Reformationstag 가 아니라 Reformationsfest |
| 10 | „Buß- und Bettag“ | 주 전역 | 법문에 날짜 정의 없음 (D 참조) |
| 11 | „1. Weihnachtstag (25. Dezember)“ | 주 전역 | |
| 12 | „2. Weihnachtstag (26. Dezember)“ | 주 전역 | |

- 주 전역 11개, 지역 한정 1개(Fronleichnam).
- Fronleichnam 대상 지역을 정하는 법규명령(Rechtsverordnung) 자체는 이번에 열람하지 않았음. 소르브 지역(Landkreis Bautzen)의 일부 지자체라는 통상 설명은 이번 조사에서 공식 출처로 확인하지 않음 **[추론/미확인]**. 범위 밖이므로 추가 확인하지 않음.
- 공휴일이 아닌 항목(참고, 모두 범위 밖):
  - § 2 Gedenk- und Trauertage: Volkstrauertag, Totensonntag, „der 8. Mai als Tag der Befreiung vom Nationalsozialismus…“ — 기념일이며 § 1의 gesetzliche Feiertage 가 아님.
  - § 2a: 지자체가 조례(Satzung)로 정할 수 있는 1989 평화혁명 „örtlicher Gedenktag“.
  - § 3 Religiöse Feiertage (Erscheinungsfest 6.1., Frühjahrsbußtag, Gründonnerstag, 공휴일이 아닌 곳의 Fronleichnam, Johannestag, Peter und Paul, Mariä Himmelfahrt, Allerheiligen, Mariä Empfängnis): 예배 참석을 위한 결석·결근권만 부여하며 공휴일이 아님.

## C. 2020-01-01 이후 변경 / 1990년 이후 도입분 / 2020+ 일회성 공휴일

모두 **포털 기재** 사항이며 개정 연쇄를 검증하지는 않았다.

1. **§ 1 Abs. 1 (공휴일 목록)** — 포털 각주: „§ 1 Absatz 1 geändert durch Artikel 4 des Gesetzes vom 6. Juni 2002 (SächsGVBl. S. 168, 170)“. **(포털 기재)**
   - 2020-01-01 이후 § 1 개정 각주는 없음. 공휴일 목록에 대한 마지막 개정은 2002년으로 기재됨.
   - 2002년 개정 내용(어떤 문구가 바뀌었는지)은 확인하지 않음. 2020+ 결과에는 영향이 없다고 봄 **[추론]**.
2. **1992 원 법률 자체**(1990년 이후 도입, 1992-11-21 시행으로 포털 기재): 현재 목록 전체의 근거이며 Buß- und Bettag와 Reformationsfest가 주 전역 공휴일로 들어 있음. **(포털 기재)**
3. **§ 2 신규 문구(2025)** — 8. Mai를 Gedenktag로 지정. 포털 각주: „§ 2 neu gefasst durch Artikel 1 der Verordnung vom 23. April 2025 (SächsGVBl. S. 146)“. **(포털 기재)** 시행일은 2025-05-07(개정법 페이지의 „Fassung gültig ab: 7. Mai 2025“). **공휴일이 아니므로 범위 밖.**
   - 포털 내부 불일치(관측): SächsSFG 각주는 „Verordnung vom 23. April 2025“라고 적었지만, 개정 문서 자체(https://www.revosax.sachsen.de/vorschrift/21192)와 Vollzitat은 „Gesetz … vom 23. April 2025 (SächsGVBl. S. 146)“이고 표제는 „Gesetz zur Einführung eines Gedenktages…“이다. 개정 문서 기재: „Der Sächsische Landtag hat am 26. März 2025 … beschlossen“, 출처 „SächsGVBl. 2025 Nr. 6, S. 146“. 각주의 „Verordnung“은 포털 표기 오류로 보임 **[추론]**.
4. **2020년 이후 일회성 공휴일**: 통합본에는 일회성 공휴일 조항이 없고, 2020 이후 § 1 개정 각주도 없음. SN에는 해당 없음(포털 기준). 예컨대 2020·2025년 8. Mai는 SN에서 공휴일이 아니며, 2025년부터 기념일(§ 2)임. **(포털 기재)**
5. § 4, § 6 개정(2008, 2010, 2013, 2025)은 휴일 보호 규정이며 공휴일 목록과 무관.

## D. 주 전역 항목별 필요한 규칙 유형

레포가 지원하는 유형: (1) 고정 월/일, (2) 부활절 일요일 기준 일수 오프셋, (3) 일회성 날짜(`_YYYY`, de_be에만 있음). 연도 범위 유효성 없음, 요일 기반 규칙 없음.

| 항목 | 규칙 유형 | 비고 |
|---|---|---|
| Neujahr | (1) 01-01 | |
| Karfreitag | (2) Easter −2 | |
| Ostermontag | (2) Easter +1 | |
| Tag der Arbeit | (1) 05-01 | |
| Christi Himmelfahrt | (2) Easter +39 | |
| Pfingstmontag | (2) Easter +50 | |
| Tag der Deutschen Einheit | (1) 10-03 | |
| Reformationsfest | (1) 10-31 | 2020 이후 전 기간 유효(1992 법률부터 존재, 포털 기재). 연도 범위 불필요 |
| 1. Weihnachtstag | (1) 12-25 | |
| 2. Weihnachtstag | (1) 12-26 | |
| **Buß- und Bettag** | **NEW** | 아래 참조 |

**Buß- und Bettag — 법문의 정의**
- § 1 Abs. 1에는 „Buß- und Bettag,“라는 명칭만 있고 **날짜나 계산식이 없다**(관측). 법률 어디에도 이 날의 정의 문구가 없다(통합본 전문 기준 관측).
- 같은 법률 § 2는 Totensonntag를 „letzter Sonntag vor dem 1. Advent“, Volkstrauertag를 „vorletzter Sonntag vor dem 1. Advent“로 정의한다. Buß- und Bettag 정의는 없다.
- 필요한 계산 **[추론 — 법문 밖의 관행적 정의]**: Buß- und Bettag는 통상 Totensonntag(1. Advent 전 마지막 일요일) 직전 수요일로 본다.
  - 1. Advent 일요일(11-27~12-03 사이 일요일)에서 11일 전. 결과적으로 11월 16일~22일 사이의 수요일.
  - 부활절과 무관한 **요일 기반 규칙**이며 레포의 (1)(2)(3) 어느 것으로도 표현할 수 없다 → **NEW 규칙 유형**.
  - 검산 예시(계산값, 관측 아님) **[추론]**: 2026-11-18 (1. Advent 2026-11-29 → Totensonntag 11-22 → 수요일 11-18). 레포 밖 제3자 API 스냅샷(`fapi_2026_SN.json`, 2차 참고)의 2026-11-18 과 일치.
- 법문에 정의가 없으므로, 구현 근거(`source`)에 무엇을 쓸지(법문 명칭만 있고 날짜 규칙은 관행) 결정이 필요함 **[추론]**.

그 밖에 2020+ 범위에서 연도 범위 유효성이 필요한 주 전역 항목: 없음(포털 기준).

## E. 키 매핑

| 항목 | 키 | 구분 |
|---|---|---|
| Neujahr | `neujahr` | 기존 키 재사용 |
| Karfreitag | `karfreitag` | 기존 키 재사용 |
| Ostermontag | `ostermontag` | 기존 키 재사용 |
| Tag der Arbeit | `erster_mai` | 기존 키 재사용 |
| Christi Himmelfahrt | `christi_himmelfahrt` | 기존 키 재사용 |
| Pfingstmontag | `pfingstmontag` | 기존 키 재사용 |
| Tag der Deutschen Einheit | `tag_der_deutschen_einheit` | 기존 키 재사용 |
| Reformationsfest | `reformationstag` | 기존 키 재사용 (법문 명칭은 „Reformationsfest“. 표시명 차이만 있고 날짜는 동일) |
| 1. Weihnachtstag | `erster_weihnachtstag` | 기존 키 재사용 |
| 2. Weihnachtstag | `zweiter_weihnachtstag` | 기존 키 재사용 |
| Buß- und Bettag | `buss_und_bettag` | **예고됨(pre-announced), 미사용** — 키는 있으나 규칙 유형이 NEW |
| (Fronleichnam) | — | 범위 밖(지역 한정) |

- NEW 키: 없음.

## F. 관보(SächsGVBl.) 접근성

관측한 내용:
- **REVOSax** (www.revosax.sachsen.de): 정적 HTML에 본문이 모두 들어 있음(JS 셸 아님). 딥링크 가능(`/vorschrift/<ID>`, `/vorschrift/<ID>.<n>` 역사판, `/vorschrift_gesamt/<ID>/<ver>.pdf`). 요청 7건 모두 200, 차단·레이트리밋 없음.
  - 다만 REVOSax가 링크하는 PDF는 **통합본 PDF**이며 관보 원문 PDF가 아님. SächsSFG·개정법 페이지에는 관보 PDF 링크가 없고, 출처 표기(„SächsGVBl. 2025 Nr. 6, S. 146“)만 있음(관측).
  - 검색은 CSRF 토큰이 있는 POST 폼. 사용하지 않음.
- **관보 발행처**: SV SAXONIA Verlag. 그 사이트(saxonia-verlag.de/juristischer-verlag/)에 „Verlag der amtlichen Verkündungs- und Veröffentlichungsblätter“라고 적혀 있음(SächsGVBl. 포함).
- **recht-sachsen.de** (SAXONIA 운영, Magento 기반 쇼프):
  - 목록 https://www.recht-sachsen.de/veroffentlichungen/sgvl.html → 200. 호별 상품 페이지, 가격 표시(예: Heft 12/2026 „8,56 €“, 연간 구독 „75,49 €“). 목록은 페이지네이션(`?p=2…5`)되며 `archiv.html` 링크가 있으나 열람하지 않음. 어느 연도까지 온라인에 있는지 확인하지 않음.
  - 호별 페이지는 딥링크 가능: https://www.recht-sachsen.de/sgvl/sachsisches-gesetz-und-verordnungsblatt-2025-6.html → 200, 제목 „Sächsisches Gesetz- und Verordnungsblatt Heft 6/2025“, 가격 „8,03 €“, 변형 „Elektronisch“/„Print“(유료). 설명에 개정법 제목이 나옴.
  - 이 페이지의 „Vorschau“ 첨부 https://www.recht-sachsen.de/downloadable/download/attachment/id/3249/ → **200, `application/octet-stream`, 893,093 B**. 실제로는 PDF 1.6, 48쪽, 메타데이터 Title „Sächsisches Gesetz- und Verordnungsblatt Nr. 6/2025“(로그인 없이 받음).
    - 1쪽(S. 145, 목차)만 텍스트 추출 가능: „Gesetz zur Einführung eines Gedenktages … vom 23. April 2025 …… 146“.
    - 2~48쪽은 텍스트 레이어가 없는 이미지 페이지. 본문(S. 146)을 읽을 수 있는지(워터마크·저해상도 미리보기 여부)는 확인하지 않음.
    - 유료 상품의 미리보기이므로 정본 인용 출처로 쓰기에는 지위가 불분명함 **[추론]**.
  - 로그인·403·429는 관측되지 않음(요청 5건, 모두 200).
- **EDAS (Landtag Sachsen)** https://edas.landtag.sachsen.de/ (http→https 리다이렉트, 200, text/html iso-8859-1, 3,420 B): 정적 HTML은 **frameset**(Navigation.aspx 등 ASP.NET 프레임)과 `#/details`를 `/redas/#/details`로 보내는 JS 리다이렉트뿐이고 문서 내용은 없음. 규칙에 따라 여기서 중단함. EDAS에 관보 사본이 있는지는 **확인하지 않음**.
- 1992년 원 관보(SächsGVBl. 1992 S. 536)와 2002년 개정(S. 168, 170)은 이번에 찾지 않음. recht-sachsen.de 아카이브 범위는 미확인.

종합: 통합본은 **개방**(REVOSax, 딥링크·PDF 가능). 관보 원문은 **부분 개방**. 호별 페이지는 딥링크되고 미리보기 PDF도 로그인 없이 받을 수 있지만, 정식 원문은 유료 상품이고 과거 연도 범위는 확인하지 않음. EDAS는 frameset/JS 앱이라 중단함.

---

## 5줄 요약
1. 주 전역 공휴일: **11개** (Neujahr, Karfreitag, Ostermontag, 1. Mai, Christi Himmelfahrt, Pfingstmontag, 3. Okt., Reformationsfest, Buß- und Bettag, 25./26. Dez.). 출처 REVOSax 통합본(2차), 2025-05-07판.
2. 지역 한정으로 제외: **1개**, Fronleichnam(내무부 법규명령으로 정한 지역만) → 범위 밖. 8. Mai(2025~)는 Gedenktag이며 공휴일 아님. 2020+ 일회성 공휴일 없음(포털 기재).
3. NEW 규칙 유형: **Buß- und Bettag의 요일 기반 규칙 1종**. 법문에는 날짜 정의가 없고, 관행상 1. Advent 전 마지막 일요일 직전 수요일(11/16~22) [추론].
4. NEW 키: **없음**. 10개는 기존 키 재사용, `buss_und_bettag`는 예고 키(미사용). Reformationsfest → `reformationstag`.
5. 관보 접근: **부분 개방**. REVOSax 통합본은 개방·딥링크 가능. SächsGVBl.은 recht-sachsen.de에서 유료 판매하며, 2025 Nr. 6 미리보기 PDF는 200(893,093 B)으로 받음. EDAS는 frameset/JS라 중단. 차단(403/429)은 관측되지 않음.
