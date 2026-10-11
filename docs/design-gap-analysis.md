# Design gap analysis: the envelope before the deck and length revision

Status: review of the design as it stood before the sixth-deck and envelope revision work. It lists the flaws that matter, with evidence from the repo, a severity and the next action. Nothing here changes the design. It records what the design could not yet support.

## How to read this

- **Critical:** blocks any design decision that depends on it. Stability, keel, endurance and structure all depend on these.
- **High:** a real geometry or compliance gap. It will change the layout once fixed.
- **Medium:** a process or documentation gap that lets the design look more complete than it is.

Counts below come from the repo as of the revision pass: 48 room entries in `layout/decks-layout.json`, 29 of them marked `inferred`, and 71 "To be determined" lines in `systems.json`.

## Critical

### C1. There is no weight register, so the displacement and keel targets are unverified

- **Evidence:** `README.md` gives a reference canoe-body of about 786.3 m³ (around 806 t displaced) and says it is "not a verified lightship or full-load mass". `slides.json` gives keel-up draft targets of 4.8–5.0 m and keel-down targets of 7.2–7.8 m. The next gate in `slides.json` is "reconciled weight register + structure + deck volume".
- **Why it is critical:** the keel draft targets only mean something once the displacement is known. Until the weight register exists, every keel number is a target with no basis.
- **Next action:** build the weight register from the systems list and the room list, then check the draft targets against it.

### C2. The envelope volume does not agree with the reference hull volume

- **Evidence:** each deck uses the same 643.6 m² outline (`layout/decks-layout.json`). At the smallest deck spacing, 2.35 m (Tween to Tank, from `decks.json`), one deck encloses about 1,513 m³. The reference displacement is 786.3 m³. See `docs/archive/68m/envelope-revision.md`, step 10.
- **Why it is critical:** enclosed volume above the waterline does not have to equal displaced volume, so the two numbers need not match. But a single deck at about twice the total displacement means the plan-area model cannot be trusted. Any mass or stability figure built on it would be wrong.
- **Next action:** replace the single outline with per-deck outlines (C3), then recompute the volume and compare it with the reference.

### C3. One outline is used for every deck

- **Evidence:** all five decks in `layout/decks-layout.json` share the same ellipse, 68 m by 12.1 m, giving 643.6 m² each.
- **Why it is critical:** a real hull narrows toward the bow and stern and toward the upper decks. The uniform outline makes the upper and end decks look larger than they can be, which inflates the plan-area budget (`docs/archive/68m/envelope-revision.md`) and the volume.
- **Next action:** draw an outline per deck from the sections and the lines plan. Until then, every area figure is an upper bound.

### C4. Stability and endurance both depend on numbers that do not exist

- **Evidence:** `systems.json` says the 60-day endurance target "has no energy budget yet, so it is unverified", and that battery mass and location "will affect the stability model". Fuel capacity is "not sized against the endurance target" (`systems.json`). `slides.json` says performance and stability are "subject to naval-engineering validation".
- **Why it is critical:** the design makes two targets (60-day endurance and a stable hull) that cannot be checked. The battery and fuel masses feed the weight register (C1) and the stability model, so the gap compounds.
- **Next action:** set an energy budget for the 60-day target, size the fuel, and carry both masses into the weight register.

## High

### H1. The keel and watertight subdivision are not reconciled with the hull

- **Evidence:** `slides.json` says deck elevations, the lifting keel envelope and watertight subdivision "must be reconciled with the 68-meter immersed hull". The only keel geometry in the layout is a rectangle, "Ballast and keel trunk", at x 31–36 m and y ±1.5 m, marked `inferred`.
- **Next action:** take the keel envelope from the lines plan, then check the trunk and the watertight bulkheads against it.

### H2. Most of the room geometry is inferred, not dimensioned

- **Evidence:** 29 of 48 room entries are marked `inferred`. The coordinates were read from the schematic at about 14 px per metre (`layout/decks-layout.json`, `docs/layout-gaps.md`).
- **Why it matters:** `npm run validate:layout` checks overlaps and whether rooms sit inside the outline, but it cannot check real sizes. A passing check says the rooms don't collide. It does not say they fit.
- **Next action:** dimension the rooms from the general arrangement, and mark each room as dimensioned or inferred in the data.

