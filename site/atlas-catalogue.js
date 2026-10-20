// Presentation/search only: source anatomy, IDs and geometry remain in the catalogue.
export const normalizeSearch = value => String(value || '').toLowerCase().replace(/ё/g, 'е');
export const catalogueMatches = (data, term) => !term ||
  [data.ru, data.lat, data.c, data.educationCode, ...(data.searchAliases || [])]
    .some(value => value && normalizeSearch(value).includes(normalizeSearch(term)));

export const typicalThumbSesamoid = data => data.catalogueRole === 'typical_thumb_sesamoid';
export const catalogueVariant = data => data.anatomicalVariant === true;

export function musclePartLatin(muscle, part) {
  // The three existing TA98 part labels are already verified in every region.
  return muscle.lat === 'm. trapezius' && part?.lat
    ? `${muscle.lat}, ${part.lat}` : muscle.lat;
}

export function upperLimbCoverage(side, sub, structures) {
  const relevant = [...structures].filter(s => s.kind !== 'c' && s.meshes.length);
  const left = relevant.filter(s => s.side === 'left');
  const notes = [];
  if (side !== 'right') {
    if (!left.some(s => ['radius_left', 'ulna_left'].includes(s.id)) &&
        !left.some(s => s.data?.sub === 'hand'))
      notes.push('Левая кисть и предплечье пока без 3D-моделей.');
    if (!left.some(s => s.kind === 'm')) notes.push('Мышцы левой руки в этом разделе пока без 3D.');
    if (side === 'both') notes.unshift('Обе стороны: показаны доступные модели; набор сторон неполный.');
  }
  if (['all', 'hand'].includes(sub)) notes.push('Сесамовидные кости большого пальца доступны как карточки без 3D.');
  return notes.join(' ');
}
