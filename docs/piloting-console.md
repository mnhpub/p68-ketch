# Piloting console: design spec (concept)

Status: concept UI design. It is a simulation in the lookbook app and is not connected to any vessel system.
Source: `src/PilotingView.tsx`, `src/piloting/`.

## Purpose

Two crew can pilot the vessel from two helm stations: the **bridge** (inside, Station A in the code, `bridge`)
and the **outdoor pilot house** (Station B, `pilothouse`). Each station has touch control surfaces, and each
critical function has a second path and a manual path. The screen shows what is commanding the ship at any
moment and who is allowed to change it.

## Principles

1. **One station holds control.** Only the station holding control can change demands, rudder, thrusters or
   autopilot. The other station shows the same state and can request control.
2. **Handover is two-step.** The requester asks, and the holder accepts. The requester cannot take control on its own.
3. **Deliberate actuation.** Anything that moves the vessel, stops it, or changes control is press-and-hold,
   not a tap. Holds are 1–2 seconds, scaled to how consequential the action is.
4. **Two-person confirmation for reversion.** Manual steering reversion is requested by the holder and
   confirmed by the other station.
5. **Emergency stop is always available** from either station, regardless of who holds control.
6. **Every path is visible.** Each subsystem shows its network, hardwired and local manual paths and which one is active.
7. **Faults are alarms, not silent failovers.** A lost primary network is logged, and the active path changes visibly.

## Control rules

| Action | Who can do it | Gesture | Confirmation |
|---|---|---|---|
| Propulsion demand (port, starboard) | Holder, not in emergency stop | Drag slider, 5% steps | None; slider is continuous, so a stop is one drag away |
| Rudder | Holder, autopilot off | Buttons, 1° or 5° steps | None |
| Engage autopilot | Holder, not in reversion | Hold 1.5 s | Self |
| Disengage autopilot | Holder | Hold 1 s | Self |
| Bow and stern thrusters | Holder | Drag slider, centre detent | None |
| Request control | Non-holder | Tap | Holder must accept |
| Accept handover | Holder | Tap | Pending request required |
| Request manual reversion | Holder | Tap | Other station must confirm |
| Confirm manual reversion | Non-holder | Hold 2 s | Required |
| Emergency stop | Either station | Hold 2 s | None; zeroes demand and thrusters, disengages autopilot |
| Clear emergency stop | Holder only | Hold 2 s | Holder must have authority |

## Layout (per station)

- **Header:** station, who holds control, and status pills for emergency stop, mode, network and alarm count.
- **Authority strip:** states who holds control and offers the request or handover action.
- **Propulsion:** two vertical shaft sliders with detents at 0, 25, 50, 75 and 100%, and path status for each shaft.
- **Steering:** rudder readout and bar, five large nudge buttons, autopilot control, and the reversion workflow.
- **Thrusters:** bow and stern force sliders with a centre detent, and path status.
- **Alarm and event log:** the most recent eight events.
- **Footer:** emergency stop, always visible. Clear emergency stop appears only while the stop is active.

Night operation: palette is low brightness with no pure white. Alarms use dim red. A red-lit night mode should be
checked with the crew.

## Station locations

| Station | Location | What it changes for the design |
|---|---|---|
| Bridge | Inside, Bridge deck (+9.30 m) | Standard indoor helm. Glare from the window glazing needs checking. |
| Outdoor pilot house | Outside, roof of the aft Commander level above the Lido. Roof elevation not yet set. | Exposed to weather, spray, sun and cold. See below. |

**Outdoor pilot house requirements (to be designed):**

- **Screens:** readable in direct sun, and at night with the red-lit mode. Brightness and anti-glare treatment to be chosen.
- **Touch in the weather:** the touch surfaces must work with gloves and when wet. Consider a physical
  fallback for the critical controls (emergency stop, rudder, throttle) rather than relying on touch alone.
- **Enclosure:** the station's electronics need to be sealed and cooled for the exposed location.
- **Network route:** the outdoor station needs its own path to the primary network and a separate hardwired route.
  Both must avoid a single cable run that one incident can cut.
- **Emergency stop reachable:** the hardwired emergency stop must be reachable from the outdoor station, not only the bridge.
- **Sightlines:** the outdoor station's view forward and aft must be checked against the rig and mast.

The outdoor pilot house is recorded in `decks.json` as a roof item on the Commander / Lido level. Its roof elevation,
size and access route are not yet set. The roof is shared with a sun deck and an events area, so crowd loads and
emergency access apply. See `docs/outdoor-pilot-house-impact.md`.

## Redundancy model

| Subsystem | Network (primary) | Hardwired (secondary) | Local manual |
|---|---|---|---|
| Propulsion shafts | Normal command path | Takes over when network fails | Local field control, not commanded from the helm |
| Steering | Normal command path | Takes over when network fails | Hand steering gear; used under manual reversion |
| Thrusters | Normal command path | Takes over when network fails | Local field control |

The screen is a display and command surface only. The **hardwired emergency stop and the local manual controls
must work without the screen**. The UI must not be the only safety layer.

## Touch and accessibility

- Minimum target 56 px. Sliders use 64 px knobs and tracks at least 56 px wide.
- Sliders accept drag, tap, and arrow keys (one step per press).
- Hold buttons accept press-and-hold and keyboard Enter or Space held down.
- Disabled controls are dimmed and carry `aria-disabled`. Each control has an aria label.
- Layout collapses to two columns below 1100 px and one column below 680 px.

## What this design does not include

- No safety analysis, failure mode analysis, or hardware interlock design. These must come first.
- No bridge ergonomics or human-factors review. Required before any real-world use.
- No standard-specific compliance claims. Applicable navigation and bridge rules need review by the classification society and the flag state.
- No authentication or crew identity. Station identity is assumed, not verified.
- No audit trail beyond the on-screen log.

## Open questions

- Which functions need an independent hardwired control, not just the screen? The outdoor pilot house makes this more urgent.
- How is the outdoor pilot house reached from the Commander level and the bridge, and how is the roof separated from the events area?
- Does reversion need a timed override, or should it stay until reset?
- Should the emergency stop also cut power to propulsion at the source, or only zero the demand?
