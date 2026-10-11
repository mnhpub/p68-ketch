# Gap analysis: 120 m four-mast concept

Status: current gap analysis. It supersedes the 68 m gap list in `docs/design-gap-analysis.md` for this concept. The old IDs (C1 to C4, H1 to H6, M1 to M5) are kept in the register so the history is traceable.

The live register is `layout/gap-closure.json`. Its status is produced by `npm run validate:gaps`, not typed in. See `docs/gap-closure-process.md` for how a gap closes.

## Gaps, ordered by what they block

| ID | Severity | Gap | Old ID | Blocks | Closes when |
|---|---|---|---|---|---|
| G01 | Critical | No masses in the weight register; 1,487 t not covered | C1 | Stability, keel, draft, endurance | Register covers at least 95% of 1,487 t, from supplier and schedule data |
| G02 | Critical | Reference displacement and draft were not one set of numbers | C2 | Every budget check | Reference, draft and stability block agree; budget draft flag cleared |
| G03 | Critical | One outline for every deck; no lines plan or waterplane | C3 | Draft, volume, deck areas | Lines plan with Cb and Cwp; per-deck outlines replace the single ellipse |
| G04 | Critical | KG not calculated; no GZ curve or heel limit | C4 | Roll, heel and safety case | KG below the limit for GM 2.13 m; GZ curve checked against rules |
| G05 | Critical | Battery-only endurance fails above 20 kW | C4 | Energy design basis | Real loads in; battery share under review limit, or fuel and genset case recorded |
| G06 | High | Keel and watertight subdivision not reconciled | H1 | Draft and ballast | Keel position for 1.8 m draft; subdivision on lines plan |
| G07 | High | Most room geometry inferred, not dimensioned | H2 | Layout accuracy | Dimensioned general arrangement; layout regenerated from it |
| G08 | High | Roof level assumed; pilot house depends on it | H3 | Pilot house, cover height | Roof level confirmed on a sheet |
| G09 | High | Accessibility checks pass on current criteria | H4 | Nothing new | Closed (automated) |
| G10 | High | Tender launch point and bay not placed | H5 | Tender operations | Bay and launch point on the general arrangement |
| G11 | High | Sail plan missing; clearances use placeholder rig | H6 | Sail clearance and heel | Real sail plan; clearance uses the hull's LOA and beam; check passes |
| G12 | High | Genset exhaust blocked on the pilot-house roof | n/a | Power plant venting | Owner review of the alternative; no blocking register problem |
| G13 | Medium | Systems register mostly undecided | M3 | Fit-out and systems design | Each system decided or named as an open gate |
| G14 | Medium | New A/V rooms have no interior renders | M4 | Renders matching the brief | Interior render for each new room; formal chain rerun |
| G15 | Medium | Medical and pet accommodation placed on Tween; deck decision open | M5 | Accommodation | Requests on Tween (checked); pet suites deck recorded |
| G16 | Medium | Site scope register carries 68 m-era figures | n/a | Public statements | No stale figures in `scope.json` |
| G17 | Medium | Deck structure and headroom not analysed | M2 | Structure, mast foundations | Structural analysis of decks, masts and roof loads |

## What is not in the register

- Class society and flag state rules: no review has taken place. Add a gap when a rule set is named.
- Propulsion power: still undefined (old open item 7). It blocks bus cable sizing and the energy design. Add as G18 when the power is set.
- Crew and guest numbers: still undefined (old open item 8). They drive water, provisioning and cabin figures.

## Priority

1. G01 (masses). Every other stability and draft check depends on it.
2. G03 (per-deck outlines). Volume and deck area checks depend on it.
3. G05 (endurance basis) and G12 (exhaust route). Both change the power plant and the roof.
4. G11 (sail plan). It replaces the rig placeholder that the clearance and heel results use.
5. G07 and G08 (dimensioning and roof level). They sharpen the layout the rest depends on.
