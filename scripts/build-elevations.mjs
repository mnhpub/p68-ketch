// Draws the port (side) and aft (end) elevations as SVG, schematic.
// Deck heights come from the vertical space schedule (P68-KETCH-E). Deck extents
// come from layout/decks-layout.json. The aft envelope widths are read
// approximately from the END ELEVATIONS sheet and the transverse section at
// station X=21 m. Output goes to drawings/.
// Run with: npm run build:elevations
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const layout = JSON.parse(readFileSync(join(root, 'layout/decks-layout.json'), 'utf8'));
const outDir = join(root, 'drawings');
mkdirSync(outDir, {recursive: true});

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const svg = (body, w, h, title) => `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" font-family="Helvetica, Arial, sans-serif">
<title>${esc(title)}</title>
<rect width="${w}" height="${h}" fill="#ffffff"/>
${body}
</svg>
`;

// Deck floor heights (m above DWL), from the vertical space schedule.
const FLOORS = [
  {name: 'Bridge', z: 9.3, next: 11.7},
  {name: 'Commander / Lido', z: 6.6, next: 9.3},
  {name: 'Main / Master', z: 3.35, next: 6.6},
  {name: 'Tween', z: 0.85, next: 3.35},
  {name: 'Tank / Technical', z: -1.5, next: 0.85},
];

// Extent of each deck along the length, from its rooms (roof overlays excluded).
function extent(name) {
  const deck = layout.decks.find((d) => d.name === name);
  const xs = deck.rooms.filter((r) => !r.roof).flatMap((r) => [r.rect[0], r.rect[2]]);
  return [Math.min(...xs), Math.max(...xs)];
}

