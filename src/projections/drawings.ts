// Projection: the list of drawing sheets and renders the app shows. Files live in public/.
export type Sheet = {file: string; title: string; note: string};
export type Render = {file: string; title: string};

// Engineering deck plans, plotted from the DXF sources in drawings/cad/ (scripts/drafting/cad_plans.py).
export const ENGINEERING: (Sheet & {dxf: string})[] = [
  {file: 'eng-deck-01-bridge.svg', dxf: 'P68-ENG-01-bridge.dxf', title: 'P68-ENG-01 Bridge', note: 'Deck status, room schedule, lift lobbies, roof access'},
  {file: 'eng-deck-02-commander-lido.svg', dxf: 'P68-ENG-02-commander-lido.dxf', title: 'P68-ENG-02 Commander and Lido', note: 'Deck status, lift lobby, roof overlay'},
  {file: 'eng-deck-03-main-master.svg', dxf: 'P68-ENG-03-main-master.dxf', title: 'P68-ENG-03 Main and Master', note: 'Deck status, public lift lobby, owner suite'},
  {file: 'eng-deck-04-tween.svg', dxf: 'P68-ENG-04-tween.dxf', title: 'P68-ENG-04 Tween', note: 'Deck status, accessible cabin, cabin route gap'},
  {file: 'eng-deck-05-tank-technical.svg', dxf: 'P68-ENG-05-tank-technical.dxf', title: 'P68-ENG-05 Tank and Technical', note: 'Deck status, tank envelopes, lift B'},
];
export const ENGINEERING_PDF = 'P68-engineering-deck-plans.pdf';

export const SHEETS: Sheet[] = [
  {file: 'general-arrangement-overview.svg', title: 'General arrangement overview', note: 'All five levels stacked'},
  {file: 'deck-01-bridge.svg', title: 'Bridge', note: 'Command position, lift A and B lobbies, roof access passage'},
  {file: 'deck-02-commander-lido.svg', title: 'Commander and Lido', note: 'Lifts, Commander lift lobby, roof overlay'},
  {file: 'deck-03-main-master.svg', title: 'Main and Master', note: 'Public lift lobby, owner suite, passages'},
  {file: 'deck-04-tween.svg', title: 'Tween', note: 'Accessible cabin opposite lift B, lobby'},
  {file: 'deck-05-tank-technical.svg', title: 'Tank and Technical', note: 'Lift B, technical corridor'},
  {file: 'elevation-port.svg', title: 'Port elevation', note: 'Schematic. Mast heights approximate. Cover to +11.70 m'},
  {file: 'elevation-aft.svg', title: 'Aft elevation', note: 'Schematic. Envelope widths approximate'},
];

export const RENDERS: Render[] = [
  {file: '01-bridge-helm.jpg', title: 'Bridge passage and command position'},
  {file: '02-commander-lookout-lift-lobby.jpg', title: 'Commander lookout and lift lobby'},
  {file: '03-main-salon-passage.jpg', title: 'Main salon, passage and owner suite doors'},
  {file: '04-tween-accessible-cabin.jpg', title: 'Tween corridor and accessible cabin'},
  {file: '05-tank-technical-corridor.jpg', title: 'Tank technical corridor'},
  {file: '06-aft-lido-exterior.jpg', title: 'Aft Lido with roof and pilot house cover'},
  {file: '07-outdoor-pilot-house.jpg', title: 'Outdoor pilot house helm'},
  {file: '08-bridge-lift-lobby.jpg', title: 'Bridge lift lobby'},
  {file: '09-main-lift-lobby.jpg', title: 'Main public lift lobby'},
  {file: '10-accessible-cabin-interior.jpg', title: 'Accessible cabin interior'},
  {file: '11-tween-lift-lobby.jpg', title: 'Tween lift lobby'},
  {file: '12-pilot-house-controls.jpg', title: 'Helm controls with touch screens'},
  {file: '13-sun-deck-events.jpg', title: 'Sun deck and events'},
];

// Deck explorer: the current plan for each deck level, keyed by the decks.json name.
const DECK_SHEET: Record<string, string> = {
  'Bridge': 'deck-01-bridge.svg',
  'Commander / Lido': 'deck-02-commander-lido.svg',
  'Main / Master': 'deck-03-main-master.svg',
  'Tween': 'deck-04-tween.svg',
  'Tank / Technical': 'deck-05-tank-technical.svg',
};

// Returns the current layout plan for a deck, or the fallback concept image.
export function deckPlanSrc(deckName: string, fallback: string): string {
  const sheet = DECK_SHEET[deckName];
  return sheet ? `/drawings/${sheet}` : fallback;
}

// Bird's-eye block views of each deck, with numbered rooms and a feature key.
export const BIRDSEYE: Sheet[] = [
  {file: 'birdseye-bridge.svg', title: "Bridge bird's-eye", note: 'Oblique block view with area and feature map'},
  {file: 'birdseye-commander-lido.svg', title: "Commander and Lido bird's-eye", note: 'Lifts, lobbies, Lido and lookout'},
  {file: 'birdseye-main-master.svg', title: "Main and Master bird's-eye", note: 'Public lift lobby, owner suite, galley'},
  {file: 'birdseye-tween.svg', title: "Tween bird's-eye", note: 'Accessible cabin and lift B lobby'},
  {file: 'birdseye-tank-technical.svg', title: "Tank and Technical bird's-eye", note: 'Tanks, bilges, technical corridor, lift B'},
];

// Deck explorer: the bird's-eye view for each deck level, keyed by the decks.json name.
const BIRDSEYE_BY_DECK: Record<string, string> = {
  'Bridge': 'birdseye-bridge.svg',
  'Commander / Lido': 'birdseye-commander-lido.svg',
  'Main / Master': 'birdseye-main-master.svg',
  'Tween': 'birdseye-tween.svg',
  'Tank / Technical': 'birdseye-tank-technical.svg',
};

export function deckBirdseyeSrc(deckName: string, fallback: string): string {
  const sheet = BIRDSEYE_BY_DECK[deckName];
  return sheet ? `/drawings/${sheet}` : fallback;
}

// Blender renders built from the DXF sources (scripts/drafting/render_*.py). Files live in public/renders/.
export type Shot = {file: string; title: string; note: string};
const DECK_FILES = ['01-bridge', '02-commander-lido', '03-main-master', '04-tween', '05-tank-technical'];
const DECK_TITLES = ['Bridge', 'Commander and Lido', 'Main and Master', 'Tween', 'Tank and Technical'];

export const FINISH_PLANS: Shot[] = DECK_FILES.map((f, i) => ({
  file: `finish/finish-plan-${f}.jpg`, title: `${DECK_TITLES[i]} finish-out plan`, note: 'Proposed finishes and furniture, walls cut at 1.10 m',
}));
export const CUTAWAYS: Shot[] = DECK_FILES.map((f, i) => ({
  file: `finish/cutaway-${f}.jpg`, title: `${DECK_TITLES[i]} cutaway`, note: 'Finish-out cutaway from the aft starboard quarter',
}));
// Rendered so far at full quality. Anchor, underway, dusk and the interiors are scripted in
// scripts/drafting/render_exteriors.py and render_interiors.py and are added here once rendered.
export const EXTERIORS: Shot[] = [
  {file: 'exterior/port.jpg', title: 'At port', note: 'Stern-to on the quay, golden hour'},
];
export const INTERIORS: Shot[] = [];
