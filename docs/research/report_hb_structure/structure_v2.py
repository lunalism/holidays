# ruff: noqa
"""[v2 — 구현 결함 수정판] 파일 단위 구조 검사(G1–G4). v1(structure.py)과 다른 곳은 EIF 정규식 하나뿐이다.
 판정 규칙은 실행 전에 고정했다. 어느 하나라도 불충족·판정 불가면 R.

사용: python -I structure.py <pages_reclassified.tsv> <report_hb_flagged/norm_types.tsv> <txt-dir> > files_structure.tsv
  <txt-dir> 는 report_hb_fulltext/extract.py 출력(쪽 머리 "\f=== page N ===")이다.

대상: 새 분류에서 BLANK 가 아닌 쪽("검색 불가 쪽")이 하나라도 있는 파일.

정규화(쪽마다): 줄 끝 "-" + 다음 줄 소문자 시작이면 잇기 → 공백 축약 → casefold. "¬"·soft hyphen 은 지운다.

G1 제목: 목록 제목과 텍스트층을 둘 다 [0-9a-zäöüß] 만 남기고(나머지 문자 제거) 비교해, 제목 전체가 텍스트층의 부분 문자열이면 충족.
G2 실행부 + 서명:
   - Gesetz·other(Ortsgesetz)·Zustimmungsgesetz·Verordnung·unclear:
     구조 r"artikel \\d+|§ ?\\d+" 와 시행 조항 r"tritt\\b[^.]{0,200}?in kraft" 가 있어야 한다.
   - Berichtigung: 지시 r"(ist|sind) wie folgt zu berichtigen|zu ergänzen" 가 있어야 한다.
   - Bekanntmachung: r"gibt[^.]{0,200}?bekannt|bekannt ?gemacht" 가 있어야 한다.
   - other(Vertrag): r"vereinbar|schließen[^.]{0,120}?(vertrag|folgend)" 가 있어야 한다.
   - 모든 유형에 서명 줄이 있어야 한다.
     꼴: r"(bremen|bremerhaven) ?, ?(den )?\\d{1,2}\\. ?[a-zäöü]+ \\d{4}" 뒤 150 자 안에 서명 주체
     (der senat|senator|senatorin|senatskanzlei|magistrat|bürgermeister|präsident|vorstand|rektor|minister)가 온다.
     「서명 쪽」 = 실행부 표지(시행 조항·지시·공고문·합의문)의 첫 위치 이후로 처음 나오는 서명 줄의 쪽.
G3 위치 + 부속 언급: 검색 불가 쪽 전부가 서명 쪽보다 뒤에 있어야 한다.
   그리고 서명 쪽까지의 텍스트층에 부속 낱말 r"ersichtliche fassung|beigefügt|angefügt|anlage|anhang|staatsvertrag|abkommen|vertrag"
   가 있어야 한다. 찾은 낱말을 우선순위(위 순서) 첫 것으로 그 문장(앞뒤 120 자)과 쪽을 적는다.
G4 Feiertagsgesetz 아님: 텍스트층 문장(". " 로 자름) 중 부속 낱말(anlage|anhang|ersichtliche fassung|beigefügt|angefügt)과
   r"feiertag|113-c|sonn-" 이 함께 든 문장이 없어야 한다. "…die aus dem Anhang/der Anlage … ersichtliche Fassung" 의 주어(무엇의 Fassung 인지)를 적는다.
"""
import csv
import pathlib
import re
import sys

csv.field_size_limit(10**7)

LAWLIKE = {"Gesetz", "other(Ortsgesetz)", "Zustimmungsgesetz zu Staatsvertrag", "Verordnung", "unclear"}
PAGE = re.compile(r"\f=== page (\d+) ===\n")
STRUCT = re.compile(r"artikel \d+|§ ?\d+")
# v2: 날짜의 마침표("1. januar")를 문장 끝으로 보지 않도록, 숫자 바로 뒤의 "." 만 허용한다. 그 밖은 v1 과 같다.
EIF = re.compile(r"tritt\b(?:[^.]|(?<=\d)\.){0,200}?in kraft")
BER = re.compile(r"(ist|sind) wie folgt zu berichtigen|zu ergänzen")
BEK = re.compile(r"gibt[^.]{0,200}?bekannt|bekannt ?gemacht")
VER = re.compile(r"vereinbar|schließen[^.]{0,120}?(vertrag|folgend)")
SIGN = re.compile(r"(bremen|bremerhaven) ?, ?(den )?\d{1,2}\. ?[a-zäöü]+ \d{4}.{0,150}?"
                  r"(der senat|senator|senatorin|senatskanzlei|magistrat|bürgermeister|präsident|vorstand|rektor|minister)")
ATT_ORDER = ["ersichtliche fassung", "beigefügt", "angefügt", "anlage", "anhang", "staatsvertrag", "abkommen", "vertrag"]
ATT4 = re.compile(r"anlage|anhang|ersichtliche fassung|beigefügt|angefügt")
FT = re.compile(r"feiertag|113-c|sonn-")
FASSUNG = re.compile(r"([^.]{0,160}?)\b(erhält|erhalten)\b([^.]{0,60}?)\bdie aus de[mr] (anhang|anlage)[^.]{0,80}?ersichtliche fassung")


