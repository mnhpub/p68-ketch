# Hull size selection: 64 m LOA, 58.4 m LWL, 12.1 m beam

Status: proposed size, derived from the room layout and the buoyancy relation. It is not yet applied to the outlines in `layout/decks-layout.json`, which remain at 68 m. The derivation is in `layout/proposed-size.json`.

## Step 1: Length from the rooms

Every room in `layout/decks-layout.json` is a rectangle. The 192 rectangle corners must lie inside the hull outline. Using the same ellipse model as the layout (semi-axes L/2 and 6.05 m), the search over length finds the smallest LOA at which all corners fit: **64.0 m**. The binding constraints are the room positions, not the area budget.

The area budget alone would allow a smaller hull, but the rooms cannot be moved into a shorter outline without redrawing the layout. The room positions set the length.

## Step 2: Beam

The widest room has a half-beam of about 5.0 m (the Bridge roof access passage, y −5). The rooms alone would allow a beam of about 10 m. The beam is kept at **12.1 m**, because stability, ballast and the lift and mag-rail routes depend on it, and none of those is derived in this repo yet. Changing the beam is a separate decision.

## Step 3: Waterline

The recorded waterline-to-LOA ratio is 62/68 = 0.912. Applied to 64 m, LWL = **58.4 m**.

## Step 4: Buoyancy check

Displacement is Δ = ρ × Cb × LWL × B × T, with ρ = 1.025 t/m³ and Cb = 0.375 (midpoint of the placeholder range 0.30 to 0.45). With LWL × B = 706.6 m²:

| Draft | Displacement |
|---|---|
| Keel-up 4.8 m | **1,304 t** |
| Keel-down 7.2 m | **1,956 t** |

At the reference 806 t, the draft is 2.97 m.

**This is the consequence the size choice cannot remove.** The keel-up target needs about 1,300 t at this hull. The reference is 806 t. Either the weight register must reach about 1,300 t, or the draft targets change. This is a mass or a target decision, not a size decision.

## Step 5: Area budget at 64 m

The gross deck area becomes π/4 × 64 × 12.1 = 608.2 m² per deck. Every request still fits (`layout/envelope-budget.json`):

| Deck | Net free (m²) | Requested (m²) | Left (m²) |
|---|---|---|---|
| Bridge | 290.8 | 0 | 290.8 |
| Commander / Lido | 230.4 | 15 | 215.4 |
| Main / Master | 192.7 | 0 | 192.7 |
| Tween | 208.5 | 88 | 120.5 |
| Tank / Technical | 248.2 | 96 | 152.2 |

## What this does not settle

- **Outlines.** The 64 m outlines must be generated and checked by `validate:layout` and `validate:access`. The 68 m outlines in the repo are not changed by this note.
- **Margin.** 64.0 m is the exact minimum, with no margin. The ellipse is idealised, so a real hull needs margin at the bow and stern, which would add length.
- **Draft targets.** The displacement at 64 m is 1,304 t against 806 t. That is the decision to make next.
- **Beam.** Set by stability and ballast, not by the rooms.
