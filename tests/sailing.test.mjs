// Sailing dynamics: stability, heel, natural periods and hull speed, checked against the closed-form
// relations in docs/hull-dynamics-first-pass.md.
import {test} from 'node:test';
import assert from 'node:assert/strict';

const g = 9.81, rho = 1.025, rhoAir = 1.225;
const LOA = 68.0, LWL = 62.0, B = 13.0, Cb = 0.375, Cwp = 0.70, DISP_T = 1487;
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

test('metacentric height limits: KG for GM 1.0 m is 6.01 m', () => {
  assert.ok(Math.abs(KB + BM - 1.0 - 6.01) < 0.02);
});

test('heel rises with the square of wind speed (doubling wind roughly quadruples the heeling moment)', () => {
  const q15 = 0.5 * rhoAir * (15 * 0.5144) ** 2;
  const q30 = 0.5 * rhoAir * (30 * 0.5144) ** 2;
  assert.ok(Math.abs(q30 / q15 - 4) < 1e-9);
});

test('heel at GM 1.0 m for the placeholder sail: 1.8, 3.2 and 7.2 degrees at 15, 20 and 30 kn', () => {
  assert.ok(Math.abs(heelDeg(15, 1.0) - 1.8) < 0.1);
  assert.ok(Math.abs(heelDeg(20, 1.0) - 3.2) < 0.1);
  assert.ok(Math.abs(heelDeg(30, 1.0) - 7.2) < 0.2);
});

test('a higher GM gives less heel for the same wind', () => {
  assert.ok(heelDeg(20, 1.5) < heelDeg(20, 1.0));
});

test('roll period: 10.4 s at GM 1.0 m, and shorter at higher GM', () => {
  const k = 0.4 * B;
  const roll = (GM) => (2 * Math.PI * k) / Math.sqrt(g * GM);
  assert.ok(Math.abs(roll(1.0) - 10.43) < 0.05);
  assert.ok(roll(1.5) < roll(1.0));
});

test('heave period: short for a hull this size', () => {
  const Awp = Cwp * LWL * B;
  const Th = 2 * Math.PI * Math.sqrt(V / (g * Awp));
  assert.ok(Math.abs(Th - 3.2) < 0.05);
});

test('hull speed 19.1 kn and the wave of hull length has a period of about 6.3 s', () => {
  const Vh = 1.34 * Math.sqrt(LWL * 3.28084);
  assert.ok(Math.abs(Vh - 19.1) < 0.05);
  assert.ok(Math.abs(Math.sqrt((2 * Math.PI * LWL) / g) - 6.3) < 0.05);
});

test('draft from the 1,487 t target matches the 4.8 m keel-up target', () => {
  assert.ok(Math.abs(T - 4.80) < 0.01);
});
