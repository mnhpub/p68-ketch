// Checks systems.json against domains.json. Run with: npm run validate:systems
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (name) => JSON.parse(readFileSync(join(root, name), 'utf8'));
const domains = load('domains.json');
const systems = load('systems.json');

const STATUSES = ['concept', 'reviewed', 'as-built'];
const BASES = ['target', 'model', 'tbd'];
const errors = [];
const domainIds = new Set(domains.map((d) => d.id));
const seen = new Set();

for (const d of domains) {
  if (!d.id || !d.label) errors.push(`domain ${JSON.stringify(d.id)} is missing id or label`);
}

for (const s of systems) {
  const where = `system ${s.id ?? '(no id)'}`;
  if (!s.id) errors.push('a system has no id');
  if (seen.has(s.id)) errors.push(`${where}: duplicate id`);
  seen.add(s.id);
  if (!domainIds.has(s.domain)) errors.push(`${where}: unknown domain "${s.domain}"`);
  if (!s.name) errors.push(`${where}: missing name`);
  if (!STATUSES.includes(s.status)) errors.push(`${where}: status must be one of ${STATUSES.join(', ')}`);
  if (typeof s.safety_critical !== 'boolean') errors.push(`${where}: safety_critical must be true or false`);
  if (typeof s.public_release !== 'boolean') errors.push(`${where}: public_release must be true or false`);
  if (!s.summary) errors.push(`${where}: missing summary`);
  if (!s.approval_status) errors.push(`${where}: missing approval_status`);
  if (!Array.isArray(s.related_decks)) errors.push(`${where}: related_decks must be an array`);
  if (!Array.isArray(s.risks)) errors.push(`${where}: risks must be an array`);
  if (s.safety_critical && (!Array.isArray(s.risks) || s.risks.length === 0)) {
    errors.push(`${where}: safety-critical systems must list at least one open risk`);
  }
  if (!Array.isArray(s.key_parameters) || s.key_parameters.length === 0) {
    errors.push(`${where}: needs at least one key parameter`);
  }
  for (const p of s.key_parameters ?? []) {
    if (!p.label || !p.value) errors.push(`${where}: parameter needs label and value`);
    if (!BASES.includes(p.basis)) errors.push(`${where}: parameter "${p.label}" basis must be one of ${BASES.join(', ')}`);
  }
}

const checklists = load('checklists.json');
const CHECKLIST_STATUSES = ['draft', 'approved'];
const checklistIds = new Set();
for (const c of checklists) {
  const where = `checklist ${c.id ?? '(no id)'}`;
  if (!c.id) errors.push('a checklist has no id');
  if (checklistIds.has(c.id)) errors.push(`${where}: duplicate id`);
  checklistIds.add(c.id);
  if (!seen.has(c.system)) errors.push(`${where}: unknown system "${c.system}"`);
  if (!c.title) errors.push(`${where}: missing title`);
  if (!CHECKLIST_STATUSES.includes(c.status)) errors.push(`${where}: status must be draft or approved`);
  if (!Array.isArray(c.steps) || c.steps.length === 0) errors.push(`${where}: needs at least one step`);
  for (const step of c.steps ?? []) {
    if (!step.text) errors.push(`${where}: a step has no text`);
    if (typeof step.critical !== 'boolean') errors.push(`${where}: step "${step.text}" critical must be true or false`);
  }
  // Phase 2: no checklist may be approved until a formal approval record exists.
  if (c.status === 'approved') errors.push(`${where}: approved status needs an approval record, none is set up yet`);
}

if (errors.length) {
  console.error(`systems.json / checklists.json: ${errors.length} problem(s)`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log(`systems.json OK: ${systems.length} systems across ${domains.length} domains`);
console.log(`checklists.json OK: ${checklists.length} checklist(s), all draft`);
