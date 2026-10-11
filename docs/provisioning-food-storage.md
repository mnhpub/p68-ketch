# Provisioning: frozen and dry food storage, with refrigeration

Status: sizing basis for review. The repo has no per-person food rate, so every figure is a placeholder to confirm. Water is produced onboard (docs/water-supply-scaling.md). Food storage holds stock between resupply, sized to the provisioning period.

## Basis (placeholders)

| Input | Value | Status |
|---|---|---|
| Food mass per person per day | 2.5 kg | Placeholder |
| Share held frozen | 50% | Placeholder |
| Share held dry | 50% | Placeholder |
| Provisioning period | 90 days | Matches the endurance target. The food-storage entry in systems.json still says 60 days, under study. |
| Frozen product packed density | 1.8 m³ per tonne | Placeholder |
| Dry product packed density | 1.0 m³ per tonne | Placeholder |
| Space allowance (racking, air, aisle) | ×1.4 | Placeholder |
| Clear height | 2.4 m | Placeholder |

## Sizing results

| Scenario | People | Frozen (t) | Frozen floor (m²) | Dry (t) | Dry floor (m²) |
|---|---|---|---|---|---|
| Owner private | 14 | 1.57 | 1.7 | 1.57 | 0.9 |
| Charter standard | 22 | 2.48 | 2.6 | 2.48 | 1.4 |
| Layout maximum | 34 | 3.83 | 4.0 | 3.83 | 2.2 |

The layout maximum sets the envelope requests. Frozen 6 m² and dry 8 m² include margin above the floor figures, for walk-in equipment and shelving access.

## Commercial frozen store

A commercial walk-in freezer held at a frozen set point, serving the professional galley, on Main / Master.

**Insulation must not be foam.** Walk-in panels are normally polyurethane foam. The materials policy bans foam on the craft, so the panels use a non-foam insulation to be specified (mineral fibre or vacuum panels). Whether mineral fibre counts as synthetic is still an open question in docs/materials-policy.md.

## Refrigeration (frozen store, layout maximum, placeholder basis)

| Item | Value | Basis |
|---|---|---|
| Store surface area | 29.5 m² | 6 m² floor, 2.4 m high |
| Envelope U-value | 0.25 W/m²K | Placeholder, non-foam panel |
| Temperature difference | 53 K | 35 °C ambient to -18 °C store |
| Envelope heat gain | 391 W | U × A × ΔT |
| Coefficient of performance | 2.0 | Placeholder |
| Envelope electrical load (average) | 0.20 kW | Heat gain ÷ COP |

The envelope load is the floor. Product pull-down, door openings, defrost and equipment heat add to it. These need the unit's data. Refrigeration adds to the energy budget (weights/energy-budget.json), and it needs its own supply on the 800 V bus.

## Dry food store

A dry store with ventilated, corrosion-resistant racking, close to the galley and clear of fuel, paint and battery spaces. Storage is secured against vessel motion. No refrigeration.

## Location and envelope

Both stores sit on Main / Master next to the professional galley. Main / Master has room in the envelope budget (layout/envelope-budget.json).

## Open decisions

1. Per-person food rate, and the 50/50 frozen to dry split.
2. Provisioning period: 90 days to match the endurance target, or the 60 days in systems.json.
3. Frozen unit's refrigeration data, for the pull-down and the energy budget.
4. Non-foam insulation for the walk-in panels, and whether mineral fibre is allowed.


## Revision: protein from the sea, fresh produce from port

Owner assumptions, recorded as placeholders:
- **Protein** is fresh from the sea. Protein is removed from the stored mass. It is handled as a daily catch in a fish-handling and chill room, not held in stores. The catch is 25.5 kg per day at 34 people (30% protein share, placeholder). This is an assumption, not a physical supply guarantee: catch rate, licensing and protected-species rules still apply.
- **Fresh fruit and vegetables** come from port. They are held only for the longest passage between ports. The passage length is a placeholder of 14 days, because the repo has no route data.
- **Dry and frozen stores** hold the remaining food for the provisioning period (90 days), split 50/50.

Revised sizing at 34 people:

