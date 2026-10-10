// Aggregate: one item from the original brief, and where it is covered in the app.
// Status is the aggregate's only state. Scope is read-only, so there are no commands for it.
export type ScopeStatus = 'register' | 'layout' | 'open';

export type ScopeItem = {
  item: string;
  system: string | null;
  layout: string;
  status: ScopeStatus;
  app?: string;
};

export type ScopeData = {items: ScopeItem[]; open: string[]};
