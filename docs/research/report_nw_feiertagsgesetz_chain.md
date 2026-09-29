사전 정리: `~/holidays-reports/report_ubuntu2604.md` 를 삭제했다. 삭제 전 `origin/main`(1fb06f6) 의 `docs/research/report_ubuntu2604.md` 와 `cmp` 로 바이트 동일을 확인했다.

# NW Feiertagsgesetz 개정 체인과 공포본 판독 — 조사 보고

- 작성: 2026-09-29. 조사만 했다. 레포 변경·브랜치·이슈·PR 은 없다.
- 기준 커밋: `main` = `1fb06f6` (#112 머지).
- 스크래치(이하 `$S`):
  `/private/tmp/claude-501/-Volumes-Data-dev-holidays/24975730-c66a-424c-9aac-edbbff0b4553/scratchpad/nw`
  - `pdf/`·`pdf2/`: 1·2 차 수령본
  - `scan/`: 체인 외 대조용 호
  - `png/`: 렌더
  - `ocr/`: OCR 교차 확인
  - `transcripts/`: 전사본
- 도구:
  - PyMuPDF 1.26.5, pikepdf 9.11.0 — 모두 `uv run --no-project --with …` 격리 실행이고 레포 의존이 아니다.
  - macOS Vision OCR(`$S/ocr.swift`, `VNRecognizeTextRequest`, accurate, de-DE, 언어 보정 끔).
  - `curl`, `shasum -a 256`.
  - poppler·tesseract·docker 는 이 머신에 없다.

---

## ⚠ 전제·기존 서술과 실물의 차이 (먼저 읽을 것)

1. **[선행 실측 2] HH 31. Oktober(#56) 는 파일 해시형이 아니다.** source 에 sha256 이 없다. URL 도 없고 「luewu.de PDF 2026-09-07 열람」 뿐이다. 파일 해시형 전례는 NI reformationstag 하나다. 아래 [E] 초안은 NI 형식을 따른다.
2. **[A]3 추론은 맞다.** 다만 Nr. 8 을 바꾼 호는 전제가 가정한 1994 가 아니라 **1991 S. 200** 이다.
   - recht.nrw.de 현행판의 § 2 각주는 이 개정을 빠뜨렸다. § 2 는 1994 만, 1991 은 § 5 만 적는다.
   - 그래서 포털 각주만 보면 체인을 잘못 세우게 된다.
3. **YAML 머리 주석의 막힘 사유 둘이 지금은 사실이 아니다.** 부수 관찰 1·2 에 적었다.
   - 관보 PDF 에 OCR 텍스트층이 있다.
   - recht.nrw.de 의 법령 면은 서버 렌더되어 딥링크가 된다.
4. **공포본 자구가 lexmea 와 두 호에서 다르다.**
   - Nr. 5: 공포본 `Christi-Himmelfahrtstag`, lexmea `Christi-Himmelfahrts-Tag`. **SUMMARY 가 바뀐다.**
   - Nr. 4: 1989 공포본의 인쇄는 `Gerichtigkeit` 다. SUMMARY `1. Mai` 에는 영향이 없다.

---

## 0. 선행 실측

### 0-1. rules/de_nw — [실측] 전제와 같음

`uv run python` 으로 두 YAML 을 읽었다.
- 11 건: easter 5 + solar 6.
- verified 11/11 이 `False` 다.
- source_todo 11/11 이 「GV. NW 1989 S. 222」를 포함한다.
- key 순서와 name:

| key | name |
|---|---|
| karfreitag | Karfreitag |
| ostermontag | Ostermontag |
| christi_himmelfahrt | Christi-Himmelfahrts-Tag |
| pfingstmontag | Pfingstmontag |
| fronleichnam | Fronleichnamstag |
| neujahr | Neujahrstag |
| erster_mai | 1. Mai |
| tag_der_deutschen_einheit | Tag der Deutschen Einheit |
| allerheiligen | Allerheiligentag |
| erster_weihnachtstag | 1. Weihnachtstag |
| zweiter_weihnachtstag | 2. Weihnachtstag |

### 0-2. 승격 전례의 서지 형식 — [실측]

**(가) HH `reformationstag`** (`rules/de_hh/solar_holidays.yaml`, #56). 구성 요소는 다음과 같다.
1. 법·조·호: `Feiertagsgesetz(HH) § 1 Nr. 8`
2. 조문 인용: `'31. Oktober'`, 통칭 괄호
3. 공포 법률명·일자: `Fünftes Gesetz … vom 12.03.2018`
4. 관보 호·면: `HmbGVBl. 2018 Nr. 9 S. 63`
5. 괄호 안: 공포일, 열람 출처(`luewu.de PDF`), 열람일
6. 날짜 대조: feiertage-api 2026

**URL·sha256 없음** — 위 ⚠1.

**(나) NI `reformationstag`** — 파일 해시형. 구성 요소는 다음과 같다.
1. 법·조·호: `NFeiertagsG § 2 Abs. 1 Buchst. h`
2. 조문 인용
3. 공포 법률명·일자·조항: `… vom 22.06.2018 Art. 1 Nr. 1`
4. 괄호: 개정 내용 요약(삽입·재번호·삭제)
5. 관보: `Nds. GVBl. 2018 Nr. 7 S. 122`
6. 괄호 안:
   - 공포일, 시행일
   - 포털 PDF 직접 URL
   - `sha256 <64hex>`
   - 열람일
   - `재수령 대조 일치`
   - Wayback 사본 동일 sha256
7. SUMMARY 정리 서술
8. 날짜 대조

**(다) rules/de `tag_der_deutschen_einheit`** (#110) — 이미지 스트림 해시형. 구성 요소는 다음과 같다.
1. 법·조: `Einigungsvertrag Art. 2 Abs. 2`
2. 조문 인용: 문장 전체
3. 조약 일자, 관보(`BGBl. 1990 II Nr. 35 S. 889`), 인용 면(`Art. 2 는 S. 890`)
4. 괄호 안:
   - 공포일
   - bgbl.de 문서 식별자·URL, Wayback 사본 URL
   - `파일 sha256 은 요청마다 달라 적지 않고 S. 890 이미지 스트림 sha256 <64hex> 을 적는다 — 정의는 이 파일 머리 주석`
   - 열람일
5. `스캔 판독 자구 일치, Art. 2 무개정`

해시의 정의·재현 명령은 `rules/de/solar_holidays.yaml` 머리 주석 L46–L54 에 있다. 정의는 "복호화 후 /Filter 를 풀지 않은 이미지 XObject 스트림 바이트의 sha256" 이다.

### 0-3. SUMMARY 규약 — [실측]

`rules/de_nw/solar_holidays.yaml` 머리 주석 「--- name ---」 절(발췌 복사):

> "SUMMARY 에 그대로 실린다. § 2 Abs. 1 의 조문 표기(lexmea)에서 정관사 der 와 서술부·괄호를 뺀 것이다"

같은 절에 적용례가 이어진다: Nr. 4 → "1. Mai", Nr. 8 → "Tag der Deutschen Einheit", Nr. 9 → "Allerheiligentag".
`easter_holidays.yaml` 머리 주석은 Nr. 5 를 "Christi-Himmelfahrts-Tag"(하이픈, 조문 그대로)로 적는다.

**규약의 기준 텍스트가 「(lexmea)」로 박혀 있다.** 공포본으로 승격하면 이 괄호도 바뀐다.

---

## [A] 개정 체인

### A1. 1989 S. 222 의 성격 — [실측] **Neufassung 공고(신규 공포)다**

GV. NW. 1989 Nr. 19 (Ausgegeben 9. Mai 1989) S. 222. 표제는 「Bekanntmachung der Neufassung des Gesetzes über die Sonn- und Feiertage」, 「Vom 23. April 1989」.
- 근거: 1 쪽 목차와 2 쪽 표제(`$S/pdf/1989-19.pdf`). 인용면 렌더는 `$S/png/1989_S222_full.png`.
- 서두의 수권 근거는 GV. NW. 1989 S. 90 의 Art. II 다. 1977 년 공고본(GV. NW. S. 98)에 1984·1989 개정을 반영한 Wortlaut 를 공고한다.
- 복사 인용:
  > "Der Innenminister wird ermächtigt, das Gesetz über die Sonn- und Feiertage in der neuen Fassung"

  출처: GV. NW. 1989 Nr. 9 S. 90 Art. II, OCR 층. `$S/scan/1989-9.pdf` sha256 `3a719ef8…eadf`.
- § 14 각주(S. 224):
  > "Die vom Inkrafttreten bis zum Zeitpunkt der Neubekanntmachung eingetretenen Änderungen ergeben"
- 전제대로 1989 이전은 거슬러 올라가지 않는다. 예외는 Nr. 4·5 의 자구 판단을 위해 1977 공고본(S. 98) 한 면을 보조로만 본 것이다(C3).

### A2. 1989 이후 § 2 에 닿은 개정 — [실측] **두 호**

| # | 법률 | 공포(관보 표기) | GV. NW. 면 | § 2 변경 | 기타 |
|---|---|---|---|---|---|
| 1 | Gesetz zur Änderung des Feiertagsgesetzes NW vom 17. April 1991 | Nr. 19, Ausgegeben 3. Mai 1991 | **1991 S. 200** | Art. I Nr. 1: **§ 2 Abs. 1 Nr. 8 신규 문언** "der 3. Oktober als Tag der Deutschen Einheit," | Nr. 2 § 5 Abs. 1 Satz 2, Nr. 3 § 6 Abs. 1 에서 17. Juni 삭제. Art. II 공포 익일 시행 |
| 2 | Zweites Gesetz zur Änderung des Feiertagsgesetzes Nordrhein-Westfalen vom 20. Dezember 1994 | Nr. 88, Ausgegeben 30. Dezember 1994 | **1994 S. 1114** | Art. I Nr. 1: **§ 2 Abs. 1 Nr. 10(Buß- und Bettag) 삭제, Nr. 11·12 → 10·11** | Nr. 2 § 6 Abs. 1 에서 Buß- und Bettag 삭제. Art. II 공포 익일 시행 |

**목록을 세운 출처**

1. recht.nrw.de 현행판 「Änderungshistorie」
   - 법령 면(아래)과 검색 색인 문서 `entity:node/125179` 에 같은 문자열이 있다.
   - 복사 인용:
     > "geändert durch Gesetz v. 17. 4. 1991 (GV. NW. S. 200), 20. 12. 1994"
   - 법령 면: https://recht.nrw.de/lrgv/gesetz/01012000-bekanntmachung-der-neufassung-des-gesetzes-ueber-die-sonn-und-feiertage/ — 「Fassungen vom 01.01.2000 (aktuelle Seite)」가 유일한 판이다.
2. 공포본의 자기 서술로 구간을 닫았다(아래 「빠짐없음의 근거」).

**빠짐없음의 근거**

| 구간 | 닫는 근거 | 성격 |
|---|---|---|
| 1989-04-23 → 1991-04-17 | 1991 S. 200 서두: 1989 공고본을 개정 없이 인용 ("Bekanntmachung vom 23. April 1989 (GV. NW. S. 222) wird wie folgt geändert") | 공포본 [실측] |
| 1991 → 1994-12-20 | 1994 S. 1114 서두: `geändert durch Gesetz vom 17. April 1991 (GV. NW. S. 200)` — 하나뿐 | 공포본 [실측] |
| 1994 → 2006 | GV. NRW. 2006 S. 516 (LÖG NRW) § 1: `zuletzt geändert durch Gesetz vom 20. Dezember 1994 ( GV. NRW. S. 1114 )` | 공포본 텍스트 [실측] |
| 2006 → 2015-06-25 | GV. NRW. 2015 S. 496 § 1: `zuletzt durch Gesetz vom 20. Dezember 1994 ( GV. NRW. S. 1114 ) geändert` | 공포본 텍스트 [실측] |
| 2015 → 2026 Nr. 27 | 자기 서술 없음. (a) 포털 현행판이 1994 에서 끝남, (b) 전문 색인 전수 검색 무적중 | 포털·색인 [실측] + 완전성 [추론] |

2006·2015 의 두 인용은 recht.nrw.de 검색 색인의 공포 문서 원문 필드(`field_normtext_processed`)에서 읽었다. 문서 URL: `/gvnrw/2006-s516`, `/gvnrw/2015-s496`. 두 호의 PDF 는 받지 않았다(미확인).

**2015 → 2026 검색의 방법**

- recht.nrw.de 공개 검색 미들웨어를 썼다. 포털 SPA 가 쓰는 공개 엔드포인트다.
  - `POST https://recht.nrw.de/search-middleware/opensearch_internet/_search`
  - 인증·우회 없음.
- 대상: `law_and_ordinance_gazette`(공포 문서 단위 전문, 1997–2026, 7,049 건)와 `state_law_and_regulations`(현행판).
- 구문 검색어와 결과:
  - `Feiertagsgesetz`·`Feiertagsgesetzes`·`Gesetzes über die Sonn- und Feiertage`·`Gesetz über die Sonn- und Feiertage`·`Feiertagsgesetz NW`·`Feiertagsgesetzes NW`·`Feiertagsgesetz NRW`·`GV. NRW. S. 1114`·`GV. NW. S. 1114`
  - 공포 문서 적중은 모두 **인용하는 법령**이다. 1998 S. 148, 1998 S. 240, 1998 S. 381, 2001 S. 262, 2002 S. 334, 2006 S. 516, 2012 S. 524, 2013 S. 138, 2013 S. 208, 2015 S. 496, 2020 S. 40, 2022 S. 574, 2023 S. 350. 2026 S. 189 는 다른 법의 S. 1114 를 가리켜 무관하다.
  - 제목에 `*feiertag*` 가 든 공포 문서는 1998 S. 381, 2005 S. 836(Landtag 의 Bekanntmachung, Videotheken), 2015 S. 496 뿐이다.
  - 제목이 「…Änderung des Feiertagsgesetzes…」인 1995 년 이후 문서는 0 건이다.
- 색인 완전성 대조: 1998–2026 의 호(`gazette_gv_nrw`, 호 단위 목록) 마다 공포 문서가 1 건 이상 색인되어 있는지 셌다.
  - 빠진 호는 **1998 Nr. 3**, **2021 Nr. 75a**(18.05.2021, 호 면에 PDF·문서 모두 없음) 둘이다.
  - 1998 Nr. 3 은 2006 자기 서술 구간 안이다.
  - **2021 Nr. 75a 는 미확인 공백이다.**
  - 1995·1996 은 문서 단위 색인이 없다(호 PDF 만). 이 구간은 2006 자기 서술로 닫힌다.

[추론] HH 전례(공포본 체인을 2026 Nr. 26 까지 호별로 스캔해 무개정)와 비교하면:
- 2015 년까지는 이 레포 전례보다 강한 근거로 닫힌다. 공포본 자기 서술 둘이다.
- 2015 → 2026 은 전문 색인 전수 검색으로 닫는다. 호별 목차 판독은 아니다.
- 색인이 호 단위로 빠짐없음을 확인했고 공백은 2021 Nr. 75a 하나다. 그래서 RP 전례의 「2004~2026 전 호 스캔」과 동급으로 볼 수 있다고 판단한다. 다만 이 판단은 사람이 한다.

### A3. 17. Juni 추론 — [실측] **확인**

- 1989 S. 222 § 2 Abs. 1 Nr. 8 은 `der 17. Juni als Tag der deutschen Einheit,` 다. 소문자 d 이고, 호 수는 12 다.
  - 렌더: `$S/png/1989_S222_par2abs1.png`
  - 전사: `$S/transcripts/1989_S222_par2.txt`
- 1991 S. 200 Art. I Nr. 1 이 Nr. 8 을 `„der 3. Oktober als Tag der Deutschen Einheit,"` 로 바꿨다(대문자 D).
  - 렌더: `$S/png/1991_S200_top.png`
  - 전사: `$S/transcripts/1991_S200_artI.txt`
- 1977 공고본(S. 98)도 Nr. 8 이 17. Juni 다.

### A4. 마지막 개정 이후 무변경 — [실측] + [추론]

- 마지막 § 2 개정은 1994 S. 1114 다.
- 이후 무변경은 A2 표의 셋째~다섯째 행으로 닫힌다.
  - 공식 문서의 자기 서술이 2015-06-25 까지 닿는다.
  - 2015 → 2026 은 포털 현행판과 색인 전수 검색이다.
- HH 처럼 「2026 Nr. 27 (공포 2026-09-2x) 까지 무개정」으로 적을 수 있다. 조건은 두 가지다.
  - 2021 Nr. 75a 공백을 받아들이는가.
  - 색인 검색을 호별 스캔과 동급으로 인정하는가.

  둘 다 사람 판단이다.

---

## [B] 취득과 고정

수령일은 2026-09-29(UTC 02:3x) 다. 각 호 URL 은 호 면(`https://recht.nrw.de/gvnrw/<연도>-<호>` → 301 → 끝 슬래시)의 「PDF-Version herunterladen」 링크에서 얻었다.

| 호 | 직접 URL | curl | 1 차 sha256 | 2 차 | Wayback |
|---|---|---|---|---|---|
| 1989 Nr. 19 (S. 221–224) | https://recht.nrw.de/system/files/GV_Archiv/4122-xmmgvb8919.pdf | 200, 163,255 B, application/pdf | `b72dd60b57c8b59139d27313e193f13d0b0fd06fce4da727749dd9a58b780a49` | 동일 | 20260206163943·20260710201428 두 사본 모두 동일 sha256. CDX digest `SAYDN34NPAYHDDA7IK6AQIAYVEDCEI3V` = 라이브 sha1 base32 |
| 1991 Nr. 19 (S. 197–200) | https://recht.nrw.de/system/files/GV_Archiv/3762-xmmgvb9119.pdf | 200, 357,687 B | `4c7dd3aad931ce0b5906db48681a0cdfb6cb425a1964a8a970c14a683aa2dbc5` | 동일 | CDX 없음 |
| 1994 Nr. 88 (S. 1111–1118) | https://recht.nrw.de/system/files/GV_Archiv/4383-xmmgvb9488.pdf | 200, 400,477 B | `329fd81bb58b2e9a0cb17d8e0d7df3e28ffe0de35b175648fce282359ab823f8` | 동일 | CDX 없음 |

같은 날 받은 인접 호 5 개(1991 Nr. 18, 1994 Nr. 84–87)도 2 회 수령 sha256 이 모두 같았다.

**판정: 결정적이다.**
- 정적 파일이다(`cache-control: … max-age=2592000`).
- 1989 판은 7 개월 간격 Wayback 사본까지 같다.
- 따라서 **파일 sha256 형식(NI 전례)의 후보**다. #110 의 이미지 스트림 해시는 필요하지 않다.

보조로 #110 정의(pikepdf `read_raw_bytes()`, 필터 미해제)의 인용 면 이미지 스트림 sha256 도 적어 둔다. 세 파일 모두 비암호화이고 JBIG2Globals 가 없어 스트림이 자기 완결이다. 2 차 수령본에서도 같은 값이 나왔다.

```
pdf/1989-19.pdf page 2 /Im0 obj(50, 0) /JBIG2Decode 1653x2339 45690B sha256=c31bc22ab8adf102113d1400cd4aaf55358e940350248f5449ad8074eab65fc3
pdf/1991-19.pdf page 4 /Im0 obj(43, 0) /JBIG2Decode 1657x2342 26935B sha256=6f794e525931dd437fa7eabf105cd941ec690d3f37949ee1f7ceeedcb66f76b8
pdf/1994-88.pdf page 4 /I3 obj(11, 0) /CCITTFaxDecode 1648x2292 47486B sha256=b7d8ea4bc5f475320e9360092c3fcf366c85a87b109701f1c385c2ec10209901
```

재현: `cd $S && uv run -q --no-project --with pikepdf==9.11.0 python hash_images.py`. 출력은 `$S/hash_images.txt`.

파일 구조:
- 1989·1991: PDF 1.6/1.4, 「Adobe Acrobat 9.0 Paper Capture Plug-in」, JBIG2, **OCR 텍스트층 있음**(1989 S. 222 면 5,574 자).
- 1994: PDFlib+PDI 6.0.0p1, CCITT G4, 텍스트층 없음.
- 해상도는 모두 약 200 dpi, 1-bit.

---

## [C] 판독

### C1. 렌더·전사 — [실측]

| 인용 면 | 렌더 PNG | 전사본 |
|---|---|---|
| 1989 S. 222 § 2 (Abs. 1 전체) | `$S/png/1989_S222_par2abs1.png` (300 dpi 크롭), 원본 비트맵 `$S/png/1989_S222_full.png` | `$S/transcripts/1989_S222_par2.txt` |
| 1991 S. 200 Art. I–II | `$S/png/1991_S200_top.png` (150 dpi), `$S/png/1991_S200_artI.png` (400 dpi), 원본 `$S/png/1991_S200_full.png` | `$S/transcripts/1991_S200_artI.txt` |
| 1994 S. 1114 표제~Art. II | `$S/png/1994_nr88_p4_bottom.png`(좌단: 표제·서두 앞), `$S/png/1994_nr88_p4_top.png`(우단: 서두 계속·Art. I·II), 400 dpi `$S/png/1994_S1114_artI.png`, 원본 `$S/png/1994_nr88_p4_full.png` | `$S/transcripts/1994_S1114_artI.txt` |
| 1994 Nr. 88 목차 | `$S/png/1994_nr88_p1_top.png` (「Zweites Gesetz zur Änderung des Feiertagsgesetzes Nordrhein-Westfalen … 1114」) | — |
| (보조) 1977 S. 98 § 2 Abs. 1 | `$S/png/1977_S98_q10.png` | `$S/transcripts/1977_S98_par2abs1.txt` |
| 체인 적용 현행 자구 | — | `$S/transcripts/current_par2abs1_by_chain.txt` |

### C2. OCR 교차 확인 — [실측]

- **1989 S. 222 § 2 Abs. 1** — 두 OCR 모두 전사와 **글자 단위로 같다**. `Gerichtigkeit`·`Christi-Himmelfahrtstag` 을 포함한다.
  - Vision: `$S/png/1989_S222_par2abs1.png`
  - Acrobat OCR 층: `$S/ocr/1989_S222_ocrlayer.txt`. 이 층은 좌우단이 섞여 "§2 Feiertage" 가 Nr. 3 뒤에 끼는데, 배치 문제일 뿐 자구 차이는 없다.
  - Acrobat 층의 차이는 조문 밖(서두)에만 있다: `Artikels 11`(원문 II), `~L 19`(원문 Nr. 19).
- **1991 S. 200** — Vision(`$S/ocr/1991_S200_artI_vision.txt`)이 Art. I 전문을 전사와 같게 읽었다. 행 끝 몇 글자가 빠진 것(`da`, `folg`, `de`)은 크롭 경계 때문이다. Acrobat 층(`$S/ocr/1991_nr19_p4_ocrlayer.txt`)도 Nr. 1 문언이 같고, 서명자를 `Schaor` 로 읽었다(원문 Schoor).
- **1994 S. 1114** — 텍스트층이 없어 Vision 만 썼다. 차이는 모두 OCR 오인식이다.
  - 150 dpi 전면(`…_top_vision.txt`)은 Art. I Nr. 1–2 를 판독 불능 문자열로 냈다.
  - 400 dpi 크롭(`$S/ocr/1994_S1114_artI_vision.txt`)의 차이: `I.`(원문 `1.`), `I1`(원문 `11`), `Abs. I`(원문 `Abs. 1`).
  - 표제 크롭(`…_title_vision.txt`)의 차이: `Anderung`/`Felertagsgesetzes`(원문 Änderung/Feiertagsgesetzes).
  - 육안 판독이 정본이다.

### C3. 현행 자구와 lexmea 대조, IHK 차이 판정 — [실측]

lexmea 는 JS 앱이라 curl 로 본문을 받지 못했다(`lexmea.de/de/gesetz/feiertagsgesetz-nw` 는 200 이지만 본문 없음). 대조 대상 lexmea 자구는 YAML 머리 주석에 기록된 것을 썼다(「Imported 21.10.2025」). recht.nrw.de 현행판 본문(색인 `field_body_field_text_processed`)도 같이 적는다. 두 비공식 자구는 서로 같다.

| Nr. | 체인 적용 공포본 자구 (근거 호) | lexmea | 일치 |
|---|---|---|---|
| 1 | der Neujahrstag, (1989) | 동일 | ○ |
| 2 | der Karfreitag, (1989) | 동일 | ○ |
| 3 | der Ostermontag, (1989) | 동일 | ○ |
| 4 | der 1. Mai als Tag des Bekenntnisses … sozialer **Gerichtigkeit**, Völkerversöhnung … (1989) | … sozialer **Gerechtigkeit** … | **✕ (1 자)** |
| 5 | der **Christi-Himmelfahrtstag**, (1989) | der **Christi-Himmelfahrts-Tag** | **✕** |
| 6 | der Pfingstmontag, (1989) | 동일 | ○ |
| 7 | der Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis), (1989) | 동일 | ○ |
| 8 | der 3. Oktober als Tag der Deutschen Einheit, (1991 S. 200) | 동일 | ○ |
| 9 | der Allerheiligentag (1. November), (1989) | 동일 | ○ |
| 10 | der 1. Weihnachtstag, (1989 Nr. 11 → 1994 재번호) | 동일 | ○ |
| 11 | der 2. Weihnachtstag. (1989 Nr. 12 → 1994 재번호) | 동일 | ○ |

**IHK Köln 과의 차이 판정 — 모두 lexmea 쪽이 공포본이다.**
- Nr. 7: 괄호 정의가 있다(1989 S. 222).
- Nr. 8: 어순은 「der 3. Oktober als Tag der Deutschen Einheit」, 대문자 D, 괄호 없음(1991 S. 200 Art. I Nr. 1 의 새 문언 그대로).
- Nr. 10·11: 괄호 날짜가 없다(1989 S. 222 Nr. 11·12).

**lexmea 가 틀린 두 호**
- **Nr. 5** — 공포본 1977 S. 98 과 1989 S. 222 가 모두 `Christi-Himmelfahrtstag` 다. 이후 개정은 Nr. 5 를 건드리지 않았다. 하이픈 `-Tag` 는 lexmea·IHK·recht.nrw.de 현행판 등 비공식 셋에만 있다.
  - [추론] 1977 이전 원 제정(1961)에서 왔거나 현행판 편집에서 생긴 것이다. 확인하지 않았다.
- **Nr. 4** — 1989 공고본의 인쇄는 `Gerichtigkeit` 다. 1977 공고본은 `Gerechtigkeit` 다. 1989 S. 90 개정은 § 2 를 건드리지 않았다(조문 목록 § 4·5·6·7·10, `$S/scan/1989-9.pdf` OCR 층).
  - 1989 Nr. 20–69 의 OCR 층을 검색했다. S. 222 의 Berichtigung 은 없다. 텍스트층이 없는 Nr. 56·64 는 목차를 보았고 무관하다.
  - [추론] Neubekanntmachung 은 선언적이라 공고의 오식이 법문을 바꾸지 않는다. 법적으로 유효한 자구는 `Gerechtigkeit` 로 볼 공산이 크다. 공포본 인용을 그대로 옮길지(`[sic]` 표기), 1977 자구로 적을지는 판단 요청이다.
  - 1990 년 이후의 Berichtigung 은 보지 않았다(미확인).

---

## [D] 항목별 판정표

공통 사항:
- 「근거 호」의 체인 폐쇄는 A2·A4 를 따른다. 2015 년까지는 공포본 자기 서술, 이후는 색인 검색이다.
- 모든 항목의 호 번호 체계는 1994 재번호 뒤의 것이다. 그래서 1994 S. 1114 가 11 건 모두의 번호 근거가 된다.
- SUMMARY 규약(der·서술부·괄호 제외)을 공포본에 적용했을 때 **지금 name 과 달라지는 것은 christi_himmelfahrt 하나**다.

| key | 근거 호(연도·면) | 공포본 자구 | lexmea 일치 | verified 전망 | 이유 |
|---|---|---|---|---|---|
| allerheiligen | 1989 S. 222 (Nr. 9) | der Allerheiligentag (1. November), | ○ | true 가능 | 자구 일치, SUMMARY `Allerheiligentag` 그대로 |
| christi_himmelfahrt | 1989 S. 222 (Nr. 5) | der Christi-Himmelfahrtstag, | **✕** | true 가능 — **SUMMARY 변경** | 공포본 자구로 name 이 `Christi-Himmelfahrts-Tag` → **`Christi-Himmelfahrtstag`**. 1977 공고본도 같은 표기. easter_holidays.yaml 머리 주석의 Nr. 5 서술도 바뀐다 |
| erster_mai | 1989 S. 222 (Nr. 4) | der 1. Mai als Tag des Bekenntnisses … sozialer Gerichtigkeit … | **✕ (1 자)** | true 가능 — source 인용 방식 판단 필요 | SUMMARY `1. Mai` 불변. 공포본 인쇄 오식을 source 인용에 어떻게 적을지만 남는다(C3) |
| erster_weihnachtstag | 1989 S. 222 (Nr. 11) + 1994 S. 1114 (→ Nr. 10) | der 1. Weihnachtstag, | ○ | true 가능 | 괄호 날짜 없음(IHK 기각) |
| fronleichnam | 1989 S. 222 (Nr. 7) | der Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis), | ○ | true 가능 | 괄호 정의 있음(IHK 기각). 날짜 등가 서술은 이번에 다시 보지 않음 |
| karfreitag | 1989 S. 222 (Nr. 2) | der Karfreitag, | ○ | true 가능 | 자구 일치 |
| neujahr | 1989 S. 222 (Nr. 1) | der Neujahrstag, | ○ | true 가능 | 자구 일치 |
| ostermontag | 1989 S. 222 (Nr. 3) | der Ostermontag, | ○ | true 가능 | 자구 일치 |
| pfingstmontag | 1989 S. 222 (Nr. 6) | der Pfingstmontag, | ○ | true 가능 | 자구 일치 |
| tag_der_deutschen_einheit | **1991 S. 200** (Art. I Nr. 1, Nr. 8 신규 문언) | der 3. Oktober als Tag der Deutschen Einheit, | ○ | true 가능 | 1989 판은 17. Juni. IHK 어순·소문자 기각 |
| zweiter_weihnachtstag | 1989 S. 222 (Nr. 12) + 1994 S. 1114 (→ Nr. 11) | der 2. Weihnachtstag. | ○ | true 가능 | 괄호 날짜 없음(IHK 기각) |

**true 가능: 11/11.** 공통 조건은 A4 의 두 사람 판단이다(2015 → 2026 을 색인 검색으로 닫는 것, 2021 Nr. 75a 공백). 거기에 christi_himmelfahrt 의 SUMMARY 변경 수용과 erster_mai 의 인용 방식이 더해진다.

---

## [E] 서지 문자열 초안 (NI 파일 해시형을 따름, 레포 미적용)

해시가 길어 세 호를 머리 주석에 한 번 정의하고 항목 source 는 짧게 가리키는 안(E0)과, NI 처럼 항목마다 전부 적는 안(E1)을 함께 적는다. 어느 쪽인지는 판단 요청이다.

### E0. 머리 주석 공통 블록 초안

```
# --- 공포본 (recht.nrw.de GV_Archiv PDF, 2026-09-29 열람, 재수령 대조 일치) ---
#   [1989] Bekanntmachung der Neufassung des Gesetzes über die Sonn- und Feiertage vom 23.04.1989,
#          GV. NW. 1989 Nr. 19 S. 222 (09.05.1989 공포)
#          https://recht.nrw.de/system/files/GV_Archiv/4122-xmmgvb8919.pdf
#          sha256 b72dd60b57c8b59139d27313e193f13d0b0fd06fce4da727749dd9a58b780a49
#          (Wayback 20260206·20260710 사본도 같은 sha256)
#   [1991] Gesetz zur Änderung des Feiertagsgesetzes NW vom 17.04.1991 Art. I Nr. 1 (§ 2 Abs. 1 Nr. 8 신규 문언),
#          GV. NW. 1991 Nr. 19 S. 200 (03.05.1991 공포)
#          https://recht.nrw.de/system/files/GV_Archiv/3762-xmmgvb9119.pdf
#          sha256 4c7dd3aad931ce0b5906db48681a0cdfb6cb425a1964a8a970c14a683aa2dbc5
#   [1994] Zweites Gesetz zur Änderung des Feiertagsgesetzes Nordrhein-Westfalen vom 20.12.1994 Art. I Nr. 1
#          (§ 2 Abs. 1 Nr. 10 삭제, Nr. 11·12 → 10·11), GV. NW. 1994 Nr. 88 S. 1114 (30.12.1994 공포)
#          https://recht.nrw.de/system/files/GV_Archiv/4383-xmmgvb9488.pdf
#          sha256 329fd81bb58b2e9a0cb17d8e0d7df3e28ffe0de35b175648fce282359ab823f8
# 1994 이후 무개정: GV. NRW. 2006 S. 516 § 1·2015 S. 496 § 1 의 "zuletzt geändert … 20. Dezember 1994"
# 인용, 2015 → 2026 Nr. 27 은 recht.nrw.de 공포 문서 전문 색인 검색(무적중).
```

### E1. 항목별 source 초안 (NI 형식 전부 기재, 대표 3 건 + 나머지 패턴)

- **karfreitag**(1989 근거의 대표형; neujahr·ostermontag·pfingstmontag·allerheiligen·fronleichnam 동형):
  `Feiertagsgesetz NW § 2 Abs. 1 Nr. 2 'der Karfreitag' — Bekanntmachung der Neufassung des Gesetzes über die Sonn- und Feiertage vom 23.04.1989, GV. NW. 1989 Nr. 19 S. 222 (09.05.1989 공포; recht.nrw.de PDF https://recht.nrw.de/system/files/GV_Archiv/4122-xmmgvb8919.pdf sha256 b72dd60b57c8b59139d27313e193f13d0b0fd06fce4da727749dd9a58b780a49, 2026-09-29 열람, 재수령 대조 일치; Wayback 20260206·20260710 사본도 같은 sha256). 호 번호는 1994 재번호 뒤 체계(GV. NW. 1994 S. 1114 Art. I Nr. 1), 1994 이후 무개정은 머리 주석. 부활절 −2 일은 feiertage-api 2026 NW(04-03) 대조 일치`
  - fronleichnam 은 인용이 `'der Fronleichnamstag (Donnerstag nach dem Sonntag Trinitatis)'` 이고, SUMMARY 정리 서술과 기존 등가 서술을 유지한다.
  - allerheiligen 은 `'der Allerheiligentag (1. November)'` + SUMMARY 괄호 제외 서술.
- **tag_der_deutschen_einheit**(1991 근거):
  `Feiertagsgesetz NW § 2 Abs. 1 Nr. 8 'der 3. Oktober als Tag der Deutschen Einheit' — Gesetz zur Änderung des Feiertagsgesetzes NW vom 17.04.1991 Art. I Nr. 1 (Nr. 8 신규 문언, 구 문언 'der 17. Juni als Tag der deutschen Einheit'), GV. NW. 1991 Nr. 19 S. 200 (03.05.1991 공포, 04.05.1991 시행; recht.nrw.de PDF https://recht.nrw.de/system/files/GV_Archiv/3762-xmmgvb9119.pdf sha256 4c7dd3aad931ce0b5906db48681a0cdfb6cb425a1964a8a970c14a683aa2dbc5, 2026-09-29 열람, 재수령 대조 일치). SUMMARY 는 서술부만 남긴 'Tag der Deutschen Einheit'. 날짜 3. 10. 은 feiertage-api 2026 NW 대조 일치`
- **erster_weihnachtstag**(1989 + 1994 근거; zweiter_weihnachtstag 동형):
  `Feiertagsgesetz NW § 2 Abs. 1 Nr. 10 'der 1. Weihnachtstag' — GV. NW. 1989 Nr. 19 S. 222 의 Nr. 11 (… 1989 PDF·sha256 …) 을 Zweites Gesetz zur Änderung des Feiertagsgesetzes Nordrhein-Westfalen vom 20.12.1994 Art. I Nr. 1 이 Nr. 10 으로 재번호, GV. NW. 1994 Nr. 88 S. 1114 (30.12.1994 공포; recht.nrw.de PDF https://recht.nrw.de/system/files/GV_Archiv/4383-xmmgvb9488.pdf sha256 329fd81bb58b2e9a0cb17d8e0d7df3e28ffe0de35b175648fce282359ab823f8, 2026-09-29 열람, 재수령 대조 일치). 날짜 25. 12. 은 feiertage-api 2026 NW 대조 일치`
- **christi_himmelfahrt**: 인용 `'der Christi-Himmelfahrtstag'` + `SUMMARY 는 공포본 표기 'Christi-Himmelfahrtstag'(lexmea·IHK·recht.nrw.de 현행판의 'Christi-Himmelfahrts-Tag' 는 공포본 1977 S. 98·1989 S. 222 어디에도 없다)`.
- **erster_mai**: 인용안 둘.
  - (i) 조문 전체를 인용하되 `Gerichtigkeit [sic]` 로 표기(전문은 `$S/transcripts/1989_S222_par2.txt`)
  - (ii) 서술부를 생략한 `'der 1. Mai als Tag des Bekenntnisses …'` + 오식 주석.

---

## 부수 관찰

1. **관보 PDF 에 텍스트층이 있다(1989·1991).** YAML·`rules/de_nw/__init__.py` 의 「JBIG2 스캔이라 텍스트 미추출」과 다르다. 이미지는 JBIG2 가 맞지만 Acrobat Paper Capture 의 OCR 층이 있다(PyMuPDF `get_text()`). 1994 판은 CCITT G4 에 텍스트층이 없다. 판독 근거는 이번에도 이미지다.
2. **recht.nrw.de 법령 면이 서버 렌더되어 딥링크가 된다.** 주소는 `/lrgv/gesetz/01012000-bekanntmachung-der-neufassung-des-gesetzes-ueber-die-sonn-und-feiertage/` 이고, 「Änderungshistorie」와 「Fassungen」이 HTML 에 있다. 호 면(`/gvnrw/<연도>-<호>`)도 PDF 링크를 HTML 로 준다. 검색 화면만 SPA(`/suche/vbl`)다. 포털이 개편된 것으로 보인다 — [추론], CSS 경로 `2025-10`.
3. **포털 현행판 각주의 결함.** § 2 의 개별 각주가 1991 S. 200 을 빠뜨렸다(§ 5 각주에만 있다). 현행판 본문은 Nr. 4 `Gerechtigkeit`, Nr. 5 `Christi-Himmelfahrts-Tag` 로 1989 공포본과 다르다.
4. **색인의 공포일이 관보 표기와 하루씩 어긋나는 호가 있다.** 1991 Nr. 19 는 색인 1991-05-04 / 관보 「3. Mai 1991」, 1994 Nr. 88 은 색인 1994-12-31 / 관보 「30. Dezember 1994」다. source 에는 관보 표기를 쓴다.
5. **일회성 공휴일이 있었다.** GV. NRW. 2015 S. 496 「Gesetz über die Bestimmung des 31. Oktober 2017 als 500. Jahrestag der Reformation zum Feiertag in Nordrhein-Westfalen」 § 1:
   > "Der 31. Oktober 2017 ist Feiertag im Sinne des"

   § 2 는 2017-11-01 실효다. YAML 머리 주석 「일회성 항목은 확인된 것이 없다」와 다르다. 다만 de_nw 피드 범위는 `RANGE_START = date(2020, 1, 1)`(`rules/de_nw/feed.py:54`)라 발행물 영향은 없다. § 2 개정이 아니라 별도 법률이라 체인에는 넣지 않았다.
6. 다른 주(HE 관보, BE 커버 하한)는 이번에 보지 않았다.

---

## 판단 요청 (결정은 사람)

1. 2015 → 2026 무개정을 전문 색인 전수 검색으로 닫을지, 2021 Nr. 75a 공백을 수용할지(A4). 이 두 판단이 11 건 true 의 공통 전제다.
2. christi_himmelfahrt 의 SUMMARY 를 `Christi-Himmelfahrtstag` 로 바꿀지. 발행되는 SUMMARY 가 바뀐다. UID(key)는 불변이다.
3. erster_mai source 에서 1989 인쇄 오식 `Gerichtigkeit` 를 어떻게 적을지(C3). SUMMARY 에는 영향이 없다.
4. 서지 문자열을 E0(머리 주석 정의 + 짧은 참조)과 E1(항목별 전부) 중 어느 쪽으로 할지.
5. SUMMARY 규약 문구의 기준 텍스트 「(lexmea)」를 공포본으로 바꾸는 것을 승격 PR 에 포함할지.
