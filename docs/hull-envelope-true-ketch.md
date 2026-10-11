# Hull envelope rework: a true ketch at 68 m LOA

Status: rework of the calculations with the lessons learned so far. The length is the recorded 68 m LOA, since no new length has been given. The waterline is 62 m and the beam 12.1 m, all from `slides.json`. Placeholders are marked. The calculation is `scripts/validate-hull-envelope.mjs`, with its inputs in `layout/hull-envelope-inputs.json`. Run it with `npm run validate:hull-envelope`.

## What changed from the earlier calculations

The earlier calculations used one outline on every deck (643.6 m²). That was the first lesson: it makes the upper decks look as large as the main deck, and it inflates the volume. This rework adds a taper sensitivity (0%, 10% and 20% narrower per level above the Tank level) and uses the waterline length, not LOA, for displacement, as a true ketch's displacement is set by the waterline.

The second lesson concerns the draft. The keel draft targets (4.8 to 5.0 m keel-up, 7.2 to 7.8 m keel-down) are not consistent with the reference displacement (786.3 m³, about 806 t). This rework puts a number on that gap.

## Results

### Enclosed volume (all five levels, Tank to Bridge)

| Taper per level above the Tank | Deck areas, Tank to Bridge (m²) | Enclosed volume (m³) |
|---|---|---|
| 0% (uniform outline, current model) | 646 each | 6,979 |
| 10% | 646, 582, 517, 452, 388 | 5,525 |
| 20% | 646, 517, 388, 258, 129 | 4,071 |

Even at 20% taper, the enclosed volume is about five times the 786 m³ reference. Enclosed volume above the waterline is not displacement, so the two are not like-for-like. Taper also isn't the whole fix, since the plan areas are still generous. Both points stand, and the rework does not resolve them.

### Displacement needed for the keel draft targets

Displacement is V = Cb × LWL × B × T. With LWL × B = 750.2 m² and a loaded sailing-yacht block coefficient of 0.30 to 0.45 (placeholder):

| Draft | Cb 0.30 | Cb 0.45 |
|---|---|---|
| Keel-up 4.8 m | 1,080 m³ (1,107 t) | 1,620 m³ (1,661 t) |
| Keel-down 7.2 m | 1,620 m³ (1,661 t) | 2,431 m³ (2,491 t) |

### Draft implied by the reference displacement

786.3 m³ at Cb 0.30 to 0.45 gives a draft of **2.33 to 3.49 m**. The keel-up target of 4.8 m is out of reach at any block coefficient in that range.

**This is the main finding of the rework.** The reference displacement is too small for the keel draft targets. Either the displacement is about twice what the reference says (1,080 to 1,620 m³ at keel-up, against 786 m³), or the draft targets are wrong. The lifting-keel design cannot be settled until one of these is corrected. The displacement and the draft must come from the lines plan and the weight register, not from either number alone.

### Waterplane

Waterplane area is 0.70 × LWL × B = 525 m² (placeholder waterplane coefficient). The earlier outline check used the uniform 643.6 m², which is the full deck, not the waterplane. The waterplane figure is the one that sets the draft, and it is smaller.

## Ketch specifics

A true ketch has two masts, a mainmast forward and a smaller mizzen aft. Four points follow:

- **Mast foundations take deck area and structure.** The rework uses 2.0 m² for the mainmast and 1.5 m² for the mizzen (placeholders), 3.5 m² in total. The stays, their fittings and the load paths through the decks are not included, and they are significant.
- **Mast positions are approximate.** They are read from the sections sheet (`docs/layout-gaps.md`). The foundations cannot be placed on a deck until the mast positions are fixed from the sail plan.
- **Rig weight sits high.** A carbon mainmast and an aft mizzen (`slides.json`) add topside weight. That affects stability and the keel draft, and it belongs in the weight register.
- **Sail loads reach the hull.** The sail loads, reefing geometry and the effect of the sails on the wind model are not yet calculated (the wind model in `src/aggregates/dock.ts` acts on the hull alone).

## What this means for the earlier decisions

- **The plan-area budget** (`docs/envelope-revision.md`) still fits, but it uses the uniform outline. With taper it has more room on the upper decks and less on the lower ones, so the Tank level still matters most.
- **The battery and tender decisions** depend on the Tank-level area, which the taper does not change. The Tank is the widest deck in either model.
- **The keel and draft** are the decisions that most need the rework, and they cannot be settled until the displacement question is answered.

## Open decisions and inputs

1. **Lines plan**, to replace the placeholder block coefficient and waterplane coefficient, and to give the real deck outlines.
2. **The displacement question:** is the reference 786 m³ (806 t) the right displacement, or are the keel draft targets?
3. **Weight register:** every item, with its mass, so the displacement can be checked against the Cb range.
4. **Mast positions and foundations**, from the sail plan.
5. **Taper**, from the sections, to replace the sensitivity range.
6. **Length.** If a new length is wanted, the outlines, the displacement and every area figure move with it, and the rework is run again.
