// Draws the provisional deck layout from layout/decks-layout.json as SVG.
// One file per deck, plus an overview sheet. Output goes to drawings/.
// Run with: npm run build:drawings
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const layout = JSON.parse(readFileSync(join(root, 'layout/decks-layout.json'), 'utf8'));
const LOA = layout.loa;
const HB = layout.beam / 2 + 0.5; // label offset beyond the hull, from the centreline
const decks = JSON.parse(readFileSync(join(root, 'decks.json'), 'utf8'));
const outDir = join(root, 'drawings');
mkdirSync(outDir, {recursive: true});

const S = 11; // pixels per metre
const X0 = 70; // pixel x of the stern (0 m)
const Y0 = 110; // pixel y of the top of the plan (y = -6.5 m)
const YMIN = -6.5;
const PLAN_H = 13 * S;
const WIDTH = 960;
const DECK_H = 470;

const px = (x) => X0 + x * S;
const py = (y) => Y0 + (y - YMIN) * S;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function shoelace(poly) {
  let a = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x1, y1] = poly[i];
    const [x2, y2] = poly[(i + 1) % poly.length];
    a += x1 * y2 - x2 * y1;
  }
  return Math.abs(a) / 2;
}

// Break a room name into short lines that fit the room width.
function wrap(name, maxChars) {
  const words = name.replace(/:/g, ': ').split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > maxChars && cur) {
      lines.push(cur.trim());
      cur = w;
    } else {
      cur = (cur + ' ' + w).trim();
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

// Fill colour by room type, so routes, lifts and the accessible cabin read at a glance.
function fillFor(name) {
  if (/Mag-rail lift/.test(name)) return "#8fd0e6";
  if (/Accessible guest cabin/.test(name)) return "#c5e8c0";
  if (/lobby|passage|corridor|circulation/i.test(name)) return "#dfe9f5";
  return "#e3ebee";
}

// Draws one deck. dy shifts the drawing down for the overview sheet.
function drawDeck(ld, deck, dy = 0) {
  const parts = [];
  const g = (s) => parts.push(`<g transform="translate(0 ${dy})">${s}</g>`);

  const outline = ld.outline.map(([x, y]) => `${px(x)},${py(y)}`).join(' ');
  const outlineArea = shoelace(ld.outline);
  let assigned = 0;

  const pieces = [];
  // Grid every 10 m along the length
  for (let x = 0; x <= LOA; x += 10) {
    pieces.push(`<line x1="${px(x)}" y1="${py(-HB)}" x2="${px(x)}" y2="${py(HB)}" stroke="#cfd8dc" stroke-dasharray="2 4"/>`);
    pieces.push(`<text x="${px(x)}" y="${py(-HB) - 6}" font-size="9" fill="#78909c" text-anchor="middle">${x} m</text>`);
  }
  // Centreline
  pieces.push(`<line x1="${px(0)}" y1="${py(0)}" x2="${px(LOA)}" y2="${py(0)}" stroke="#90a4ae" stroke-dasharray="8 4 2 4"/>`);
  // Hull outline for this deck
  pieces.push(`<polygon points="${outline}" fill="#f7f3ea" stroke="#263238" stroke-width="1.6"/>`);

  // Rooms: solid rooms first, roof overlays last so they sit on top
  const ordered = [...ld.rooms.filter((r) => !r.roof), ...ld.rooms.filter((r) => r.roof)];
  for (const r of ordered) {
    const [x0, y0, x1, y1] = r.rect;
    const w = (x1 - x0) * S;
    const h = (y1 - y0) * S;
    const cx = (px(x0) + px(x1)) / 2;
    const cy = (py(y0) + py(y1)) / 2;
    if (r.roof) {
      pieces.push(`<rect x="${px(x0)}" y="${py(y0)}" width="${w}" height="${h}" fill="none" stroke="#8e3b6a" stroke-width="1.4" stroke-dasharray="6 4"/>`);
      pieces.push(`<text x="${cx}" y="${py(y1) - 6}" font-size="9" fill="#8e3b6a" text-anchor="middle">ROOF OVER AFT LIDO (overlay, not a level)</text>`);
      continue;
    }
    const area = (x1 - x0) * (y1 - y0);
    assigned += area;
    pieces.push(`<rect x="${px(x0)}" y="${py(y0)}" width="${w}" height="${h}" fill="${fillFor(r.name)}" stroke="#455a64" stroke-width="0.9"/>`);
    const lines = wrap(r.name, Math.max(8, Math.floor(w / 5.6)));
    const lineH = 11;
    const top = cy - ((lines.length + 1) * lineH) / 2 + 9;
    lines.forEach((ln, i) => {
      pieces.push(`<text x="${cx}" y="${top + i * lineH}" font-size="9" fill="#102027" text-anchor="middle">${esc(ln)}</text>`);
    });
    pieces.push(`<text x="${cx}" y="${top + lines.length * lineH}" font-size="8" fill="#546e7a" text-anchor="middle">${area.toFixed(0)} m²</text>`);
  }

  // Bow and stern markers
  pieces.push(`<text x="${px(0) - 6}" y="${py(-HB) + 14}" font-size="11" fill="#263238" text-anchor="end">STERN</text>`);
  pieces.push(`<text x="${px(LOA) + 6}" y="${py(-HB) + 14}" font-size="11" fill="#263238">BOW</text>`);

  // Title block
  const dl = deck.elevation;
  pieces.push(`<text x="${X0}" y="${py(HB) + 34}" font-size="13" font-weight="600" fill="#102027">P68 KETCH · ${esc(ld.name.toUpperCase())}</text>`);
  pieces.push(`<text x="${X0}" y="${py(HB) + 52}" font-size="10" fill="#37474f">Datum ${esc(dl)} · Zone: ${esc(deck.zone)}</text>`);
  pieces.push(`<text x="${X0}" y="${py(HB) + 68}" font-size="10" fill="#37474f">Assigned ${assigned.toFixed(0)} m² of ${outlineArea.toFixed(0)} m² deck outline (${((assigned / outlineArea) * 100).toFixed(0)}%). Unassigned area is open for layout.</text>`);
  pieces.push(`<text x="${X0}" y="${py(HB) + 84}" font-size="10" font-weight="600" fill="#8e3b6a">PROVISIONAL SCHEMATIC · NOT FOR CONSTRUCTION · NOT FOR FABRICATION · NOT SCALED</text>`);
  // Legend
  const legendItems=[["#8fd0e6","Mag-rail lift"],["#dfe9f5","Lobby / passage / circulation"],["#c5e8c0","Accessible guest cabin"],["#e3ebee","Other room"]];
  legendItems.forEach(([c,label],i)=>{const lx=X0+i*190;const ly=py(HB)+120;pieces.push(`<rect x="${lx}" y="${ly}" width="12" height="10" fill="${c}" stroke="#455a64"/><text x="${lx+17}" y="${ly+9}" font-size="9" fill="#37474f">${label}</text>`);});
  // Scale bar: 10 m
  pieces.push(`<line x1="${X0}" y1="${py(HB) + 96}" x2="${X0 + 10 * S}" y2="${py(HB) + 96}" stroke="#263238" stroke-width="2"/>`);
  pieces.push(`<text x="${X0}" y="${py(HB) + 110}" font-size="9" fill="#37474f">0</text>`);
  pieces.push(`<text x="${X0 + 10 * S}" y="${py(HB) + 110}" font-size="9" fill="#37474f" text-anchor="middle">10 m</text>`);
  pieces.push(`<text x="${WIDTH - 20}" y="${py(HB) + 110}" font-size="9" fill="#78909c" text-anchor="end">Source: layout/decks-layout.json · draft 00</text>`);

  g(pieces.join('\n'));
  return {svg: parts.join('\n'), assigned, outlineArea};
}

function wrapSvg(body, height, title) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${height}" viewBox="0 0 ${WIDTH} ${height}" font-family="Helvetica, Arial, sans-serif">
<title>${esc(title)}</title>
<rect width="${WIDTH}" height="${height}" fill="#ffffff"/>
${body}
</svg>
`;
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

// Individual deck sheets
let idx = 0;
for (const ld of layout.decks) {
  const deck = decks.find((d) => d.name === ld.name);
  idx += 1;
  const {svg} = drawDeck(ld, deck);
  const file = `deck-${String(idx).padStart(2, '0')}-${slug(ld.name)}.svg`;
  writeFileSync(join(outDir, file), wrapSvg(svg, DECK_H, `P68 Ketch ${ld.name} layout`));
  console.log(`wrote drawings/${file}`);
}

// Overview: all decks stacked, bridge at the top
const overviewParts = [];
let total = 0;
layout.decks.forEach((ld, i) => {
  const deck = decks.find((d) => d.name === ld.name);
  const {svg} = drawDeck(ld, deck, i * DECK_H);
  overviewParts.push(svg);
  total += 1;
});
writeFileSync(join(outDir, 'general-arrangement-overview.svg'),
  wrapSvg(overviewParts.join('\n'), DECK_H * total, 'P68 Ketch general arrangement overview (provisional)'));
console.log(`wrote drawings/general-arrangement-overview.svg (${total} decks stacked)`);
