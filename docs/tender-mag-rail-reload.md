# Mag-rail tender deployment and reload: concept

Status: concept, not designed. Nothing here is sized, approved or placed on a deck. Tender dimensions and mass are not set. Companion to `docs/accommodation-considerations.md`.

## What the reload does

Two tenders, one in service and one in storage. A **reload** swaps them: the tender in the water is recovered, returned to storage, and the second tender is brought to the launch point and lowered. A mag-rail carriage moves each tender along a fixed track between storage and the starboard launch point.

## Why the passenger lift can't do it

- Lift car internal size is 1.5 m by 2.0 m (`layout/accessibility.json`). A tender won't fit inside.
- Lift B serves Tank / Technical (`layout/decks-layout.json`, shaft at x 48–51 m, centreline). It can carry people and stores, not tenders.
- A dedicated tender lift needs its own shaft. The existing lift shafts are 3.0 m by 1.9 m each, side by side, and are too small.

So the reload path must be a horizontal rail on Tank / Technical, with a separate transfer to the launch point.

## Layout constraints (from the schematic)

Coordinates are metres. x runs from the stern (0) to the bow (68). y runs from port (negative) to starboard (positive).

| Space | Position | Relevance |
|---|---|---|
| Fuel / water tanks | x 8–30, both sides | Occupy most of the aft Tank level. No clear run here. |
| Ballast and keel trunk | x 31–36, centre (y ±1.5) | Central obstruction. |
| Pump / manifold spaces | x 31–36, starboard (y 1.5–3.2) | Starboard obstruction at the same x. |
| Wastewater / bilges | x 38–48 | Aft-of-lift floor area. |
| Technical access corridor | x 48–51 (y −2.7 to 0) and x 51–59 (y ±2.8) | The only wide, open run on this level. Forward of the lifts. |
| Lift B shaft | x 48–51, y 0 to 1.9 | Starboard shaft. |

Problem: the open run on Tank / Technical is forward of the lifts (x 51–59). The starboard launch point is not placed anywhere on the layout. The bay (named in `scope.json`) has no geometry. Any route from storage to the launch point must cross the obstructions above or pass through a hatch that is not yet located.

## Options

1. **Tank-level rail to an aft starboard hatch.** Storage sits in the open run. The rail runs aft, clear of the tanks, to a hatch in the hull at the bay. The route cuts through the fuel tank block, so it needs a clear corridor the layout doesn't yet provide.
2. **Tank-level rail forward to a tender lift at the bow end.** A separate tender lift shaft is needed, and the bay is aft. This moves the problem rather than solving it.
3. **Stowage on deck with davit only.** No rail. Storage moves to the bay itself, which removes the reload. Only viable if the bay has room.

Recommended for review: option 1, if the aft hatch is possible. It needs the bay and the aft starboard hull geometry before it can be sized.

## Reload sequence (concept)

| State | Meaning | Exit condition |
|---|---|---|
| Stowed | Tender in storage cradle, rail locked | Operator requests deploy |
| Released | Cradle unlocked, tender on the rail | Carriage reaches the launch point |
| At launch | Carriage at starboard transfer point | Davit or crane takes the load |
| Launched | Tender in the water, tethered | Recovery requested |
| Recovering | Tender lifted back to the transfer point | Carriage returns to stowage |

Each step is a hold on the helm side, as with sails and dock mode. Two-station confirmation is needed for the launch and the recovery. Either station can stop the carriage, which mirrors the stowing rule for sails.

## Interlocks

- **No movement while underway or in dock mode.** The vessel's motion would add to the load on the rail and davit. Both states already exist in the piloting aggregate.
- **Sea state limit.** Launch and recovery are blocked above a wave height and wind limit. The inputs already exist in the piloting environment (`headingDeg`, `windKn`, `waveM`). The limits are not set.
- **Emergency stop.** The hardwired emergency stop must halt the carriage without the screen (`docs/piloting-console.md`). The carriage stops in place and the davit holds the load.
- **Person in the path.** Presence sensors on the track and at the transfer point. The rail does not move while a person is detected. The sensors are not chosen.
- **Manual recovery.** A hand crank or local control to move the carriage if the drive fails. Manual operation needs a clear rule about who may use it.

## Hazards to review

- **Battery and fuel near the rail.** Tenders with batteries or fuel are stored in Tank / Technical, next to the fuel tank block (`battery-storage`, `fuel-processing`). Ventilation and fire detection come first.
- **Load path.** The carriage, track, and hull fixings take the tender's weight and the vessel's motion. None of these loads are calculated.
- **Hull opening.** An aft starboard hatch is a hull penetration. Its watertight design belongs to the structure review, not this note.

## Open questions

1. Tender size, mass and type. These drive the carriage, the track, and whether one or two tenders share a carriage.
2. Starboard launch point: where is it on the hull, and is there room for an aft hatch?
3. Is there an aft corridor through the fuel tank block, or must the storage move?
4. Which launch method: davit, crane, or side launch?
5. Who may operate the reload, and from which station?
6. Sea state limits for launch and recovery, and who sets them.
