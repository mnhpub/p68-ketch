# Materials policy: no foam, no synthetics outdoors

Status: owner decision, recorded. Strict. No exceptions unless the owner names one in writing.

## The rules

1. **No foam anywhere on the craft.** This covers upholstery, cushions, insulation, gaskets, packaging, fenders, buoyancy and the fill of any fitting. Closed-cell and open-cell foams, polyurethane and polyethylene foams, and foam-filled core materials are all excluded.
2. **Teak only for outdoor decking.** No synthetic or engineered decking on any exterior surface.
3. **No synthetic materials in outdoor accommodation.** Outdoor furniture, cushions, covers, fabric, fixings and fittings are natural materials or metal, as set out below.

## What is allowed

| Use | Allowed | Notes |
|---|---|---|
| Outdoor decking | Teak | Certified sourcing, and an upkeep plan (oiling, cleaning, sanding) |
| Outdoor metal fittings, frames | Stainless steel (316 or better), titanium | Dissimilar-metal isolation from the hull and structure |
| Outdoor cushion fill | Natural fibre, to be specified: for example wool, horsehair, coir, cotton batting | Must dry out and resist mould. Not foam, not polyester batting |
| Outdoor fabric | Natural fibre, to be specified: for example cotton canvas, linen | Natural fabrics degrade in sun and damp; see the open risk below |
| Interior upholstery | Steel coil or sinuous springs with natural fibre fill and natural-fibre covers | No foam in any layer |
| Insulation | Natural or mineral fibre to be specified | Whether man-made mineral fibre counts as synthetic must be settled before use |

## The risk this creates

Natural fabrics are the weak point. Cotton and linen fade and rot in sun and damp, and wool does not last outdoors. Synthetic fabrics such as solution-dyed acrylic are what marine outdoor furniture normally uses for UV resistance, and the policy rules them out. The owner's brief asks for resilience, so the policy and the brief pull against each other. The honest position is that outdoor natural fabrics will need replacing more often than synthetic ones, and the spares plan (`docs/exterior-and-maintenance.md`) must allow for it. No synthetic substitute should be used without a fresh written decision.

## Conflicts found in the current design

These are places where the rules conflict with a system or item already in the repo. Each needs a decision. None has been changed.

| Item | Where | Conflict | Options to decide between |
|---|---|---|---|
| Tender hulls | `docs/accommodation-considerations.md`, `docs/tender-mag-rail-reload.md` | Many tender hulls are foam-cored or foam-filled for buoyancy and rigidity. | Solid laminate, or a non-foam core such as balsa wood (natural), or aluminium or steel construction |
| Buoyancy | `slides.json`, "Hull & Buoyancy" | Buoyancy in many craft comes from foam. | Sealed air-filled compartments, designed to the stability and damage-survival rules |
| Life jackets, fenders, safety equipment | Not yet in the repo | Standard life-saving and fender products are often foam-filled. | Inflatable or natural-material alternatives, where the rules allow them |
| Gaskets and seals | Not yet in the repo | Closed-cell foam gaskets are common. | Solid natural rubber or metal-to-metal seals |
| Sails | `systems.json`, `sail-system` | Sails are normally synthetic (polyester or similar). The rule covers outdoor accommodation, not sails, so sails may fall outside it. | Confirm whether sails are in scope of the policy |
| Lines, mooring and anchor rope | `systems.json`, `anchor-system` | Modern rope is synthetic. The rule does not name rope. | Confirm whether rope is in scope |
| Medical and EMS kit cases and packaging | `docs/accommodation-considerations.md` | Padded cases are usually foam. | Natural fibre padding, or padding-free cases with dividers |
| Battery rack pads, cable clamps | `docs/energy-management-architecture.md` | Vibration pads are often foam or elastomer. | Metal springs or natural-rubber mounts |
| Mineral wool insulation | Battery room, cabins | Man-made mineral fibre is not foam, but it is not natural. | Decide whether it counts as synthetic |

