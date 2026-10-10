// Regenerates the inline data in index.html from the JSON sources.
// The view code in index.html is hand-written; only the data block between
// "const slides=" and "const sections=" is replaced. Run with: npm run build:standalone
import {readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const load = (name) => JSON.parse(readFileSync(join(root, name), 'utf8'));

const block = [
  `const slides=${JSON.stringify(load('slides.json'))};`,
  `const decks=${JSON.stringify(load('decks.json'))};`,
  `const systems=${JSON.stringify(load('systems.json'))};`,
  `const domains=${JSON.stringify(load('domains.json'))};`,
  `const checklists=${JSON.stringify(load('checklists.json'))};`,
  '',
].join('\n');

const path = join(root, 'index.html');
const html = readFileSync(path, 'utf8');
const start = html.indexOf('const slides=');
const end = html.indexOf('const sections=');
if (start < 0 || end < 0 || end < start) {
  console.error('index.html: could not find the data block markers "const slides=" and "const sections="');
  process.exit(1);
}

writeFileSync(path, html.slice(0, start) + block + html.slice(end));
console.log('index.html data block regenerated from JSON sources');
