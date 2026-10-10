// Commands for the piloting aggregate. Each command is a request to change pilot state.
import type {Shaft, Side, Station} from '../aggregates/pilot';

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
