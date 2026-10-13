# Materials, finish-out and methods: allowed and disallowed

Status: summary of owner decisions as of 13 Oct 2026. The rules are in `docs/materials-policy.md` (ADR-0006) and
`docs/preservation-and-maintenance.md`; this page lists them in one place and does not add any new rule. Where this
page and the policy differ, the policy governs.

Key: **Allowed** = owner-approved. **Excluded** = banned by owner decision. **To decide** = open, not to be used until
the owner decides.

## 1. Materials

### Allowed

| Material | Where | Conditions |
|---|---|---|
| Teak | Outdoor decking, and interior joinery and panelling | The only wood on the craft, and never structural. Needs a certified plantation source (FSC or equivalent) with chain of custody. Its status under the exotic ban is still open (see To decide). |
| Stainless steel, 316 or better | All rigid appointments, inside and out: fittings, rails, cleats, hinges, brackets, furniture frames, galley and workshop fixtures, locker and rack frames, interior panels | High recycled content, with a grade certificate. Galvanic isolation from other metals. Passivated after fabrication. |
| Titanium | Outdoor fittings and frames, and as a lightweight option | State the energy cost of production before specifying. |
| Steel (structural) | Hull, Tank / Technical, Tween, and the structural plating and beams of every deck | Never exposed to the elements: it must be protected. The protection system is still open (see To decide). |
| Domestic natural stone (slate, limestone, granite) | Surfaces | Quarry certificate and transport distance recorded. |
| Wool (certified, e.g. RWS) | Interior fill and upholstery | Does not last outdoors. |
| Horsehair, coir | Upholstery fill and matting | Certified source. |
| Cotton (GOTS organic), linen (certified) | Fabric, indoors and out | Degrades outdoors, so the spares plan carries a higher replacement rate. |
| Steel coil or sinuous springs | Interior upholstery | With natural fibre fill and natural covers. No foam in any layer. |
| Sintered stainless vent, metal flame arrestor | Battery room venting | These replace PTFE membranes. Check against the IP67 rating and the fire review. |
| Solid natural rubber, metal-to-metal seals, metal springs | Gaskets, seals, vibration mounts | These replace foam gaskets and foam pads. |
| Sealants (controlled exception) | Teak deck seams, sealing of exposed-steel protection, joints in the sealed structure | Only under the controlled-process conditions in section 3. |

### Excluded

| Material | Scope | Note |
|---|---|---|
| Foam of any kind | Whole craft | Open- and closed-cell, PU, PE, foam cores. Covers upholstery, insulation, gaskets, fenders, buoyancy, packaging, case padding. |
| Synthetics in outdoor accommodation | Outdoor furniture, cushions, covers, fabric, fixings | Includes solution-dyed acrylic and polyester batting. The sealant exception is the only carve-out. |
| Synthetic or engineered decking | All exterior decking | Teak only. |
| PFAS, including PTFE and Gore-Tex membranes | Whole craft | PFAS-free claims are verified independently. |
| Silk | Whole craft | Removes silk cushions, throws and bedding. |
| Gold and silver | Whole craft | Recycled precious metals would need a separate owner decision. |
| Ivory | Whole craft | Includes reclaimed and antique. "Ivory" survives only as a colour. |
| Synthetic ivory, ivory-look resins, celluloid | Whole craft | Ivory-look surfaces become teak or steel with decorative processes. |
| Exotic materials (timber, stone, skins and others) | Whole craft | The definition of "exotic" is open, and so is teak's status under it. |
| Woods other than teak | Whole craft | Walnut, oak, sycamore, ash, beech, cherry and maple are all out. |
| Wood as structure | Whole craft | Structure is steel. |
| Chrome-plated steel | Not approved | Plating cracks and lifts in the marine environment. Use solid stainless or titanium unless the owner decides otherwise. |
| Aluminium | Not approved | Needs an explicit decision, plus galvanic isolation. |

### To decide (do not use until the owner decides)

| Item | Question |
|---|---|
| Teak | Is it "exotic" under the ban, or an explicit exception? |
| Definition of "exotic" | Any imported species, any CITES-listed species, or both? |
| Leather | Animal material. Currently in the helm chairs and bridge seating. If allowed: vegetable-tanned, from a certified tannery. |
| Down and feathers | Animal material with welfare questions. |
| Hemp, jute, sisal, cork | Natural, but not yet assessed. |
| Bamboo and viscose | Regenerated fibres: do they count as natural? |
| Mineral wool insulation | Man-made, and not foam: synthetic or not? |
| Coatings on structural steel | Synthetic paint systems, or galvanising and metallic coatings? PFAS-free verification either way. |
| Hull protection in seawater | Coating, cathodic protection (anodes as a consumable), or both. |
| Does the no-exposed-steel rule cover stainless? | Or carbon structural steel only? |
| Wood joinery as a "rigid appointment" | If it is, the stainless rule overrides teak joinery. |
| Stainless rule versus the lightweight interior | Accept the weight, allow titanium, or name another material. |
| Sails, rope, mooring lines | Inside or outside the no-synthetics policy? |
| Tender hulls | Solid laminate, balsa core, aluminium or steel? (Foam cores are excluded.) |
| Buoyancy | Sealed air compartments, subject to class acceptance. |
| Life jackets, fenders | Inflatable or natural-material alternatives, where the rules allow them. |
| Approved sealant families | For example polysulfide, PU, silicone or MS polymer, and which joints each covers. |

