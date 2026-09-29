# 2024-07-10 이후 개정 탐색 — PARDOK(베를린 주의회 의회 문서 시스템)

2026-09-29 실행. 공개 검색 화면(`https://pardok.parlament-berlin.de/portala/browse.tt.html`)을
headless Chromium(Playwright, 레포 dev 의존성)으로 열고, 화면의 검색 칸
(`searchgeneric1-text`)에 검색어를 넣고 선거기 19(2021-11-04~)를 골라 실행했다.
로그인·인증 없음. 스크립트는 `scripts/`.

## 검색어와 결과 (선거기 19, 문서 전 종류)

화면이 만든 질의(`searchgeneric1-parsed`)는 제목·주제·요지·서술 필드(WEBUW·WEBTW·WEBSW·
WEBAW·WEBFW 등)와 번호·시소러스를 본다. 예: `Feiertage` →
`((/WP 19) AND (((/WEBUW,WEBTW,WEBSW,WEBAW,WEBFW ("Feiertage*") OR … ))) AND TYP=DOKDBE`.

| 검색어 | 적중 |
|---|---|
| Feiertage | 5 |
| Sonn- und Feiertage | 4 |
| Feiertagsgesetz | 2 |
| Frauentag | 1 (Antrag 19/2280 — 입법 아님) |
| Feiertag | 114 |
| Gedenktag | 44 |

`Feiertag`(114) 전체를 Vollanzeige 로 펼쳐 법률안(Gesetzentwurf)만 추리면 넷이다.

| Drucksache | 무엇 | 바꾸는 곳 | 상태(2026-09-29 PARDOK) |
|---|---|---|---|
| 19/1359 (05.12.2023, Senatsvorlage) | Viertes Gesetz zur Änderung … | § 1 Abs. 1 Nr. 10·11 | Angenommen, Gesetz vom 10.07.2024 — GVBl. 2024 Nr. 28 S. 460 그 자체 |
| 19/0947 (18.04.2023, AfD) | 17. Juni 2023 일회성 | § 1 Abs. 1 | Zurückgezogen(II. Lesung 12.09.2024 기록) |
| 19/2729 (07.11.2025, Grüne) | Fünftes Gesetz zur Änderung … (유대교 축일 보호) | § 2 Abs. 1·2 변경·Abs. 3 삽입, § 3 삽입, §§ 3–6 → 4–7 | I. Lesung 20.11.2025, 위원회 셋 모두 "Beratung ist (noch) nicht erfolgt" — 법률 아님 |
| 19/1496 (27.02.2024, Grüne) | Drittes Gesetz zur Änderung des Berliner Ladenöffnungsgesetzes | 다른 법률 | — |

## 가결 법률 전수(선거기 19)

PARDOK 이 화면에 두는 정형 질의 "angenommene Gesetzentwürfe WP 19"(Vorgangstyp
Gesetzentwurf AND Status angenommen)를 Vollanzeige·한 쪽 전체로 펼쳤다.

- 204 건. "Gesetz vom" 날짜는 2022-02-07 ~ 2026-09-03, 그중 2024-07-10 이후 109 건.
- 이 204 건의 서술에서 `feiertag`·`sonn- und` 가 나오는 것은 19/1359(2024 개정) 하나다.

## 한계

- PARDOK 의 서술 필드(제목·요지·변경 조항 요약)를 본 것이다. 옴니버스 법률의 전문(각
  조항 본문)을 하나하나 읽지는 않았다 — 어느 옴니버스 법률이 서술에 적지 않고
  Feiertagsgesetz 를 고쳤다면 이 탐색은 그것을 놓친다.
- 상태는 2026-09-29 의 PARDOK 표기다. 19/2729 가 뒤에 가결되더라도 § 1 이 아니라 § 2·§ 3
  을 바꾸는 안이다.
