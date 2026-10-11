// Regression checks on the scaling figures recorded in the design notes. Each test recomputes a
// documented figure from its inputs. If an input changes, the test fails and the doc must be updated.
import {test} from 'node:test';
import assert from 'node:assert/strict';

const near = (a, b, tol) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b} (tol ${tol})`);

const rho = 1.025, Cb = 0.375, LWL = 62.0, B = 13.0;

test('draft at 1,487 t is 4.80 m, matching the keel-up target', () => {
  const V = 1487 / rho;
  const T = V / (Cb * LWL * B);
  near(T, 4.80, 0.01);
});

test('displacement at keel-up 4.8 m and keel-down 7.2 m', () => {
  near(rho * Cb * LWL * B * 4.8, 1487, 1);
  near(rho * Cb * LWL * B * 7.2, 2231, 2);
});

test('waterplane second moment and BM at the final size', () => {
  const I = (Math.PI / 64) * LWL * B ** 3;
  near(I, 6686, 2);
  near(I / (1487 / rho), 4.61, 0.01);
});

test('KG limit for GM 1.0 m is 6.01 m', () => {
  const V = 1487 / rho;
  const T = V / (Cb * LWL * B);
  const KB = T / 2;
  const BM = ((Math.PI / 64) * LWL * B ** 3) / V;
  near(KB + BM - 1.0, 6.01, 0.02);
});

test('hull speed and wave period at the chosen waterline', () => {
  const Vh = 1.34 * Math.sqrt(LWL * 3.28084);
  near(Vh, 19.1, 0.05);
  near(Math.sqrt((2 * Math.PI * LWL) / 9.81), 6.3, 0.05);
});

test('roll period at GM 1.0 m is 10.4 s', () => {
  const k = 0.4 * B;
  near((2 * Math.PI * k) / Math.sqrt(9.81 * 1.0), 10.43, 0.05);
});

test('drinking-water unit counts for each occupancy scenario', () => {
  const unit = 5 * 3.78541 * 0.6;
  const cases = [
    [14, 0, 5],
    [22, 0, 8],
    [34, 0, 12],
    [34, 4, 13],
    [100, 0, 36],
  ];
  for (const [people, pets, expected] of cases) {
    const demand = people * 4 + pets * 1;
    assert.equal(Math.ceil(demand / unit), expected, `${people} people, ${pets} pets`);
  }
});

test('galley-free reverse osmosis energy for 1,800 L/day is about 7 kWh', () => {
  near(1800 * 0.004, 7.2, 0.01);
});
