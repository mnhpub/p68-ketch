"""Circulation and egress sheet: lifts, stairs, medical bay, tender storage, exits and routes.

Concept only. Stairs, exits, the medical bay and tender storage are not placed on the layout, so they are
drawn as labelled candidates. Lifts are shown for accessible movement only, not as escape routes.
Requires: pip install ezdxf matplotlib (virtual environment, not a project dependency).
Sources: decks.json (access text), layout/accessibility.json (lift stops), layout/decks-layout.json (lobbies),
layout/envelope-budget.json (candidate areas), layout/release-notice.json (release terms).
Output: drawings/schematics/P68-sheet-09-circulation-egress.dxf and P68-circulation-egress.pdf
Run with: python3 scripts/build-circulation.py
"""
import json
import textwrap
from pathlib import Path

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drawings" / "schematics"
OUT.mkdir(parents=True, exist_ok=True)
NOTICE = json.loads((ROOT / "layout/release-notice.json").read_text())
SIZE = json.loads((ROOT / "layout/proposed-size.json").read_text())
LOA = SIZE["loa_m"]
STATUS = "CONCEPT - NOT FOR CONSTRUCTION"
DATE = "10 Oct 2026"
RELEASE = (f"OPEN DESIGN RELEASE - {NOTICE['release_class']}. Licence: {NOTICE['licence']} "
           f"Funding: {NOTICE['funding']}")
NOTE = ("Stairs, exits, medical bay and tender storage are NOT placed on the layout: drawn as labelled candidates. "
        "Lifts are for accessible movement, not escape. Routes are concept only.")

# Level rows (drawing metres, y up). Row spacing 4 m. Bridge at the top.
ROWS = {"Bridge": 16.0, "Commander / Lido": 12.0, "Main / Master": 8.0, "Tween": 4.0, "Tank / Technical": 0.0}
ELEV = {"Bridge": "+9.30 m", "Commander / Lido": "+6.60 m", "Main / Master": "+3.35 m", "Tween": "+0.85 m", "Tank / Technical": "-1.50 m"}


def primitives():
    """Returns drawing primitives: ('line', pts, layer), ('rect', x0, y0, x1, y1, layer), ('text', x, y, s, size, layer)."""
    P = []
    for name, y in ROWS.items():
        P.append(("line", [(0, y), (LOA, y)], "LEVEL"))
        P.append(("text", -6.5, y - 0.4, f"{name}  {ELEV[name]}", 1.3, "TEXT"))
    # Lifts: lift A serves Bridge to Main; lift B serves all five levels (accessibility.json)
    P.append(("rect", 48.0, 8.0, 49.5, 16.0, "LIFT"))
    P.append(("rect", 49.5, 0.0, 51.0, 16.0, "LIFT"))
    P.append(("text", 48.0, 16.6, "Lift A (Bridge to Main)", 0.9, "TEXT"))
    P.append(("text", 49.5, -1.0, "Lift B (all levels)", 0.9, "TEXT"))
    # Stairs as recorded in decks.json: Bridge-Commander, Main-Tween (stairs), Tween-Tank (protected service stairs)
    stairs = [(42.0, 12.0, 16.0, "Stair Bridge-Commander (to set)"),
              (42.0, 4.0, 8.0, "Stair Main-Tween (to set)"),
              (42.0, 0.0, 4.0, "Stair Tween-Tank (to set)")]
    for x0, y0, y1, label in stairs:
        P.append(("rect", x0, y0, x0 + 2.0, y1, "STAIR"))
        P.append(("text", x0 + 2.3, (y0 + y1) / 2, label, 0.9, "TEXT"))
    P.append(("text", 42.0, 10.0, "No stair Commander-Main: lift only", 0.8, "TEXT"))
    # Candidate medical bay on Tween, next to the Tween lift lobby (accommodation note)
    P.append(("rect", 36.0, 4.4, 40.5, 6.6, "MEDBAY"))
    P.append(("text", 36.2, 6.9, "Medical bay (candidate, not placed)", 0.9, "TEXT"))
    # Candidate tender storage on Tank, with access from the bay (accommodation note)
    P.append(("rect", 52.0, 0.3, 58.0, 2.2, "TENDER"))
    P.append(("text", 52.2, 2.5, "Tender storage (candidate, not placed)", 0.9, "TEXT"))
    # Exits: positions to set. Drawn at the stern on Main and Tank.
    for y, label in [(8.0, "Exit, Main (to set)"), (0.0, "Exit, Tank (to set)")]:
        P.append(("rect", 0.0, y - 0.6, 1.4, y + 0.6, "EXIT"))
        P.append(("text", 1.7, y + 0.8, label, 0.9, "TEXT"))
    # Routes
    P.append(("line", [(36.5, 5.0), (46.5, 4.0), (49.7, 4.0), (49.7, 8.0), (1.4, 8.0)], "ROUTE_MEDBAY"))
    P.append(("line", [(38.2, 4.4), (43.0, 4.0), (43.0, 0.0), (52.0, 0.0)], "ROUTE_TENDER"))
    P.append(("line", [(58.0, 0.0), (1.4, 0.0)], "ROUTE_TENDER"))
    P.append(("text", 20.0, 20.0, "Route A: medical bay to lift B, then Main to the stern exit (accessible route).", 1.0, "TEXT"))
    P.append(("text", 20.0, 19.0, "Route B: medical bay to the Tween-Tank stair, then Tank to the stern exit. Tender route: storage to the exit.", 1.0, "TEXT"))
    P.append(("text", 0.0, -3.5, f"Concept circulation sheet. {LOA:.0f} m LOA. Drawing metres, real size.", 0.9, "TEXT"))
    return P


