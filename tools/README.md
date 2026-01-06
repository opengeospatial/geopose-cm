# Tools

## `pdf_slide_analyzer.py`

Renders a slide PDF to images and generates a Markdown report containing:
- embedded PDF text extraction (PyMuPDF)
- optional OCR of the rendered images (macOS Vision via PyObjC)

Example:

```zsh
cd /Users/christineperey/Desktop/GitHub\ GeoPose/geopose-cm
python3 tools/pdf_slide_analyzer.py \
  "refactoring-resources/GeoPose 1.1 slides.pptx.pdf" \
  --out-dir "refactoring-resources/slide-images-lowres" \
  --dpi 110 \
  --format jpg \
  --jpeg-quality 80 \
  --ocr \
  --report "refactoring-resources/slide-images-lowres/report.md"
```

Notes:
- OCR requires `pyobjc-framework-Vision` (installed via `python3 -m pip install --user pyobjc-framework-Vision`).
- If OCR is disabled, the report will still include embedded PDF text and image links.