## What this changes

- The outdoor furniture and cushion requirements in `docs/exterior-and-maintenance.md` now refer to this policy. Its "marine-grade UV-stable fabric" line is superseded.
- The tender construction choice is now constrained. It is no longer open-ended.
- The spares plan must include natural-fibre replacement cushions and fabric, at a higher rate than the synthetic alternative would need.

## Open decisions for the owner

1. Are sails, rope and mooring lines inside the policy?
2. Is man-made mineral wool insulation allowed?
3. Tender construction: solid laminate, balsa core, aluminium or steel?
4. Buoyancy: is an air-filled compartment design acceptable to the class and the owner?
5. Outdoor natural fabric: accept the replacement rate, or spend design effort on the best natural option?

## Natural fibres and animal materials: inventory

The policy above allows natural materials but never lists them. This inventory closes that gap. Each material is marked as allowed, excluded by the owner, or still to decide.

| Material | Status | Notes |
|---|---|---|
| Silk | **Excluded by the owner** | Not used anywhere in the craft, indoors or out. Removes silk cushions, throws and bedding from the design. |
| Leather | To decide | Animal material. Present in the bridge seating and the helm chairs. Outdoor leather is a poor fit for sun and salt. |
| Down and feathers | To decide | Animal material with welfare questions. Not used in the current design. |
| Wool | Allowed (to specify) | Natural. Good for interior fill. Does not last outdoors. |
| Horsehair | Allowed (to specify) | Natural. Traditional upholstery fill. |
| Coir | Allowed (to specify) | Natural. Fill and matting. |
| Cotton | Allowed (to specify) | Natural. Degrades in sun and damp outdoors. |
| Linen | Allowed (to specify) | Natural. Used in the bedding in the renders. Degrades outdoors. |
| Hemp, jute, sisal | To decide | Natural. Rough textures. Not yet assessed for use. |
| Cork | To decide | Natural. Possible for flooring or stopper uses. Not yet assessed. |
| Gore-Tex and other PTFE (expanded PTFE) membranes | **Excluded** | Synthetic fluoropolymer, so it is excluded by the no-synthetics rule outdoors. PTFE belongs to the PFAS family, which is excluded everywhere on the craft. Manufacturers' PFAS-free claims for water coatings must be verified independently, and the membrane itself is still PTFE. |
| Bamboo or viscose-type fibres | To decide | Regenerated from wood pulp by chemical processing. Whether it counts as natural is a policy question. |

The render briefs in `IMAGE_GENERATION.json` call for silk cushions, silk throws and silk bedding, and leather for the helm chairs. Those briefs conflict with this inventory, so the renders should be regenerated before they are used in review. This note does not change the renders.

**Ivory as a material is excluded.** This includes reclaimed, antique and salvaged ivory. Elephant ivory is listed under CITES Appendix I, its trade is restricted in most countries, and reclaimed ivory usually cannot be legally sold or moved across borders. It also keeps demand alive for poaching. The word "ivory" in the renders and slides is a colour, and it stays a colour.

Ivory-coloured alternatives that need no animal material: natural stone in cream tones, and natural-fibre fabrics in an undyed cream. Wood is teak only, so it is not an ivory alternative here.

## Membranes: a correction

The battery room design in `docs/energy-management-architecture.md` proposes a breather or membrane vent to equalise pressure while keeping water out. Membranes of this kind are usually expanded PTFE, which this policy excludes. The design needs a different vent: for example a sintered stainless steel vent, or a pressure-relief arrangement with a metal flame arrestor. Neither is chosen yet, and the choice should be checked against the IP67 requirement and the fire-safety review before it is used.

Other membranes in the design (for example in cabin ventilation or the sailing gear) need the same check against this policy.

## Ivory-look surfaces: wood or steel

Owner direction: ivory-look surfaces change to wood or steel, using decorative processes. Synthetic ivory is not used. This replaces the synthetic-ivory option raised above.

