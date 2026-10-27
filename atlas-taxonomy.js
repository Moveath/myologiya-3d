// Textbook catalogue: system -> region -> group -> (named part) -> structure.
// Groups pick existing records by their data group (g) and, where one data group
// mixes textbook groups, by side-free base ID. Records, IDs, sections and models
// are unchanged; this only decides where a structure is listed.
// `missing` names structures that have no model yet, so the gap stays visible.
export const CATALOGUE = [
  {system: 'bones', id: 'skull-bones', ru: 'Кости черепа', groups: [
    {id: 'neurocranium', ru: 'Мозговой череп', g: ['head_neurocranium']},
    // TA98 A02.1.16.001 lists the hyoid with the cranium; UDC 611.716.5 files it under the facial skull.
    {id: 'viscerocranium', ru: 'Лицевой череп', g: ['head_viscerocranium', 'neck_hyoid'],
      note: 'Подъязычная кость относится к лицевому черепу, её модель открывается в разделе «Шея».'},
  ]},
  {system: 'bones', id: 'trunk-bones', ru: 'Кости туловища', groups: [
    {id: 'spine', ru: 'Позвоночный столб', parts: [
      {id: 'cervical-vertebrae', ru: 'Шейные позвонки', g: ['neck_vertebrae']},
      {id: 'thoracic-vertebrae', ru: 'Грудные позвонки', g: ['thorax_spine']},
      {id: 'lumbar-vertebrae', ru: 'Поясничные позвонки', g: ['b_lumbar']},
      {id: 'sacrum', ru: 'Крестец', g: ['b_pelvis'], bases: ['sacrum']},
    ], note: 'Отделы открываются в разных разделах: «Шея», «Грудь и живот», «Поясница, таз и нижняя конечность». Копчик отдельной модели не имеет — он отмечен ориентиром на модели крестца.'},
    {id: 'thoracic-cage', ru: 'Грудная клетка', parts: [
      {id: 'ribs', ru: 'Рёбра', g: ['thorax_ribs']},
      {id: 'costal-cartilages', ru: 'Рёберные хрящи', g: ['b_soft_thorax']},
      {id: 'sternum', ru: 'Грудина', g: ['thorax_sternum']},
    ]},
  ]},
  {system: 'bones', id: 'upper-limb-bones', ru: 'Кости верхней конечности', groups: [
    {id: 'upper-girdle-bones', ru: 'Пояс верхней конечности', g: ['b_girdle']},
    {id: 'humerus', ru: 'Плечевая кость', g: ['b_free'], bases: ['humerus']},
    {id: 'forearm-bones', ru: 'Кости предплечья', g: ['b_free'], bases: ['radius', 'ulna']},
    {id: 'hand-bones', ru: 'Кости кисти', parts: [
      {id: 'carpus', ru: 'Кости запястья', g: ['b_carpus']},
      {id: 'metacarpus', ru: 'Пястные кости', g: ['b_meta']},
      {id: 'hand-phalanges', ru: 'Фаланги пальцев', g: ['b_phal']},
      {id: 'hand-sesamoids', ru: 'Сесамовидные кости', g: ['b_hand_sesamoids']},
    ]},
  ]},
  {system: 'bones', id: 'lower-limb-bones', ru: 'Кости нижней конечности', groups: [
    {id: 'lower-girdle-bones', ru: 'Пояс нижней конечности', g: ['b_pelvis'], bases: ['hip_bone'],
      note: 'Таз в целом образуют две тазовые кости, крестец и копчик.'},
    {id: 'femur-patella', ru: 'Бедренная кость и надколенник', g: ['b_limb'], bases: ['femur', 'patella']},
    {id: 'leg-bones', ru: 'Кости голени', g: ['b_limb'], bases: ['tibia', 'fibula']},
    {id: 'foot-bones', ru: 'Кости стопы', parts: [
      {id: 'tarsus', ru: 'Кости предплюсны', g: ['b_tarsus']},
      {id: 'metatarsus', ru: 'Плюсневые кости', g: ['b_metatarsus']},
      {id: 'foot-phalanges', ru: 'Фаланги пальцев', g: ['b_toes'], except: ['sesamoid_pedis']},
      {id: 'foot-sesamoids', ru: 'Сесамовидные кости', g: ['b_toes'], bases: ['sesamoid_pedis']},
    ]},
  ]},
  {system: 'soft', id: 'connective', ru: 'Связки, сухожилия и апоневрозы', groups: [
    {id: 'connective-tissue', ru: 'Связки, сухожилия, апоневрозы и перепонки', g: ['b_soft_head', 'b_soft', 'b_soft_leg']},
  ]},
  {system: 'muscles', id: 'head-muscles', ru: 'Мышцы головы', groups: [
    {id: 'mimetic', ru: 'Мимические мышцы', parts: [
      {id: 'scalp', ru: 'Мышцы свода черепа', g: ['head_scalp']},
      {id: 'face', ru: 'Мышцы лица', g: ['head_face']},
      {id: 'auricle', ru: 'Мышцы ушной раковины', g: ['head_ear']},
    ]},
    {id: 'mastication', ru: 'Жевательные мышцы', g: ['head_mastication']},
  ]},
  {system: 'muscles', id: 'neck-muscles', ru: 'Мышцы шеи', groups: [
    {id: 'neck-superficial', ru: 'Поверхностные мышцы шеи', g: ['neck_superficial']},
    {id: 'suprahyoid', ru: 'Надподъязычные мышцы', g: ['neck_suprahyoid']},
    {id: 'infrahyoid', ru: 'Подподъязычные мышцы', g: ['neck_infrahyoid']},
    {id: 'neck-deep', ru: 'Глубокие мышцы шеи', parts: [
      {id: 'scalene', ru: 'Латеральная группа: лестничные мышцы', g: ['neck_scalene']},
      {id: 'prevertebral', ru: 'Медиальная группа: предпозвоночные мышцы', g: ['neck_prevertebral']},
    ]},
  ]},
  {system: 'muscles', id: 'back-muscles', ru: 'Мышцы спины', groups: [
    {id: 'back-superficial', ru: 'Поверхностные мышцы спины', g: ['thorax_back', 'neck_girdle'],
      bases: ['thorax_trapezius', 'thorax_latissimus_dorsi', 'neck_levator_scapulae', 'thorax_rhomboid_major',
        'thorax_rhomboid_minor', 'thorax_serratus_posterior_superior', 'thorax_serratus_posterior_inferior']},
    {id: 'back-deep', ru: 'Глубокие мышцы спины', parts: [
      {id: 'splenius', ru: 'Ременные мышцы', g: ['neck_posterior'], bases: ['splenius_capitis', 'splenius_cervicis']},
      {id: 'erector-spinae', ru: 'Мышца, выпрямляющая позвоночник', g: ['neck_posterior', 'thorax_deep_back'],
        bases: ['iliocostalis_cervicis', 'thorax_iliocostalis_thoracis', 'longissimus_capitis', 'longissimus_cervicis',
          'thorax_longissimus_thoracis', 'spinalis_cervicis', 'thorax_spinalis_thoracis']},
      {id: 'transversospinales', ru: 'Поперечно-остистые мышцы', g: ['neck_posterior', 'thorax_deep_back'],
        bases: ['semispinalis_capitis', 'semispinalis_cervicis', 'thorax_semispinalis_thoracis', 'thorax_multifidus', 'thorax_rotatores_thoracis']},
      {id: 'interspinales-intertransversarii', ru: 'Межостистые и межпоперечные мышцы', g: ['neck_posterior', 'thorax_deep_back'],
        bases: ['interspinales_cervicis', 'thorax_interspinales_thoracis', 'thorax_intertransversarii_thoracis'],
        missing: 'Пока нет моделей: поясничные межостистые мышцы, шейные и поясничные межпоперечные мышцы.'},
    ]},
    {id: 'suboccipital', ru: 'Подзатылочные мышцы', g: ['neck_suboccipital']},
  ]},
  {system: 'muscles', id: 'chest-muscles', ru: 'Мышцы груди', groups: [
    {id: 'chest-limb', ru: 'Мышцы груди, связанные с верхней конечностью', g: ['thorax_pectoral']},
    {id: 'chest-own', ru: 'Собственные мышцы груди', g: ['thorax_wall']},
    {id: 'diaphragm', ru: 'Диафрагма', g: ['thorax_diaphragm']},
  ]},
  {system: 'muscles', id: 'abdomen-muscles', ru: 'Мышцы живота', groups: [
    // Gray (1918) and Loyola: anterolateral and posterior muscles of the abdomen; TA98 A04.5.01.
    {id: 'abdomen-anterolateral', ru: 'Мышцы переднебоковой стенки живота', g: ['abdomen_anterolateral'],
      bases: ['abdomen_obliquus_externus_abdominis', 'abdomen_obliquus_internus_abdominis', 'abdomen_transversus_abdominis',
        'abdomen_rectus_abdominis', 'abdomen_pyramidalis'],
      missing: 'Пока нет модели: мышца, поднимающая яичко, — она описана в карточке внутренней косой мышцы.'},
    {id: 'abdomen-posterior', ru: 'Мышцы задней стенки живота', g: ['abdomen_posterior'],
      note: 'Gray и Loyola относят к задней стенке живота также большую и малую поясничные и подвздошную мышцы; в атласе подвздошно-поясничная мышца стоит в мышцах таза.'},
  ]},
  {system: 'muscles', id: 'perineum-muscles', ru: 'Мышцы промежности', groups: [
    {id: 'pelvic-diaphragm', ru: 'Диафрагма таза', g: ['pelvic_floor']},
    {id: 'perineum-other', ru: 'Другие мышцы промежности',
      missing: 'Пока нет моделей: поверхностная и глубокая поперечные мышцы промежности, луковично-губчатая и седалищно-пещеристая мышцы, наружный сфинктер мочеиспускательного канала, наружный сфинктер заднего прохода.'},
  ]},
  {system: 'muscles', id: 'upper-limb-muscles', ru: 'Мышцы верхней конечности', groups: [
    {id: 'upper-girdle-muscles', ru: 'Мышцы пояса верхней конечности', g: ['girdle']},
    {id: 'arm-muscles', ru: 'Мышцы плеча', parts: [
      {id: 'arm-anterior', ru: 'Передняя группа', g: ['arm_ant']},
      {id: 'arm-posterior', ru: 'Задняя группа', g: ['arm_post']},
    ]},
    {id: 'forearm-muscles', ru: 'Мышцы предплечья', parts: [
      {id: 'forearm-anterior', ru: 'Передняя группа', g: ['fa_ant']},
      {id: 'forearm-posterior', ru: 'Задняя группа', g: ['fa_post']},
    ]},
    {id: 'hand-muscles', ru: 'Мышцы кисти', parts: [
      {id: 'thenar', ru: 'Возвышение большого пальца', g: ['hand_thenar']},
      {id: 'hypothenar', ru: 'Возвышение мизинца', g: ['hand_hypo']},
      {id: 'hand-middle', ru: 'Средняя группа', g: ['hand_mid']},
    ]},
  ]},
  {system: 'muscles', id: 'lower-limb-muscles', ru: 'Мышцы нижней конечности', groups: [
    {id: 'pelvis-muscles', ru: 'Мышцы таза', parts: [
      {id: 'pelvis-internal', ru: 'Внутренняя группа', g: ['pelvis_int']},
      {id: 'pelvis-external', ru: 'Наружная группа (ягодичная область)', g: ['pelvis_ext']},
    ]},
    {id: 'thigh-muscles', ru: 'Мышцы бедра', parts: [
      {id: 'thigh-anterior', ru: 'Передняя группа', g: ['thigh_ant']},
      {id: 'thigh-medial', ru: 'Медиальная группа', g: ['thigh_med']},
      {id: 'thigh-posterior', ru: 'Задняя группа', g: ['thigh_post']},
    ]},
    {id: 'shank-muscles', ru: 'Мышцы голени', parts: [
      {id: 'shank-anterior', ru: 'Передняя группа', g: ['shank_ant']},
      {id: 'shank-lateral', ru: 'Латеральная группа', g: ['shank_lat']},
      {id: 'shank-posterior', ru: 'Задняя группа', g: ['shank_post']},
    ]},
    {id: 'foot-muscles', ru: 'Мышцы стопы', parts: [
      {id: 'foot-dorsal', ru: 'Тыльная поверхность', g: ['foot_dorsal']},
      {id: 'foot-medial', ru: 'Подошва: медиальная группа', g: ['foot_med']},
      {id: 'foot-lateral', ru: 'Подошва: латеральная группа', g: ['foot_lat']},
      {id: 'foot-middle', ru: 'Подошва: средняя группа', g: ['foot_mid']},
    ]},
  ]},
];

