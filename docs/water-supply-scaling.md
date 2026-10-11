# Water supply: atmospheric water capture, scaled to demand

Status: owner direction recorded, with the scaling worked out. The occupancy, water-per-person and energy figures are placeholders. The repo has no occupancy figures yet, so every result below moves with them.

## Owner direction

Water is supplied by plain air-water capture (atmospheric water generation, AWG), rated at 5 US gallons (18.9 L) per day per unit. The unit count is scaled to the output needed.

## Inputs (placeholders)

| Input | Value | Status |
|---|---|---|
| Rated output per unit | 18.9 L/day (5 gal) | Owner direction |
| Output at marine conditions | 60% of rated (11.4 L/day) | Placeholder. AWG output falls with low humidity and cool air. Verify with the chosen unit's data. |
| Litres per person per day (drinking, cooking, hygiene, laundry) | 150 | Placeholder |
| Litres per pet per day | 5 | Placeholder |
| AWG energy | 0.4 kWh per litre | Placeholder: a 5-gallon unit drawing 300–600 W for about 24 h gives roughly 0.3–0.5 kWh per litre. |
| Seawater reverse osmosis (RO) energy | 0.004 kWh per litre | Placeholder: RO typically takes 3–5 kWh per cubic metre. Verify with the chosen plant. |

## Scaling results

| Case | People | Pets | Demand (L/day) | AWG units needed | AWG energy (kWh/day) | AWG average power | RO energy (kWh/day) |
|---|---|---|---|---|---|---|---|
| Low | 12 | 0 | 1,800 | 159 | 720 | 30 kW | 7 |
| Medium | 26 | 4 | 3,920 | 346 | 1,568 | 65 kW | 16 |
| High | 40 | 8 | 6,040 | 532 | 2,416 | 101 kW | 24 |

**The finding:** AWG cannot be the whole water supply. Even the low case needs 159 units and about 30 kW of continuous power, which is a large share of the whole electrical budget. The same water from seawater RO takes about 7 kWh a day, roughly 100 times less energy.

## Where AWG does fit

Drinking water alone is a much smaller load. At 4 litres per person per day for 40 people, that is 160 L/day, which needs 15 derated units and about 64 kWh a day, or about 2.7 kW on average. That is a practical backup supply for drinking water, and it keeps working if the RO plant is down.

## Recommendation for review

1. **Seawater RO as the main supply** for all demand beyond drinking water, sized from the occupancy figure once it is set.
2. **AWG as a drinking-water backup**, sized to the drinking demand, not the whole demand.
3. **Heat recovery** from the genset coolant or exhaust, as set out in `docs/ventilation-strategy.md`, offsets part of the RO plant's energy if a thermal desalination option is chosen.

## Other requirements the AWG units bring

- **Air intake and exhaust.** AWG units draw large volumes of outside air and discharge warm, humid air. This is a new vent source, added to the ventilation register: intake from a clean outside point, exhaust clear of every intake, and no discharge onto an outdoor space.
- **Water quality.** Condensed water is nearly pure, with no minerals and no protection against bacteria. It needs remineralisation and disinfection before it is used, and it needs the potable-water testing in `docs/preservation-and-maintenance.md`, under the potable-water checks.
- **Condensate and drainage.** Condensate drains are stainless and routed to the freshwater system only after treatment.
- **Materials.** AWG units often use foam insulation and foamed plastic parts. Both are banned by the materials policy. Units must be specified foam-free, or excluded.
- **Maintenance and spares.** Filters, condenser coils and fans need a schedule and spares, as set out in the spares plan.

## Open decisions

1. Occupancy figures, which set every number above.
2. Whether a foam-free AWG unit exists at the required size. If not, the drinking backup needs another source.
3. The RO plant's size, intake and brine outlet, set by the environmental review.
4. The remineralisation and disinfection method for AWG water.

## Occupancy basis (proposal, for owner confirmation)

The repo holds no guest or crew numbers. The figures below are proposals, derived from the layout areas in `layout/decks-layout.json`, with cabin sizes stated. The owner must confirm each one.

### How the berth counts were derived

| Item | Source | Assumption | Result |
|---|---|---|---|
| Guest cabins | Layout: "Guest cabins" rectangles, total 142.0 m² | 15 m² per twin cabin | 9 cabins, 18 berths |
| Owner suite | Layout: 45.5 m² | Two berths | 2 |
| VIP accommodation | Layout: 32.9 m² | Two berths | 2 |
| Accessible guest cabin | Layout: 24.6 m² | Two berths | 2 |
| Guest total at layout maximum | | | 24 guests |
| Crew quarters | Layout: 54.8 m² | 10 m² per twin cabin | 5 cabins, 10 crew berths |
| Roof events | `docs/outdoor-pilot-house-impact.md` | 100 people (a load assumption for events, not sleeping berths) | 100 visitors on event days |

The room areas are the only data behind these figures. The cabin sizes are placeholders. If the owner intends a smaller guest count, the crew count, not the guest count, becomes the larger share of demand.

