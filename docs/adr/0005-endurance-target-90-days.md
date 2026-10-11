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
