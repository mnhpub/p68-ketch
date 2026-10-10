// Projection: derives the scope view model from the scope aggregate and the systems register.
// The view reads only from here, never from the raw JSON.
import scopeData from '../../scope.json';
import systemData from '../../systems.json';
import type {System} from '../aggregates/system';
import type {ScopeData, ScopeItem, ScopeStatus} from '../aggregates/scopeItem';

const scope = scopeData as ScopeData;
const systems = systemData as System[];

export const STATUS_LABEL: Record<ScopeStatus, string> = {
  register: 'In the systems register',
  layout: 'Placed on the layout or in another tab',
  open: 'Open',
};

export type ScopeRow = {item: string; register: string; layout: string; status: ScopeStatus; statusLabel: string};

// Resolve a register id to its display name, or to the app location for non-register items.
function registerName(i: ScopeItem): string {
  if (i.system) return systems.find((s) => s.id === i.system)?.name ?? i.system;
  return i.app ? `See ${i.app}` : '';
}

export function scopeRows(): ScopeRow[] {
  return scope.items.map((i) => ({
    item: i.item,
    register: registerName(i),
    layout: i.layout,
    status: i.status,
    statusLabel: STATUS_LABEL[i.status],
  }));
}

export function scopeCoverage() {
  const covered = scope.items.filter((i) => i.status !== 'open').length;
  return {covered, total: scope.items.length};
}

export function scopeOpenItems(): string[] {
  return scope.open;
}
