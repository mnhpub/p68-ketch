# Accommodation considerations: medical bay, tenders

Status: open. Nothing here is designed, placed or approved. The three items are in `scope.json` as `open`, with no room placement. This note lists the questions each space raises and the constraints already recorded in the repo.

## Constraints already in the repo

- **Lifts:** mag-rail lifts A and B. Lift B serves Bridge, Commander / Lido, Main / Master, Tween and Tank / Technical. Lift A does not reach Tween or Tank. Lift car internal size is 1.5 m by 2.0 m, still to be designed (`layout/accessibility.json`).
- **Accessible route:** minimum route width 0.915 m, door clear width 0.815 m, turning space 1.525 m. These are standard building figures, not yet checked against 36 CFR Part 1191.
- **Guest-facing areas:** ADA applies to guest-facing areas (`layout/accessibility.json`). Whether the medical bay is guest-facing is not decided.
- **Tank / Technical:** holds fuel and water tanks, wastewater and bilges, and the pump and manifold spaces. Fuel and battery arrangements sit here or nearby (`battery-storage`, `fuel-processing` in `systems.json`).
- **Bay:** the dinner-for-two experience is recorded as "Bay (tender support open)" in `scope.json`. The bay and the tenders must be planned together.

## Medical bay

- **Location:** Tween is the candidate, near lift B and the accessible route. Lift B is the only lift to Tween from the bridge decks, so a medical evacuation depends on it.
- **Evacuation:** a stretcher must reach the lift car and the outside. Check the car size against a stretcher and attendant.
- **Scope:** treatment room, equipment and medicine storage, oxygen, and waste disposal. None of these are chosen. Clinical standards depend on the flag state and the classification society.
- **Power and ventilation:** medical equipment needs a supply that the 600 V bus and battery arrangements can carry. Ventilation is part of HVAC, which is not yet placed.
- **Access rules:** who may enter, and whether it is guest-facing, sets the accessibility requirements.

## Starboard tender service

- **Tenders:** two. Size, weight, hull type and launch method are not set.
- **Side:** starboard, at the bay. The launch and recovery area must be clear of the bay dinner and the outdoor areas.
- **Method:** davit, crane or side launch. Each sets a load path that the structure has to take. None is designed.
- **Sea state:** launch and recovery limits depend on the sea conditions. These are the same sea and wind inputs the auto-dock environment model uses, but they are not tied to any launch limit yet.
- **Safety:** launch and recovery need a crew, a briefing and a lifeline. The piloting console has no tender control.

## Internal tender storage

- **Location:** Tank / Technical is the candidate, with access from the bay. Internal stowage avoids a deck davit, but it takes floor area on the lowest deck.
- **Access:** the route from the bay to Tank / Technical has to be checked for tender size and for the technical access corridor.
- **Fuel and batteries:** outboard fuel or electric batteries on board need ventilation, fire detection and separation from the stores. These links are to `fuel-processing` and `battery-storage`, and nothing is designed yet.
- **Wet stowage:** drainage to the wastewater and bilges, and the effect on the ballast and keel trunk, need checking.

## Open decisions

1. Medical bay: guest-facing or crew-only? This sets the accessibility rules.
2. Medical bay: which deck, and does lift B's capacity suffice for evacuation?
3. Tenders: size, weight and type, so the davit or crane and the storage can be sized.
4. Tenders: launch at the bay, or stowed in Tank / Technical with a route to the bay?
5. Tenders and bay: how the bay dinner-for-two uses the tender support.
