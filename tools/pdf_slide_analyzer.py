#!/usr/bin/env python3
"""PDF slide analyzer: render pages to images and extract text.

- Renders each PDF page to a JPEG/PNG at a configurable DPI (via PyMuPDF)
- Extracts embedded PDF text (via PyMuPDF)
- Optionally OCRs the rendered image using macOS Vision (via PyObjC)
- Writes a Markdown report linking each rendered slide image and including extracted text

This is intended to help interpret diagrams + captions from slide PDFs.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF


@dataclass(frozen=True)
class OcrResult:
    text: str
    engine: str


def _try_import_vision():
    try:
        import Vision  # type: ignore
        from Foundation import NSURL  # type: ignore

        return Vision, NSURL
    except Exception:
        return None


def ocr_with_macos_vision(image_path: Path) -> Optional[OcrResult]:
    imported = _try_import_vision()
    if imported is None:
        return None

    Vision, NSURL = imported

    url = NSURL.fileURLWithPath_(str(image_path))
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, {})

    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    request.setUsesLanguageCorrection_(True)

    ok, err = handler.performRequests_error_([request], None)
    if not ok:
        raise RuntimeError(f"Vision OCR failed for {image_path}: {err}")

    results = request.results() or []
    lines = []
    for obs in results:
        candidates = obs.topCandidates_(1)
        if candidates and len(candidates) > 0:
            lines.append(str(candidates[0].string()))

    return OcrResult(text="\n".join(lines).strip(), engine="macOS Vision")


def render_pdf_pages(
    pdf_path: Path,
    out_dir: Path,
    dpi: int,
    image_format: str,
    jpeg_quality: int,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)

    rendered: list[Path] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_file = out_dir / f"slide-{i+1:02d}.{image_format}"

            if image_format.lower() in {"jpg", "jpeg"}:
                pix.save(out_file, output="jpeg", jpg_quality=jpeg_quality)
            elif image_format.lower() == "png":
                pix.save(out_file)
            else:
                raise ValueError(f"Unsupported format: {image_format}")

            rendered.append(out_file)

    return rendered


def extract_embedded_text(pdf_path: Path) -> list[str]:
    texts: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            texts.append((page.get_text("text") or "").strip())
    return texts


def write_report(
    pdf_path: Path,
    out_dir: Path,
    image_paths: list[Path],
    embedded_text: list[str],
    ocr_texts: list[Optional[OcrResult]],
    report_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rel_prefix = os.path.relpath(out_dir, report_path.parent)

    lines: list[str] = []
    lines.append(f"# Slide analysis report\n")
    lines.append(f"- Source PDF: `{pdf_path}`")
    lines.append(f"- Rendered images: `{out_dir}`\n")

    for idx, img in enumerate(image_paths, start=1):
        lines.append(f"## Slide {idx:02d}\n")
        rel_img = Path(rel_prefix) / img.name
        lines.append(f"![Slide {idx:02d}]({rel_img.as_posix()})\n")

        et = embedded_text[idx - 1] if idx - 1 < len(embedded_text) else ""
        if et:
            lines.append("**Embedded PDF text**")
            lines.append("```text")
            lines.append(et)
            lines.append("```\n")

        ocr = ocr_texts[idx - 1] if idx - 1 < len(ocr_texts) else None
        if ocr is not None and ocr.text:
            lines.append(f"**OCR text ({ocr.engine})**")
            lines.append("```text")
            lines.append(ocr.text)
            lines.append("```\n")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render slide PDF to images and extract text (embedded + OCR).")
    parser.add_argument("pdf", type=Path, help="Path to the PDF")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory to write rendered images")
    parser.add_argument("--dpi", type=int, default=110, help="Render DPI (default: 110)")
    parser.add_argument("--format", default="jpg", choices=["jpg", "jpeg", "png"], help="Image format")
    parser.add_argument("--jpeg-quality", type=int, default=80, help="JPEG quality (if using jpg/jpeg)")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR using macOS Vision (requires PyObjC)")
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Markdown report output path",
    )

    args = parser.parse_args()

    image_paths = render_pdf_pages(
        pdf_path=args.pdf,
        out_dir=args.out_dir,
        dpi=args.dpi,
        image_format=args.format,
        jpeg_quality=args.jpeg_quality,
    )

    embedded_text = extract_embedded_text(args.pdf)

    ocr_texts: list[Optional[OcrResult]] = [None] * len(image_paths)
    if args.ocr:
        for i, image_path in enumerate(image_paths):
            ocr_texts[i] = ocr_with_macos_vision(image_path)

    write_report(
        pdf_path=args.pdf,
        out_dir=args.out_dir,
        image_paths=image_paths,
        embedded_text=embedded_text,
        ocr_texts=ocr_texts,
        report_path=args.report,
    )

    print(f"Wrote report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