### H3. The roof level is assumed, and the pilot house depends on it

- **Evidence:** `docs/layout-gaps.md` says the roof level (+9.30 m) "is assumed to match the Bridge floor. It is not confirmed on any sheet." The pilot house cover is 2.4 m high, taking the top to +11.70 m. The roof sun deck shares the Aft Lido footprint on Commander (`layout/decks-layout.json`).
- **Next action:** confirm the roof level on a sheet, then check the cover height and the sightlines against the rig.

### H4. Accessibility figures are not checked against the rule

- **Evidence:** `layout/accessibility.json` says the ADA figures are "standard building values" and must be checked against 36 CFR Part 1191 before use. Door widths, thresholds and turning spaces are "not modelled". The accessible cabin interior is "to be specified" (`docs/layout-gaps.md`).
- **Why it matters:** the accessible route and the tender options (pet- and ADA-friendly) both depend on these figures.
- **Next action:** check every figure against the current text, then model the door and turning dimensions in the accessible route.

### H5. The tender reload has no feasible path on the layout

- **Evidence:** the lift car is 1.5 m by 2.0 m internal (`layout/accessibility.json`), too small for a tender. The lift shafts are 3.0 m by 1.9 m each. The Tank level is mostly fuel and water tanks, ballast and pump spaces (`layout/decks-layout.json`). The bay has no geometry, and no starboard launch point or aft hatch is placed. `docs/tender-mag-rail-reload.md` records this as the key open question.
- **Next action:** place the bay and the launch point, then test a rail route through the Tank level. This must come before tender storage is sized.

### H6. Sails and the rig are not in the envelope

- **Evidence:** the mast positions and aft envelope widths are "approximate, read from the sections sheet" (`docs/layout-gaps.md`). The wind model in `src/aggregates/dock.ts` acts on the hull alone, and sails are not modelled as a wind load.
- **Next action:** place the masts from the sail plan, then model the sail windage in the environment model.

## Medium

### M1. The checks can pass on a model that is not dimensioned

- **Evidence:** the validators pass on the current geometry (`npm run validate:layout`, `validate:access`). The roof-exclusion error (`docs/archive/68m/envelope-revision.md`, lessons) was only caught when the numbers were compared with hand figures.
- **Why it matters:** green checks read as completeness. They should be reported as "consistent with the model", not "correct".
- **Next action:** label each check with what it can and cannot prove, as in the revision doc.

### M2. Deck headroom and structure have no analysis

- **Evidence:** the deck spacings, from the elevations in `decks.json`, are 2.70 m (Bridge +9.30 to Commander +6.60), 3.25 m (Commander to Main +3.35), 2.50 m (Main to Tween +0.85) and 2.35 m (Tween to Tank −1.50). None of these is tested against structural depth or service headroom.
- **Next action:** set a structural depth and a clear headroom per deck, then check each spacing against them.

### M3. The systems register is mostly undecided

- **Evidence:** 71 "To be determined" lines in `systems.json`. Four scope items are open (`scope.json`), and the guest app scope is unconfirmed.
- **Next action:** prioritise the systems that carry mass or volume (battery, fuel, HVAC, tenders) first, because they feed the weight register.

### M4. Renders and the brief can disagree

- **Evidence:** render 12 shows a wheel as well as touch screens, which the brief does not specify (`docs/layout-gaps.md`). Renders are AI concept images and are not matched to the geometry.
- **Next action:** treat renders as mood only, and check each one against the brief before it is used in a review.

### M5. Medical and pet accommodation were not in the original brief

- **Evidence:** the medical bay, pet wash, pet suites and the EMS-capable tender appear only in the scope register and the placeholder budget (`scope.json`, `layout/envelope-budget.json`). None is placed on a deck with a clinical or pet-care standard behind it.
- **Next action:** set the standards and the requirements before sizing these spaces.

