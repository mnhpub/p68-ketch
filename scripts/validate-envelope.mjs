// Plan-area budget check. Gross area is the shoelace area of each deck outline. Claimed area is
// the unique room rectangles on each deck. The outdoor roof area (names starting "Roof:") is excluded:
// it sits above the hull plan and shares the Aft Lido footprint. Roof access passages are interior and count.
// Net free area is gross minus claimed, less the circulation, structure and services allowance.
// Requests from layout/envelope-budget.json must fit within net free area on their deck.
// Run with: npm run validate:envelope
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
const layout = load('layout/decks-layout.json');
const budget = load('layout/envelope-budget.json');
const errors = [];

const shoelace = (pts) => {
  let s = 0;
  for (let i = 0; i < pts.length; i++) {
    const [x1, y1] = pts[i];
    const [x2, y2] = pts[(i + 1) % pts.length];
    s += x1 * y2 - x2 * y1;
  }
  return Math.abs(s) / 2;
};

const allowance = budget.circulation_structure_services_allowance_pct / 100;
if (!(allowance >= 0 && allowance < 1)) errors.push(`allowance ${budget.circulation_structure_services_allowance_pct}% is out of range`);

const rows = [];
const byDeck = {};
for (const deck of layout.decks) {
  const gross = shoelace(deck.outline);
  const seen = new Set();
  let claimed = 0;
  for (const r of deck.rooms) {
    if (!r.rect) {
      errors.push(`${deck.name}: room "${r.name}" has no rect`);
      continue;
    }
    if (r.name.startsWith('Roof:')) continue;
    const key = `${r.name}|${r.rect.join(',')}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const [x0, y0, x1, y1] = r.rect;
    claimed += (x1 - x0) * (y1 - y0);
  }
  const net = (gross - claimed) * (1 - allowance);
  byDeck[deck.name] = {gross, claimed, net, requested: 0};
}

for (const req of budget.requests) {
  const d = byDeck[req.deck];
  if (!d) {
    errors.push(`request "${req.item}" names deck "${req.deck}", which is not in decks-layout.json`);
    continue;
  }
  if (!(req.area_m2 > 0)) errors.push(`request "${req.item}" has a non-positive area`);
  d.requested += req.area_m2;
}

for (const [name, d] of Object.entries(byDeck)) {
  const left = d.net - d.requested;
  if (left < 0) errors.push(`${name}: requests ${d.requested.toFixed(1)} m² but net free is ${d.net.toFixed(1)} m²`);
  rows.push(`${name.padEnd(18)} gross ${d.gross.toFixed(1).padStart(7)}  claimed ${d.claimed.toFixed(1).padStart(7)}  net free ${d.net.toFixed(1).padStart(7)}  requested ${d.requested.toFixed(1).padStart(6)}  left ${left.toFixed(1).padStart(7)} m²`);
}

console.log(`Allowance ${budget.circulation_structure_services_allowance_pct}% (placeholder)`);
console.log(rows.join('\n'));

if (errors.length) {
  console.error(`\nenvelope-budget.json: ${errors.length} problem(s)`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log(`\nenvelope-budget.json OK: ${budget.requests.length} requests fit within net free area on their decks`);
