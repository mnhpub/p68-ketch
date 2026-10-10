// Systems dynamics: energy, fuel, battery room and water systems, checked against the figures in
// weights/energy-budget.json and the notes in docs/.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const energy = JSON.parse(readFileSync(join(root, 'weights/energy-budget.json'), 'utf8'));
const days = energy.endurance_target_days;
const spec = energy.battery_specific_energy_kwh_per_kg;
const dod = energy.usable_depth_of_discharge;
const lhv = energy.fuel_option.lower_heating_value_kwh_per_kg;
const eta = energy.fuel_option.genset_electrical_efficiency;

const energyKwh = (kw) => kw * 24 * days;
const batteryT = (kwh) => kwh / (spec * dod) / 1000;
const fuelT = (kwh, e = eta) => kwh / (e * lhv) / 1000;

test('90-day energy at 20 kW is 43.2 MWh', () => {
  assert.ok(Math.abs(energyKwh(20) - 43200) < 1e-6);
});

test('battery-only mass scales linearly with load (same energy twice needs twice the mass)', () => {
  assert.ok(Math.abs(batteryT(2 * energyKwh(20)) / batteryT(energyKwh(20)) - 2) < 1e-9);
});

test('battery-only mass at 20 kW is about 450 t over 90 days at 0.12 kWh/kg and 80% DoD', () => {
  assert.ok(Math.abs(batteryT(energyKwh(20)) - 450) < 0.5);
});

test('fuel mass falls as genset efficiency rises', () => {
  assert.ok(fuelT(energyKwh(20), 0.42) < fuelT(energyKwh(20), 0.35));
  assert.ok(fuelT(energyKwh(20), 0.35) < fuelT(energyKwh(20), 0.30));
});

test('fuel at 35% efficiency for 20 kW over 90 days is about 10.4 t', () => {
  assert.ok(Math.abs(fuelT(energyKwh(20)) - 10.4) < 0.05);
});

test('battery-to-fuel mass ratio at 20 kW is about 43 at 0.12 kWh/kg', () => {
  const ratio = batteryT(energyKwh(20)) / fuelT(energyKwh(20));
  assert.ok(Math.abs(ratio - 43) < 1);
});

test('battery room: 400 kWh usable needs 500 kWh nameplate; eight racks take 84 six-kWh modules', () => {
  const nameplate = 400 / dod;
  assert.equal(nameplate, 500);
  assert.equal(Math.floor((8 * 42) / 4), 84);
  assert.ok(Math.abs(nameplate / 84 - 5.95) < 0.05);
});

test('battery room heat: 3% loss at 100 kW peak gives 3 kW, and 375 W per rack across eight racks', () => {
  const heat = 100 * 0.03;
  assert.equal(heat, 3);
  assert.equal((heat * 1000) / 8, 375);
});

test('battery room airflow per rack at 10 K rise: about 112 m³/h for eight racks', () => {
  const m3s = 375 / (1.2 * 1005 * 10);
  assert.ok(Math.abs(m3s * 3600 - 112) < 1);
});

test('atmospheric capture: 5 gal unit derated to 60% gives about 11.4 L/day', () => {
  const unit = 5 * 3.78541 * 0.6;
  assert.ok(Math.abs(unit - 11.36) < 0.05);
});

test('reverse osmosis energy at 0.004 kWh/L is far below atmospheric capture at 0.4 kWh/L', () => {
  assert.ok(0.4 / 0.004 >= 100);
});

test('exhaust heat recovery: 20 kW load at 35% gives about 57 kW fuel and 17 kW exhaust', () => {
  const fuelKw = 20 / 0.35;
  assert.ok(Math.abs(fuelKw - 57.1) < 0.1);
  assert.ok(Math.abs(0.3 * fuelKw - 17.1) < 0.1);
});

test('exhaust heat to electricity at 10% is under 5% of the 20 kW load', () => {
  const orcKw = 0.5 * 0.3 * (20 / 0.35) * 0.1;
  assert.ok(orcKw / 20 < 0.05);
});
