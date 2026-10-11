// Commands for the piloting aggregate. Each command is a request to change pilot state.
import type {Environment} from '../aggregates/dock';
import type {Shaft, Side, Station} from '../aggregates/pilot';
import type {ChecklistId, Waypoint} from '../aggregates/underway';

export type SailMode = 'deploy' | 'retract' | 'maintenance' | 'endMaintenance';

export type PilotAction =
  | { type: 'demand'; shaft: Shaft; value: number; by: Station }
  | { type: 'helm'; turns: number; by: Station }
  | { type: 'centre'; by: Station }
  | { type: 'autopilot'; on: boolean; by: Station }
  | { type: 'thrust'; side: Side; value: number; by: Station }
  | { type: 'dock'; on: boolean; by: Station }
  | { type: 'environment'; patch: Partial<Environment> }
  | { type: 'sails'; mode: SailMode; by: Station }
  | { type: 'underway'; on: boolean; by: Station }
  | { type: 'route'; waypoints: Waypoint[]; by: Station }
  | { type: 'waypointRequest'; by: Station }
  | { type: 'waypointConfirm'; by: Station }
  | { type: 'check'; list: ChecklistId; index: number; done: boolean; by: Station }
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
