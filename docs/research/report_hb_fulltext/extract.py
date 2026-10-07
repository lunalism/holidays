# ruff: noqa
"""PDF 텍스트층을 쪽마다 뽑는다. OCR 은 하지 않는다.

사용: uv run --no-project --with 'pypdf==5.4.0' python -I extract.py <pdf-dir> <txt-dir> > extract_stats.tsv
      (<pdf-dir> 대신 PDF 파일 하나와 <out.txt> 를 줘도 된다 — 대조군용)
출력 txt: 쪽마다 "\f=== page N ===\n" 머리 뒤에 그 쪽 텍스트(pypdf extract_text 그대로, 정규화 없음).
표준출력: file<TAB>pages<TAB>chars(머리 제외 전체 문자 수)<TAB>쪽별 비공백 문자 수(쉼표 구분)<TAB>error
"""
import pathlib
import sys

import pypdf


def extract(pdf, out):
    try:
        reader = pypdf.PdfReader(str(pdf))
        parts, total, nonws = [], 0, []
        for i, page in enumerate(reader.pages, 1):
            t = page.extract_text() or ""
            parts.append(f"\f=== page {i} ===\n{t}\n")
            total += len(t)
            nonws.append(sum(1 for c in t if not c.isspace()))
    except Exception as e:  # 읽지 못한 파일은 오류 열에 적고 계속한다
        return [pdf.name, "", "", "", f"{type(e).__name__}: {e}"]
    pathlib.Path(out).write_text("".join(parts), encoding="utf-8")
    return [pdf.name, str(len(nonws)), str(total), ",".join(map(str, nonws)), ""]


src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
print("file\tpages\tchars\tnonws_per_page\terror")
if src.is_dir():
    dst.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(src.glob("*.pdf")):
        print("\t".join(extract(pdf, dst / (pdf.stem + ".txt"))), flush=True)
else:
    print("\t".join(extract(src, dst)))
