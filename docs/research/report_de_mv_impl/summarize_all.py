# ruff: noqa
"""portal_search_all.py 의 <prefix>.search.json 에서 검색어가 든 RESULT_LIST 응답을 모두 모아 docId 로 겹침을 뺀 표.

사용: python3 summarize_all.py <query> <label> <prefix>.search.json >> p3_results.tsv
열: query, label(분류), 보고된 건수, 순번(첫 등장 순), docId, 날짜, 분류, 제목, 부제
분류로 좁힌 검색이면 마지막 RESULT_LIST 요청의 CATEGORY 필터와 같은 응답만 쓴다 — 좁히기 전 첫 화면(「Alles」)을
섞지 않는다.
"""
import json
import sys

query, label, path = sys.argv[1:4]
seen, n, reported = set(), 0, ""
lists = [x for x in json.load(open(path, encoding="utf-8"))
         if "RESULT_LIST" in (x.get("request") or "") and "FastSearch" in (x.get("request") or "")
         and "body" in x]
final = json.loads(lists[-1]["request"])["filters"].get("CATEGORY") if lists else None
for x in lists:
    if json.loads(x["request"])["filters"].get("CATEGORY") != final:
        continue
    body = x["body"]
    reported = str(body.get("hits", ""))
    for it in body.get("resultList", []):
        if it.get("docId") in seen:
            continue
        seen.add(it.get("docId"))
        n += 1
        print("\t".join([query, label, reported, str(n), it.get("docId", ""), it.get("date", ""),
                         it.get("categoryId", ""), " ".join(it.get("titleList", [])),
                         " | ".join(it.get("subtitleList", []))]))
print(f"# {query} [{label}]: reported={reported} collected={n}", file=sys.stderr)
