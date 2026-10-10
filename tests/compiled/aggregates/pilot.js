"use strict";
// Concept state for the two-station piloting screen. Nothing here is sent to
// equipment. The reducer encodes the two-person rules: one station holds
// control at a time, handover is requested and accepted, and manual reversion
// is requested at one station and confirmed at the other.
Object.defineProperty(exports, "__esModule", { value: true });
exports.initialPilotState = exports.dockThrust = exports.BOOSTER_PERCENT_PER_ROTATION = exports.HELM_DEGREES_PER_ROTATION = exports.RUDDER_LIMIT = exports.otherStation = exports.stationName = exports.STATION_NAME = void 0;
exports.canCommand = canCommand;
exports.pilotReducer = pilotReducer;
const dock_1 = require("./dock");
const underway_1 = require("./underway");
exports.STATION_NAME = {
    bridge: 'Bridge',
    pilothouse: 'Outdoor pilot house',
};
const stationName = (s) => exports.STATION_NAME[s];
exports.stationName = stationName;
const otherStation = (s) => (s === 'bridge' ? 'pilothouse' : 'bridge');
exports.otherStation = otherStation;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
exports.RUDDER_LIMIT = 35;
// Helm ratio: each full rotation of the helm wheel moves the rudder this many degrees.
// Positive turns are starboard, negative turns are port.
exports.HELM_DEGREES_PER_ROTATION = 1;
// Dock mode booster assist: thruster force per helm turn of rudder. At 1° per turn,
// each turn adds this many percent of bow and stern thrust, in opposite directions,
// so the boosters swing the bow the same way as the rudder.
exports.BOOSTER_PERCENT_PER_ROTATION = 5;
// Booster demand for dock mode. Yaw comes from the rudder (1° per turn). Sideways force
// cancels the lateral disturbance from wind, current and sea state. With bow and stern
// forces b and s: sideways = (b + s) / 2 and yaw = (s - b) / 2, so b = sideways - yaw and s = sideways + yaw.
// Positive thrust is starboard. Starboard rudder: bow pushes port, stern pushes starboard.
const dockThrust = (rudder, env) => {
    const yaw = (rudder / exports.HELM_DEGREES_PER_ROTATION) * exports.BOOSTER_PERCENT_PER_ROTATION;
    const sideways = clamp(-(0, dock_1.lateralDisturbance)(env), -100, 100);
    return {
        // + 0 turns a negative zero into zero, so a settled booster reads as off.
        bow: clamp(Math.round(sideways - yaw), -100, 100) + 0,
        stern: clamp(Math.round(sideways + yaw), -100, 100) + 0,
    };
};
exports.dockThrust = dockThrust;
exports.initialPilotState = {
    authority: 'bridge',
    pendingRequest: null,
    demand: { port: 0, stbd: 0 },
    rudder: 0,
    autopilot: false,
    thrust: { bow: 0, stern: 0 },
    dock: false,
    environment: dock_1.initialEnvironment,
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
function canCommand(state, by) {
    return !state.estop && state.authority === by;
}
function pilotReducer(state, action) {
    const addLog = (level, text) => [...state.log, { id: state.log.length + 1, level, text }];
    switch (action.type) {
        case 'demand':
            if (!canCommand(state, action.by))
                return state;
            return { ...state, demand: { ...state.demand, [action.shaft]: clamp(action.value, 0, 100) } };
        case 'helm': {
            // Manual rudder is locked while autopilot is engaged.
            if (!canCommand(state, action.by) || state.autopilot)
                return state;
            const rudder = clamp(state.rudder + action.turns * exports.HELM_DEGREES_PER_ROTATION, -exports.RUDDER_LIMIT, exports.RUDDER_LIMIT);
            return { ...state, rudder, thrust: state.dock ? (0, exports.dockThrust)(rudder, state.environment) : state.thrust };
        }
        case 'centre':
            if (!canCommand(state, action.by) || state.autopilot)
                return state;
            return { ...state, rudder: 0, thrust: state.dock ? (0, exports.dockThrust)(0, state.environment) : state.thrust };
        case 'autopilot':
            if (!canCommand(state, action.by) || (action.on && (state.reversion || state.dock)))
                return state;
            return {
                ...state,
                autopilot: action.on,
                log: addLog('info', action.on ? `Autopilot engaged at ${(0, exports.stationName)(action.by)}` : `Autopilot disengaged at ${(0, exports.stationName)(action.by)}`),
            };
        case 'thrust':
            // In dock mode the boosters are set from the rudder and environment, not by hand.
            if (!canCommand(state, action.by) || state.dock)
                return state;
            return { ...state, thrust: { ...state.thrust, [action.side]: clamp(action.value, -100, 100) } };
        case 'dock':
            if (!canCommand(state, action.by) || action.on === state.dock)
                return state;
            // Dock mode is hand steering only, so it cannot start under autopilot or with sails up.
            if (action.on && (state.autopilot || state.underway || state.sails !== 'retracted'))
                return state;
            if (action.on && !(0, underway_1.checklistComplete)('dock-approach', state.checks))
                return state;
            return action.on
                ? {
                    ...state,
                    dock: true,
                    thrust: (0, exports.dockThrust)(state.rudder, state.environment),
                    log: addLog('info', `Dock mode engaged at ${(0, exports.stationName)(action.by)}. Auto-dock compensation on.`),
                }
                : {
                    ...state,
                    dock: false,
                    thrust: { bow: 0, stern: 0 },
                    checks: (0, underway_1.clearChecklist)('dock-approach', state.checks),
                    log: addLog('info', `Dock mode disengaged at ${(0, exports.stationName)(action.by)}. Boosters off.`),
                };
        case 'environment': {
            // Sensor inputs. Any station may update them, since they are readings and not commands.
            const environment = { ...state.environment, ...action.patch };
            return { ...state, environment, thrust: state.dock ? (0, exports.dockThrust)(state.rudder, environment) : state.thrust };
        }
        case 'sails':
            switch (action.mode) {
                case 'deploy':
                    // Sails only go up at the helm, not in dock mode, and not from maintenance.
                    if (!canCommand(state, action.by) || state.sails !== 'retracted' || state.dock)
                        return state;
                    return { ...state, sails: 'deployed', log: addLog('info', `Sails deployed at ${(0, exports.stationName)(action.by)}`) };
                case 'retract':
                    // Stowing the sails is a safe-state action, so either station can do it, even during emergency stop.
                    if (state.sails !== 'deployed')
                        return state;
                    return { ...state, sails: 'retracted', log: addLog('info', `Sails retracted at ${(0, exports.stationName)(action.by)}`) };
                case 'maintenance':
                    if (!canCommand(state, action.by) || state.sails !== 'retracted')
                        return state;
                    return { ...state, sails: 'maintenance', log: addLog('warn', `Sails locked for maintenance at ${(0, exports.stationName)(action.by)}`) };
                case 'endMaintenance':
                    if (!canCommand(state, action.by) || state.sails !== 'maintenance')
                        return state;
                    return { ...state, sails: 'retracted', log: addLog('info', `Sail maintenance lock released at ${(0, exports.stationName)(action.by)}. Sails stowed.`) };
            }
            return state;
        case 'underway':
            if (!canCommand(state, action.by) || action.on === state.underway)
                return state;
            if (action.on) {
                // Underway needs a route with legs left, no dock mode, and the departure checklist complete.
                if (state.dock || state.route.length === 0 || state.activeWaypoint >= state.route.length)
                    return state;
                if (!(0, underway_1.checklistComplete)('underway-departure', state.checks))
                    return state;
                return { ...state, underway: true, log: addLog('info', `Underway engaged at ${(0, exports.stationName)(action.by)}. Leg 1 of ${state.route.length}.`) };
            }
            return {
                ...state,
                underway: false,
                waypointPending: null,
                checks: (0, underway_1.clearChecklist)('underway-departure', state.checks),
                log: addLog('info', `Underway disengaged at ${(0, exports.stationName)(action.by)}.`),
            };
        case 'route':
            // The route can only change while not underway.
            if (!canCommand(state, action.by) || state.underway)
                return state;
            return {
                ...state,
                route: action.waypoints,
                activeWaypoint: 0,
                waypointPending: null,
                log: addLog('info', `Route loaded: ${action.waypoints.length} waypoints.`),
            };
        case 'waypointRequest':
            // The holder asks to confirm arrival at the active waypoint. The other station confirms.
            if (!canCommand(state, action.by) || !state.underway || state.waypointPending !== null)
                return state;
            if (state.activeWaypoint >= state.route.length)
                return state;
            return { ...state, waypointPending: action.by, log: addLog('info', `Waypoint ${state.route[state.activeWaypoint].name} reached. Confirmation requested at ${(0, exports.stationName)(action.by)}.`) };
        case 'waypointConfirm': {
            if (!state.underway || state.waypointPending === null || action.by === state.waypointPending || state.estop)
                return state;
            const reached = state.route[state.activeWaypoint].name;
            const next = state.activeWaypoint + 1;
            const done = next >= state.route.length;
            return {
                ...state,
                activeWaypoint: next,
                waypointPending: null,
                underway: done ? false : state.underway,
                log: addLog('info', done
                    ? `Waypoint ${reached} confirmed at ${(0, exports.stationName)(action.by)}. Route complete. Underway ends.`
                    : `Waypoint ${reached} confirmed at ${(0, exports.stationName)(action.by)}. Leg ${next + 1} of ${state.route.length}.`),
            };
        }
        case 'check':
            // Checklist ticks can be made from either station, but only while that mode is off.
            if (action.list === 'underway-departure' ? state.underway : state.dock)
                return state;
            return { ...state, checks: { ...state.checks, [`${action.list}:${action.index}`]: action.done } };
        case 'request':
            if (action.by === state.authority || state.estop)
                return state;
            return { ...state, pendingRequest: action.by, log: addLog('info', `${(0, exports.stationName)(action.by)} requests control`) };
        case 'cancelRequest':
            return { ...state, pendingRequest: null };
        case 'accept':
            // The holding station hands over. The requester is not asked to confirm.
            if (action.by !== state.authority || state.pendingRequest === null)
                return state;
            return {
                ...state,
                authority: state.pendingRequest,
                pendingRequest: null,
                log: addLog('info', `Control handed over to ${(0, exports.stationName)(state.pendingRequest)}`),
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
                checks: (0, underway_1.clearChecklist)('underway-departure', state.checks),
                log: addLog('alarm', `Emergency stop activated at ${(0, exports.stationName)(action.by)}. Propulsion demand set to zero.`),
            };
        case 'clearEstop':
            if (action.by !== state.authority)
                return state;
            return { ...state, estop: false, log: addLog('warn', `Emergency stop cleared at ${(0, exports.stationName)(action.by)}`) };
        case 'reversionRequest':
            if (action.by !== state.authority || state.reversion || state.estop)
                return state;
            return { ...state, reversionPending: action.by, log: addLog('warn', `Manual reversion requested at ${(0, exports.stationName)(action.by)}`) };
        case 'reversionConfirm':
            // Confirmation must come from the other station.
            if (state.reversionPending === null || action.by === state.reversionPending)
                return state;
            return {
                ...state,
                reversion: true,
                reversionPending: null,
                autopilot: false,
                log: addLog('warn', `Manual steering reversion confirmed at ${(0, exports.stationName)(action.by)}. Autopilot disengaged.`),
            };
        case 'reversionCancel':
            return { ...state, reversionPending: null };
        case 'networkFault':
            return {
                ...state,
                networkFault: action.on,
                log: addLog(action.on ? 'alarm' : 'info', action.on ? 'Primary network control lost. Hardwired path active.' : 'Primary network control restored.'),
            };
        case 'reset':
            return exports.initialPilotState;
    }
}
