"use strict";
// Underway navigation and piloting checklists. The route and checklist content are concept
// data, reviewed by no one yet. Checklists here are piloting procedures and are kept apart
// from the safety register in checklists.json.
Object.defineProperty(exports, "__esModule", { value: true });
exports.headingError = exports.DEMO_ROUTE = exports.checkKey = exports.PILOT_CHECKLISTS = void 0;
exports.checklistComplete = checklistComplete;
exports.clearChecklist = clearChecklist;
const dock_1 = require("./dock");
exports.PILOT_CHECKLISTS = {
    'underway-departure': {
        title: 'Underway departure',
        mode: 'underway',
        steps: [
            { text: 'Confirm the route is loaded and the first waypoint is correct.', critical: true },
            { text: 'Confirm both stations show the same heading and position.', critical: true },
            { text: 'Confirm sails are stowed or set for the planned leg.', critical: true },
            { text: 'Confirm emergency stop works from both stations.', critical: true },
            { text: 'Log the departure time and the crew on watch.', critical: false },
        ],
    },
    'dock-approach': {
        title: 'Dock approach',
        mode: 'dock',
        steps: [
            { text: 'Confirm the berth, fenders and lines are ready.', critical: true },
            { text: 'Confirm sails are retracted.', critical: true },
            { text: 'Confirm the environment readings are current.', critical: true },
            { text: 'Confirm a lookout can see the berth from the helm.', critical: true },
        ],
    },
};
// Checks are stored by key: "<checklist id>:<step index>".
const checkKey = (list, index) => `${list}:${index}`;
exports.checkKey = checkKey;
function checklistComplete(list, checks) {
    return exports.PILOT_CHECKLISTS[list].steps.every((s, i) => !s.critical || checks[(0, exports.checkKey)(list, i)]);
}
function clearChecklist(list, checks) {
    const next = {};
    for (const [k, v] of Object.entries(checks))
        if (!k.startsWith(`${list}:`))
            next[k] = v;
    return next;
}
// Concept route for the demo. Real routes come from the navigation system.
exports.DEMO_ROUTE = [
    { name: 'Anchorage approach', bearingDeg: 45, distanceNm: 3.2 },
    { name: 'Berth entrance', bearingDeg: 80, distanceNm: 0.8 },
];
// Heading error to the course. Positive means the course lies to starboard of the heading.
const headingError = (courseDeg, headingDeg) => (0, dock_1.normalise)(courseDeg - headingDeg);
exports.headingError = headingError;
