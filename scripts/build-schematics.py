"""Concept schematics: one DXF per sheet for AutoCAD, plus one PDF with every sheet.

Requires: pip install ezdxf matplotlib (a virtual environment, not a project dependency).
Sources: layout/decks-layout.json (room rectangles), decks.json (deck elevations),
layout/proposed-size.json (final principal dimensions).
Output: drawings/schematics/. Every sheet is marked CONCEPT, NOT FOR CONSTRUCTION.
Run with: python3 scripts/build-schematics.py
"""
import json
import math
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

layout = json.loads((ROOT / "layout/decks-layout.json").read_text())
decks = json.loads((ROOT / "decks.json").read_text())
size = json.loads((ROOT / "layout/proposed-size.json").read_text())

LOA, B = float(layout["loa"]), float(layout["beam"])
LWL = LOA * 62 / 68  # waterline ratio from docs/hull-size-final.md
STATUS = "CONCEPT - NOT FOR CONSTRUCTION"
DATE = "10 Oct 2026"
NOTICE = json.loads((ROOT / "layout/release-notice.json").read_text())
RELEASE = (f"OPEN DESIGN RELEASE - {NOTICE['release_class']}. Licence: {NOTICE['licence']} "
           f"Funding: {NOTICE['funding']}")
_HULL = json.loads((Path(__file__).resolve().parent.parent / "layout" / "decks-layout.json").read_text())
NOTE = (f"Hull outline from layout/decks-layout.json at {_HULL['loa']:g} m by {_HULL['beam']:.1f} m. Rooms are from layout coordinates, inferred, not dimensioned. "
        "Deck datum as recorded in decks.json.")
MM = 1000  # model units are millimetres, real size


def hull_outline(n=120):
    """Ellipse plan model in metres, stern at x=0, centreline y=0."""
    a, b = LOA / 2, B / 2
    return [(a + a * math.cos(2 * math.pi * i / n), b * math.sin(2 * math.pi * i / n)) for i in range(n)]


def elevation_value(text):
    return float(text.replace("−", "-").replace(" m", "").replace("+", ""))


def deck_by_name(name):
    return next(d for d in layout["decks"] if d["name"] == name)


def elevation_of(name):
    return next((d["elevation"] for d in decks if d["name"] == name), "")


# ---------- DXF sheets (one file per sheet) ----------

def new_dxf():
    doc = ezdxf.new("R2013", setup=True)
    doc.units = ezdxf.units.MM
    for name, color in [("HULL_MODEL", 8), ("CENTRELINE", 1), ("GRID", 9), ("ROOMS", 3), ("LIFT", 5),
                        ("TEXT", 7), ("FRAME", 7), ("DECK", 4), ("WATERLINE", 5)]:
        doc.layers.add(name, color=color)
    return doc


def paper_frame(doc, title, sheet_no):
    """A3 landscape paper space with a frame and title block (paper units, mm)."""
    psp = doc.layout()
    psp.page_setup(size=(420, 297), margins=(10, 10, 10, 10), units="mm", offset=(0, 0))
    psp.add_lwpolyline([(10, 10), (410, 10), (410, 287), (10, 287), (10, 10)], dxfattribs={"layer": "FRAME"})
    psp.add_lwpolyline([(250, 10), (250, 45), (410, 45)], dxfattribs={"layer": "FRAME"})
    psp.add_text(title, dxfattribs={"layer": "TEXT", "height": 5}).set_placement((255, 36))
    psp.add_text("P68 KETCH - CONCEPT SCHEMATIC", dxfattribs={"layer": "TEXT", "height": 3.5}).set_placement((255, 28))
    psp.add_text(f"SHEET {sheet_no}   {DATE}   {STATUS}", dxfattribs={"layer": "TEXT", "height": 2.8}).set_placement((255, 21))
    psp.add_text(NOTE[:100], dxfattribs={"layer": "TEXT", "height": 2.2}).set_placement((15, 17))
    psp.add_text(NOTE[100:], dxfattribs={"layer": "TEXT", "height": 2.2}).set_placement((15, 13))
    for i, line in enumerate(textwrap.wrap(RELEASE, 150)[:3]):
        psp.add_text(line, dxfattribs={"layer": "TEXT", "height": 2.0}).set_placement((15, 34 - i * 3.5))
    return psp


