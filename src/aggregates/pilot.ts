// Concept state for the two-station piloting screen. Nothing here is sent to
// equipment. The reducer encodes the two-person rules: one station holds
// control at a time, handover is requested and accepted, and manual reversion
// is requested at one station and confirmed at the other.

import type {PilotAction} from '../commands/pilot';
import {type Environment, initialEnvironment, lateralDisturbance} from './dock';
import {checklistComplete, clearChecklist, type ChecklistId, type Waypoint} from './underway';

export type Station = 'bridge' | 'pilothouse';

export const STATION_NAME: Record<Station, string> = {
  bridge: 'Bridge',
  pilothouse: 'Outdoor pilot house',
};
export const stationName = (s: Station) => STATION_NAME[s];
export type Shaft = 'port' | 'stbd';
export type Side = 'bow' | 'stern';
export type Level = 'info' | 'warn' | 'alarm';
export type SailState = 'retracted' | 'deployed' | 'maintenance';

export type LogEntry = {
  id: number;
  level: Level;
  text: string;
};

export type PilotState = {
  authority: Station;
  pendingRequest: Station | null;
  demand: Record<Shaft, number>;
  rudder: number;
  autopilot: boolean;
  thrust: Record<Side, number>;
  // Dock mode: hand steering with bow and stern boosters assisting the rudder, auto-compensated for environment.
  dock: boolean;
  environment: Environment;
  sails: SailState;
  // Underway: route legs, the active leg, and two-station confirmation of each waypoint.
  underway: boolean;
  route: Waypoint[];
  activeWaypoint: number;
  waypointPending: Station | null;
  // Checklist ticks, keyed "<checklist id>:<step index>".
  checks: Record<string, boolean>;
  estop: boolean;
  networkFault: boolean;
  reversionPending: Station | null;
  reversion: boolean;
  log: LogEntry[];
};


export const otherStation = (s: Station): Station => (s === 'bridge' ? 'pilothouse' : 'bridge');

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export const RUDDER_LIMIT = 35;

// Helm ratio: each full rotation of the helm wheel moves the rudder this many degrees.
// Positive turns are starboard, negative turns are port.
export const HELM_DEGREES_PER_ROTATION = 1;

// Dock mode booster assist: thruster force per helm turn of rudder. At 1° per turn,
// each turn adds this many percent of bow and stern thrust, in opposite directions,
// so the boosters swing the bow the same way as the rudder.
export const BOOSTER_PERCENT_PER_ROTATION = 5;

// Booster demand for dock mode. Yaw comes from the rudder (1° per turn). Sideways force
// cancels the lateral disturbance from wind, current and sea state. With bow and stern
// forces b and s: sideways = (b + s) / 2 and yaw = (s - b) / 2, so b = sideways - yaw and s = sideways + yaw.
// Positive thrust is starboard. Starboard rudder: bow pushes port, stern pushes starboard.
export const dockThrust = (rudder: number, env: Environment): Record<Side, number> => {
  const yaw = (rudder / HELM_DEGREES_PER_ROTATION) * BOOSTER_PERCENT_PER_ROTATION;
  const sideways = clamp(-lateralDisturbance(env), -100, 100);
  return {
    // + 0 turns a negative zero into zero, so a settled booster reads as off.
    bow: clamp(Math.round(sideways - yaw), -100, 100) + 0,
    stern: clamp(Math.round(sideways + yaw), -100, 100) + 0,
  };
};

export const initialPilotState: PilotState = {
  authority: 'bridge',
  pendingRequest: null,
  demand: { port: 0, stbd: 0 },
  rudder: 0,
  autopilot: false,
  thrust: { bow: 0, stern: 0 },
  dock: false,
  environment: initialEnvironment,
  sails: 'retracted',
  underway: false,
  route: [],
  activeWaypoint: 0,
  waypointPending: null,
  checks: {},
  estop: false,
  networkFault: false,
  reversionPending: null,
  reversion: false,
  log: [{ id: 1, level: 'info', text: 'Control held on the bridge. Propulsion at zero.' }],
};

// Only the station holding control can change demands, while the system is not in emergency stop.
export function canCommand(state: PilotState, by: Station): boolean {
  return !state.estop && state.authority === by;
}

