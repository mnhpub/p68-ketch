# ADR-0002: Propulsion: electric motors on an 800 V DC bus

Status: Proposed (owner direction, bus basis in docs/bus-800v-design.md)

## Context

Electric motor propulsion is the design. The bus voltage options were 355 V, 600 V and 800 V. The owner selected 800 V with headroom for continuous loads.

## Decision

800 V nominal, window 720 to 880 V, headroom H 1.25 on continuous current at minimum voltage, insulation at least 1,100 V. Supersedes the 600 V target in systems.json.

## Open gates

- Propulsion continuous power (not calculated; sets bus rating and cable)
- Headroom factor for marine continuous loads
- Systems register still says 600 V and must be updated
