# Ventilation strategy for the whole craft

Status: design principles and a register of sources. Outlet locations are not set, because the general arrangement is not dimensioned. The register is `layout/ventilation-register.json`, and its checks are run by `npm run validate:ventilation`.

## Why venting needs a whole-craft view

The paint store, the battery room, the fuel tanks, the gensets and the tender stowage each need a vent on their own. Every one of them goes to the outside, and every one of them can put something harmful into air that people breathe, if the routes are not planned together. Separate design notes for each space would miss the clashes, so the strategy sets the rules once and applies them to every source.

## Hazard classes

| Class | Meaning | Examples |
|---|---|---|
| H | Flammable or toxic gas and vapour | Battery off-gas, paint solvent, fuel vapour, outboard fumes |
| C | Combustion exhaust | Diesel gensets, engine room air |
| O | Odour and contamination | Pet areas, galley, laundry, bilges, waste, workshop fumes |
| A | Occupied-space air | Cabins, lounges, bridge, medical bay |

## The rules

1. **One source, one outlet.** No duct, fan or outlet is shared between sources of different hazard class, or between different separation groups. This is enforced by `validate:ventilation`.
2. **Hazardous and combustion exhaust go to a safe outside point,** sited clear of every air intake, the outdoor pilot house, the Lido, the sun deck, and the tender stowage's own outlets.
3. **Occupied-space air is supplied from a clean outside point,** filtered, and kept at a positive pressure relative to any hazardous space. Occupied air never recirculates from a hazardous or odour space.
4. **Pressure relationships are set per zone.** Hazardous spaces (battery, paint, fuel) are held at a negative or controlled pressure relative to their neighbours. Occupied spaces are held positive. Medical isolation is a controlled exception.
5. **Explosion-proof equipment** wherever a flammable atmosphere can form: paint store, fuel and tender stowage, and the battery room if gas can build up there.
6. **No PTFE membranes** in any breather or vent, following the materials policy. Sintered metal and plain ducted outlets are the approach.
7. **Intakes and outlets are separated by distance and height.** Intakes are drawn from the cleanest available point, and outlets are placed so their discharge cannot be drawn back into an intake.
8. **Every outlet has a named location** before the design is treated as complete. Until then, the register records the separation as unproven.

## Source register (summary)

The full register is `layout/ventilation-register.json`. It lists 16 sources: 4 hazardous (H), 2 combustion (C), 7 odour (O) and 3 occupied (A). Of the 16 outlets, 13 have no set physical location, so separation between them cannot yet be proven.

## Where the sources clash today

These clashes come from the existing design, and each one needs a decision:

- **Battery room and paint store** are both hazardous, both need dedicated outlets, and both sit on the Tank / Technical level. The Tank level has limited room for separate routes.
- **Battery room breather.** Membrane breathers are usually PTFE, which the materials policy excludes (`docs/materials-policy.md`). The battery room's breather needs a non-PTFE alternative.
- **Tender stowage** outboard fumes and the battery room's gas-tight exhaust must not share a duct.
- **Pet suites and pet wash** are odour sources on the Tween and Tank levels, close to guest cabins and the battery room. Their extract must stay separate from both.
- **Galley extract** on Main / Master must stay separate from the cabins and the medical bay.
- **Gensets** produce combustion exhaust, which must be routed away from the outdoor pilot house, the Lido, the sun deck and every intake. This is the hardest route on the vessel, because the outdoor spaces are the highest-value areas.

## What the strategy needs before it can be finished

1. The general arrangement, dimensioned, so each outlet has a real position.
2. A set of outlet positions on the hull, with the separation distances checked against each intake.
3. The ventilation standards for each hazard class, set by the fire-safety review.
4. Fan and duct sizing from an air-flow calculation per space.
5. Air-change figures for each space, set by the relevant standard and the space's use.

## Scope

This is a whole-craft strategy. The paint store, battery room and tender stowage notes already in the repo are sources within it, and their own requirements are unchanged. Where they conflict with this strategy, the strategy's separation rules apply.

## Owner request: genset exhaust in a lift shaft (not accepted)

The owner asked for the genset exhaust to run in a lift shaft. It is recorded in `layout/ventilation-register.json`, and the validator blocks it as an error until the decision is revisited.

**Why it is not accepted:**
- **Lift shafts are passenger and escape routes.** They open onto the lift lobbies on every level. Combustion gas (carbon monoxide, oxides of nitrogen, soot and heat) would reach those lobbies, which are the main route for guests and crew, including the medical route.
- **The shafts are not fire-separated from exhaust.** A hot exhaust in a shaft is a fire and smoke hazard in the same space people use to leave the craft.
- **Both lift shafts share one footprint.** Lift A and lift B sit side by side at x 48–51 m. Exhaust in either would reach the lobbies of both lifts.
- **Lift B also serves the Tank / Technical level,** so the exhaust route would start on the level where the gensets are, rising through the lobbies above.

These points rest on the layout and on the separation principles. The applicable fire and passenger-vessel rules must be checked by the fire-safety review and the classification society before any exhaust route is fixed.

**Alternatives to consider:**
1. **A dedicated exhaust trunk** in its own shaft, parallel to the lift shafts but separate from them, running from the Tank level to a stack outside. The space for this must come from the general arrangement.
2. **A stern or side exhaust** from the Tank level, through the hull, to a stack placed away from the outdoor pilot house, the Lido, the sun deck and every intake. This avoids the forward shafts entirely.
3. **Reducing the number of genset exhausts** by consolidating the gensets, so one trunk serves them all.

The choice depends on where the gensets sit, which is not yet dimensioned.

## Exhaust heat recovery

Yes, genset exhaust and coolant heat can be recovered. The figures below are placeholders, based on typical diesel energy splits and recovery rates, and must be replaced by the chosen engine's data.

**Energy at 20 kW electrical, 35% electrical efficiency (placeholder split):**
- Fuel power: 20 ÷ 0.35 ≈ 57 kW
- Exhaust heat (about 30% of fuel): about 17 kW
- Coolant heat (about 25% of fuel): about 14 kW
- Recovering half the exhaust heat gives about 8.6 kW of heat
- Converting that to electricity with an organic Rankine cycle at about 10% gives about 0.9 kW, roughly 4% of the 20 kW load

**What this means:** electricity recovery is small at this load, so it does not close the endurance target and adds weight and maintenance. Recovered heat used directly is worth more. The best uses on this craft are:
- **Battery room heating.** LFP cells need warming below their charge limit (`docs/energy-management-architecture.md`), so recovered heat can do part of that job.
- **Hot water** for the accommodation and the galley.
- **Water-makers.** Thermal desalination, if chosen, uses low-grade heat directly.
- **Tender and workshop heating** where needed.

**Constraints:**
- Exhaust heat exchangers add back-pressure, which the engine maker must approve.
- Cooled exhaust condenses acidic water, which needs drainage and corrosion-resistant materials (stainless, which is approved).
- The heat exchanger and any ORC add weight to the Tank level, which is already claimed by the fuel, battery and tender spaces.
- The exhaust trunk route is still open (see the lift-shaft decision above), and the recovery equipment has to fit on that route.

**Recommendation for review:** use the coolant and exhaust heat directly for battery heating, hot water and water-making first. Treat electricity recovery as a later option, only if a real load profile shows it is worth the weight.