// The same muscle is modelled in several sections. The catalogue lists the canonical
// (bilateral) record once and offers the others as "also in section" links.
export const ALTERNATES = {
  thorax_trapezius: ['neck_trapezius', 'trapezius'],
  thorax_latissimus_dorsi: ['latissimus_dorsi'],
  thorax_rhomboid_major: ['rhomboid_major'],
  thorax_rhomboid_minor: ['rhomboid_minor'],
  thorax_pectoralis_major: ['pectoralis_major'],
  thorax_pectoralis_minor: ['pectoralis_minor'],
  thorax_subclavius: ['subclavius'],
  thorax_serratus_anterior: ['serratus_anterior'],
  neck_levator_scapulae: ['levator_scapulae'],
};

export const pairBase = id => id.replace(/_(?:left|right)$/, '');

// "Жевательная мышца · правая", "1-е ребро, правое", "Левая ключица", "I пястная кость слева" -> side-free name
const SIDE_WORD = '(?:прав|лев)(?:ая|ый|ое|ые)|справа|слева';
export function pairName(ru) {
  const name = String(ru || '').trim()
    .replace(new RegExp(`\\s*[·,]\\s*(?:${SIDE_WORD})$`, 'i'), '')
    .replace(new RegExp(`\\s+(?:справа|слева)$`, 'i'), '')
    .replace(/^(?:Прав|Лев)(?:ая|ый|ое|ые)\s+/, '');
  return name.charAt(0).toUpperCase() + name.slice(1);
}

