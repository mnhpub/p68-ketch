# ADR-0007: Venting: separation by hazard class; no lift-shaft or pilot-house roof outlets

Status: Accepted (rules); pilot-house outlet blocked pending owner review

## Context

One source, one outlet. Hazardous, combustion and odour outlets never share a duct with occupied air. Lift shafts are passenger and escape routes. The pilot house roof is an occupied outdoor helm and guest area.

## Decision

Rules enforced by scripts/validate-ventilation.mjs. Genset exhaust outlet blocked at the pilot house roof. Multi-engine exhaust needs isolation and back-pressure checks.

## Open gates

- Stack location for gensets and the powerplant (stern or side alternative)
- Ventilation standards and air-change figures from the fire review
- 13 of 16 outlets have no physical position
