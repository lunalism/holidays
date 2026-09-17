# BGBl. 1990 II — Einigungsvertrag Art. 2 Abs. 2 공포본 실측 보고

- 작성: 2026-09-17 (UTC 07:00–07:20 실측). 레포 무수정(`git status --porcelain` 빈 출력 확인).
- 받은 파일: `~/holidays-reports/bgbl1990/` (PDF 7 벌, HTML/헤더/해시 로그, 재현 스크립트 `hash_page.py`).
- 표기: 「사실」은 명령·출력 또는 원문 인용. 「[추론]」은 사실에서 끌어낸 것. 「미확인」은 손대지 않은 것.
- 권고 없음.

## A. 서지

### A1. Einigungsvertragsgesetz 와 조약 본문

사실(공포본 스캔 육안 + bgbl.de 목차 breadcrumb + gesetze-im-internet 메타데이터):

| 항목 | 값 | 출처 |
|---|---|---|
| 관보 | Bundesgesetzblatt Teil II, Jahrgang 1990 | PDF p.1 머리(「Bundesgesetzblatt Teil II · Z 1998 A · 1990 · Nr. 35」) |
| 호 | **Nr. 35** | PDF p.1; bgbl.de breadcrumb `Nr. 35 vom 28.09.1990` |
| Ausgabetag | **1990-09-28** (「Ausgegeben zu Bonn am 28. September 1990」) | PDF p.1 |
| 호의 면 범위 | S. 885–1248 (PDF 364 면, p.1 = S. 885, p.364 = S. 1248) | PDF 머리글 육안(p.361 「Nr. 35 — Tag der Ausgabe: Bonn, den 28. September 1990 / 1245」, p.362 「1246」, p.364 「1248」) |
| Einigungsvertragsgesetz | Gesetz zu dem Vertrag vom 31. August 1990 … — Einigungsvertragsgesetz — und der Vereinbarung vom 18. September 1990, **Vom 23. September 1990**, 시작 **S. 885** | PDF p.1 목차 「23. 9. 90 … 885」; GII Vollzitat 「(BGBl. 1990 II S. 885)」 |
| Vertrag(조약 본문) | Vertrag … über die Herstellung der Einheit Deutschlands, 시작 **S. 889** (PDF p.5) | PDF p.5 머리 「Nr. 35 — Tag der Ausgabe: … 889」; GII 「Einigungsvertrag vom 31. August 1990 (BGBl. 1990 II S. 889)」; XML `<fundstelle typ="amtlich"><periodikum>BGBl II</periodikum><zitstelle>1990, 889</zitstelle>` |
| **Art. 2 Abs. 2 가 실린 면** | **S. 890 = PDF p.6** | PDF p.6 머리 「890 Bundesgesetzblatt, Jahrgang 1990, Teil II」, 본문 「Kapitel I … Artikel 2 Hauptstadt, Tag der Deutschen Einheit … (2) Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag.」 |
| 같은 호의 둘째 항목 | Gesetz über die Inkraftsetzung von Vereinbarungen betreffend den befristeten Aufenthalt von Streitkräften …, 24. 9. 90, S. 1246 | PDF p.1 목차; bgbl.de attr_id `bgbl290s1246.pdf` |

### A2. 발효 공고

사실:
- gesetze-im-internet EinigVtr 각주: 「G v. 23.9.1990 II 885 In Kraft gem. Bek. v. 16.10.1990 II 1360 mWv 29.9.1990」.
- bgbl.de 문서 `bgbl290s1360.pdf` 의 breadcrumb(`text.xav` 응답의 `topubkwn`): `Bundesgesetzblatt / Bundesgesetzblatt Teil II / 1990 / Nr. 40 vom 26.10.1990 / Bekanntmachung über das Inkrafttreten des Vertrages … — Einigungsvertrag — und der Vereinbarung … zur Durchführung und Auslegung des Einigungsvertrages`.
- 그 PDF(1 면, 55,735 B, sha256 `5721d2c6…`; 파일 해시는 비결정적 — C 참조) 육안: 「1360 Bundesgesetzblatt, Jahrgang 1990, Teil II … Bekanntmachung über das Inkrafttreten des Vertrages … Vom 16. Oktober 1990 … am 29. September 1990 in Kraft getreten sind. Bonn, den 16. Oktober 1990 Der Bundesminister des Innern Im Auftrag Härdtl」.

→ **Bek. vom 16.10.1990, BGBl. 1990 II Nr. 40 (Ausgabetag 26.10.1990) S. 1360, 발효 1990-09-29.**

### A3. 출처 간 차이

- 서지 값(연도·Teil·Nr.·Ausgabetag·면)은 공포본 스캔, bgbl.de breadcrumb, gesetze-im-internet 셋이 일치. 차이 없음.
- 이전 조사 요약은 Bek. 의 Ausgabetag 을 적지 않았다. 이번에 26.10.1990 으로 확정.
- 미확인: Bundesanzeiger 인쇄본 실물, dip.bundestag.de 의 Drucksache 는 보지 않았다.

## B. 취득 경로와 이용 조건

### B1. recht.bund.de 의 1990 년분 안내