def deck_dxf(doc, deck, sheet_no):
    msp = doc.modelspace()
    msp.add_lwpolyline([(x * MM, y * MM) for x, y in deck["outline"]], close=True, dxfattribs={"layer": "HULL_MODEL"})
    msp.add_line((0, 0), (LOA * MM, 0), dxfattribs={"layer": "CENTRELINE"})
    for x in range(0, int(LOA) + 1, 10):
        msp.add_line((x * MM, -B / 2 * MM - 800), (x * MM, B / 2 * MM + 800), dxfattribs={"layer": "GRID"})
        msp.add_text(f"{x} m", dxfattribs={"layer": "GRID", "height": 600}).set_placement((x * MM, -B / 2 * MM - 1500))
    for r in deck["rooms"]:
        if "rect" not in r:
            continue
        x0, y0, x1, y1 = [v * MM for v in r["rect"]]
        layer = "LIFT" if "lift" in r["name"].lower() else "ROOMS"
        msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], close=True, dxfattribs={"layer": layer})
        if (x1 - x0) >= 4 * MM and (y1 - y0) >= 2 * MM:
            msp.add_text(r["name"], dxfattribs={"layer": "TEXT", "height": 400}).set_placement(((x0 + x1) / 2, (y0 + y1) / 2))
    # Paper space viewport fitted to the hull, at about 1:150 on A3.
    psp = paper_frame(doc, f"PLAN - {deck['name'].upper()}  (deck {elevation_of(deck['name'])})", sheet_no)
    vh = 45000.0  # model height shown, mm
    psp.add_viewport(center=(210, 150), size=(400, 240), view_center_point=(LOA * MM / 2, 0), view_height=vh)


def principal_dxf(doc, sheet_no):
    psp = paper_frame(doc, "PRINCIPAL DIMENSIONS AND DECK PROFILE", sheet_no)
    rows = [
        ("LOA", f"{LOA:.1f} m"), ("LWL", f"{LWL:.1f} m"), ("Beam", f"{B:.1f} m"), ("L/B", f"{LOA / B:.2f}"),
        ("Design displacement target", "1,487 t"), ("Draft, keel-up target", "4.8 m (4.80 m at 1,487 t)"),
        ("Draft, keel-down target", "7.2 m (2,231 t)"), ("GM target", "1.0 m; KG limit 6.01 m"),
        ("Roll period at GM 1.0 m", "10.4 s"), ("Hull speed", "19.1 kn"),
        ("Gyro (roll damping, zeta 0.10)", "255 kN·m peak; H 1.27e6 kg·m²/s"),
    ]
    y = 270
    for k, v in rows:
        psp.add_text(k, dxfattribs={"layer": "TEXT", "height": 3.2}).set_placement((20, y))
        psp.add_text(v, dxfattribs={"layer": "TEXT", "height": 3.2}).set_placement((120, y))
        y -= 8
    psp.add_text("PROFILE - DECK LEVELS (datum as in decks.json)", dxfattribs={"layer": "TEXT", "height": 3.5}).set_placement((20, 150))
    base, scale = 90, 8
    for d in decks:
        yy = base + elevation_value(d["elevation"]) * scale
        psp.add_line((20, yy), (300, yy), dxfattribs={"layer": "DECK"})
        psp.add_text(f"{d['name']}  {d['elevation']}", dxfattribs={"layer": "TEXT", "height": 2.6}).set_placement((305, yy - 1))
    psp.add_line((20, base), (300, base), dxfattribs={"layer": "WATERLINE"})
    psp.add_text("Waterline (blue) relation to the deck datum to be confirmed.", dxfattribs={"layer": "TEXT", "height": 2.4}).set_placement((20, base - 6))


