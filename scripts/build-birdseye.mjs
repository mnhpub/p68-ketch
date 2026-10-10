// Draws an oblique bird's-eye block view of each deck from layout/decks-layout.json,
// with numbered rooms and a feature key. Schematic: rooms are extruded to a
// nominal 2.4 m height. Output: drawings/birdseye-*.svg.
// Run with: npm run build:birdseye
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const layout = JSON.parse(readFileSync(join(root, 'layout/decks-layout.json'), 'utf8'));
const outDir = join(root, 'drawings');
mkdirSync(outDir, {recursive: true});

const W = 1120;
const H = 640;
const PANEL_X = 800;
const ROOM_H = 2.4; // nominal room height, metres
const COS = Math.cos(Math.PI / 6);
const SIN = 0.5;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Oblique projection: viewer above and to the bow-starboard side.
const project = (x, y, z) => ({sx: (x - y) * COS, sy: (x + y) * SIN - z});

function category(name) {
  if (/Mag-rail lift/.test(name)) return {key: 'lift', fill: '#7fc8df', label: 'Mag-rail lift'};
  if (/Accessible guest cabin/.test(name)) return {key: 'access', fill: '#bfe3b4', label: 'Accessible guest cabin'};
  if (/lobby|passage|corridor|circulation/i.test(name)) return {key: 'route', fill: '#d4e4f0', label: 'Lobby, passage or circulation'};
  if (/tank|bilge|ballast|pump|manifold|void/i.test(name)) return {key: 'tech', fill: '#cfd3d6', label: 'Tank or technical space'};
  return {key: 'room', fill: '#eadfc9', label: 'Room'};
}

// Darken a hex colour for the side faces.
function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => Math.round(v * f));
  return `rgb(${c.join(',')})`;
}

