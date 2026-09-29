# report_he_be_gazette_access — 재현 기록

`docs/research/report_he_be_gazette_access.md` 의 판독 전사본과 탐색 산출물이다. 보고
본문은 조사 당시의 스크래치 디렉터리를 `$S` 로 가리킨다. 그 경로는 세션이 끝나면
사라지므로 옮겨 온 파일의 대응을 아래에 적는다.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않고 레포 의존성도 아니다.**
실행은 `uv run --no-project --with pymupdf==1.26.5 …` 격리 실행과 macOS Vision OCR
(`scan/ocr.swift` 를 `swiftc -O ocr.swift -o ocrbin` 으로 빌드)을 전제로 한다.

## 경로 대응

| 보고·조사의 경로 | 이 폴더 | 비고 |
|---|---|---|
| `$S/transcripts/1971_S344_par1abs1.txt` | `1971_S344_par1abs1.txt` | GVBl. 1971 I Nr. 36 S. 344 § 1 Abs. 1 전사 |
| `$S/transcripts/1994_S596_artI.txt` | `1994_S596_artI.txt` | GVBl. 1994 I Nr. 25 S. 596 Art. 1(서두·§ 1 부분) 전사 |
| `$S/transcripts/current_par1abs1_by_chain.txt` | `current_par1abs1_by_chain.txt` | 1994 를 1971 에 적용한 § 1 Abs. 1 현행 자구 |
| `$S/png/1971_S344_par1.png`·`$S/png/1994_S596_artI.png` | (옮기지 않음) | `render_pngs.py` 로 다시 만든다(2026-09-29 대조: 두 장 모두 바이트 동일) |
| `$S/he/issues_scan.tsv` | `scan/issues_scan.tsv` | 2010–2026 전 776 호 검색(775 호 텍스트층 전문, 2012 Nr. 16 은 1 쪽 목차 OCR) 결과(연도, 호, 텍스트 길이, Feiertag 적중 문맥) |
| `$S/he/inhalt_ocr.tsv` | `scan/inhalt_ocr.tsv` | 1952–2009 연간 색인 777 쪽 OCR 적중(연도:쪽, 텍스트 길이, 문맥) |
| `$S/he_scan.py` | `scan/he_scan.py` | 2010–2026 호별 검색(재시도·Content-Length 검사) |
| `$S/ocr_inhalt.py` | `scan/ocr_inhalt.py` | 연간 색인 전 쪽 Vision OCR |
| `$S/he_toc.py`·`$S/he_find.py` | `scan/he_toc.py`·`scan/he_find.py` | 호 1 쪽 목차 읽기·호 안에서 개정 조문 면 찾기 |
| `$S/../nw/ocr.swift` | `scan/ocr.swift` | Vision OCR 소스(NW 조사와 같은 것) |
| `$S/starweb_gvbl.html` | (옮기지 않음) | starweb 호 목록 면(2.6 MB). `he_scan.py` 가 여기서 링크를 읽는다 — `https://starweb.hessen.de/portal/browse.tt.html?action=gvbl` 에서 다시 받는다 |
| `$S/he/**/*.pdf`, `$S/hejs/` | (옮기지 않음) | PDF·포털 JS 번들은 레포에 두지 않는다 |

BE 조사분(PARDOK·berlin.de 사본)은 이 폴더에 없다 — BE 승격 PR 몫이다.

## PNG 재현

PDF 두 벌을 받아 sha256 을 맞춘 뒤 렌더한다. 명령과 sha256 은 `render_pngs.py`
머리에 있다(sha256 의 정본은 `rules/de_he/solar_holidays.yaml` 머리 주석).

    uv run --no-project --with pymupdf==1.26.5 python render_pngs.py

## 탐색 범위와 한계

- 1952–2009: 연간 색인(`inhalt.pdf`)의 「Feiertag」 항목. 1952–2003·2008–2009 는 스캔이라
  전 쪽 Vision OCR, 2004–2007 은 텍스트층. 색인은 옴니버스 개정(1974)을 이 항목에
  올리지 않았다 — 체인은 개정 공포본 서두의 자기 인용으로 세웠다.
- 2010–2026: `scan/issues_scan.tsv` 가 전 호 텍스트층 전문 검색이다(2026 Nr. 65,
  28.09.2026 까지). 텍스트층이 없는 2012 Nr. 16 은 1 쪽 목차만 OCR 로 봤다.
  2013–2022 는 연간 색인(`00000.pdf`)도 있고, 2023–2026 은 연간 색인이 없어 이 검색만
  근거다.
