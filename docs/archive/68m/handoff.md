# Handoff: P68 design, for continuing in a cloud session

Branch: `design-revision-p68-13m`. Public site last deployed from this branch before the latest changes. Nothing in this handoff is deployed.

## Done
- Size: 68 m LOA, 62 m waterline, 13.0 m beam; displacement target 1,487 t at the 4.8 m keel-up draft (ADR-0001).
- Outlines regenerated at 68 by 13.0 m; layout, access and envelope checks pass.
- Energy: 90-day endurance (ADR-0005); LFP rackmount buffer, option B (ADR-0004); 800 V bus basis (ADR-0002); powerplant energy-only (ADR-0003).
- Materials policy, venting rules, water (produced onboard), circulation (ADR-0006 to ADR-0009).
- Provisioning: frozen and dry stores, chilled produce, wine cellar, cheese zone, dry grains (docs/provisioning-food-storage.md).
- Schematics: DXF and PDF sheets in drawings/schematics/; feature diagrams in drawings/features/; underway heel section in drawings/previews/.
- ADR set in docs/adr/ with open gates.
- Tests (51) and type check pass.

## Open
1. App: register and systems text still say 60 days in places (src/App.tsx register metric; systems.json battery, waste and food entries). Change to 90 days; provisioning period needs owner decision.
2. App: Deck explorer and drawings tab do not show candidate spaces, the feature diagrams or the schedule of candidate areas.
3. App: redeploy the public Worker once items 1 and 2 are done (wrangler, from the branch). Needs owner go-ahead.
4. Gap analysis of discussed items against scope, envelope and drawings (not yet written as a document).
5. Schedule sheet of candidate areas for the schematic set.
6. Photoreal renderings deferred until an image-generation tool is available (ADR-0010).
7. Propulsion power (blocks bus cable sizing and ADR-0002).
8. Crew and guest counts (blocks water, provisioning and cabin figures).

## Commands
- Tests: `npm test`
- Checks: `npm run validate:layout`, `validate:access`, `validate:envelope`, `validate:budgets`, `validate:systems`, `validate:ventilation` (one expected failure: pilot-house genset outlet, blocked pending owner review).
- Build public: `npm run build:public`
- Schematics: `python3 scripts/build-schematics.py`, `build-circulation.py`, `build-feature-diagrams.py`, `build-underway-preview.py` (need a virtual environment with matplotlib and ezdxf).
