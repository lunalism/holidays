#!/bin/sh
# C — SYNTHETIC. 스크래치 워크트리(인자 1)의 rules/ 에 주 피드 7 개를 흉내 낸 최소 모듈을 넣는다.
# render 는 rules/ 스캔(feed_codes)으로 피드를 찾고, 주 피드 줄은 FEED_PATH·CALNAME·LAND_NAME·
# LAND_NAME_DE 만 읽는다(render.py::_row). 그 넷만 둔다. 커밋하지 않는다 — 워크트리는 측정 뒤 버린다.
set -eu
WT="$1"
while IFS='|' read -r code ko de; do
  mkdir -p "$WT/rules/$code"
  : > "$WT/rules/$code/__init__.py"
  cat > "$WT/rules/$code/feed.py" <<PY
# SYNTHETIC — noscript 중복 측정용. 레포에 들이지 않는다.
from pathlib import Path
CALNAME = "독일·$ko 공휴일"
LAND_NAME = "$ko"
LAND_NAME_DE = "$de"
FEED_PATH = Path(__file__).resolve().parents[2] / "feeds" / "$code.ics"
PY
done <<LIST
de_bb|브란덴부르크|Brandenburg
de_hb|브레멘|Bremen
de_mv|메클렌부르크포어포메른|Mecklenburg-Vorpommern
de_sl|자를란트|Saarland
de_sn|작센|Sachsen
de_st|작센안할트|Sachsen-Anhalt
de_th|튀링겐|Thüringen
LIST
