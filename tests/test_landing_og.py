"""랜딩 <head> 의 og:locale 계열과 og:image 크기는 기존 값에서 유도된다.

근거는 docs/seo.md 「링크 프리뷰 표기」. 새 문구·새 자산 없이 채우는 셋 —
og:locale(locale 키의 구분자 변환), og:locale:alternate(languages() 에서 자기를
뺀 것), og:image:width/height(assets/og.png 의 실제 픽셀 크기).

이 파일이 고정하는 것은 값이 아니라 유도식이다. 특히 둘:

- locale 키(BCP 47, 하이픈)는 원본 그대로이고 og:locale(밑줄)은 렌더 시점의
  변환이다. 변환이 원본을 건드리면 스크립트의 toLocaleDateString 이 깨진다.
- og:image 크기는 파일에서 읽는다. 상수로 두면 이미지가 바뀌었을 때 값이
  어긋난 채로 통과한다 — 여기서는 파일을 독립적으로 파싱해 태그와 대조하고,
  가짜 PNG 로 유도가 파일을 따라오는지도 본다.

render.render(lang) 을 직접 부르므로 마커가 없다 — tests/test_landing_head.py
와 같은 자리. og:image:alt·면별 이미지는 미결이라 여기 없다.
"""

from __future__ import annotations

import re
import struct
import zlib

import pytest
import yaml

from landing import render

LANGS = render.languages()
every_page = pytest.mark.parametrize("lang", LANGS)

HEAD = re.compile(r"<head>(.*?)</head>", re.DOTALL)
META = r'<meta property="{}" content="([^"]*)">'


def _head(lang: str) -> str:
    m = HEAD.search(render.render(lang))
    assert m, "<head> 가 없다"
    return m.group(1)


def _metas(head: str, name: str) -> list[str]:
    return re.findall(META.format(re.escape(name)), head)


def _meta(head: str, name: str) -> str:
    found = _metas(head, name)
    assert len(found) == 1, f"{name} 이 {len(found)} 개다"
    return found[0]


def _locale_key(lang: str) -> str:
    text = (render.LOCALES_DIR / f"{lang}.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)["locale"]


def _png_size(data: bytes) -> tuple[int, int]:
    """PNG IHDR 의 폭·높이. render 의 구현과 별개로 여기서 직접 읽는다."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[12:16] == b"IHDR"
    return struct.unpack(">II", data[16:24])


def _tiny_png(width: int, height: int) -> bytes:
    """폭·높이만 의미 있는 최소 PNG. 유도가 파일을 따라오는지 보는 데 쓴다."""

    def chunk(kind: bytes, body: bytes) -> bytes:
        crc = struct.pack(">I", zlib.crc32(kind + body))
        return struct.pack(">I", len(body)) + kind + body + crc

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * width for _ in range(height))
    chunks = chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + chunks


# ---------------------------------------------------------------------------
# og:locale — 그 면의 언어, 밑줄 구분
# ---------------------------------------------------------------------------


@every_page
def test_og_locale_is_the_locale_key_with_an_underscore(lang):
    assert _meta(_head(lang), "og:locale") == _locale_key(lang).replace("-", "_")


@every_page
def test_og_locale_alternate_is_every_other_language(lang):
    # 속성이 반복되는 형태 — OG 프로토콜이 배열을 그렇게 표현한다.
    expected = {_locale_key(other).replace("-", "_") for other in LANGS if other != lang}
    assert set(_metas(_head(lang), "og:locale:alternate")) == expected
    assert len(_metas(_head(lang), "og:locale:alternate")) == len(expected)


@every_page
def test_og_locale_values_carry_no_hyphen(lang):
    head = _head(lang)
    for value in [_meta(head, "og:locale"), *_metas(head, "og:locale:alternate")]:
        assert "-" not in value and "_" in value, value


@every_page
def test_the_locale_key_keeps_its_hyphen(lang):
    # 변환은 렌더 시점의 것이다. 원본 키는 BCP 47 그대로이고, 스크립트의
    # toLocaleDateString 에도 그 형식으로 들어간다.
    assert "-" in _locale_key(lang)
    page = render.render(lang)
    assert f'toLocaleDateString("{_locale_key(lang)}"' in page


# ---------------------------------------------------------------------------
# og:image:width / height — 파일의 실제 크기
# ---------------------------------------------------------------------------


@every_page
def test_og_image_size_matches_the_png_file(lang):
    head = _head(lang)
    width, height = _png_size((render.ROOT / render.OG_IMAGE_PATH).read_bytes())
    assert _meta(head, "og:image:width") == str(width)
    assert _meta(head, "og:image:height") == str(height)


def test_og_image_size_follows_the_file(tmp_path, monkeypatch):
    # 유도의 증명 — 이미지를 바꾸면 값이 따라온다. 상수였다면 여기서 걸린다.
    fake = tmp_path / "og.png"
    fake.write_bytes(_tiny_png(2, 3))
    monkeypatch.setattr(render, "OG_IMAGE_FILE", fake)
    head = _head("ko")
    assert _meta(head, "og:image:width") == "2"
    assert _meta(head, "og:image:height") == "3"


def test_a_non_png_og_image_stops(tmp_path, monkeypatch):
    # 형식이 바뀌면 조용히 0×0 을 내지 않고 멈춘다.
    fake = tmp_path / "og.png"
    fake.write_bytes(b"GIF89a" + b"\x00" * 30)
    monkeypatch.setattr(render, "OG_IMAGE_FILE", fake)
    with pytest.raises(ValueError, match="PNG"):
        render.render("ko")