## Priority order

1. C1, the weight register, since every stability and keel decision depends on it.
2. C3, per-deck outlines, since the volume and area figures depend on them.
3. C4, the endurance budget and fuel sizing, which feed the weight register.
4. H5, the bay and launch point, which gate the tender decisions.
5. H2, dimensioning the inferred rooms.

## What this means

The previous design looked more complete than it was. The layout passed its checks, the room list was detailed, and the scope register was long. But the critical numbers (displacement, stability, endurance, and the keel draft) were never derived from the geometry. Each check was real but narrow, and no check tied the rooms to the weight or the volume of the hull. The envelope revision in `docs/archive/68m/envelope-revision.md` addresses the area question, but it leaves C1 to C4 open. Those four must be closed before the design can make a claim about performance.

## Implementation status

What was implemented in the follow-up pass, and what was not.

| Gap | Status | What exists now | What is still needed |
|---|---|---|---|
| C1 weight register | Structure implemented, no masses | `weights/weight-register.json`, 16 items, all unknown. The validator reports 0% coverage. | Masses from the systems and fit-out schedules. Nothing has been invented. |
| C2 volume vs reference | Checked and flagged | `npm run validate:budgets` shows one deck at about 1,513 m³ against 786.3 m³ | Per-deck outlines (C3) |
| C3 one outline per deck | Not implemented | Flagged through the draft and volume checks | Per-deck outlines from the sections and lines plan. Drawing a tapered shape from guesses would replace one unverified model with another. |
| C4 endurance and fuel | Arithmetic implemented, inputs are placeholders | `weights/energy-budget.json` and the validator. Battery-only requirement: 300 t at 20 kW, 750 t at 50 kW, 1,500 t at 100 kW, against 806 t displacement. | Real hotel loads, supplier battery data, a fuel and genset plan, and solar contribution |
| H5 tender launch and bay | Not implemented | Nothing new placed | The bay and the starboard launch point, from the general arrangement |
| H2 dimensioning | Not implemented | Nothing new dimensioned | Dimensioned general arrangement |

### Main finding from the implementation

A battery-only 60-day endurance does not close at any of the placeholder loads. At 20 kW average the battery alone is 22% of the reference displacement. This is arithmetic on stated assumptions, not a design result. But it means the 60-day target is probably not achievable on batteries alone, and the design needs either a different energy source for the endurance case, or a different target. This decision belongs to the owner before any more energy design is done.

### Checks

- `npm run validate:budgets`: structure OK, six flags raised. Flags are findings, not data errors, and they do not fail the run.
- The other validators (`validate:layout`, `validate:access`, `validate:systems`, `validate:envelope`) are unaffected.

## Endurance refinement

The battery-only result above is now compared with a diesel genset option, using the same energy.

| Average load | Battery-only mass | Diesel fuel mass (genset, 35% efficiency) |
|---|---|---|
| 20 kW | 300 t | 6.9 t |
| 50 kW | 450 t | 17.3 t |
| 100 kW | 900 t | 34.6 t |

Diesel is about 43 times lighter than battery at 20 kW (at 0.12 kWh/kg; the earlier 26 times used 0.2 kWh/kg and is superseded). That ratio is not a design choice, it follows from the energy density of the two options. The 60-day target is therefore a question of energy source before it is a question of hull mass.

What the fuel option needs, at 20 kW:
- About 8.1 m³ of diesel at 0.85 t/m³. Fuel tank volume, not mass, is the constraint on the Tank / Technical level.
- A genset, mass and model not yet chosen (`diesel-generation`, a Kohler candidate).
- Fuel stowage and fire separation, which the fuel-processing system must address.

Caveats:
- The hotel loads are placeholders. A real load profile is the first input the endurance budget needs.
- Battery figures use assumed specific energy and depth of discharge. Fuel figures use a standard heating value and an assumed genset efficiency. Each is marked for verification.
- Solar, which is a roof candidate, is not counted. It reduces the fuel or battery requirement but does not remove it for a 60-day case without a load study.
