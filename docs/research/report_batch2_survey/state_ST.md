# Sachsen-Anhalt (ST) 공휴일 법령 조사

- 조사일: 2026-09-30 (UTC 09:25–09:31)
- 요청 수: 16건 (로그: `state_ST_fetch.log`)
- 표기 규칙: 직접 관찰하지 않고 도출한 문장에는 [추론] 을 붙였다. 인용은 독일어 원문 그대로 두었다.

## A. 법령

- 공식 명칭: „Gesetz über die Sonn- und Feiertage (FeiertG LSA)“
- 현행 판: „in der Fassung der Bekanntmachung vom 25. August 2004“ (비공식 사이트 gesetze.co 제목에서 관찰)
- 공식 포털 URL: https://www.landesrecht.sachsen-anhalt.de/bsst/document/jlr-FeiertGSTrahmen (접속일 2026-09-30)
  - 이 문서 ID 는 gesetze.co 페이지 데이터의 `source_url` 에서도 관찰했다.
  - 결과는 HTTP 200, 5310 바이트였다. 정적 HTML 에는 `<noscript>` 안내문만 있고 법문이 없는 **JS 셸**이다. 인용한 안내문은 „Wenn Sie diese Meldung sehen, haben Sie in Ihrem Browser kein JavaScript aktiviert.“ 이다.
  - 이 문서 URL 의 `<title>` 은 „Bürgerservice Thüringen“ 이었다(포털 루트의 제목은 „Landesrecht Sachsen-Anhalt“). 원인은 알 수 없다.
  - 포털 루트(`/` → `/bsst/`)와 옛 jportal 딥링크(→ `/bsst/?docId=jlr-NNLST0000411C…`)도 같은 5310 바이트 JS 셸이었다. **공식 포털 경로는 여기서 중단했다.**
- **이 레포에서 통합본(consolidated text)은 2차 자료다.** 효력의 정본은 관보(GVBl. LSA)에 실린 원 개정법이다. 게다가 이번에 본문을 읽은 곳은 공식 포털이 아니다.
- **비공식 출처(공식 아님):** https://gesetze.co/ST/FeiertG_LSA (및 `/1`, `/2`, `/2a`, `/3`). 아래 B·C 의 인용은 모두 여기서 가져왔다.
  - 페이지 데이터의 `update_time` 은 "2026-05-27T02:30:23Z" 이다.
  - Stand-Vermerk 에는 „letzte berücksichtigte Änderung: §§ 1 und 5 geändert und § 2a eingefügt“ 라고 적혀 있다.
  - 이어서 „durch Artikel 5 des Gesetzes vom 4. Mai 2026 (GVBl. LSA S. 178, 180)“ 라고 적혀 있다.
  - [추론] 공식 포털을 미러링한 것으로 보이지만 동일성은 검증하지 않았다.
- 교차 확인(비공식): de.wikipedia „Gesetzliche Feiertage in Deutschland“ 의 표를 봤다.
  - ST 열에는 11개 항목이 „ja“ 이고, Buß- und Bettag 는 „bis 1994“ 로 적혀 있다.
  - 합계 행은 11 이다(고정일 7, 고정 요일 4).
  - 기존 로컬 파일 `fapi_2026_ST.json` 에도 2026년 11개 항목이 있고, 이 목록과 일치한다.

## B. 공휴일 목록 (§ 2 „Staatlich anerkannte Feiertage“, 비공식 통합본 기준)

| Nr. | 법문 (인용) | 범위 |
|---|---|---|
| 1 | „der Neujahrstag“ | 주 전역 |
| 2 | „der Tag Heilige Drei Könige (6. Januar)“ | 주 전역 |
| 3 | „der Karfreitag“ | 주 전역 |
| 4 | „der Ostermontag“ | 주 전역 |
| 5 | „der 1. Mai“ | 주 전역 |
| 6 | „der Tag Christi Himmelfahrt“ | 주 전역 |
| 7 | „der Pfingstmontag“ | 주 전역 |
| 8 | „der Tag der Deutschen Einheit (3. Oktober)“ | 주 전역 |
| 9 | „der Reformationstag (31. Oktober)“ | 주 전역 |
| 10 | „(weggefallen)“ | — |
| 11 | „der 1. Weihnachtsfeiertag“ | 주 전역 |
| 12 | „der 2. Weihnachtsfeiertag“ | 주 전역 |

