# Preservation and maintenance: keeping the craft pristine for decades

Status: design intent, documented as wanted. Intervals are placeholders until the suppliers, the coating and sealant makers, and the classification society give figures. Nothing here is a warranty or a certified schedule.

## Intent

The owner wants the craft kept in pristine condition for many years. That means finishing and sealing work is planned and recorded, not done ad hoc. Every protected surface, every sealed joint and every replaceable part has a documented method, an inspection interval and a record of the last time it was done.

## Finishing and sealing processes (wanted, and documented)

These are the controlled processes the owner has approved. Each is recorded per job.

| Process | Where it applies | Records kept |
|---|---|---|
| Teak deck seam sealing | Outdoor teak decking, between boards | Sealant family, batch, applicator, date, joint location |
| Sealing of exposed steel protection | Lido, sun deck, roof and any steel frame exposed to the elements | Coating or sealant system, surface preparation, primer, curing, inspection |
| Joint sealing in the sealed structure | Hull and interior joints that must stay watertight or air-tight | Product, batch, joint location, pressure or leak test result |
| Surface preparation and priming | Any steel or stainless surface before finishing | Preparation grade, primer, ambient conditions |
| Teak finishing | Decking and interior joinery | Oil or finish product, coats, date, area covered |
| Stainless passivation | Stainless fittings and panels, after fabrication and welding | Passivation method, test result, date |

Each process runs under a written procedure. Products are approved by family before use, and each product carries a certificate for PFAS-free content and low emissions, as the sealant exception requires (`docs/materials-policy.md`).

## Maintenance cycles (placeholders)

| System | Activity | Placeholder interval | Owner of the record |
|---|---|---|---|
| Hull, below the waterline | Inspection of protective system and anodes, out of the water | Annually, and after any grounding | Engineering |
| Hull, above the waterline | Inspection of coating and sealing | Every 6 months | Engineering |
| Cathodic protection (if used) | Anode inspection and replacement | Per anode manufacturer, checked annually | Engineering |
| Teak decking | Clean, oil or finish, inspect seams | Every 3 months, with a full seam check yearly | Deck crew |
| Sealants throughout | Inspect for cracking and lift; replace where failed | Yearly inspection, replacement per family | Engineering and deck crew |
| Exposed steel protection | Inspect and touch up | Every 6 months | Engineering |
| Stainless fittings and panels | Clean, check for crevice and chloride attack | Every 3 months | Deck and interior crew |
| Outdoor furniture (teak, stainless, natural cushions) | Clean, inspect, repair | Monthly in season, full check yearly | Deck crew |
| Interior upholstery and soft goods | Clean, repair on board | As needed, full check yearly | Interior crew |

Placeholder intervals will be replaced by supplier and class figures before any schedule is treated as final.

## Records

- Every job is logged: date, location, product and batch, procedure followed, who did it, and the inspection result.
- Records are kept on board and in shore backup, so they survive the loss of one copy.
- Records feed the crew checklists (`src/aggregates/underway.ts` for piloting; a separate maintenance system for the rest, as set out in `docs/exterior-and-maintenance.md`). The public side holds the content; no maintenance system connects to vessel control.
- The record of each protective system is the basis for any later sale, insurance or classification survey.

## Replacement and spares

- Sealants, teak, natural cushions and stainless parts are replaced on the schedule above, not when they fail.
- Spares for each process (sealant by family, coating touch-up kits, teak oil, stainless replacement fixings) are held on board, as set out in the spares plan.

## Open decisions

1. The hull protection system, and whether coatings fall under the same controlled-process exception as sealants.
2. Cathodic protection, with its anode replacement schedule, if chosen.
3. The approved sealant families and coating systems.
4. The inspection intervals, once the suppliers and the classification society give figures.

## Painting kit, paint store and drip control

Owner direction: a painting kit for the maintenance crew, kept in the maintenance area, with paint stored properly and no paint drips anywhere on the craft.

### Paint store

