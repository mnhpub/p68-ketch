// Behaviour tests for the piloting aggregate. Run with: npm test
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const require = createRequire(import.meta.url);
const pilot = require('./compiled/aggregates/pilot.js');
const dock = require('./compiled/aggregates/dock.js');
const underway = require('./compiled/aggregates/underway.js');
const {initialPilotState, pilotReducer, dockThrust, RUDDER_LIMIT} = pilot;
const {initialEnvironment} = dock;
const {checkKey, PILOT_CHECKLISTS} = underway;

const run = (state, actions) => actions.reduce(pilotReducer, state);

// Ticks every critical step of a checklist.
const ticked = (list, state = initialPilotState) => {
  const checks = {...state.checks};
  PILOT_CHECKLISTS[list].steps.forEach((s, i) => {
    if (s.critical) checks[checkKey(list, i)] = true;
  });
  return {...state, checks};
};

test('helm moves the rudder 1 degree per turn and clamps at the limit', () => {
  let s = run(initialPilotState, [{type: 'helm', turns: 5, by: 'bridge'}]);
  assert.equal(s.rudder, 5);
  s = run(s, [{type: 'helm', turns: -2, by: 'bridge'}]);
  assert.equal(s.rudder, 3);
  s = run(s, [{type: 'helm', turns: 100, by: 'bridge'}]);
  assert.equal(s.rudder, RUDDER_LIMIT);
});

test('helm is refused from the station without control', () => {
  const s = run(initialPilotState, [{type: 'helm', turns: 5, by: 'pilothouse'}]);
  assert.equal(s.rudder, 0);
});

test('dock thrust: 5% per helm turn, bow and stern opposed for yaw', () => {
  const t = dockThrust(5, initialEnvironment);
  assert.equal(t.bow, -25);
  assert.equal(t.stern, 25);
});

test('dock mode needs the departure-independent dock checklist, sails retracted, and no autopilot', () => {
  const blocked = run(initialPilotState, [{type: 'dock', on: true, by: 'bridge'}]);
  assert.equal(blocked.dock, false, 'refused without checklist');
  const ready = run(ticked('dock-approach'), [{type: 'dock', on: true, by: 'bridge'}]);
  assert.equal(ready.dock, true);
  assert.deepEqual(ready.thrust, {bow: 0, stern: 0});
});

test('thrusters cannot be set by hand in dock mode', () => {
  const s = run(ticked('dock-approach'), [{type: 'dock', on: true, by: 'bridge'}, {type: 'thrust', side: 'bow', value: 50, by: 'bridge'}]);
  assert.equal(s.thrust.bow, 0);
});

test('wind from port with zero yaw gives equal negative booster demand (starboard push compensated)', () => {
  const env = {...initialEnvironment, windKn: 20, windFromDeg: 270, headingDeg: 0};
  const t = dockThrust(0, env);
  assert.ok(t.bow < 0, 'bow demand compensates the starboard push');
  assert.equal(t.bow, t.stern);
});

test('underway needs a route and the departure checklist', () => {
  const noRoute = run(ticked('underway-departure'), [{type: 'underway', on: true, by: 'bridge'}]);
  assert.equal(noRoute.underway, false);
  const route = [{name: 'A', bearingDeg: 0, distanceNm: 1}];
  const s = run(ticked('underway-departure'), [
    {type: 'route', waypoints: route, by: 'bridge'},
    {type: 'underway', on: true, by: 'bridge'},
  ]);
  assert.equal(s.underway, true);
});

test('waypoint confirmation needs the other station', () => {
  const route = [{name: 'A', bearingDeg: 0, distanceNm: 1}, {name: 'B', bearingDeg: 90, distanceNm: 1}];
  let s = run(ticked('underway-departure'), [
    {type: 'route', waypoints: route, by: 'bridge'},
    {type: 'underway', on: true, by: 'bridge'},
    {type: 'waypointRequest', by: 'bridge'},
  ]);
  const same = pilotReducer(s, {type: 'waypointConfirm', by: 'bridge'});
  assert.equal(same.activeWaypoint, 0, 'holder cannot confirm own request');
  s = pilotReducer(s, {type: 'waypointConfirm', by: 'pilothouse'});
  assert.equal(s.activeWaypoint, 1);
});

test('emergency stop ends dock mode and underway, and zeroes the boosters', () => {
  const s = run(ticked('dock-approach'), [
    {type: 'dock', on: true, by: 'bridge'},
    {type: 'estop', by: 'pilothouse'},
  ]);
  assert.equal(s.dock, false);
  assert.equal(s.underway, false);
  assert.deepEqual(s.thrust, {bow: 0, stern: 0});
});

test('sails: deploy refused in dock mode, retract allowed from either station during emergency stop', () => {
  let s = run(ticked('dock-approach'), [{type: 'dock', on: true, by: 'bridge'}]);
  assert.equal(pilotReducer(s, {type: 'sails', mode: 'deploy', by: 'bridge'}).sails, 'retracted');
  s = run(initialPilotState, [
    {type: 'sails', mode: 'deploy', by: 'bridge'},
    {type: 'estop', by: 'bridge'},
    {type: 'sails', mode: 'retract', by: 'pilothouse'},
  ]);
  assert.equal(s.sails, 'retracted');
});
