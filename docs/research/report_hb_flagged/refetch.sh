#!/bin/sh
# 사용: refetch.sh <report_hb_fulltext/flagged_pages.txt> <report_hb_fulltext/corpus.tsv> <pdf-dir>
# 플래그 쪽이 있는 파일마다, scratch 에 없으면 corpus.tsv 의 URL 에서 한 번 받는다. 간격·재시도는 fetch.sh.
D=$(dirname "$0")
tail -n +2 "$1" | cut -f1 | sort -u | while read -r f; do
  [ -s "$3/$f" ] && continue
  y=${f%%_*}; n=${f#*_}; n=${n%.pdf}; n=$(expr "$n" + 0)
  url=$(awk -F'\t' -v y="$y" -v n="$n" '$1==y && $2==n {print $4}' "$2")
  "$D/fetch.sh" "$url" "$3/$f"
done
