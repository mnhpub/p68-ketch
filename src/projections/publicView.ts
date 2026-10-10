import type {Checklist, System} from '../aggregates/system';

// Build audience. The public build (VITE_AUDIENCE=public) includes only systems
// marked public_release: true, and only checklists for those systems. The private
// build includes everything and must sit behind Cloudflare Access.
export const isPublicBuild = import.meta.env.VITE_AUDIENCE === 'public';

export function visibleSystems(systems: System[]): System[] {
  return isPublicBuild ? systems.filter((s) => s.public_release) : systems;
}

export function visibleChecklists(checklists: Checklist[], systems: System[]): Checklist[] {
  const ids = new Set(visibleSystems(systems).map((s) => s.id));
  return checklists.filter((c) => ids.has(c.system));
}
