"""Schematic diagrams of new features, drawn from the repo data. Not photorealistic renders.

Requires: pip install matplotlib (a virtual environment, not a project dependency).
Output: drawings/features/ (PNG and PDF). Every diagram is CONCEPT, NOT FOR CONSTRUCTION.
Run with: python3 scripts/build-feature-diagrams.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "drawings" / "features"
OUT.mkdir(parents=True, exist_ok=True)
NOTICE = json.loads((ROOT / "layout/release-notice.json").read_text())
STATUS = "CONCEPT - NOT FOR CONSTRUCTION"
FOOT = f"{STATUS}. Open design release, {NOTICE['release_class']}. Licence to be confirmed."
INK = "#102027"
ACC = "#1f6f8b"
WARN = "#a33"


def box(ax, x, y, w, h, text, fc="#f4f7f8", ec=ACC, fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, wrap=True)


def arrow(ax, x0, y0, x1, y1, color=ACC):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color=color, lw=1.2))


def finish(fig, name, title, subtitle):
    fig.text(0.02, 0.96, title, fontsize=14, color=INK, weight="bold")
    fig.text(0.02, 0.925, subtitle, fontsize=9, color="#5d7887")
    fig.text(0.02, 0.02, FOOT, fontsize=7, color="#8e3b6a")
    fig.savefig(OUT / f"{name}.png", dpi=160)
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)


def energy_bus():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7.5); ax.axis("off")
    box(ax, 0.3, 5.2, 2.6, 1.2, "Low-speed diesel gensets\n(PM generators)")
    box(ax, 0.3, 3.4, 2.6, 1.2, "Toyota EV powerplant\n(energy production only)")
    box(ax, 0.3, 1.6, 2.6, 1.2, "Solar (roof candidates)")
    box(ax, 3.7, 3.4, 2.4, 1.2, "Converters to 800 V\n(355 V step-up 2.25)", fc="#e8f1f4")
    box(ax, 6.9, 2.9, 2.6, 2.2, "800 V DC BUS\nnominal 800 V\nwindow 720 to 880 V\nheadroom H 1.25", fc="#dbe9ee", ec=INK, fs=9)
    box(ax, 10.3, 5.2, 2.4, 1.2, "Propulsion motors\n(twin, one per shaft)")
    box(ax, 10.3, 3.4, 2.4, 1.2, "LFP buffer 400 kWh\n(rackmount, ~10 racks)")
    box(ax, 10.3, 1.6, 2.4, 1.2, "Hotel and ship loads\n(refrigeration, HVAC,\nmedical, galley)")
    box(ax, 3.7, 0.9, 2.4, 0.9, "Energy management system\n(supervisory, separate)", fc="#f7f1e9", ec="#b7791f")
    for y in (5.8, 4.0, 2.2):
        arrow(ax, 2.9, y, 3.7, 3.9 if y != 2.2 else 3.6)
    arrow(ax, 6.1, 4.0, 6.9, 4.0)
    arrow(ax, 9.5, 4.2, 10.3, 5.8)
    arrow(ax, 9.5, 4.0, 10.3, 4.0)
    arrow(ax, 9.5, 3.7, 10.3, 2.2)
    ax.text(0.3, 0.25, "Propulsion is electric motor propulsion on the bus. Generation sources feed the bus; the buffer covers peaks and quiet running.", fontsize=8, color="#5d7887")
    finish(fig, "01-energy-and-800v-bus", "Energy production and the 800 V bus",
           "Sources, converters, bus, buffer, propulsion and loads (docs/bus-800v-design.md, docs/hybrid-energy-production.md)")


def battery_room():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
    specs = [
        ("Option A: four racks, packed", 4, 0.0, WARN, "12 kWh modules, 750 W per rack, 224 m³/h per rack"),
        ("Option B: eight racks, spread (recommended)", 8, 0.8, ACC, "6 kWh modules, 375 W per rack, 112 m³/h per rack"),
    ]
    for ax, (title, n, gap, color, note) in zip(axes, specs):
        ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Rectangle((0.2, 0.2), 9.6, 7.6, fill=False, ec=INK, lw=1.4, ls="--"))
        ax.text(0.4, 7.45, "Sealed battery room (IP67), closed-loop cooling", fontsize=8, color=INK)
        slots = n if n == 4 else 8
        cols = 4 if n == 4 else 4
        rw = 0.6
        for i in range(slots):
            c, r = i % cols, i // cols
            x = 0.8 + c * (rw + (gap if n == 8 else 0.4) + 1.4) if n == 8 else 0.8 + c * 2.2
            y = 4.2 - r * 3.3 if n == 8 else 3.5
            if n == 8:
                x = 0.8 + c * 2.2
                y = 3.9 - r * 3.0
            ax.add_patch(Rectangle((x, y), rw * 2 + 0.2, 2.6 if n == 8 else 2.9, fc="#e8f1f4", ec=color, lw=1.0))
            ax.text(x + 0.5, y + 1.3, f"rack {i + 1}", fontsize=6, color=INK, rotation=90, va="center")
        ax.text(5, 0.35, note, ha="center", fontsize=8, color=INK)
        ax.set_title(title, fontsize=11, color=color, loc="left")
    fig.text(0.5, 0.06, "Recommendation for review: option B (air gaps between racks; halves heat and airflow per rack). Module size to be confirmed against products.", ha="center", fontsize=8, color=INK)
    finish(fig, "02-battery-room-rack-layouts", "Battery room: rack layout options",
           "Schematic plan, not to scale (docs/energy-management-architecture.md, weights/energy-budget.json)")


def provisioning():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis("off")
    ax.add_patch(Rectangle((0.3, 0.6), 12.4, 5.8, fill=False, ec=INK, lw=1.4))
    ax.text(0.5, 6.2, "Main / Master: provisioning block beside the professional galley (schematic)", fontsize=9, color=INK)
    box(ax, 0.6, 3.6, 3.2, 2.0, "Professional galley", fc="#e8f1f4")
    box(ax, 4.4, 4.5, 2.4, 1.2, "Commercial frozen store\n6 m², -18 °C\nnon-foam panels", fc="#e6f0f5", ec=ACC, fs=7)
    box(ax, 4.4, 2.9, 2.4, 1.2, "Dry food store\n8 m², cool, pest-proof", fc="#f3efe6", ec="#b7791f", fs=7)
    box(ax, 7.2, 4.5, 2.4, 1.2, "Chilled produce\n4 m², from port", fc="#e9f3ea", ec="#3a7d44", fs=7)
    box(ax, 7.2, 2.9, 2.4, 1.2, "Cheese chill zone\n2 m², 2 to 6 °C", fc="#e9f3ea", ec="#3a7d44", fs=7)
    box(ax, 10.0, 4.5, 2.4, 1.2, "Wine cellar\n4 m², 12 to 14 °C\nlow vibration", fc="#f3e9ee", ec="#8e3b6a", fs=7)
    box(ax, 10.0, 2.9, 2.4, 1.2, "Frozen butter\n(in frozen store)", fc="#e6f0f5", ec=ACC, fs=7)
    ax.text(0.6, 1.1, "Protein is fresh from the sea and handled as a daily catch in a separate chill room (not yet placed).", fontsize=8, color="#5d7887")
    ax.text(0.6, 0.8, "Dry grains and flour: 0.5 m² of floor at placeholder rates, held in the dry store.", fontsize=8, color="#5d7887")
    finish(fig, "03-provisioning-main-master", "Provisioning stores beside the galley",
           "Schematic block, not to scale; areas are placeholders (docs/provisioning-food-storage.md)")


def main():
    energy_bus()
    battery_room()
    provisioning()
    print("wrote 3 feature diagrams (PNG and PDF) to drawings/features/")


if __name__ == "__main__":
    main()
