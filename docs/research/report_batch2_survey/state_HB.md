# Bremen (HB) — 공휴일 법령 조사 (batch 2 survey)

- 조사일: 2026-09-30 (UTC 09:25–09:32)
- 요청 로그: `state_HB_fetch.log` (총 20회 HTTP 요청, 그 외 문서 ID 검색용 WebSearch 3회)
- 표기: [추론] = 직접 관찰하지 않고 도출한 문장. 태그가 없는 문장은 이번 세션에서 받은 응답을 직접 확인한 내용이다.

## A. 법령

- 정식 명칭(포털 표기): „Gesetz über die Sonn-, Gedenk- und Feiertage“ vom 12. November 1954. 공식 약칭은 문서에서 확인하지 못함.
  - 2018년 개정 관보(아래 C)는 „Gesetz über die Sonn- und Feiertage“라는 옛 이름을 씀. 이름에 „Gedenk-“가 붙은 것은 2020-03-14 판부터 [추론: 2020 판 표제가 „Die Sonntage und die staatlich anerkannten Gedenk- und Feiertage“로 바뀌고 § 7a가 들어간 것을 보고 판단].
- 공식 법령 포털: Transparenzportal Bremen (`www.transparenz.bremen.de`), Fundstelle „SaBremR 113-c-1“
- 포털에서 확인한 통합본(consolidated) 판:

| 문서 ID | PDF URL (template=00_html_to_pdf_d) | „Inkrafttreten“ 기재 | 결과 |
|---|---|---|---|
| 74780 | `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.74780.de&template=00_html_to_pdf_d` | 04.06.2013 | 200 PDF, 쪽마다 „außer Kraft“ |
| 87915 | `…gsid=bremen2014_tp.c.87915.de&template=00_html_to_pdf_d` | 28.07.2015 | 200 PDF, 쪽마다 „außer Kraft“ |
| 145882 | `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.145882.de&template=00_html_to_pdf_d` | 14.03.2020 | 200 PDF (8쪽), 쪽마다 „außer Kraft“ |
| 296390 | `https://www.transparenz.bremen.de/sixcms/detail.php?gsid=bremen2014_tp.c.296390.de&template=00_html_to_pdf_d` | (확인 못 함) | **500 „db-connection failed“, 재시도해도 500** |

