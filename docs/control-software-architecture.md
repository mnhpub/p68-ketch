# Control software architecture: principles for the public side

Status: principles only, for the public side. The control system is separate, unstarted work. Its platform, configuration, interfaces, network zones and certification route are not documented in this repository.

## The principle

Supervisory systems, in the separate control work, run supervision: the piloting screens, the energy management system (EMS), auto-dock calculations, logging, and the integration of sensors and networks. Safety functions do not depend on the operating system. They run on certified, deterministic hardware: PLCs, hardwired interlocks, and embedded controllers.

A general-purpose operating system is not a hard real-time or safety-certified platform. The design therefore assumes that the supervisory layer can fail, freeze or be compromised, and that the vessel stays safe when it does. This is the same rule the piloting console already states: the screen is a display and command surface, and the hardwired emergency stop and local manual controls must work without it (`docs/piloting-console.md`).

## Layers

| Layer | Runs on | Examples | Failure behaviour |
|---|---|---|---|
| Safety | Certified or hardwired logic (PLC, relays) | Emergency stop, fire and gas response, steering reversion, thruster and propulsion limits, battery protection trips | Acts without the supervisory layer |
| Device control | Embedded controllers | Generator governors, BMS cell protection, drive and converter control, rack cooling controllers | Holds a safe state if the supervisory layer is lost |
| Supervision | Supervisory platform (separate work) | Piloting screens, EMS, auto-dock demand, route and checklist state, sensor monitoring, event log | Degrades to the device layer; alarms raised |
| Connectivity | Separate network zones | Satellite link, guest networks, crew networks, shore connection | Never reaches the control zone directly |

## What the existing code tells us

The piloting logic is written as pure reducers in `src/aggregates/`. Each reducer takes a state and a command and returns a new state, with no browser or device calls. That makes it portable: the same logic can run in a supervisory service on the platform, or in a test harness, without change.

What the reducers do not do is enforce safety. They encode the two-person rules and the mode interlocks, which matter for correct operation. The hard limits must be enforced again in the safety layer, so that a bug or a compromised supervisory layer cannot exceed them. Examples: rudder and booster limits, the emergency stop that zeroes propulsion, and the sail and dock interlocks.

## Timing

- Auto-dock and EMS decisions run at a slow rate, which a supervisory platform can meet. Any loop that must act in milliseconds belongs in the device layer.
- Logs are time-stamped against a common clock, so that events across systems can be ordered after the fact.
- The piloting event log is the only audit trail at present (`docs/piloting-console.md`, "What this design does not include"). A supervisory platform makes a durable, tamper-evident log practical. That should be specified, not assumed.

## Network zones

- Control, crew, guest and satellite traffic run in separate zones, with no route from guest or satellite networks into control. This is in line with `systems.json`, where the onboard network entry says the design is not started and needs security review.
- The control zone carries no internet access. Updates reach it through a controlled path.
- Satellite carries data for monitoring and reporting, not commands.

## Updates and offline operation

- Every control function works without an internet or satellite connection.
- Software updates to supervisory systems are tested and staged before deployment, and the previous version can be restored.
- Device-layer firmware is updated only under a documented procedure, and never during underway or dock mode.

## Security

The security hardening of the repository is deferred to the testing phase, as recorded in the project's notes. This note adds one requirement for that phase: the control platform's configuration, access control, update path and network zones need a security review before any vessel use, and that review's findings should not be published in the public repository.

## Certification and approval

- Supervisory software is not certified. Its use in any safety-relevant role needs a route the class society and flag state accept, such as segregation and the hardware safety layer above, or a certified platform.
- Software that affects safety needs a documented development and verification process before use. That process is not yet defined.

## Open decisions

1. Which platform, support model and update policy. Kept out of the public repository.
2. Which functions run in the safety layer, and which of the supervisory functions above must be hardware-backed.
3. Network zones and their boundaries, including the satellite gateway.
4. Logging: the format, retention, tamper protection and who can read it.
5. Certification route for the supervisory software, and the class society's requirements.

## Public side boundary

This repository is the public side: the lookbook, the design data and the concept interfaces. The vessel's control system is a separate body of work and has not started. Its design, interfaces and platform are not documented here.

The one rule the public side must keep: the public build has no route to any vessel control system, and its helm and piloting screens send no commands to equipment. The concept banner on the piloting screen states this. Any future connection is a separate design, reviewed on its own, and is not added to this repository's public build.
