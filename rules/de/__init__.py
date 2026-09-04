"""독일 공휴일 규칙 — 전국 공통(bundeseinheitlich) 9 건.

주별(Bundesland) 공휴일은 여기 없다. 이 피드는 16 개 주 전체에서 유효한
법정 공휴일만 싣는다. 주별 항목은 별도 피드의 몫이다.

대체공휴일(이동) 규칙도 없다. substitute 계열 모듈을 두지 않는다 — BayFTG
전문에 이동 조항이 없고, 일요일과 겹친 해(2021·2022·2023·2027)의 실측에서
보상 휴일이 0 건이다(solar_holidays.yaml 머리 주석).

날짜는 두 표에서 온다.
    solar_holidays.yaml    고정 날짜 5 건
    easter_holidays.yaml   부활절 기준 오프셋 4 건
부활절 자체는 python-dateutil 의 easter() 가 계산한다(rules/de/feed.py).
"""