function drawDeck(deck) {
  const rooms = deck.rooms.filter((r) => !r.roof);
  const roof = deck.rooms.filter((r) => r.roof);

  // Hull slab: the deck outline, extruded slightly
  const slabZ = -0.4;
  const outline = deck.outline;

  // Collect screen points to fit the drawing
  const pts = [];
  for (const [x, y] of outline) {
    pts.push(project(x, y, 0), project(x, y, slabZ));
  }
  for (const r of rooms) {
    const [x0, y0, x1, y1] = r.rect;
    for (const [x, y] of [[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) {
      pts.push(project(x, y, 0), project(x, y, ROOM_H));
    }
  }
  const minX = Math.min(...pts.map((p) => p.sx));
  const maxX = Math.max(...pts.map((p) => p.sx));
  const minY = Math.min(...pts.map((p) => p.sy));
  const maxY = Math.max(...pts.map((p) => p.sy));
  const drawW = PANEL_X - 40;
  const drawH = H - 110;
  const scale = Math.min(drawW / (maxX - minX), drawH / (maxY - minY)) * 0.95;
  const ox = 20 + (drawW - (maxX - minX) * scale) / 2 - minX * scale;
  const oy = 80 + (drawH - (maxY - minY) * scale) / 2 - minY * scale;
  const P = (x, y, z) => {
    const p = project(x, y, z);
    return `${(p.sx * scale + ox).toFixed(1)},${(p.sy * scale + oy).toFixed(1)}`;
  };

  const parts = [];
  parts.push(`<text x="24" y="34" font-size="16" font-weight="600" fill="#102027">P68 KETCH · ${esc(deck.name.toUpperCase())} · BIRD'S-EYE</text>`);
  parts.push(`<text x="24" y="54" font-size="11" fill="#37474f">Oblique block view from the layout. Rooms extruded to ${ROOM_H} m. Schematic, not for construction.</text>`);

  // Hull slab: side and top
  const slabTop = outline.map(([x, y]) => P(x, y, 0)).join(' ');
  const slabBottom = outline.map(([x, y]) => P(x, y, slabZ)).join(' ');
  parts.push(`<polygon points="${slabBottom}" fill="#7d8c93" stroke="none"/>`);
  parts.push(`<polygon points="${slabTop}" fill="#f7f3ea" stroke="#263238" stroke-width="1.2"/>`);

  // Rooms, painter's order: back to front (smallest x + y first)
  const sorted = [...rooms].sort((a, b) => (a.rect[0] + a.rect[1]) - (b.rect[0] + b.rect[1]));
  const keyed = [];
  sorted.forEach((r, i) => {
    const n = i + 1;
    const [x0, y0, x1, y1] = r.rect;
    const cat = category(r.name);
    const top = [P(x0, y0, ROOM_H), P(x1, y0, ROOM_H), P(x1, y1, ROOM_H), P(x0, y1, ROOM_H)].join(' ');
    // Visible side faces: the x-max face and the y-max face
    const faceX = [P(x1, y0, 0), P(x1, y1, 0), P(x1, y1, ROOM_H), P(x1, y0, ROOM_H)].join(' ');
    const faceY = [P(x0, y1, 0), P(x1, y1, 0), P(x1, y1, ROOM_H), P(x0, y1, ROOM_H)].join(' ');
    parts.push(`<polygon points="${faceX}" fill="${shade(cat.fill, 0.78)}" stroke="#263238" stroke-width="0.5"/>`);
    parts.push(`<polygon points="${faceY}" fill="${shade(cat.fill, 0.62)}" stroke="#263238" stroke-width="0.5"/>`);
    parts.push(`<polygon points="${top}" fill="${cat.fill}" stroke="#263238" stroke-width="0.6"/>`);
    const cx = (x0 + x1) / 2;
    const cy = (y0 + y1) / 2;
    const c = P(cx, cy, ROOM_H);
    const [lx, ly] = c.split(',').map(Number);
    parts.push(`<circle cx="${lx}" cy="${ly}" r="9" fill="#ffffff" stroke="#263238" stroke-width="0.8"/>`);
    parts.push(`<text x="${lx}" y="${ly + 4}" font-size="10" font-weight="700" fill="#102027" text-anchor="middle">${n}</text>`);
    keyed.push({n, name: r.name, area: (x1 - x0) * (y1 - y0), cat, note: r.note});
  });

  // Roof overlay: dashed outline above the aft roof, at the cover height
  for (const r of roof) {
    const [x0, y0, x1, y1] = r.rect;
    const pts2 = [P(x0, y0, ROOM_H + 0.2), P(x1, y0, ROOM_H + 0.2), P(x1, y1, ROOM_H + 0.2), P(x0, y1, ROOM_H + 0.2)].join(' ');
    parts.push(`<polygon points="${pts2}" fill="none" stroke="#8e3b6a" stroke-width="1.4" stroke-dasharray="6 4"/>`);
    const c = P((x0 + x1) / 2, (y0 + y1) / 2, ROOM_H + 0.4).split(',').map(Number);
    parts.push(`<text x="${c[0]}" y="${c[1]}" font-size="10" fill="#8e3b6a" text-anchor="middle">Roof overlay (above)</text>`);
  }

  // Feature key panel
  const kx = PANEL_X;
  parts.push(`<rect x="${kx - 10}" y="64" width="${W - kx}" height="${H - 84}" fill="#f4f6f7" stroke="#cfd8dc"/>`);
  parts.push(`<text x="${kx}" y="84" font-size="12" font-weight="700" fill="#102027">Area and feature map</text>`);
  let ky = 104;
  for (const k of keyed) {
    parts.push(`<circle cx="${kx + 8}" cy="${ky - 4}" r="8" fill="#ffffff" stroke="#263238" stroke-width="0.8"/>`);
    parts.push(`<text x="${kx + 8}" y="${ky}" font-size="9" font-weight="700" fill="#102027" text-anchor="middle">${k.n}</text>`);
    parts.push(`<rect x="${kx + 22}" y="${ky - 9}" width="10" height="10" fill="${k.cat.fill}" stroke="#263238" stroke-width="0.5"/>`);
    parts.push(`<text x="${kx + 38}" y="${ky}" font-size="10" fill="#102027">${esc(k.name)}</text>`);
    parts.push(`<text x="${W - 16}" y="${ky}" font-size="9" fill="#546e7a" text-anchor="end">${Math.round(k.area)} m²</text>`);
    ky += 16;
  }
  ky += 10;
  parts.push(`<text x="${kx}" y="${ky}" font-size="11" font-weight="700" fill="#102027">Legend</text>`);
  ky += 16;
  const legend = [['#7fc8df', 'Mag-rail lift'], ['#d4e4f0', 'Lobby, passage or circulation'], ['#bfe3b4', 'Accessible guest cabin'], ['#cfd3d6', 'Tank or technical space'], ['#eadfc9', 'Room']];
  for (const [fill, label] of legend) {
    parts.push(`<rect x="${kx}" y="${ky - 9}" width="12" height="10" fill="${fill}" stroke="#263238" stroke-width="0.5"/>`);
    parts.push(`<text x="${kx + 18}" y="${ky}" font-size="10" fill="#37474f">${esc(label)}</text>`);
    ky += 15;
  }
  parts.push(`<text x="${kx}" y="${H - 16}" font-size="9" fill="#8e3b6a">PROVISIONAL · NOT FOR CONSTRUCTION · Source: decks-layout.json</text>`);

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Helvetica, Arial, sans-serif">
<title>P68 Ketch ${esc(deck.name)} bird's-eye view</title>
<rect width="${W}" height="${H}" fill="#ffffff"/>
${parts.join('\n')}
</svg>
`;
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
for (const deck of layout.decks) {
  const file = `birdseye-${slug(deck.name)}.svg`;
  writeFileSync(join(outDir, file), drawDeck(deck));
  console.log(`wrote drawings/${file}`);
}
