"""KASI getRestDeInfo 응답(XML) 파서.

원시 XML 을 날짜별 항목으로 옮긴다. 해석은 하지 않는다. 대체공휴일이 왜 생겼는지,
그 날이 정말 공휴일인지 같은 판단은 rules/kr 이 한다. 여기서는 옮기기만 한다.

--------------------------------------------------------------------------
설계
--------------------------------------------------------------------------
키는 locdate 다. seq 는 읽지 않는다.
seq 는 1 과 2 가 섞여 나오는데 규칙을 모른다(kasi_names.yaml 의 seq-의미 참조).
의미를 모르는 값을 계산에 끌어들이면 나중에 왜 그렇게 동작하는지 아무도 설명하지
못하게 된다. 확인될 때까지 없는 것으로 다룬다.

이름 → 키 매핑은 kasi_names.yaml 이 들고 있다. 코드에 두지 않는다.
표에 없는 이름은 UnmappedHolidayName 으로 터뜨린다. 조용히 건너뛰면 KASI 가
새로 추가한 공휴일을 놓치고, 놓친 것은 오류로 드러나지 않는다.

"대체공휴일(광복절)"의 괄호 안 이름은 caused_by_name 에 원문 그대로 남긴다.
교차검증용이다. 우리 쪽 유도 결과와 원인 공휴일이 같은지 확인할 때 쓴다.
계산에는 쓰지 말 것. 그 순간 KASI 가 정답이 되고 우리 규칙 테이블은 장식이 된다.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

NAMES_PATH = Path(__file__).parent / "kasi_names.yaml"

# 이름 안의 괄호를 뜯는 데만 정규식을 쓴다. XML 구조는 파서가 읽는다.
_SUBSTITUTE_RE = re.compile(r"^(.+?)\((.+)\)$")

KIND_SUBSTITUTE = "substitute"


class KasiParseError(ValueError):
    """응답을 읽을 수 없다."""


class UnmappedHolidayName(KasiParseError):
    """kasi_names.yaml 에 없는 dateName 을 만났다.

    무시하지 않고 터뜨린다. 새 공휴일이 생겼거나 표기가 바뀌었다는 신호이고,
    둘 다 사람이 판단할 일이다. 표에 한 줄 넣고 끝낼 문제가 아니다.
    """


class AmbiguousHolidayName(KasiParseError):
    """이름은 아는데 그 날짜의 성격을 모른다.

    "대통령선거일"이 그렇다. 임기만료 선거면 법정공휴일이고 궐위 선거면
    임시공휴일인데, 이름만으로는 갈리지 않는다. by_date 에 그 날짜가 없으면
    사유를 확인하기 전까지 답하지 않는다. 한쪽으로 찍으면 절반은 틀린다.
    """


@dataclass(frozen=True)
class KasiHoliday:
    """응답 한 줄. 해석하지 않은 상태 그대로."""

    date: date
    name: str              # dateName 원문
    key: str               # 매핑된 공휴일 키. 선거일·임시공휴일 등은 None
    kind: str              # statutory / substitute / election ...
    caused_by_name: str = ""  # 대체공휴일의 괄호 안 원문. 교차검증 전용

    @property
    def is_substitute(self) -> bool:
        return self.kind == KIND_SUBSTITUTE


def load_names(path: Path = None) -> dict:
    raw = yaml.safe_load((path or NAMES_PATH).read_text(encoding="utf-8"))
    return {
        "prefix": raw["substitute_prefix"],
        "names": raw["names"],
    }


def load_service(path: Path = None) -> dict:
    """활용 서비스 정보(operation, expires_on).

    이름 매핑과 같은 파일에 있지만 성격이 다르다. 이름 표는 응답을 읽는 데
    쓰이고, 이쪽은 그 응답을 받을 자격이 언제까지인지를 말한다.
    같은 파일에 두는 이유는 둘 다 같은 활용신청에 매여 있어서다 —
    다른 서비스를 신청하면 둘 다 새로 생긴다.
    """
    raw = yaml.safe_load((path or NAMES_PATH).read_text(encoding="utf-8"))
    service = raw.get("service")
    if not service:
        raise KasiParseError(
            "kasi_names.yaml 에 service 블록이 없다. 활용기간 만료일을 확인할 수 없다."
        )
    return service


def _parse_locdate(value: str) -> date:
    if not re.fullmatch(r"\d{8}", value):
        raise KasiParseError(f"locdate 형식이 아니다: {value!r}")
    return date(int(value[:4]), int(value[4:6]), int(value[6:]))


def _resolve(name: str, table: dict, day: date) -> tuple:
    """dateName 을 (key, kind, caused_by_name) 으로 옮긴다."""
    entry = table["names"].get(name)
    if entry is not None:
        by_date = entry.get("by_date")
        if by_date:
            # 이름 하나로 성격이 정해지지 않는 항목. 날짜별로 확인해 둔 것만 답한다.
            override = by_date.get(day)
            if override is None:
                raise AmbiguousHolidayName(
                    f"{name!r} 의 {day} 성격이 kasi_names.yaml 의 by_date 에 없다.\n"
                    "임기만료 선거인지 궐위 선거인지에 따라 election/temporary 가 갈린다. "
                    "사유를 확인하고 by_date 에 넣을 것. 짐작으로 한쪽을 고르지 말 것."
                )
            return entry.get("key"), override["kind"], ""
        return entry.get("key"), entry.get("kind") or "statutory", ""

    # "대체공휴일(광복절)" 꼴인가.
    match = _SUBSTITUTE_RE.match(name)
    if match and match.group(1) == table["prefix"]:
        cause = match.group(2)
        if cause not in table["names"]:
            raise UnmappedHolidayName(
                f"대체공휴일의 원인 공휴일 {cause!r} 가 kasi_names.yaml 에 없다 "
                f"(원문 {name!r}). 원인 쪽도 매핑해 두어야 교차검증이 된다."
            )
        return None, KIND_SUBSTITUTE, cause

    raise UnmappedHolidayName(
        f"kasi_names.yaml 에 없는 dateName: {name!r}\n"
        "조용히 건너뛰지 않는다. 새 공휴일이 생겼거나 표기가 바뀌었다는 신호다.\n"
        "응답을 확인하고 표에 넣을 것. 넣기 전에 rules/kr 쪽도 손볼 것이 있는지 볼 것."
    )


def check_envelope(xml: str):
    """정상 응답 봉투인지 확인하고 루트 엘리먼트를 돌려준다.

    실패하면 KasiParseError. 통과하면 그 응답은 저장해도 되는 것이다.

    이 함수가 따로 있는 이유는 kasi_client 가 캐시에 쓰기 전에 같은 검사를
    해야 하기 때문이다. 클라이언트가 XML 을 직접 뜯으면 검사가 두 벌이 되고,
    한쪽만 고쳐 놓으면 저장은 되는데 읽지 못하는 파일이 생긴다.
    응답 구조를 아는 곳은 이 모듈 하나여야 한다.

    두 가지 실패 형태를 갈라 본다.

      resultCode 가 없다   data.go.kr 이 인증 실패 등을 다른 봉투
                          (OpenAPI_ServiceResponse)로 준다. 관측된 실물은
                          tests/fixtures/kasi_errors/ 에 있다.
      resultCode != 00     정상 봉투인데 서비스 쪽 오류다.

    둘 다 HTTP 상태와 무관하게 성립한다. 관측된 인증 오류는 401·403 과 함께
    왔지만, 봉투만 보고도 판정할 수 있어야 한다. HTTP 상태에 기대면 200 으로
    오는 오류를 놓친다.
    """
    try:
        root = ET.fromstring(xml.strip())
    except ET.ParseError as exc:
        raise KasiParseError(f"XML 로 읽히지 않는다: {exc}") from exc

    code = root.findtext("header/resultCode")
    if code is None:
        detail = (root.findtext(".//errMsg") or root.findtext(".//returnAuthMsg") or "").strip()
        raise KasiParseError(
            f"resultCode 가 없다. 정상 응답 봉투가 아니다 (root={root.tag!r})."
            + (f" 메시지: {detail}" if detail else "")
        )
    if code.strip() != "00":
        message = (root.findtext("header/resultMsg") or "").strip()
        raise KasiParseError(f"정상 응답이 아니다. resultCode={code.strip()} {message}")
    return root


def item_count(xml: str) -> int:
    """응답에 실린 item 개수. 봉투가 정상이 아니면 KasiParseError.

    parse() 로 세지 않는 이유가 있다. parse() 는 이름을 전부 매핑해야 통과하므로
    kasi_names.yaml 에 없는 이름이 하나만 있어도 터진다. 여기서 필요한 것은
    "이 응답에 몇 건이 실려 있나"뿐이고, 그 답은 이름을 몰라도 낼 수 있다.
    매핑 여부에 세는 일이 걸리면 캐시 보호가 이름 표 상태에 끌려다니게 된다.

    totalCount 가 아니라 item 을 직접 센다. totalCount 는 없을 수도 있는
    엘리먼트라 없으면 0 인지 미상인지 갈리지 않는다. item 은 세면 그만이다.
    둘이 어긋나는 경우는 parse() 가 페이지네이션으로 잡는다.
    """
    root = check_envelope(xml)
    return len(root.findall("body/items/item"))


def parse(xml: str, table: dict = None) -> tuple:
    """원시 XML → KasiHoliday 목록. 날짜 오름차순.

    같은 날짜에 항목이 여럿이면 그대로 여럿 돌려준다. 합치지 않는다.
    합치는 규칙을 정하려면 seq 의 의미를 알아야 하는데 아직 모른다.
    """
    table = table or load_names()
    root = check_envelope(xml)

    out = []
    for item in root.findall("body/items/item"):
        name = (item.findtext("dateName") or "").strip()
        locdate = (item.findtext("locdate") or "").strip()
        if not name or not locdate:
            raise KasiParseError(
                "item 에 locdate 또는 dateName 이 없다: "
                + str({child.tag: child.text for child in item})
            )
        # seq 는 읽지 않는다. 의미를 모르는 값을 계산에 끌어들이지 않는다.
        day = _parse_locdate(locdate)
        key, kind, cause = _resolve(name, table, day)
        out.append(
            KasiHoliday(
                date=day,
                name=name,
                key=key,
                kind=kind,
                caused_by_name=cause,
            )
        )

    total = root.findtext("body/totalCount")
    if total is not None and int(total.strip()) != len(out):
        raise KasiParseError(
            f"totalCount({total.strip()}) 와 파싱된 항목 수({len(out)}) 가 다르다. "
            "페이지네이션에 걸렸을 수 있다. numOfRows 를 확인할 것."
        )

    return tuple(sorted(out, key=lambda h: (h.date, h.name)))
