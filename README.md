# P68 Ketch · Interactive Presentation Studio

A 22-chapter architectural presentation for the 120-meter (approximately 394-foot) four-mast expedition ketch.


## React / TypeScript

After installing Node.js, in this folder run:

```sh
npm install
npm run dev
```

Visit **http://localhost:5173/react.html**. `src/App.tsx` and `src/styles.css` are the editable application. The Vite build uses `react.html` as the React entrypoint; `index.html` is intentionally the network-free preview. The React code imports `slides.json` and `decks.json`.

## Navigation

- `←` and `→` move through slides
- Chapters and slide index allow direct navigation
- Deck Explorer browses five preliminary floor/technical levels
- Fabrication Workflow reviews the digital-to-steel process
- Design Register separates concepts from hydrostatic model parameters
- Click images to view enlarged source assets
- Fullscreen icon enters immersive mode where supported

## Drawings and renders

Engineering deck plans are AutoCAD DXF sources in `drawings/cad/`, plotted to `drawings/P68-engineering-deck-plans.pdf`.
Finish-out plans, cutaways, exterior and interior renders are made in Blender from those DXF files. See
`docs/drafting-and-rendering.md`.

## Data and quality restrictions

Ten low-resolution presentation images have been replaced with individually regenerated luxury concept visuals, 1536–1774 px wide, with detailed walnut, ivory upholstery, stone and brass finishes. The three existing exterior compositions now carry Greek flags. Technical drawings are unchanged. Both presentations use the new full-resolution WebP assets in `public/assets/`; original source images are retained. Prompts and output filenames are recorded in `IMAGE_GENERATION.json` (built-in image_gen). These are illustrative AI concept renders, not coordinated architectural or engineering models.

The design remains **concept-stage only**. The reference canoe-body is approximately 786.3 m³ (around 806 t displaced seawater), not a verified lightship or full-load mass. Planned 60-day endurance, lifting keel, and mag-rail elevator remain unverified. Fabrication concepts are not CNC-ready files. See `DESIGN_RELEASE_POLICY.md`.
