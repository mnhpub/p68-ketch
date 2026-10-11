"""Underway preview: midship section at 0, 3.2 and 7.2 degrees of heel, from the hull model.
Schematic, not a rendering. Heel comes from the stability block in layout/sail-clearance-120m-4mast.json (placeholder rig, see docs/concept-120m-four-mast.md).
Requires: pip install matplotlib (virtual environment, not a project dependency).
Output: drawings/previews/underway-heel-section.png and .pdf
Run with: python3 scripts/build-underway-preview.py
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
_HULL = json.loads((ROOT / "layout" / "decks-layout.json").read_text())
OUT = ROOT / "drawings" / "previews"
OUT.mkdir(parents=True, exist_ok=True)
SAIL = json.loads((ROOT / "layout/sail-clearance-120m-4mast.json").read_text())
notice = json.loads((ROOT / "layout/release-notice.json").read_text())
B = float(_HULL["beam"])
ST = SAIL["stability"]
KEEL_UP = float(ST["draft_m"])
KEEL_DOWN = KEEL_UP * 1.5  # keel-down as 1.5 times keel-up (placeholder ratio)
WL_Z = 0.0


def heel_deg(kn):
    """Heel from the stability block: heeling moment over righting moment, small angle GZ = GM sin(heel)."""
    g = 9.81
    q = 0.5 * ST["air_density_kg_m3"] * (kn * 0.5144) ** 2
    moment = sum(q * s["A"] * ST["cf"] * s["ce"] for s in SAIL_ROWS())
    righting = ST["displacement_t"] * 1000 * g * ST["gm_m"]
    return math.degrees(math.asin(min(1.0, moment / righting)))


def SAIL_ROWS():
    rows = []
    for sail in SAIL["sails"]:
        if not sail.get("top_m"):
            continue
        zb = SAIL["heights_m"][sail["height_key"]]
        rows.append({"A": 0.5 * sail["radius_m"] * (sail["top_m"] - zb) * ST.get("sail_area_scale", 1),
                     "ce": zb + (sail["top_m"] - zb) / 3})
    return rows


HEELS = [(0.0, "upright, 0 kn"), (heel_deg(20), f"20 kn wind, {heel_deg(20):.1f} deg heel"), (heel_deg(30), f"30 kn wind, {heel_deg(30):.1f} deg heel")]


def rot(x, y, deg):
    t = math.radians(deg)
    return x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)


def hull_section():
    # Schematic hull section: rectangular deck edges with a keel fin below the waterline.
    half = B / 2
    top = 9.3
    bottom = -KEEL_DOWN
    pts = [(-half, top), (-half, 0.0), (-half * 0.85, -KEEL_UP), (-1.5, bottom), (1.5, bottom), (half * 0.85, -KEEL_UP), (half, 0.0), (half, top)]
    return pts


def main():
    fig, axes = plt.subplots(1, 3, figsize=(15, 7))
    pts = hull_section()
    for ax, (heel, label) in zip(axes, HEELS):
        ax.set_aspect("equal")
        ax.set_xlim(-12, 12)
        ax.set_ylim(-9, 14)
        ax.axhline(WL_Z, color="#1f6f8b", lw=1.4, ls="--")
        ax.text(-11.5, WL_Z + 0.3, "waterline", fontsize=7, color="#1f6f8b")
        ax.axhline(-KEEL_UP, color="#8e3b6a", lw=0.8, ls=":")
        ax.text(-11.5, -KEEL_UP - 0.5, f"keel-up {KEEL_UP:.1f} m", fontsize=7, color="#8e3b6a")
        hull = [rot(x, y, heel) for x, y in pts]
        xs, ys = zip(*(hull + [hull[0]]))
        ax.fill(xs, ys, color="#dbe9ee", ec="#102027", lw=1.1)
        ax.plot([rot(-6.5, 9.3, heel)[0], rot(6.5, 9.3, heel)[0]], [rot(-6.5, 9.3, heel)[1], rot(6.5, 9.3, heel)[1]], color="#2f4d5e", lw=0.8)
        ax.set_title(label, fontsize=10, color="#102027")
        ax.axis("off")
    fig.suptitle("P68 underway: midship section at heel (schematic, not a rendering)", fontsize=13, color="#102027", y=0.97)
    fig.text(0.02, 0.04, f"Section at {_HULL['loa']:g} m LOA, {_HULL['beam']:.1f} m beam. Heel from the placeholder rig (about 4,000 m² of sail) at GM 2.13 m and 1,487 t. The waterline is shown level; the hull heels about it.", fontsize=8, color="#5d7887")
    fig.text(0.02, 0.015, f"CONCEPT - NOT FOR CONSTRUCTION. Open design release, {notice['release_class']}. Licence to be confirmed.", fontsize=7, color="#8e3b6a")
    fig.savefig(OUT / "underway-heel-section.png", dpi=160)
    fig.savefig(OUT / "underway-heel-section.pdf")
    plt.close(fig)
    print("wrote underway-heel-section.png and .pdf to drawings/previews/")


if __name__ == "__main__":
    main()