- § 2 에는 지역 한정 항목이 없다. 한정 적용되는 공휴일은 **0건**이다.
- § 3 (1): „Die Sonntage und die staatlich anerkannten Feiertage sind Tage allgemeiner Arbeitsruhe.“
- [추론] Nr. 10 은 Buß- und Bettag 였을 가능성이 크다(위키백과의 „bis 1994“ 와 맞는다). 통합본에는 삭제 전 문구가 나오지 않는다.
- **공휴일이 아닌 항목:** § 2a „Gedenktage“ (2026년 신설, C 참조) 가 있다.
  - „der 8. Mai als Tag der Befreiung vom Nationalsozialismus …“
  - „der 17. Juni als Gedenktag für die Opfer des SED-Unrechts.“
  - § 3 (1) 이 Arbeitsruhe 를 일요일과 § 2 공휴일에만 부여한다. 따라서 Gedenktage 는 휴무일이 아니다. **피드 대상이 아니다(범위 밖).**
  - § 1 (1) 은 보호 대상을 „Sonntage, die staatlich anerkannten Feiertage, die Gedenktage und die religiösen Feiertage“ 로 나열한다. religiöse Feiertage 도 § 2 공휴일과 별개 범주다. [추론] 이 범주는 휴무일이 아니므로 범위 밖이다. 해당 조문 본문은 가져오지 않았다.

## C. 2020-01-01 이후 변경 / 1990년 이후 도입 / 단발 휴일

- **§ 2 공휴일 목록 자체의 2020년 이후 변경:** 관찰된 것이 없다.
  - 통합본에 나오는 마지막 개정(2026)은 §§ 1, 5 개정과 § 2a 신설이다. § 2 는 여기에 들어 있지 않다 (포털 기재 — gesetze.co 가 옮겨 적은 Stand-Vermerk 기준).
  - 개정 사슬은 검증하지 않았다. 비공식 페이지에 조문별 이력이 없어서 § 2 의 마지막 개정일은 확인하지 못했다.
- **§ 2a Gedenktage (8. Mai, 17. Juni)** 는 „Artikel 5 des Gesetzes vom 4. Mai 2026 (GVBl. LSA S. 178, 180)“ 로 신설되었다 (포털 기재).
  - 시행일은 확인하지 못했다.
  - 공휴일이 아니므로 피드와는 무관하다. 다만 레포의 `achter_mai_*`, `siebzehnter_juni_2028`(베를린 단발 공휴일)과 이름이 비슷해 혼동할 수 있으니 주의해야 한다.
- **1990년 이후 도입되어 2020년 이후에도 영향이 있는 항목:** 법 자체가 1990년 이후 제정되었다(현행 판은 2004년 공고본). 따라서 11개 항목 모두 형식상 1990년 이후의 법에 근거한다.
  - [추론] Heilige Drei Könige 와 Reformationstag 는 동독 지역 주에서 통일 후 도입된 항목이다. 2020년 이전부터 계속 적용되었으므로 2020년 이후 규칙 변경은 없다.
- **2020년 이후 단발 휴일:** 관찰된 것이 없다. 통합본 § 2 에 연도를 지정한 항목이 없고, 위키백과 표의 8. Mai 행 ST 칸도 비어 있다.

## D. 필요한 규칙 유형 (주 전역 11개)

| 항목 | 규칙 |
|---|---|
| Neujahrstag | (1) 고정 01-01 |
| Heilige Drei Könige | (1) 고정 01-06 |
| Karfreitag | (2) 부활절 −2 |
| Ostermontag | (2) 부활절 +1 |
| 1. Mai | (1) 고정 05-01 |
| Christi Himmelfahrt | (2) 부활절 +39 |
| Pfingstmontag | (2) 부활절 +50 |
| Tag der Deutschen Einheit | (1) 고정 10-03 |
| Reformationstag | (1) 고정 10-31 |
| 1. Weihnachtsfeiertag | (1) 고정 12-25 |
| 2. Weihnachtsfeiertag | (1) 고정 12-26 |

- **NEW 규칙 유형: 없음.** 2020년 이후 안에서 유효 시작일이나 종료일이 필요한 항목도 관찰되지 않았다.

## E. 키

