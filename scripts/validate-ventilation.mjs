// Ventilation register checks. Structural errors fail the run. Separation rules are enforced as errors.
// Run with: npm run validate:ventilation
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
const reg = load('layout/ventilation-register.json');
const decks = new Set(load('decks.json').map((d) => d.name));
const errors = [];
const ids = new Set();
const classes = Object.keys(reg.hazard_classes);

for (const s of reg.sources) {
  if (ids.has(s.id)) errors.push(`duplicate source id "${s.id}"`);
  ids.add(s.id);
  for (const k of ['space', 'deck', 'hazard', 'separation_group', 'outlet', 'outlet_deck']) {
    if (!s[k]) errors.push(`"${s.id}" is missing ${k}`);
  }
  if (!classes.includes(s.hazard)) errors.push(`"${s.id}" has hazard class "${s.hazard}", which is not defined`);
  if (s.deck && !decks.has(s.deck) && !s.deck.includes(' / ')) errors.push(`"${s.id}" names deck "${s.deck}", which is not in decks.json`);
}

// Separation: a shared outlet must not join sources of different hazard class or different separation group.
const byOutlet = new Map();
for (const s of reg.sources) {
  const key = s.outlet.toLowerCase();
  if (!byOutlet.has(key)) byOutlet.set(key, []);
  byOutlet.get(key).push(s);
}
for (const [key, group] of byOutlet) {
  if (group.length < 2) continue;
  const hazards = new Set(group.map((g) => g.hazard));
  const groups = new Set(group.map((g) => g.separation_group));
  if (hazards.size > 1 || groups.size > 1) {
    errors.push(`shared outlet "${key}" joins ${group.map((g) => g.id).join(', ')}: hazard classes ${[...hazards].join('/')}, separation groups ${[...groups].join('/')}. Each must have its own outlet.`);
  }
}

// Lift shafts are passenger and escape routes. Hazardous, combustion and odour outlets may not use them.
for (const s of reg.sources) {
  if (s.hazard !== 'A' && /lift|shaft/i.test(`${s.outlet} ${s.outlet_deck}`)) {
    errors.push(`"${s.id}" (class ${s.hazard}) routes its outlet through a lift shaft. Lift shafts are passenger and escape routes and may not carry hazardous, combustion or odour outlets.`);
  }
}

// Combustion, hazardous and odour outlets may not be sited on or above an occupied outdoor space.
const occupiedOutdoor = /pilot house|sun deck|lido|events|roof/i;
for (const s of reg.sources) {
  if (s.hazard !== 'A' && occupiedOutdoor.test(`${s.outlet} ${s.outlet_deck}`)) {
    errors.push(`"${s.id}" (class ${s.hazard}) places its outlet on or above an occupied outdoor space. Blocked pending owner review (docs/genset-exhaust-and-systems.md).`);
  }
}

// Occupied-space air (A) must not share an outlet with hazardous or odour sources.
const hazardousOrOdour = reg.sources.filter((s) => s.hazard !== 'A');
const occupied = reg.sources.filter((s) => s.hazard === 'A');
for (const o of occupied) {
  for (const h of hazardousOrOdour) {
    if (o.outlet.toLowerCase() === h.outlet.toLowerCase()) errors.push(`occupied "${o.id}" shares an outlet with "${h.id}"`);
  }
}

const summary = {};
for (const s of reg.sources) summary[s.hazard] = (summary[s.hazard] ?? 0) + 1;
console.log(`Vent register: ${reg.sources.length} sources (${classes.map((c) => `${c}: ${summary[c] ?? 0}`).join(', ')})`);
console.log(`Distinct outlets to set: ${byOutlet.size}`);
const unset = reg.sources.filter((s) => /to set/.test(s.outlet_deck) || /to set/.test(s.outlet));
console.log(`FLAG ${unset.length} of ${reg.sources.length} outlets have no set physical location. Separation between them cannot be proven until the general arrangement is dimensioned.`);

if (errors.length) {
  console.error(`\nventilation register: ${errors.length} problem(s)`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log('ventilation register OK: every source classified, no shared outlets across hazard classes or separation groups.');
