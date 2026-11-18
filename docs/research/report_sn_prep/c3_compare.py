# ruff: noqa
"""C3 — Buß- und Bettag 의 날짜 관행 셋을 1990–2100 에 계산해 비교한다.

사용: uv run python c3_compare.py > c3_compare.tsv  (레포 루트에서, holidays·python-dateutil 은 레포 고정판)
(a) 11월 23일보다 엄격히 앞선 마지막 수요일.
(b) 대림절 첫째 주일(11월 27일–12월 3일의 일요일)에서 11일 전 — SächsSFG § 2 의 Totensonntag(「letzter
    Sonntag vor dem 1. Advent」) 바로 앞 수요일.
(c) HE 1971·NW 1977/1989 조문의 꼴 「Mittwoch vor dem letzten Sonntag nach Trinitatis」. Trinitatis = 부활절
    + 56 일. 「Sonntag nach Trinitatis」 를 Trinitatis + 7k 로 세고, 대림절 첫째 주일 앞에서 끝난다고 둔다
    ([추론] — 교회력의 관행. 조문은 그 끝을 적지 않는다). 그 마지막 일요일 앞의 수요일.
python-holidays(고정판) DE(subdiv='SN') 의 「Buß- und Bettag」 날짜를 2020–2031 에 함께 적는다.
"""
import datetime as dt
import importlib.metadata

import holidays
from dateutil.easter import easter

WED = 2


def a(year):
    d = dt.date(year, 11, 22)
    while d.weekday() != WED:
        d -= dt.timedelta(days=1)
    return d


def advent1(year):
    d = dt.date(year, 11, 27)
    while d.weekday() != 6:
        d += dt.timedelta(days=1)
    return d


def b(year):
    return advent1(year) - dt.timedelta(days=11)


def c(year):
    trinitatis = easter(year) + dt.timedelta(days=56)
    last = None
    k = 1
    while True:
        s = trinitatis + dt.timedelta(days=7 * k)
        if s >= advent1(year):
            break
        last = s
        k += 1
    return last - dt.timedelta(days=4), k - 1  # 그 일요일 앞 수요일, 「n. Sonntag nach Trinitatis」 의 n


print(f"# holidays {importlib.metadata.version('holidays')}")
print("year\ta\tb\tc\tsundays_after_trinitatis\ta==b==c\tpython_holidays_SN")
for year in range(1990, 2101):
    ca, n = c(year)
    ph = ""
    if 2020 <= year <= 2031:
        days = [d for d, name in holidays.DE(subdiv="SN", years=year).items() if "Bettag" in name]
        ph = ",".join(d.isoformat() for d in days)
    same = a(year) == b(year) == ca
    print(f"{year}\t{a(year)}\t{b(year)}\t{ca}\t{n}\t{same}\t{ph}")
