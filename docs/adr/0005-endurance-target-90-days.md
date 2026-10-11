# ADR-0005: Endurance target: 90 days

Status: Accepted (owner)

## Context

Owner set the endurance target to 90 days (previously 60).

## Decision

Energy budget recalculated at 90 days. Battery-only at 20 kW needs 450 t; diesel fuel for the same energy needs 10.4 t. Fuel is the energy source.

## Open gates

- Real hotel load profile (placeholders in weights/energy-budget.json)
- Fuel tank sizing and genset efficiency from a part-load curve
- App and systems text still say 60 days in places

## Concept decision (120 m four-mast, 1,487 t)

- Design basis: marine diesel through the gensets gives the 90-day endurance. Solar and shore charge the battery bank.
- The battery is a buffer for peaks and quiet running. It is not sized to carry the 90 days, so battery-only figures (450 t at 20 kW) are not the design case.
- 90-day fuel at 35% genset efficiency: about 10 t at 20 kW, 26 t at 50 kW, 52 t at 100 kW (`npm run validate:budgets`).
- Still open: real hotel load profile, fuel tank sizing and genset part-load curve.

