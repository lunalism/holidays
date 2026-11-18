# report_de_sn_impl — de_sn 구현 때의 확인 기록

de_sn(작센 피드) 구현 PR 의 사전 확인 P1·P3 에서 돌린 것과 출력이다. 별도 보고서는 없다 — `report_de_mv_impl/` 과
같은 꼴이다. 결과는 `rules/de_sn/solar_holidays.yaml` 머리 주석과 PR 본문에 있다. 조사 당시 경로는
`~/holidays-reports/report_de_sn_impl/` 이다. 2026-11-18(UTC 08:00:21Z–08:00:25Z), `origin/main` `38c8db2` 기준.

**이 폴더의 스크립트는 재현 기록이다. CI 는 돌리지 않는다.**
- 요청 둘(`fetch.log`)은 `report_sn_prep/fetch.sh` 의 복사본(`fetch.sh`)으로 보냈다.
- 텍스트 추출은 `report_sn_prep/extract_revosax.py` 를 그대로 썼다(이 폴더에 복사하지 않았다):
  `uv run --no-project --with 'pypdf==5.4.0' python ../report_sn_prep/extract_revosax.py <pdf> text/revosax_3997_48138_p1.txt`

| 파일 | 무엇 |
|---|---|
| `fetch.sh`·`fetch.log` | P1 — REVOSax 화면(Stand·Fassung 줄)과 통합본 PDF 한 번 |
| `text/revosax_3997_48138_p1.txt` | P1 — PDF 텍스트층과 sha256. 전문 `4f9b905c…`, § 1 `5e6fdcb4…`, § 2 `fed4093e…` — `report_sn_prep` 의 두 추출과 같다. PDF 자체도 53,502 B, sha256 `93d9dc8b…` 로 같다 |
| `pyholidays_sn.py` → `.out` | P3 — holidays 0.102 DE(subdiv='SN') 2020–2031. `report_sn_prep/pyholidays_sn.out` 과 바이트가 같다 |

- 화면 HTML 과 PDF 는 scratch(`<scratch>/de_sn_impl/`)에만 두었다(`docs/research/README.md` 「넣지 않는 것」).
- P2(key 대응)는 레포 안의 `grep` 이라 이 폴더에 출력이 없다 — PR 본문의 표.
