# ADR-0003: Toyota EV powerplant: energy production only, feeding the bus

Status: Accepted (owner)

## Context

The Toyota EV platform's pack is about 355 V native. The owner directed that the powerplant does not drive propulsion.

## Decision

Powerplant feeds the bus through a converter. Native voltage 355 V is from secondary sources and must be verified. Step-up to 800 V is a ratio of 2.25.

## Open gates

- Powerplant rating and converter efficiency
- Marine rating of the automotive motor and inverter
- Exhaust routing for the engine (see ADR-0007)
