# drafts — de_sn 표 초안 (적용하지 않음)

**초안이다. 레포에 적용하지 않았다.** 설계안 (ii)(대림절 첫째 주일 기준 오프셋, `advent_offset`)를 고른다면의 꼴만 보인다.
- 항목 11 건: 고정 6(`de_sn_solar_holidays.yaml`) + 부활절 이동 4(`de_sn_easter_holidays.yaml`) + 대림절 기준 1(`de_sn_advent_holidays.yaml`).
- Fronleichnam(지정 지역만)은 범위 밖이라 없다.
- key `buss_und_bettag` 는 예고만 된 값이다(`rules/de/solar_holidays.yaml:23–24`). 승인 전이다 — 보고 판단 요청 1.
- `source` 의 서지는 이 조사(2026-11-18)의 관측이다. 머리 주석은 구현 PR 이 쓴다.
- verified 는 전부 false 로 두었다 — 공포본(1992 원법·2002 개정)을 받지 못했다(보고 B3).
