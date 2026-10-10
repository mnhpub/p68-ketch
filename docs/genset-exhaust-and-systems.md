# Genset exhaust, all exhaust needs, and the generation systems

Status: requirements for review. Nothing is chosen, sized or certified. The register of sources is `layout/ventilation-register.json`, and its separation checks are run by `npm run validate:ventilation`. This document covers every exhaust need on the craft, the generation plant's own requirements, and the safety and maintenance requirements for both.

## 1. The owner's request, and where it stands

The owner asked for the genset exhaust to come out of the top of the outdoor pilot house, clear of sail operations, with turbocharging, supercharging, energy recapture, thermal systems, a separate sensor and control system, clear status and maintenance indicators, spares for every part, and safety checks on engine start, stop, fuel and run toggles.

**Accepted in principle:** turbocharging, supercharging, energy and heat recapture, thermal systems, a separate monitoring and control system, status and maintenance indicators, spares, and the start, stop, fuel and run safety checks. These are developed below.

**Not accepted, and blocked by the register check:** the stack at the top of the outdoor pilot house roof. That roof is the outdoor helm (Station B), a guest area, and the sun deck and events area sit beside it (`layout/accessibility.json`, `docs/outdoor-pilot-house-impact.md`). Combustion exhaust there puts carbon monoxide, oxides of nitrogen and soot where people stand and steer, and the wind can carry it back down. The owner's sail-clearance point is correct but does not solve this. The register check blocks any combustion, hazardous or odour outlet on or above an occupied outdoor space.

**Alternative for review:** a stack aft or on the stern, from the Tank / Technical level through the hull, sited clear of every intake, every outdoor space and the sail area, and above the highest point that people reach. Its position needs the general arrangement.

## 2. Every exhaust need on the craft

Each row is in `layout/ventilation-register.json`. The hazard class decides the rules: H (flammable or toxic gas and vapour), C (combustion), O (odour and contamination), A (occupied air).

| Source | Class | Space | Outlet requirement | Equipment requirement |
|---|---|---|---|---|
| Battery room | H | Tank / Technical | Gas-tight exhaust, separate from every other duct, to a safe outside point | Explosion-protected fans and sensors. Pressure relief sized by fire review. Non-PTFE vent. |
| Paint store | H | Tank / Technical | Low-level extraction to a safe outside point | Explosion-proof equipment, vapour detection with door interlock |
| Fuel tank vents | H | Tank / Technical | Tank vents to a safe outside point, away from intakes and people | Flame screens on every vent |
| Tender stowage | H | Tank / Technical | Dedicated extract for outboard fuel and battery fumes | Explosion-protected where a flammable atmosphere can form |
| Gensets | C | Tank / Technical | Stack from the Tank level to the stern or side, clear of all intakes and outdoor spaces | Silencer, exhaust temperature sensing, back-pressure monitoring, condensate drain |
| Engine room air | C | Tank / Technical | Extract to outside, separate from the genset stack | Combustion air drawn from a clean outside point |
| Pet suites | O | Tween | Dedicated extract to outside, no recirculation | Separate duct from cabins and galley |
| Pet wash | O | Tank / Technical | Dedicated extract, drained to a separate waste route | Keep clear of the battery room |
| Galley | O | Main / Master | Grease-filtered hood extract to outside | Separate from cabins and the medical bay |
| Laundry (dryers) | O | Tween | Dedicated dryer duct to outside | Lint filtering, heat sensing |
| Bilges and wastewater | O | Tank / Technical | Vent to outside with odour filter | Clear of intakes |
| Waste processing | O | Tank / Technical | Dedicated odour-filtered extract | Separate from other extracts |
| Workshop | O | Tank / Technical | Extract to outside, fume extraction at the bench | Separate from the paint store extract |
| Medical bay | A | Tween | Filtered extract to outside, pressure-controlled | Isolation capability, positive and negative pressure zones |
| Guest accommodation | A | Tween, Main / Master | Extract to outside, fresh-air intake from a clean point | Positive pressure against hazardous spaces |
| Bridge and lounges | A | Bridge, Commander, Lido, Main | Extract to outside, fresh-air intake from a clean point | Positive pressure against hazardous spaces |

### Rules that apply to every outlet

1. **No shared duct, fan or outlet** between sources of different class or separation group.
2. **No hazardous, combustion or odour outlet on or above an occupied outdoor space**, and no outlet that discharges into a lift shaft or escape route.
3. **Every outlet clear of every intake.** Intakes are drawn from the cleanest point available. Distances are set from the general arrangement and the wind study, not assumed here.
4. **Discharge direction and height** are set so that exhaust cannot be drawn back into an intake or onto a deck.
5. **Weather protection** on every outlet: a cap that keeps out rain and spray without blocking flow.
6. **Fire dampers** where a duct passes through a fire division.
7. **Condensate drainage** on any duct carrying hot, humid or combustion gas.
8. **Membranes** in any vent follow the materials policy: no PTFE. Sintered metal or plain ducted outlets are the approach.
9. **Every outlet has a named physical location** before the design is treated as complete. Thirteen of the sixteen currently have none, so separation cannot yet be proven.

## 3. Generation plant: technologies

