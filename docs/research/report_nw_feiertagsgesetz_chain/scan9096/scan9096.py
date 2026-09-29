# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import json, subprocess, urllib.request, re, os, time
import fitz
S = "https://recht.nrw.de/search-middleware/opensearch_internet/_search"
TIMEOUT = 60

def retry(fn, what):
    for attempt in range(3):
        try:
            return fn()
        except Exception as e:
            print(f"retry {attempt+1}/3 {what}: {type(e).__name__}: {e}", flush=True)
            time.sleep(5 * 3 ** attempt)
    return None

def q(body):
    req = urllib.request.Request(S, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=TIMEOUT))

def fetch_pdf(url, dest):
    tmp = dest + ".part"
    with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
        expected = int(r.headers.get("Content-Length") or -1)
        data = r.read()
    if expected >= 0 and len(data) != expected:
        raise IOError(f"short read {len(data)}/{expected}")
    open(tmp, "wb").write(data)
    os.replace(tmp, dest)
    return True

done = set()
if os.path.exists("scan9096/result.tsv"):
    done = {tuple(l.split("\t")[:2]) for l in open("scan9096/result.tsv") if l.split("\t")[2] not in ("NETFAIL",)}
out = open("scan9096/result.tsv", "a")
for y in range(1990, 1997):
    r = retry(lambda: q({"size": 300, "query": {"bool": {"must": [{"term": {"type": "gazette_gv_nrw"}}, {"term": {"field_issue_year": y}}]}}, "_source": ["field_issue_number"]}), f"index {y}")
    if r is None:
        out.write(f"{y}\t*\tNETFAIL\t\tindex query\n"); out.flush(); continue
    for n in sorted(int(h["_source"]["field_issue_number"][0]) for h in r["hits"]["hits"]):
        if (str(y), str(n)) in done:
            continue
        f = f"scan9096/{y}-{n}.pdf"
        if not os.path.exists(f):
            html = retry(lambda: urllib.request.urlopen(f"https://recht.nrw.de/gvnrw/{y}-{n}/", timeout=TIMEOUT).read().decode("utf-8", "replace"), f"page {y}-{n}")
            if html is None:
                out.write(f"{y}\t{n}\tNETFAIL\t\tissue page\n"); out.flush(); continue
            m = re.search(r"GV_Archiv/[^\"]+\.pdf", html)
            if not m:
                out.write(f"{y}\t{n}\tNOPDF\t\t\n"); out.flush(); continue
            if retry(lambda: fetch_pdf("https://recht.nrw.de/system/files/" + m.group(0), f), f"pdf {y}-{n}") is None:
                out.write(f"{y}\t{n}\tNETFAIL\t\tpdf\n"); out.flush(); continue
        d = fitz.open(f)
        text = "\n".join(p.get_text() for p in d)
        mode = "textlayer"
        if len(text) < 200:
            mode = "vision-p1"
            png = f"scan9096/{y}-{n}_p1.png"
            d[0].get_pixmap(dpi=200).save(png)
            text = subprocess.run(["./ocrbin", png], capture_output=True, text=True).stdout
            os.remove(png)
        hits = []
        for mm in re.finditer(r"(?i)feiertag|sonn- und feier", text):
            hits.append(text[max(0, mm.start()-120):mm.start()+120].replace("\n", " ").replace("\t", " "))
        bers = [text[max(0, mm.start()-150):mm.start()+200].replace("\n", " ").replace("\t", " ") for mm in re.finditer(r"(?i)berichtigung", text)]
        out.write(f"{y}\t{n}\t{mode}\t{len(bers)}\t{' || '.join(hits)}\t{' || '.join(bers)}\n"); out.flush()
print("done", flush=True)
