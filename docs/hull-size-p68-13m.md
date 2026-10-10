# P68 hull size: 68 m LOA, 62 m waterline, 13.0 m beam

Status: chosen size, owner direction. Supersedes `docs/hull-size-final.md` (66 m) and the 64 m and 66 m figures in the dynamics and gyro notes. Those notes keep their method, but their numbers are superseded by the table below.

## Why this size

The vessel is P68, a 68 m ketch, and the length is part of its identity, so the length is held at 68 m. The beam is 13.0 m, chosen by the owner. Weight and displacement follow the hull, not the other way round. The room layout fits the 68 m hull, as it did before.

## Buoyancy

Displacement is Δ = ρ × Cb × LWL × B × T, with ρ = 1.025 t/m³ and Cb = 0.375 (placeholder). With LWL × B = 62 × 13.0 = 806 m²:

| Draft | Displacement |
|---|---|
| Keel-up 4.8 m | **1,487 t** |
| Keel-down 7.2 m | **2,231 t** |

The design displacement target is now **1,487 t**. The keel-up draft fixes it, and the earlier 1,350 t target no longer applies. At 1,487 t the draft is 4.80 m, exactly on the keel-up target.

## Stability, sea and motion

| Quantity | Value |
|---|---|
| Displaced volume | 1,451 m³ |
| Waterplane area (Cwp 0.70) | 564 m² |
| Waterplane second moment | 6,686 m⁴ |
| BM | 4.61 m |
| KB (T/2) | 2.40 m |
| KG limit for GM 1.0 m | **6.01 m** |
| Roll period at GM 1.0 m | **10.4 s** (radius of gyration 0.4 × B = 5.2 m) |
| Heave period | 3.2 s (a lower bound) |
| Hull speed | **19.1 kn** |
| Wave period of a hull-length wave | 6.3 s |

The working range is still GM about 1.0 m. The roll period is clear of the 5 to 8 s sea periods.

## Sail heel (placeholder sail, 600 m², centre of effort 30 m)

| Wind (kn) | Heel at GM 1.0 m |
|---|---|
| 15 | 1.8° |
| 20 | 3.2° |
| 30 | 7.2° |

The sail plan must set the sail area. These heel figures depend on the placeholder.

## Roll control (gyro)

- Roll inertia: 4.02 × 10⁷ kg·m²; roll stiffness: 1.46 × 10⁷ N·m/rad.
- Damping torque for ζ 0.10 at a 5° amplitude: **255 kN·m** peak.
- Angular momentum at 0.2 rad/s precession: **1.27 × 10⁶ kg·m²/s**.

## What is unchanged

- Room positions and the area budget: the rooms fit inside the 68 m hull. The 13.0 m beam adds plan area, so the budget still fits (the regenerated outlines give a gross deck area of 691 m²).
- The genset isolation figures (27 mm at 90% isolation for a 600 rpm genset), since they depend only on the forcing frequency.
- The water scaling and the drinking-water units, since they depend on occupancy, not on the hull.

## What still needs deciding

1. Block coefficient, Cb, from a lines plan. 0.375 is a placeholder.
2. Mass register: the 1,487 t target now needs to be met item by item. It is still 0% covered.
3. Outlines at 68 m and 13.0 m beam: regenerated for every deck in `layout/decks-layout.json` by scaling the beam of the original outline by 13.0/12.1. The layout, access and envelope checks pass. The outline is a scaled model, not a lines plan.
4. Stability study and sea trials against the class rules.