def section_dxf(doc, sheet_no):
    """Midship section in DXF, mm model space, at x = LOA / 2. Model section, not a lines plan."""
    msp = doc.modelspace()
    xm = LOA / 2
    half = max(abs(y) for d in layout["decks"] for x, y in d["outline"] if abs(x - xm) < 1.0)
    z0 = elevation_value(decks[-1]["elevation"])
    zs = []
    for deck in layout["decks"]:
        z = elevation_value(elevation_of(deck["name"]))
        zs.append(z)
        msp.add_line((-half * MM, (z - z0) * MM), (half * MM, (z - z0) * MM), dxfattribs={"layer": "DECK"})
        msp.add_text(f"{deck['name']} {elevation_of(deck['name'])}", dxfattribs={"layer": "TEXT", "height": 300}).set_placement((half * MM + 400, (z - z0) * MM))
    msp.add_lwpolyline([(-half * MM, (zs[-1] - z0) * MM - 0), (-half * MM, (zs[0] - z0) * MM)], dxfattribs={"layer": "HULL_MODEL"})
    msp.add_lwpolyline([(half * MM, (zs[-1] - z0) * MM), (half * MM, (zs[0] - z0) * MM)], dxfattribs={"layer": "HULL_MODEL"})
    msp.add_text("MIDSHIP SECTION (model, rectangular, not a lines plan)", dxfattribs={"layer": "TEXT", "height": 400}).set_placement((-half * MM, (zs[-1] - z0) * MM - 2000))
    psp = paper_frame(doc, f"MIDSHIP SECTION (x = {xm:.0f} m)", sheet_no)
    mid = (max(zs) - z0) * MM / 2
    psp.add_viewport(center=(210, 150), size=(400, 240), view_center_point=(0, mid), view_height=22000.0)


def profile_dxf(doc, sheet_no):
    """Centreline profile in DXF, mm model space. Model profile, not a lines plan."""
    msp = doc.modelspace()
    base = 0.0
    for deck in layout["decks"]:
        z = elevation_value(elevation_of(deck["name"]))
        msp.add_line((0, z * MM), (LOA * MM, z * MM), dxfattribs={"layer": "DECK"})
        msp.add_text(f"{deck['name']} {elevation_of(deck['name'])}", dxfattribs={"layer": "TEXT", "height": 300}).set_placement((LOA * MM + 400, z * MM))
        for r in deck["rooms"]:
            if "rect" not in r or abs(r["rect"][1]) > 2.0 or abs(r["rect"][3]) < 0.5:
                continue
            x0, _, x1, _ = r["rect"]
            layer = "LIFT" if "lift" in r["name"].lower() else "ROOMS"
            msp.add_lwpolyline([(x0 * MM, z * MM), (x1 * MM, z * MM), (x1 * MM, z * MM + 2000), (x0 * MM, z * MM + 2000), (x0 * MM, z * MM)], close=True, dxfattribs={"layer": layer})
    msp.add_line((0, base), (LOA * MM, base), dxfattribs={"layer": "WATERLINE"})
    msp.add_text("Waterline (datum relation to be confirmed)", dxfattribs={"layer": "TEXT", "height": 300}).set_placement((0, base - 1500))
    psp = paper_frame(doc, "CENTRELINE PROFILE (model)", sheet_no)
    psp.add_viewport(center=(210, 150), size=(400, 240), view_center_point=(LOA * MM / 2, 4000), view_height=30000.0)


# ---------- PDF renderings (all sheets in one file) ----------

def release_lines(ax):
    """Open design release terms at the foot of a PDF sheet."""
    for i, line in enumerate(textwrap.wrap(RELEASE, 200)[:3]):
        ax.text(25, 10 - i * 4, line, fontsize=5, color="#5d7887")


def pdf_plan(deck, sheet_no):
    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.set_aspect("equal")
    ax.axis("off")
    sx = (420 - 50) / LOA
    cy = 150
    m = lambda x, y: (25 + x * sx, cy + y * sx)
    ox, oy = zip(*[m(x, y) for x, y in deck["outline"]])
    ax.plot(ox, oy, color="#8da5b0", linestyle="--", linewidth=0.8)
    a, b = m(0, 0), m(LOA, 0)
    ax.plot([a[0], b[0]], [a[1], b[1]], color="#c6a67d", linewidth=0.5)
    for x in range(0, int(LOA) + 1, 10):
        p, q = m(x, -B / 2 - 0.6), m(x, B / 2 + 0.6)
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#d0d7db", linewidth=0.3)
        ax.text(p[0], p[1] - 4, f"{x} m", fontsize=5, color="#5d7887", ha="center")
    for r in deck["rooms"]:
        if "rect" not in r:
            continue
        x0, y0, x1, y1 = r["rect"]
        color = "#a33" if "lift" in r["name"].lower() else "#2f4d5e"
        p = m(x0, y0)
        ax.add_patch(Rectangle(p, (x1 - x0) * sx, (y1 - y0) * sx, fill=False, edgecolor=color, linewidth=0.6))
        if (x1 - x0) >= 4 and (y1 - y0) >= 2:
            c = m((x0 + x1) / 2, (y0 + y1) / 2)
            ax.text(c[0], c[1], r["name"], fontsize=5, color="#102027", ha="center", va="center")
    ax.text(25, 40, f"PLAN - {deck['name'].upper()}  (deck {elevation_of(deck['name'])})", fontsize=12, color="#102027")
    ax.text(25, 30, NOTE, fontsize=6, color="#5d7887")
    ax.text(25, 22, f"{STATUS}   {DATE}   SHEET {sheet_no}", fontsize=7, color="#8e3b6a")
    release_lines(ax)
    return fig