// ---- Port elevation ----------------------------------------------------------
{
  const W = 1000;
  const H = 470;
  const SX = 9.8; // pixels per metre along the length
  const SZ = 11; // pixels per metre in height
  const px = (x) => 230 + x * SX;
  const pz = (z) => 350 - z * SZ;
  const parts = [];
  parts.push(`<text x="30" y="34" font-size="14" font-weight="600" fill="#102027">P68 KETCH · PORT ELEVATION (SCHEMATIC)</text>`);
  parts.push(`<text x="30" y="52" font-size="10" fill="#37474f">Deck heights from the vertical space schedule. Deck extents from the provisional layout. Mast positions approximate.</text>`);

  // Hull: waterline at z=0, bottom curve to z=-2.5 at midships
  const bottom = [];
  for (let x = 0; x <= 68; x += 1) {
    const z = -2.5 * Math.sqrt(Math.max(0, 1 - ((x - 34) / 34) ** 2));
    bottom.push(`${px(x)},${pz(z)}`);
  }
  parts.push(`<polygon points="${[`${px(0)},${pz(0)}`, `${px(68)},${pz(0)}`, ...bottom.reverse()].join(' ')}" fill="#15324a" stroke="#0a1f2e" stroke-width="1"/>`);
  parts.push(`<line x1="${px(0)}" y1="${pz(0)}" x2="${px(68)}" y2="${pz(0)}" stroke="#2a9fd6" stroke-dasharray="6 4"/>`);
  parts.push(`<text x="${px(68) + 6}" y="${pz(0) + 4}" font-size="9" fill="#2a9fd6">DWL</text>`);

  // Superstructure blocks and deck floors. Labels sit in a fixed left column.
  for (const f of FLOORS) {
    const [x0, x1] = extent(f.name);
    const fill = f.z >= 3.35 ? '#e8d4b2' : '#e9eef1';
    parts.push(`<rect x="${px(x0)}" y="${pz(f.next)}" width="${(x1 - x0) * SX}" height="${(f.next - f.z) * SZ}" fill="${fill}" stroke="#263238" stroke-width="0.8" opacity="0.92"/>`);
    parts.push(`<line x1="${px(x0)}" y1="${pz(f.z)}" x2="${px(x1)}" y2="${pz(f.z)}" stroke="#102027" stroke-width="2"/>`);
    parts.push(`<text x="${px(0) - 12}" y="${pz(f.z) + 4}" font-size="10" fill="#102027" text-anchor="end">${esc(f.name)} +${f.z.toFixed(2)} m</text>`);
  }

  // Pilot house cover over the aft roof: roof at +9.30 m, cover to +11.70 m (resolved)
  const [cx0, cx1] = [7.1, 20.1];
  parts.push(`<line x1="${px(cx0)}" y1="${pz(9.3)}" x2="${px(cx1)}" y2="${pz(9.3)}" stroke="#8e3b6a" stroke-width="2"/>`);
  parts.push(`<rect x="${px(cx0)}" y="${pz(11.7)}" width="${(cx1 - cx0) * SX}" height="${(11.7 - 9.3) * SZ}" fill="none" stroke="#8e3b6a" stroke-dasharray="6 4"/>`);
  parts.push(`<text x="${px((cx0 + cx1) / 2)}" y="${pz(10.5)}" font-size="9" fill="#8e3b6a" text-anchor="middle">Pilot house cover (+11.70 m)</text>`);

  // Twin mag-rail lifts at 48–51 m, serving Bridge to Tank (A: Main to Bridge)
  parts.push(`<rect x="${px(48)}" y="${pz(9.3)}" width="${3 * SX}" height="${(9.3 + 1.5) * SZ}" fill="#8fd0e6" stroke="#263238" stroke-width="0.8"/>`);
  parts.push(`<line x1="${px(48)}" y1="${pz(3.35)}" x2="${px(51)}" y2="${pz(3.35)}" stroke="#263238" stroke-width="0.8"/>`);
  parts.push(`<text x="${px(51) + 8}" y="${pz(12.4)}" font-size="9" fill="#102027">Mag-rail lifts A and B, forward (48–51 m)</text>`);
  parts.push(`<text x="${px(51) + 8}" y="${pz(11.5)}" font-size="8" fill="#546e7a">Lift A serves Main to Bridge. Lift B serves Tank to Bridge.</text>`);

  // Masts (approximate, from the longitudinal section)
  const mast = (x, z0, z1, label) => {
    parts.push(`<line x1="${px(x)}" y1="${pz(z0)}" x2="${px(x)}" y2="${pz(z1)}" stroke="#6b7c86" stroke-width="3"/>`);
    parts.push(`<text x="${px(x) + 6}" y="${pz(z1) + 4}" font-size="9" fill="#37474f">${label}</text>`);
  };
  mast(21.0, 6.5, 19, 'Mizzen (approx.)');
  mast(39.9, 7.8, 19, 'Main (approx.)');

  // Bow and stern, scale bar and title block
  parts.push(`<text x="${px(0) - 6}" y="${pz(-2.5) + 22}" font-size="11" fill="#263238" text-anchor="end">STERN</text>`);
  parts.push(`<text x="${px(68) + 6}" y="${pz(-2.5) + 22}" font-size="11" fill="#263238">BOW</text>`);
  parts.push(`<line x1="${px(0)}" y1="${pz(-2.5) + 40}" x2="${px(0) + 10 * SX}" y2="${pz(-2.5) + 40}" stroke="#263238" stroke-width="2"/>`);
  parts.push(`<text x="${px(0) + 10 * SX}" y="${pz(-2.5) + 54}" font-size="9" fill="#37474f" text-anchor="middle">10 m</text>`);
  parts.push(`<text x="${W - 20}" y="${H - 16}" font-size="9" fill="#8e3b6a" text-anchor="end">PROVISIONAL SCHEMATIC · NOT FOR CONSTRUCTION · Source: decks-layout.json, P68-KETCH-E</text>`);
  writeFileSync(join(outDir, 'elevation-port.svg'), svg(parts.join('\n'), W, H, 'P68 Ketch port elevation (schematic)'));
  console.log('wrote drawings/elevation-port.svg');
}

