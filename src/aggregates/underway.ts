// Underway navigation and piloting checklists. The route and checklist content are concept
// data, reviewed by no one yet. Checklists here are piloting procedures and are kept apart
// from the safety register in checklists.json.

import {normalise} from './dock';

export type ChecklistId = 'underway-departure' | 'dock-approach';

export type ChecklistStep = {text: string; critical: boolean};

export type Checklist = {title: string; mode: 'underway' | 'dock'; steps: ChecklistStep[]};

export const PILOT_CHECKLISTS: Record<ChecklistId, Checklist> = {
  'underway-departure': {
    title: 'Underway departure',
    mode: 'underway',
    steps: [
      {text: 'Confirm the route is loaded and the first waypoint is correct.', critical: true},
      {text: 'Confirm both stations show the same heading and position.', critical: true},
      {text: 'Confirm sails are stowed or set for the planned leg.', critical: true},
      {text: 'Confirm emergency stop works from both stations.', critical: true},
      {text: 'Log the departure time and the crew on watch.', critical: false},
    ],
  },
  'dock-approach': {
    title: 'Dock approach',
    mode: 'dock',
    steps: [
      {text: 'Confirm the berth, fenders and lines are ready.', critical: true},
      {text: 'Confirm sails are retracted.', critical: true},
      {text: 'Confirm the environment readings are current.', critical: true},
      {text: 'Confirm a lookout can see the berth from the helm.', critical: true},
    ],
  },
};

// Checks are stored by key: "<checklist id>:<step index>".
export const checkKey = (list: ChecklistId, index: number) => `${list}:${index}`;

export function checklistComplete(list: ChecklistId, checks: Record<string, boolean>): boolean {
  return PILOT_CHECKLISTS[list].steps.every((s, i) => !s.critical || checks[checkKey(list, i)]);
}

export function clearChecklist(list: ChecklistId, checks: Record<string, boolean>): Record<string, boolean> {
  const next: Record<string, boolean> = {};
  for (const [k, v] of Object.entries(checks)) if (!k.startsWith(`${list}:`)) next[k] = v;
  return next;
}

export type Waypoint = {name: string; bearingDeg: number; distanceNm: number};

// Concept route for the demo. Real routes come from the navigation system.
export const DEMO_ROUTE: Waypoint[] = [
  {name: 'Anchorage approach', bearingDeg: 45, distanceNm: 3.2},
  {name: 'Berth entrance', bearingDeg: 80, distanceNm: 0.8},
];

// Heading error to the course. Positive means the course lies to starboard of the heading.
export const headingError = (courseDeg: number, headingDeg: number) => normalise(courseDeg - headingDeg);
