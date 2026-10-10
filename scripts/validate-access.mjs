// Checks the layout against the accessibility criteria in layout/accessibility.json.
// It reports gaps; it does not fail the build, because the layout is still provisional.
// Run with: npm run validate:access
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
const access = load('layout/accessibility.json');
const layout = load('layout/decks-layout.json');
const gaps = [];

const pattern = new RegExp(access.route_name_patterns.join('|'), 'i');
const minRoute = access.criteria.accessible_route_min_width_m;
const liftStops = new Set(access.lift_stops);
const EPS = 0.05;

const isRoute = (r) => pattern.test(r.name);
const width = (r) => Math.min(r.rect[2] - r.rect[0], r.rect[3] - r.rect[1]);

// True when two rooms share an edge segment (they touch, without overlapping).
function touches(a, b) {
  const [ax0, ay0, ax1, ay1] = a.rect;
  const [bx0, by0, bx1, by1] = b.rect;
  const xOverlap = Math.min(ax1, bx1) - Math.max(ax0, bx0);
  const yOverlap = Math.min(ay1, by1) - Math.max(ay0, by0);
  const vertEdge = (Math.abs(ax1 - bx0) < EPS || Math.abs(bx1 - ax0) < EPS) && yOverlap > EPS;
  const horizEdge = (Math.abs(ay1 - by0) < EPS || Math.abs(by1 - ay0) < EPS) && xOverlap > EPS;
  return vertEdge || horizEdge;
}

// A room is on an accessible route if a route-named room of adequate width touches it.
function hasAccessibleRouteTo(room, rooms) {
  return rooms.some((other) => other !== room && isRoute(other) && width(other) >= minRoute && touches(room, other));
}

// 1. Every public level must be reachable by a lift.
for (const level of access.public_levels) {
  if (!liftStops.has(level)) {
    gaps.push(`${level}: public level has no lift stop, so guest areas here are not on an accessible route`);
  }
}

// 2. Circulation that is named as a route must be wide enough.
for (const deck of layout.decks) {
  if (!access.public_levels.includes(deck.name)) continue;
  for (const r of deck.rooms) {
    if (!isRoute(r) || r.name.startsWith('Mag-rail')) continue;
    if (width(r) < minRoute) {
      gaps.push(`${deck.name}: "${r.name}" is ${width(r).toFixed(2)} m wide, below the ${minRoute} m accessible route width`);
    }
  }
}

// 3. Public levels must have a route room laid out.
for (const deck of layout.decks) {
  if (!access.public_levels.includes(deck.name)) continue;
  if (!deck.rooms.some(isRoute)) {
    gaps.push(`${deck.name}: no corridor, passage or lobby is laid out, so the accessible route cannot be checked`);
  }
}

// 4. Each lift shaft on a public level must open onto an adequate lobby or passage.
for (const deck of layout.decks) {
  if (!access.public_levels.includes(deck.name)) continue;
  for (const lift of deck.rooms.filter((r) => r.name.startsWith('Mag-rail lift'))) {
    if (!hasAccessibleRouteTo(lift, deck.rooms)) {
      gaps.push(`${deck.name}: ${lift.name} has no adjacent lobby or passage at least ${minRoute} m wide, so guests cannot reach it by an accessible route`);
    }
  }
}

// 5. At least one accessible guest cabin, on a lift-served level, with a route to it.
const acc = access.accessible_guest_cabins;
if (acc && acc.required > 0) {
  if (!acc.level) {
    gaps.push(`accessible guest cabin (${acc.required} required): level not yet assigned. It must be on a lift-served level`);
  } else if (!liftStops.has(acc.level)) {
    gaps.push(`accessible guest cabin is on ${acc.level}, which no lift serves`);
  } else {
    const deck = layout.decks.find((d) => d.name === acc.level);
    const cabins = deck ? deck.rooms.filter((r) => r.name === 'Accessible guest cabin') : [];
    if (cabins.length === 0) {
      gaps.push(`accessible guest cabin is listed on ${acc.level} but has no layout room there`);
    } else {
      for (const cabin of cabins) {
        if (!hasAccessibleRouteTo(cabin, deck.rooms)) {
          gaps.push(`accessible guest cabin on ${acc.level} has no adjacent lobby or passage at least ${minRoute} m wide`);
        }
      }
    }
  }
}

// 6. Roof: the Bridge must have a roof access passage that touches a lift lobby.
const bridge = layout.decks.find((d) => d.name === 'Bridge');
const roofPassages = bridge ? bridge.rooms.filter((r) => r.name === 'Roof access passage') : [];
if (access.roof && roofPassages.length === 0) {
  gaps.push('roof: no roof access passage laid out on the Bridge');
} else if (access.roof) {
  const lobbies = bridge.rooms.filter((r) => /lift lobby/i.test(r.name));
  const linked = roofPassages.some((p) => lobbies.some((l) => touches(p, l) && width(p) >= minRoute));
  if (!linked) gaps.push('roof: the roof access passage does not touch a lift lobby');
}

// 7. Lift shafts must fit the car: shaft width at least the car width.
const carW = access.criteria.lift_car_internal_m ? access.criteria.lift_car_internal_m[0] : null;
const carMin = access.criteria.lift_car_min_m[0];
if (carW !== null && carW < carMin) gaps.push(`lift car width ${carW} m is below the ADA minimum of ${carMin} m`);
for (const deck of layout.decks) {
  for (const lift of deck.rooms.filter((r) => /Mag-rail lift/.test(r.name))) {
    const shaft = width(lift);
    if (carW !== null && shaft < carW) gaps.push(`${deck.name}: ${lift.name} shaft is ${shaft.toFixed(2)} m, narrower than the ${carW} m car`);
  }
}

if (gaps.length) {
  console.log(`Accessibility: ${gaps.length} gap(s) to resolve (criteria in layout/accessibility.json, values to verify)`);
  for (const g of gaps) console.log(`  - ${g}`);
} else {
  console.log('Accessibility: no gaps against the current criteria');
}
