# Hull dynamics, first pass: waves, stability and sail heel

Status: first-pass calculations on the final size (`docs/archive/68m/hull-size-final.md`). They are built piece by piece, and each block takes the previous block's output. The mass register is not yet populated, so the results use the 1,350 t displacement target and the placeholder proportions below. Each number is labelled as given, derived or placeholder. Nothing here replaces a stability study, a seakeeping analysis or a sail plan.

## Inputs

| Input | Value | Status |
|---|---|---|
| LOA | 66.0 m | Derived (`docs/archive/68m/hull-size-final.md`) |
| LWL | 60.2 m | Derived |
| Beam | 12.1 m | Derived, kept |
| Displacement | 1,350 t | Design target (`docs/archive/68m/hull-size-final.md`) |
| Block coefficient, Cb | 0.375 | Placeholder (range 0.30 to 0.45) |
| Waterplane coefficient, Cwp | 0.70 | Placeholder |
| KB | T / 2 | Placeholder rule of thumb |
| Sail area and centre of effort | 600 m², 30 m above waterline | Placeholder. Not from a sail plan. |
| Sail force coefficient | 0.7 | Placeholder |
| Seawater, air density | 1.025 t/m³, 1.225 kg/m³ | Standard |

## Block 1: Volume, draft and waterplane

- Displaced volume: V = Δ / ρ = 1,350 / 1.025 = **1,317 m³**
- Draft: T = V / (Cb × LWL × B) = 1,317 / (0.375 × 60.2 × 12.1) = **4.82 m**

The draft matches the 4.8 m keel-up target, which is the consistency check that closes the size choice.

- Waterplane area: A_wp = Cwp × LWL × B = 0.70 × 60.2 × 12.1 = **510 m²**
- Waterplane second moment (ellipse): I_wp = π/64 × LWL × B³ = **5,235 m⁴**

## Block 2: Metacentric height and the centre of gravity limit

- Metacentre above centre of buoyancy: BM = I_wp / V = 5,235 / 1,317 = **3.97 m**
- Centre of buoyancy: KB ≈ T / 2 = **2.41 m** (placeholder rule)
- GM = KB + BM − KG

For a minimum GM of 1.0 m, the centre of gravity must sit no higher than **KG = 5.39 m above the keel**. That is the limit the mass register must meet. The tall rig, the tenders and the batteries are the items that push KG up, so they must be placed low, and the rig's centre of mass must be checked against this limit.

KG is not yet calculated. The limit is what the design must achieve.

## Block 3: Hull speed and the wave the hull makes

- Hull speed: Vh ≈ 1.34 × √LWL(ft) = 1.34 × √197.5 = **18.8 kn**
- At hull speed the bow and stern waves are as long as the waterline: λ ≈ LWL = **60.2 m**
- Period of a wave of that length (deep water): T = √(2πλ/g) = **6.2 s**

The hull is most efficient, and most likely to pitch, when it sails at hull speed into seas with a period near 6 s. Wind-driven seas in the open ocean often have periods of 5 to 8 s, so the hull's wave and the sea can match. This is a planning point, to be checked against the wave climate of the intended cruising areas.

## Block 4: Natural periods of heave and roll

- Heave: T_h = 2π √(V / (g × A_wp)) = 2π √(1,317 / (9.81 × 510)) = **3.2 s**. Added mass and damping lengthen this in practice, so the figure is a lower bound.
- Roll: T_roll = 2π k / √(g × GM), with radius of gyration k ≈ 0.4 × B = 4.8 m.

| GM (m) | Roll period (s) | Comment |
|---|---|---|
| 0.5 | 13.7 | Very slow, tender, uncomfortable in seas |
| 1.0 | 9.7 | Slow roll, clear of the 5 to 8 s sea periods |
| 1.5 | 7.9 | Close to the 5 to 8 s sea periods, risk of resonance |

**The working range is GM about 1.0 m.** Lower GM gives a slow, tender roll. Higher GM gives a quick roll that can match the sea. The rig and the centre of gravity decide where in the range the vessel lands, so the GM target is 1.0 m, and the KG limit of 5.39 m follows from it.

## Block 5: Sail heel

Heeling moment M = q × A × Cf × h, with dynamic pressure q = ½ ρ_air V², A = 600 m², Cf = 0.7 and h = 30 m. Righting moment = Δ × g × GM × sin φ. Heel at GM 1.0 m:

| Wind (kn) | q (Pa) | Sail force (kN) | Heeling moment (MN·m) | Heel (°) |
|---|---|---|---|---|
| 15 | 36 | 15.3 | 0.46 | 2.0 |
| 20 | 65 | 27.2 | 0.82 | 3.5 |
| 30 | 146 | 61.3 | 1.84 | 8.0 |

These heel angles depend on the placeholder sail area and effort height. The real figures come from the sail plan. The method is the one to keep: heel rises with the square of the wind speed, and the GM sets how much heel a given force produces. A 600 m² sail area would be modest for a 66 m ketch, so the real heel at 30 kn could be well above 8°. The sail plan must set the area, and then the heel must be checked against a limit (typically a reef point, set by the owner and the stability study).

## What the blocks show

1. The 1,350 t target and the 4.8 m keel-up draft agree at this size. The earlier mismatch is closed.
2. Stability needs KG at or below 5.39 m for GM 1.0 m. The mass register has to meet this limit.
3. The roll period at GM 1.0 m, 9.7 s, avoids the usual sea periods. A higher GM would bring the roll period into the sea range.
4. Hull speed of 18.8 kn sets a wave period of 6.2 s, which is the sea state to plan for at speed.
5. Sail heel is small at the placeholder area, and the real figure depends on the sail plan.

## Still to do, in order

1. **Mass register**, every item with its mass and its height, to compute KG and the real GM.
2. **Sail plan**, for sail area, centre of effort and reefing points, to replace the placeholder heel.
3. **Lines plan**, for Cb, Cwp and the real waterplane, to replace the placeholders.
4. **Stability study**, to confirm GM, the heel limit and the righting arm curve, against the classification society's rules.
5. **Seakeeping**, the heave, pitch and roll response in the actual wave climate of the intended cruising areas.