// Resolve the textbook tree against the atlas data.
// sideOf(id, section) -> 'left' | 'right' | other; returns regions with pairs per part.
export function buildCatalogue(A, sideOf) {
  const sectionOf = {};
  for (const g of A.groups || []) sectionOf['m:' + g.id] = g.sec;
  for (const g of A.boneGroups || []) sectionOf['b:' + g.id] = g.sec;
  const alternateOf = {};
  for (const [canonical, others] of Object.entries(ALTERNATES)) for (const base of others) alternateOf[base] = canonical;
  const records = (kind, source) => Object.entries(source || {}).map(([id, d]) => ({id, d, kind, sec: sectionOf[kind + ':' + d.g], base: pairBase(id)}));
  const all = [...records('m', A.muscles), ...records('b', A.bones)];
  const byBase = {};
  for (const r of all) (byBase[r.sec + ':' + r.base] ||= []).push(r);
  const membersOf = rows => {
    const members = {};
    for (const r of rows) {
      const side = sideOf(r.id, r.sec);
      members[side === 'left' || side === 'right' ? side : 'single'] ||= r.id;
    }
    return members;
  };
  const alternatesFor = base => Object.entries(byBase).filter(([key, rows]) => alternateOf[rows[0].base] === base)
    .map(([key, rows]) => ({sec: rows[0].sec, members: membersOf(rows)}));
  const placed = new Set();
  const pairsFor = (spec, kind) => {
    const rows = all.filter(r => r.kind === kind && spec.g?.includes(r.d.g) && !alternateOf[r.base]
      && (!spec.bases || spec.bases.includes(r.base)) && !(spec.except || []).includes(r.base));
    const order = spec.bases ? (a, b) => spec.bases.indexOf(a) - spec.bases.indexOf(b) : () => 0;
    const bases = [...new Set(rows.map(r => r.sec + ':' + r.base))].sort((a, b) => order(a.split(':')[1], b.split(':')[1]));
    return bases.map(key => {
      const group = byBase[key].filter(r => r.kind === kind), first = group[0];
      group.forEach(r => placed.add(r.id));
      const members = membersOf(group), main = members.right || members.single || members.left;
      const data = (kind === 'm' ? A.muscles : A.bones)[main];
      return {key, base: first.base, sec: first.sec, kind, name: pairName(data.ru), lat: data.lat, members, alternates: alternatesFor(first.base)};
    });
  };
  const tree = CATALOGUE.map(region => ({...region, groups: region.groups.map(group => {
    const kind = region.system === 'muscles' ? 'm' : 'b';
    const parts = (group.parts || (group.g ? [{id: group.id, g: group.g, bases: group.bases, except: group.except}] : []))
      .map(part => ({...part, pairs: pairsFor(part, kind)}));
    return {...group, parts};
  })}));
  const unplaced = all.filter(r => !placed.has(r.id) && !alternateOf[r.base]).map(r => r.id);
  return {tree, unplaced};
}

// Leaf (part or group) of every placed structure, used for colouring bones by group.
export function catalogueLeaves(tree) {
  const leaves = [];
  for (const region of tree) for (const group of region.groups) for (const part of group.parts) {
    const ids = part.pairs.flatMap(p => Object.values(p.members));
    if (ids.length) leaves.push({id: part.id, ru: part.ru || group.ru, region: region.id, system: region.system, ids});
  }
  return leaves;
}
