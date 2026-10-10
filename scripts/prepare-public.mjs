// Writes public-only copies of the data for the public build. Restricted systems
// are removed, and domain descriptions that name restricted topics are replaced,
// before bundling, so those details are not compiled into the public JavaScript.
// Output: build/public/.
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'build/public');
mkdirSync(out, {recursive: true});
const load = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));

// Restricted filtering is off during development: the public site shows every section.
// Set to true for the testing-phase public site.
const FILTER_RESTRICTED = false;

const allSystems = load('systems.json');
const systems = FILTER_RESTRICTED ? allSystems.filter((s) => s.public_release === true) : allSystems;
const ids = new Set(systems.map((s) => s.id));
const checklists = load('checklists.json').filter((c) => ids.has(c.system));

// A domain with any restricted system gets a neutral description, so restricted topics are not named.
const restrictedDomains = new Set(FILTER_RESTRICTED ? allSystems.filter((s) => !s.public_release).map((s) => s.domain) : []);
const domains = load('domains.json').map((d) => (restrictedDomains.has(d.id)
  ? {...d, description: 'Some systems in this domain are restricted. Details are available to authorised users.'}
  : d));

writeFileSync(join(out, 'systems.json'), JSON.stringify(systems, null, 2) + '\n');
writeFileSync(join(out, 'checklists.json'), JSON.stringify(checklists, null, 2) + '\n');
writeFileSync(join(out, 'domains.json'), JSON.stringify(domains, null, 2) + '\n');
console.log(`public data: ${systems.length} systems, ${checklists.length} checklists, ${domains.length} domains`);
