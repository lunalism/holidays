"""内閣府「国民の祝日について」CSV 의 파싱과 검증.

    https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv

응답 구조를 아는 곳은 여기 하나다. cao_client 는 받아서 캐시에 넣기만 하고,
무엇이 정상인지는 이 모듈에 묻는다. 한국 쪽 kasi_client / kasi_parser 의
역할 분담과 같다 — 검사가 두 벌이 되면 한쪽만 고쳐 놓고 "저장은 되는데 읽지
못하는 파일"이 생긴다.

--------------------------------------------------------------------------
인코딩은 Shift-JIS(CP932) 다
--------------------------------------------------------------------------
응답 헤더의 Content-Type 은 `text/csv` 뿐이고 charset 이 없다. 헤더를 믿으면
안 되고, 실제 바이트가 CP932 다(첫 바이트가 8d 91 96 af = 「国民」).
BOM 은 없고 줄끝은 CRLF 다.

cp932 로 읽는다. shift_jis 로도 디코드되고 지금 파일에서는 결과가 같지만,
cp932 가 상위집합이라 기종의존문자가 섞여 들어와도 깨지지 않는다.

--------------------------------------------------------------------------
'休日' 은 두 규칙을 합쳐 부르는 이름이다
--------------------------------------------------------------------------
이 표에서 名称 이 `休日` 인 행은 振替休日(祝日法 제3조제2항)과
国民の休日(같은 조 제3항)을 구분하지 않는다. 원본이 구분하지 않으므로 여기서도
구분하지 않는다 — 가르는 것은 규칙 유도이고 그건 이 모듈의 일이 아니다.

두 규칙이 같은 날짜를 내는 해가 실제로 있다(1987-05-04). 그런 날은 원리적으로
갈리지 않으므로, 판정 결과를 원본 파싱 단계에 섞으면 안 된다.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date

ENCODING = "cp932"

# 헤더 한 줄이 그대로 이 문자열이어야 한다. 표기가 바뀌면 컬럼 의미도 바뀌었을 수
# 있으므로 조용히 넘기지 않는다.
HEADER = ("国民の祝日・休日月日", "国民の祝日・休日名称")

# 원본이 振替休日과 国民の休日을 함께 부르는 이름.
NAME_KYUJITSU = "休日"


class CaoParseError(ValueError):
    """CSV 를 읽을 수 없다."""


@dataclass(frozen=True)
class Row:
    """CSV 한 줄. 원본 그대로이며 우리 판정이 섞이지 않는다."""

    day: date
    name: str


def decode(raw: bytes) -> str:
    """원시 바이트 → 문자열.

    바이트를 인자로 받는다. 파일을 여기서 읽지 않는 것은 캐시 원본이 진실
    공급원이기 때문이다 — 어디서 온 바이트든 같은 검사를 통과해야 한다.
    """
    if raw[:3] == b"\xef\xbb\xbf":
        raise CaoParseError(
            "UTF-8 BOM 이 붙어 있다. 이 파일은 CP932 였다.\n"
            "인코딩이 바뀌었을 수 있으니 원본을 먼저 확인할 것."
        )
    try:
        return raw.decode(ENCODING)
    except UnicodeDecodeError as exc:
        raise CaoParseError(
            f"{ENCODING} 로 디코드하지 못했다: byte {exc.start}\n"
            "내각부가 인코딩을 바꿨을 수 있다. 원본 바이트를 확인할 것."
        ) from None


def parse(raw: bytes) -> list:
    """원시 바이트 → [Row]. 파일에 실린 순서 그대로.

    정렬하지 않는다. 원본이 이미 날짜 오름차순이고, 여기서 다시 정렬하면
    "원본이 흐트러졌다"는 사실이 보이지 않게 된다. 순서 검사는 check() 가 한다.
    """
    rows = list(csv.reader(io.StringIO(decode(raw))))
    if not rows:
        raise CaoParseError("CSV 가 비어 있다.")

    head = tuple(c.strip() for c in rows[0])
    if head != HEADER:
        raise CaoParseError(
            f"헤더가 예상과 다르다.\n  기대: {HEADER}\n  실제: {head}\n"
            "컬럼 의미가 바뀌었을 수 있다. 사람이 확인할 것."
        )

    out = []
    for lineno, row in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in row):
            continue  # 끝의 빈 줄
        if len(row) != 2:
            raise CaoParseError(f"{lineno} 행의 컬럼이 2 개가 아니다: {row!r}")
        out.append(Row(day=_day(row[0], lineno), name=row[1].strip()))
    return out


def _day(value: str, lineno: int) -> date:
    """`YYYY/M/D` → date. zero-padding 이 없으므로 strptime 대신 쪼갠다."""
    parts = value.strip().split("/")
    if len(parts) != 3:
        raise CaoParseError(f"{lineno} 행의 날짜 형식이 YYYY/M/D 가 아니다: {value!r}")
    try:
        y, m, d = (int(p) for p in parts)
        return date(y, m, d)
    except ValueError as exc:
        raise CaoParseError(f"{lineno} 행의 날짜를 읽지 못했다: {value!r} — {exc}") from None


def check(raw: bytes) -> list:
    """캐시에 쓰기 전 검사. 통과하면 [Row] 를 돌려준다.

    parse() 가 구조를 보고, 여기서 표 전체의 성질을 본다. 한 줄씩 봐서는
    알 수 없는 것들이다.
    """
    rows = parse(raw)
    if not rows:
        raise CaoParseError("헤더만 있고 데이터가 없다.")

    days = [r.day for r in rows]
    if days != sorted(days):
        raise CaoParseError(
            "날짜가 오름차순이 아니다. 원본은 정렬되어 있어야 한다.\n"
            "정렬이 깨졌다면 파일이 우리가 아는 그 파일이 아니다."
        )

    dupes = sorted({d for d in days if days.count(d) > 1})
    if dupes:
        raise CaoParseError(
            "같은 날짜가 두 번 나온다: "
            + ", ".join(d.isoformat() for d in dupes[:5])
            + "\n이 표는 날짜가 유일해야 한다(한 날짜에 공휴일은 하나로 적힌다)."
        )

    blank = [r for r in rows if not r.name]
    if blank:
        raise CaoParseError(
            f"名称 이 빈 행이 {len(blank)} 건 있다: "
            + ", ".join(r.day.isoformat() for r in blank[:5])
        )
    return rows


def row_count(raw: bytes) -> int:
    """데이터 행 수. 캐시 가드가 쓰는 값이다."""
    return len(parse(raw))