def pdf_principal(sheet_no):
    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.axis("off")
    ax.text(20, 280, "PRINCIPAL DIMENSIONS", fontsize=14, color="#102027")
    rows = [
        ("LOA", f"{LOA:.1f} m"), ("LWL", f"{LWL:.1f} m"), ("Beam", f"{B:.1f} m"), ("L/B", f"{LOA / B:.2f}"),
        ("Design displacement target", "1,487 t"), ("Draft, keel-up target", "4.8 m (4.80 m at 1,487 t)"),
        ("Draft, keel-down target", "7.2 m (2,231 t)"), ("GM target", "1.0 m; KG limit 6.01 m"),
        ("Roll period at GM 1.0 m", "10.4 s"), ("Hull speed", "19.1 kn"),
        ("Gyro (roll damping, zeta 0.10)", "255 kN·m peak; H 1.27e6 kg·m²/s"),
    ]
    y = 262
    for k, v in rows:
        ax.text(20, y, k, fontsize=8, color="#102027")
        ax.text(130, y, v, fontsize=8, color="#102027")
        y -= 9
    ax.text(20, 150, "PROFILE - DECK LEVELS (datum as in decks.json)", fontsize=9, color="#102027")
    base, scale = 90, 8
    for d in decks:
        yy = base + elevation_value(d["elevation"]) * scale
        ax.plot([20, 300], [yy, yy], color="#2f4d5e", linewidth=0.8)
        ax.text(305, yy - 2, f"{d['name']}  {d['elevation']}", fontsize=7, color="#102027")
    ax.plot([20, 300], [base, base], color="#1f6f8b", linewidth=0.9)
    ax.text(20, base - 6, "Waterline (blue) relation to the deck datum to be confirmed.", fontsize=6, color="#5d7887")
    ax.text(25, 22, f"{STATUS}   {DATE}   SHEET {sheet_no}", fontsize=7, color="#8e3b6a")
    ax.text(25, 14, NOTE, fontsize=6, color="#5d7887")
    release_lines(ax)
    return fig


def pdf_section(sheet_no):
    """Midship section at x = LOA / 2, from the regenerated outline. Model section, not a lines plan."""
    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.set_aspect("equal")
    ax.axis("off")
    xm = LOA / 2
    half = max(abs(y) for d in layout["decks"] for x, y in d["outline"] if abs(x - xm) < 1.0)
    sc = 17.0  # mm per metre, one scale both ways
    cx, cy = 210, 50
    z0 = elevation_value(decks[-1]["elevation"])  # lowest deck as datum for the section drawing
    def m(y, z):
        return (cx + y * sc, cy + (z - z0) * sc)
    for deck in layout["decks"]:
        z = elevation_value(elevation_of(deck["name"]))
        a, b = m(-half, z), m(half, z)
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#2f4d5e", linewidth=0.8)
        ax.text(b[0] + 4, b[1] - 2, f"{deck['name']} {elevation_of(deck['name'])}", fontsize=6, color="#102027")
    left = [m(-half, elevation_value(elevation_of(d["name"]))) for d in decks]
    right = [m(half, elevation_value(elevation_of(d["name"]))) for d in decks]
    ax.plot([p[0] for p in left], [p[1] for p in left], color="#8da5b0", linestyle="--", linewidth=0.7)
    ax.plot([p[0] for p in right], [p[1] for p in right], color="#8da5b0", linestyle="--", linewidth=0.7)
    ax.text(25, 280, "MIDSHIP SECTION (model: rectangular section from the uniform-taper outline; not a lines plan)", fontsize=10, color="#102027")
    ax.text(25, 270, f"x = {xm:.0f} m from the stern. Beam {2 * half:.1f} m. Deck datum as in decks.json.", fontsize=7, color="#5d7887")
    ax.text(25, 22, f"{STATUS}   {DATE}   SHEET {sheet_no}", fontsize=7, color="#8e3b6a")
    ax.text(25, 14, NOTE, fontsize=6, color="#5d7887")
    release_lines(ax)
    return fig


