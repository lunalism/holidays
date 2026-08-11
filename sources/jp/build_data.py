"""캐시된 内閣府 CSV → data/jp/<연도>.yaml.

--------------------------------------------------------------------------
왜 기계가 쓴 파일을 커밋하는가
--------------------------------------------------------------------------
rules/kr/ 의 YAML 은 사람이 관보를 확인해 근거와 함께 적은 표다. 이쪽은 성격이
다르다 — 내각부 CSV 가 곧 정부의 공식 발표이므로, data/jp/ 는 그 발표를 우리
스키마로 옮긴 사본이다. 사람이 새 사실을 적는 자리가 아니다.

진실 공급원은 sources/jp/cache/syukujitsu.csv 의 원본 바이트다. 이 파일들은
거기서 언제든 다시 만들 수 있고, 다시 만든 결과가 달라지면 그것이 곧 원본이
바뀌었다는 신호다. 그래서 시계를 읽지 않는다 — 같은 캐시로 두 번 돌리면 같은
바이트가 나와야 diff 가 "무엇이 실제로 바뀌었나"를 보여준다.

--------------------------------------------------------------------------
발행 범위만 옮긴다
--------------------------------------------------------------------------
CSV 는 1955 년부터 들고 있지만 여기로 오는 것은 RANGE_START ~ RANGE_END 뿐이다.
그 이전 구간은 캐시에 그대로 남아 있으므로 버리는 것이 아니다.

상한이 today+N 이 아니라 CSV 상한인 것이 한국과 다르다. 이 표는 연 1 회(전년
2 월) 한 해씩만 늘고, 특히 春分の日·秋分の日 은 전년 2 월 1 일 관보 고시로
확정되기 전까지 공식 날짜가 존재하지 않는다. 계산으로 미래를 채우면 정부가
아직 정하지 않은 날짜를 우리가 발표하는 것이 된다.

--------------------------------------------------------------------------
uid_token 에 우리 판정을 넣지 않는다
--------------------------------------------------------------------------
token 은 CSV 의 名称 에서 나온다. kind 에서 유도하지 않는다.

이 표의 `休日` 은 振替休日(제3조제2항)과 国民の休日(제3항)을 합쳐 부르는
이름이고, 두 규칙이 같은 날짜를 내는 해가 실제로 있다(1987-05-04). 어느 쪽인지는
우리가 규칙으로 유도한 판정이므로 나중에 바뀔 수 있다. 그것이 token 에 들어가
있으면 재분류가 곧 UID 변경이 되고, 구독자 캘린더에서 삭제 + 재생성으로
나타난다. rules/kr/feed.py 의 _token() 이 kind 를 쓰지 않는 것과 같은 이유다.

그래서 `休日` 은 kind 가 무엇으로 판정되든 token 이 kyujitsu 하나다.
날짜가 UID 에 이미 들어 있어 충돌하지 않는다 — CSV 는 한 날짜에 한 행이다.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from sources.jp import cao_client, cao_parser

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "jp"

# 발행 범위. 상한은 CSV 가 담고 있는 마지막 날짜다.
RANGE_START = date(2020, 1, 1)
RANGE_END = date(2027, 11, 23)

KIND_STATUTORY = "statutory"  # 国民の祝日 (祝日法 제2조)
KIND_SUBSTITUTE = "substitute"  # 振替休日 (제3조제2항)
KIND_BRIDGE = "bridge"  # 国民の休日 (제3조제3항)

LAW = "「国民の祝日に関する法律」(昭和23年法律第178号)"
OLYMPIC_LAW = (
    "「令和三年東京オリンピック競技大会・東京パラリンピック競技大会特別措置法」"
    "(平成27年法律第33号) 第32条"
)

# CSV 의 名称 → uid_token.
#
# 한 번 공개되면 바꿀 수 없다. 표기가 흔들려도(体育の日 → スポーツの日) token 은
# 그대로여야 하므로, 개칭 전후를 같은 token 으로 묶는다 — 같은 날을 가리키는
# 같은 축일이고 이름만 바뀐 것이다.
UID_TOKENS = {
    "元日": "new_years_day",
    "成人の日": "coming_of_age_day",
    "建国記念の日": "national_foundation_day",
    "天皇誕生日": "emperors_birthday",
    "春分の日": "vernal_equinox",
    "昭和の日": "showa_day",
    "憲法記念日": "constitution_day",
    "みどりの日": "greenery_day",
    "こどもの日": "childrens_day",
    "海の日": "marine_day",
    "山の日": "mountain_day",
    "敬老の日": "respect_for_the_aged_day",
    "秋分の日": "autumnal_equinox",
    "体育の日": "sports_day",
    "スポーツの日": "sports_day",
    "文化の日": "culture_day",
    "勤労感謝の日": "labor_thanksgiving_day",
    cao_parser.NAME_KYUJITSU: "kyujitsu",
}

# 조문이 날짜를 직접 정하지 않아 원문 대조가 끝나지 않은 것들.
#
#   春分の日 · 秋分の日  제2조는 「春分日」「秋分日」이라고만 한다. 실제 날짜는
#                        국립천문대가 전년 2 월 1 일 관보에 고시한다. 우리는 그
#                        관보를 확인하지 않았다.
#   建国記念の日          제2조가 「政令で定める日」이다. 그 정령(昭和41年政令
#                        第376号)을 확인하지 않았다.
UNVERIFIED = {
    "春分の日": "国立天文台が前年2月1日に官報で告示する日。当該年の官報を未確認。",
    "秋分の日": "国立天文台が前年2月1日に官報で告示する日。当該年の官報を未確認。",
    "建国記念の日": "第2条は「政令で定める日」とする。当該政令(昭和41年政令第376号)を未確認。",
}

# 올림픽 특별조치법 제32조가 옮긴 축일. {(연도, 명칭): (월, 일, 치환 문구)}
#
# 제1항이 令和2년(2020), 제2항이 令和3년(2021)이다. 조문을 e-Gov 에서 받아
# 그대로 옮겼다. 아래 문구는 조문의 「…とあるのは「…」」 부분이다.
_P1, _P2 = "第32条第1項", "第32条第2項"
OLYMPIC_MOVES = {
    (2020, "海の日"): (7, 23, "「七月の第三月曜日」とあるのは「七月二十三日」", _P1),
    (2020, "山の日"): (8, 10, "「八月十一日」とあるのは「八月十日」", _P1),
    (2020, "スポーツの日"): (7, 24, "「十月の第二月曜日」とあるのは「七月二十四日」", _P1),
    (2021, "海の日"): (7, 22, "「七月の第三月曜日」とあるのは「七月二十二日」", _P2),
    (2021, "山の日"): (8, 8, "「八月十一日」とあるのは「八月八日」", _P2),
    (2021, "スポーツの日"): (7, 23, "「十月の第二月曜日」とあるのは「七月二十三日」", _P2),
}

SUNDAY = 6


class BuildError(ValueError):
    """데이터를 만들 수 없다."""


def _classify(day: date, statutory: set) -> tuple:
    """`休日` 한 건의 kind 와 판정 근거.

    두 규칙을 각각 독립으로 판정하고, 둘 다 걸리면 멈춘다. 임의로 하나를
    고르지 않는다 — 그 선택이 곧 확인되지 않은 판정이 되고, 근거 필드가
    사실이 아닌 것을 말하게 된다.

    실제로 밟히는 경로다. 1987-05-04 이 그 예다(제2항으로도 제3항으로도
    설명된다). 지금 발행 범위 안에는 없지만 범위를 넓히면 걸린다.
    """
    prev_day, next_day = day - timedelta(days=1), day + timedelta(days=1)
    is_bridge = prev_day in statutory and next_day in statutory

    # 振替: 앞으로 거슬러 올라가며 祝日 이 이어지는 동안 일요일 祝日 을 찾는다.
    # 조문이 "그 날 후 가장 가까운 「국민의 축일」이 아닌 날"이라 연휴가 겹치면
    # 원인일과 휴일 사이가 벌어진다(2025-05-04 일 → 5/6).
    trigger = None
    probe = prev_day
    while probe in statutory:
        if probe.weekday() == SUNDAY:
            trigger = probe
            break
        probe -= timedelta(days=1)

    if trigger and is_bridge:
        raise BuildError(
            f"{day.isoformat()}: 振替休日 과 国民の休日 둘 다로 설명된다.\n"
            f"  제2항 원인일 {trigger.isoformat()}(일) / "
            f"제3항 전후 {prev_day.isoformat()}·{next_day.isoformat()}\n"
            "원본(内閣府 CSV)은 둘을 구분하지 않으므로 코드가 정할 수 없다.\n"
            "어느 조문이 이 날을 만들었는지는 사람이 정할 것."
        )
    if trigger:
        return KIND_SUBSTITUTE, {
            "rule": "第3条第2項",
            "trigger_date": trigger,
            "trigger_weekday": "日",
        }
    if is_bridge:
        return KIND_BRIDGE, {
            "rule": "第3条第3項",
            "prev_date": prev_day,
            "next_date": next_day,
        }
    raise BuildError(
        f"{day.isoformat()}: 名称 이 「休日」인데 어느 조문으로도 설명되지 않는다.\n"
        "전날/다음날이 「국민의 축일」이 아니고, 앞쪽에 일요일 축일도 없다.\n"
        "규칙이 개정되었거나 원본이 바뀌었을 수 있다. 사람이 확인할 것."
    )


def _entry(row, statutory: set) -> dict:
    """행 하나 → data/jp 항목 하나."""
    token = UID_TOKENS.get(row.name)
    if not token:
        raise BuildError(
            f"{row.day.isoformat()}: 모르는 名称 {row.name!r}.\n"
            "새 축일이 생겼거나 표기가 바뀌었다. UID_TOKENS 에 넣기 전에 "
            "그것이 새 축일인지 기존 축일의 개칭인지 확인할 것 — 개칭이면 "
            "기존 token 을 그대로 써야 UID 가 바뀌지 않는다."
        )

    out = {"date": row.day, "name": row.name, "uid_token": token}

    if row.name == cao_parser.NAME_KYUJITSU:
        kind, basis = _classify(row.day, statutory)
        out["kind"] = kind
        out["basis"] = basis
        out["verified"] = True
        out["source"] = f"{LAW} {basis['rule']}"
        return out

    out["kind"] = KIND_STATUTORY
    moved = OLYMPIC_MOVES.get((row.day.year, row.name))
    if moved:
        month, dayn, phrase, article = moved
        if (row.day.month, row.day.day) != (month, dayn):
            raise BuildError(
                f"{row.day.isoformat()} {row.name}: 특별조치법 {article} 는 "
                f"{month}월 {dayn}일로 읽히는데 CSV 는 다르다.\n"
                "조문과 원본이 어긋난다. 사람이 확인할 것."
            )
        out["verified"] = True
        out["source"] = f"{OLYMPIC_LAW} {article} — {phrase}"
        out["basis"] = {"rule": article, "note": "オリンピック特別措置法による移動"}
        return out

    todo = UNVERIFIED.get(row.name)
    out["verified"] = not todo
    out["source"] = f"{LAW} 第2条"
    if todo:
        out["source_todo"] = todo
    return out


def build(raw: bytes) -> dict:
    """캐시 바이트 → {연도: [항목]}. 발행 범위 안만."""
    rows = cao_parser.check(raw)

    # 祝日 집합은 표 전체에서 만든다. 범위 경계 바로 밖의 축일이 경계 안 휴일의
    # 판정에 쓰이기 때문이다(1/1 이 일요일이면 1/2 이 振替다).
    statutory = {r.day for r in rows if r.name != cao_parser.NAME_KYUJITSU}

    out = {}
    for row in rows:
        if not (RANGE_START <= row.day <= RANGE_END):
            continue
        out.setdefault(row.day.year, []).append(_entry(row, statutory))
    return out


def _dump(year: int, entries: list, meta: dict) -> str:
    """YAML 한 파일. 손으로 쓴 표와 섞이지 않게 머리말을 붙인다."""
    lines = [
        "# 이 파일은 기계가 만든다. 손으로 고치지 말 것.",
        "#",
        "# 원본  内閣府「国民の祝日について」",
        f"#       {cao_client.URL}",
        f"#       Last-Modified {meta.get('last_modified') or '(미상)'}",
        "#",
        "# 다시 만들려면: uv run python -m sources.jp.build_data",
        "# 진실 공급원은 sources/jp/cache/syukujitsu.csv 의 원본 바이트다.",
        "#",
        "# kind      statutory 国民の祝日 / substitute 振替休日 / bridge 国民の休日",
        "# basis     그 kind 로 판정한 근거. 원본에는 없고 우리가 유도한 값이다.",
        "# uid_token 名称 에서 나온다. kind 에서 유도하지 않는다(모듈 docstring 참조).",
        "",
        "version: 1",
        "country: jp",
        f"year: {year}",
        "holidays:",
    ]
    for e in entries:
        lines.append(f"  - date: {e['date'].isoformat()}")
        lines.append(f"    name: {e['name']}")
        lines.append(f"    uid_token: {e['uid_token']}")
        lines.append(f"    kind: {e['kind']}")
        lines.append(f"    verified: {'true' if e['verified'] else 'false'}")
        lines.append(f"    source: {e['source']}")
        if e.get("source_todo"):
            lines.append(f"    source_todo: {e['source_todo']}")
        basis = e.get("basis")
        if basis:
            lines.append("    basis:")
            for key, value in basis.items():
                text = value.isoformat() if isinstance(value, date) else value
                lines.append(f"      {key}: {text}")
    return "\n".join(lines) + "\n"


def write(raw: bytes = None, meta: dict = None) -> list:
    """data/jp/<연도>.yaml 을 쓴다. 쓴 경로 목록."""
    raw = cao_client.cached() if raw is None else raw
    meta = cao_client._read_meta() if meta is None else meta

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for year, entries in sorted(build(raw).items()):
        path = DATA_DIR / f"{year}.yaml"
        path.write_text(_dump(year, entries, meta), encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":  # pragma: no cover
    for _path in write():
        print(f"[jp] {_path}")