// ---- Aft elevation -----------------------------------------------------------
{
  const W = 620;
  const H = 540;
  const cy = 300; // centreline
  const py = (y) => cy + y * 22;
  const pz = (z) => 420 - z * 16;
  const parts = [];
  parts.push(`<text x="30" y="34" font-size="14" font-weight="600" fill="#102027">P68 KETCH · AFT ELEVATION (SCHEMATIC)</text>`);
  parts.push(`<text x="30" y="52" font-size="10" fill="#37474f">Envelope widths read approximately from the END ELEVATIONS sheet and the transverse section at X=21 m.</text>`);

  // Hull at station X=21: half-widths from the transverse section
  const side = [[5.5, 3.35], [5.0, 0], [4.2, -1.2], [2.6, -2.0], [0, -2.5]];
  const hullPts = [...side.map(([y, z]) => `${py(y)},${pz(z)}`), ...side.slice().reverse().map(([y, z]) => `${py(-y)},${pz(z)}`)];
  parts.push(`<polygon points="${hullPts.join(' ')}" fill="#15324a" stroke="#0a1f2e"/>`);
  parts.push(`<line x1="${py(-6)}" y1="${pz(0)}" x2="${py(6)}" y2="${pz(0)}" stroke="#2a9fd6" stroke-dasharray="6 4"/>`);
  parts.push(`<text x="${py(6) + 4}" y="${pz(0) + 4}" font-size="9" fill="#2a9fd6">DWL</text>`);

  // Superstructure envelopes, approximate half-widths per level
  const env = [
    {name: 'Tween', half: 5.0, z0: 0.85, z1: 3.35, fill: '#e9eef1'},
    {name: 'Main / Master', half: 4.4, z0: 3.35, z1: 6.6, fill: '#e8d4b2'},
    {name: 'Commander / Lido', half: 3.6, z0: 6.6, z1: 9.3, fill: '#e8d4b2'},
    {name: 'Bridge', half: 2.6, z0: 9.3, z1: 11.7, fill: '#e9eef1'},
  ];
  for (const e of env) {
    parts.push(`<rect x="${py(-e.half)}" y="${pz(e.z1)}" width="${e.half * 44}" height="${(e.z1 - e.z0) * 16}" fill="${e.fill}" stroke="#263238" stroke-width="0.8"/>`);
    parts.push(`<text x="${py(e.half) + 8}" y="${pz((e.z0 + e.z1) / 2) + 4}" font-size="10" fill="#102027">${esc(e.name)} +${e.z0.toFixed(2)} m</text>`);
  }
  // Mizzen and main at the centreline, from the section
  parts.push(`<line x1="${py(0)}" y1="${pz(11.7)}" x2="${py(0)}" y2="${pz(19)}" stroke="#6b7c86" stroke-width="3"/>`);
  parts.push(`<text x="${py(0) + 6}" y="${pz(18.5)}" font-size="9" fill="#37474f">Mizzen and main (centreline, approx.)</text>`);

  parts.push(`<text x="30" y="${H - 44}" font-size="9" fill="#37474f">Hull and superstructure widths are schematic.</text>`);
  parts.push(`<text x="30" y="${H - 30}" font-size="9" fill="#37474f">Lifts A and B sit on the centreline, forward, and are not shown in this end view.</text>`);
  parts.push(`<text x="${W - 20}" y="${H - 14}" font-size="9" fill="#8e3b6a" text-anchor="end">PROVISIONAL SCHEMATIC · NOT FOR CONSTRUCTION</text>`);
  writeFileSync(join(outDir, 'elevation-aft.svg'), svg(parts.join('\n'), W, H, 'P68 Ketch aft elevation (schematic)'));
  console.log('wrote drawings/elevation-aft.svg');
}
