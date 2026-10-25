// One landmark instance can appear under several bones without cloning the pin.
// Legacy sh means shared catalogue/context, not necessarily a bony contribution.
export function relatedBoneIds(pin) {
  const explicit = pin.relations?.map(relation => relation.bone).filter(Boolean);
  return [...new Set(explicit?.length ? explicit : pin.sh?.length ? pin.sh : [pin.b])].filter(Boolean);
}

export const isSharedLandmark = pin => relatedBoneIds(pin).length > 1;
export const landmarkBelongsTo = (pin, bone) => relatedBoneIds(pin).includes(bone);
// Catalogue membership and anatomical participation are independent.
export const isOwnBoneTerm = (pin, bone) => pin.t === 'ta' &&
  (pin.catalogueBones ? pin.catalogueBones.includes(bone) : pin.b === bone && !pin.sh && !pin.relations?.length);
export const contributingBoneIds = pin => [...new Set((pin.relations || [])
  .filter(r => ['boundaryContribution', 'component'].includes(r.role)).map(r => r.bone))];
export const hasLandmarkPosition = pin => !!pin?.p && pin.anchorStatus !== 'unverified';
// Shown, but only as an educational approximation transferred from the reviewed right record.
export const isApproximateLandmark = pin => hasLandmarkPosition(pin) && pin.anchorStatus === 'contralateral_transfer';
export const relationLabel = role => ({boundaryContribution:'образует границу',component:'участвует в образовании',
  adjacentContext:'контекст',variantOf:'связь с вариантом'}[role] || 'связь каталога');

export function indexLandmarks(pins) {
  const byId = Object.create(null), byBone = Object.create(null), byMuscle = Object.create(null);
  for (const pin of pins) {
    if (byId[pin.id]) throw new Error(`Duplicate landmark id: ${pin.id}`);
    byId[pin.id] = pin;
    for (const bone of relatedBoneIds(pin)) (byBone[bone] ||= []).push(pin);
    for (const [muscle, role, part] of pin.m || []) (byMuscle[muscle] ||= []).push({pin, role, part: part || null});
  }
  return {byId, byBone, byMuscle};
}

// One search result per instance, even if it is listed under multiple bone cards.
export function landmarkSearchOwner(pin, selectedBone) {
  const bones = relatedBoneIds(pin);
  return bones.includes(selectedBone) ? selectedBone : bones.includes(pin.b) ? pin.b : bones[0];
}
