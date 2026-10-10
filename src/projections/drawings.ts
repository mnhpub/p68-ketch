// Projection: the list of drawing sheets and renders the app shows. Files live in public/.
export type Sheet = {file: string; title: string; note: string};
export type Render = {file: string; title: string};

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
  {file: '01-bridge-helm.jpg', title: 'Bridge helm and lounge'},
  {file: '02-commander-lookout-lift-lobby.jpg', title: 'Commander lookout and lift doors'},
  {file: '03-main-salon-passage.jpg', title: 'Main salon and passage'},
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