| 항목 | 키 | 구분 |
|---|---|---|
| Neujahrstag | neujahr | 기존 재사용 |
| Heilige Drei Könige | heilige_drei_koenige | 기존 재사용 |
| Karfreitag | karfreitag | 기존 재사용 |
| Ostermontag | ostermontag | 기존 재사용 |
| 1. Mai | erster_mai | 기존 재사용 |
| Christi Himmelfahrt | christi_himmelfahrt | 기존 재사용 |
| Pfingstmontag | pfingstmontag | 기존 재사용 |
| Tag der Deutschen Einheit | tag_der_deutschen_einheit | 기존 재사용 |
| Reformationstag | reformationstag | 기존 재사용 |
| 1. Weihnachtsfeiertag | erster_weihnachtstag | 기존 재사용 |
| 2. Weihnachtsfeiertag | zweiter_weihnachtstag | 기존 재사용 |

- 사전 공지 키(mariae_himmelfahrt, buss_und_bettag)는 쓰지 않는다. **NEW 키: 없음.**

## F. 관보(GVBl. LSA) 접근성

- **공식 관보 포털: 무료 온라인 관보 포털은 관찰하지 못했다.**
  - 법무부 페이지(https://justiz.sachsen-anhalt.de/service/recht-und-gesetz/landesrecht, 200)에 따르면 GVBl. LSA 의 발행처는 Ministerium für Justiz und Verbraucherschutz 다.
  - 제작과 배포는 „Freyburger Buchdruckwerkstätte GmbH“ 가 맡는다. 안내 문구는 „Informationen zur Nutzung, Registrierung sowie zu den Preisen“ 이다.
  - 이 페이지에서 링크된 곳은 `landesrecht-sachsen-anhalt.info` 다. https:// 와 http://www. 로 한 번씩 시도했는데 둘 다 curl 000(연결 실패)이었다. DNS 는 83.221.235.179 로 해석되었고, 재시도하지 않았다.
  - [추론] 관보는 등록제·유료 배포로 보인다. 어느 연도가 PDF 로 공개되어 있는지는 확인하지 못했다.
- **landesrecht.sachsen-anhalt.de** (juris 포털)는 모든 경로가 JS 셸이었다. 관보 PDF 는 관찰하지 못했다.
- **PADOKA (Landtag):** https://padoka.landtag.sachsen-anhalt.de/ 는 200 이고 meta-refresh 로 `/portal/browse.tt.html` 로 넘어간다(200, 약 1.7 MB).
  - 검색 폼의 Dokumentart 선택지에 „Gesetz- und Verordnungsblatt“ 가 있다. 의회 문서 서버가 관보 사본을 보유한 것으로 보인다.
  - 정적 HTML 에는 PDF 링크가 없고(`Infodienst.pdf` 만 있음), 검색은 JS/폼 제출로 한다. 규칙에 따라 여기서 중단했다(API 역공학 안 함).
  - 페이지에 „Anmelden“ 링크가 있지만, 로그인 없이도 검색 UI 는 표시되었다.
- **검색 결과에 보인 것:** 제3자 사이트(st.kassenverwalter.de)에 GVBl 호 PDF 사본이 올라가 있다. 가져오지 않았다.
  - [추론] 공식 무료 딥링크 경로가 없어서 이런 사본이 떠도는 것으로 보인다.
- **최근 개정 관보 PDF 가져오기:** 대상은 GVBl. LSA 2026 S. 178이었지만 URL 을 찾지 못해 **시도하지 않았다**.
- 403/429 응답이나 레이트 리밋은 관찰되지 않았다.

## 요약

1. 주 전역 공휴일 11개 (§ 2 Nr. 1–9, 11–12. Nr. 10 은 „weggefallen“). 비공식 통합본 기준이며, 공식 포털은 JS 셸이다.
2. 한정 적용 공휴일은 0건이라 제외한 것이 없다. § 2a Gedenktage(8. Mai, 17. Juni, 2026 신설)는 휴무일이 아니라서 범위 밖이다.
3. NEW 규칙 유형: 없음 (고정일 7개, 부활절 오프셋 4개).
4. NEW 키: 없음 (11개 모두 기존 키를 재사용).
5. 관보 접근: 막힘/부분적. 공식 포털은 JS 셸, 관보는 출판사 등록제로 보이며 해당 사이트는 연결에 실패했다. PADOKA 는 JS 검색 폼뿐이고 PDF 는 확보하지 못했다.
