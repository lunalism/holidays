# be_2019 — BE 2019·2024 개정 관보 면의 증거

`rules/de_be` 의 frauentag·achter_mai_2020(GVBl. für Berlin 2019 Nr. 3 S. 22)과
achter_mai_2025·siebzehnter_juni_2028(2024 Nr. 28 S. 460)의 근거 자료다. PDF 는 두지
않는다 — URL 과 sha256 으로 다시 받는다.

**`scripts/` 는 재현 기록이다. CI 는 돌리지 않고 레포 의존성도 아니다.**

| 파일 | 내용 |
|---|---|
| `transcripts_par1.txt` | 두 호에서 § 1 Abs. 1 에 닿는 조항만 추린 전사 |
| `2019_S22_full_textlayer.txt`·`2024_S460_full_textlayer.txt` | 두 PARDOK PDF 의 텍스트층 그대로 |
| `comparison_2019_S22.md` | PARDOK 발췌와 berlin.de 판 호 전체(Wayback)의 S. 22 대조 — 텍스트·렌더 동일 |
| `pardok_search_2024_2026.md` | 2024-07-10 이후 개정 탐색 기록(검색어·적중·가결 법률 전수·한계) |
| `scripts/pw_form.py` | 검색 화면에 검색어를 넣어 실행하고 결과 쪽 텍스트를 저장 |
| `scripts/pw_feiertag_full.py` | `Feiertag` 적중 전체를 Vollanzeige 로 펼쳐 저장·법률안 추림 |
| `scripts/pw_adopted_full.py` | 가결 법률(선거기 19) 전수를 펼쳐 저장·`feiertag` 검색 |

두 PDF(2026-09-29 수령, 재수령 sha256 동일):

- 2019: `https://pardok.parlament-berlin.de/starweb/adis/citat/VT/18/gvbl/g19030022.pdf`
  sha256 `714f8bfc1cb1ac1babe023519d62b02546bd2310dfe8429ce452cce380bc85e2`
- 2024: `https://pardok.parlament-berlin.de/starweb/adis/citat/VT/19/gvbl/g24280460.pdf`
  sha256 `750494cd72ff03c5259022a396f2641be42ac6aff5b1d5367c2994c469503353`

2024-07-10 이후 탐색의 요지와 한계:

- PARDOK 서술 필드 검색과 선거기 19 가결 법률 204 건 전수에서 2024 개정 뒤의
  Feiertagsgesetz 개정 법률을 찾지 못했다.
- 이 탐색은 PARDOK 의 서술 필드를 본 것이고, 옴니버스 법률의 전문은 읽지 않았다.
- Drs. 19/2729(Grüne, 2025-11-07)는 § 2·§ 3 을 바꾸는 개정안이고 위원회 심의 전이다
  (법률 아님).
- Drs. 19/0947(AfD, 2023)은 § 1 Abs. 1 의 17. Juni 2023 일회성 안이었고 철회됐다.

## 정정 — 상위 보고의 "두 판" 서술

`../../report_he_be_gazette_access.md` [D] 표의 berlin.de 2019 Nr. 3 행은 Wayback 에서
"다른 digest·약 1.02 MB 캡처 둘"을 들어 "같은 URL 이 두 판을 낸 적이 있다"고 적었다.
그 보고는 날짜가 박힌 기록이라 고치지 않고 여기서 바로잡는다.

| Wayback 캡처 | digest(SHA-1 base32) | 받은 크기 | 열림 |
|---|---|---|---|
| 20220111073510(다수, 7 개 200 캡처 중 5 개가 이 digest) | `VPXJJABRWABBHO2ENFKXPYNZJ5K5HJ2P` | 1,701,342 B | 12 쪽 |
| 20190720185641(소수) | `HYT7OYMXSSRLKV75C2BLI6UU3GNWHYMD` | **1,048,576 B(= 1 MiB)** | **0 쪽** — 스트림 중간에서 끝남 |
| 20210506194614(소수) | `HYT7OYMXSSRLKV75C2BLI6UU3GNWHYMD`(CDX 표기) | 받지 않음 — digest 가 위 캡처와 같다 | — |

소수 digest 는 1 MiB 에서 잘린 캡처다. berlin.de 가 다른 판을 낸 증거가 아니다.