def norm(t):
    t = t.replace("¬", "").replace("­", "")
    lines = t.split("\n")
    out = []
    for line in lines:
        if out and out[-1].rstrip().endswith("-") and line.lstrip()[:1].islower():
            out[-1] = out[-1].rstrip()[:-1] + line.lstrip()
        else:
            out.append(line)
    return " ".join(" ".join(out).split()).casefold()


def alnum(t):
    return re.sub(r"[^0-9a-zäöüß]", "", t.casefold().replace("¬", "").replace("­", ""))


def pages_of(path):
    parts = PAGE.split(path.read_text(encoding="utf-8"))
    return [(int(parts[i]), norm(parts[i + 1])) for i in range(1, len(parts), 2)]


recl = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"))
types = {r["file"]: r for r in csv.DictReader(open(sys.argv[2], encoding="utf-8"), delimiter="\t")}
txtdir = pathlib.Path(sys.argv[3])

nonsearch = {}
for r in recl:
    if r["new_class"] != "BLANK":
        nonsearch.setdefault(r["file"], []).append(int(r["page"]))

w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["file", "year", "nr", "title", "norm_type", "nonsearch_pages", "nonsearch_count",
            "G1", "G1_evidence", "G2", "G2_evidence", "G3", "G3_evidence", "G4", "G4_evidence", "group"])
for f in sorted(nonsearch):
    t = types[f]
    ns = sorted(nonsearch[f])
    pgs = pages_of(txtdir / (f[:-4] + ".txt"))
    full = ""
    offs = []
    for no, text in pgs:
        offs.append((len(full), no))
        full += text + " "

    def page_at(pos):
        p = offs[0][1]
        for o, no in offs:
            if o <= pos:
                p = no
        return p

    # G1
    ta = alnum(t["title"])
    fa = alnum(" ".join(text for _, text in pgs))
    g1 = bool(ta) and ta in fa
    g1e = f"title_norm[{len(ta)}] {'found' if g1 else 'not found'}: {t['title'][:120]}"
    if g1:
        # 첫 낱말 위치로 쪽을 대략 적는다
        first = re.escape(t["title"].split()[0].casefold())
        m = re.search(first, full)
        g1e += f" (p{page_at(m.start()) if m else '?'})"
    # G2
    nt = t["norm_type"]
    marker = None
    ev = []
    ok_op = False
    if nt in LAWLIKE:
        ms, me = STRUCT.search(full), EIF.search(full)
        ok_op = bool(ms and me)
        if ms:
            ev.append(f"struct '{ms.group(0)}' p{page_at(ms.start())}")
        if me:
            ev.append(f"eif '{me.group(0)[:80]}' p{page_at(me.start())}")
            marker = me.start()
    else:
        rx = {"Berichtigung": BER, "Bekanntmachung": BEK, "other(Vertrag)": VER}.get(nt)
        mo = rx.search(full) if rx else None
        ok_op = bool(mo)
        if mo:
            ev.append(f"operative '{mo.group(0)[:80]}' p{page_at(mo.start())}")
            marker = mo.start()
    sign_page = None
    if marker is not None:
        msig = SIGN.search(full, marker)
        if msig:
            sign_page = page_at(msig.start())
            ev.append(f"sign '{msig.group(0)[:100]}' p{sign_page}")
    g2 = ok_op and sign_page is not None
    if sign_page is None:
        ev.append("sign: not found after operative marker")
    # G3
    g3e = []
    after = sign_page is not None and all(p > sign_page for p in ns)
    g3e.append(f"nonsearch {ns} vs sign p{sign_page}: {'all after' if after else 'NOT all after'}")
    upto = "".join(text + " " for no, text in pgs if sign_page is not None and no <= sign_page)
    att = None
    for word in ATT_ORDER:
        m = re.search(word, upto)
        if m:
            att = (word, m)
            break
    if att:
        word, m = att
        g3e.append(f"attach '{word}' p{page_at(m.start())}: …{upto[max(0, m.start()-120):m.end()+120]}…")
    else:
        g3e.append("attach: none up to sign page")
    g3 = after and att is not None
    # G4
    bad = [s for s in re.split(r"\. ", full) if ATT4.search(s) and FT.search(s)]
    fass = [f"{m.group(1)[-100:].strip()} | {m.group(2)}{m.group(3)}" for m in FASSUNG.finditer(full)]
    g4 = not bad
    g4e = ("conflict: " + " || ".join(b[:200] for b in bad[:3])) if bad else "no attachment+Feiertag sentence"
    if fass:
        g4e += " ; Fassung-of: " + " || ".join(fass[:5])
    group = "G" if (g1 and g2 and g3 and g4) else "R"
    w.writerow([f, t["year"], t["nr"], t["title"], nt, ",".join(map(str, ns)), len(ns),
                "met" if g1 else "unmet", g1e, "met" if g2 else "unmet", " ; ".join(ev),
                "met" if g3 else "unmet", " ; ".join(g3e), "met" if g4 else "unmet", g4e, group])
