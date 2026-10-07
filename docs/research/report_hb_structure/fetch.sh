#!/bin/sh
# 사용: fetch.sh <url> <out-file>  — report_hb_flagged/fetch.sh 그대로(로그만 이 폴더).
# 식별 UA, 로그는 fetch.log 에 한 줄(시각, URL, 상태, content-type, 바이트, 최종 URL).
# 바뀐 점: 요청 뒤 3 초를 쉰다(요청 간격 2 초 이상 보장). 5xx 면 최대 두 번 재시도(10 초, 20 초 뒤).
D=$(dirname "$0")
UA='holidays.lunalism.com research (contact: repo issues)'
n=0
while :; do
  r=$(curl -s -A "$UA" -L --max-time 120 -o "$2" -w '%{http_code}\t%{content_type}\t%{size_download}\t%{url_effective}' "$1")
  printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$r" | tee -a "$D/fetch.log"
  sleep 3
  code=${r%%	*}
  case "$code" in
    5??) if [ "$n" -lt 2 ]; then n=$((n+1)); sleep $((10*n)); continue; fi ;;
  esac
  break
done
