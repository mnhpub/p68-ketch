// Weight and energy checks. Structural errors (bad references, missing fields) fail the run.
// Physics results (battery share, draft, volume) are reported as FLAG lines and do not fail the run,
// because they are findings about the design, not errors in the data.
// Run with: npm run validate:budgets
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
const register = load('weights/weight-register.json');
const energy = load('weights/energy-budget.json');
const decks = load('decks.json');
const layout = load('layout/decks-layout.json');
const systems = load('systems.json');
const errors = [];
const flags = [];

const deckNames = new Set(decks.map((d) => d.name));
const systemIds = new Set(systems.map((s) => s.id));
const SEAWATER = 1.025; // t/m³, standard seawater density
// Design draft and keel-down from the active concept's stability block (docs/concept-120m-four-mast.md).
const CONCEPT = load('layout/sail-clearance-120m-4mast.json');
const KEEL_UP_MIN_M = CONCEPT.stability.draft_m;
const KEEL_DOWN_MIN_M = +(KEEL_UP_MIN_M * 1.5).toFixed(2); // placeholder ratio, as in the first-pass note

// Weight register: structure, references and coverage.
const ids = new Set();
let known = 0;
let knownMass = 0;
for (const it of register.items) {
  if (ids.has(it.id)) errors.push(`weight register: duplicate id "${it.id}"`);
  ids.add(it.id);
  if (it.deck !== null && !deckNames.has(it.deck)) errors.push(`weight register: "${it.id}" names deck "${it.deck}", which is not in decks.json`);
  if (it.system !== null && !systemIds.has(it.system)) errors.push(`weight register: "${it.id}" names system "${it.system}", which is not in systems.json`);
  if (!['unknown', 'placeholder', 'sourced'].includes(it.mass_status)) errors.push(`weight register: "${it.id}" has mass_status "${it.mass_status}"`);
  if (it.mass_t === null) {
    if (it.mass_status !== 'unknown') errors.push(`weight register: "${it.id}" has no mass but status "${it.mass_status}"`);
  } else {
    if (!(it.mass_t > 0)) errors.push(`weight register: "${it.id}" has a non-positive mass`);
    known++;
    knownMass += it.mass_t;
  }
}
const coverage = (100 * known) / register.items.length;
console.log(`Weight register: ${register.items.length} items, ${known} with a mass (${coverage.toFixed(0)}% coverage), known mass ${knownMass.toFixed(1)} t`);
if (known < register.items.length) flags.push(`weight register is ${coverage.toFixed(0)}% covered, so no total displacement can be checked against the reference ${register.reference_displacement_t} t`);

// Reference volume is derived from the reference displacement, not typed in.
const refVolume = register.reference_displacement_t / SEAWATER;
console.log(`Reference: ${register.reference_displacement_t} t / ${SEAWATER} t/m³ = ${refVolume.toFixed(1)} m³`);

// Energy budget: battery-only requirement for the endurance target.
const days = energy.endurance_target_days;
const spec = energy.battery_specific_energy_kwh_per_kg;
const dod = energy.usable_depth_of_discharge;
if (!(spec > 0) || !(dod > 0 && dod <= 1)) errors.push('energy budget: specific energy must be positive and depth of discharge must be in (0, 1]');
console.log(`\nEndurance ${days} days, battery-only. Specific energy ${spec} kWh/kg, usable DoD ${dod}.`);
const fo = energy.fuel_option;
if (!fo || !(fo.lower_heating_value_kwh_per_kg > 0) || !(fo.genset_electrical_efficiency > 0 && fo.genset_electrical_efficiency <= 1)) errors.push('energy budget: fuel_option needs a positive heating value and an efficiency in (0, 1]');
console.log('Scenario  avg kW   energy MWh   battery t   share of displacement   fuel t (genset)');
const scenarios = [];
for (const sc of energy.hotel_load_scenarios_kw) {
  if (!(sc.average_kw > 0)) errors.push(`energy budget: scenario "${sc.label}" has a non-positive load`);
  const kwh = sc.average_kw * 24 * days;
  const massT = kwh / (spec * dod) / 1000;
  const share = (100 * massT) / register.reference_displacement_t;
  scenarios.push({label: sc.label, massT, share});
  const fuelT = kwh / (fo.genset_electrical_efficiency * fo.lower_heating_value_kwh_per_kg) / 1000;
  console.log(`${sc.label.padEnd(9)} ${String(sc.average_kw).padStart(6)}   ${(kwh / 1000).toFixed(1).padStart(10)}   ${massT.toFixed(0).padStart(9)}   ${share.toFixed(1).padStart(8)}%   ${fuelT.toFixed(1).padStart(10)}`);
  if (share > energy.mass_fraction_limit_pct) flags.push(`${sc.label} (${sc.average_kw} kW): battery alone needs ${massT.toFixed(0)} t, ${share.toFixed(0)}% of displacement, above the ${energy.mass_fraction_limit_pct}% review limit`);
}

// Buffer architecture: battery sized for peak hours, fuel supplies the energy.
const buf = energy.buffer_architecture;
if (buf) {
  const bufKwh = buf.peak_load_kw * buf.buffer_hours_at_peak;
  const bufT = bufKwh / (spec * dod) / 1000;
  console.log(`\nBuffer architecture: ${buf.peak_load_kw} kW × ${buf.buffer_hours_at_peak} h = ${bufKwh} kWh, LFP battery ${bufT.toFixed(1)} t (${(100 * bufT / register.reference_displacement_t).toFixed(2)}% of displacement)`);
}

