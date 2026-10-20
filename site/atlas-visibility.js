import { MODEL_SIDES } from './atlas-model-sides.js';

export function structureSide(section, id, data) {
  if (['left','right'].includes(data?.side)) return data.side;
  return MODEL_SIDES[section]?.[id] || (/_(left|right)$/.exec(id || '')?.[1]) || 'unseparated';
}

export const sideAllows = (side, view) => view === 'both' || !['left','right'].includes(side) || side === view;

// Use recorded attachment owners, not proximity, bone names in prose or mirrored anatomy.
export function muscleBoneIds(entries, part, isBone) {
  // Whole-muscle evidence does not establish an attachment of an individual part.
  return [...new Set(entries.filter(e => !part || e.part === part)
    .map(e => e.pin.b).filter(isBone))];
}

// null delegates to existing layer/subsection rules; 0/2 are explicit decisions.
export function selectionVisibility(s, policy) {
  if (!sideAllows(s.side, policy.side) || policy.hidden.has(s.id)) return 0;
  if (policy.isolate) {
    return s.id === policy.isolate || policy.boundary.includes(s.id) ||
      (policy.muscle && policy.related.includes(s.id)) ? 2 : 0;
  }
  if (policy.boundary.includes(s.id)) return 2;
  if (policy.muscle && ['b','c'].includes(s.kind)) return policy.related.includes(s.id) ? 2 : 0;
  return null;
}
