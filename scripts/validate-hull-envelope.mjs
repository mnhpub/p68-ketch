// Hull envelope rework: deck areas with taper, enclosed volume, displacement from the block coefficient,
// and the draft implied by the reference displacement, checked against the keel draft targets.
// Structural errors fail the run. Physics results are printed as FLAG lines and do not fail the run.
// Run with: npm run validate:hull-envelope
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
const inp = load('layout/hull-envelope-inputs.json');
const decks = load('decks.json');
const errors = [];
const flags = [];

const num = (s) => Number.parseFloat(String(s).replace('−', '-').replace(/[^\d.+-]/g, ''));
const levels = decks.map((d) => ({name: d.name, z: num(d.elevation)})).sort((a, b) => a.z - b.z);
if (levels.length !== 5) errors.push(`expected 5 levels in decks.json, found ${levels.length}`);
if (inp.lwl_m > inp.loa_m) errors.push('waterline length exceeds LOA');

const spacings = levels.slice(1).map((l, i) => l.z - levels[i].z);
const minSpacing = Math.min(...spacings);
if (minSpacing <= 0) errors.push('deck elevations are not increasing');

// Plan area of a deck at the given taper: an ellipse of the full beam, narrowed per level above the lowest deck.
const fullArea = Math.PI * (inp.loa_m / 2) * (inp.beam_m / 2);
const rows = [];
for (const taperPct of inp.upper_deck_taper_pct_per_level) {
  const areas = levels.map((l, i) => {
    const narrowing = Math.max(0.05, 1 - (taperPct / 100) * i);
    return fullArea * narrowing;
  });
  let volume = 0;
  for (let i = 0; i < levels.length - 1; i++) volume += ((areas[i] + areas[i + 1]) / 2) * (levels[i + 1].z - levels[i].z);
  rows.push({taperPct, areas, volume});
}

console.log(`Inputs: LOA ${inp.loa_m} m, LWL ${inp.lwl_m} m, beam ${inp.beam_m} m (repo values)`);
console.log(`Full plan ellipse ${fullArea.toFixed(1)} m² (uniform outline in decks-layout.json is 643.6 m²)`);
console.log('\nTaper per level   Lowest-to-top deck areas (m²)                     Enclosed volume (m³)');
for (const r of rows) {
  console.log(`${String(r.taperPct).padStart(4)}%            ${r.areas.map((a) => a.toFixed(0).padStart(4)).join(' ')}          ${r.volume.toFixed(0).padStart(7)}`);
}

// Displacement from block coefficient: V = Cb × LWL × B × T.
const wl = inp.lwl_m * inp.beam_m;
console.log(`\nDisplacement from draft: V = Cb × LWL × B × T, with LWL × B = ${wl.toFixed(1)} m²`);
for (const cb of inp.block_coefficient_range) {
  const t = inp.keel_up_draft_m;
  const vUp = cb * wl * t[0];
  const vDown = cb * wl * inp.keel_down_draft_m[0];
  console.log(`  Cb ${cb.toFixed(2)}: keel-up ${t[0]} m needs ${vUp.toFixed(0)} m³ (${(vUp * inp.seawater_t_m3).toFixed(0)} t); keel-down ${inp.keel_down_draft_m[0]} m needs ${vDown.toFixed(0)} m³ (${(vDown * inp.seawater_t_m3).toFixed(0)} t)`);
}

// Draft implied by the reference displacement.
const refDraftAt = (cb) => inp.reference_volume_m3 / (cb * wl);
const dLo = refDraftAt(inp.block_coefficient_range[1]);
const dHi = refDraftAt(inp.block_coefficient_range[0]);
console.log(`\nDraft implied by the reference ${inp.reference_volume_m3} m³: ${dLo.toFixed(2)} m to ${dHi.toFixed(2)} m across Cb ${inp.block_coefficient_range[1]} to ${inp.block_coefficient_range[0]}`);
console.log(`Keel-up target ${inp.keel_up_draft_m[0]} m; keel-down target ${inp.keel_down_draft_m[0]} m.`);
if (dHi < inp.keel_up_draft_m[0]) flags.push(`the reference displacement implies a draft of at most ${dHi.toFixed(2)} m, below the keel-up target of ${inp.keel_up_draft_m[0]} m. The volume or the draft targets are wrong.`);

// Waterplane check from the waterplane coefficient.
const wp = inp.waterplane_coefficient * wl;
console.log(`Waterplane area ${inp.waterplane_coefficient} × LWL × B = ${wp.toFixed(0)} m²`);

// Ketch rig footprints taken from the Main / Master or Tween decks are not yet placed. Report the total.
const rigArea = inp.ketch_rig.mainmast_foundation_m2 + inp.ketch_rig.mizzen_foundation_m2;
console.log(`Ketch rig foundations: ${rigArea.toFixed(1)} m² of deck structure at mast positions (placeholders; stays not included).`);

// Reconciliation flag: the uniform model against the reference volume.
const uniform = rows[0].volume;
if (uniform > inp.reference_volume_m3) flags.push(`the uniform model encloses ${uniform.toFixed(0)} m³ against a reference displacement volume of ${inp.reference_volume_m3} m³.`);
const best = rows[rows.length - 1].volume;
flags.push(`even at ${inp.upper_deck_taper_pct_per_level[inp.upper_deck_taper_pct_per_level.length - 1]}% taper per level the enclosed volume is ${best.toFixed(0)} m³. Taper alone does not reconcile the volume with the reference.`);

if (errors.length) {
  console.error(`\nhull envelope: ${errors.length} structural problem(s)`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log(`\nFLAGS (${flags.length}):`);
for (const f of flags) console.log(`  FLAG ${f}`);
console.log('\nhull envelope: structure OK. Flags are findings for review.');
