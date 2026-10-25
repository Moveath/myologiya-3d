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
    const forearm = ['radius_left', 'ulna_left'].filter(id => left.some(s => s.id === id));
    const hand = left.filter(s => s.kind === 'b' && s.data?.sub === 'hand' && !s.id.startsWith('sesamoid_')).length;
    if (!forearm.length && !hand)
      notes.push('Левая кисть и предплечье пока без 3D-моделей.');
    else {
      if (!hand) notes.push('Левая кисть пока без 3D-моделей.');
      else if (hand < 27) notes.push(`Левая кисть представлена частично: ${hand} из 27 обычных костей; остальные пока без 3D.`);
      if (!forearm.length) notes.push('Левое предплечье пока без 3D-моделей.');
      else if (forearm.length < 2) notes.push(forearm.includes('radius_left')
        ? 'Левая локтевая кость пока без 3D-модели.'
        : 'Левая лучевая кость пока без 3D-модели.');
    }
    if (!left.some(s => s.kind === 'm')) notes.push('Мышцы левой руки в этом разделе пока без 3D.');
    if (side === 'both') notes.unshift('Обе стороны: показаны доступные модели; набор сторон неполный.');
  }
  if (['all', 'hand'].includes(sub)) {
    // Loaded thumb sesamoids are an educational CT reconstruction of another body, not BodyParts3D.
    const sesamoids = relevant.filter(s => s.id.startsWith('sesamoid_mcp1_') && (side === 'both' || s.side === side));
    notes.push(sesamoids.length === (side === 'both' ? 4 : 2)
      ? 'Сесамовидные кости большого пальца — учебная реконструкция по КТ другого тела (Visible Human).'
      : 'Сесамовидные кости большого пальца доступны как карточки без 3D.');
  }
  return notes.join(' ');
}
