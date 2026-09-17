"""BGBl. PDF 의 한 페이지 이미지 스트림 해시. 파일 해시가 아니라 스트림 해시.

사용:  uv run --with pikepdf==9.11.0 --with pypdf==6.19.0 --with pymupdf==1.26.5 \
           --with pdfminer.six==20251107 python hash_page.py <pdf> [pdf-page(1-based), 기본 6]
출력:  (a0) 디스크에 저장된 스트림 바이트(AES 암호문) — 사본마다 다름
       (a)  복호화한 뒤, 필터(CCITTFax)는 풀지 않은 바이트 — pikepdf 와 pypdf 로 교차
       (b)  CCITT G4 를 푼 1-bit 비트맵(행마다 바이트 정렬, 1=검정, 패딩 0)
            — pdfminer 와 PyMuPDF 로 교차
"""

import hashlib
import re
import sys

import fitz
import pikepdf
import pypdf
from pdfminer.ccitt import ccittfaxdecode


def sha(b):
    return hashlib.sha256(b).hexdigest()


def page_images(page):
    imgs = []

    def walk(res, prefix=""):
        for k, v in (res.get("/XObject", {}) or {}).items():
            if v.get("/Subtype") == "/Image":
                imgs.append((prefix + str(k), v))
            elif v.get("/Subtype") == "/Form":
                walk(v.get("/Resources", {}), prefix + str(k) + ">")

    walk(page.Resources)
    return imgs


def ondisk_stream(data, num, length):
    m = re.search(rb"(?<![0-9])%d 0 obj\b" % num, data)
    s = data.index(b"stream", m.end()) + len(b"stream")
    s += 2 if data[s : s + 2] == b"\r\n" else 1
    return data[s : s + length]


def pack_1bit(samples, w, h):
    """8-bit gray(0=검정) → 1-bit, 행 바이트 정렬, 1=검정, 패딩 0."""
    packed = bytearray()
    for y in range(h):
        bits = n = 0
        for v in samples[y * w : (y + 1) * w]:
            bits = (bits << 1) | (1 if v == 0 else 0)
            n += 1
            if n == 8:
                packed.append(bits)
                bits = n = 0
        if n:
            packed.append(bits << (8 - n))
    return bytes(packed)


def main():
    path = sys.argv[1]
    page_no = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    pdf = pikepdf.open(path)
    imgs = page_images(pdf.pages[page_no - 1])
    print(f"{path}: pdf-page {page_no}, image XObjects: {len(imgs)}, encrypted={pdf.is_encrypted}")
    data = open(path, "rb").read()
    reader = pypdf.PdfReader(path)
    if reader.is_encrypted:
        reader.decrypt("")
    for name, st in imgs:
        num = st.objgen[0]
        dp = {str(k): v for k, v in st.get("/DecodeParms", {}).items()}
        print(
            f"  {name} obj {st.objgen} Filter={st.Filter} {int(st.Width)}x{int(st.Height)}"
            f" bpc={int(st.BitsPerComponent)} cs={st.ColorSpace}"
            f" Decode={list(st.get('/Decode', []))}"
            f" Length={int(st.Length)} DecodeParms={dp}"
        )
        ondisk = ondisk_stream(data, num, int(st.Length))
        print(f"    (a0) on-disk bytes            len={len(ondisk)} sha256={sha(ondisk)}")
        raw = st.read_raw_bytes()
        raw2 = reader.get_object(num)._data
        print(f"    (a)  decrypted, still encoded len={len(raw)} sha256={sha(raw)}  [pikepdf]")
        print(
            f"    (a)  decrypted, still encoded len={len(raw2)} sha256={sha(raw2)}  [pypdf]"
            f"  agree={raw == raw2}"
        )
        if st.Filter != "/CCITTFaxDecode":
            continue
        params = {
            "K": int(dp.get("/K", 0)),
            "Columns": int(dp.get("/Columns", 1728)),
            "Rows": int(dp.get("/Rows", int(st.Height))),
            "BlackIs1": bool(dp.get("/BlackIs1", False)),
            "EncodedByteAlign": bool(dp.get("/EncodedByteAlign", False)),
            "EndOfLine": bool(dp.get("/EndOfLine", False)),
        }
        dec = ccittfaxdecode(raw, params)
        print(f"    (b)  decoded 1-bit (1=black)  len={len(dec)} sha256={sha(dec)}  [pdfminer.six]")
        pix = fitz.Pixmap(fitz.open(path), num)
        packed = pack_1bit(pix.samples, pix.width, pix.height)
        print(
            f"    (b)  decoded 8-bit gray       len={len(pix.samples)} sha256={sha(pix.samples)}"
            "  [PyMuPDF Pixmap]"
        )
        print(
            f"    (b)  PyMuPDF packed to 1-bit  sha256={sha(packed)}"
            f"  agree-with-pdfminer={packed == dec}"
        )


if __name__ == "__main__":
    main()
