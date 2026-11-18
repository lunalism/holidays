"""P4 — python-holidays(레포 고정판) DE(subdiv='MV') 2020–2031 해마다의 목록.

사용: uv run python pyholidays_mv.py > pyholidays_mv.out
"""
import importlib.metadata

import holidays

print("holidays", importlib.metadata.version("holidays"))
for year in range(2020, 2032):
    days = holidays.DE(subdiv="MV", years=year)
    print(year, len(days), "; ".join(f"{d.isoformat()} {n}" for d, n in sorted(days.items())))