def pdf_profile(sheet_no):
    """Centreline profile: each deck's rooms along the length, at deck level. Model profile, not a lines plan."""
    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 420)
    ax.set_ylim(0, 297)
    ax.axis("off")
    sx = (420 - 50) / LOA
    base = 90
    sz = 9
    for deck in layout["decks"]:
        z = elevation_value(elevation_of(deck["name"]))
        y = base + z * sz
        ax.plot([25, 25 + LOA * sx], [y, y], color="#2f4d5e", linewidth=0.8)
        ax.text(25 + LOA * sx + 3, y - 2, f"{deck['name']} {elevation_of(deck['name'])}", fontsize=6, color="#102027")
        for r in deck["rooms"]:
            if "rect" not in r or abs(r["rect"][1]) > 2.0 or abs(r["rect"][3]) < 0.5:
                continue
            x0, _, x1, _ = r["rect"]
            color = "#a33" if "lift" in r["name"].lower() else "#5d7887"
            ax.add_patch(Rectangle((25 + x0 * sx, y), (x1 - x0) * sx, 3.0, fill=True, facecolor=color, edgecolor="none", alpha=0.5))
    wl = base
    ax.plot([25, 25 + LOA * sx], [wl, wl], color="#1f6f8b", linewidth=0.9)
    ax.text(25, wl - 8, "Waterline (blue), deck datum as in decks.json (relation to be confirmed)", fontsize=6, color="#5d7887")
    ax.text(25, 250, "CENTRELINE PROFILE (model: deck levels and centreline room extents; not a lines plan)", fontsize=10, color="#102027")
    ax.text(25, 240, "Shaded bands: rooms crossing the centreline. Red: lift shafts.", fontsize=7, color="#5d7887")
    ax.text(25, 22, f"{STATUS}   {DATE}   SHEET {sheet_no}", fontsize=7, color="#8e3b6a")
    ax.text(25, 14, NOTE, fontsize=6, color="#5d7887")
    release_lines(ax)
    return fig


def main():
    sheets = []
    dxf_paths = []
    n = 1
    doc = new_dxf()
    principal_dxf(doc, n)
    p = OUT / f"P68-sheet-{n:02d}-principal.dxf"
    doc.saveas(p)
    dxf_paths.append(p.name)
    sheets.append(pdf_principal(n))
    for deck in layout["decks"]:
        n += 1
        doc = new_dxf()
        deck_dxf(doc, deck, n)
        slug = deck["name"].lower().replace(" / ", "-").replace(" ", "-")
        p = OUT / f"P68-sheet-{n:02d}-plan-{slug}.dxf"
        doc.saveas(p)
        dxf_paths.append(p.name)
        sheets.append(pdf_plan(deck, n))
    sheets.append(pdf_section(n + 1))
    sheets.append(pdf_profile(n + 2))
    n += 1
    doc = new_dxf()
    section_dxf(doc, n)
    p = OUT / f"P68-sheet-{n:02d}-midship-section.dxf"
    doc.saveas(p)
    dxf_paths.append(p.name)
    n += 1
    doc = new_dxf()
    profile_dxf(doc, n)
    p = OUT / f"P68-sheet-{n:02d}-centreline-profile.dxf"
    doc.saveas(p)
    dxf_paths.append(p.name)
    with PdfPages(OUT / "P68-concept-schematics.pdf") as pdf:
        for fig in sheets:
            pdf.savefig(fig)
            plt.close(fig)
    print(f"wrote {len(dxf_paths)} DXF sheets and P68-concept-schematics.pdf ({len(sheets)} pages)")


if __name__ == "__main__":
    main()