### Wood

- **Teak only** (owner decision, see the teak-only section below). Walnut, oak and sycamore are no longer in the palette.
- **Decorative processes** such as bookmatching, marquetry, inlay and burl figure. These give the depth and pattern that ivory-look surfaces were meant to supply.
- **Finish:** natural oil or a low-emission lacquer, with a repair route so surfaces are sanded and refinished on board rather than replaced.

**Exotic materials are banned.** Owner decision. No exotic timber, stone, skin or other exotic material goes into the craft. The CITES check no longer applies to a species that is excluded anyway. Domestic and temperate species, such as walnut, oak and sycamore, are not affected by this ban.

Open point on teak: teak is an imported tropical hardwood. If the owner counts it as exotic, it is banned, and the outdoor decking needs a different material, because the outdoor decking rule names teak only. See the open decisions below.

### Steel

- **Stainless steel (316 or better) or titanium** panels, with decorative finishes such as brushed, bead-blasted, patinated or inlaid metal.
- **Interior steel** is not synthetic, so it is allowed under the policy. Outdoor steel stays 316 or titanium, as already set.
- Metal surfaces must be checked for fingerprinting and cleaning routine, and for how repairs are done on board.

### What this removes

- Synthetic ivory and any other ivory-look resin.
- Celluloid, which is excluded on a vessel for fire reasons.

### Open decisions

1. Is teak exotic under the ban? If yes, the outdoor decking needs a different material, and the policy must be updated.
2. Confirm the definition of "exotic": is it any imported species, any species protected under CITES, or both?
3. Walnut, oak and sycamore are removed by the teak-only decision. The bridge and salon renders need recasting in teak.
4. Stainless or titanium for steel surfaces, and which finish.

## Sustainable, non-synthetic materials

Owner direction: sustainable materials, and nothing synthetic. This sits alongside the bans above: no foam, no synthetics, no exotic materials, and no ivory.

### What "sustainable" means here

A material qualifies when it meets these tests, and the claim is backed by a recognised certification or a documented source:

1. **Natural or mineral origin.** It is not synthetic, and it is not made from a petrochemical.
2. **Responsibly sourced.** Timber is certified (FSC or PEFC), and fibres and leather come from certified supply chains.
3. **Domestic or reclaimed where possible.** Local supply cuts transport, and reclaimed material avoids new harvest or extraction.
4. **Low-toxicity processing and finish.** Natural oils, mineral paints and low-emission finishes, with the emission claim verified.
5. **Durable and repairable.** It lasts, and it can be sanded, re-stitched or re-finished on board, so it is not thrown away.
6. **Recyclable or biodegradable at end of life.**

### Candidates that fit

| Use | Candidate | Basis | Check before use |
|---|---|---|---|
| Wood | Teak only (owner decision): interior joinery and exterior decking. Wood is not structural. | Owner decision. Teak's status under the exotic ban is still to confirm. |
| Metal | Stainless steel 316 or better with high recycled content, and titanium | Recyclable and long-lived | Recycled-content certificate; titanium production is energy-intensive, so the trade-off must be stated |
| Stone | Domestic natural stone (for example slate, limestone or granite from a nearby quarry) | Mineral, long-lived, local | Quarry certification and transport distance |
| Outdoor fabric | Organic cotton (GOTS certified), certified linen | Natural and certified | Performance outdoors is limited; see the open risk in this policy |
| Wool | Certified wool (for example Responsible Wool Standard) | Natural and traceable | Welfare and sourcing certificate |
| Cork | Harvested cork (bark stripped without felling) | Renewable, natural, low-impact | Supplier certificate |
| Fill | Wool, coir, horsehair | Natural and renewable | Certification for each source |
| Leather (decision needed) | Vegetable-tanned leather from a certified tannery | Natural, repairable, long-lived | Owner decision: leather is still under "to decide" in this policy |
| Finish | Natural oils, mineral paints, low-emission natural lacquers | Low toxicity | Emission certificate |

