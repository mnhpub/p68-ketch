"""Underway preview: midship section at 0, 3.2 and 7.2 degrees of heel, from the hull model.
Schematic, not a rendering. Heel angles are the placeholder sail results in docs/hull-size-p68-13m.md.
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
OUT = ROOT / "drawings" / "previews"
OUT.mkdir(parents=True, exist_ok=True)
size = json.loads((ROOT / "layout/proposed-size.json").read_text())
notice = json.loads((ROOT / "layout/release-notice.json").read_text())
B = size["beam_m"]
KEEL_UP, KEEL_DOWN = 4.8, 7.2
WL_Z = 0.0
HEELS = [(0.0, "upright, 0 kn"), (3.2, "20 kn wind, 3.2 deg heel"), (7.2, "30 kn wind, 7.2 deg heel")]


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
        ax.text(-11.5, -KEEL_UP - 0.5, "keel-up 4.8 m", fontsize=7, color="#8e3b6a")
        hull = [rot(x, y, heel) for x, y in pts]
        xs, ys = zip(*(hull + [hull[0]]))
        ax.fill(xs, ys, color="#dbe9ee", ec="#102027", lw=1.1)
        ax.plot([rot(-6.5, 9.3, heel)[0], rot(6.5, 9.3, heel)[0]], [rot(-6.5, 9.3, heel)[1], rot(6.5, 9.3, heel)[1]], color="#2f4d5e", lw=0.8)
        ax.set_title(label, fontsize=10, color="#102027")
        ax.axis("off")
    fig.suptitle("P68 underway: midship section at heel (schematic, not a rendering)", fontsize=13, color="#102027", y=0.97)
    fig.text(0.02, 0.04, f"Section at 68 m LOA, 13.0 m beam. Heel from the placeholder sail (600 m², Cf 0.7, h 30 m) at GM 1.0 m. The waterline is shown level; the hull heels about it.", fontsize=8, color="#5d7887")
    fig.text(0.02, 0.015, f"CONCEPT - NOT FOR CONSTRUCTION. Open design release, {notice['release_class']}. Licence to be confirmed.", fontsize=7, color="#8e3b6a")
    fig.savefig(OUT / "underway-heel-section.png", dpi=160)
    fig.savefig(OUT / "underway-heel-section.pdf")
    plt.close(fig)
    print("wrote underway-heel-section.png and .pdf to drawings/previews/")


if __name__ == "__main__":
    main()
