#!/bin/sh
# 사용: e_fetch_products.sh <e_listing.tsv> <out-dir>  — 2020 년 이후 호의 상품 화면을 차례로 받는다(fetch.sh, 3 초 간격).
D=$(dirname "$0")
awk -F'\t' 'NR>1 && $1>=2020 {print $1"_"$2"_"$3"\t"$5}' "$1" | while IFS="$(printf '\t')" read -r key url; do
  "$D/fetch.sh" "$url" "$2/$key.html" > /dev/null
done
