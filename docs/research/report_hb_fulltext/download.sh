#!/bin/sh
# 사용: download.sh <listing.tsv> <pdf-dir>
# listing.tsv 에서 year >= 2020 이고 href 가 .pdf 인 줄을 순서대로 받는다. URL 은 목록의 href 를
# 그대로(이미 퍼센트 인코딩됨) https://www.gesetzblatt.bremen.de 뒤에 붙인 것이다 — 패턴으로 만들지 않는다.
# 이미 받은 파일(크기 > 0)은 건너뛴다. 간격·재시도는 fetch.sh 가 맡는다.
D=$(dirname "$0")
awk -F'\t' 'NR>1 && $1>=2020 && $5 ~ /\.pdf$/ {print $1"\t"$3"\t"$5}' "$1" |
while IFS='	' read -r y nr href; do
  out="$2/$(printf '%s_%03d.pdf' "$y" "$nr")"
  [ -s "$out" ] && continue
  "$D/fetch.sh" "https://www.gesetzblatt.bremen.de$href" "$out"
done
