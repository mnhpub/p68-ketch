export type Domain = {
  id: string;
  label: string;
  description: string;
};

export type Basis = 'target' | 'model' | 'tbd';

export type Parameter = {
  label: string;
  value: string;
  basis: Basis;
};

export type SystemStatus = 'concept' | 'reviewed' | 'as-built';

export type System = {
  id: string;
  domain: string;
  name: string;
  status: SystemStatus;
  safety_critical: boolean;
  public_release: boolean;
  summary: string;
  approval_status: string;
  key_parameters: Parameter[];
  risks: string[];
  related_decks: string[];
};

export type ChecklistStep = {
  text: string;
  critical: boolean;
};

export type Checklist = {
  id: string;
  system: string;
  title: string;
  status: 'draft' | 'approved';
  steps: ChecklistStep[];
};

export const statusLabel: Record<SystemStatus, string> = {
  concept: 'Concept',
  reviewed: 'Reviewed',
  'as-built': 'As-built',
};

export const basisLabel: Record<Basis, string> = {
  target: 'Design target',
  model: 'Model value',
  tbd: 'To be determined',
};
