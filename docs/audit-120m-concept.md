# Audit: 120 m four-mast concept

Status: audit of the repository as of this branch. Every figure below is measured by a validator or calculated from a file named beside it. Nothing here is a design approval. The concept is provisional and not for construction.

Scope: the 120 m by 20 m hull in `layout/hull.json`, its layout, envelope, sail clearance, stability and heel inputs, weight and energy budgets, ventilation, accessibility, drawings and renders, and the site content.

Companion documents: `docs/gap-analysis-120m.md` (what is missing and why it matters) and `docs/gap-closure-process.md` (how gaps close).

## 1. Measured results

| Area | Check | Result | Source |
|---|---|---|---|
| Hull | LOA, beam, waterline | 120.0 m, 20.0 m, 109.4 m (ratio 0.912) | `layout/hull.json` |
| Layout | Rooms, overlaps, inside outline | 54 rooms, no overlaps, all inside | `npm run validate:layout` |
| Envelope | Area requests fit net free area | 17 of 17 fit | `npm run validate:envelope` |
| Access | Accessibility rules | No gaps against current criteria | `npm run validate:access` |
| Sails | Sweeps and mast feet clear of houses | Pass; side deck 2.30 m minimum | `npm run validate:sails` |
| Sails | Heel at 10, 20, 30 kn | 1.7°, 6.8°, 15.4° (placeholder rig, about 4,000 m²) | `layout/sail-clearance-120m-4mast.json` stability block |
| Sails | Reef points | 15° at about 30 kn; 20° at about 34 kn | same |
| Stability | Roll period at GM 2.13 m | 11.0 s (k = 0.4 B) | `docs/concept-120m-four-mast.md` |
| Weight | Mass register coverage | 0 of 17 items; 0% of 1,487 t | `weights/weight-register.json` |
| Budgets | Reference displacement | 1,487 t, volume 1,451 m³ (derived, not typed) | `scripts/validate-design-budgets.mjs` |
| Budgets | Implied draft | 0.77 m from the uniform outline, against 1.8 m target | same |
| Budgets | Enclosed volume of one deck | 4,412 m³, three times the reference volume | same |
| Energy | Battery-only at 20 kW | 450 t, 30% of displacement (review limit 10%) | same |
| Energy | Battery-only at 50 kW | 1,125 t, 76% of displacement | same |
| Energy | Battery-only at 100 kW | 2,250 t, 151% of displacement | same |
| Ventilation | Outlets with a set position | 14 of 18 have no physical location | `npm run validate:ventilation` |
| Ventilation | Blocking problem | Genset exhaust on or above an occupied outdoor space (pilot-house roof) | same |
| Systems | Systems register | 42 systems across 8 domains; 3 checklists, all draft | `npm run validate:systems` |
| Tests | Unit tests | 51 of 51 pass | `npm test` |
| Build | App type check and build | Pass | `npm run build` |
| Site | Stale figures in scope register | 4 items carry 68 m-era figures | `scope.json` |

## 2. What the audit found

1. **Nothing in the displacement is verified.** The register has 17 items and no masses. The 1,487 t target has no supporting weights, so no stability, keel or draft figure can be checked against it.
2. **The draft cannot yet be shown to work.** The concept assumes a 1.8 m draft at 1,487 t. The layout uses a single outline for every deck, which gives an implied draft of 0.77 m. The model and the draft target disagree until per-deck outlines and a lines plan exist.
3. **Endurance does not close on batteries.** At any review load above 20 kW, battery-only storage exceeds 10% of displacement. The concept relies on fuel and gensets, and that case is not yet recorded as the design basis.
4. **The rig is not designed.** Sail areas are triangle estimates scaled to about 4,000 m². Mast stations, boom lengths and centres of effort are placeholders. The sail clearance result depends on those placeholders.
5. **One blocking ventilation problem.** The genset exhaust outlet is on the pilot-house roof, which is an occupied outdoor space. The register blocks it until the owner reviews the alternative.
6. **Most room geometry is inferred.** Rooms come from a digitised general arrangement, not from dimensions. The new A/V rooms are placed in clear space, but they are not dimensioned on a general arrangement either.
7. **The site still shows 68 m figures.** The register and the masthead were updated, but `scope.json` still carries four stale figures, which the site displays as current.

## 3. What is good

- The hull is one source. Layout, drawings, elevations, CAD and schematics follow `layout/hull.json`.
- The 68 m source layout is kept, and the default hull reproduces it exactly, so the build can be checked against a known state.
- Sail clearances, accessibility and the room layout pass with measured margins.
- The A/V and entertainment rooms are in the layout, the envelope and the render set.
- The budget validator now derives its reference from the register and the draft from the concept, so the old 68 m numbers can no longer drive the checks.

## 4. Limits of this audit

- It checks the repository, not the physical design. A pass means the files agree, not that the design is right.
- Placeholder inputs (Cb, Cwp, Cf, sail areas, loads) drive the calculations. Results move when they change.
- No class society, flag state or yard review has taken place.
