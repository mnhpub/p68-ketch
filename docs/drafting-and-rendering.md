# Drafting and rendering toolchain

Status: concept. Everything produced here is schematic or illustrative and is **not for construction or fabrication**.
See `DESIGN_RELEASE_POLICY.md`.

## Pipeline

```
layout/decks-layout.json ─┐
layout/accessibility.json ├─▶ scripts/drafting/cad_plans.py ─▶ drawings/cad/P68-ENG-0N-<deck>.dxf   (source)
layout/finishes.json      │                                   ├▶ drawings/eng-deck-NN-<deck>.svg       (plot, app)
layout/deck-status.json  ─┘                                   └▶ drawings/P68-engineering-deck-plans.pdf (plot, print)

drawings/cad/*.dxf ─▶ scripts/drafting/render_finish.py    ─▶ drawings/renders/finish/   (finish-out plans, cutaways)
                   ─▶ scripts/drafting/render_interiors.py ─▶ drawings/renders/interior/ (controls, features, accommodation)
bvessel.py model   ─▶ scripts/drafting/render_exteriors.py ─▶ drawings/renders/exterior/ (port, anchor, underway, dusk)
```

The DXF files are the drawing sources. The plots and the Blender renders read the DXF, not the JSON, so a DXF
edited in AutoCAD can be re-plotted and re-rendered. Rerunning `cad_plans.py` regenerates the DXF from the layout
JSON and overwrites manual edits, so make lasting layout changes in `layout/decks-layout.json`.

## Commands

```sh
pip install -r scripts/drafting/requirements.txt   # ezdxf, pymupdf, numpy, pillow, bpy (Blender 5.2)
npm run build:cad       # DXF sources, SVG and PDF plots, copied to public/
npm run build:renders   # Blender renders (CPU, about an hour at full quality), copied to public/
```

Each render script takes `--fast` for a quick low-sample preview, and a subset: deck indices for
`render_finish.py` (`1 3 plan`), scene names for `render_exteriors.py` (`port anchor underway dusk`) and shot keys
for `render_interiors.py` (see `SHOTS` in the script). Blender rendering needs OSMesa or EGL in headless containers
(`apt-get install libosmesa6 libegl1`).

## DXF conventions (AutoCAD 2018)

| Item | Convention |
|---|---|
| Units | Model space in metres (`$INSUNITS` 6). Paper space in millimetres. |
| Axes | X from the aft perpendicular (AP, X 0) to the bow (X 68). Y positive to port. Z above the DWL. |
| Layers | AIA/NCS style: `A-AREA` room polylines, `A-AREA-PATT` status fills, `A-AREA-IDEN` tags, `A-WALL`, `A-WALL-PRTN`, `A-DOOR`, `A-CONV` lifts, `A-ROOF-OTLN`, `A-FLOR-OTLN` deck outline, `S-GRID` stations and buttocks, `S-MAST`, `A-ANNO-DIMS`, `G-ANNO-*` sheet items, `G-VIEW` viewport (no plot). |
| Room data | XDATA `P68` on each `A-AREA` polyline: name, status, finish, furniture, number, finish label. |
| Blocks | `P68-TAG` (room tag, attribute `NUM`), `P68-TITLE` (title block, attributes for number, revision, scale, date, source, datum, status, sheet, title). |
| Dimensions | `DIMENSION` entities in style `P68-200` (sized for 1:200, architectural ticks). |
| Layout | `A3 1-200`: frame, viewport at 1:200, room schedule, deck status, general notes, revisions, references, key plan, legend, title block. |

DWG: the files are DXF, which AutoCAD opens natively. Save as DWG from AutoCAD, or convert with the ODA File
Converter, if a DWG deliverable is needed.

## Status colours

| Colour | Meaning | Source |
|---|---|---|
| Green | Room read from the GA sheet | Not marked `inferred` in the layout |
| Blue | Resolved decision | Note says resolved or restored (see `layout/accessibility.json` decisions) |
| Amber | Inferred from the schematic, to check | Marked `inferred` in the layout |

Open items per level live in `layout/deck-status.json` and print on each sheet's status panel.

## What the renders are and are not

- **Finish-out plans and cutaways** show the proposed finish schedule (`layout/finishes.json`) and indicative
  furniture placed by rule (`bfurnish.py`). Cabin partitions are indicative; the cabin count is not set.
- **Exteriors** use the repository's main dimensions, deck heights, mast stations and Lido roof heights. Hull lines,
  superstructure plan shapes, rig heights (main about 55 m, mizzen about 42 m above the waterline), the sail plan and
  the tender are illustrative.
- **Interiors** are built from the DXF rooms. Outboard walls are glazed on the upper levels and have portholes on Tween.
  They are not a coordinated interior design.

## Hull scale: one source for every drawing

- `layout/hull.json` holds the hull: LOA, beam and mast stations (as fractions of LOA, with height and foundation). It is the only place these values are set.
- `npm run build:hull` builds `layout/decks-layout.json` from `layout/source/decks-layout-68m.json` and the hull file. Outlines come from the hull's ellipse. Each room keeps its size and moves with its nearest anchor (stern, mizzen, main, bow), so extra length goes into the gaps.
- The same command then rebuilds the deck plans, elevations and bird's-eye views, and runs the layout, envelope and access checks. The CAD sheets (`npm run build:cad`) and renders (`npm run build:renders`) read the same layout, but run separately.
- To draw another hull, copy its file over `layout/hull.json` (for example `layout/hull-120m-4mast.json`) and run `npm run build:hull`. Restore the 68 m file to return to the current drawings.
- Not yet driven by the hull: the sail clearance houses (`layout/sail-clearance-*.json`), the underway-preview heel inputs, and the deck list, which is still five decks.
