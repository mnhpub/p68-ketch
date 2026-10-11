"""Extract layout/decks-layout.json from the AutoCAD deck sheets (drawings/cad/P68-ENG-NN-*.dxf).

The DXF sheets are the source of truth for the deck plans. This script reads them and writes the layout
that the drawings, elevations, checks and renders use. Nothing is typed in by hand.

Read from each sheet:
- A-FLOR-OTLN: the deck outline (per deck, so decks may taper).
- A-AREA polylines with XDATA P68 (name, status, finish, furniture): rooms, as their bounding rectangles.
- A-ROOF-OTLN polylines with XDATA P68: roof rooms (outside the hull plan).
- S-MAST circles with their labels: mast stations, merged across sheets.

Read from layout/hull.json: rig data by mast name (top height, foundation area) and nothing else.
Run with: npm run extract:layout   (also runs automatically at the start of npm run build:hull)
"""
import json
import sys
from pathlib import Path

import ezdxf

ROOT = Path(__file__).resolve().parent.parent
CAD = ROOT / "drawings" / "cad"
HULL = json.loads((ROOT / "layout" / "hull.json").read_text())
OUT = ROOT / "layout" / "decks-layout.json"
DECKS = [
    ("Bridge", "bridge"),
    ("Commander / Lido", "commander-lido"),
    ("Main / Master", "main-master"),
    ("Tween", "tween"),
    ("Tank / Technical", "tank-technical"),
]


def unflip(points):
    """The plot stores y as -y (port negative in the layout). Return layout coordinates."""
    return [[round(x, 2), round(-y, 2)] for x, y in points]


def rect_of(points):
    pts = unflip(points)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]


def xdata_name(entity):
    if entity.has_xdata("P68"):
        return entity.get_xdata("P68")[0].value
    return None


def xdata_status(entity):
    if entity.has_xdata("P68"):
        vals = [t.value for t in entity.get_xdata("P68")]
        return vals[1] if len(vals) > 1 else ""
    return ""


def read_sheet(name, slug):
    path = CAD / f"P68-ENG-{DECKS.index((name, slug)) + 1:02d}-{slug}.dxf"
    if not path.exists():
        raise SystemExit(f"missing deck sheet {path.relative_to(ROOT)}; run npm run build:cad once to create it")
    msp = ezdxf.readfile(path).modelspace()

    outline = None
    for e in msp.query("LWPOLYLINE"):
        if e.dxf.layer == "A-FLOR-OTLN":
            outline = unflip(list(e.get_points("xy")))
            break
    if outline is None:
        raise SystemExit(f"{path.name}: no A-FLOR-OTLN outline")

    rooms = []
    for e in msp.query("LWPOLYLINE"):
        if e.dxf.layer == "A-AREA" and e.has_xdata("P68"):
            rooms.append({
                "name": xdata_name(e),
                "rect": rect_of(list(e.get_points("xy"))),
                "inferred": xdata_status(e) == "inferred",
            })
    for e in msp.query("LWPOLYLINE"):
        if e.dxf.layer == "A-ROOF-OTLN" and e.has_xdata("P68"):
            rooms.append({
                "name": xdata_name(e),
                "rect": rect_of(list(e.get_points("xy"))),
                "inferred": False,
                "roof": True,
            })

    masts = []
    labels = [t.dxf.text for t in msp.query("TEXT") if t.dxf.layer == "S-MAST"]
    for c in msp.query("CIRCLE"):
        if c.dxf.layer != "S-MAST":
            continue
        cx = round(c.dxf.center[0], 2)
        # The label is the S-MAST text nearest to the circle
        label = min(
            (t for t in msp.query("TEXT") if t.dxf.layer == "S-MAST"),
            key=lambda t: abs(t.dxf.insert[0] - cx),
            default=None,
        )
        name = label.dxf.text.split(" MAST")[0].strip().title() if label else f"Mast at {cx}"
        masts.append({"name": name, "x": cx})
    return outline, rooms, masts


def main():
    decks = []
    mast_found = {}
    for name, slug in DECKS:
        outline, rooms, masts = read_sheet(name, slug)
        decks.append({"name": name, "outline": outline, "rooms": rooms})
        for m in masts:
            mast_found.setdefault(m["name"], m["x"])
    # Rig data from hull.json, matched by name. A mast with no rig data is an error.
    rig = {m["name"]: m for m in HULL["masts"]}
    masts = []
    for name, x in mast_found.items():
        if name not in rig:
            raise SystemExit(f"mast '{name}' on the sheets has no rig data in layout/hull.json")
        r = rig[name]
        masts.append({"name": name, "x": x, "foundation_m2": r["foundation_m2"], "top_m": r["top_m"]})
    missing = [n for n in rig if n not in mast_found]
    if missing:
        raise SystemExit(f"masts in layout/hull.json not drawn on any sheet: {missing}")
    loa = round(max(max(p[0] for p in d["outline"]) for d in decks), 2)
    beam = round(max(2 * max(abs(p[1]) for p in d["outline"]) for d in decks), 2)
    for key, value in (("loa", loa), ("beam", beam)):
        target = HULL.get(key)
        if target is not None and abs(target - value) > 0.05:
            print(f"warning: sheets give {key} {value} m, layout/hull.json says {target} m. The sheets are the source; update hull.json.")
    masts.sort(key=lambda m: m["x"])
    out = {
        "_note": "Generated by scripts/extract-layout-from-dxf.py from the AutoCAD deck sheets in drawings/cad/. Do not edit by hand: edit the DXF in AutoCAD, then run npm run build:hull.",
        "units": "m",
        "loa": loa,
        "beam": beam,
        "source": "drawings/cad/P68-ENG-NN-*.dxf (AutoCAD deck sheets, source of truth)",
        "masts": masts,
        "decks": decks,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"decks-layout.json written from the sheets: {loa} m by {beam} m, "
          f"{len(decks)} decks, {sum(len(d['rooms']) for d in decks)} rooms, masts "
          + ", ".join(f"{m['name']} {m['x']}" for m in masts))


if __name__ == "__main__":
    sys.exit(main())
