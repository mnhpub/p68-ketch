// Concept state for the two-station piloting screen. Nothing here is sent to
// equipment. The reducer encodes the two-person rules: one station holds
// control at a time, handover is requested and accepted, and manual reversion
// is requested at one station and confirmed at the other.

export type Station = 'bridge' | 'pilothouse';

export const STATION_NAME: Record<Station, string> = {
  bridge: 'Bridge',
  pilothouse: 'Outdoor pilot house',
};
export const stationName = (s: Station) => STATION_NAME[s];
export type Shaft = 'port' | 'stbd';
export type Side = 'bow' | 'stern';
export type Level = 'info' | 'warn' | 'alarm';

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
  estop: boolean;
  networkFault: boolean;
  reversionPending: Station | null;
  reversion: boolean;
  log: LogEntry[];
};

export type PilotAction =
  | { type: 'demand'; shaft: Shaft; value: number; by: Station }
  | { type: 'rudder'; value: number; by: Station }
  | { type: 'autopilot'; on: boolean; by: Station }
  | { type: 'thrust'; side: Side; value: number; by: Station }
  | { type: 'request'; by: Station }
  | { type: 'cancelRequest' }
  | { type: 'accept'; by: Station }
  | { type: 'estop'; by: Station }
  | { type: 'clearEstop'; by: Station }
  | { type: 'reversionRequest'; by: Station }
  | { type: 'reversionConfirm'; by: Station }
  | { type: 'reversionCancel' }
  | { type: 'networkFault'; on: boolean }
  | { type: 'reset' };

export const otherStation = (s: Station): Station => (s === 'bridge' ? 'pilothouse' : 'bridge');

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export const RUDDER_LIMIT = 35;

export const initialPilotState: PilotState = {
  authority: 'bridge',
  pendingRequest: null,
  demand: { port: 0, stbd: 0 },
  rudder: 0,
  autopilot: false,
  thrust: { bow: 0, stern: 0 },
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

    case 'rudder':
      // Manual rudder is locked while autopilot is engaged.
      if (!canCommand(state, action.by) || state.autopilot) return state;
      return { ...state, rudder: clamp(action.value, -RUDDER_LIMIT, RUDDER_LIMIT) };

    case 'autopilot':
      if (!canCommand(state, action.by) || (action.on && state.reversion)) return state;
      return {
        ...state,
        autopilot: action.on,
        log: addLog('info', action.on ? `Autopilot engaged at ${stationName(action.by)}` : `Autopilot disengaged at ${stationName(action.by)}`),
      };

    case 'thrust':
      if (!canCommand(state, action.by)) return state;
      return { ...state, thrust: { ...state.thrust, [action.side]: clamp(action.value, -100, 100) } };

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