### Scenarios

| Scenario | Guests | Crew | Pets | Demand (L/day) | AWG units | AWG average power | RO energy (kWh/day) |
|---|---|---|---|---|---|---|---|
| Owner private | 4 | 10 | 0 | 2,100 | 185 | 35 kW | 8 |
| Charter standard | 12 | 10 | 0 | 3,300 | 291 | 55 kW | 13 |
| Layout maximum | 24 | 10 | 0 | 5,100 | 450 | 85 kW | 20 |
| Layout maximum with pets | 24 | 10 | 4 | 5,120 | 451 | 85 kW | 21 |
| Event day (drinking water only) | 100 visitors | | | 400 | 36 | 7 kW | (not applicable) |

Crew is held at 10 in every scenario, since a vessel of this size needs a crew whatever the guest count. Every scenario uses 150 L per person per day and 5 L per pet per day, both placeholders.

### What the scenarios show

- **Atmospheric water cannot be the whole supply** in any scenario. Even the owner-private case needs 185 units and about 35 kW of continuous power.
- **Reverse osmosis is the main supply** in every scenario. It needs 8 to 21 kWh a day.
- **Drinking water from the atmospheric units is the practical backup.** At event-day drinking demand, 36 units draw about 7 kW on average, which is workable as a backup if the event load is kept short.
- **The guest count is the main lever.** Demand moves by about 1,200 L a day between the owner-private and the charter standard cases.

### What the owner needs to confirm

1. The guest count: a private owner count, a charter standard, or the layout maximum.
2. The crew count.
3. The number of pets.
4. Whether event days are part of the water plan, and for how many visitors.
5. The water per person per day, since hygiene and laundry use vary widely by guest.

## Drinking-water scaling (owner direction: atmospheric capture for drinking water only)

The atmospheric units are sized for drinking water alone. Reverse osmosis supplies everything else: hygiene, cooking, laundry, pets beyond drinking, and cleaning. The drinking figure is 4 litres per person per day, with 1 litre per pet per day. Both are placeholders for the owner to confirm.

| Scenario | People | Pets | Drinking demand (L/day) | Atmospheric units | Average power | Energy (kWh/day) |
|---|---|---|---|---|---|---|
| Owner private | 14 | 0 | 56 | 5 | 0.9 kW | 22 |
| Charter standard | 22 | 0 | 88 | 8 | 1.5 kW | 35 |
| Layout maximum | 34 | 0 | 136 | 12 | 2.3 kW | 54 |
| Layout maximum with pets | 34 | 4 | 140 | 13 | 2.3 kW | 56 |
| Event day, 100 visitors | 100 | 0 | 400 | 36 | 6.7 kW | 160 |

Units are derated to 11.4 L a day, from the rated 18.9 L, and each draws 0.4 kWh per litre (both placeholders, see the inputs above).

### What this changes

- **The atmospheric units become a practical drinking supply.** At 5 to 13 units for the normal scenarios, the average power is 1 to 2 kW, which is workable on the battery buffer.
- **Event days are the peak.** Thirty-six units draw about 7 kW on average, and that load has to be planned into the event schedule, not left to run unchecked.
- **Reverse osmosis carries the rest.** Its energy is small, about 8 to 21 kWh a day across the scenarios above (see the occupancy section), so the split puts the bulk of the water on the plant that costs least energy.

### Requirements that still apply to drinking water

- Remineralisation and disinfection before use, since condensed water has no minerals and no protection against bacteria.
- Potable-water testing under the checklists in `docs/preservation-and-maintenance.md`.
- Foam-free units, since foam is banned under the materials policy.
- Air intake and exhaust routed as set in `layout/ventilation-register.json`, with the atmospheric units' exhaust clear of every intake.

## Embarked water: buffer only

Owner direction: water is produced onboard. No potable water is embarked as provisions. The water on board is a storage buffer that covers a production outage, not a supply for the passage.

- **Production:** reverse osmosis is the main supply, and atmospheric units are the drinking backup (see above).
- **Buffer:** sized to cover a stated outage period at the chosen demand. The outage period is a policy decision. This note uses **72 hours** as a placeholder.

| Scenario | Drinking buffer (4 L/person/day) | Full-demand buffer (150 L/person/day) |
|---|---|---|
| Owner private (14 people) | 168 L | 6.3 m³ |
| Charter standard (22 people) | 264 L | 9.9 m³ |
| Layout maximum (34 people) | 408 L | 15.3 m³ |
| Event day drinking (400 L/day) | 1,200 L | not applicable |

- The drinking buffer is small, and it can be held in the Tank / Technical water storage. The full-demand buffer is large and needs a deliberate choice of how much water to hold against a production failure.
- Event days need their own drinking reserve, since the 400 L/day drinking load is the peak.
- The buffer is not a provisioning figure. Potable water quality, treatment and storage hygiene still apply (see the potable-water checks in `docs/preservation-and-maintenance.md`).

**Decision needed:** the outage period the buffer must cover, and whether the buffer covers drinking only or full demand.
