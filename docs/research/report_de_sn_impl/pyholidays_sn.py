"""python-holidays(레포 고정판) DE(subdiv='SN') 2020–2031 해마다의 목록.

사용: uv run python pyholidays_sn.py > pyholidays_sn.out
"""
import importlib.metadata

import holidays

print("holidays", importlib.metadata.version("holidays"))
for year in range(2020, 2032):
    days = holidays.DE(subdiv="SN", years=year)
    print(year, len(days), "; ".join(f"{d.isoformat()} {n}" for d, n in sorted(days.items())))
