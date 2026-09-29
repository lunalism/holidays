# ruff: noqa
# 재현 기록 — 조사 때 실제로 돌린 코드를 그대로 둔다(린트 정리 없음). CI 는 돌리지 않는다.
import re, os, time, urllib.request
import fitz
s = open("starweb_gvbl.html", encoding="utf-8", errors="replace").read()
links = sorted(set(re.findall(r'cache/GVBL/(20(?:1\d|2\d))/(\d+)\.pdf', s)))
out = open("he/issues_scan.tsv", "a")
done = {tuple(l.split("\t")[:2]) for l in open("he/issues_scan.tsv")} if os.path.getsize("he/issues_scan.tsv") else set()
def get(url, dest):
    for a in range(3):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                n = int(r.headers.get("Content-Length") or -1); data = r.read()
            if n >= 0 and len(data) != n: raise IOError(f"short {len(data)}/{n}")
            open(dest, "wb").write(data); return True
        except Exception as e:
            print("retry", url, e, flush=True); time.sleep(5 * 3 ** a)
    return False
for y, n in links:
    if (y, n) in done: continue
    f = f"he/issues/{y}-{n}.pdf"
    if not os.path.exists(f):
        time.sleep(0.5)
        if not get(f"https://starweb.hessen.de/cache/GVBL/{y}/{n}.pdf", f):
            out.write(f"{y}\t{n}\tNETFAIL\t\n"); out.flush(); continue
    d = fitz.open(f); t = "\n".join(p.get_text() for p in d)
    hits = [t[max(0, m.start()-200):m.start()+250].replace("\n", " ").replace("\t", " ") for m in re.finditer(r"(?i)feiertag", t)]
    out.write(f"{y}\t{n}\t{len(t)}\t{' || '.join(hits)}\n"); out.flush()
print("done", len(links), flush=True)
