# ruff: noqa
"""B2 실험: 독일 로더(rules/de_bb/feed.py 복제 계열)가 모르는 필드 valid_from 을 어떻게 다루는가.
레포 파일은 고치지 않는다 — 임시 YAML 을 만들고 모듈의 SOLAR_PATH 만 바꿔 본다."""
import datetime as dt, pathlib, sys, tempfile
import yaml
from rules.de_bb import feed

tmp = pathlib.Path(tempfile.mkdtemp())
src = yaml.safe_load(feed.SOLAR_PATH.read_text(encoding="utf-8"))
src["holidays"].append({"key": "frauentag", "name": "Frauentag", "scope": "land", "month": 3, "day": 8,
                        "valid_from": dt.date(2023, 1, 1), "verified": False, "source": "test"})
p = tmp / "solar_holidays.yaml"
p.write_text(yaml.safe_dump(src, allow_unicode=True), encoding="utf-8")
loaded = feed._load(p, "month", "day")
print("load ok; frauentag entry keys:", sorted(next(e for e in loaded if e["key"] == "frauentag")))
feed.SOLAR_PATH = p
for y in (2020, 2022, 2023):
    days = [e.day for e in feed.events(dt.date(y, 1, 1), dt.date(y, 12, 31)) if e.token.endswith("frauentag")]
    print(y, days)
