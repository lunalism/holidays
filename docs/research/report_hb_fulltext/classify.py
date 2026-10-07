# ruff: noqa
"""hits.tsv 의 적중마다 분류(A/B/C/D)를 붙인다. 판정은 사람(조사자)이 적중 문맥을 읽고 정한 것이고,
이 스크립트는 그 판정을 호 단위 표(RULES)로 적어 적중 줄에 옮길 뿐이다.

사용: python -I classify.py hits.tsv > classification.tsv
열: file, page, pattern, offset, class, inferred(추론이면 "[추론]"), basis
RULES 에 없는 호는 "?" 로 남긴다 — 남으면 판정이 빠진 것이다.
"""
import csv
import sys

csv.field_size_limit(10**7)

B_2020_012 = ("B", "", "Art. 1 Nr. 1 「Die Überschrift wird wie folgt gefasst: „Gesetz über die Sonn-, Gedenk- und Feiertage“」, "
              "Nr. 2 「Die Überschrift des I. Abschnittes wird wie folgt gefasst …」, Nr. 3 「Nach § 7 wird folgender § 7a eingefügt」 — "
              "§ 2 를 가리키는 개정 지시 없음")

RULES = {
    "2020_012": B_2020_012,
    "2025_098": ("D", "[추론]", "Bekanntmachung über die Änderung von Zuständigkeiten(§ 7 Rechtsbereinigungsgesetz) Anlage 1 의 표에 "
                 "「Gesetz über die Sonn-, Gedenk- und Feiertage … § 11」 — 관할 이전 공고. 조문 자구를 바꾸는 개정 지시가 없어 D 로 봄"),
    "2020_067": ("D", "", "Kostenverordnung(내무) 수수료표 「110 Sonn- und Feiertagsrecht …」, 「§ 11 i.V.m. § 4 …」 — 법을 인용할 뿐"),
    "2022_017": ("D", "", "Kostenverordnung(내무) 수수료표 — 같은 꼴"),
    "2024_017": ("D", "", "Kostenverordnung(내무) 수수료표 — 같은 꼴"),
    "2025_100": ("D", "", "Kostenverordnung(내무) 수수료표 — 새 법명 「Sonn-, Gedenk- und Feiertage」 를 인용할 뿐"),
    "2021_096": ("D", "", "Bremerhaven 일요일 영업 명령 § 2 「Die Vorschriften des Gesetzes über die Sonn- und Feiertage, … 」 — 인용"),
    "2022_035": ("D", "", "Bremerhaven 일요일 영업 명령 § 2 — 같은 꼴"),
    "2023_001": ("D", "", "Bremerhaven 일요일 영업 명령 § 2 — 같은 꼴"),
    "2023_120": ("D", "", "Bremerhaven 일요일 영업 명령 § 2 — 같은 꼴"),
    "2024_139": ("D", "", "Bremerhaven 일요일 영업 명령 § 2 — 같은 꼴"),
    "2025_125": ("D", "", "Bremerhaven 일요일 영업 명령 § 2 — 같은 꼴"),
    "2023_063": ("D", "", "Ladenschlussgesetz 개정 — 「Sonn- und Feiertage」 는 영업일 수 규정의 낱말"),
    "2022_142": ("D", "", "학교 방학·수업 없는 날 규정 § 4 「gesetzliche Feiertage sind in Bremen: der Neujahrstag, … der 31. Oktober "
                 "(Reformationstag), der 1. und der 2. Weihnachtstag」 — 열거를 옮겨 적을 뿐 Feiertagsgesetz 개정 아님"),
    "2020_044": ("D", "", "법원 당직 규정 「an Wochenenden und Feiertagen」 — 낱말"),
    "2021_145": ("D", "", "폐기물 규정 「Feiertagsverschiebungen」 — 낱말"),
    "2022_012": ("D", "", "교정 공무원 근무시간 규정 「Sonn- oder Feiertag」 — 낱말"),
    "2022_062": ("D", "", "수수료표 「Sonn- oder Feiertag(e)」 단가 — 낱말"),
    "2023_075": ("D", "", "휴가 규정 「gesetzliche Feiertage」 — 낱말"),
    "2024_115": ("D", "", "근무시간 규정 「gesetzlichen Feiertag」 — 낱말"),
    "2024_120": ("D", "", "임금·수당 표 「an gesetzlichen Feiertagen 100 %」 — 낱말"),
    "2025_124": ("D", "", "임금·수당 표 — 같은 꼴"),
    "2026_083": ("D", "", "수당 규정 「an Sonn- und gesetzlichen Feiertagen」 — 낱말"),
    # gedenk — Gedenkstätte·Gedenkstein·Gedenkfeiern
    "2020_006": ("D", "", "제방 경계 서술 「Gedenkstätte Bunker Valentin」"),
    "2025_103": ("D", "", "제방 경계 서술 「Gedenkstätte Bunker Valentin」"),
    "2020_032": ("D", "", "코로나 명령 「Gedenkstätten」"),
    "2020_034": ("D", "", "코로나 명령 「Gedenkstätten」"),
    "2021_031": ("D", "", "코로나 명령 「Gedenkstätten」"),
    "2021_055": ("D", "", "코로나 명령 「Gedenkstätten」"),
    "2021_059": ("D", "", "코로나 명령 「Gedenkstätten」"),
    "2024_118": ("D", "", "묘지 수수료 「Gedenkstein」(p3) · 「einmaligen gewerblichen Tätigkeit」(p6)"),
    "2025_108": ("D", "", "묘지 규정 「Gedenkfeiern」"),
}
# einmalig — 일회성 지급·수수료·재선임 등. 공휴일 지정 문맥 없음.
for f in ["2020_007", "2020_015", "2020_074", "2020_147", "2020_151", "2021_026", "2021_030", "2021_083",
          "2022_016", "2022_038", "2022_086", "2022_118", "2022_158", "2023_058", "2023_107", "2023_116",
          "2023_126", "2024_015", "2024_037", "2024_075", "2024_100", "2024_136", "2025_044", "2025_049",
          "2025_060", "2025_062", "2025_079", "2025_080", "2025_132", "2026_018", "2026_021", "2026_069"]:
    RULES[f] = ("D", "", "「einmalig(e)」 — 일회성 지급·수수료·재선임·시험 등. 공휴일 문맥 아님")

w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["file", "page", "pattern", "offset", "class", "inferred", "basis"])
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"):
    c, inf, basis = RULES.get(r["file"], ("?", "", ""))
    w.writerow([r["file"], r["page"], r["pattern"], r["offset"], c, inf, basis])
