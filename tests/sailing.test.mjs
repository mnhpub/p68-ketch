// Sailing dynamics: stability, heel, natural periods and hull speed, checked against the closed-form
// relations in the concept note docs/concept-120m-four-mast.md.
import {test} from 'node:test';
import assert from 'node:assert/strict';

const g = 9.81, rho = 1.025, rhoAir = 1.225;
const LOA = 120.0, LWL = 120.0 * 0.912, B = 20.0, Cb = 0.375, Cwp = 0.70, DISP_T = 1487;
const V = DISP_T / rho;
const T = V / (Cb * LWL * B);
const I = (Math.PI / 64) * LWL * B ** 3;
const BM = I / V;
const KB = T / 2;

const heelDeg = (windKn, GM, sailArea = 600, cf = 0.7, h = 30) => {
  const q = 0.5 * rhoAir * (windKn * 0.5144) ** 2;
  const M = q * sailArea * cf * h;
  const s = M / (DISP_T * 1000 * g * GM);
  return (Math.asin(Math.min(1, s)) * 180) / Math.PI;
};

test('metacentric height limit: KG for GM 2.13 m is about 28.4 m (the rig is well below it)', () => {
  assert.ok(Math.abs(KB + BM - 2.13 - 28.4) < 0.1);
});

test('heel rises with the square of wind speed (doubling wind roughly quadruples the heeling moment)', () => {
  const q15 = 0.5 * rhoAir * (15 * 0.5144) ** 2;
  const q30 = 0.5 * rhoAir * (30 * 0.5144) ** 2;
  assert.ok(Math.abs(q30 / q15 - 4) < 1e-9);
});

test('heel grows with wind and falls with GM for the same sail', () => {
  assert.ok(heelDeg(30, 2.13, 4000, 0.7, 22) > heelDeg(20, 2.13, 4000, 0.7, 22));
  assert.ok(heelDeg(20, 2.5, 4000, 0.7, 22) < heelDeg(20, 2.13, 4000, 0.7, 22));
});

test('roll period: 11.0 s at GM 2.13 m, and shorter at higher GM', () => {
  const k = 0.4 * B;
  const roll = (GM) => (2 * Math.PI * k) / Math.sqrt(g * GM);
  assert.ok(Math.abs(roll(2.13) - 11.0) < 0.05);
  assert.ok(roll(2.5) < roll(2.13));
});

test('heave period: short for a hull this size', () => {
  const Awp = Cwp * LWL * B;
  const Th = 2 * Math.PI * Math.sqrt(V / (g * Awp));
  assert.ok(Math.abs(Th - 1.95) < 0.05);
});

test('hull speed 25.4 kn and the wave of hull length has a period of about 8.4 s', () => {
  const Vh = 1.34 * Math.sqrt(LWL * 3.28084);
  assert.ok(Math.abs(Vh - 25.4) < 0.05);
  assert.ok(Math.abs(Math.sqrt((2 * Math.PI * LWL) / g) - 8.4) < 0.05);
});

test('draft from the 1,487 t target is about 1.8 m (the concept draft)', () => {
  assert.ok(Math.abs(T - 1.8) < 0.05);
});
