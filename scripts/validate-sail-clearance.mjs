// Sail clearance check. Each sail sector is tested in plan against the house envelopes and the
// deck above main. A sail is modelled as a triangle over its sector: its foot is at the boom (or clew)
// height at the outer edge, and its top reaches the mast top at the pivot, falling linearly with radius.
// A structure conflicts when its height band [base, roof] overlaps the sail's band at that point, with
// the margin. Also checks mast foundations against the main-deck houses, the clear side deck, and the
// enclosed area against the program.
// Run with: npm run validate:sails   (or: node scripts/validate-sail-clearance.mjs <layout.json>)
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const file = process.argv[2] ?? 'layout/sail-clearance-120m-4mast.json';
const c = JSON.parse(readFileSync(join(root, file), 'utf8'));
const errors = [];
const info = [];
const {loa, beam, clearance_margin_m: margin, heights_m: h} = c;
const cx = loa / 2, ay = loa / 2, by = beam / 2;
const halfWidthAt = (x) => by * Math.sqrt(Math.max(0, 1 - ((x - cx) / ay) ** 2));
const area = (r) => (r[2] - r[0]) * (r[3] - r[1]);
const baseOf = (hs) => (hs.base_key ? h[hs.base_key] : hs.base_m);
const roofOf = (hs) => h[hs.roof_key];
const STEP = 0.25;

// 1. Houses inside the hull outline
for (const hs of c.houses) {
  const [x0, y0, x1, y1] = hs.rect;
  for (const [x, y] of [[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) {
    if (((x - cx) / ay) ** 2 + (y / by) ** 2 > 1) errors.push(`${hs.name}: corner (${x}, ${y}) is outside the hull outline`);
  }
}

// 2. Mast foundations clear of main-deck houses
for (const m of c.masts) {
  const r = Math.sqrt(m.foundation_m2 / Math.PI);
  for (const hs of c.houses.filter((hh) => hh.deck === 'Main')) {
    const [x0, y0, x1, y1] = hs.rect;
    const dx = Math.max(x0 - m.x, 0, m.x - x1);
    const dy = Math.max(y0, -y1, 0);
    const gap = Math.hypot(dx, dy) - r;
    if (gap < margin) errors.push(`${m.name} mast foundation is ${gap.toFixed(2)} m from ${hs.name} (need ${margin} m)`);
  }
}

// 3. Sail sectors against houses: height bands overlap at a plan point
for (const s of c.sails) {
  const R = s.radius_m, half = (s.half_angle_deg * Math.PI) / 180;
  const zb = h[s.height_key], top = s.top_m;
  for (const hs of c.houses) {
    const base = baseOf(hs), roof = roofOf(hs);
    const [x0, y0, x1, y1] = hs.rect;
    let hit = false, worst = Infinity;
    for (let x = x0; x <= x1; x += STEP) {
      for (let y = y0; y <= y1; y += STEP) {
        const vx = x - s.pivot_x, vy = y - s.pivot_y;
        const r = Math.hypot(vx, vy);
        if (r > R || r === 0) continue;
        // sector axis points aft (toward smaller x)
        const ang = Math.acos(Math.min(1, Math.max(-1, -vx / r)));
        if (ang > half) continue;
        const zt = zb + (top - zb) * (1 - r / R); // sail top over this point
        if (roof <= zb - margin) continue; // structure entirely below the sail foot
        if (base >= zt + margin) continue; // structure entirely above the sail here
        hit = true;
        worst = Math.min(worst, (base - zt));
      }
    }
    if (hit) {
      errors.push(`${s.name} meets ${hs.name} (structure ${base}-${roof} m, sail ${zb}-${top} m; worst gap ${worst.toFixed(2)} m, need ${margin} m)`);
    } else {
      info.push(`${s.name}: clear of ${hs.name}`);
    }
  }
}

// 4. Clear side deck beside main-deck houses
let minSide = Infinity;
for (const hs of c.houses.filter((hh) => hh.deck === 'Main')) {
  const [x0, y0, x1, y1] = hs.rect;
  const hw = Math.max(Math.abs(y0), Math.abs(y1));
  for (let x = x0; x <= x1; x += 1) minSide = Math.min(minSide, halfWidthAt(x) - hw);
}
info.push(`Clear side deck beside the main-deck houses: ${minSide.toFixed(2)} m minimum`);
if (minSide < 2) errors.push(`Clear side deck ${minSide.toFixed(2)} m is under 2 m`);

// 5. Enclosed program against the house envelopes
const enclosed = c.houses.reduce((t, hs) => t + area(hs.rect), 0);
const gross = (Math.PI / 4) * loa * beam;
info.push(`Enclosed envelope ${enclosed.toFixed(0)} m2 against program ${c.program_enclosed_m2} m2 (main deck gross ${gross.toFixed(0)} m2)`);
if (enclosed < c.program_enclosed_m2) errors.push(`Enclosed envelope ${enclosed.toFixed(0)} m2 is ${(c.program_enclosed_m2 - enclosed).toFixed(0)} m2 short of the program`);

// 6. Sail heel. Each sail is a triangle: foot = sweep radius, luff = mast top minus foot height.
// Heeling moment M = q * A * Cf * h, summed over sails with the centre of effort at a third of the luff.
// Righting moment = displacement * g * GM. sin(heel) = M / righting (small-angle GZ = GM sin(heel)).
if (c.stability && c.sails) {
  const st = c.stability;
  const g = 9.81, rho = st.air_density_kg_m3, cf = st.cf;
  const rigs = c.sails.filter((s) => s.top_m);
  const sailRows = rigs.map((s) => {
    const zb = h[s.height_key];
    const A = 0.5 * s.radius_m * (s.top_m - zb) * (st.sail_area_scale ?? 1);
    const ce = zb + (s.top_m - zb) / 3;
    return {name: s.name, A, ce};
  });
  const totalA = sailRows.reduce((t, r) => t + r.A, 0);
  const righting = st.displacement_t * 1000 * g * st.gm_m; // N m per radian of sin
  info.push(`Sail area (triangle estimate) ${totalA.toFixed(0)} m2 across ${sailRows.length} sails; GM ${st.gm_m} m, displacement ${st.displacement_t} t`);
  info.push('Heel (deg) by true wind (kn):');
  const rows = [];
  for (const kn of st.wind_kn) {
    const v = kn * 0.5144;
    const q = 0.5 * rho * v * v;
    const M = sailRows.reduce((t, r) => t + q * r.A * cf * r.ce, 0);
    const heel = (Math.asin(Math.min(1, M / righting)) * 180) / Math.PI;
    rows.push(`${String(kn).padStart(3)} kn: ${heel.toFixed(1)} deg  (heeling moment ${(M / 1e6).toFixed(1)} MN m)`);
  }
  info.push(...rows.map((r) => '  ' + r));
  for (const limit of st.reef_heel_deg) {
    const target = Math.sin((limit * Math.PI) / 180) * righting; // heeling moment at the limit
    const sumA = sailRows.reduce((t, r) => t + r.A * r.ce, 0);
    const vKn = Math.sqrt((2 * target) / (rho * cf * sumA)) / 0.5144;
    info.push(`Wind at ${limit} deg heel (reef point, all sails set): ${vKn.toFixed(1)} kn`);
  }
}

console.log(info.join('\n'));
if (errors.length) {
  console.log(`\n${errors.length} clearance problem(s):`);
  for (const e of errors) console.log(`  - ${e}`);
  process.exitCode = 1;
} else {
  console.log(`\n${file} OK`);
}