사실(https://www.recht.bund.de/de/archiv/archiv_node.html, 2026-09-17 열람, HTTP 200):

> Archiv des Bundesgesetzblatts vor dem Jahr 2023
> Bis zum 31. Dezember 2022 wurde die rechtsverbindliche Fassung von Gesetzen und Verordnungen als amtliche Papierausgabe veröffentlicht. Parallel dazu erfolgte die Publikation des Bundesgesetzblatt auf der Internetseite https://www.bgbl.de , die durch den Bundesanzeiger Verlag betrieben wird. Auf dieser Webseite können Sie alle Ausgaben des Bundesgesetzblatts von 1949 bis 2022 einsehen. Der Umfang umfasst das Bundesgesetzblatt Teil 1 (BGBl. I) sowie das Bundesgesetzblatt Teil 2 (BGBl. II).

- 같은 사이트 첫 화면의 검색 안내: 「Hier können Sie nach allen veröffentlichten Verkündungen und Bekanntmachungen ab dem Jahr 2023 suchen.」 연도 필터는 2023–2026 만 있다.
- 메뉴 항목 이름은 「Archiv vor 2023」.

### B2. bgbl.de — 운영 주체, 열람·저장 조건

사실(전부 2026-09-17 열람):

- 운영 주체 — https://www.bgbl.de/xaver/bgbl/extern/static/impressum.html:
  > IMPRESSUM
  > Herausgeber:
  > © Bundesanzeiger Verlag GmbH
  > Amsterdamer Str. 192
  > 50735 Köln
  > … Die Gesellschaft hat ihren Sitz in Köln und ist eingetragen beim Amtsgericht Köln HRB: 31248

- 첫 화면 — https://www.bgbl.de/ (→ `/xaver/bgbl/start.xav`):
  > Bundesgesetzblatt-Archiv der von 1949 bis 2022 erschienenen Ausgaben
  > In den Jahren 1949 bis 2022 erfolgte die rechtswirksame Verkündung von Rechtsnormen in den gedruckten Bundesgesetzblättern. Das hier vorgehaltene frei zugängliche Archiv beinhaltet die bis zu diesem Zeitpunkt erschienenen Gesetzblätter so, wie sie veröffentlicht wurden. Ab 1.1.2023 wurde die Verkündung im Internet unter www.recht.bund.de eingeführt.

- 도움말 — https://www.bgbl.de/xaver/bgbl/extern/static/hilfe.html. 저장·인쇄·링크에 관한 문장 전부:
  > 6.1 Dokumentenmenü Bundesgesetzblatt
  > … Wenn Sie ein PDF-Dokument ausgewählt haben, können Sie mit dieser Funktionsfläche den Link zu dem ausgewählten Dokument entnehmen. Nach Aktivieren der Funktionsfläche öffnet sich ein Textfenster. Kopieren Sie nun die Linkadresse heraus.
  > Wenn Sie ein PDF-Dokument ausgewählt haben, können Sie mit dieser Funktion die angezeigte PDF-Datei in einem neuen Fenster öffnen. Dabei steht Ihnen für die Betrachtung der PDF-Datei mehr Raum zur Verfügung.

  > 6.4 PDF-Plugin
  > Zur Anzeige der PDF-Dateien in Ihrem Browser benötigen Sie das kostenlose Programm „Adobe Acrobat Reader". …
  > Über die Menüleiste können Sie die PDF-Dokumente unter anderem drucken, speichern, die Seiten navigieren oder die Größe der PDF-Datei einstellen.

  > 7. Dokumente drucken
  > … Wenn Sie ein PDF-Dokument drucken möchten, verwenden Sie bitte das Druck-Symbol im PDF-Plugin.

  > 1.3 Weitere Menüpunkte
  > … Über „LOGOUT“ beenden Sie die Anwendung, was Sie mit Mausklick auf „OK“ bestätigen müssen.

- 이용 조건 문서의 존재 — 사이트에 「Nutzungsbedingungen」「AGB」「Lizenz」「Urheber」 문구가 있는 페이지가 없다. 첫 화면·Hilfe·Impressum·Datenschutz 네 HTML 을 `grep -ci nutzungsbedingung` → 전부 0. 링크 목록에도 Hilfe/Datenschutz/Impressum 셋뿐. `robots.txt` 는 없다(302 → `/404.html`).
- 문서 응답의 기계 판독 메타데이터 — `text.xav` 응답(PDF 뷰 HTML) 안의 JSON-LD:
  > {"@context":"https://schema.org/","@type":"WebPage","isAccessibleForFree":"True","hasPart":{"@type":"WebPageElement","isAccessibleForFree":"True","cssSelector":".dtXavPaywall"}}
- Datenschutz(https://www.bgbl.de/xaver/bgbl/extern/static/datenschutz.html)에서 접근 조건과 닿는 문장:
  > Für die Nutzung unserer Internetseite ist es, soweit hier nicht anders erwähnt, nicht erforderlich, dass Sie personenbezogene Daten mitteilen.
  > … Des Weiteren verwenden wir Cookies, um den Nutzungsumfang kostenloser Inhalte zu messen. Um diesen Nutzungsumfang ermitteln zu können, sendet unsere Internetseite eine sogenannte Unit-ID an Ihren Browser.
- 로그인 — 없었다. 세션 쿠키 `bgblxaver`(HttpOnly; Secure)가 첫 요청에서 자동 발급되고, 그 쿠키만으로 PDF 를 받았다. 계정·비밀번호·결제 화면 없음.
- PDF 자체의 권한 플래그(C2 에서 실측): AES-128, 사용자 비밀번호 빈 문자열, `/P -1036` → print_lowres/print_highres/extract/accessibility 허용, modify_other/modify_assembly 불허.

[추론] 「저장」이 명시된 자리는 도움말 6.4 의 「drucken, speichern」 한 곳이고, 이는 Acrobat 플러그인 기능 설명이다. 별도의 이용 조건·라이선스 문서가 없으므로 「저장 허용」의 근거는 (i) 이 도움말 문장, (ii) 첫 화면의 「frei zugängliche Archiv」, (iii) JSON-LD `isAccessibleForFree: True`, (iv) PDF 권한 플래그(추출·인쇄 허용) 넷이다. 재사용·재배포에 관한 문장은 사이트 어디에도 없다(허용도 금지도 없음).
미확인: Bundesanzeiger Verlag 본사 사이트(bundesanzeiger-verlag.de)의 AGB 는 열지 않았다. 관보 원문 자체의 저작권법상 지위(UrhG § 5 amtliche Werke)는 법률 판단이라 여기서 다루지 않는다.

### B3. 받는 방법

사실:
- 단위: **문서(attr_id) 단위**. 한 attr_id 가 「호의 시작 면」과 같으면 사실상 호 전체가 된다. `bgbl290s0885.pdf` 는 S. 885–1248 의 364 면(둘째 문서 S. 1246–1248 포함). `bgbl290s1360.pdf` 는 1 면(Bek. 하나). 같은 호에 `bgbl290s1246.pdf` 가 따로 있다.
- attr_id 규칙: `bgbl` + Teil(`1`/`2`) + 연도 두 자리(`90`) + `s` + 시작 면 4 자리 + `.pdf`. 고해상도 변형 `bgbl290s0885_gross.pdf`(breadcrumb 제목 뒤에 「-- 23 MB-Version in besserer Qualität ! --」; 361 면 = S. 885–1245, 문서만; JBIG2, 3296×4677).
- 요청 순서(실측, 전부 `curl`):
  1. `GET https://www.bgbl.de/xaver/bgbl/text.xav?SID=&tf=xaver.component.Text_0&tocf=&qmf=&hlf=xaver.component.Hitlist_0&bk=bgbl&start=%2F%2F*%5B%40attr_id%3D%27bgbl290s0885.pdf%27%5D&skin=pdf&tlevel=-2&nohist=1` → 200, 쿠키 `bgblxaver` 발급, HTML 안에 `src="media.xav/bgbl290s0885.pdf?SID=&iid=67234&sinst=&ssinst=&_csrf=<40hex>"`.
  2. `GET https://www.bgbl.de/xaver/bgbl/media.xav/bgbl290s0885.pdf?…&_csrf=…` (쿠키 동반) → 302 `Location: https://www.bgbl.de/xaver/bgbl/media/<32hex 세션값>/bgbl290s0885_67234.pdf`.
  3. 그 URL → 200, `Content-Type: application/pdf`, `Content-Length: 8796446`(1 회차)/`8796449`(2 회차), `Last-Modified` = 요청 시각(07:01:16Z / 07:04:07Z), `ETag` 매번 다름.
- 영구 URL 여부:
  - 인용용 진입 URL `https://www.bgbl.de/xaver/bgbl/start.xav?startbk=Bundesanzeiger_BGBl&jumpTo=bgbl290s0885.pdf` → 200 (Wayback 에 2015 년부터 같은 형태의 캡처 있음 — B4). 이것이 안정 URL.
  - `media/<32hex>/…` URL 은 세션값 포함. 쿠키 없이 재요청 → 302 `/404.html`. `media.xav/…` 를 `_csrf` 없이 또는 쿠키 없이 → 403. 즉 **PDF 바이트에 닿는 URL 은 영구가 아니다.**
  - `Content-Disposition` 헤더 없음.
- 자동화 범위: 이번 조사에서 bgbl.de 에 보낸 PDF 요청은 4 건(Nr. 35 일반 2 회, Nr. 35 gross 1 회, Nr. 40 문서 1 회). HTML 요청 약 10 건. 대량 수집 아님.

### B4. Wayback 사본

사실(CDX `https://web.archive.org/cdx/search/cdx?url=bgbl.de/xaver/bgbl/media/*&filter=original:.*bgbl290s0885.*&filter=statuscode:200&output=json`, 저장본 `bgbl1990/wayback_cdx.json`):

| 캡처 시각(UTC) | 원 URL | CDX length |
|---|---|---|
| 20210615032013 | https://www.bgbl.de/xaver/bgbl/media/14360CBE077A40C29B55772DE17FC7DF/bgbl290s0885_67234.pdf | 8623247 |
| 20211204104652 | https://www.bgbl.de/xaver/bgbl/media/156E22FE3620F096EF22CF68BE70DFA6/bgbl290s0885_67234.pdf | 8623097 |
| 20230719131947 | https://www.bgbl.de/xaver/bgbl/media/B9530373AE1BE942B45341AEC08B37B4/bgbl290s0885_67234.pdf | 8623072 |

- 받기: `https://web.archive.org/web/<ts>id_/<원 URL>` (id_ = 원본 바이트). 세 벌 모두 200, 8,796,467 / 8,796,465 / 8,796,445 B(CDX length 는 압축 저장 크기라 다르다).
- `start.xav?…jumpTo=bgbl290s0885.pdf` 계열 캡처도 있다(2015-04-03 403, 2019 301, 2024-06-20 302 등; `_gross` 도 2015-12-28 부터). `archive.org/wayback/available` API 는 429 로 막혀 CDX 로 대체.
- `_gross` 의 media 캡처는 CDX 에서 조회하지 않았다(미확인).

### B5. 그 밖의 공공 경로

- gesetze-im-internet.de (BMJ/juris, 통합본 — 공포본 아님): `https://www.gesetze-im-internet.de/einigvtr/` (HTML·PDF·XML·EPUB), `https://www.gesetze-im-internet.de/einigvtrg/`. XML zip(`einigvtr/xml.zip`, 259,273 B, builddate 20260506175711) 받아 E3 에 씀. 이용 조건은 이 레포가 이미 근거로 쓰고 있어 다시 읽지 않았다.
- 미확인: dip.bundestag.de(Drucksache 11/7760 등), Bundesarchiv, 대학 도서관 스캔.

## C. 파일의 결정성과 해시

### C1. 같은 호를 여러 번 받은 결과

사실. 대상은 전부 attr_id `bgbl290s0885.pdf`(BGBl. 1990 II Nr. 35, S. 885–1248, 364 면).

| 사본 | 취득 | 시각(UTC) | 크기(B) | 파일 sha256 |
|---|---|---|---|---|
| live1 | bgbl.de 세션 1 | 2026-09-17 07:01:24 | 8,796,446 | `ebfc9f056cceca6353a6cf9b730535e2be003968c26827b63be288cb249bc47c` |
| live2 | bgbl.de 세션 2(새 쿠키) | 2026-09-17 07:04:06 | 8,796,449 | `546e3f911f8ab3205fde59b425829da83a2dfc2865554c2bc00aea5d85b728ab` |
| wayback1 | Wayback 20210615032013 id_ | — | 8,796,467 | `4c72e8eee33959af886d0a52cb6937e6fa112822e881062131ced07a8fe45c01` |
| wayback2 | Wayback 20211204104652 id_ | — | 8,796,465 | `76522b4240d6fa55a2870c98e4b33e482e92e04e9028abbde3dafa04deadf1cb` |
| wayback3 | Wayback 20230719131947 id_ | — | 8,796,445 | `504414fbb83776f7b59a234f9ece947bf36d76cb832465630cc8ab42e5ca86e0` |

- 다섯 파일 해시 전부 다름. 크기도 전부 다름(±20 B 안).
- 두 라이브 회차 간격은 2 분 42 초. `cmp live1 live2` → 「differ: char 208, line 11」. 같은 오프셋에서 바이트가 같은 자리는 8,796,446 중 248,812(2.8 %).
- 부수 취득(표 밖): `bgbl290s0885_gross.pdf` 24,723,313 B sha256 `f2115cd614a886828c951c14a350b5c478a33d816eec5da65d39897acf0876c9`(1 회만); `bgbl290s1360.pdf` 55,735 B sha256 `5721d2c64de81088b5ff9ba5d4213efa8b87dfc93c7a666513b46f393a01b630`(1 회만). 이 둘의 결정성은 재수령하지 않아 미확인이나, 같은 생성기(아래)라 [추론] 같은 방식으로 매번 달라진다.

### C2. 파일 안에서 무엇이 달라지는가

도구: pikepdf 9.11.0(libqpdf 12.2.0), pypdf 6.19.0, PyMuPDF 1.26.5(MuPDF 1.26.10), Python 3.9.6, `cmp`, `shasum -a 256`. 설치는 C5.

사실:
- **암호화.** 다섯 파일 모두 `pdf.is_encrypted == True`. `/Encrypt`: `/Filter /Standard /V 4 /R 4 /Length 128 /CF <</StdCF <</CFM /AESV2 /AuthEvent /DocOpen /Length 16>>>> /StmF /StdCF /StrF /StdCF /P -1036`. 사용자 비밀번호는 빈 문자열(pypdf `decrypt("")` → `PasswordType.USER_PASSWORD`). 파일별 암호화 키(pikepdf `encryption.encryption_key`)가 다르다 — 예: live1 `6c56179fdd50acf7a9a58ebf084a2cce`, wayback1 `bb1c88049c44fc3a2b482a8e71250416`. **모든 스트림과 문자열이 파일마다 다른 키로 AES-CBC 암호화되므로 디스크 바이트가 거의 전부 다르다.** 이것이 2.8 % 일치의 원인.
- `/ID`: 파일마다 다름(두 원소 동일). live1 `651d76c15be88b40a076e518133d422a`, live2 `89c7716333f0d2b9e720b480117888e8`, wb1 `e0eae83d4f8514f2059e2643ea48b440`, wb2 `c9c9ef00fdf38a202a35665581c97a20`, wb3 `f36bad140e48169d4d0e3f121851e542`.
- `/Info`: `/CreationDate` = 요청 시각(`D:20260917070116Z`, `D:20260917070407Z`, `D:20210615052013+02'00'`, `D:20211204114653+01'00'`, `D:20230719151947+02'00'`). `/Keywords` = 「erstellt am 17.09.2026」(라이브·2023) / 「erstellt für Bürgerzugang am 15.06.2021」「… 04.12.2021」(2021 두 벌). `/Producer` = 「PDFlib+PDI 9.3.1 (JDK 21.0/Linux-x86_64)」(2026) / 「PDFlib+PDI 9.3.1 (JDK 1.8/Linux-x86_64)」(2021·2023).
- 구조: 다섯 파일 모두 PDF 1.6, 364 면, 객체 2,240 개, 선형화 아님, 텍스트층 없음(PyMuPDF `get_text()` 0 자, `/Font` 없음). 객체 번호·오프셋도 같다(예: 객체 35 의 스트림 시작 오프셋 87114 가 다섯 벌 동일).
- 복호화 뒤 객체 단위 비교(2,240 객체의 사전 + 스트림 raw 바이트): **다른 객체는 1 개(객체 2240 = xref 스트림; 그 사전에 `/Encrypt`·`/ID`·`/Info`·`/Length` 가 들어 있음)뿐**, 나머지 2,239 개는 다섯 벌에서 동일. 트레일러에서 다른 키: `/Encrypt`, `/ID`, `/Info`, `/Length`.
- 압축·필터·텍스트 레이어의 차이는 없다. 즉 **달라지는 것은 (1) 암호화 키에 따른 암호문, (2) /ID, (3) /Info 의 날짜·키워드·Producer, (4) xref 스트림** 넷이다.

[추론] 서버가 요청마다 PDFlib 로 새 PDF 를 만들고(Last-Modified·CreationDate 가 요청 시각) 그때마다 새 키로 암호화한다. 내용물(페이지 트리·이미지)은 2021-06 부터 2026-09 까지 동일.

### C3. S. 890 의 페이지 이미지 스트림

사실:
- S. 890 = **PDF p.6(0-기준 5)**. 페이지 라벨은 `/PageLabels /S /D` 라 「6」.
- 페이지 콘텐츠 스트림(FlateDecode, 48 B): `q\n/I5 Do\nQ\n`. `/Resources /XObject /I5` = **Form XObject 객체 (34,0)**, BBox `[0 0 593.28 841.86]`, 내용 `q\n593.2799988 0 0 841.8600006 0 0 cm\n/Im0 Do\nQ\n`, 그 `/Resources /XObject /Im0` = **이미지 XObject 객체 (35,0)**. 페이지가 참조하는 이미지는 **1 개**(Form 을 거쳐서).
- 객체 (35,0) 사전:
  - `/Type /XObject /Subtype /Image /Name /Im1`
  - `/Filter /CCITTFaxDecode`
  - `/Width 618 /Height 877`
  - `/ColorSpace /DeviceGray /BitsPerComponent 1`
  - `/Decode [1 0]`
  - `/DecodeParms <</K -1 /Columns 618 /Rows 877 /BlackIs1 false /EndOfLine false /EncodedByteAlign true>>`
  - `/Length 19664` (암호문 길이 = 16 B IV + 19,643 B 를 16 B 로 패딩한 19,648 B)
- 같은 구조가 364 면 전부에 적용된다(C6). 해상도 618×877 on 593.28×841.86 pt ≈ 75 dpi(1-bit). `_gross` 변형은 같은 면이 JBIG2 3296×4677(≈400 dpi).

### C4. 두 가지 해시, 사본별

정의:
- **(a0)** 디스크에 저장된 스트림 바이트 그대로(= AES 암호문). 「PDF 에 저장된 인코딩된 스트림 바이트 그대로」를 문자 그대로 읽으면 이것이다.
- **(a)** 복호화한 뒤, `/Filter` 는 풀지 않은 바이트(CCITT G4 부호 그대로, 19,643 B). pikepdf `Stream.read_raw_bytes()` 와 pypdf `StreamObject._data` 로 교차.
- **(b)** CCITT G4 를 푼 비트맵. 두 디코더로 교차: pdfminer.six `ccittfaxdecode` → 1-bit, 행마다 바이트 정렬(78 B × 877 = 68,406 B), 1 = 검정, 패딩 비트 0. PyMuPDF `fitz.Pixmap(doc, 35)` → 8-bit gray 541,986 B(618×877, 값은 0/255 둘뿐). PyMuPDF 결과를 같은 규약(1 = 검정, 패딩 0)으로 1-bit 로 묶으면 pdfminer 출력과 바이트 단위 동일.

| 사본 | (a0) on-disk 암호문 sha256 | (a) 복호화·미디코드 sha256 | (b) 1-bit sha256 [pdfminer = PyMuPDF packed] | (b′) PyMuPDF 8-bit gray sha256 |
|---|---|---|---|---|
| live1 | `510d3bc5890066d1aae9ab6adf7c91cae5702e5e6e7a06e7681150eea7bc60a1` | `0f70b21d7715670a0db1d9433d8ea04ff534a7e53d3f40521301db6d8a92a6af` | `ad7c2447f4c95486de22a5698fc7cd3bc2c0830255a6950d348f5a7be08cfb30` | `d0ee47f42cbdc7dfe2b8d4defd28c206281d2c63ae08a21fea24a96868502047` |
| live2 | `b9c0e31a6181b6354b02f8445691ed46b847f92d54758023693aee388dc3c2a1` | 동일 `0f70b21d…a6af` | 동일 `ad7c2447…fb30` | 동일 `d0ee47f4…2047` |
| wayback1 (2021-06) | `143775c8768afcd7973b79fc671871b65ca5dac46de14e6c7ee6d8796367531d` | 동일 | 동일 | 동일 |
| wayback2 (2021-12) | `12ba693720161ac4bb3f24def07319806b65463c57e235348755dc8079569529` | 동일 | 동일 | 동일 |
| wayback3 (2023-07) | `eaf6fe719ccb05b4233729b164ad06618cc84982dea530cd67422d5307ed9fc0` | 동일 | 동일 | 동일 |

- **(a0) 는 다섯 벌 전부 다르다**(암호화 키가 다르므로 당연).
- **(a) 는 다섯 벌 동일** — 두 도구(pikepdf, pypdf; AES 구현이 서로 다름) 값 일치.
- **(b) 는 다섯 벌 동일** — 두 디코더(pdfminer.six, MuPDF) 픽셀 단위 일치. 디코딩은 도구에 따라 **표현**(1-bit 패킹 vs 8-bit gray, 극성)이 달라 해시가 달라지므로, 기록할 때는 표현 규약을 함께 적어야 한다. 위 표의 (b) 규약: 「1-bit, 행 바이트 정렬, 1 = 검정, 패딩 0」 = pdfminer.six `ccittfaxdecode` 의 출력 그대로.
- 실패한 경로: Pillow/libtiff 로 G4 를 풀려고 TIFF 로 감싸 봤으나 `EncodedByteAlign true` 를 libtiff 가 지원하지 않아(「Fax4Decode: Uncompressed data (not supported)」「Bad code word」) 출력이 깨지고 사본마다 달랐다. 이 경로는 쓰지 않는다.
- 도구 버전이 (a)·(b) 값에 영향을 주는지: (a) 는 복호화만이라 AES 표준 구현이면 같다. (b) 는 CCITT G4 디코더 구현이 다르면 출력이 다를 수 있으나 두 구현이 일치했다.

### C5. 재현 명령

설치(레포 의존성 밖; `uv` 0.12.2, 시스템 Python 3.9.6 사용됨. `--with` 는 격리 환경을 만들어 레포 `pyproject.toml` 을 건드리지 않는다):

```bash
# 받기 — 1) 세션+CSRF 얻기  2) media.xav → 302 → media/<hash>/… 따라가기
cd ~/holidays-reports/bgbl1990
UA="Mozilla/5.0 (holidays-research; manual)"
curl -s -c cookies.txt -b cookies.txt -A "$UA" -o text_pdf.html \
  "https://www.bgbl.de/xaver/bgbl/text.xav?SID=&tf=xaver.component.Text_0&tocf=&qmf=&hlf=xaver.component.Hitlist_0&bk=bgbl&start=%2F%2F*%5B%40attr_id%3D%27bgbl290s0885.pdf%27%5D&skin=pdf&tlevel=-2&nohist=1"
URL=$(python3 -c "import re,html;s=open('text_pdf.html').read();print('https://www.bgbl.de/xaver/bgbl/'+html.unescape(re.search(r'src=\"(media\.xav/[^\"]*)\"',s).group(1)))")
curl -s -L -c cookies.txt -b cookies.txt -A "$UA" -D hdr.txt -o live_bgbl290s0885.pdf "$URL"
shasum -a 256 live_bgbl290s0885.pdf     # 매번 다르다

# Wayback 원본 바이트
curl -s -L -o wayback3_20230719131947.pdf \
  "https://web.archive.org/web/20230719131947id_/https://www.bgbl.de/xaver/bgbl/media/B9530373AE1BE942B45341AEC08B37B4/bgbl290s0885_67234.pdf"

# 해시 — 스크립트는 ~/holidays-reports/bgbl1990/hash_page.py (이 보고서와 같이 둠)
uv run --with pikepdf==9.11.0 --with pypdf==6.19.0 --with pymupdf==1.26.5 --with pdfminer.six==20251107 \
  python hash_page.py live_bgbl290s0885.pdf 6
```

기대 출력(어느 사본이든 (a0) 만 다르고 나머지는 아래):

```
live1_bgbl290s0885.pdf: pdf-page 6, image XObjects: 1, encrypted=True
  /I5>/Im0 obj (35, 0) Filter=/CCITTFaxDecode 618x877 bpc=1 cs=/DeviceGray Decode=[1, 0] Length=19664 DecodeParms={'/BlackIs1': False, '/Columns': 618, '/EncodedByteAlign': True, '/EndOfLine': False, '/K': -1, '/Rows': 877}
    (a0) on-disk bytes            len=19664 sha256=510d3bc5890066d1aae9ab6adf7c91cae5702e5e6e7a06e7681150eea7bc60a1
    (a)  decrypted, still encoded len=19643 sha256=0f70b21d7715670a0db1d9433d8ea04ff534a7e53d3f40521301db6d8a92a6af  [pikepdf]
    (a)  decrypted, still encoded len=19643 sha256=0f70b21d7715670a0db1d9433d8ea04ff534a7e53d3f40521301db6d8a92a6af  [pypdf]  agree=True
    (b)  decoded 1-bit (1=black)  len=68406 sha256=ad7c2447f4c95486de22a5698fc7cd3bc2c0830255a6950d348f5a7be08cfb30  [pdfminer.six]
    (b)  decoded 8-bit gray       len=541986 sha256=d0ee47f42cbdc7dfe2b8d4defd28c206281d2c63ae08a21fea24a96868502047  [PyMuPDF Pixmap]
    (b)  PyMuPDF packed to 1-bit  sha256=ad7c2447f4c95486de22a5698fc7cd3bc2c0830255a6950d348f5a7be08cfb30  agree-with-pdfminer=True
```

(a) 만 최소 코드로 다시 얻으려면:

```bash
uv run --with pikepdf==9.11.0 python -c "
import pikepdf,hashlib
p=pikepdf.open('live_bgbl290s0885.pdf'); im=p.pages[5].Resources.XObject['/I5'].Resources.XObject['/Im0']
print(im.objgen, hashlib.sha256(im.read_raw_bytes()).hexdigest())"
# → (35, 0) 0f70b21d7715670a0db1d9433d8ea04ff534a7e53d3f40521301db6d8a92a6af
```

### C6. 호 전체 이미지 스트림 — 묶음 해시 판단용 사실

사실(다섯 사본 각각, pikepdf 로 364 면 순회):
- 면 수 364, **면당 이미지 1 개(364 면 전부)**, 전체 이미지 364 개. 필터 전부 `/CCITTFaxDecode`, 전부 618×877×1-bit, 전부 Form XObject 경유.
- 면별 (a) 해시(복호화·미디코드)를 페이지 순으로 이어 붙인 sha256: **`b24082d8bc6f36f89cd65fc5bd2e9ef492ec617c5a271fc5756393094e4ff602`** — 다섯 사본 동일. 면별로 비교해도 다른 면 0.
- 복호화 후 객체 단위 비교(C2)도 이미지 364 개를 포함해 2,239 객체 동일.
- 호 전체를 잇는 규약(페이지 순, 각 면 (a) 해시의 raw 32 B 연결)은 이 보고서가 정한 것이며 표준이 아니다. 다른 규약(예: 스트림 바이트 자체를 연결)이면 값이 다르다.
- `_gross` 변형은 면 수(361)와 필터(JBIG2)가 달라 위 값과 호환되지 않는다(1 회만 받아 사본 간 비교 없음).

## D. 이 레포의 서지 형식

### D1. 형식이 규정된 자리

사실:
- 규정 문서·코드는 없다. `grep -rn sha256` 이 잡는 곳은 README 한 줄, 규칙 YAML 의 주석·source, 테스트 상수, docs 뿐이며 스키마·검증 코드는 없다. `rules/de/feed.py::_checked` 는 `key/name/source` 비어 있지 않음과 `verified` 가 bool 인 것만 본다.
- README.md:203–205 (「### 독일 — 각 주 관보」):
  > 수집 대상이 아닙니다. 각 항목의 근거는 그 주 관보의 공포본이고, 서지(관보
  > 호수·면·공포일·sha256)는 규칙 YAML 의 `source` 필드에 있습니다.
- PR #56 본문(「## 승격 근거 — 공포 관보 원문」)이 실제 선례:
  > - 서지: **Fünftes Gesetz zur Änderung des Feiertagsgesetzes, vom 12. März 2018**, Hamburgisches Gesetz- und Verordnungsblatt Teil I, **HmbGVBl. 2018 Nr. 9** (Dienstag, den 20. März 2018), S. 61–64, 해당 법은 **S. 63**.
  > - 사본: luewu.de PDF, 2026-09-07 열람.
  >   ```
  >   curl -sSL -o /tmp/GVBL_HH_2018-9.pdf "https://www.luewu.de/wp-content/uploads/2025/08/GVBL_HH_2018-9.pdf"
  >   457762 bytes, 4 pages
  >   sha256 025be364db842223fc6b8356da91adc3b4e7a39f52410103c317273af66a4aa8
  >   ```
  > - 원문 확인(pypdf 텍스트 추출, 3 면): …
  단, #56 의 YAML `source` 자체에는 sha256 이 없다(아래 D2 de_hh). sha256 을 `source` 에 넣기 시작한 것은 그 뒤 SH·BW·NI·RP 다.
- docs/holiday_15.md:222–225 가 이 조사의 발단:
  > - **BGBl. 1990 II S. 889 공포본 확보** — Einigungsvertrag Art. 2 Abs. 2.
  >   현재 rules/de 와 de_bw 가 gesetze-im-internet 통합본을 근거로 들고 있어
  >   #56 서지 형식(공포본 PDF + sha256)에 못 미친다. 10-03 을 든 전 피드에
  >   일괄 해당.
- 테스트가 형식을 고정하는 자리: `tests/test_de_sh_feed.py:411` 「여기서 서지·공포일·URL·sha256 네 값과 열람일을 전부 본다(Codex 리뷰 #60 지적)」; de_bw/de_ni/de_rp 테스트도 `GAZETTE_… = {"cite","published","url","sha256"}` 상수를 두고 `source` 에 네 값 + `READ_ON`(「2026-09-09 열람」)이 들어 있는지 본다.

### D2. 공포본 근거를 든 기존 `source` 인용

- `rules/de_sh/solar_holidays.yaml:103–109` (tag_der_deutschen_einheit, verified true):
  ```
  source: >-
    SFTG(SH) § 2 Abs. 1 Nr. 7 '3. Oktober - Tag der Deutschen Einheit -' — Gesetz
    über Sonn- und Feiertage (SFTG) vom 28.06.2004, GVOBl. Schl.-H. 2004 Nr. 8
    S. 213 (15.07.2004 공포; Verkündungsportal 연도판 PDF
    https://verkuendungsportal.schleswig-holstein.de/mm/gvobl_jahrgang_2004/GVOBl_2004.pdf
    sha256 dba6f1a10bf991211a29d6f6c52f2e4f4dab5526c627d46f76b1df6ced26bc41,
    2026-09-09 열람). 2018-03-21 개정(GVOBl. Schl.-H. 2018 Nr. 6 S. 69) 후에도
  ```
- `rules/de_ni/solar_holidays.yaml:163–171` (reformationstag, verified true):
  ```
  source: >-
    NFeiertagsG § 2 Abs. 1 Buchst. h 'der 31. Oktober, als Reformationstag' — Gesetz zur
    Änderung des Niedersächsischen Gesetzes über die Feiertage vom 22.06.2018 Art. 1 Nr. 1
    (Buchst. h 삽입, 구 Buchst. h·i → i·j, Satz 2 삭제), Nds. GVBl. 2018 Nr. 7 S. 122
    (28.06.2018 공포, 29.06.2018 시행; 니더작센 포털 PDF
    https://www.niedersachsen.de/download/132379/Nds._GVBl._Nr._7_2018_vom_28.06.2018_S._111-154.pdf
    sha256 99d4848d3b86f2bd5b7af9e33af05b75fdee7098b8cdcdd16e07a378bd378b3d,
    2026-09-09 열람, 재수령 대조 일치; Wayback 20240415 사본도 같은 sha256). SUMMARY 는
    서술부를 정리한 'Reformationstag'. 날짜 31. 10. 은 feiertage-api 2026 NI 대조 일치
  ```
- `rules/de_bw/solar_holidays.yaml:139–150` (tag_der_deutschen_einheit — 이번 조사 대상, 미러):
  ```
  source: >-
    Einigungsvertrag Art. 2 Abs. 2 — 'Der 3. Oktober ist als Tag der Deutschen Einheit
    gesetzlicher Feiertag.' (gesetze-im-internet.de; rules/de 의 같은 항목을 미러).
    FTG(BW) 의 § 1 열거에는 없고 § 7 Abs. 2 "mit Ausnahme des 1. Mai und des
    3. Oktober" 등에서 전제만 한다(GBl. 1995 Nr. 17 S. 450). 날짜는 조문에 박혀 있고
    feiertage-api 2026 BW 대조 일치
  ```
  BW 의 다른 11 건은 머리 주석(`solar_holidays.yaml:12–16`)에 공포본을 두고 항목 source 가 그 sha256 을 반복한다:
  ```
  # 현행 자구의 인쇄본: Bekanntmachung der Neufassung des Feiertagsgesetzes vom
  #   8. Mai 1995, GBl. 1995 Nr. 17 (30.06.1995) S. 450–452, Gliederungs-Nr. 1134.
  #   https://www.landtag-bw.de/resource/blob/75054/19739a8ea1fb5eee00898b30364b0f93/GBl199517.pdf
  #   sha256 98f68c3039ac0a2df4f9ffc2417aa3f3ef25669c19a6b72e08c15f8f85d4fb94 (2,407,426 B,
  #   OCR 텍스트층 + S. 450 페이지 이미지 육안 대조, 구현 세션에서 재수령해 sha256 일치).
  ```
- `rules/de_hh/solar_holidays.yaml:141–145` (reformationstag, #56 그 자체 — sha256 이 source 에 없음):
  ```
  source: >-
    Feiertagsgesetz(HH) § 1 Nr. 8 '31. Oktober' (통칭 Reformationstag) — Fünftes
    Gesetz zur Änderung des Feiertagsgesetzes vom 12.03.2018, HmbGVBl. 2018 Nr. 9
    S. 63 (20.03.2018 공포, luewu.de PDF 2026-09-07 열람). 날짜는 feiertage-api
    2026 HH 대조 일치
  ```
- 공식 sha256 게시가 있는 경로: `rules/de_ni/solar_holidays.yaml:15–16` 주석 「2024-01-01 부터는 verkuendung-niedersachsen.de(전자 공포, 정본, 호별 sha256 게시)다」, docs/holiday_15.md:158 「verkuendung-niedersachsen.de 가 공식 sha256 을 게시한다 — `/pubStore` … `/api/ndsgvbl/<yyyy>/<nr>` 메타·해시」. **그러나 그 경로를 실제 근거로 든 항목은 없다**(`grep -rn 공식 rules/de*/ | grep -i sha` → 0). 지금까지의 sha256 은 전부 조사자가 받은 파일에서 직접 잰 값이며, 「재수령 대조 일치」「Wayback 사본도 같은 sha256」을 결정성의 증거로 병기한다.

### D3. PDF 를 레포에 두는가

사실: 두지 않는다. `git ls-files | grep -i '\.pdf$'` → 0. README 「독일 — 각 주 관보: 수집 대상이 아닙니다」. `sources/` 에는 kr(KASI XML)·jp(CSV) 캐시만 있다.

### D4. 파일 해시가 아닌 형태의 해시 전례

사실: 없다. 레포의 sha256 은 전부 「받은 PDF 파일 전체」의 해시다. `grep -rn -i "이미지 스트림|스트림 해시|stream hash|md5|sha1"` 로 잡히는 것은 docs 의 md5(발행 .ics·업로드본 바이트 비교)뿐이며 근거 서지로 쓴 것은 아니다. 「텍스트층 없음, 이미지」인 공포본(BW 1994 Nr. 27)도 파일 해시로 적었다(`rules/de_bw/solar_holidays.yaml:25`).

## E. 자구 대조

### E1. 공포본 S. 890 의 Art. 2 원문

사실: PDF 에 텍스트층이 없다(C2). 아래는 **스캔(618×877, 1-bit)을 150 dpi 로 렌더해 육안 판독한 것**이다. `_gross`(400 dpi) 렌더로 재확인.

> Artikel 2
> Hauptstadt, Tag der Deutschen Einheit
> (1) Hauptstadt Deutschlands ist Berlin. Die Frage des Sitzes von Parlament und Regierung wird nach der Herstellung der Einheit Deutschlands entschieden.
> (2) Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag.

면 머리: 「890 Bundesgesetzblatt, Jahrgang 1990, Teil II」. 같은 면에 Kapitel I 「Wirkung des Beitritts」, Artikel 1 「Länder」, Kapitel II 「Grundgesetz」, Artikel 3·4 시작.

### E2. YAML 인용과의 대조

- `rules/de/solar_holidays.yaml:66–68` 의 `source`(YAML `>-` 접기 후 실제 값):
  `Einigungsvertrag Art. 2 Abs. 2 — 'Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag.' (gesetze-im-internet.de)`
- 따옴표 안 71 자를 육안 판독문 「Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag.」과 Python 으로 `==` 비교 → **True**(71 자, 비 ASCII 문자 없음). gesetze-im-internet XML 의 Art 2 본문에서 뽑은 같은 구절과도 `==` True.
- `rules/de_bw/solar_holidays.yaml:146–147` 도 같은 71 자.
- 주의: YAML 원문은 「Tag der\n      Deutschen」에서 줄이 접혀 있고, 파일 텍스트를 그대로 비교하면 개행+들여쓰기 때문에 False 가 난다. 비교는 로더를 거친 값으로 해야 한다.

### E3. Art. 2 의 개정 이력(통합본 기준)

사실(gesetze-im-internet XML `BJNR208890990.xml`, builddate 20260506175711):
- 문서 수준 `<standangabe>`: 「Zuletzt angepasst durch § 11 V v. 15.8.2022 I 1401」. `standangabe` 를 가진 norm 은 이 문서 수준 1 개뿐.
- `enbez="Art 2"` norm: `<standangabe>` 없음, `<fussnoten>` 없음. 본문 「(1) Hauptstadt Deutschlands ist Berlin. … (2) Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag.」
- 문서 각주: 「(+++ Textnachweis ab: 29.9.1990 +++) G v. 23.9.1990 II 885 In Kraft gem. Bek. v. 16.10.1990 II 1360 mWv 29.9.1990」.
→ **Art. 2 에 개정 기록 없음.** 미확인: 2022 개정(§ 11 V v. 15.8.2022)이 어느 조문을 건드렸는지는 보지 않았다(Art. 2 가 아닌 것만 확인).

## F. 영향 범위와 발행물

### F1. Einigungsvertrag 를 드는 자리 전수

사실(`grep -rn Einigungsvertrag` 와 `grep -rni einigungsvertrag`, feeds/ 제외; 두 결과의 파일 집합은 같고 건수만 tests 에서 다르다 — 상수 이름 `EINIGUNGSVERTRAG` 때문. `tests/test_de_ni_feed.py` ci 5/cs 3, `test_de_bw_feed.py` 7/5, `test_de_rp_feed.py` 5/3).

근거(`source` 필드) — **2 곳**:
| 파일:줄 | 성격 |
|---|---|
| `rules/de/solar_holidays.yaml:66–68` | 주근거, verified true |
| `rules/de_bw/solar_holidays.yaml:145–150` | rules/de **미러**(「rules/de 의 같은 항목을 미러」), verified true |

부기(`source` 안에 「연방 근거는 Einigungsvertrag Art. 2 Abs. 2 (rules/de)」류) — **7 곳**: `rules/de_by/solar_holidays.yaml:99`, `de_he:89`, `de_nw:99`, `de_sh:111`, `de_hh:124`, `de_ni:141`, `de_rp:161`. 이들의 주근거는 각 주법 조문이고 verified 값은 주법 쪽에 따른다. `rules/de_be` 는 언급 없음(umwelt-online 근거, verified false).

주석·문서·코드 — 근거가 아닌 서술: `rules/de/solar_holidays.yaml:32`, `rules/de_bw/solar_holidays.yaml:8,40,72`, `rules/de_ni/solar_holidays.yaml:11`, `rules/de_rp/solar_holidays.yaml:14`, `rules/de_bw/__init__.py:16`, `rules/de_ni/__init__.py:17`, `rules/de_rp/__init__.py:20`, `rules/de/feed.py:89`(주석), `README.md:65`, `docs/holiday_11.md:24`, `docs/holiday_14.md:103,122`, `docs/holiday_15.md:52–53,222`.

테스트 — `tests/test_de_feed.py:288`(docstring), `tests/test_de_bw_feed.py:10,21,43,146,446–458`, `tests/test_de_ni_feed.py:37,131,458,464–468`, `tests/test_de_rp_feed.py:45,150,484,490–494`.

발행물 — `feeds/de.ics`, `de_bw.ics`, `de_by.ics`, `de_he.ics`, `de_hh.ics`, `de_ni.ics`, `de_nw.ics`, `de_rp.ics`, `de_sh.ics` 각 12 줄(2020–2031 의 10-03 이벤트 DESCRIPTION). `de_be.ics` 0.

### F2. `source` 가 나가는 곳

사실:
- .ics: **DESCRIPTION** 속성. `rules/de/feed.py:160–170`:
  ```python
  description=f"{BUNDESWEIT_SENTENCE}\n\n근거: {_one_line(entry['source'])}",
  ```
  (`_one_line` 은 공백 정규화, `rules/de/feed.py:118–119`). 주 피드도 같은 꼴(`rules/de_bw/feed.py:149`). `verified`·`source_todo` 는 나가지 않는다(`tests/test_de_feed.py:266,308`).
- status.json: 나가지 않는다. `verification` 절은 kr 전용(`rules/kr/status.py:53–66`, `item_count 48 / unverified_count 32`); de 피드는 `feeds.de = {events, path, provisional_events, range}` 뿐.
- 랜딩: `landing/render.py` 가 쓰는 것은 `{item_count}·{unverified_count}`(kr) 뿐. `source` 문자열은 쓰지 않는다.

### F3. `source` 만 바꿨을 때 .ics 바이트와 SEQUENCE

실험: `git archive HEAD` 를 스크래치에 풀고 `rules/de/solar_holidays.yaml` 의 해당 `source` 끝 「(gesetze-im-internet.de)」만 「(BGBl. 1990 II Nr. 35 S. 890, TESTMARKER)」로 바꾼 뒤 `uv run python -m rules.de.feed` 로 재생성, 커밋본 `feeds/de.ics` 와 diff. 레포 원본은 건드리지 않았다.

사실:
- 바이트는 바뀐다. DTSTAMP 를 제외한 diff 는 24 줄 = 12 이벤트 × (before 1 줄 + after 1 줄), 전부 DESCRIPTION 의 접힌 연속 줄(「 licher Feiertag.' (gesetze-im-internet.de)」→「 licher Feiertag.' (BGBl. 1990 II Nr. 35 S. 890\, TESTMARKER)」; 쉼표는 RFC 5545 이스케이프 `\,`).
- UID 집합 동일. SUMMARY·DTSTART·DTEND·TRANSP 불변.
- **SEQUENCE: 108 건 전부 0 → 0.** 코드 근거 `core/ics.py:378–380`:
  ```python
  moved = prev.dtstart != event.day or prev.dtend != event.day + timedelta(days=1)
  sequence = prev.sequence + 1 if moved else prev.sequence
  ```
  SEQUENCE 는 날짜가 움직일 때만 오른다. DESCRIPTION 변경으로 올리는 경로는 없다(`core/ics.py:301–345` docstring 이 그 선택과 반론을 적어 둠).
- DTSTAMP 는 실행 시각으로 1 값 변경(20260907T100006Z → 실행 시각).
- de_bw 도 같은 코드 경로라 [추론] 동일(12 줄 DESCRIPTION, SEQUENCE 0). 부기 7 피드는 `source` 를 바꿀 때만 바뀐다.

### F4. verified 가 이미 true 인 상태에서 서지 형식만 바뀔 때 걸리는 테스트·집계

사실:
- `tests/test_published_feed.py:188–232` `test_the_published_feed_is_reproducible_from_the_committed_inputs[de|de_bw]` — 커밋된 .ics 를 지금 코드·데이터로 바이트 재현. **YAML 만 바꾸고 발행본을 재생성하지 않으면 실패**(마커 `published_artifact`).
- `tests/test_de_bw_feed.py:446–458` — de_bw 항목 source 에 `"Einigungsvertrag Art. 2 Abs. 2"`, 따옴표 포함 71 자 인용, `"§ 7 Abs. 2"` 가 있어야 하고 de 항목 source 에도 `"Einigungsvertrag Art. 2 Abs. 2"` 가 있어야 한다. 이 문자열들을 유지하는 한 통과.
- `tests/test_de_feed.py:287–296` — de 에서 true 는 tag_der_deutschen_einheit 하나뿐이어야 하고 `source_todo` 가 없어야 한다. 불변.
- `tests/test_de_ni_feed.py:464–468`, `tests/test_de_rp_feed.py:490–494` — **자기 피드**의 10-03 source 에 대해 「— 앞 구간에 gesetze-im-internet 이 없어야」 한다. de/de_bw 에 대한 같은 제약은 없다.
- 집계: status.json·랜딩의 verified 집계는 kr 전용(F2)이라 de 값 변화 없음. `docs/holiday_15.md:219–220` 「주 피드 아홉의 verified 현황은 true 36 / false 60」은 문서 서술이며 코드가 세지 않는다.
- verified 가 이미 true 이므로 true/false 개수를 세는 테스트는 어느 것도 바뀌지 않는다.

## 이전 조사와의 차이

| 이전 요약 | 이번 실측 | 판정 |
|---|---|---|
| recht.bund.de 는 2023 이후분만, 과거분은 bgbl.de | 동일. 원문 인용 확보(B1) | 일치 |
| bgbl.de 무료·무로그인, 도움말에 「speichern」 명시 | 동일. 다만 「speichern」은 6.4 PDF-Plugin 의 Acrobat 메뉴 설명 한 곳이고, 별도 이용 조건 문서는 없다(B2) | 일치 + 정밀화 |
| Nr. 35(1990-09-28) 호 전체 PDF S. 885–1248, Art. 2 Abs. 2 = S. 890 | 동일. 단위는 「호」가 아니라 attr_id(문서) 단위이고 이 문서가 호 전체와 겹친다. `_gross` 변형(361 면, JBIG2)이 따로 있다(B3) | 일치 + 정밀화 |
| Bek. 1990-10-16, Nr. 40, S. 1360 | 동일. Ausgabetag 26.10.1990 추가(A2) | 일치 |
| 파일 sha256 매번 다름(라이브 2, Wayback 3) | 동일(C1). 원인은 **AES-128 암호화(파일별 키) + /ID + /Info + xref 스트림**으로 특정(C2). 이전 요약은 원인을 적지 않았다 | 일치 + 원인 |
| 페이지 이미지 스트림 해시 전부 같음 `6de8685b…`; 어느 면·어떤 바이트인지 기록 없음 | 스트림 해시가 사본 간 같다는 결론은 동일. **그러나 값 `6de8685b…` 는 이번에 잰 어느 값과도 다르다** — (a0) 다섯 값, (a) `0f70b21d…`, (b) `ad7c2447…`, (b′) `d0ee47f4…`, 호 전체 연결 `b24082d8…` 모두 아님. 이전 값의 대상(면·바이트 수준·디코더·표현)을 알 수 없어 재현 불가. 이번 값은 면(p.6 = S. 890)·객체(35,0)·수준(a/b)·도구·표현 규약을 전부 적었다(C3–C5) | **불일치(값)**. 실측을 따른다 |
| 자구 완전 일치, Art. 2 개정 없음 | 동일(E2, E3) | 일치 |
| 영향: 근거 2, 발행물 2, 부기 7 | 동일(F1). 테스트·주석·문서 자리는 추가로 열거 | 일치 |

## 결정에 걸리는 사실

1. **공식 경로에서 받을 수 있고 저장이 허용되는가.**
   - recht.bund.de 가 1949–2022 열람처로 bgbl.de(Bundesanzeiger Verlag GmbH)를 지정한다(B1 원문).
   - bgbl.de 는 로그인·결제 없이 세션 쿠키만으로 PDF 를 준다. 첫 화면 「frei zugängliche Archiv」, JSON-LD `isAccessibleForFree: True`, 도움말 6.4 「drucken, speichern」, PDF 권한 플래그 인쇄·추출 허용(B2).
   - 이용 조건·라이선스 문서는 사이트에 없다. 재사용·재배포 문구도 없다(B2).
   - PDF 바이트에 닿는 URL 은 세션 종속이라 영구가 아니다. 인용 가능한 안정 URL 은 `start.xav?startbk=Bundesanzeiger_BGBl&jumpTo=bgbl290s0885.pdf`(B3). Wayback 에 2021·2021·2023 원본 바이트 사본 3 벌이 있다(B4).

2. **파일 해시가 결정적인가. 아니라면 사본 간 일치하는 해시와 재현 명령.**
   - 파일 sha256 은 **비결정적**(요청마다 새 PDF, AES 키·/ID·/Info·xref 가 바뀜). 5 벌 5 값(C1, C2).
   - 사본 간 일치하는 값(5 벌, 2021–2026, 라이브·Wayback):
     - (a) S. 890(PDF p.6) 이미지 객체 (35,0) 의 **복호화 후·미디코드 CCITT G4 스트림** 19,643 B: `0f70b21d7715670a0db1d9433d8ea04ff534a7e53d3f40521301db6d8a92a6af` — pikepdf·pypdf 교차 일치.
     - (b) 같은 이미지를 **디코드한 1-bit 비트맵**(행 바이트 정렬, 1 = 검정, 패딩 0) 68,406 B: `ad7c2447f4c95486de22a5698fc7cd3bc2c0830255a6950d348f5a7be08cfb30` — pdfminer.six·MuPDF 교차 일치. (8-bit gray 표현이면 `d0ee47f4…2047`.)
     - 호 전체(364 면) (a) 해시 연결: `b24082d8bc6f36f89cd65fc5bd2e9ef492ec617c5a271fc5756393094e4ff602`.
   - 디스크 바이트 그대로의 스트림 해시 (a0) 는 사본마다 다르다 — 「인코딩된 스트림 바이트 그대로」를 문자 그대로 잡으면 결정적이지 않다.
   - 재현 명령·도구 버전은 C5. 스크립트 `~/holidays-reports/bgbl1990/hash_page.py`.
   - 레포의 sha256 전례는 전부 파일 해시이고, 파일 해시가 아닌 형태의 전례는 없다(D4). 공식 게시 해시를 든 항목도 없다(D2).
   - `_gross`(400 dpi, JBIG2, 361 면) 변형은 별개 파일이며 결정성은 재수령하지 않아 미확인.

3. **구현이 건드릴 자리의 수와 발행물 변경 여부.**
   - `source` 근거 2(rules/de, rules/de_bw 미러). 부기 7 은 문구를 바꾸기로 할 때만.
   - 발행물: `feeds/de.ics`·`feeds/de_bw.ics` 각 12 이벤트의 DESCRIPTION 바이트가 바뀐다. **SEQUENCE 는 오르지 않는다**(날짜 불변, `core/ics.py:378–380`). UID 불변. `test_published_feed` 때문에 발행본 재생성이 같은 PR 에 있어야 한다(F3, F4).
   - status.json·랜딩 무영향(F2). verified 개수 집계 무변화(F4).
   - 자구는 공포본 스캔 육안 판독·통합본·YAML 71 자 모두 동일(E2). Art. 2 개정 없음(E3).
   - 공포본은 텍스트층이 없는 75 dpi 스캔이라 「원문 확인」은 육안 판독이다(E1). `_gross` 400 dpi 로 재확인 가능.
