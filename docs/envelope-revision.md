# Envelope revision: plan-area budget from first principles

Status: working revision, not a design. Every number here is either read from the layout data or is a labelled placeholder. The checks are rerun by `npm run validate:envelope`. The steps below start from the hull outline and build up one at a time, so each figure can be traced back.

## Step 1: The hull outline

The hull plan is an ellipse 68 m long and 12.1 m wide.

- Semi-axes: a = 68 / 2 = 34 m, b = 12.1 / 2 = 6.05 m
- Ellipse area: π × a × b = π × 34 × 6.05 = **646.2 m²**

## Step 2: Check the polygon

The layout stores each deck outline as a 40-point polygon, not an exact ellipse. Its area is worked out with the shoelace formula, which sums the cross-products of consecutive vertices and halves the result.

- Polygon area (shoelace): **643.6 m²**
- Difference from the exact ellipse: 646.2 − 643.6 = 2.6 m², or 0.41%

The polygon runs slightly inside the ellipse, so it gives a small underestimate. That is acceptable for a budget, and it is conservative.

## Step 3: Gross area per deck

Every deck uses the same outline, so each deck has the same gross plan area.

- Gross per deck: 643.6 m²
- Five decks: 5 × 643.6 = **3218 m²** of gross plan area in total

Caveat, to revisit: a real hull narrows toward the bow, the stern and the upper decks. Using one outline for every level overstates the area on the upper decks and the ends. This is the most important modelling issue in the layout, and it is a flag, not a fix.

## Step 4: Claimed area per deck

Each room is a rectangle `[x0, y0, x1, y1]`, so its area is (x1 − x0) × (y1 − y0). Duplicate rectangles are counted once. Rooms named `Roof:` are excluded, because they are the outdoor roof area, which sits above the hull plan and shares the Aft Lido footprint. Roof access passages are interior and are counted.

| Deck | Claimed (m²) |
|---|---|
| Bridge | 192.8 |
| Commander / Lido | 279.0 |
| Main / Master | 332.9 |
| Tween | 310.4 |
| Tank / Technical | 253.6 |

Spot check, Tank / Technical: fuel/water tanks 71.9 + 45.2 = 117.1; ballast trunk 15.0; pump spaces 8.5; wastewater 55.2; technical corridor 44.0 + 8.1 = 52.1; lift B 5.7. Sum: 117.1 + 15.0 + 8.5 + 55.2 + 52.1 + 5.7 = **253.6 m²**. This matches.

## Step 5: Available area

Available = gross − claimed.

| Deck | Available (m²) |
|---|---|
| Bridge | 643.6 − 192.8 = 450.8 |
| Commander / Lido | 643.6 − 279.0 = 364.6 |
| Main / Master | 643.6 − 332.9 = 310.7 |
| Tween | 643.6 − 310.4 = 333.2 |
| Tank / Technical | 643.6 − 253.6 = 390.0 |

## Step 6: Net free area

Net free = available × (1 − allowance). The allowance covers circulation, structure and services. It is a **placeholder of 30%**, not derived from any study.

- Bridge: 450.8 × 0.70 = 315.6
- Commander / Lido: 364.6 × 0.70 = 255.2
- Main / Master: 310.7 × 0.70 = 217.5
- Tween: 333.2 × 0.70 = 233.2
- Tank / Technical: 390.0 × 0.70 = 273.0

## Step 7: Requests

The placeholder requests in `layout/envelope-budget.json`, by deck:

| Deck | Requests | Sum (m²) |
|---|---|---|
| Commander / Lido | pet-friendly lounge 15 | 15 |
| Tween | medical bay 20 + pet resort suites 28 + crew wellness 12 | 60 |
| Tank / Technical | medical tender store 6 + tender storage 42 + pet wash 8 | 56 |
| Bridge, Main | none | 0 |

Total requested: 15 + 60 + 56 = **131 m²**.

## Step 8: Fit and left over

Left = net free − requested.

| Deck | Net free | Requested | Left |
|---|---|---|---|
| Bridge | 315.6 | 0 | 315.6 |
| Commander / Lido | 255.2 | 15 | 240.2 |
| Main / Master | 217.5 | 0 | 217.5 |
| Tween | 233.2 | 60 | 173.2 |
| Tank / Technical | 273.0 | 56 | 217.0 |

Every deck fits. The validator prints the same figures, with small rounding differences.

## Step 9: How sensitive is this to the placeholder allowance?