### Still open

- **Teak.** Teak is the outdoor decking species. It is either an exotic imported hardwood, which is banned, or it is allowed as a certified plantation species. The owner has not decided. Until that decision is made, the outdoor decking material is not specified.
- **Leather.** Animal product: owner decision needed.
- **Outdoor fabric.** Natural fabric degrades in sun and damp. The open risk in this policy still stands.
- **Titanium.** Its sustainability depends on the production route, which must be stated before it is specified.

### What this does not change

The bans stand: no foam, no synthetics outdoors, no exotic materials, no ivory, no silk, and no PFAS membranes.

## Precious metals and silk: excluded

Owner direction: silk, gold and silver are excluded from the craft.

- **Silk:** excluded, as recorded above.
- **Gold and silver:** excluded. Gold and silver are mined, and mining is a major source of pollution and habitat loss. The owner's sustainability direction is incompatible with using either as a feature material.
- **Recycled gold and silver** are the one variant that could be reconsidered, since they avoid new mining. This is not allowed under the present direction. If the owner wants to allow it, that is a separate decision, with recycled-content certification required.

Reading of the instruction: "silk, gold, silver" was read as a list of exclusions, continuing the bans above. If you meant these as materials you want, tell me and I'll reverse the entry.

## Approved: stainless steel

Owner direction: stainless steel is approved.

- **Grade:** 316 or better, with high recycled content, per the sustainable-materials tests above.
- **Uses:** interior and exterior, including deck fittings, rails, cleats, hinges, furniture frames, and interior panels and surfaces.
- **Not covered:** chrome-plated steel. Plating is a different material and keeps the caution recorded in `docs/exterior-and-maintenance.md`.
- **Still to be verified for each supply:** the recycled-content certificate, the grade certificate, and the finish.

## Rule: stainless steel for all rigid appointments

Owner direction: the craft's rigid appointments are stainless steel throughout.

**Reading of "rigid appointments":** the fixed, load-carrying fittings and furniture frames of the craft: deck and interior fittings, rails, brackets, furniture frames, galley and workshop fixtures, and the frames of the stowage lockers and racks. Grade 316 or better, with high recycled content, as already approved.

### Conflicts to settle

1. **Wood joinery.** Teak joinery is rigid, and the owner must state whether it is an "appointment" under this rule. See the teak-only section for the decision still open.
2. **Weight.** Stainless steel is heavy. Every steel appointment has to be added to the weight register, and the envelope and keel draft checks (`docs/design-gap-analysis.md`) will move. Weight is currently 0% covered, so this cannot yet be quantified.
3. **Galvanic corrosion.** Stainless fittings bolted to aluminium, carbon steel or bronze fittings will corrode the less noble metal. Each joint needs isolation. This is a design rule, not a material change.
4. **Cost and fabrication.** Bespoke stainless joinery is costly to fabricate. Its cost goes into the budget once the fit-out schedule exists.
5. **Interior feel.** Stainless is cold and reflective in a living space. The renders and slides show walnut and leather, which this rule removes. Any new render brief must follow this rule.

### What the rule does not cover

- The hull and the structure are the subject of the steel and structural reviews, not this appointments rule.
- Soft furnishings (cushions, fabric, upholstery fill) are governed by the separate natural-material and no-foam rules.

### Open decisions

1. Is wood joinery an appointment under this rule, or outside it?
2. Does the rule cover the hull and primary structure, or only the fittings?


## Wood: teak only

Owner direction: wood is not structural, and teak is the only wood used on the craft.

