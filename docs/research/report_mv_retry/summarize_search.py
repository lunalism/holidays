# ruff: noqa
"""portal_search.py 가 남긴 <prefix>.search.json 에서 결과 목록을 표로 뽑는다.

사용: python3 summarize_search.py <query> <prefix>.search.json >> search_results.tsv
열: query, 보고된 건수(hits), 순번, docId, 날짜, 분류(categoryId), 제목(titleList), 부제(subtitleList, ' | ' 로 이음)
RESULT_LIST 를 요청한 응답(검색어가 든 것)만 쓴다.
"""
import json
import sys

query, path = sys.argv[1:3]
for x in json.load(open(path, encoding="utf-8")):
    req = x.get("request") or ""
    if "RESULT_LIST" not in req or "FastSearch" not in req:
        continue
    body = x["body"]
    for i, it in enumerate(body["resultList"], 1):
        print("\t".join([
            query, str(body["hits"]), str(i), it.get("docId", ""), it.get("date", ""),
            it.get("categoryId", ""), " ".join(it.get("titleList", [])),
            " | ".join(it.get("subtitleList", [])),
        ]))
