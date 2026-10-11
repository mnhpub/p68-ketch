# ADR-0011: Hull scale from one source; lessons from the 68 m hull

Status: Proposed (for owner review). Accepted in part by the owner direction to move to 120 m and 1,487 t; the concept is in docs/concept-120m-four-mast.md.

## Context

The 68 m by 13.0 m design grew its drawings, checks and text by hand. Changing the hull meant editing many files, and the results still didn't agree. The 120 m four-mast concept exposed the gaps. Lessons from the 68 m hull:

1. **Dimensions were copied, not derived.** LOA (68), beam (13.0 or 12.1), mast stations (21.0 and 39.9), the beam dimension (x 70.4) and the "AP X 0 to FP X 68" label were typed into 10 or more scripts and captions.
2. **A second size file drifted.** `layout/proposed-size.json` held a separate 64 m size. The schematic and circulation scripts read it, so they failed or drew the wrong hull once the layout changed.
3. **Room positions were digitised, not dimensioned.** Uniform scaling would enlarge every cabin by about 1.8 times in length and 1.5 in width, so rooms no longer matched the programme.
4. **Displacement, draft and beam were set separately.** The 68 m hull had a 1,350 t target, then 806 t, then 1,487 t, and a 4.8 m keel-up draft that did not follow from the displacement at 13.0 m beam. The draft target has to come from the displacement, beam and Cb, not be set on its own.
5. **The sail rig was not in the envelope.** Mast stations were approximate, sail area was a 600 m² placeholder (about 6 times too small for the displacement), and sail clearance was not checked (see the design gap analysis, H6).
6. **Font and toolchain assumptions were local.** The render scripts loaded DejaVu fonts that only exist on Linux. The pinned `bpy==5.2.2` was not available from the package index; 5.0.1 was the nearest.
7. **Tracked outputs were overwritten.** Switching the hull and rebuilding replaced the 68 m drawings in git, so the working tree showed the wrong hull until restored.

## Decision

1. **One hull source.** `layout/hull.json` holds LOA, beam and the mast stations. Every drawing, elevation, CAD sheet, schematic and check reads from it, or from `layout/decks-layout.json`, which `scripts/build-layout.mjs` generates from it. The `proposed-size.json` size values must not be read by any drawing script.
2. **Rooms keep their size.** The 68 m room positions are the source. Each room moves with its nearest anchor (stern, mizzen, main mast or bow), so extra length goes into the gaps.
3. **Displacement drives draft.** Draft is calculated from displacement, LWL, beam and Cb. A draft target is not set on its own.
4. **Build chain.** `npm run build:hull` regenerates the layout and the plans, elevations and bird's-eye views, and runs the checks. The CAD and drafting scripts (Python, ezdxf) and the renders (Blender, bpy) run as one chain on the same layout.
5. **Regression check first.** The default hull must reproduce the source rooms exactly before any other hull is drawn.
6. **Outputs kept apart.** A formal run of another hull writes its outputs to a separate folder, so the tracked drawings are not overwritten.
7. **Fonts and toolchain.** Font lookup falls back across platforms. The toolchain pins the nearest available version and records the difference.

## Open gates

- Mass register, to reach 1,487 t item by item.
- Keel and hull form, for the draft that follows from the displacement.
- A sail plan, to replace the rig triangles and set the reef points.
- The sail clearance houses (`layout/sail-clearance-*.json`) still use their own geometry, not `hull.json`.
- The deck list is still five decks. The four-mast concept has four.
- Full-quality renders for the formal 120 m run (the run so far used `--fast`).
