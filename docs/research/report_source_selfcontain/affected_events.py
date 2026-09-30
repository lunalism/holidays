# ruff: noqa
"""E — 바뀔 source 항목(범주별)이 발행본에서 몇 개 이벤트의 DESCRIPTION 에 실리는지 센다.
UID = {YYYYMMDD}-{token}@…, token = key(de) 또는 <feed>-<key>(주 피드). 레포 루트에서 실행."""
import re
from collections import Counter, defaultdict
from pathlib import Path

AFFECTED = {  # feed: {key: [categories]}
    "de": {"tag_der_deutschen_einheit": ["C2", "C5"]},
    "de_bw": {"tag_der_deutschen_einheit": ["C1", "C2", "C3"], "fronleichnam": ["C4", "C5"],
              "heilige_drei_koenige": ["C4", "C5"], "allerheiligen": ["C4", "C5"],
              **{k: ["C5"] for k in ("karfreitag", "ostermontag", "christi_himmelfahrt", "pfingstmontag",
                                     "neujahr", "erster_mai", "erster_weihnachtstag", "zweiter_weihnachtstag")}},
    "de_by": {"tag_der_deutschen_einheit": ["C1"]},
    "de_hh": {"tag_der_deutschen_einheit": ["C1", "C3"], "reformationstag": ["D"]},
    "de_ni": {"tag_der_deutschen_einheit": ["C1", "C3"]},
    "de_nw": {"tag_der_deutschen_einheit": ["C1", "C3"], "erster_mai": ["C3"], "allerheiligen": ["C4"]},
    "de_rp": {"tag_der_deutschen_einheit": ["C1"], "christi_himmelfahrt": ["C3"], "fronleichnam": ["C3", "C4"],
              "allerheiligen": ["C3", "C4"], "erster_weihnachtstag": ["C6"], "zweiter_weihnachtstag": ["C6"]},
    "de_sh": {"tag_der_deutschen_einheit": ["C1", "C3"]},
}
uid_re = re.compile(r"^UID:(\d{8})-(.+?)@", re.M)
for feed, keys in AFFECTED.items():
    text = Path(f"feeds/{feed}.ics").read_text(encoding="utf-8")
    tokens = [t for _, t in uid_re.findall(text)]
    total = len(tokens)
    per = Counter()
    years = defaultdict(set)
    for (d, t) in uid_re.findall(text):
        key = t if feed == "de" else t.removeprefix(feed + "-")
        if key in keys:
            per[key] += 1
            years[key].add(d[:4])
    hit = sum(per.values())
    print(f"{feed}\tevents_total={total}\tchanged={hit}\t" + ", ".join(f"{k}={per[k]}({min(years[k])}-{max(years[k])})" for k in keys))
