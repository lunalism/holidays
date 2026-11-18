#!/bin/sh
# 사용: e_fetch_previews.sh <products-dir> <out-dir> <연도…>
# 상품 화면에 「Vorschau」 첨부(downloadable/download/attachment/id/N/)가 있는 호만, 그 화면의 링크 그대로 받는다.
# 이미 받은 파일은 건너뛴다. fetch.sh(3 초 간격)로 받는다.
D=$(dirname "$0"); P="$1"; O="$2"; shift 2
for y in "$@"; do
  for f in "$P"/"${y}"_*.html; do
    key=$(basename "$f" .html)
    [ -s "$O/$key.pdf" ] && continue
    url=$(grep -o 'https://www.recht-sachsen.de/downloadable/download/attachment/id/[0-9]*/' "$f" | head -1)
    [ -n "$url" ] && "$D/fetch.sh" "$url" "$O/$key.pdf" > /dev/null
  done
done
