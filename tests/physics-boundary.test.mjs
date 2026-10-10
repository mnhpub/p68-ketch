// Boundary tests: zero, limit and out-of-range inputs for the physics and the control clamps.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const require = createRequire(import.meta.url);
const pilot = require('./compiled/aggregates/pilot.js');
const dock = require('./compiled/aggregates/dock.js');
const {initialPilotState, pilotReducer, dockThrust, RUDDER_LIMIT, HELM_DEGREES_PER_ROTATION} = pilot;
const {initialEnvironment, lateralDisturbance, normalise} = dock;

test('zero environment gives zero lateral disturbance', () => {
  assert.equal(lateralDisturbance(initialEnvironment), 0);
});

test('dock thrust at zero rudder and zero environment is zero on both boosters', () => {
  assert.deepEqual(dockThrust(0, initialEnvironment), {bow: 0, stern: 0});
});

test('booster demand clamps at ±100% at the rudder limit', () => {
  const t = dockThrust(RUDDER_LIMIT, initialEnvironment);
  assert.equal(t.bow, -100);
  assert.equal(t.stern, 100);
});

test('booster demand clamps when rudder and environment push the same way', () => {
  const env = {...initialEnvironment, windKn: 60, windFromDeg: 270, headingDeg: 0};
  const t = dockThrust(RUDDER_LIMIT, env);
  assert.ok(t.bow >= -100 && t.bow <= 100);
  assert.ok(t.stern >= -100 && t.stern <= 100);
});

test('helm at exactly the limit is accepted and one step beyond is clamped', () => {
  const turns = RUDDER_LIMIT / HELM_DEGREES_PER_ROTATION;
  const s = pilotReducer(initialPilotState, {type: 'helm', turns, by: 'bridge'});
  assert.equal(s.rudder, RUDDER_LIMIT);
  const over = pilotReducer(s, {type: 'helm', turns: 1, by: 'bridge'});
  assert.equal(over.rudder, RUDDER_LIMIT);
});

test('normalise wraps headings into -180..180 at the boundaries', () => {
  assert.equal(normalise(0), 0);
  assert.equal(normalise(180), -180);
  assert.equal(normalise(-180), -180);
  assert.equal(normalise(360), 0);
  assert.equal(normalise(-90), -90);
});

test('a wind from exactly ahead (relative 0) gives no lateral push', () => {
  const env = {...initialEnvironment, windKn: 30, windFromDeg: 0, headingDeg: 0, waveM: 0};
  assert.ok(Math.abs(lateralDisturbance(env)) < 1e-9);
});

test('a wind from directly abeam pushes the vessel the other way: from port, to starboard', () => {
  const fromPort = {...initialEnvironment, windKn: 20, windFromDeg: 270, headingDeg: 0};
  const fromStbd = {...initialEnvironment, windKn: 20, windFromDeg: 90, headingDeg: 0};
  assert.ok(lateralDisturbance(fromPort) > 0);
  assert.ok(lateralDisturbance(fromStbd) < 0);
  assert.ok(Math.abs(lateralDisturbance(fromPort) + lateralDisturbance(fromStbd)) < 1e-9);
});

test('zero wind speed gives no wind push whatever the direction', () => {
  const env = {...initialEnvironment, windKn: 0, windFromDeg: 90, headingDeg: 0};
  assert.equal(lateralDisturbance(env), 0);
});

test('a current directly along the heading gives no lateral drift', () => {
  const env = {...initialEnvironment, currentKn: 3, currentSetDeg: 0, headingDeg: 0};
  assert.ok(Math.abs(lateralDisturbance(env)) < 1e-9);
});

test('a current from exactly abeam gives the full lateral drift', () => {
  const env = {...initialEnvironment, currentKn: 1, currentSetDeg: 90, headingDeg: 0};
  assert.ok(Math.abs(lateralDisturbance(env) - 10) < 1e-9);
});

test('a wind-driven push goes to zero when the wind is exactly along the heading, even in a gale', () => {
  const env = {...initialEnvironment, windKn: 60, windFromDeg: 180, headingDeg: 0, waveM: 0};
  assert.ok(Math.abs(lateralDisturbance(env)) < 1e-6);
});
