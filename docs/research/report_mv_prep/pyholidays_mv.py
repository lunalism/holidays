# ruff: noqa
"""B4: 고정된 python-holidays 의 DE(subdiv='MV') 2020~2031 — 해마다 건수와 3월 8일·이름."""
import importlib.metadata as m
import holidays
print("holidays", m.version("holidays"))
for y in range(2020, 2032):
    h = holidays.DE(subdiv="MV", years=y)
    mar8 = [(d.isoformat(), n) for d, n in sorted(h.items()) if d.month == 3 and d.day == 8]
    print(y, len(h), mar8)
h = holidays.DE(subdiv="MV", years=2026)
for d, n in sorted(h.items()):
    print(" ", d, n)
