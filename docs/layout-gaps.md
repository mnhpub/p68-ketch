# Layout and drawing gaps

Status: working register, 10 Oct 2026. Items are closed (fixed and checked), resolved (decided, recorded in `layout/accessibility.json` under `decisions`), or open (needs a source, verification, or a design decision not yet made).

## Closed

| Item | How it was closed | Check |
|---|---|---|
| Bridge lift access went through the command position | Two lift lobbies, port and starboard, beside the command position | `npm run validate:access` |
| Commander lift access ran through the lookout | Dedicated Commander lift lobby beside the shafts | `npm run validate:access` |
| Main lift reached through the owner's passage | Public Main lift lobby off the salon passage | `npm run validate:access` |
| Tween had no lift stop | Lift B serves all decks, including Tween | `npm run validate:access` |
| Accessible cabin not on a lift-served level | Accessible cabin on Tween, opposite lift B, with a lobby | `npm run validate:access` |
| Access checker passed a lift with no lobby | Checker tests each lift and the accessible cabin for an adjacent route room | Removing the bridge lobbies produces two gaps |
| Layout overlaps and out-of-hull rooms | Layout validator | `npm run validate:layout` |
| Roof access had no route | Roof access passage on the Bridge, linked to lift A's lobby | `npm run validate:access` (roof check) |
| Lift shafts unchecked against the car | Shaft width checked against the car width and the ADA minimum | `npm run validate:access` (lift check) |

## Resolved (decisions recorded)

| Decision | Resolution | Basis |
|---|---|---|
| Owner suite size | Extended aft to the bow block, about 7 m by 6.5 m | The 5 m block was too small |
| Roof access | Lift A Bridge stop plus a Bridge-level roof access passage | A ramp for a 2.7 m rise would need about 32 m at 1:12 |
| Pilot house cover height | Roof at +9.30 m, cover to +11.70 m (2.4 m high) | Matches the sections' conceptual bridge projection |
| Observation lounge | Former lift lobby area, about 9 m by 6.5 m | Removes the undersized room |
| Accessible cabin size | 6 m by 4.1 m schematic, interior to be specified | Adequate for turning space in a schematic |
| Lift car size | 1.5 m by 2.0 m internal | Clears the ADA minimums of 1.372 m by 1.73 m |
| Lift position | Forward, 48 to 51 m, per the owner brief | The General Arrangement sheet is superseded for this point |

These are my decisions on the open items. Change any of them in `layout/decks-layout.json` or `layout/accessibility.json` and rerun the checks.

## Open: verification and sources

1. **ADA figures.** The criteria in `layout/accessibility.json` are standard building values. Check them against the passenger-vessel text in 36 CFR Part 1191 before use.
2. **Door widths, thresholds and turning spaces** are not modelled in the layout. The accessible cabin's interior needs a detailed pass.
3. **Layout coordinates** were read from the schematic at about 14 px per metre. They are not dimensioned. Replace them when the design team has dimensioned plans.
4. **Mast positions** in the elevations are approximate, read from the longitudinal section.
5. **Aft envelope widths** in the aft elevation are approximate, read from the END ELEVATIONS sheet.
6. **Roof level** (+9.30 m) is assumed to match the Bridge floor. It is not confirmed on any sheet.

## Open: renders

1. **Renders 06, 07, 12 and 13** were regenerated on 10 Oct 2026 to match the resolved layout. The superseded versions are in `drawings/renders/superseded/`. Render 12 shows a wheel as well as touch screens, which the brief does not specify.
2. **All renders** are AI concept illustrations for mood and material direction only.

## Open: scope

1. **Systems register.** Most parameters are still "To be determined". The content fill-in is the next phase.
2. **Guest-facing app scope.** Booking, guest services and the dinner experience are proposed for a separate application. Scope not yet confirmed.

## Next checks

- Re-run `npm run validate:layout`, `npm run validate:access`, `npm run build:drawings`, `npm run build:elevations` after any layout change.
- Regenerate the renders after any further layout change. Renders 06, 07, 12 and 13 match the layout as of 10 Oct 2026.
