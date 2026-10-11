# 800 V bus: design basis and headroom

Status: design basis for review. The 800 V option is listed in `systems.json` (propulsion, "600 V or above 800 V, not decided"). This note picks it as the basis and sets the headroom rules. Propulsion power is still not calculated, so no equipment is sized. Every factor marked placeholder must be confirmed against the applicable rules and the equipment data.

"Flux" is read here as headroom: the margin between the rated capacity of each part and the loads it carries continuously, including the worst case.

## Voltage window

| Item | Value | Status |
|---|---|---|
| Nominal bus voltage | 800 V DC | Owner direction |
| Minimum operating voltage | 720 V (−10%) | Placeholder window |
| Maximum operating voltage | 880 V (+10%) | Placeholder window |

Current is worst at the lowest voltage, because I = P / V. Ratings are set from the minimum voltage, not the nominal.

## Headroom rules

1. **Continuous current at minimum voltage:** I_cont = P_cont / V_min.
2. **Rated current with headroom:** I_rated ≥ H × I_cont, with **H = 1.25** (placeholder for continuous loads). Conductors, busbars, switchgear and fuses are rated to I_rated.
3. **Insulation:** rated to at least H × V_max = 1.25 × 880 V = **1,100 V**.
4. **Thermal:** every component is checked at the ambient and enclosure temperature of its space (Tank / Technical is the hottest candidate, next to the genset exhaust and the battery room).
5. **Derating:** no component runs above its rated continuous current in any operating mode, including the worst combination of sources and loads.

## Current at continuous power

| Continuous power | I at 720 V (minimum) | With headroom (×1.25) | I at 800 V nominal |
|---|---|---|---|
| 1 MW | 1,389 A | 1,736 A | 1,250 A |
| 2 MW | 2,778 A | 3,472 A | 2,500 A |
| 5 MW | 6,944 A | 8,681 A | 6,250 A |

Each MW of continuous load needs a bus rated at about 1,736 A. Above roughly 2 MW continuous, the bus, cable and switchgear sizes grow quickly, which is why the propulsion power must be known before the cable is chosen.

## Source and buffer on the 800 V bus

- **Toyota EV powerplant.** Native pack output is about 355 V (`docs/bus-voltage-alignment.md`). A step-up converter raises it to 800 V, a ratio of 2.25. The converter's efficiency at that ratio is not yet known.
- **LFP buffer.** At 3.2 V nominal per cell, an 800 V string needs about 250 cells in series, with cell balancing across the string. The buffer can sit on the 800 V bus directly, or on a 355 V string with its own converter. The pack and its battery management are sized in `docs/energy-management-architecture.md`.
- **Diesel gensets.** Their generator output is converted to 800 V through the power electronics already described in `docs/electrical-generation-concept.md`.

## Safety and insulation

- A DC bus at 800 V is a shock and arc-flash hazard. Isolation, creepage, clearance and interlocks are set by the applicable low-voltage and high-voltage rules and the classification society. The rules here are design targets, not compliance claims.
- Each high-voltage section has a lock-out point, and the high-voltage lock-out procedure in `checklists.json` (draft) applies. Work on the bus requires the isolation checks the checklist sets out.
- Fault current at 800 V DC must be interrupted by DC-rated breakers. AC-rated breakers are not used on the DC bus.

## Consequences for the register

- `systems.json`: the propulsion entry's "600 V" values change to 800 V once confirmed. The register's option "600 V or above 800 V" becomes 800 V.
- `weights/weight-register.json`: the propulsion and cable items gain the headroom rating, which affects their mass.
- `docs/bus-voltage-alignment.md`: option 2 (355 V to 600 V) becomes a 355 V to 800 V step-up under this basis.

## Open decisions

1. Propulsion continuous power, which fixes the bus rating and the cable.
2. The headroom factor H, and whether the rules set a different value for marine continuous loads.
3. Operating voltage window, from the equipment data.
4. The step-up converter's efficiency and mass at a 2.25 ratio.
5. The buffer's location: directly on the 800 V bus, or a 355 V string with its own converter.
