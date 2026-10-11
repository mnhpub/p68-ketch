# Toyota EV powerplant: energy production only, to a 600 V output bus

Status: decision recorded, owner direction. The Toyota EV powerplant is an energy source. It does not drive propulsion. Its output feeds the 600 V output bus. Ratings, the converter design and the AC or DC choice are not set.

## Role

- **Energy production only.** The powerplant generates electricity for the 600 V bus. It has no propulsion output, so it does not drive a shaft, a thruster or a tender drive.
- **Output bus.** The powerplant's converter delivers into the 600 V output bus, the same bus that feeds the propulsion drives, the LFP battery buffer and the ship's loads (`docs/energy-management-architecture.md`).
- **Propulsion stays separate.** Propulsion comes from the electric propulsion path on the 600 V bus (`propulsion-600v`), supplied from the buffer and the generation sources. The powerplant's role ends at the bus.

## Chain

1. Energy source: the Toyota EV powerplant, as a generator. Its own engine and motor-generator are the sources, not a traction system.
2. Power conversion: a converter from the powerplant's output to the 600 V bus. The powerplant's own voltage is not 600 V, so the conversion is required.
3. 600 V output bus: feeds the propulsion drives, the LFP battery buffer through its charger, and the ship's loads.
4. Battery buffer: charged from the bus, discharged to cover peaks and quiet running (`weights/energy-budget.json`, `buffer_architecture`).

## What this changes

- **Generation sources** now include the Toyota EV powerplant alongside the low-speed diesel generators and solar. All of them feed the same bus.
- **The energy budget** should count the powerplant's output at the bus, after conversion losses. The conversion efficiency is not yet known, so the budget must carry it as a placeholder.
- **Marine rules.** The powerplant's engine is a road-vehicle engine. Its marine use as a generator needs the same marine-engine route as the gensets: exhaust routing (`docs/genset-exhaust-and-systems.md`), fuel safety and the class and flag-state rules. The Toyota motor and inverter are automotive and need marine rating and a salt and vibration review.
- **The 600 V bus is still open** on AC or DC architecture (`systems.json`, `propulsion-600v`). The powerplant converter's type depends on that choice.

## Open decisions

1. The powerplant's rated output, and its converter efficiency at the bus.
2. AC or DC for the 600 V output bus. This sets the converter type.
3. Marine rating of the Toyota motor and inverter, and whether the engine is kept as a generator or replaced.
4. The powerplant's mass and position, for the weight register and the KG limit.