## 2. Finish-out

Interior aesthetics are **deferred** by the owner (colours, finishes, joinery look, upholstery, interior render briefs).
The criteria in force now are **lightweight and durable**, within every ban above.

### Conflicts in the current finish schedule (`layout/finishes.json`) and renders

The finish schedule was written for the finish-out renders before several policy decisions. These entries now conflict
and must change before the schedule or the renders are used in review.

| Current entry | Conflict | Policy-compliant direction |
|---|---|---|
| Bookmatched walnut floor (salon, lookout, lounge, library, helm) | Walnut is excluded: teak only. | Teak, or deferred under interior aesthetics |
| Rift oak floor (crew, accessible cabin, service circulation) | Oak is excluded. | Teak, or deferred |
| Wool-silk carpet (owner suite, VIP, guest cabins) | Silk is excluded. | Certified wool carpet |
| Calacatta marble (lobbies) | An imported Italian stone, which conflicts with the domestic-stone direction and may count as exotic. | Domestic slate, limestone or granite |
| Brass (lift cars, trim, inlay, render details) | Not on the approved list. | Stainless steel, decorative finish |
| Porcelain tile (galley, laundry) | Not assessed. Ceramic is mineral, but it is not named. | Owner decision, or domestic stone |
| Epoxy resin floor (workshop, A/V, studio) | A synthetic floor coating. It is not outdoors, but it falls under the open coatings decision. | Owner decision |
| Painted steel tread plate (technical corridor) | The coating system is not decided. | Owner decision on coatings, or plain stainless tread plate |
| Cognac leather (helm chairs, banquette, dining chairs in renders) | Leather is still to decide. | Hold until decided |
| "Ivory" upholstery (renders) | Allowed **only as a colour**. | Undyed cream wool, cotton or linen |

What stays compliant: laid teak outdoor decking, honed limestone (if domestic), and stainless fittings.

## 3. Methods

### Allowed (controlled processes, recorded per job)

| Method | Where | Record kept |
|---|---|---|
| Teak deck seam sealing | Outdoor decking | Sealant family, batch, applicator, date, joint |
| Sealing of exposed-steel protection | Lido, sun deck, roof, exposed frames | System, surface preparation, primer, curing, inspection |
| Joint sealing in the sealed structure | Watertight and air-tight joints | Product, batch, location, leak or pressure test |
| Surface preparation and priming | Steel and stainless before finishing | Preparation grade, primer, conditions |
| Teak finishing with natural oil or a low-emission lacquer | Decking and joinery | Product, coats, date, area |
| Stainless passivation | After fabrication and welding | Method, test result, date |
| Decorative wood processes: bookmatching, marquetry, inlay, burl figure | Teak surfaces | Within teak only |
| Decorative metal finishes: brushed, bead-blasted, patinated, inlaid | Stainless and titanium surfaces | Cleaning and on-board repair route documented |
| Painting by the maintenance crew | Approved surfaces only | Drip tray at every point of use, stop and clean at the first drip, cure before removing drop sheets, waste sealed. Logged: area, product and batch, containment, inspection, crew member. |
| Galvanic isolation at dissimilar-metal joints | Every stainless-to-steel or other metal joint | Design rule |
| On-board repair: sand, refinish, re-stitch | All surfaces | Preferred over replacement |

Conditions on every sealant and finishing product:
1. The product family is approved by the owner before use.
2. It is PFAS-free, with no foam and no restricted additives, and the supplier provides a certificate.
3. It has a low-emission certificate for enclosed spaces.
4. It is applied under a written procedure covering preparation, primer, mixing, application, curing and inspection.
5. It is inspected and replaced on a schedule kept in the maintenance records.
6. It is traceable: product, batch, applicator and date recorded against each joint.

### Disallowed

| Method | Why |
|---|---|
| Foam sealing, foam-backed gaskets, foam fill or packing | No-foam rule |
| PFAS-based sealants, coatings or water-repellent treatments | PFAS ban |
| Extending the sealant exception to coatings, membranes or decorative fills | Not covered by the exception. Coatings need their own decision. |
| Chrome plating | Not approved: it cracks and lifts, and the plating chemistry is regulated |
| Painting teak | Teak is never painted |
| Painting stainless | Only with owner approval |
| Leaving steel exposed to the elements | No-exposed-steel rule |
| Synthetic or engineered decking, synthetic outdoor fabric or fill | No-synthetics-outdoors rule |
| Synthetic ivory-look resins or celluloid | Excluded (celluloid is also a fire hazard) |
| Uncontrolled painting: no tray, drips left to cure | Painting procedure |
| Storing paint or solvents with fuel or batteries, or sharing their ducts | Paint store rules. The paint store has its own low-level extraction, a vapour-detector interlock, and no shared duct with the battery room. |
| Any product used before its family is approved | Controlled-process rule |
