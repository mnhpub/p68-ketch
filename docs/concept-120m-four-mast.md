# Concept: 120 m four-mast ketch, 20 m beam, 1,487 t

Status: concept, placeholder rig and houses. The 4.8 m keel-up draft target no longer applies.

## Decisions

| Item | Value | Basis |
|---|---|---|
| LOA | 120 m | Length for the four-mast rig and the programme |
| LWL | 109.4 m | LWL/LOA 0.912, as before |
| Beam | 20 m | Fits the programme and the side decks, and the sail clearances |
| Displacement | 1,487 t | Owner direction. Matches the mass target in the project's documents |
| Draft | 1.8 m | Follows from displacement, beam and Cb 0.375 (placeholder). **Supersedes the 4.8 m keel-up target** |
| GM | 2.13 m | Gives an 11 s roll (k = 0.4 B). Relaxed, comfortable roll, clear of the 5 to 8 s sea band |
| KG | Not yet calculated | Limit is well above the rig. Mass register still to populate |
| Sail area | About 4,000 m² | Triangle estimate from the rig, scaled. About 31 sail area to displacement^(2/3): a performance range |
| Masts | Jigger 0.14 L, mizzen 0.31 L, main 0.59 L, fore 0.80 L | Placeholder stations |
| Accommodation | Tween (guest, crew, medical, pet suites) | Owner direction |
| Tank / Technical | Mechanical engineering only | Owner direction. Pet wash and medical tender store moved to Tween |

## Performance and comfort

- Roll period at GM 2.13 m: 11.0 s.
- Heel (placeholder rig, scaled to 4,000 m²):

| True wind | Heel |
|---|---|
| 10 kn | 1.7° |
| 15 kn | 3.8° |
| 20 kn | 6.8° |
| 25 kn | 10.6° |
| 30 kn | 15.4° |

- Reef at about 20 to 25 kn to hold heel near 10°. 15° falls at about 30 kn and 20° at about 34 kn.
- Helm: 1° of rudder per full helm rotation (`src/aggregates/pilot.ts`), unchanged.

## Sail clearance

Checked by `npm run validate:sails` against `layout/sail-clearance-120m-4mast.json`:

- Main, fore, mizzen, jigger and jib sweeps are clear of every house and of the bridge.
- Mast foundations are clear of the main-deck houses.
- The bridge sits aft, over the main house between the mizzen and main masts.
- A bridge forward of the fore mast conflicts with the jib sweep unless the jib foot is about 12 m or less. With that shorter jib the programme is 39 m² short.

## Programme

- Enclosed house and bridge envelope: 718 m² against 717 m² required.
- Clear side deck beside the main-deck houses: 2.30 m minimum.
- Tween holds accommodation and the medical bay, with the pet wash and medical tender store added to it.
- Tank holds fuel, water, ballast, batteries, mechanical workshop, tender storage and paint store.

## Open

1. Mass register, to reach 1,487 t item by item. The 1,487 t target is not yet covered.
2. Keel and hull form, for the 1.8 m draft. Cb 0.375 and Cwp are placeholders.
3. Real sail plan, to replace the triangle estimate and set the reef points.
4. Stability study: GZ curve, heel limit and the righting arm.
5. Roll control: a first-pass roll-damping review (bilge keels or a roll tank) is still to be done against the 11 s target.
6. Tapered per-deck outlines are not yet drawn in the AutoCAD sheets; the layout uses the hull ellipse on every deck.
