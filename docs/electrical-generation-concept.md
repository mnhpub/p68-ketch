# Electrical generation concept: low-speed diesel and brushless generators

Status: concept. The engine, generator, power electronics and mass are not chosen. Every efficiency figure here is a placeholder until a manufacturer's part-load curve exists. The numbers below are for review and do not describe a product.

## The concept

The generation plant is built around three goals:

1. **High efficiency.** Diesel engines running at low speed and high torque, with a large swept volume, so the fuel burnt per kWh is low.
2. **Endurance and low maintenance.** Engines and generators that run for long hours at low stress, with long service intervals.
3. **Quiet and smooth.** Low RPM reduces noise, vibration and wear. A brushless generator has no brushes or slip rings, so it has fewer wear parts.

The generator is a brushless permanent-magnet (PM) machine, direct-driven by the engine, with power electronics between the generator and the 600 V distribution bus. This fits the systems register, where the propulsion architecture (AC or DC) and the bus voltage are still open (`systems.json`, `propulsion-600v`).

## Why the energy source matters more than the efficiency

| Source at 20 kW for 60 days | Mass | Notes |
|---|---|---|
| Battery only (0.12 kWh/kg LFP, 80% DoD) | 300 t | 37% of the 806 t reference displacement |
| Diesel, conventional genset at part load (30%) | 8.1 t fuel | Fuel tank about 9.5 m³ |
| Diesel, current assumption (35%) | 6.9 t fuel | Fuel tank about 8.1 m³ |
| Diesel, low-speed engine and PM generator (42%) | 5.8 t fuel | Fuel tank about 6.8 m³ |
| Diesel, best case at rated load (46%) | 5.3 t fuel | Only at a load the engine is designed for |

The efficiency gain from the concept is real but modest. Moving from 35% to 42% saves about 1.1 t of fuel over 60 days at 20 kW. Moving from battery to diesel saves about 173 t. For the 60-day target, the choice of energy source dominates, and the engine concept is a secondary lever.

## Four checks before any efficiency claim

1. **Part load.** Large engines reach their best efficiency near rated load. At a low average load they run far below it. The 20 kW figure depends on the part-load curve of the engine chosen, not on its rated efficiency. The 42% and 46% figures assume the engine runs at an efficient point, which may not hold at a 20 kW average. A real engine can be chosen to match the load, or the load can be concentrated into fewer hours at a higher output with a battery buffer.
2. **Generator mass.** A low-speed, direct-driven PM generator needs a large diameter to make torque without a gearbox. That mass is not yet in the weight register. It is probably significant and goes against the aim of a light hull.
3. **Fuel tank volume.** The fuel volume figures assume 0.85 t/m³ diesel and do not include tank separation, expansion space or fire protection. The Tank / Technical level must accommodate them, alongside the tenders (`docs/tender-mag-rail-reload.md`).
4. **Redundancy.** A single long-running engine is a single point of failure for the whole electrical plant. The backup-power system (`systems.json`, `backup-power`) must cover loss of the main generation, and the emergency stop must cut the fuel supply safely.

## Quiet and maintenance claims

These are design targets, not results. Each needs a supplier figure before it goes into a specification:

- Noise at the bridge, the accommodation decks and the tender stowage, measured in dB(A) at stated loads.
- Vibration, mounted with isolation, checked at the accommodation decks.
- Service interval, in running hours, for the engine and for the generator and power electronics.
- Exhaust routing, which affects the outdoor pilot house, the Lido and the sun deck.

## What this changes in the register

- `weights/weight-register.json`: the diesel item now refers to this concept. Its mass is unknown, and the generator mass is a separate open item.
- `weights/energy-budget.json`: the generation efficiency scenarios are the placeholders in the table above, so the validator can show fuel at each one.
- `systems.json`: `diesel-generation` (Kohler candidate) should be revised once the engine and generator are chosen. This note does not change it.
