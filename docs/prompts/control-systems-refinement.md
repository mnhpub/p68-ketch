# Prompt: continued refinement of the P68 control systems

Paste the section below into a new Claude Code session on this repository. It is written against `main` as of
13 Oct 2026 (merge of PR #16). Check `git log` first; if the control files have moved on, update the inventory before
starting.

---

You are continuing the control-systems work on the P68 Ketch repository (`mnhpub/p68-ketch`). Work on a feature branch,
commit in small steps, and open a PR when done.

## Ground rules (do not break these)

1. **Public-side boundary.** This repository is the public side. The piloting screens are a simulation and send no
   commands to equipment. Do not add any route from the app to a vessel control system, and keep the concept banner.
   See `docs/control-software-architecture.md`, "Public side boundary".
2. **Safety lives in hardware.** The reducers encode operating rules (two-person rules, mode interlocks), not safety.
   Every hard limit you add must be listed as one the safety layer must enforce again (PLC, hardwired interlock or
   embedded controller). Never present supervisory software as the only safety layer.
3. **Pure reducers, tested.** Control logic stays in `src/aggregates/` as pure functions (state + command → new state),
   with commands typed in `src/commands/`. Every new rule gets a test in `tests/`. The UI in `src/piloting/` only renders
   state and dispatches commands.
4. **Concept status.** Every value you introduce is a placeholder unless the repo gives a source. Mark it as such, keep
   "not for construction" language, and do not claim compliance with any class, flag or IMO rule.
5. **One hull source.** Read dimensions from `layout/hull.json` (ADR-0011), never hard-code LOA, beam or mast stations.
6. **Keep docs in step.** Update `docs/piloting-console.md` (control rules table, open questions) and the relevant ADR or
   note in the same commit as the code.
7. **Checks before every push:** `npx tsc -b`, `npm test`, and the `validate:*` scripts. All must pass.

## Current control systems (inventory)

### A. Piloting console (simulation): `src/aggregates/pilot.ts`, `dock.ts`, `underway.ts`, `src/commands/pilot.ts`

| Function | Current behaviour |
|---|---|
| Two helm stations | Bridge (inside, +9.30 m) and outdoor pilot house (roof). One station holds authority. |
| Authority handover | Two-step: the other station requests, the holder accepts. |
| Propulsion demand | Port and starboard shafts, sliders in 5% steps. |
| Helm and rudder | 1° of rudder per helm turn, limit ±35° (`RUDDER_LIMIT`). |
| Autopilot | Engage with a 1.5 s hold, disengage with a 1 s hold. Not in reversion or dock mode. Trajectory tracking is not modelled. |
| Bow and stern thrusters | Sliders with a centre detent. Locked in dock mode. |
| Dock mode (booster assist) | Boosters follow the helm at 5% per turn, clamped to ±100%, and cancel the lateral disturbance from wind, current and waves (`lateralDisturbance`). Needs sails retracted. |
| Sail modes | Retracted, deployed and maintenance. Deploy is a 2 s hold, locked in dock mode. Retract is a safe-state action from either station. Sails are not modelled as a wind load. |
| Underway and route | Load a route, engage with a hold. Each waypoint needs two-station confirmation. Heading error is shown as a readout only. |
| Checklists | `underway-departure` and `dock-approach`, both draft. Critical steps gate each mode, and ticks clear when the mode disengages. |
| Emergency stop | Either station, 2 s hold. Zeroes demand and thrusters, ends autopilot, dock mode and underway. Only the holder can clear it. |
| Manual steering reversion | Requested by the holder, confirmed by the other station with a 2 s hold. |
| Redundancy display | Network, hardwired and local manual paths per subsystem, plus a simulated network fault. |
| Event log | On-screen only. No durable audit trail. |

### B. Systems register entries that are controls (`systems.json`, all `concept`, none reviewed)

- **Safety critical:** `command-and-control`, `navigation-systems`, `onboard-automation`, `side-thrusters`, `propulsion-600v`, `battery-storage`, `electrical-distribution`, `backup-power`, `anchor-system`, `sail-system`, `fuel-processing`, `diesel-generation`, `engineering-components`.
- **Supporting:** `external-communications`, `ship-communications`, `wifi-network` (network zones), `keycard-access`, `premise-security`, `checklist-system`.

### C. Control architecture notes

- `docs/control-software-architecture.md`: four layers (safety, device, supervision, connectivity), timing, network zones, updates, certification. Five open decisions.
- `docs/energy-management-architecture.md`: EMS duties (source selection, charging limits, load shedding order, quiet, underway, charge and emergency modes, BMS fault isolation, reading piloting state).
- `docs/genset-exhaust-and-systems.md`: genset start permissives, run toggles, and local panels whose protections the supervisory layer cannot override.
- `docs/tender-mag-rail-reload.md`: tender carriage interlocks and manual recovery.
- `docs/roll-control-gyro.md`: roll damping targets and gyro sizing (placeholders).
- `docs/ventilation-strategy.md`, `docs/bus-800v-design.md`: pressure zones and electrical interlocks.

### D. Known inconsistencies to resolve first

1. **Bus voltage:** `systems.json` still names `propulsion-600v` and a 600 V bus, but ADR-0002 selects 800 V DC. `docs/energy-management-architecture.md` also says 600 V.
2. **Hull scale:** ADR-0011 moves toward the 120 m concept. The roll-control note mixes 120 m inputs with 68 m results, and the piloting gains (booster per turn, disturbance gains) were never tied to a hull.
3. **Emergency stop scope** is open: does it cut propulsion power at the source, or only zero the demand?

## Tasks, in order

1. **Reconcile the data.** Fix the 600 V and 800 V mismatch across `systems.json`, the EMS note and the console text. If you rename the system id, keep `validate:systems` passing and keep public-release filtering correct. Add a test that fails on any remaining mismatch.
2. **Safety-layer register.** Add `layout/control-safety-functions.json` (or a similar data file). For each hard limit and interlock in the reducers (rudder limit, booster clamp, emergency stop effects, sail and dock interlock, reversion, underway gating), record the layer that must enforce it, the failure behaviour and the open question. Show it as a table on the Piloting console page and in `docs/piloting-console.md`.
3. **EMS link in the simulation.** Add a minimal energy state: battery state of charge, EMS mode (quiet, underway, charge, emergency) and available booster power. Dock mode and thrusters must respect available power. Below a reserve threshold the EMS enters emergency mode, with steering and navigation protected. Use pure reducers and tests, with placeholder values marked.
4. **Sail wind load.** Model deployed sails as a wind load in `lateralDisturbance`, as a placeholder sail area times a pressure coefficient. Add an alarm when dock mode would be needed with sails up (it is blocked today; explain why in the log).
5. **Autopilot track-keeping.** Replace the heading-error readout with a simple proportional rudder demand toward the active waypoint, rate-limited and capped at the rudder limit. It runs only with autopilot engaged and underway on. Test that it never exceeds the limit and hands back cleanly on disengage or emergency stop.
6. **Durable event log design.** Specify the log record (time, station, command, result, reason), with no backend. Add an export of the on-screen log to JSON, and write a short spec for retention and tamper evidence as open requirements.
7. **Open questions.** Answer or sharpen each item in `docs/piloting-console.md` "Open questions" and the five open decisions in `docs/control-software-architecture.md`. Where an answer is the owner's call, write the options with trade-offs and leave the decision open.

## Definition of done

- `npx tsc -b`, `npm test`, `npm run validate:layout`, `validate:access`, `validate:systems` and `validate:hull-envelope` all pass.
- New rules each have tests, including negative cases: wrong station, wrong mode, emergency stop active.
- `docs/piloting-console.md` control rules table and the safety-layer register match the code.
- No value is presented as approved, and nothing in the public build can reach equipment.
- The PR description lists every placeholder introduced and every question left for the owner.
