"""KASI 관측과 우리 계산이 어긋나는 지점을 상시 보고한다.

--------------------------------------------------------------------------
이 테스트는 승패를 가리지 않는다
--------------------------------------------------------------------------
어느 쪽도 자동으로 채택하지 않는다. 목록만 낸다.

두 소스는 성격이 다르다. KASI 는 관측이고 우리 표는 법령 해석이다. 어긋난다고
해서 한쪽이 틀렸다고 단정할 수 없다. 실제로 2015-08-14 임시공휴일은 KASI 에
없지만 국무회의 의결로 실재했다. 그때 KASI 를 정답으로 삼았다면 있었던 공휴일을
지웠을 것이다.

반대 방향도 있다. 2024-10-01 임시공휴일은 우리 표에만 없었고 KASI 가 알려 줬다.

그래서 불일치는 고쳐야 할 실패가 아니라 봐야 할 목록이다.
xfail 로 두어 실패 보고서에 전체 목록이 항상 실리되 빌드를 막지는 않게 한다.
pytest -rx 로 목록을 본다.

이 방식의 한계도 적어 둔다. xfail 이라 새 불일치가 생겨도 빨간불이 켜지지 않는다.
회귀 감지는 이 테스트의 일이 아니다. 그 일은 정답 픽스처가 한다.

--------------------------------------------------------------------------
원인 미상 대체공휴일 — 추정하지 않는다
--------------------------------------------------------------------------
2015~2023 년 응답의 대체공휴일은 이름이 그냥 "대체공휴일"이고 괄호 안 원인이
없다. 그런 항목이 11 건이다. caused_by 는 unknown 으로 둔다.

원인을 직전 공휴일로 추정할 수는 있다. 하지 않는다. 계산에 쓰지 않는 것만으로는
부족해서, 이 리포트의 분류 문구에서도 뺐다. 분류에 추정이 한 번 들어가면
"대체공휴일(설날)로 보임" 같은 문구가 남고, 다음 사람은 그걸 확인된 사실로
읽는다. 리포트는 관측 그대로만 적는다 — 원인 표기가 없다는 사실까지가 관측이다.

이 11 건은 그대로 두는 것이 낫다. 음력을 구현하면 우리 계산이 이 날짜들의
대체공휴일을 스스로 유도해 낸다. 그때 유도된 원인이 우리 규칙 테이블에서
나온 것이므로 KASI 를 정답으로 삼지 않고도 원인이 정해진다.
지금 추정으로 채워 두면 그 검증이 무의미해진다. 채운 값과 유도한 값이 같은지
비교하는 것이 아니라, 채운 값을 다시 읽는 것이 되기 때문이다.

즉 이 11 건은 음력 구현의 검증 지표다. 구현 후 이 분류가 0 건이 되어야 하고,
0 건이 되지 않는다면 우리 대체공휴일 유도나 음력 환산 중 하나가 틀린 것이다.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from rules.kr import holiday_calendar as hc
from sources.kr import kasi_parser as kp

CACHE_DIR = Path(__file__).parent.parent / "sources" / "kr" / "cache"


def _cached_years() -> list:
    years = []
    for path in sorted(CACHE_DIR.glob("getRestDeInfo_*.xml")):
        year = int(path.stem.rsplit("_", 1)[1])
        years.append((year, path))
    return years


pytestmark = pytest.mark.skipif(not _cached_years(), reason="캐시된 KASI 응답이 없다.")


def _our_holidays(year: int) -> dict:
    out = {}
    day = dt.date(year, 1, 1)
    while day.year == year:
        found = hc.holidays_on(day)
        if found:
            out[day] = found
        day += dt.timedelta(days=1)
    return out


def _cause_key(item, names: dict) -> str:
    """대체공휴일의 원인 공휴일 이름 → 키. 없으면 빈 문자열.

    교차검증 전용이다. 이 값으로 대체공휴일을 유도하면 KASI 가 정답이 되고
    우리 규칙 테이블은 장식이 된다.
    """
    if not item.caused_by_name:
        return ""
    entry = names["names"].get(item.caused_by_name) or {}
    return entry.get("key") or ""


def collect_discrepancies() -> list:
    """(날짜, 분류, KASI, ours, 비고) 목록. 판정하지 않는다."""
    coverage = hc.coverage()["effective"]
    unresolved = hc.unresolved_holidays()
    names = kp.load_names()
    rows = []

    for year, path in _cached_years():
        if year < coverage.start.year:
            continue  # 우리 쪽 신뢰 구간 밖. 대조 대상이 아니다.

        items = kp.parse(path.read_text(encoding="utf-8"))
        if not items:
            rows.append((dt.date(year, 1, 1), "KASI-빈응답", "-", "-", f"{year} 년 데이터 없음"))
            continue

        kasi = {}
        for item in items:
            kasi.setdefault(item.date, []).append(item)
        ours = _our_holidays(year)

        for day in sorted(set(kasi) | set(ours)):
            k, o = kasi.get(day), ours.get(day)
            if k and o:
                continue  # 날짜가 겹치면 일치로 본다. 이름 표기 차이는 별개 문제다.
            if k:
                # 관측된 사실만 적는다. 우선순위로 하나를 고르지 않고 해당하는 것을
                # 전부 잇는다. 우선순위를 두면 뒤 조건이 앞 조건에 조용히 가려지고,
                # 가려진 쪽은 목록에서 사라져 없는 것처럼 보인다.
                facts = []
                # caused_by_name 을 원인 공휴일 키로 되짚는다. 이것이 그 필드의
                # 용도다 — 교차검증. 계산(대체공휴일 유도)에는 쓰지 않는다.
                if any(i.key in unresolved or _cause_key(i, names) in unresolved for i in k):
                    facts.append("음력 미구현 (예상)")
                if any(i.is_substitute and not i.caused_by_name for i in k):
                    # 원인을 인접 공휴일로 추정하지 않는다. 문구에도 넣지 않는다.
                    # 모듈 docstring 의 "원인 미상 대체공휴일" 참조.
                    facts.append(
                        "원인 미상 대체공휴일 — KASI 에 원인 표기 없음 (caused_by: unknown)"
                    )
                note = " / ".join(facts) or "우리 표에 없음 — 확인 필요"
                rows.append((day, "KASI만", ", ".join(i.name for i in k), "-", note))
            else:
                rows.append(
                    (day, "ours만", "-", ", ".join(h.name for h in o), "KASI 에 없음 — 확인 필요")
                )
    return rows


def format_table(rows: list) -> str:
    header = f"{'날짜':<12} {'구분':<12} {'KASI':<26} {'ours':<20} 비고"
    lines = [header, "-" * 100]
    for day, kind, k, o, note in rows:
        lines.append(f"{day}  {kind:<12} {k:<26} {o:<20} {note}")
    counts = {}
    for _, _, _, _, note in rows:
        counts[note] = counts.get(note, 0) + 1
    lines.append("-" * 100)
    lines.append(f"합계 {len(rows)}건")
    for note, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {n:3d}  {note}")
    return "\n".join(lines)


@pytest.mark.xfail(
    reason="소스 간 불일치는 정상 상태다. 어느 쪽도 자동 채택하지 않는다. -rx 로 목록을 볼 것.",
)
def test_sources_agree():
    rows = collect_discrepancies()
    assert not rows, "\n" + format_table(rows)


def _unknown_cause_substitute_days() -> list:
    """KASI 가 원인 없이 "대체공휴일"로만 준 날짜들. 캐시에서 직접 뽑는다.

    목록을 여기 적어 두지 않는 이유는, 적어 두면 캐시가 늘 때 그 항목이
    검증 대상에서 조용히 빠지기 때문이다. 응답에서 매번 다시 뽑는다.
    """
    days = []
    coverage = hc.coverage()["effective"]
    for year, path in _cached_years():
        if year < coverage.start.year:
            continue
        for item in kp.parse(path.read_text(encoding="utf-8")):
            if item.is_substitute and not item.caused_by_name:
                days.append(item.date)
    return sorted(set(days))


def test_we_derive_the_substitutes_whose_cause_kasi_never_gave():
    """원인 미상 대체공휴일을 우리 계산이 스스로 유도해 내는지.

    이것이 음력 구현의 검증 지표다. 2015~2023 년 응답의 대체공휴일은 이름이
    그냥 "대체공휴일"이고 괄호 안 원인이 없다. 그 원인을 인접 공휴일로 추정해
    채우지 않기로 했으므로(모듈 docstring 참조), 확인할 길은 우리 규칙이 그
    날짜들을 유도해 내는지뿐이었다.

    유도된 원인은 우리 규칙 테이블에서 나온 것이다. KASI 를 정답으로 삼지 않고도
    원인이 정해진다는 것이 요점이다. 미리 추정으로 채워 두었다면 이 대조는
    채운 값을 다시 읽는 것이 되어 아무것도 검증하지 못했을 것이다.

    source_key 가 무엇인지까지는 주장하지 않는다. 제3조제1항제3호의 겹침에서
    어느 쪽이 트리거인지는 아직 확정되지 않았다(3호-귀속-불명).
    여기서 고정하는 것은 "그 날짜에 대체공휴일이 유도된다"까지다.
    """
    days = _unknown_cause_substitute_days()
    assert days, "원인 미상 대체공휴일이 캐시에서 하나도 안 나온다. 파서를 의심할 것."

    missing = []
    for day in days:
        derived = [h for h in hc.holidays_on(day) if h.kind == "substitute"]
        if not derived:
            missing.append((day, [h.name for h in hc.holidays_on(day)]))

    assert not missing, (
        f"KASI 는 대체공휴일이라는데 우리는 유도하지 못한 날짜 {len(missing)}/{len(days)} 건:\n"
        + "\n".join(f"  {day}  ours={names or '없음'}" for day, names in missing)
        + "\n음력 환산이나 대체공휴일 규칙 중 하나가 틀렸다는 뜻이다."
    )


def test_report_never_guesses_a_cause():
    """리포트 분류 문구에 추정 원인이 섞이지 않는지.

    파서가 caused_by_name 을 비워 두는 것만으로는 부족하다. 분류 쪽에서
    "직전 공휴일로 보아 설날" 같은 문구를 붙이면 추정이 다시 들어오고,
    다음 사람은 그것을 확인된 사실로 읽는다.

    원인 후보는 키가 붙은 이름들이다. 키가 없는 이름("대체공휴일", "임시공휴일",
    선거일)은 원인이 될 수 없으므로 문구에 나와도 추정이 아니다.
    """
    causes = [n for n, e in kp.load_names()["names"].items() if (e or {}).get("key")]
    for day, _, _, _, note in collect_discrepancies():
        guessed = [n for n in causes if n in note]
        assert not guessed, (
            f"{day}: 분류 문구에 공휴일 이름 {guessed} 가 들어 있다.\n  {note}\n"
            "관측되지 않은 원인을 문구로 남기지 말 것."
        )


def test_our_extras_are_deliberate():
    """우리 표에만 있는 항목은 근거가 적혀 있어야 한다.

    KASI 가 모르는 공휴일을 우리가 주장하려면 그만한 이유가 있어야 한다.
    2015-08-14 이 그 경우이고, 국무회의 의결 근거가 designated_holidays.yaml 에 있다.
    근거 없이 우리 쪽에만 있는 날짜가 생기면 여기서 드러난다.
    """
    extras = [row for row in collect_discrepancies() if row[1] == "ours만"]
    documented = {dt.date(2015, 8, 14)}
    undocumented = [row for row in extras if row[0] not in documented]
    assert not undocumented, (
        "우리 표에만 있고 근거가 기록되지 않은 날짜:\n" + format_table(undocumented)
    )
