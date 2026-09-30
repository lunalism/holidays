#!/bin/sh
# 사용: fetch.sh <url> <out-file>  — 식별 UA, 로그는 fetch.log 에 한 줄. 호출 간격은 부르는 쪽이 둔다(3 초 이상).
D=$(dirname "$0")
UA='holidays.lunalism.com research (contact: repo issues)'
r=$(curl -s -A "$UA" -L --max-time 60 -o "$2" -w '%{http_code}\t%{content_type}\t%{size_download}\t%{url_effective}' "$1")
printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$r" | tee -a "$D/fetch.log"
