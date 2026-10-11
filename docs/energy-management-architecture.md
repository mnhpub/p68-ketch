# Energy management architecture: all generation charges an LFP battery bank

Status: concept. Nothing here is chosen or certified. Battery capacity, cell supplier, EMS product and generator models are open. Class society and flag-state requirements for electrical systems and battery installations have not been reviewed and apply in full.

## The architecture

All energy production feeds one battery bank:

- **Sources:** low-speed diesel gensets with brushless permanent-magnet generators (see `docs/electrical-generation-concept.md`), solar on the roof candidates (`solar-generation`), and shore power when alongside.
- **Store:** LiFePO4 (LFP) battery bank with a marine battery management system (BMS) for cell balancing, protection and state of charge.
- **Distribution:** the 600 V bus, with converters between the sources, the bank and the loads. The AC or DC architecture is still open (`systems.json`, `propulsion-600v`).
- **Control:** a marine-grade energy management system (EMS) that decides what runs, what charges, and what is shed.

The battery is a buffer, not the energy store. Fuel and solar are the energy, and the battery covers peaks, quiet running and short gaps in generation. This is the buffer architecture in `weights/energy-budget.json`.

## Correction to the earlier battery figure

The earlier battery-only calculation assumed 0.2 kWh/kg, a generic lithium-ion value. That is too high for LFP, which is heavier per kWh. The corrected system-level assumption is 0.12 kWh/kg for a marine LFP pack, including enclosure and busbars. It is still an assumption to verify.

| Load | Battery-only, 60 days (0.12 kWh/kg, 80% DoD) |
|---|---|
| 20 kW | 300 t, 37% of 806 t displacement |
| 50 kW | 750 t, 93% |
| 100 kW | 1,500 t, 186% |

Battery-only endurance is not viable at any placeholder load. The conclusion from before is unchanged, and the figure is worse.

## Sizing the buffer

Battery as buffer: 100 kW peak for 4 hours is 400 kWh. At 0.12 kWh/kg and 80% DoD, that is 4.2 t, about 0.5% of displacement.

Combined with 6.9 t of diesel for 60 days at 20 kW (35% efficiency), the energy store totals about 11 t. That is roughly 1.4% of displacement, against 300 t for the battery-only case at 20 kW.

Both the 100 kW peak and the 4-hour buffer are placeholders. They come from a load study, which has not been done.

## What the EMS must do

These functions are the requirements the EMS has to meet. They are not a product choice.

1. **Source selection.** Choose which generator runs, and when, for the state of charge and the load. Run each genset near an efficient load, rather than at a low average, to avoid the part-load penalty in the generation note.
2. **Charging.** Limit charge current and voltage to the BMS's limits. LFP has a low-temperature charging limit, typically around 0 °C, and needs heating or a block below it. Confirm against the chosen cells.
3. **Load management.** Shed loads in priority order. Navigation, communications, emergency stop, fire detection, bilge and steering are never shed. Medical equipment, including the AED on tenders, is never shed either.
4. **Operating modes.** Define at least these: quiet mode (battery only, gensets off, for anchorage and dock approach); underway (gensets and battery together); charge (gensets running, battery charging); and emergency (minimum loads, with the state of charge reserved for steering and navigation).
5. **Fault response.** A BMS fault must isolate the affected string without disabling the whole bank, and must raise an alarm to the piloting console and the event log.
6. **Interfaces.** The EMS reads the piloting state (dock mode, underway, sails, auto-dock thruster demand) so that boosters and thrusters are not starved by a low battery.

## LFP-specific points

- **Thermal management.** Cell temperature must stay in the chosen cells' operating range. This is HVAC load on the energy budget, and the battery space needs ventilation and heating.
- **Cycle life.** LFP is well suited to daily cycling, but cycle life depends on depth of discharge and temperature. The 80% DoD figure is a planning value to verify against the cell datasheet.
- **Fire.** LFP has a lower thermal-runaway hazard than some lithium chemistries, but it is not zero. The battery space needs fire detection, separation from fuel and tenders, and a defined response. This must go through the fire-safety review already noted in `systems.json`.
- **Balancing.** Long strings need active or passive cell balancing, which the BMS must provide.

## Marine-grade EMS

"Marine-grade" here means that the EMS and BMS are designed and tested for the marine environment: vibration, salt, humidity, temperature and electromagnetic conditions. It also means that the class society and flag state have accepted the design. No product has been chosen, and no compliance is claimed.

## Open questions

1. Real load profile, by season and by operating mode. This is the first input the budget needs.
2. LFP cell and pack supplier, with datasheet figures for specific energy, DoD, cycle life and charge temperature.
3. Buffer size: peak load and hours of buffer, from the load profile.
4. Genset model and part-load curve, which fixes the fuel figures.
5. DC or AC distribution, which fixes the converter and EMS architecture.
6. Class and flag-state requirements for the battery installation, the EMS and the bus.

## Rackmount battery bank

The battery bank is rackmount: standard 19-inch racks, with LFP modules that slide in. This affects space, installation and maintenance.

