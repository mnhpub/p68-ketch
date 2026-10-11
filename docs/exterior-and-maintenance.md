# Exterior durability, stowage, and maintenance workshop

Status: design intent and requirements for review. No material, supplier or room is chosen. Areas are placeholders in `layout/envelope-budget.json`, checked by `npm run validate:envelope`.

## Design intent

The owner's brief for the exterior and the workshop is resilience over replacement. Anything outside should last a long time, and anything that does wear should be quick to repair on board. Furniture, tableware and soft goods that are not fixed down are stowed, and stowage must be easy to reach and easy to maintain. The workshop and stores are designed for the vessel to keep itself running far from a shipyard.

## Exterior surfaces

### Decking

- **Teak** is the traditional choice for a yacht deck. It is durable and comfortable underfoot, but it needs maintenance (oiling, cleaning, periodic sanding), and natural teak needs certified sourcing. An engineered synthetic decking is the alternative: lower maintenance, a stable colour, and no sourcing question. Both are candidates. The choice is a design decision, not made here.
- Whichever is chosen, the deck needs drainage to the scuppers, slip resistance in wet conditions, and a plan for replacing boards without lifting the whole deck.

### Metal fittings and hardware

- **Marine-grade stainless steel (316 or better) or titanium** for rails, cleats, hinges, fixings and furniture frames. These resist salt corrosion without a coating that can fail.
- **Chrome plating is a caution.** On marine fittings, a plating layer can crack or lift and expose the base metal underneath, and it can cost more to repair than to replace. The owner's preference for chrome is noted, and the case for a solid stainless or titanium finish should be made against it, not assumed. Plating chemistry is also a regulated question for some waters and yards.
- Use dissimilar-metal isolation between fittings and the hull and structure to limit galvanic corrosion.

### Outdoor furniture

- Frames in stainless steel or aluminium with a marine-grade finish, and marine-grade UV-stable fabric for cushions.
- Cushions are removable, with a stated replacement spare set stored on board (see Soft goods below).
- Designs that can be stowed flat or stacked, with quick-release tie-down points on the deck for storm stowage.

## Stowage

Items that are not fixed down are stowed, and every stowage place has a plan.

| Item | Stowage | Access |
|---|---|---|
| Deck chairs, loungers | Dedicated lockers on the Lido and sun deck, or a deck store | Within reach of the outdoor deck, no lift required |
| Tables | Stowed flat in a deck store, or fixed | Same as chairs |
| Cushions and soft goods | Dry store, on the accommodation deck | Via lift B, with a route for a full cushion set |
| Tableware, glassware | Locked, padded, dry storage near the galley | Galley access; secured against motion |
| Spare cushions, fabric and upholstery stock | Dry store with humidity control | Near the upholstery repair room |

Stowage must hold items against vessel motion. Lockers and racks need restraint, and the restraint loads are not yet calculated.

Lift car internal size is 1.5 m by 2.0 m (`layout/accessibility.json`). A chair or table can go in the car, but a full set of cushions or a large table top may need a separate cargo route.

## Maintenance workshop and stores

The workshop serves the vessel's systems, so its location follows the systems it supports.

| Workshop or store | Systems served | Location (candidate) | Placeholder area |
|---|---|---|---|
| Mechanical maintenance | Engines, gensets, water-makers, pumps | Tank / Technical | 24 m² |
| Electrical maintenance | Battery bank, converters, electrical distribution | Tank / Technical, separated from the battery room | Within the mechanical workshop, to be split |
| Water and waste maintenance | Water-makers, waste processing, wastewater | Tank / Technical, next to the wastewater space | Within the mechanical workshop |
| Fuel maintenance | Fuel storage and processing | Tank / Technical, separated from fuel and battery | Within the mechanical workshop |
| Upholstery and soft-goods repair | Cushions, fabric, sewing and repair | Tween, next to the workshop and storage | 12 m² |
| Dry stores: spares, tableware, glassware, furniture | All of the above, and the guest areas | Tween and Tank / Technical | 16 m² (Tween) |

The Tween workshop and storage (24 m², existing in the layout) is kept as the general workshop for the accommodation deck. The Tank / Technical mechanical workshop is a new request, because engine, fuel, water and waste work must not share a room with the stores.

Hazards to keep apart: fuel and oil storage, battery charging, and solvents or adhesives used for upholstery. Each needs its own room, ventilation and fire protection.

## Spares and consumables

- **Engine and generator spares**: filters, belts, seals and fluids for the planned service intervals, held on board.
- **Electrical spares**: fuses, contactors and cable terminations for the distribution and the battery racks.
- **Water and waste spares**: membranes, pump seals and filters for the water-makers and waste processing.
- **Soft goods**: a full spare set of cushions, and spare fabric and thread for repairs.
- **Tableware and glassware**: a breakage allowance, stored in the dry store.

The quantities need a service schedule from each system's supplier before they are set. This note does not set them.

## Crew checklists and maintenance records

The crew needs checklists for maintenance and for daily operation. The safety register (`checklists.json`) holds the safety procedures. The piloting checklists (`src/aggregates/underway.ts`) hold the departure and approach procedures, and they are draft.

A maintenance checklist and record system is a separate body of work. It needs:
- A way to tick off tasks by station, crew member and time, with the record kept.
- Links from each task to the system and the spares it uses.
- A mobile version for use in the workshop and on deck. Whether that is a native iOS app or a web app is a decision not yet made.

The control side of any crew system is the separate work described in `docs/control-software-architecture.md`. Checklist content and records can be developed on the public side, but no maintenance system connects to vessel control.

## Requirements to test

1. Every stowed item has a named place, a restraint method, and an access route.
2. Every workshop has a named system it serves, and any hazards in it are separated.
3. Every spare has a named system, a service interval and a stock quantity once the supplier gives one.
4. Exterior materials are chosen against salt and UV exposure, with a documented replacement interval.

## Open questions

1. Teak or synthetic decking, and if teak, which sourcing standard.
2. Stainless or titanium for fittings, or a coated alternative, with the chrome question resolved.
3. Furniture stowage: the number of pieces and the lockers on the Lido and sun deck.
4. Spares quantities, once service intervals are known.
5. Native iOS or web app for the crew checklists and maintenance records.