Break-even allowance is the allowance at which the requests just fill the net free area. Solve for it: requested = (available) × (1 − allowance), so allowance = 1 − requested / available.

| Deck | Requested | Available | Break-even allowance |
|---|---|---|---|
| Commander / Lido | 15 | 364.6 | 1 − 15/364.6 = 95.9% |
| Tween | 60 | 333.2 | 1 − 60/333.2 = 82.0% |
| Tank / Technical | 56 | 390.0 | 1 − 56/390.0 = 85.6% |

The tightest deck is Tween, and it only fails if the allowance reaches 82%. The fit holds across any realistic allowance. The result does not depend on the 30% placeholder.

## Step 10: Sanity check on the volume

Area alone does not say the envelope is right. The layout also needs height, so this check uses the deck spacing from `decks.json`.

- Deck heights: Bridge +9.30, Commander +6.60, Main +3.35, Tween +0.85, Tank −1.50 m
- Smallest spacing: Tween to Tank, 0.85 − (−1.50) = 2.35 m
- Enclosed volume of one deck at the smallest spacing: 643.6 × 2.35 = 1512.5, reported as **1,513 m³** by `npm run validate:envelope` and `validate:budgets`

The README gives a reference canoe-body volume of **786.3 m³** (displacement, about 806 t). These are different quantities: enclosed volume above the waterline is not the same as displaced volume. The gap is still large. One deck's enclosed volume is about twice the whole reference displacement. That says either the plan-area model is too generous for the upper decks, or the canoe-body reference is too small for five decks. Either way, it has to be resolved before the envelope is trusted.

## What the math says

1. On this layout, plan area is not the constraint. Every deck fits the requests with room to spare, and the result holds up to an allowance of about 82%.
2. The surplus is partly an artefact. One identical outline on every deck inflates the upper and end decks, and the volume check suggests the envelope is generous.
3. The real constraints lie elsewhere: stability, weight, keel draft, and vertical access. Those are where the revision work should go next.

## Next steps

- Replace the single outline with per-deck outlines that narrow with height. This removes the artefact in point 2.
- Carry each request's mass through to the weight register once the weight register exists.
- Re-check the tender and medical decisions in `docs/accommodation-considerations.md` against the revised plan areas.

## Lessons learned

These come from this revision pass. Each one changed a number or a decision, so they are recorded for the next pass.

1. **Filter by geometry, not by name alone.** The first version of the validator excluded every room whose name started with "Roof". That removed the two Bridge "Roof access passage" rectangles, which are interior passages inside the hull plan. The Bridge claimed area came out at 131.2 m² instead of 192.8 m². Checking the coordinates showed that only the outdoor "Roof:" area sits above the hull plan. The exclusion now matches `Roof:` exactly. Lesson: before excluding a category, check where its members sit.

2. **Compute from the data, then compare with hand figures.** The hand totals for the five decks were written before the script ran. The script's Bridge figure disagreed with the hand figure, and that disagreement is what exposed the roof error. Lesson: run the check on the data first, then reconcile any difference, rather than trusting either side alone.

3. **Verify the foundation numbers.** The polygon area (643.6 m²) and the exact ellipse area (646.2 m²) differ by 0.41%. That is small, but it is worth stating so the budget can be traced. Lesson: state the approximation and its size, rather than hiding it inside a total.

4. **Sensitivity to placeholders matters more than the placeholder value.** The 30% allowance is invented. Computing the break-even allowance per deck (82% for Tween, the tightest) shows the conclusion does not depend on it. Lesson: when an input is a placeholder, test how far it can move before the conclusion changes.

5. **A tidy result can hide a bad model.** The budget fits with room to spare, but that comes from giving every deck the same outline. The volume check (one deck at about 1,513 m³ against a 786.3 m³ reference) shows the model is generous. Lesson: a passing check on a simplified model says less than it appears to. Test the model's assumptions as well as the arithmetic.

6. **Re-read shared files before editing.** `scripts/validate-envelope.mjs` and other files changed on disk during this pass. The changes were consistent with the intended edits, so they were kept, but the risk is real. Lesson: re-read a file before editing it when other changes may have landed.

7. **Keep temporary files in the scratchpad.** Earlier in the session a validator run wrote its output to `/tmp`, which the environment guidance says to avoid unless asked. It had no effect on the repo, but it should not be repeated.

8. **Ask what "the envelope" covers before revising it.** The request covered plan area, volume, and the new pet and tender needs. The area budget answers only part of that. Lesson: name which dimension a revision addresses, and what it leaves for later. The next steps above cover what is still open.
