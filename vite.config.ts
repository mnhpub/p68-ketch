import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import {fileURLToPath} from 'node:url';

// The public build reads filtered data from build/public/, so restricted systems
// never reach the bundle. See scripts/prepare-public.mjs.
const publicBuild = process.env.VITE_AUDIENCE === 'public';
const here = (p: string) => fileURLToPath(new URL(p, import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: publicBuild
    ? {
        alias: [
          {find: /^\.\.\/systems\.json$/, replacement: here('./build/public/systems.json')},
          {find: /^\.\.\/checklists\.json$/, replacement: here('./build/public/checklists.json')},
          {find: /^\.\.\/domains\.json$/, replacement: here('./build/public/domains.json')},
        ],
      }
    : undefined,
  build: {rollupOptions: {input: 'react.html'}},
});
