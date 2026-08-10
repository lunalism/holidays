"""밖으로 나가는 문자열에서 비밀값을 지운다.

--------------------------------------------------------------------------
왜 core 에 있나 — 국가 중립인가
--------------------------------------------------------------------------
전에는 이 코드가 sources/kr/kasi_client.py 에만 있었다. 거기서 나온 이유는
KASI 인증키가 쿼리 문자열로 실려 나가기 때문이었지만, **코드 자체에 KASI
지식이 없다.**

여기 담긴 사실은 이것뿐이다 — 비밀값이 URL 에 실리면 원본·퍼센트 인코딩·
이중 인코딩·디코딩된 형태 중 무엇으로든 나타날 수 있다. 그건 HTTP 의 성질이지
특정 API 의 성질이 아니다. 다른 나라 소스를 붙여도 같은 것이 필요하다.

국가별인 것은 "어느 환경변수에 비밀값이 들었나"다. 그건 여기서 정하지 않는다.
호출자가 값을 넘기거나, secrets_from_env() 가 이름으로 찾아낸다.

--------------------------------------------------------------------------
왜 buildlog 가 이걸 쓰나
--------------------------------------------------------------------------
logs/build.jsonl 은 저장소에 커밋되고, Pages 를 붙이면 공개 URL 로 그대로
서빙된다. 그 파일의 error 필드에는 빌드 로그 끝부분이 실린다.

지금 발행 파이프라인은 네트워크를 타지 않아 키가 흘러들 원천이 없다. 하지만
나중에 KASI 조회가 한 스텝 들어오는 순간, 스크럽을 빠뜨린 예외 한 줄이 공개
파일에 박힌다. 그때 알아채기는 어렵고 되돌리기는 더 어렵다 — git 히스토리에
남고, 이미 크롤링된 뒤일 수 있다.

그래서 buildlog 는 무엇이 들어올지 모르는 채로 일단 거른다.
core/buildlog.py 의 record_from_env() 참조.
"""

from __future__ import annotations

import os
from urllib.parse import quote, unquote

# 이름에 이 조각이 들어간 환경변수는 비밀값으로 본다.
#
# 목록 방식(어느 변수를 지울지 적어 두기)을 쓰지 않은 이유는 잊히기 때문이다.
# 새 비밀값을 스텝에 추가하면서 목록 갱신을 빠뜨리면 그 값만 조용히 새어 나가고,
# 빠뜨렸다는 사실은 유출된 뒤에야 드러난다. 이름 규칙은 잊을 수가 없다.
#
# 과탐은 감수한다. 비밀이 아닌 값이 마스킹돼도 손해는 오류 메시지 하나가
# 덜 읽히는 것뿐이고, 반대 방향의 손해와 비교가 되지 않는다.
SECRET_NAME_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")

# 이 길이 이하의 값은 환경변수 이름이 걸려도 지우지 않는다.
# "true", "1", "none" 같은 값까지 마스킹하면 오류 메시지가 읽히지 않게 된다.
MIN_SECRET_LENGTH = 8


def mask(secret: str) -> str:
    """로그용. 앞뒤 4자와 길이만 남긴다."""
    if len(secret) <= 12:
        return "*" * len(secret)
    return f"{secret[:4]}...{secret[-4:]}({len(secret)}자)"


def forms(secret: str) -> set:
    """이 비밀값이 문자열에 나타날 수 있는 모든 형태.

    이중 인코딩까지 포함해야 한다. 라이브러리가 이미 인코딩된 값을 한 번 더
    인코딩하면 '%2B' 가 '%252B' 가 되는데, 그 형태가 예외 메시지에 실려 나온다.
    실제로 관측된 적이 있다 — sources/kr/kasi_client.py 의 key_forms 주석 참조.
    """
    once = quote(secret, safe="")
    return {
        secret,
        once,
        quote(once, safe=""),
        unquote(secret),
        quote(unquote(secret), safe=""),
    }


def scrub(text: str, *secrets: str) -> str:
    """비밀값이 어떤 형태로 들어 있든 지운다.

    로그·출력·예외 메시지에 넣기 전에 통과시킬 것.
    긴 형태부터 지워야 짧은 형태가 먼저 걸려 부분 치환되는 일이 없다.
    """
    if not text:
        return text
    for secret in secrets:
        if not secret:
            continue
        replacement = mask(secret)
        for form in sorted(forms(secret), key=len, reverse=True):
            if form:
                text = text.replace(form, replacement)
    return text


def secrets_from_env(env: dict = None) -> list:
    """환경에서 비밀값으로 보이는 것들의 값.

    이름에 SECRET_NAME_HINTS 가 들어가고 MIN_SECRET_LENGTH 이상인 값만 고른다.
    값이 긴 것부터 돌려준다 — 짧은 값이 긴 값의 일부일 때 부분 치환을 막는다.
    """
    env = os.environ if env is None else env
    found = [
        value
        for name, value in env.items()
        if value
        and len(value) >= MIN_SECRET_LENGTH
        and any(hint in name.upper() for hint in SECRET_NAME_HINTS)
    ]
    return sorted(set(found), key=len, reverse=True)