- **Scope of wood:** interior joinery and panelling, and exterior decking. Both are teak. Walnut, oak, sycamore, ash, beech, cherry and maple are no longer in the palette, and the walnut in the bridge and salon renders must be recast in teak.
- **Structure:** wood carries no structural load. Structural members are steel, as the stainless and structural reviews set out.
- **Teak and the exotic ban:** the owner has approved teak as the only wood. Teak is an imported tropical hardwood, so this is either a definition of "exotic" that excludes teak, or an exception to the ban. The owner must confirm which. The teak sourcing still needs a certified plantation source (FSC or equivalent) and a documented chain of custody.
- **Joinery under the stainless rule:** the owner has not yet said whether wood joinery is a "rigid appointment". If it is, the stainless rule and the teak-only rule conflict, and the owner must choose.

### Open decisions

1. Confirm teak is not "exotic" under the ban, or grant it as an explicit exception.
2. Does the stainless rule cover wood joinery? If it does, joinery must be steel and teak is limited to decking.
3. Teak sourcing: certified plantation source and a documented chain of custody.

## Interior aesthetics: deferred

Owner direction: interior aesthetics are decided later. The interior selection criteria now are **lightweight and durable**.

- **Deferred:** colours, finishes, the look of joinery and upholstery, and any render brief for the interior. Renders for interior spaces are on hold until the aesthetic decision is made.
- **Criteria now in force for any interior material:** lightweight (mass per square metre or per part is a deciding factor), durable (service life and repairability on board), and within the bans above (no foam, no synthetics outdoors, no exotic materials, no ivory, no silk, no precious metals, no PFAS).

### Conflict with the stainless rule

The stainless rule (all rigid appointments in 316 or better steel) is heavy. Lightweight and durable point the other way. The owner needs to decide which governs the interior:

1. Keep the stainless rule and accept the weight, which will move the keel draft and the envelope checks.
2. Make lightweight the governing criterion for the interior, and allow titanium, which is light and durable but costly and energy-intensive to produce.
3. Allow another lightweight, durable interior material that is not foam, not synthetic outdoors, and not banned. No such material has been named yet, and any candidate must be checked against every ban above before it is considered.

Aluminium is not on the approved list, and it is not named by the owner. It would need an explicit decision before use, and it would need galvanic isolation from the stainless fittings.

## Structural steel: hull, Tank / Technical, Tween and deck

Owner direction: the primary structure is steel for the hull, the Tank / Technical level, the Tween level and the deck.

**Reading of "decks":** the structural plating and beams of all the decks (Bridge, Commander / Lido, Main / Master, Tween and Tank / Technical), not the teak outdoor decking laid over them. Teak decking is a separate, non-structural layer and remains teak only.

**Structure is steel. Wood is not.** This matches the teak-only rule (wood is not structural) and the stainless rule for rigid appointments. The stainless rule governs fittings and furniture frames. The steel here is the structure beneath them.

### Consequences to settle

1. **Coatings are synthetic.** Marine steel is protected by paint systems, which are synthetic polymers (epoxies and polyurethanes). The no-synthetics rule is written for outdoor accommodation, but the no-foam and no-PFAS rules apply to the craft as a whole. The owner must decide whether synthetic coating systems on structural steel are allowed, and if so which, with PFAS-free products verified. Alternatives such as hot-dip galvanising or metallic coatings avoid the polymer question, but they need checking for weight and for compatibility with the stainless fittings.
2. **Steel is heavy.** Hull and deck steel will dominate the weight register. The register is 0% covered, so the total cannot yet be checked against the 806 t reference. The keel draft and envelope checks depend on it (`docs/design-gap-analysis.md`).
3. **Galvanic isolation.** Stainless fittings bolted to the steel structure need isolation, as set out in the stainless rule.
4. **Lightweight versus structure.** The interior criteria are lightweight and durable. Steel structure works against lightweight, and the owner's direction on structure stands.

### Open decisions

1. Are synthetic coating systems allowed on structural steel? If yes, which systems, with PFAS-free verification.
2. Is hot-dip galvanising or another metallic coating preferred over paint?
3. Confirmed: "decks" means the structural plating and beams of every level. Teak outdoor decking stays a separate layer.

