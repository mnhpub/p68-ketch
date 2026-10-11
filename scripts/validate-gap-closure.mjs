// Gap closure check for the 120 m four-mast concept. Reads layout/gap-closure.json. Automated steps are
// tested against the repository. Manual steps close only when "done": true is recorded in the register,
// with the evidence named in its "evidence" field. A gap is closed when every step is done.
// Run with: npm run validate:gaps   (exit code 1 if any gap check is in error)
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {execSync} from 'node:child_process';
import {existsSync} from 'node:fs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));
const register = load('layout/gap-closure.json');
const hull = load('layout/hull.json');
const sail = load('layout/sail-clearance-120m-4mast.json');
const weights = load('weights/weight-register.json');
const budget = load('layout/envelope-budget.json');
const decks = load('layout/decks-layout.json');
const scope = readFileSync(join(root, 'scope.json'), 'utf8');

const run = (cmd) => {
  try {
    return {ok: true, out: execSync(cmd, {cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe']})};
  } catch (e) {
    return {ok: false, out: String(e.stdout ?? '') + String(e.stderr ?? '')};
  }
};

const checks = {
  register_coverage_95() {
    const ref = weights.reference_displacement_t;
    const covered = weights.items.reduce((t, i) => t + (i.mass_t ?? 0), 0);
    const pct = (100 * covered) / ref;
    return {pass: pct >= 95, detail: `${pct.toFixed(0)}% of ${ref} t covered`};
  },
  reference_matches_concept() {
    const a = weights.reference_displacement_t, b = sail.stability.displacement_t;
    return {pass: a === b && sail.stability.draft_m === 1.8, detail: `register ${a} t, concept ${b} t at ${sail.stability.draft_m} m draft`};
  },
  budgets_no_draft_flag() {
    const r = run('node scripts/validate-design-budgets.mjs');
    const flagged = /FLAG implied draft/.test(r.out);
    return {pass: !flagged, detail: flagged ? 'implied draft flag still raised (uniform outline)' : 'no draft flag'};
  },
  battery_share_reviewed() {
    const r = run('node scripts/validate-design-budgets.mjs');
    const flags = (r.out.match(/FLAG .*battery alone needs/g) ?? []).length;
    return {pass: flags === 0, detail: `${flags} battery-only load(s) above the 10% review limit`};
  },
  access_passes() {
    const r = run('node scripts/validate-access.mjs');
    return {pass: r.ok, detail: r.ok ? 'no gaps' : 'accessibility gaps reported'};
  },
  sail_matches_hull() {
    const ok = sail.loa === hull.loa && sail.beam === hull.beam;
    return {pass: ok, detail: `sail file ${sail.loa} m by ${sail.beam} m, hull ${hull.loa} m by ${hull.beam} m`};
  },
  sails_pass() {
    const r = run('node scripts/validate-sail-clearance.mjs layout/sail-clearance-120m-4mast.json');
    return {pass: r.ok, detail: r.ok ? 'clearances pass' : 'clearance problems'};
  },
  ventilation_clear() {
    const r = run('node scripts/validate-ventilation.mjs');
    const problems = /problem\(s\)/.test(r.out) || !r.ok;
    return {pass: !problems, detail: problems ? 'blocking ventilation problem' : 'no blocking problems'};
  },
  av_renders_exist() {
    const slugs = ['theatre', 'cinema', 'broadcast-main-stage', 'broadcast-side-stage', 'broadcast-production-control', 'av-media-room'];
    const missing = slugs.filter((s) => !existsSync(join(root, 'drawings/renders/interior', `${s}.jpg`)));
    return {pass: missing.length === 0, detail: missing.length ? `missing: ${missing.join(', ')}` : 'all six present'};
  },
  medical_pet_on_tween() {
    const want = ['Medical bay', 'Pet resort suites'];
    const ok = want.every((w) => budget.requests.some((q) => q.item.startsWith(w) && q.deck === 'Tween'));
    return {pass: ok, detail: ok ? 'both on Tween' : 'not both on Tween'};
  },
  systems_have_gates() {
    const systems = load('systems.json');
    const missing = systems.filter((x) => !x.approval_status || !x.risks?.length).map((x) => x.id);
    return {pass: missing.length === 0, detail: missing.length ? `no gate or risk recorded for: ${missing.join(', ')}` : `${systems.length} systems each name a review gate and list risks`};
  },
  scope_no_stale_figures() {
    // A 68 m-era figure is stale only when the text presents it as current. Items labelled as archived,
    // superseded or history are allowed to keep their figures.
    const historical = /archiv|superseded|history|earlier|previous/i;
    const figure = /\b68 ?m\b|\b64\.0 m\b|\b806 t\b|\b1,350 t\b|\b4\.8 m\b/;
    const items = [...scope.matchAll(/"((?:[^"\\]|\\.)*)"/g)].map((m) => m[1]);
    const stale = items.filter((t) => figure.test(t) && !historical.test(t));
    return {pass: stale.length === 0, detail: stale.length ? `${stale.length} item(s) present 68 m-era figures as current` : 'none'};
  },
};

let errors = 0;
const rows = [];
for (const g of register.gaps) {
  const results = g.checklist.map((step) => {
    if (step.auto) {
      const fn = checks[step.check];
      if (!fn) return {step: step.step, status: 'error', detail: `unknown check ${step.check}`};
      const r = fn();
      return {step: step.step, status: r.pass ? 'done' : 'open', detail: r.detail};
    }
    return {step: step.step, status: step.done ? 'done' : 'open (manual)', detail: step.evidence ?? ''};
  });
  if (results.some((r) => r.status === 'error')) errors++;
  const done = results.filter((r) => r.status === 'done').length;
  const closed = done === results.length;
  rows.push({g, results, closed, done});
}

const pad = (s, n) => String(s).padEnd(n);
console.log(pad('ID', 5) + pad('SEV', 10) + pad('STEPS', 8) + pad('STATUS', 9) + 'TITLE');
for (const r of rows) {
  console.log(pad(r.g.id, 5) + pad(r.g.severity, 10) + pad(`${r.done}/${r.results.length}`, 8) + pad(r.closed ? 'closed' : 'open', 9) + r.g.title);
  for (const s of r.results) if (s.status !== 'done') console.log(`        - ${s.status}: ${s.step}${s.detail ? ` (${s.detail})` : ''}`);
}
const closed = rows.filter((r) => r.closed).length;
console.log(`\n${closed} of ${rows.length} gaps closed; ${rows.length - closed} open.`);
if (errors) {
  console.log(`${errors} gap(s) have a check error.`);
  process.exitCode = 1;
}
