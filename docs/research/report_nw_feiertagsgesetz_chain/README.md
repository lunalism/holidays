# report_nw_feiertagsgesetz_chain — 재현 기록

`docs/research/report_nw_feiertagsgesetz_chain.md` 의 전사본과 스캔 산출물이다. 보고
본문은 조사 당시의 스크래치 디렉터리를 `$S` 로 가리킨다. 그 경로는 세션이 끝나면
사라지므로, 옮겨 온 파일의 대응을 아래에 적는다.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않고 레포 의존성도 아니다.**
실행은 `uv run --no-project --with …` 격리 실행과 macOS Vision OCR 을 전제로 한다.

## 경로 대응

| 보고의 경로 | 이 폴더 | 비고 |
|---|---|---|
| `$S/transcripts/1989_S222_par2.txt` | `1989_S222_par2.txt` | GV. NW. 1989 S. 222 § 2 전사 |
| `$S/transcripts/1991_S200_artI.txt` | `1991_S200_artI.txt` | GV. NW. 1991 S. 200 Art. I–II 전사 |
| `$S/transcripts/1994_S1114_artI.txt` | `1994_S1114_artI.txt` | GV. NW. 1994 S. 1114 표제~Art. II 전사 |
| `$S/transcripts/current_par2abs1_by_chain.txt` | `current_par2abs1_by_chain.txt` | 세 호를 적용한 § 2 Abs. 1 현행 자구 |
| `$S/transcripts/1977_S98_par2abs1.txt` | (옮기지 않음) | 보조 대조용 |
| `$S/png/*.png` | (옮기지 않음) | `render_pngs.py` 로 다시 만든다 |
| `$S/pdf/*.pdf` 등 | (옮기지 않음) | PDF 는 레포에 두지 않는다 |
| `$S/scan9096/result.tsv` | `scan9096/result.tsv` | 1990–1996 전 512 호 탐색 결과 |
| `$S/scan9096/berichtigung_ctx.tsv` | `scan9096/berichtigung_ctx.tsv` | Berichtigung 적중의 앞뒤 문맥 |
| `$S/scan9096.py` | `scan9096/scan9096.py` | 탐색 스크립트(재개판) |
| `$S/reber.py` | `scan9096/reber.py` | 문맥 재추출 스크립트 |
| `$S/ocr.swift` | `scan9096/ocr.swift` | Vision OCR(스크립트가 `./ocrbin` 으로 부른다) |
| — | `2021_nr75a_page_continuity.md` | 2021 Nr. 75a 주변 호의 면 범위·PDF sha256 |
| — | `render_pngs.py` | PNG 재현 스크립트 |

전사본 머리의 `png/…` 는 `render_pngs.py` 가 만드는 파일 이름과 같다.

## PNG 재현

PDF 세 벌을 받아 sha256 을 맞춘 뒤 렌더한다. 명령과 sha256 은 `render_pngs.py`
머리에 있다(sha256 의 정본은 `rules/de_nw/solar_holidays.yaml` 머리 주석).

    uv run --no-project --with pymupdf==1.26.5 python render_pngs.py

같은 크기의 PNG 가 나오지만 조사 때의 PNG 와 바이트가 같다는 보장은 없다(MuPDF 의 이미지
저장소 상태 차이, `render_pngs.py` 머리 참조). 판독 대조용이다.

## 1990–1996 정오표 탐색(scan9096)

- `result.tsv` 열: 연도, 호, 방식(`textlayer` = PDF 텍스트층 전문, `vision-p1` =
  텍스트층이 없어 1 쪽만 Vision OCR), Berichtigung 적중 수, Feiertag 적중 문맥,
  (재개 뒤 행만) Berichtigung 문맥.
- 첫 실행은 1993 Nr. 71 다운로드 중 끊겼다(ContentTooShortError). 그 앞 270 행은
  첫 판 스크립트가 썼고, 재개판(`scan9096.py`, 재시도·Content-Length 검사·완료 행
  건너뛰기)이 나머지를 채웠다. 첫 판 행의 Berichtigung 문맥은 `reber.py` 가 로컬
  PDF 에서 다시 뽑아 `berichtigung_ctx.tsv` 에 합쳤다.
- 완결성: 연도별 행 수가 색인의 호 수와 같다(1990 75 · 1991 62 · 1992 63 ·
  1993 82 · 1994 89 · 1995 80 · 1996 61, 합 512). NOPDF·NETFAIL 0.
- 한계: `vision-p1` 327 호는 1 쪽 목차만 읽었다 — 목차에 오르지 않고 뒤쪽 면에만
  실린 정오표는 놓칠 수 있다.
- 1989 Nr. 20–69 는 같은 방식의 별도 탐색(텍스트층 전문, Nr. 56·64 는 목차)으로
  보았고 그 산출물은 여기 없다(보고 C3).