## Rule: no steel exposed to the elements

Owner direction: no steel is exposed to the elements. Structural steel must be protected from wind, rain, sea spray and sun wherever it is outside the craft's sealed interior.

### Where it applies, and where it conflicts

1. **The hull is in the sea.** The hull is steel, and seawater is the most severe exposure there is. The rule cannot be met by covering the hull, so it needs a protective system: coating, cathodic protection, or both. Coatings are synthetic polymers, which the owner has not yet ruled on (see the structural-steel section). This is the most significant conflict in the rule.
2. **Exposed decks.** The Lido and sun deck are outdoors. Their steel structure must sit under a sealed, protected layer, with teak decking above it.
3. **Teak decking seals.** Teak decks are normally laid with a sealant between the boards, and that sealant is usually a synthetic polymer (polysulfide, polyurethane or silicone). Under the no-synthetics rule for outdoor accommodation, the sealant needs a decision.
4. **The outdoor pilot house and rails.** Any steel frame or support on the roof or the Lido is exposed, and needs the same protection. The steel guardrails and cleats should be stainless, which is approved.
5. **Stainless is steel.** Stainless steel is a form of steel, and it corrodes in some conditions (chloride and crevice corrosion). The owner should confirm whether the rule applies to stainless, or only to carbon structural steel. Stainless fittings are approved for exterior use, so the reading matters.
6. **Mast and rig.** Any steel in the mast or rig is exposed. The sail system is not yet specified.

### Decisions needed

1. **Hull protection.** Which system protects the steel hull in seawater, and is a synthetic coating allowed for that purpose? Cathodic protection avoids the coating question, but its anodes are a consumable and need a replacement schedule.
2. **Teak decking sealant.** Is a synthetic sealant allowed in the outdoor decking, or is there a natural alternative?
3. **Does the rule apply to stainless?** If yes, the exterior stainless fittings need reconsidering. If no, the rule covers carbon structural steel only.
4. **Protection of exposed steel on the roof and Lido:** the protective system and its maintenance interval.

### Effect on the weight and maintenance records

Protective systems add weight, and they need a maintenance schedule. Both go into the weight register and the maintenance records in `docs/exterior-and-maintenance.md` once the systems are chosen.

## Exception: sealants and finishing systems

Owner direction: sealants are allowed, as a highly controlled process in finishing and sealing.

This is an **exception** to the no-synthetics rule for outdoor accommodation. It covers sealants used in finishing and sealing work: teak deck seams, the sealing of exposed steel protection, and joints in the craft's sealed structure. It does not cover anything else that is synthetic.

### Conditions the exception carries

Because the exception is a controlled process, each sealant must be:
1. **Approved by product and family.** The owner approves specific sealant families (for example polysulfide, polyurethane, silicone or MS polymer) before use. No product is used under the exception until its family is approved.
2. **PFAS-free, and free of the other bans:** no PFAS, no foam, and no halogenated or other restricted additives, verified by a certificate from the supplier.
3. **Low-emission:** an emission certificate for use in enclosed spaces.
4. **Applied under a written procedure:** surface preparation, primer, mixing, application, curing time and inspection, recorded for each job.
5. **Inspected and replaced on a schedule:** a service interval per sealant family, recorded in the maintenance records (`docs/exterior-and-maintenance.md`).
6. **Traceable:** the product, batch, applicator and date recorded against the joint or seam it seals.

### What remains outside the exception

- Foam sealing and foam-backed gaskets remain banned.
- PFAS-based sealants remain banned.
- Sealants do not extend the exception to coatings, membranes or decorative fills. Protective coatings for the steel hull and deck structure still need their own owner decision (see the structural-steel and no-exposed-steel sections).

### Open decisions

1. Which sealant families are approved, and for which joints.
2. Whether the same exception covers the protective coating system for steel, or whether coatings need a separate decision.
