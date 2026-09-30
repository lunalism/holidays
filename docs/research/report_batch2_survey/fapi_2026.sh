#!/bin/sh
# G — feiertage-api.de 2026, 7 주. 레포의 기존 주들과 같은 대조원(hinweis 공란 = 공휴일로 본다).
UA='holidays.lunalism.com research (contact: repo issues)'
for L in BB HB MV SL SN ST TH; do
  curl -s -A "$UA" "https://feiertage-api.de/api/?jahr=2026&nur_land=$L" -o "fapi_2026_$L.json" -w "$L status=%{http_code} size=%{size_download}\n"
  sleep 2
done
