# Bus voltage alignment: 600 V output bus to the Toyota EV platform's native voltage

Status: proposed, pending owner confirmation. This note reverses the 600 V target that `systems.json` sets for the propulsion bus. The alignment changes current, cable, switchgear and converter choices across the whole vessel, so it is recorded here and not yet applied to the data.

## Native voltage

The Toyota EV platform's high-voltage pack nominal voltage is about **355 V** (bZ4X, e-TNGA platform):
- km77, bZ4X 2023 technical information: 96 cells at 3.7 V, nominal total 355.2 V. <https://www.km77.com/coches/toyota/bz4x/2023/estandar/informacion/toyota-bz4x-2023-informacion-tecnica>
- PakWheels, bZ4X launch article: pack voltage 355 V with a 71.4 kWh pack. <https://www.pakwheels.com/blog/bz4x-first-battery-electric-vehicle-by-toyota/amp>
- Wikipedia, Toyota bZ4X: platform and battery options. <https://en.wikipedia.org/wiki/Toyota_bZ4X>

Caution: these are secondary sources. The nominal voltage for each facelift pack and each platform version is not confirmed by a Toyota technical document. The figure must be checked against Toyota's service data before any design uses it.

## Why align

A powerplant that outputs at its native voltage needs no step-up before the bus, so the converter and its losses go. The Toyota EV powerplant (`docs/hybrid-energy-production.md`) and the LFP buffer's charger both benefit.

## What it costs

Current at a given power is I = P / V. At 355 V, the same power draws about 1.7 times the current of a 600 V bus.

| Power | Current at 600 V | Current at 355 V |
|---|---|---|
| 1 MW | 1,667 A | 2,815 A |
| 2 MW | 3,333 A | 5,631 A |
| 5 MW | 8,333 A | 14,077 A |

Conductor cross-section, switchgear rating, busbar heating and the cost of protection all scale with current. A propulsion bus at a few megawatts would need much heavier cable and switchgear at 355 V. Propulsion at this scale is the main reason the 600 V target was chosen, so the propulsion power must be known before alignment is confirmed. The propulsion power is not yet calculated.

## Options

1. **Align the whole bus to 355 V.** Simplest for the powerplant. Heaviest for propulsion cable and switchgear. Requires the propulsion power to stay low enough to be practical.
2. **Keep the 600 V propulsion bus and align the powerplant through a DC-DC converter** from 355 V up to 600 V. The step-up adds a converter and its losses, but the propulsion cable stays at the 600 V current. This keeps the existing 600 V propulsion target.
3. **Two-voltage design:** a 355 V generation and battery bus, with a converter to a 600 V propulsion bus. This is the same as option 2, with the battery buffer also on the 355 V side.

Option 2 is the one the numbers favour, unless the propulsion power is small. Option 1 is simpler only if propulsion power is known to be low.

## What must change if the bus is aligned

These are the places that assume a 600 V bus (found by search of the repo):
- `systems.json`: the propulsion system name, summary and parameters ("600 V", "Not selected (600 V target)", and the "600 V or above 800 V" note).
- `scope.json`: the open items that mention 600 V.
- `weights/weight-register.json`: the propulsion item.
- `docs/energy-management-architecture.md`, `docs/electrical-generation-concept.md`, `docs/accommodation-considerations.md`, `docs/hybrid-energy-production.md`.

## Open decisions

1. The owner's choice of option 1, 2 or 3.
2. The propulsion power, which decides whether option 1 is practical.
3. The verified nominal voltage of the Toyota EV pack, from Toyota's own data.

## Owner note: propulsion is electric motor propulsion

Aligning the bus with the Toyota EV platform's native voltage results in electric motor propulsion. This matches the design: twin electric propulsion, one drive per shaft (`systems.json`, `propulsion-600v`).

Both options in this note are electric motor propulsion:
- **Option 1:** the propulsion motors run on a 355 V bus.
- **Option 2:** the propulsion motors run on a 600 V bus, fed through a DC-DC step-up from the 355 V side.

The choice between them is about current and cable at the propulsion power, not about the propulsion type. The propulsion power is still needed before option 1 can be confirmed.
