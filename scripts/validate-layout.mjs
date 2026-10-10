// Checks layout/decks-layout.json: rooms match decks.json, sit inside the deck
// outline, and do not overlap on the same deck. Roof overlays are exempt from
// the overlap check because they sit above other rooms by design.
// Run with: npm run validate:layout
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const layout = JSON.parse(readFileSync(join(root, 'layout/decks-layout.json'), 'utf8'));
const decks = JSON.parse(readFileSync(join(root, 'decks.json'), 'utf8'));
const errors = [];

// Ray-casting point-in-polygon test.
function inside(px, py, poly) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}

const overlaps = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];

for (const ld of layout.decks) {
  const deck = decks.find((d) => d.name === ld.name);
  if (!deck) {
    errors.push(`layout deck "${ld.name}" is not in decks.json`);
    continue;
  }
  const layoutNames = ld.rooms.map((r) => r.name);
  for (const r of deck.rooms) {
    if (!layoutNames.includes(r)) errors.push(`${ld.name}: room "${r}" from decks.json has no layout geometry`);
  }
  for (const r of ld.rooms) {
    if (!deck.rooms.includes(r.name)) errors.push(`${ld.name}: layout room "${r.name}" is not in decks.json`);
    const [x0, y0, x1, y1] = r.rect;
    if (!(x1 > x0 && y1 > y0)) errors.push(`${ld.name}: "${r.name}" has an empty or inverted rectangle`);
    for (const [x, y] of [[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) {
      if (!inside(x, y, ld.outline)) errors.push(`${ld.name}: "${r.name}" corner (${x}, ${y}) is outside the deck outline`);
    }
  }
  const solid = ld.rooms.filter((r) => !r.roof);
  for (let i = 0; i < solid.length; i++) {
    for (let j = i + 1; j < solid.length; j++) {
      if (overlaps(solid[i].rect, solid[j].rect)) {
        errors.push(`${ld.name}: "${solid[i].name}" overlaps "${solid[j].name}"`);
      }
    }
  }
}

for (const d of decks) {
  if (!layout.decks.find((ld) => ld.name === d.name)) errors.push(`decks.json level "${d.name}" has no layout`);
}

if (errors.length) {
  console.error(`decks-layout.json: ${errors.length} problem(s)`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
const count = layout.decks.reduce((n, d) => n + d.rooms.length, 0);
console.log(`decks-layout.json OK: ${count} rooms across ${layout.decks.length} decks, no overlaps, all inside outlines`);