- **현행판은 받지 못했다.** 검색엔진 스니펫에 따르면 145882 판은 „14.03.2020 bis 29.06.2025“ 동안 유효했고, 296390 판은 Inkrafttreten 30.06.2025이다. 이 날짜들은 포털을 직접 보고 확인한 것이 아니라 스니펫에서 가져왔다. 145882 PDF 쪽마다 „außer Kraft“ 표시가 있는 것은 직접 확인했다.
  - 그래서 아래 B는 **2020-03-14 판(145882, 이미 효력 상실)** 기준이다. 2025-06-30 판에서 § 2 목록이 바뀌었는지는 확인하지 못했다.
  - 2025년 관보를 제목어 „Feiertage“·„Gedenk“로 검색했더니 0건이었다(로그 #17, #18). [추론] 2025-06 개정은 제목에 Feiertag가 들어가지 않는 개정법(Artikelgesetz), 예를 들어 소관·관할 정비일 수 있다. § 2 목록이 바뀌었을 가능성은 낮지만 검증되지 않았다.
  - 모든 판의 머리글에 „Zuletzt geändert durch … Geschäftsverteilung des Senats vom 02.09.2025 (Brem.GBl. S. 674)“가 똑같이 찍혀 있다. [추론] 이 줄은 해당 판이 아니라 포털 메타데이터를 보여 주는 것으로 보인다.
- 접근일: 2026-09-30
- **통합본은 이 레포에서 2차 출처다.** 법적 효력이 있는 것은 Brem.GBl. 공포본이다. 이 레포 YAML `source`에는 가능하면 관보 판면을 인용해야 한다.
- 메타정보 페이지(`/metainformationen/…-87915`, `…-145882`)는 둘 다 500 „db-connection failed“였다. 포털 자체 검색도 503 „Die Suche ist leider momentan nicht erreichbar.“였다. [추론] 서버 쪽 일시 장애로 보이며 차단 신호(403/429)는 아니다. 그래도 규칙에 따라 해당 경로는 더 시도하지 않았다.

## B. 공휴일 목록 (2020-03-14 판, § 2 Abs. 1 „Staatlich anerkannte Feiertage sind:“)

| # | 법문 표현 | 범위 |
|---|---|---|
| a | „der Neujahrstag,“ | 주 전역 |
| b | „der Karfreitag,“ | 주 전역 |
| c | „der Ostermontag,“ | 주 전역 |
| d | „der 1. Mai,“ | 주 전역 |
| e | „der Himmelfahrtstag,“ | 주 전역 |
| f | „der Pfingstmontag,“ | 주 전역 |
| g | „der 3. Oktober - Tag der deutschen Einheit -,“ | 주 전역 |
| h | „der 1. Weihnachtstag,“ | 주 전역 |
| i | „der 2. Weihnachtstag,“ | 주 전역 |
| j | „der Reformationstag.“ | 주 전역 |

- 주 전역 공휴일: 10개. 지방자치단체나 지역으로 한정된 공휴일은 § 2에 없다.
- § 2가 아닌 다른 조항에 나오는 날(모두 **범위 밖**):
  - § 7a Abs. 1 „Der 8. Mai als Tag der Befreiung vom Nationalsozialismus …“ „… ist staatlich anerkannter Gedenktag.“ 이것은 공휴일이 아니라 **기념일(Gedenktag)**이다. 근로자에게는 „soweit betriebliche Notwendigkeiten nicht entgegenstehen“ 조건으로 기념행사 참석 기회를 줄 뿐이다. → 범위 밖(공휴일 아님)
  - § 8 Abs. 1 religiöse Feiertage는 해당 교파 신자에게만 적용되고, 예배 장소 인근 소음 금지와 § 9/§ 10 예배 참석·수업 면제가 효과다. → **범위 밖(집단 한정)**
    - „Am 31. Oktober - Reformationsfest - (evangelischer Feiertag)“ (§ 2 j와 같은 날이며, 그쪽이 주 전역 공휴일이다)
    - „am Buß- und Bettag - (evangelischer Feiertag)“
    - „am Donnerstag nach Trinitatis - Fronleichnam - (katholischer Feiertag)“
    - „am 1. November - Allerheiligen - (katholischer Feiertag)“
    - 유대교 축일: Rosch Haschana, Jom Kippur, Sukkoth, Schemini Azereth, Simchat Thora, Pessach, Schawuoth
  - § 8 Abs. 2 이슬람 축일(Opferfest, Ramadanfest, Aschura)과 Abs. 3 알레비 축일(Aşure-Tag, Hızır-Lokması, Nevruz) → 범위 밖(집단 한정)
  - § 6/§ 7 Volkstrauertag, Totensonntag, 24.12.는 행사·도박 금지일일 뿐 공휴일이 아니다. → 범위 밖
- 참고: 2026년 공휴일 API 캡처(`fapi_2026_HB.json`)도 같은 10개를 나열한다(2차 출처 비교용).

## C. 2020-01-01 이후 영향을 주는 변경

1. **Reformationstag(10/31) 상설 공휴일화**. 1990년 이후 도입되어 2020년 이후에도 효력이 있다.
   - 내용: § 2 Abs. 1 j를 „der Reformationstag.“로 새로 씀. 이전 판(2015-07-28 판)의 j는 „der 31. Oktober 2017 (500. Jahrestag der Reformation).“로, 2017년 한 번만 쉬는 날이었다.
   - 적용 연도: 2018년부터. 관보 원문에 „Das Gesetz tritt am Tag nach seiner Verkündung in Kraft.“, 공포일 „Verkündet am 28. Juni 2018“로 되어 있다. 따라서 발효일은 2018-06-29이다 [추론: 공포일+1일로 계산]. 2020년 이후 모든 연도에 적용된다.
   - 개정법: „Gesetz zur Änderung des Gesetzes über die Sonn- und Feiertage Vom 26. Juni 2018“, Brem.GBl. 2018 Nr. 63, S. 302.
   - 출처 등급: 포털 통합본 각주에 „Gesetzes vom 26.06.2018 (Brem.GBl. S. 302)“로 적혀 있다(**포털 기재**). 관보 PDF 원문에서도 같은 내용을 직접 확인했다(아래 F). 이 한 건은 관보로 확인했지만 개정 이력 전체를 추적하지는 않았다.
2. **§ 7a 8. Mai Gedenktag 신설**(2020-03-14 판)
   - 내용: 공휴일이 아닌 기념일이다. 공휴일 목록은 바뀌지 않는다.
   - 개정법: 이번에 받은 통합본 PDF에는 개정법 인용이 없어 확인하지 못했다. 발효일은 **포털 기재** „Inkrafttreten: 14.03.2020“이다.
   - 이 레포의 `achter_mai_2020`(de_be 일회성 공휴일)와는 성격이 다르다. Bremen 2020년 5월 8일은 휴일이 아니다 [추론: § 2 목록에 없고 § 7a는 휴무를 부여하지 않는 조문이라 판단].
3. **2025-06-30 판**(ID 296390): 무엇이 바뀌었는지 모른다(A 참고). 미확인.
4. 2020년 이후 일회성 공휴일: 2020-03-14 판 § 2에는 없다. 2025-06-30 이후 판은 확인하지 못했다.
   - § 12 Nr. 2에 따라 Senat는 „aus besonderem Anlaß im Einzelfall“ 이 법의 규정을 다른 날에도 적용한다고 선언할 수 있다. [추론] 이 수권은 § 3 보호(휴식일) 규정을 적용하는 것이지 § 2 공휴일을 추가하는 것이 아니다. 이 방식의 공휴일 사례가 있는지는 조사하지 않았다.

## D. 필요한 규칙 유형 (주 전역 10개)

| 항목 | 규칙 | 레포 지원 |
|---|---|---|
| Neujahrstag | 고정 01-01 | (1) 있음 |
| Karfreitag | 부활절 −2 | (2) 있음 |
| Ostermontag | 부활절 +1 | (2) 있음 |
| 1. Mai | 고정 05-01 | (1) 있음 |
| Himmelfahrtstag | 부활절 +39 | (2) 있음 |
| Pfingstmontag | 부활절 +50 | (2) 있음 |
| 3. Oktober | 고정 10-03 | (1) 있음 |
| 1. Weihnachtstag | 고정 12-25 | (1) 있음 |
| 2. Weihnachtstag | 고정 12-26 | (1) 있음 |
| Reformationstag | 고정 10-31 | (1) 있음 |

- 새로운 규칙 유형: **없음**.
  - Reformationstag는 2018년 발효라서 2020년 이후 구간 안에 시작일이나 종료일이 없다. 유효기간 규칙이 필요 없다.
  - 요일 기반 계산이 필요한 항목(Buß- und Bettag 등)은 § 8 한정 항목뿐이고 모두 범위 밖이다.
- 단서: 2025-06-30 판에서 목록이 바뀌었다면 이 결론은 달라질 수 있다(미확인).

## E. 키 매핑

| 항목 | 키 | 판정 |
|---|---|---|
| Neujahrstag | `neujahr` | 기존 재사용 |
| Karfreitag | `karfreitag` | 기존 재사용 |
| Ostermontag | `ostermontag` | 기존 재사용 |
| 1. Mai | `erster_mai` | 기존 재사용 |
| Himmelfahrtstag | `christi_himmelfahrt` | 기존 재사용 (법문은 „Himmelfahrtstag“, 같은 날) |
| Pfingstmontag | `pfingstmontag` | 기존 재사용 |
| 3. Oktober | `tag_der_deutschen_einheit` | 기존 재사용 |
| 1. Weihnachtstag | `erster_weihnachtstag` | 기존 재사용 |
| 2. Weihnachtstag | `zweiter_weihnachtstag` | 기존 재사용 |
| Reformationstag | `reformationstag` | 기존 재사용 |

- NEW 키: **없음**. 미리 알려 둔 `buss_und_bettag`는 HB에서는 § 8 집단 한정이라 쓰지 않는다.

## F. 관보(Brem.GBl.) 접근성

- 포털: `https://www.gesetzblatt.bremen.de/` (200, 정적 HTML). 페이지에 „Es wird in elektronischer Form geführt …“라고 적혀 있다.
  - 호별 PDF는 `/fastmedia/218/YYYY_MM_DD_GBl_Nr_NNNN_signed.pdf` 형식의 **직접 링크**로, 정적 HTML에 그대로 있다. JS 셸이 아니다.
  - 연도별 합본 PDF 링크는 2013–2025년치가 정적 HTML에 있다. 예: `/fastmedia/220/2018_gesetzblatt.pdf`, `/fastmedia/220/Gesetzblatt_Bremen_2025.pdf`. 링크만 보았고 내려받지는 않았다.
  - 연도 선택 목록은 2013–2026년이다. 2012년 이전 관보는 이 포털에서 보지 못했다. [추론] 2012년 이전은 다른 경로가 필요하다.
  - 제목어 검색은 GET 파라미터(`sv[suchbegriff]`, `sv[suchbegriff_jahr][0]`)로 동작하고 결과 URL을 그대로 딥링크할 수 있다. 연도 파라미터를 여러 개 주면 첫 연도만 적용됐다(로그 #13).
- **개정 PDF 1건 받음** (holiday 목록의 가장 최근 확인된 개정)
  - `https://www.gesetzblatt.bremen.de/fastmedia/218/2018_06_28_GBl_Nr_0063_signed.pdf` → **200, application/pdf, 241,672 bytes**, 1쪽, 판면 S. 302
  - 원문 발췌: „1. § 2 Absatz 1j wird wie folgt neu gefasst: der Reformationstag.“
- 인증이나 rate-limit: gesetzblatt.bremen.de에 3초 간격으로 9회 요청했고 모두 200이었다. 403/429나 로그인 요구는 없었다.
- transparenz.bremen.de(법령 포털) 관찰 결과:
  - 404: 추측한 `/suche` 경로
  - 503: 사이트 검색
  - 500 „db-connection failed“: 메타정보 페이지 2건, 현행판 PDF 2회
  - 200: 구판 PDF 3건
  - 403/429는 없었다. 장애성 오류에 해당하므로 규칙대로 재시도를 최소화하고 중단했다.
- 의회 문서 서버: `https://www.bremische-buergerschaft.de/drs_abo/Drs-18-896_3d1.pdf` → 200, application/pdf, 109,730 bytes
  - 2013년 개정안 „Mitteilung des Senats vom 7. Mai 2013“(Drucksache 18/896)이다. 법안 원문은 의회 서버에서도 받을 수 있다.
  - 관보 사본 자체를 이 서버가 싣고 있는지는 확인하지 않았다.

## 운영 메모
- scratchpad 공유 문제: 공유 scratchpad의 fetch 스크립트(`f.sh`)가 다른 병렬 에이전트에 의해 덮어써졌다. 그 때문에 초기 로그 파일이 유실됐고, 요청 2건(#16, #17)은 다른 에이전트의 `scratchpad/st.log`에 기록됐다. `state_HB_fetch.log`는 세션 출력(curl `-w` 결과)으로 다시 만들었으며, 그 사실을 파일 머리말에 적어 두었다.
- 작업용 PDF와 텍스트는 scratchpad/hb_only에만 두었다. 보고서 폴더에는 원문을 덤프하지 않았다.

## 요약 (5줄)
1. 주 전역 공휴일 10개 (2020-03-14 통합본 § 2 기준. 2025-06-30 현행판은 포털 500으로 받지 못해 미확인)
2. 한정 항목 제외: § 8 종교 축일(Buß- und Bettag, Fronleichnam, Allerheiligen, 유대교·이슬람·알레비 축일)과 § 7a 8. Mai Gedenktag(공휴일 아님)은 모두 범위 밖
3. 새로운 규칙 유형: 없음 (고정일과 부활절 오프셋만 필요. Reformationstag는 2018년 발효라 2020년 이후 구간에 유효기간 경계 없음)
4. NEW 키: 없음 (10개 모두 기존 키로 재사용)
5. 관보 접근: 열림. gesetzblatt.bremen.de의 정적 HTML과 직접 PDF 링크로 2013년부터 볼 수 있고, 2018 Nr. 63 S. 302를 200으로 받음. 법령 포털(통합본)은 부분 접근: 구판은 받았고 현행판·메타정보·검색은 500/503.