- **Its own room**, separated from fuel, battery, and any solvent or adhesive stores. Paint and its thinners are flammable, so the store is ventilated, fire-protected, and sited on the Tank / Technical level away from ignition sources.
- **Storage:** sealed containers on a lipped, corrosion-resistant shelf, labelled with product, batch, opening date and shelf life. Containers are kept upright and out of direct sun and frost.
- **Inventory:** the store holds only the approved products (see the coating decision below). Each product has a safety data sheet on file.
- **Disposal:** waste paint, rags and thinners go to a sealed hazardous-waste container, collected for proper disposal. They are not discarded with general waste or into the wastewater system.

### Painting kit (carried to the work site)

- Drop sheets and masking, sized to the area, so nothing below or beside the work is exposed.
- Tray liners, lidded containers and a drip tray for every brush, roller and gun.
- Stirrers, filters and measuring cups, one set per product family, so products are not mixed.
- Solvent-resistant gloves, respiratory protection, eye protection and coveralls, sized for the crew.
- Rags and wipes in a sealed bin, emptied at the end of each job.
- A kit list checked before every job.

### Drip control: the procedure

No paint drips anywhere on the craft. The procedure:
1. **Contain before you open.** Lay drop sheets and masking before a container is opened. Work is not started until the area is covered.
2. **Use a drip tray at every point of use.** Brushes and rollers are loaded over a tray, never over the deck or the steel.
3. **Work from the top down and from one end.** This keeps drips from landing on finished work.
4. **Stop and clean at the first drip.** A drip is wiped at once, before it cures, with the approved cleaner for that product.
5. **Clean up at the end of each session.** Drop sheets are removed only after the surface has cured, and waste is bagged, not left on deck.
6. **Inspect after each job.** The crew checks the area and the surrounding surfaces, and the inspection is recorded.

Teak, stainless and interior finishes are protected before any paint work nearby. Paint is not applied to teak, and stainless is not painted unless the owner approves it.

### Records

Each painting job is logged in the maintenance record: area, product and batch, containment used, the inspection result, and the crew member responsible.

### Open decisions

1. Which coating products are approved, for steel and for any other surface. Until that is decided, the store holds no products.
2. The paint store's location on the Tank / Technical level, separated from fuel and battery.

## Paint store ventilation (added on review)

Solvent vapour from paints and thinners is flammable and heavier than air. It collects at floor level, so ventilation that only moves air near the ceiling does nothing for it. The paint store therefore needs its own exhaust, and that exhaust must not connect to any other space.

### Requirements (for review; the standard and figures are to be confirmed by the fire-safety review)

- **Extraction from low down.** Intake at floor level, near where the containers stand, with the exhaust fan drawing continuously while the room is in use and whenever containers are open.
- **Explosion-proof equipment.** Fans, lights, switches and any sensor in the room are rated for flammable atmospheres. A standard fan or switch is an ignition source.
- **Make-up air.** Air comes in through a controlled path, so the room is not left at a negative pressure that pulls air from the adjacent spaces.
- **Dedicated exhaust to a safe outside point.** The outlet is ducted to the outside, sited clear of the outdoor pilot house, the Lido, the sun deck, the tender stowage, and every air intake for the accommodation and the battery room. It does not discharge into a closed space.
- **Vapour detection.** A flammable-vapour detector in the room, with an alarm to the piloting console and the event log, and an interlock that stops the paint store from being opened while the detector is in alarm.
- **Separate from the battery room exhaust.** The battery room's gas-tight exhaust (`docs/energy-management-architecture.md`) and the paint store's extraction are two independent ducts. They never share a duct, fan or outlet.
- **Fire protection.** A fire-rated door, and sprinkler or suppression appropriate to flammable liquids, to be chosen with the fire-safety review.

### Why this matters for the other design rules

- **The IP67 battery room** stays sealed. The paint store's extraction must not open a path into it.
- **The no-PTFE membrane rule** applies to any membrane vent in either room. A sintered metal vent or a simple duct outlet is the approach, not a membrane.
- **Make-up air** into the paint store comes from a path that does not draw from the battery room or from fuel spaces.

### Open decisions

1. The ventilation standard and the air-change figure for the paint store, set by the fire-safety review.
2. Whether the Tank / Technical level has room for a separate exhaust route to the outside, given the battery room and the fuel tanks already claim routes there.
3. The suppression system for flammable liquids in the store.
