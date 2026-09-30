# ruff: noqa
"""pre-check 3 — BRAVORS 공개 검색 화면(Schnellsuche: 현행 / Archiv-Schnellsuche: außer Kraft)으로
질의하고 결과 전 쪽의 (id, 제목, 날짜)를 TSV 로 낸다. 공개 화면이 주는 세션 쿠키만 쓴다(로그인·내부 API 없음).
식별 UA, 요청 간 4 초. 403/429/CAPTCHA 면 멈춘다."""
import http.cookiejar, re, sys, time, html, urllib.parse, urllib.request, datetime
UA = "holidays.lunalism.com research (contact: repo issues)"
BASE = "https://bravors.brandenburg.de"
LOG = sys.argv[1]; OUT = sys.argv[2]
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def req(url, data=None, ref=None):
    time.sleep(4)
    r = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None, headers={"User-Agent": UA, **({"Referer": ref} if ref else {})})
    try:
        with op.open(r, timeout=60) as resp:
            body = resp.read().decode("utf-8", "replace"); st = resp.status; final = resp.geturl()
    except urllib.error.HTTPError as e:
        body = ""; st = e.code; final = url
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H:%M:%SZ}\t{'POST' if data else 'GET'} {url} {data.get('search[searchterm]','') if data else ''}\t{st}\t{len(body)}\t{final}\n")
    if st in (403, 429) or re.search(r"captcha", body, re.I):
        sys.exit(f"STOP {st} {url}")
    return body
def parse(body):
    out = []
    for m in re.finditer(r'<dt>.*?<!--\s*(\d+)\s*-->.*?<a [^>]*>(.*?)</a>.*?</dt>\s*<dd class="datum">(.*?)</dd>', body, re.S):
        out.append((m.group(1), " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).split()), " ".join(re.sub(r"<[^>]+>", " ", m.group(3)).split())))
    return out
TERMS = ["Feiertag", "Feiertage", "Feiertagsgesetz", "§ 2 Abs. 3 FTG", "einmalig"]
SEARCHES = [("archiv", "/de/archiv_schnellsuche"), ("aktuell", "/de/vorschriften_schnellsuche")]
import math
with open(OUT, "w") as out:
    out.write("search\tterm\techo\treported\tpage\tid\ttitle\tdatum\n")
    for sname, path in SEARCHES:
        for term in TERMS:
            cj.clear()                      # 질의마다 새 세션 — 이전 결과가 남지 않게
            req(BASE + path)                # 공개 화면이 주는 세션 쿠키
            body = req(BASE + path, {"search[art_vorschrift]": "alle", "search[searchterm]": term, "suchen": "Suchen"}, BASE + path)
            t = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", body)).split())
            e = re.search(r"Suchbegriff: (.*?) wurde in", t); echo = e.group(1) if e else ""
            m = re.search(r"wurde in (\d+) Treffern gefunden", t); rep = int(m.group(1)) if m else 0
            npages = max(1, math.ceil(rep / 10))
            rows = [(1, r) for r in parse(body)]
            for p in range(2, npages + 1):
                b2 = req(f"{BASE}{path}/ergebnis/page/{p}", ref=BASE + path + "/ergebnis")
                rows += [(p, r) for r in parse(b2)]
            print(sname, repr(term), "echo", repr(echo), "reported", rep, "pages", npages, "parsed", len(rows), "unique", len({r[0] for _, r in rows}), flush=True)
            for p, (i, ti, da) in rows:
                out.write(f"{sname}\t{term}\t{echo}\t{rep}\t{p}\t{i}\t{ti}\t{da}\n")
