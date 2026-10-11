"""Check that the AutoCAD deck sheets (drawings/cad/*.dxf) agree with layout/decks-layout.json.

The DXF is meant to be the source of truth for the deck plans. This check reports any difference in
the deck outline, room rectangles, room names and mast stations. It does not change any file.
Tolerance: 0.01 m. DXF y is stored as -y (port positive in the layout, negative in the plot).
Run with: npm run check:dxf
"""
import json
import sys
from pathlib import Path

import ezdxf

ROOT = Path(__file__).resolve().parent.parent
LAYOUT = json.loads((ROOT / "layout" / "decks-layout.json").read_text())
TOL = 0.01
SHEETS = {d["name"]: f"P68-ENG-{i:02d}-{s}.dxf" for i, (d, s) in enumerate(zip(LAYOUT["decks"], [
    "bridge", "commander-lido", "main-master", "tween", "tank-technical"]), start=1)}


def close(a, b):
    return abs(a - b) <= TOL


def rect_of(points):
    xs = [p[0] for p in points]
    ys = [-p[1] for p in points]  # undo the plot's y flip
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]


problems = []
for deck in LAYOUT["decks"]:
    path = ROOT / "drawings" / "cad" / SHEETS[deck["name"]]
    if not path.exists():
        problems.append(f"{deck['name']}: missing {path.name}")
        continue
    msp = ezdxf.readfile(path).modelspace()
    # Room polylines on A-AREA, keyed by their name in XDATA
    dxf_rooms = {}
    for e in msp.query("LWPOLYLINE"):
        if e.dxf.layer != "A-AREA" or not e.has_xdata("P68"):
            continue
        name = e.get_xdata("P68")[0].value
        dxf_rooms.setdefault(name, []).append(rect_of(list(e.get_points("xy"))))
    layout_rooms = {}
    for r in deck["rooms"]:
        if r["name"].startswith("Roof:"):
            continue
        layout_rooms.setdefault(r["name"], []).append([round(v, 2) for v in r["rect"]])
    for name in sorted(set(layout_rooms) | set(dxf_rooms)):
        a = sorted(layout_rooms.get(name, []))
        b = sorted(dxf_rooms.get(name, []))
        if len(a) != len(b):
            problems.append(f"{deck['name']}: '{name}' layout has {len(a)}, DXF has {len(b)}")
            continue
        for ra, rb in zip(a, b):
            if not all(close(x, y) for x, y in zip(ra, rb)):
                problems.append(f"{deck['name']}: '{name}' layout {ra} vs DXF {rb}")
    # Deck outline on A-FLOR-OTLN
    outline = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "A-FLOR-OTLN"]
    if outline:
        ob = rect_of(list(outline[0].get_points("xy")))
        lb = [0, -LAYOUT["beam"] / 2, LAYOUT["loa"], LAYOUT["beam"] / 2]
        if not all(close(x, y) for x, y in zip(ob, lb)):
            problems.append(f"{deck['name']}: outline extent DXF {ob} vs layout bounds {lb}")
    else:
        problems.append(f"{deck['name']}: no A-FLOR-OTLN outline in the DXF")

# Mast stations on S-MAST circles (centre x) against layout masts, on the Main deck sheet
main_sheet = ezdxf.readfile(ROOT / "drawings" / "cad" / SHEETS["Main / Master"]).modelspace()
# The plot draws only the masts that pass through a level, so every drawn mast must match a layout mast.
circles = sorted(round(e.dxf.center[0], 2) for e in main_sheet.query("CIRCLE") if e.dxf.layer == "S-MAST")
masts = [round(m["x"], 2) for m in LAYOUT["masts"]]
for c in circles:
    if not any(close(c, m) for m in masts):
        problems.append(f"mast at x {c} on the Main sheet matches no layout mast {masts}")

print(f"checked {len(LAYOUT['decks'])} deck sheets against layout/decks-layout.json")
if problems:
    print(f"{len(problems)} difference(s):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("DXF and layout agree within 0.01 m")