export function pilotReducer(state: PilotState, action: PilotAction): PilotState {
  const addLog = (level: Level, text: string) => [...state.log, { id: state.log.length + 1, level, text }];

  switch (action.type) {
    case 'demand':
      if (!canCommand(state, action.by)) return state;
      return { ...state, demand: { ...state.demand, [action.shaft]: clamp(action.value, 0, 100) } };

    case 'helm': {
      // Manual rudder is locked while autopilot is engaged.
      if (!canCommand(state, action.by) || state.autopilot) return state;
      const rudder = clamp(state.rudder + action.turns * HELM_DEGREES_PER_ROTATION, -RUDDER_LIMIT, RUDDER_LIMIT);
      return { ...state, rudder, thrust: state.dock ? dockThrust(rudder, state.environment) : state.thrust };
    }

    case 'centre':
      if (!canCommand(state, action.by) || state.autopilot) return state;
      return { ...state, rudder: 0, thrust: state.dock ? dockThrust(0, state.environment) : state.thrust };

    case 'autopilot':
      if (!canCommand(state, action.by) || (action.on && (state.reversion || state.dock))) return state;
      return {
        ...state,
        autopilot: action.on,
        log: addLog('info', action.on ? `Autopilot engaged at ${stationName(action.by)}` : `Autopilot disengaged at ${stationName(action.by)}`),
      };

    case 'thrust':
      // In dock mode the boosters are set from the rudder and environment, not by hand.
      if (!canCommand(state, action.by) || state.dock) return state;
      return { ...state, thrust: { ...state.thrust, [action.side]: clamp(action.value, -100, 100) } };

    case 'dock':
      if (!canCommand(state, action.by) || action.on === state.dock) return state;
      // Dock mode is hand steering only, so it cannot start under autopilot or with sails up.
      if (action.on && (state.autopilot || state.underway || state.sails !== 'retracted')) return state;
      if (action.on && !checklistComplete('dock-approach', state.checks)) return state;
      return action.on
        ? {
            ...state,
            dock: true,
            thrust: dockThrust(state.rudder, state.environment),
            log: addLog('info', `Dock mode engaged at ${stationName(action.by)}. Auto-dock compensation on.`),
          }
        : {
            ...state,
            dock: false,
            thrust: { bow: 0, stern: 0 },
            checks: clearChecklist('dock-approach', state.checks),
            log: addLog('info', `Dock mode disengaged at ${stationName(action.by)}. Boosters off.`),
          };

    case 'environment': {
      // Sensor inputs. Any station may update them, since they are readings and not commands.
      const environment = { ...state.environment, ...action.patch };
      return { ...state, environment, thrust: state.dock ? dockThrust(state.rudder, environment) : state.thrust };
    }

    case 'sails':
      switch (action.mode) {
        case 'deploy':
          // Sails only go up at the helm, not in dock mode, and not from maintenance.
          if (!canCommand(state, action.by) || state.sails !== 'retracted' || state.dock) return state;
          return { ...state, sails: 'deployed', log: addLog('info', `Sails deployed at ${stationName(action.by)}`) };
        case 'retract':
          // Stowing the sails is a safe-state action, so either station can do it, even during emergency stop.
          if (state.sails !== 'deployed') return state;
          return { ...state, sails: 'retracted', log: addLog('info', `Sails retracted at ${stationName(action.by)}`) };
        case 'maintenance':
          if (!canCommand(state, action.by) || state.sails !== 'retracted') return state;
          return { ...state, sails: 'maintenance', log: addLog('warn', `Sails locked for maintenance at ${stationName(action.by)}`) };
        case 'endMaintenance':
          if (!canCommand(state, action.by) || state.sails !== 'maintenance') return state;
          return { ...state, sails: 'retracted', log: addLog('info', `Sail maintenance lock released at ${stationName(action.by)}. Sails stowed.`) };
      }
      return state;

    case 'underway':
      if (!canCommand(state, action.by) || action.on === state.underway) return state;
      if (action.on) {
        // Underway needs a route with legs left, no dock mode, and the departure checklist complete.
        if (state.dock || state.route.length === 0 || state.activeWaypoint >= state.route.length) return state;
        if (!checklistComplete('underway-departure', state.checks)) return state;
        return { ...state, underway: true, log: addLog('info', `Underway engaged at ${stationName(action.by)}. Leg 1 of ${state.route.length}.`) };
      }
      return {
        ...state,
        underway: false,
        waypointPending: null,
        checks: clearChecklist('underway-departure', state.checks),
        log: addLog('info', `Underway disengaged at ${stationName(action.by)}.`),
      };

    case 'route':
      // The route can only change while not underway.
      if (!canCommand(state, action.by) || state.underway) return state;
      return {
        ...state,
        route: action.waypoints,
        activeWaypoint: 0,
        waypointPending: null,
        log: addLog('info', `Route loaded: ${action.waypoints.length} waypoints.`),
      };

    case 'waypointRequest':
      // The holder asks to confirm arrival at the active waypoint. The other station confirms.
      if (!canCommand(state, action.by) || !state.underway || state.waypointPending !== null) return state;
      if (state.activeWaypoint >= state.route.length) return state;
      return { ...state, waypointPending: action.by, log: addLog('info', `Waypoint ${state.route[state.activeWaypoint].name} reached. Confirmation requested at ${stationName(action.by)}.`) };

    case 'waypointConfirm': {
      if (!state.underway || state.waypointPending === null || action.by === state.waypointPending || state.estop) return state;
      const reached = state.route[state.activeWaypoint].name;
      const next = state.activeWaypoint + 1;
      const done = next >= state.route.length;
      return {
        ...state,
        activeWaypoint: next,
        waypointPending: null,
        underway: done ? false : state.underway,
        log: addLog(
          'info',
          done
            ? `Waypoint ${reached} confirmed at ${stationName(action.by)}. Route complete. Underway ends.`
            : `Waypoint ${reached} confirmed at ${stationName(action.by)}. Leg ${next + 1} of ${state.route.length}.`,
        ),
      };
    }

    case 'check':
      // Checklist ticks can be made from either station, but only while that mode is off.
      if (action.list === 'underway-departure' ? state.underway : state.dock) return state;
      return { ...state, checks: { ...state.checks, [`${action.list}:${action.index}`]: action.done } };

    case 'request':
      if (action.by === state.authority || state.estop) return state;
      return { ...state, pendingRequest: action.by, log: addLog('info', `${stationName(action.by)} requests control`) };

    case 'cancelRequest':
      return { ...state, pendingRequest: null };

    case 'accept':
      // The holding station hands over. The requester is not asked to confirm.
      if (action.by !== state.authority || state.pendingRequest === null) return state;
      return {
        ...state,
        authority: state.pendingRequest,
        pendingRequest: null,
        log: addLog('info', `Control handed over to ${stationName(state.pendingRequest)}`),
      };

    case 'estop':
      return {
        ...state,
        estop: true,
        demand: { port: 0, stbd: 0 },
        thrust: { bow: 0, stern: 0 },
        autopilot: false,
        dock: false,
        underway: false,
        waypointPending: null,
        checks: clearChecklist('underway-departure', state.checks),
        log: addLog('alarm', `Emergency stop activated at ${stationName(action.by)}. Propulsion demand set to zero.`),
      };

    case 'clearEstop':
      if (action.by !== state.authority) return state;
      return { ...state, estop: false, log: addLog('warn', `Emergency stop cleared at ${stationName(action.by)}`) };

    case 'reversionRequest':
      if (action.by !== state.authority || state.reversion || state.estop) return state;
      return { ...state, reversionPending: action.by, log: addLog('warn', `Manual reversion requested at ${stationName(action.by)}`) };

    case 'reversionConfirm':
      // Confirmation must come from the other station.
      if (state.reversionPending === null || action.by === state.reversionPending) return state;
      return {
        ...state,
        reversion: true,
        reversionPending: null,
        autopilot: false,
        log: addLog('warn', `Manual steering reversion confirmed at ${stationName(action.by)}. Autopilot disengaged.`),
      };

    case 'reversionCancel':
      return { ...state, reversionPending: null };

    case 'networkFault':
      return {
        ...state,
        networkFault: action.on,
        log: addLog(
          action.on ? 'alarm' : 'info',
          action.on ? 'Primary network control lost. Hardwired path active.' : 'Primary network control restored.',
        ),
      };

    case 'reset':
      return initialPilotState;
  }
}
