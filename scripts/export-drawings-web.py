"""Export the latest drafting sheets for the web.

- DXF (AutoCAD) and PDF sheets are copied to public/drawings/ for download.
- Engineering deck sheets are PNG pages of the deck PDF (the deck SVGs render mostly black, see step 2).
- PDF sheets are rasterised page by page to PNG at 200 dpi (PyMuPDF).
Outputs: public/drawings/cad, public/drawings/schematics, public/drawings/png.
Run with: npm run export:drawings  (after npm run build:cad and the schematic scripts)
"""
import shutil
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
DRAW = ROOT / "drawings"
PUB = ROOT / "public" / "drawings"
PNG = PUB / "png"
CAD = PUB / "cad"
SCH = PUB / "schematics"
for d in (PNG, CAD, SCH):
    d.mkdir(parents=True, exist_ok=True)

# 1. DXF and PDF for download
for f in sorted((DRAW / "cad").glob("*.dxf")):
    shutil.copy2(f, CAD / f.name)
for f in sorted((DRAW / "schematics").glob("*.dxf")) + sorted((DRAW / "schematics").glob("*.pdf")):
    shutil.copy2(f, SCH / f.name)
shutil.copy2(DRAW / "P68-engineering-deck-plans.pdf", PUB / "P68-engineering-deck-plans.pdf")
print(f"downloads: {len(list(CAD.glob('*.dxf')))} deck DXF, {len(list(SCH.glob('*.dxf')))} schematic DXF, {len(list(SCH.glob('*.pdf')))} schematic PDF")

# 2. Engineering deck sheets: PDF pages to PNG, named by deck.
# The deck SVGs from the DXF plot render mostly black (their class styles are not all declared), so the web
# uses the PDF pages, which are the same plot. Page order matches the deck order in the sheet list.
DECK_SHEETS = ['bridge', 'commander-lido', 'main-master', 'tween', 'tank-technical']
eng = pymupdf.open(DRAW / "P68-engineering-deck-plans.pdf")
for i, name in enumerate(DECK_SHEETS, start=1):
    out = PNG / f"eng-deck-{i:02d}-{name}.png"
    eng[i - 1].get_pixmap(dpi=200, alpha=False).save(out)
    print("png", out.relative_to(ROOT))

# 3. Schematic PDF pages to PNG
pdfs = sorted((DRAW / "schematics").glob("*.pdf"))
for pdf in pdfs:
    doc = pymupdf.open(pdf)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=200, alpha=False)
        out = PNG / f"{pdf.stem}-p{i:02d}.png"
        pix.save(out)
    print(f"png {pdf.name}: {doc.page_count} page(s)")