// Battery room options: module size needed, heat load and airflow for each rack layout.
const br = energy.battery_room;
if (br) {
  const nameplate = br.usable_buffer_kwh / (dod);
  const heatKw = br.peak_load_kw * br.loss_fraction_at_peak;
  console.log(`\nBattery room: usable buffer ${br.usable_buffer_kwh} kWh → nameplate ${nameplate.toFixed(0)} kWh. Peak heat ${heatKw.toFixed(1)} kW at ${(br.loss_fraction_at_peak * 100).toFixed(0)}% loss.`);
  console.log('Option                          racks  modules  kWh/module  heat/rack W  airflow/rack m³/h  footprint m² (racks, front service)');
  for (const o of br.options) {
    const units = o.racks * br.rack_u;
    const modules = Math.floor(units / br.module_u);
    const kwhPerModule = nameplate / modules;
    const heatPerRack = (heatKw * 1000) / o.racks;
    const airM3s = heatPerRack / (br.air_density_kg_m3 * br.air_cp_j_kgk * br.design_delta_t_k);
    const footprint = o.racks * br.rack_footprint_m2 * (1 + br.rack_service_depth_m / 1.0);
    console.log(`${o.label.padEnd(31)} ${String(o.racks).padStart(5)}  ${String(modules).padStart(7)}  ${kwhPerModule.toFixed(1).padStart(10)}  ${heatPerRack.toFixed(0).padStart(11)}  ${(airM3s * 3600).toFixed(0).padStart(17)}  ${footprint.toFixed(1).padStart(10)}`);
    if (kwhPerModule > 12) flags.push(`${o.label}: needs ${kwhPerModule.toFixed(1)} kWh per module, which is larger than typical rackmount LFP modules. Check against products.`);
  }
  flags.push(`battery room heat: ${heatKw.toFixed(1)} kW at peak must leave through a closed loop. IP67 rules out open intakes and exhausts (energy-budget.json battery_room).`);
}

// Generation efficiency scenarios: fuel for the 20 kW Low case, at each whole-chain efficiency.
const lowKwh = energy.hotel_load_scenarios_kw[0].average_kw * 24 * days;
console.log(`\nGeneration efficiency scenarios (Low load, ${energy.hotel_load_scenarios_kw[0].average_kw} kW, ${days} days, ${(lowKwh / 1000).toFixed(1)} MWh):`);
console.log('Scenario                                      eff     fuel t   fuel m³ (0.85 t/m³)');
for (const g of energy.generation_efficiency_scenarios ?? []) {
  if (!(g.electrical_efficiency > 0 && g.electrical_efficiency <= 1)) errors.push(`energy budget: "${g.label}" has an efficiency outside (0, 1]`);
  const fuelKg = lowKwh / (g.electrical_efficiency * fo.lower_heating_value_kwh_per_kg);
  console.log(`${g.label.padEnd(45)} ${(g.electrical_efficiency * 100).toFixed(0).padStart(3)}%   ${(fuelKg / 1000).toFixed(1).padStart(6)}   ${(fuelKg / 850).toFixed(1).padStart(8)}`);
}

// Implied draft from the deck outline. The waterplane is approximated by the largest deck plan.
const outlineArea = Math.max(...layout.decks.map((d) => {
  const o = d.outline;
  let s = 0;
  for (let i = 0; i < o.length; i++) {
    const [x1, y1] = o[i];
    const [x2, y2] = o[(i + 1) % o.length];
    s += x1 * y2 - x2 * y1;
  }
  return Math.abs(s) / 2;
}));
const draft = register.reference_displacement_t / (SEAWATER * outlineArea);
console.log(`\nImplied draft: ${register.reference_displacement_t} t / (${SEAWATER} × ${outlineArea.toFixed(1)} m²) = ${draft.toFixed(2)} m`);
console.log(`Keel-up target ${KEEL_UP_MIN_M} m minimum, keel-down target ${KEEL_DOWN_MIN_M} m minimum.`);
if (draft < KEEL_UP_MIN_M) flags.push(`implied draft ${draft.toFixed(2)} m from the uniform outline does not reach the keel-up target of ${KEEL_UP_MIN_M} m. The outline does not describe the waterplane, so the model is inconsistent with the draft targets.`);

// Enclosed volume per deck against the reference displacement volume.
const minSpacing = (() => {
  const elev = decks.map((d) => Number.parseFloat(String(d.elevation).replace(/[^\d.+−-]/g, '').replace('−', '-')));
  const sorted = [...elev].sort((a, b) => b - a);
  let m = Infinity;
  for (let i = 0; i < sorted.length - 1; i++) m = Math.min(m, sorted[i] - sorted[i + 1]);
  return m;
})();
const perDeckVolume = outlineArea * minSpacing;
console.log(`Enclosed volume of one deck at the smallest spacing (${minSpacing.toFixed(2)} m): ${perDeckVolume.toFixed(0)} m³ against a reference ${refVolume.toFixed(1)} m³`);
if (perDeckVolume > refVolume) flags.push(`one deck encloses ${perDeckVolume.toFixed(0)} m³, more than the whole reference displacement volume of ${refVolume.toFixed(1)} m³`);

if (errors.length) {
  console.error(`\ndesign budgets: ${errors.length} structural problem(s)`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log(`\nFLAGS (${flags.length}):`);
for (const f of flags) console.log(`  FLAG ${f}`);
console.log('\ndesign budgets: structure OK. Flags are findings for review, not data errors.');
