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
                # caused_by_name 을 원인 공휴일 키로 되짚는다. 이것이 그 필드의
                # 용도다 — 교차검증. 계산(대체공휴일 유도)에는 쓰지 않는다.
                lunar = any(
                    i.key in unresolved or _cause_key(i, names) in unresolved for i in k
                )
                unknown_cause = any(i.is_substitute and not i.caused_by_name for i in k)
                if lunar:
                    note = "음력 미구현 (예상)"
                elif unknown_cause:
                    note = "원인 미상 대체공휴일 — 인접 공휴일로 추정만 가능"
                else:
                    note = "우리 표에 없음 — 확인 필요"
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
