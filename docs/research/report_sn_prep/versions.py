# ruff: noqa
"""REVOSax 역사판(3997.1–.6)과 현행 화면에서 판의 유효 기간·Stand 줄·§ 1 Abs. 1 자구·§ 1 각주·§ 2 를 뽑는다.

사용: python3 versions.py <html...> > versions.tsv  (열: 파일, 유효 기간/Fassung 줄, Stand 줄, § 1 Abs. 1 의 sha256,
§ 1 Abs. 1(항목을 ' | ' 로 이음), § 1 각주, § 2 자구)
§ 1 Abs. 1 은 「(1) Gesetzliche Feiertage sind:」 다음부터 「(2)」 앞까지의 줄이다(<br> 로 나뉜 항목).
"""
import hashlib
import html
import re
import sys


def text(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    h = re.sub(r"<br\s*/?>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", h))
    return [re.sub(r"\s+", " ", ln).strip() for ln in t.splitlines() if ln.strip()]


print("file\tvalidity\tstand\tsha256_p1abs1\tp1abs1\tp1_footnotes\tp2")
for path in sys.argv[1:]:
    h = open(path, encoding="utf-8").read()
    lines = text(h)
    validity = " ".join(ln for ln in lines if re.search(r"Fassung gültig|gültig (ab|vom|bis)", ln))[:200]
    stand = next((ln for ln in lines if ln.startswith("Rechtsbereinigt") or "mit Stand vom" in ln), "")
    i = next(n for n, ln in enumerate(lines) if ln.startswith("(1) Gesetzliche Feiertage sind"))
    j = next(n for n in range(i + 1, len(lines)) if lines[n].startswith("(2)"))
    items = lines[i + 1:j]
    # 쪼개진 항목(괄호가 다음 줄로 넘어간 것)을 잇는다
    merged = []
    for it in items:
        if merged and merged[-1].count("(") > merged[-1].count(")"):
            merged[-1] += " " + it
        else:
            merged.append(it)
    abs1 = " | ".join(merged)
    foot = " ; ".join(sorted({re.sub(r"\s+", " ", m) for m in re.findall(r'title="(§ 1[^"]*)"', h)}))
    k = next((n for n, ln in enumerate(lines) if ln == "Gedenk- und Trauertage" or ln.endswith("Gedenk- und Trauertage")), None)
    p2 = " ".join(lines[k:k + 9]) if k is not None else ""
    print("\t".join([path.rsplit("/", 1)[-1], validity, stand,
                     hashlib.sha256(abs1.encode()).hexdigest()[:16], abs1, foot, p2[:400]]))
