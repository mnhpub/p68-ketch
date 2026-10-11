"""Plot the engineering deck sheets from the AutoCAD DXF sources (the source of truth).

Reads drawings/cad/P68-ENG-NN-*.dxf and writes the plotted SVG for the app, the PDF book and the PNG
sheets' PDF source. Nothing is regenerated from the layout here: edit the DXF in AutoCAD, then run
npm run build:cad (or npm run build:hull, which extracts the layout first).
"""
import io
from pathlib import Path

import ezdxf
import pymupdf as fitz

import p68
from cad_plans import plot

CAD = p68.OUT / "cad"
ROOT_OUT = p68.OUT


def main():
    book = fitz.open()
    files = []
    for deck in p68.decks():
        stem = f"P68-ENG-{deck.index:02d}-{p68.slug(deck.name)}"
        doc = ezdxf.readfile(CAD / f"{stem}.dxf")
        svg_str, pdf_bytes = plot(doc, "A3 1-200")
        app_name = f"eng-deck-{deck.file_stem}.svg"
        (ROOT_OUT / app_name).write_text(svg_str)
        book.insert_pdf(fitz.open(stream=io.BytesIO(pdf_bytes).getvalue(), filetype="pdf"))
        files.append(app_name)
        print(f"plotted drawings/cad/{stem}.dxf -> drawings/{app_name}")
    book.set_metadata({"title": "P68 Ketch engineering deck plans (schematic)", "author": "P68 Ketch design team",
                       "creationDate": "", "modDate": ""})
    book.save(ROOT_OUT / "P68-engineering-deck-plans.pdf", garbage=4, deflate=True)
    print("wrote drawings/P68-engineering-deck-plans.pdf")
    return files


if __name__ == "__main__":
    main()
