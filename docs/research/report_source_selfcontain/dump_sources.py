# ruff: noqa
"""A — 독일 규칙 YAML 의 모든 항목을 (file, key, verified, source 한 줄) 로 뽑는다.
source 한 줄은 feed.py::_one_line 과 같은 정규화(공백 연속 → 한 칸, strip)다 — DESCRIPTION 에 실리는 문면.
사용: uv run python dump_sources.py > sources.tsv   (레포 루트에서)"""
import re
import sys
from pathlib import Path

import yaml

WS = re.compile(r"\s+")
out = sys.stdout
out.write("file\tkey\tdate_or_rule\tverified\tsource\n")
for path in sorted(Path("rules").glob("de*/*.yaml")):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for e in data["holidays"]:
        when = e.get("date") or (f"{e.get('month')}-{e.get('day')}" if "month" in e else f"easter{e.get('offset', '')}")
        src = WS.sub(" ", (e.get("source") or "").strip())
        out.write(f"{path}\t{e['key']}\t{when}\t{e.get('verified')}\t{src}\n")