def paper_frame(doc, title, sheet_no):
    psp = doc.layout()
    psp.page_setup(size=(420, 297), margins=(10, 10, 10, 10), units="mm", offset=(0, 0))
    psp.add_lwpolyline([(10, 10), (410, 10), (410, 287), (10, 287), (10, 10)], dxfattribs={"layer": "FRAME"})
    psp.add_lwpolyline([(250, 10), (250, 45), (410, 45)], dxfattribs={"layer": "FRAME"})
    psp.add_text(title, dxfattribs={"layer": "TEXT", "height": 5}).set_placement((255, 36))
    psp.add_text("P68 KETCH - CONCEPT SCHEMATIC", dxfattribs={"layer": "TEXT", "height": 3.5}).set_placement((255, 28))
    psp.add_text(f"SHEET {sheet_no}   {DATE}   {STATUS}", dxfattribs={"layer": "TEXT", "height": 2.8}).set_placement((255, 21))
    for i, line in enumerate(textwrap.wrap(NOTE, 110)[:2]):
        psp.add_text(line, dxfattribs={"layer": "TEXT", "height": 2.2}).set_placement((15, 17 - i * 3.5))
    for i, line in enumerate(textwrap.wrap(RELEASE, 150)[:3]):
        psp.add_text(line, dxfattribs={"layer": "TEXT", "height": 2.0}).set_placement((15, 34 - i * 3.5))
    return psp


LAYER_COLORS = {"LEVEL": 8, "LIFT": 5, "STAIR": 4, "MEDBAY": 1, "TENDER": 6, "EXIT": 3,
                "ROUTE_MEDBAY": 1, "ROUTE_TENDER": 6, "TEXT": 7, "FRAME": 7}


def build_dxf(path):
    doc = ezdxf.new("R2013", setup=True)
    doc.units = ezdxf.units.MM
    for name, color in LAYER_COLORS.items():
        doc.layers.add(name, color=color)
    msp = doc.modelspace()
    for item in primitives():
        if item[0] == "line":
            pts = [(x * 1000, y * 1000) for x, y in item[1]]
            msp.add_lwpolyline(pts, dxfattribs={"layer": item[2]})
        elif item[0] == "rect":
            _, x0, y0, x1, y1, layer = item
            msp.add_lwpolyline([(x0 * 1000, y0 * 1000), (x1 * 1000, y0 * 1000), (x1 * 1000, y1 * 1000), (x0 * 1000, y1 * 1000), (x0 * 1000, y0 * 1000)], close=True, dxfattribs={"layer": layer})
        elif item[0] == "text":
            _, x, y, s, size, layer = item
            msp.add_text(s, dxfattribs={"layer": layer, "height": size * 1000 * 0.35}).set_placement((x * 1000, y * 1000))
    psp = paper_frame(doc, "CIRCULATION AND EGRESS (concept)", 9)
    psp.add_viewport(center=(210, 150), size=(400, 240), view_center_point=(LOA * 1000 / 2, 8000), view_height=44000.0)
    doc.saveas(path)


def build_pdf(path):
    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(-10, 72)
    ax.set_ylim(-6, 24)
    ax.set_aspect("equal")
    ax.axis("off")
    colors = {"LEVEL": "#2f4d5e", "LIFT": "#1f6f8b", "STAIR": "#8e3b6a", "MEDBAY": "#a33", "TENDER": "#b7791f",
              "EXIT": "#3a7d44", "ROUTE_MEDBAY": "#a33", "ROUTE_TENDER": "#b7791f", "TEXT": "#102027"}
    for item in primitives():
        if item[0] == "line":
            xs, ys = zip(*item[1])
            lw = 2.0 if item[2] in ("ROUTE_MEDBAY", "ROUTE_TENDER") else 0.9
            ls = "--" if item[2].startswith("ROUTE") else "-"
            ax.plot(xs, ys, color=colors[item[2]], linewidth=lw, linestyle=ls)
        elif item[0] == "rect":
            _, x0, y0, x1, y1, layer = item
            dashed = layer in ("STAIR", "EXIT", "MEDBAY", "TENDER")
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=colors[layer], linewidth=0.8,
                                   linestyle="--" if dashed else "-"))
        elif item[0] == "text":
            _, x, y, s, size, layer = item
            ax.text(x, y, s, fontsize=size * 6, color=colors[layer])
    ax.text(-10, 23, "CIRCULATION AND EGRESS (concept): lifts, stairs, medical bay, tender storage, exits", fontsize=12, color="#102027")
    ax.text(-10, -5.6, NOTE, fontsize=6, color="#5d7887")
    ax.text(-10, -6.0, f"{STATUS}   {DATE}   SHEET 9", fontsize=6, color="#8e3b6a")
    for i, line in enumerate(textwrap.wrap(RELEASE, 200)[:3]):
        ax.text(-10, -6.0 - 0.45 * (i + 1) - 0.35, line, fontsize=5, color="#5d7887")
    fig.savefig(path) if False else None
    with PdfPages(path) as pdf:
        pdf.savefig(fig)
    plt.close(fig)


def main():
    build_dxf(OUT / "P68-sheet-09-circulation-egress.dxf")
    build_pdf(OUT / "P68-circulation-egress.pdf")
    print("wrote P68-sheet-09-circulation-egress.dxf and P68-circulation-egress.pdf")


if __name__ == "__main__":
    main()
