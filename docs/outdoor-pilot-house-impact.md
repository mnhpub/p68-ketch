# Outdoor pilot house on the Commander roof: engineering impact (concept)

Status: concept. The repo has no design model, mass register or stability calculation, so the items below are a
checklist, not a confirmation.

## Decision

The outdoor pilot house is a cover over the aft roof of the Commander level, above the Lido. The same open roof is a
sun deck and an area for games and events. It is not a new hull, deck or volume below the waterline.

## Short answer

- **Hull geometry and hull-volume figures do not change.** Length overall (68.0 m), waterline length (62.0 m),
  beam (12.1 m) and the canoe-body volume (786.3 m³) describe the hull below the waterline. A roof structure above
  the Commander level does not alter them.
- **The vessel's behaviour does change.** Topside mass raises the centre of gravity, adds windage, and increases
  draft. A roof crowd adds a variable load. The repo has no stability (GZ) curve or mass balance, so none of these
  can be confirmed here.

## Impact by parameter

| Parameter | Value in repo | Effect of this decision | Status |
|---|---|---|---|
| Length overall | 68.0 m | None if the roof stays within the hull. Check for any overhang past the transom. | Geometry check needed |
| Waterline length | 62.0 m | None | Unchanged |
| Beam | 12.1 m | None unless the roof overhangs the sides | Geometry check needed |
| Canoe-body volume | 786.3 m³ | None. This is hull volume below the waterline. | Unchanged |
| Displacement | ~806 t (seawater, from hull volume) | This is a hull-volume figure, not a mass. Actual displacement is lightship plus load, and the vessel sits deeper with added weight. | Recalculate with a mass register |
| Draft targets | Keel-up 4.8–5.0 m; keel-down 7.2–7.8 m | Will increase with added topside weight | Re-run hydrostatics |
| Centre of gravity (KG) and GM | Not calculated | KG rises with roof mass, so GM falls | Needs a stability calculation |
| Windage | Not calculated | Projected area above the waterline increases. This raises heel in wind and affects sail performance. | Needs wind-heel calculation |
| Air draft | Not in repo | Waterline to top of the cover is a new height | Set the height; check against routes and clearances |
| Roof deck structure | Not in repo | New live load for guests, games and events; the deck must be supported on the Commander structure | Structural design and live-load case |
| Mizzen interface | Slides: "aft deck structure and mizzen interface unresolved" | The roof adds weight at the same aft location | Resolve together |
| Lido pool | Slides: pool mass and free surface "to be engineered" | Roof events add to the aft load. A combined aft load case is needed. | Include in mass register |
| Access and escape | Not in repo | Roof needs stairs or lift access, guard rails, and a second escape route | Design |

## Illustrative magnitude (assumption, not design)

100 people at 80 kg is about 8 t on the roof. Against the 806 t hull-volume figure that is about 1%, but it sits aloft,
so its effect on stability is larger than its size suggests. The height of the roof is not yet set, so its effect on
KG cannot be calculated.

## Changes made to the repo

- `decks.json`: Commander / Lido gains the room "Roof: outdoor pilot house and sun deck (events)", and its access
  note now says roof access is to be designed.
- `systems.json`: navigation and command-and-control now list Commander / Lido as a related deck.
- `docs/piloting-console.md`: the outdoor pilot house location is updated.
- Hull values in `README.md`, `slides.json` and the design register are unchanged, because this decision does not
  alter them.

## Checklist before design freeze

1. **Design model.** Confirm the roof sits within the length and beam, or record any overhang.
2. **Mass register.** Include roof structure, cover, equipment, finishes, furniture, pool and event loads, each with
   a KG value.
3. **Hydrostatics.** Re-run draft, freeboard, displacement and KG for each loading condition, including the
   keel-up and keel-down cases already in the slides.
4. **Stability.** Calculate GZ with wind heel and a crowd-movement case on the roof. Review against the applicable
   stability rules with the classification society.
5. **Structure.** Design the roof deck and its supports, and check the interaction with the mizzen foundation.
6. **Air draft and sightlines.** Set the cover height, check it against routes and clearances, and check forward and
   aft visibility against the rig.
7. **Occupancy and safety.** Set a maximum roof occupancy for events. Define guard-rail height, fall protection,
   escape routes and weather protection.
8. **Engineering sign-off.** A naval architect and the classification society review items 2–5 before the roof
   layout is fixed.
