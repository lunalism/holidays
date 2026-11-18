#!/bin/sh
# 사용: fetch.sh <url> <out-file>  — report_mv_retry/fetch.sh 와 같다(5xx 재시도 한 번)
# (report_de_sn_impl).
# 식별 UA, 로그는 fetch.log 에 한 줄(시각, URL, 상태, content-type, 바이트, 최종 URL). 요청 뒤 3 초를 쉰다.
D=$(dirname "$0")
UA='holidays.lunalism.com research (contact: repo issues)'
n=0
while :; do
  r=$(curl -s -A "$UA" -L --max-time 120 -o "$2" -w '%{http_code}\t%{content_type}\t%{size_download}\t%{url_effective}' "$1")
  printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$r" | tee -a "$D/fetch.log"
  sleep 3
  code=${r%%	*}
  case "$code" in
    5??) if [ "$n" -lt 1 ]; then n=1; sleep 10; continue; fi ;;
  esac
  break
done
