# Drafting status

Status: a register of what is drafted, what is modelled, and what needs owner data or a lines plan. The drawings are in `drawings/schematics/` and are built by `scripts/build-schematics.py`.

## Drafted

| Sheet | Format | Status | Source |
|---|---|---|---|
| 1. Principal dimensions and deck profile | DXF and PDF | Drafted | `layout/hull.json`, `decks.json` |
| 2 to 6. Deck plans (Bridge, Commander / Lido, Main / Master, Tween, Tank / Technical) | DXF and PDF | Drafted from layout coordinates | `layout/decks-layout.json`, regenerated outline at 68 m by 13.0 m |
| 7. Midship section | DXF and PDF | Model section (rectangular, no tumblehome) | Deck levels and the regenerated outline |
| 8. Centreline profile | DXF and PDF | Model profile | Deck levels and centreline room extents |

## Modelled but not drafted

- Mast and rig: positions are approximate (`docs/layout-gaps.md`), and the stays are not drawn.
- Tender bay and starboard launch point: no geometry exists.
- Battery room, paint store, workshop and tender storage: placed as candidates only, with areas in `layout/envelope-budget.json`.
- Ventilation outlets: 13 of 16 have no set position (`layout/ventilation-register.json`).

## Needs owner data before drafting

1. **Lines plan.** Block coefficient, waterplane coefficient, the real outlines, and the tumblehome. Until then the section and outlines are models.
2. **Deck datum relative to the waterline.** Used by the profile and the section.
3. **Mast positions and heights** from the sail plan.
4. **Tender size and launch method**, for the bay and the storage geometry.
5. **Occupancy**, for the water and galley sizing.
6. **Mass register**, every item with its mass and height, for stability and the KG limit.

## Checks

- `npm run validate:layout`, `validate:access` and `validate:envelope` pass against the regenerated outlines.
- The schematics render without clipping. The section was corrected for scale on review.
- All eight DXF files pass the ezdxf audit with no errors.