### Turbocharging and supercharging

- A turbocharger recovers exhaust energy to boost the intake air, which raises the power and the efficiency of a given engine. A supercharger is driven from the engine, and it trades some output for quicker response.
- At the low average load in this design (about 20 kW), boost is mostly a question of part-load efficiency and response. It is not a route to more electricity at this load. The engine maker must give the part-load curve with and without boost.
- Turbo and supercharger add heat, and they change the exhaust temperature and back-pressure that the heat-recovery equipment sees (see below).

### Energy and heat recapture

- Exhaust heat recovery and coolant heat recovery are described in `docs/ventilation-strategy.md`. Direct use is first priority: battery room heating, hot water, water-making and workshop heating. Electricity recovery at about 4% of the 20 kW load is not worth the weight yet.
- Turbo-compounding (a power turbine on the exhaust) is a further option. Its gain at this load is small, and the back-pressure it adds must be approved by the engine maker.

### Thermal systems

- Coolant circuit, charge-air cooling, oil cooling and exhaust cooling each need their own heat exchanger, with its temperature and flow sensors.
- The thermal loads feed the energy budget: the heat that is recovered reduces the battery room's heating load and the hot-water load.
- Thermal circuits are closed loops, so they do not connect to any outside air except through the exchangers.

### Electrical generation

- Low-speed engine and permanent-magnet generator, as set out in `docs/electrical-generation-concept.md`. Its mass goes into the weight register.
- Power electronics feed the battery bank through the energy management system (`docs/energy-management-architecture.md`).

## 4. Safety checks on start, stop, run and fuel

These are the requirements for each genset and for the plant as a whole. The safety functions run in the hardware layer, not in the supervisory software (`docs/control-software-architecture.md`).

### Start permissives (all must be true before start)

1. No emergency stop active.
2. Fuel supply valve open and fuel pressure within range.
3. Lubricating oil pressure and level within range.
4. Coolant level and temperature within range.
5. Room extract fan running and airflow proved (engine room air, class C).
6. No fire, fuel-leak or gas alarm active in the engine room or fuel space.
7. The genset is not locked out for maintenance (lock-out tag removed by the person who applied it).
8. The start is requested from an authorised station, and the request is logged.

### Run protections (any one shuts the engine down)

1. Overspeed.
2. Low lubricating oil pressure.
3. High coolant temperature, or loss of coolant flow.
4. High exhaust temperature, or loss of exhaust back-pressure within limits.
5. Fuel leak or fuel pressure loss.
6. Fire or gas detected in the engine room.
7. Emergency stop, from any station, which is hardwired and always accepted.

### Stop and fuel

- Normal stop and emergency stop are separate. The emergency stop cuts fuel at the source and does not depend on the software.
- Fuel shut-off valves close on emergency stop and on any run protection trip.
- Fuel tanks, lines and the fuel-processing space have leak detection, with an alarm to the piloting console and the event log.
- Any fuel release drains to a containment system, not to the bilge.

### Run toggle

- The run toggle at each station is a deliberate action (hold, as for the other control functions), and it can only be engaged when the start permissives are met.
- The toggle state is shown at every station with the genset's identity, so no one starts a unit they cannot see.

## 5. Separate sensors, controls, status and maintenance

- **Sensors:** exhaust temperature and back-pressure, coolant and charge-air temperature, oil pressure and level, fuel pressure and leak, speed, load, room air flow, room temperature, and fire and gas detection. Each sensor is named in the register of sensors, with its range and its trip levels.
- **Control:** a local control panel on each genset, with the run protections above in its hardware. The supervisory software reads the state and can request a start or stop, but it cannot override a protection.
- **Status:** each genset shows running, standby, fault, locked-out or maintenance, with the cause of any trip recorded.
- **Maintenance indicators:** running hours, next service due, filter and oil change status, and any fault history. Each indicator is tied to the spares it needs.
- **Testing:** each protection is tested on commissioning and on a fixed schedule. A test is logged with its result.
- **Separation:** the genset monitoring system is separate from guest networks and from the satellite link.

## 6. Spares, end to end

Spares are held for each system, sized from the supplier's service intervals:
- **Engine:** filters, oil, seals, belts, injectors or their spares, turbo and supercharger spares, sensors.
- **Generator and power electronics:** bearings, cooling components and the control modules that the manufacturer recommends holding.
- **Heat recovery:** gaskets, exchanger spares and condensate drain parts.
- **Fuel system:** filters, seals, shut-off valve spares and leak-detection sensors.
- **Ventilation:** fan spares, filters, dampers and fire-damper spares.

Quantities are placeholders until the suppliers give service intervals and spares lists.

## 7. Open decisions

1. **Stack location.** Stern or side from the Tank level, as proposed here, or a different route. The owner's roof location is not accepted.
2. **Engine and generator models.** Which engine, its part-load curve with and without turbo or supercharger, and the generator's mass.
3. **Engine room layout and outlet positions,** from the dimensioned general arrangement.
4. **Fire and passenger-vessel rules,** from the fire-safety review and the classification society.
5. **Control and monitoring system,** as separate work (`docs/control-software-architecture.md`).
6. **Spares quantities,** once the suppliers' intervals are known.