- **Space.** Each rack is about 0.6 m wide and 1.0 m deep. Front service clearance of 1.0 m is needed, so each rack takes about 0.6 m × 2.0 m of floor. Aisle and access are extra.
- **Rack count (placeholder).** For a 400 kWh usable buffer at 80% DoD, the nameplate is 500 kWh. At an assumed 5 kWh per 4U module, that is 100 modules, or 400U, which fits 10 racks of 42U. The module size is a placeholder until a product is chosen.
- **Footprint.** 10 racks × 1.2 m² each ≈ 12 m². This is the battery room request in `layout/envelope-budget.json` (Tank / Technical, 12 m² placeholder). The room must be separated from the fuel, and the bank must be kept off the tender stowage.
- **Ventilation and cooling.** Racks need forced ventilation with a defined airflow, and the room needs heating for LFP below its charge limit. Both add to the HVAC budget.
- **Installation.** Racks are fixed to the hull structure and must be restrained against vessel motion. The restraint loads are not yet calculated.
- **Maintenance.** Modules are hot-swappable only if the BMS and EMS allow it. This must be confirmed with the product.
- **Mass.** Rack and module mass are not yet in the weight register. The battery item's mass stays unknown until a product is chosen.

## Revised battery room: layout, cooling, exhaust, pressure, IP67

This section replaces the earlier 5 kWh module and 10-rack assumption. The figures come from `npm run validate:budgets`, from the `battery_room` block in `weights/energy-budget.json`.

### Two layouts

The usable buffer is 400 kWh at 80% DoD, so the nameplate is 500 kWh.

| Option | Racks | Modules (4U) | kWh per module | Heat per rack | Airflow per rack | Floor (racks, front service) |
|---|---|---|---|---|---|---|
| A: four racks, packed | 4 | 42 | 11.9 | 750 W | 224 m³/h | 4.8 m² |
| B: eight racks, spread | 8 | 84 | 6.0 | 375 W | 112 m³/h | 9.6 m² |

Heat is 3% of the 100 kW peak, so 3.0 kW in total. This is a placeholder loss fraction, to verify with the cell and converter data.

Option A needs 12 kWh modules. Option B needs 6 kWh modules, which is a more common size, but this has to be confirmed against products. Option B also halves the heat density and the airflow per rack, and it leaves room to service each rack. Option A saves about 5 m² of floor.

**Recommendation for review: option B,** if 6 kWh modules are available, because the cooling and the serviceability are better. Option A is the fallback if the floor cannot take 9.6 m² on the Tank level.

### Closed-loop cooling, not open ventilation

IP67 means the enclosure is dust-tight and can survive temporary immersion. Open air intakes and exhausts break that rating. The battery room therefore needs:

- A **sealed air loop** through the racks, with fans inside the room. Heat leaves through an **air-to-water heat exchanger** mounted in the room's wall or on the Tank level, connected to a closed water loop that rejects heat outside the hull.
- A **heat source for cold conditions.** LFP cannot be charged below its charge limit, typically around 0 °C, so the loop must be able to warm the room.
- A **pressure equaliser** in the room wall: a breather or membrane vent that keeps the room at the outside pressure without letting water or dust in. It is rated for the IP67 requirement.

### Exhaust in a thermal event

A failing LFP cell releases gas. The gas is flammable and toxic, and it can be hot. A sealed room needs a designed path for it, or the room will pressurise. This is a **separate, gas-tight exhaust** to a safe outside point, with:

- A flame arrestor or fire-rated duct, and a damper that closes in normal running.
- Gas detection in the room, with an alarm to the piloting console and the event log.
- A **pressure-relief** route sized for the event, so the room does not rupture. The size is not calculated, and it must come from the fire-safety review.

This exhaust is the main conflict with the IP67 sealing. The breather keeps the room equalised in normal running. The gas-tight exhaust handles an event. They must not be the same path.

### Pressure

- The room is held at a small differential pressure to the adjacent spaces, monitored by a sensor. A pressure loss means a door or seal has failed. This is an alarm.
- The door has a seal, and the pressure sensor reads the room, not the duct.
- During an event, the relief path opens, and the pressure alarm is part of the sequence.

### Temperature

- Operating and charge limits come from the chosen cells, so the setpoint and alarm values are not set here. A placeholder operating band of 20 to 25 °C is used for planning only.
- Two alarm levels are needed: a high-temperature warning that starts cooling, and a high-temperature alarm that isolates the affected rack. The thresholds come from the cell datasheet.
- Each rack has its own temperature sensor, read by the BMS and the EMS.

### What this changes in the budgets

- The battery room request in `layout/envelope-budget.json` is now 16 m²: the racks (4.8 to 9.6 m²), the cooler, the EMS cabinets, the detection, and the aisle.
- The HVAC load for the battery room is a new item in the energy budget. It is not yet in the weight register or the systems register.
- The fuel and battery rooms must be separated, and the gas-tight exhaust must not pass through the tender stowage.

### Open questions

1. Module size: is a 6 kWh rackmount module available? If not, option A needs 12 kWh modules, which is less common.
2. Floor on the Tank level: is 9.6 m² available for option B, with separation from the fuel?
3. Exhaust route: a dedicated outside vent from the Tank level. Which point on the hull, and how is it kept clear of the outdoor pilot house, the Lido and the sun deck?
4. Cooling load: the battery room's cooling and heating loads, from a thermal model.
5. Fire safety: the pressure-relief size, the gas detection, and the response. This needs a fire-safety review, not a design estimate.