| Store | Basis | Mass | Floor (placeholder) | Request |
|---|---|---|---|---|
| Chilled produce | 14-day passage | 333 kg | 0.19 m² | 4 m² (practical minimum) |
| Dry food | 90 days, 50% of remaining | 1.61 t | 0.9 m² | 8 m² (unchanged) |
| Frozen food | 90 days, 50% of remaining | 1.61 t | 1.7 m² | 6 m² (unchanged) |

Protein and produce change the mass held, not the room sizes: the dry and frozen requests stay at their practical minimums.


## Specialty provisions: wine, chilled cheese, frozen butter

Status: sizing basis for review. Consumption rates are placeholders; the repo has no figures for them. The storage conditions are stated as design requirements.

| Item | Condition | Placeholder rate | Hold | Mass or bottles | Floor (placeholder) | Request |
|---|---|---|---|---|---|---|
| Wine | Cellar, 12 to 14 °C, 60 to 70% RH, dark, vibration-free | 0.5 bottle per person per day | 90 days | 1530 bottles | 1.15 m² | 4 m² cellar (practical minimum) |
| Chilled cheese | Chill, 2 to 6 °C, separate from produce (odour and humidity) | 0.04 kg per person per day | 14-day passage | 19 kg | 0.01 m² | 2 m² chill zone |
| Frozen butter | Frozen store, -18 °C | 0.02 kg per person per day | 90 days | 61 kg | 0.04 m² | within the 6 m² frozen store |

### Wine cellar
- The cellar is held near 13 °C, with a low-vibration rack. It is kept away from the engine room, the workshop and the battery room, and away from direct sun on the surfaces.
- Insulation must be non-foam (see the materials policy). Envelope heat gain at 27 m² of surface, U 0.4 W/m²K, from 35 °C ambient to 13 °C: about 238 W, or 0.12 kW average electrical at COP 2. It is a placeholder basis.
- Racking in teak or stainless, to the materials policy for interior joinery and rigid appointments.

### Chilled cheese
- A separate chill zone at 2 to 6 °C, not in the produce store, because cheese odour and humidity affect fresh produce.
- Held for the passage between ports, like produce, because cheese is resupplied in port.

### Frozen butter
- Held in the frozen store at -18 °C. The 6 m² frozen request already covers it.

### Revisions to the envelope budget
- Wine cellar, 4 m², Main / Master near the galley and salon.
- Chill zone for cheese, 2 m², on Main / Master with the chilled produce store.
- Frozen butter needs no new area.

### Open decisions
1. Per-person wine and cheese rates, which the owner sets.
2. Whether wine is held for the full 90 days or resupplied in port like produce.
3. The cellar's location on Main / Master, away from the galley's heat and odour.


## Dry stores: rice, grains, flour and baking

Status: sizing basis for review. Rates are placeholders; the repo has no figures for them.

| Item | Placeholder rate | Hold | Mass at 34 people | Notes |
|---|---|---|---|---|
| Rice, pasta and dry grains | 0.15 kg per person per day | 90 days | 459 kg | Long shelf life, held in the dry store |
| Flour and baking staples | 0.05 kg per person per day | 90 days | 153 kg | Shorter shelf life for some items; rotate stock |

Total: 0.61 t. Packed density is 1.5 m³ per tonne (bagged grains and flour, placeholder), with the ×1.4 space allowance and a clear height of 2.4 m. The floor need is 0.54 m², well inside the 8 m² dry store already requested on Main / Master.

### Storage conditions
- Dry, cool (below about 20 °C), and humidity under about 60%, to stop mould and weevils.
- Pest-proof: sealed containers, no wooden shelving that harbours pests, and a regular inspection.
- Off the deck and away from the bilges and the wastewater route. Shelving clear of the hull, so bilge water cannot reach stock.
- Ventilated without a membrane or foam: vents follow the ventilation register. The dry store is an occupied-adjacent space, so its air comes from a clean point.
- Stock rotation by first in, first out, with a dated log.

### Materials
- Shelving in stainless steel, which meets the rigid appointments rule. Containers in stainless or glass. No foam liners or foam seals.

### Envelope
The 8 m² dry store already requested on Main / Master holds this stock. No new area is needed.

### Open decisions
1. The grain and flour rates per person.
2. Whether the 90-day hold is right for flour and baking staples, given their shorter shelf life.
