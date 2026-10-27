// Read-only catalogue audit of bones, muscles and bone landmarks (BONES-MUSCLES-AUDIT).
// Loads the generated data in page order and reports structural contradictions only:
// duplicate/replaced IDs, side contradictions, broken references, missing fields and pin frames.
// It does not judge anatomical truth; every hit needs a source check before a data change.
// Usage: node tools/audit-bones-muscles-catalogue.mjs RUN_DIR
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const FILES = ['data', 'data-leg', 'data-head', 'data-neck', 'data-thorax', 'data-context-bones', 'data-muscle-recovery',
  'data-neck-recovery', 'data-left-limb-muscles', 'data-left-soft-tissues', 'data-abdomen', 'pins', 'pins-leg', 'pins-head', 'pins-head-extra', 'pins-neck',
  'pins-thorax', 'pins-context-bones', 'pins-shared', 'pins-craniometric', 'pins-left-transfer'];
const run = process.argv[2];
const ctx = {window: {}};
ctx.window.window = ctx.window;
vm.createContext(ctx);
const replaced = [], origin = {bones: {}, muscles: {}};
for (const file of FILES) {
  const A = ctx.window.ATLAS;
  const before = {bones: new Map(Object.entries(A?.bones || {})), muscles: new Map(Object.entries(A?.muscles || {}))};
  vm.runInContext(fs.readFileSync(`site/${file}.js`, 'utf8'), ctx, {filename: file});
  for (const kind of ['bones', 'muscles']) for (const [id, card] of Object.entries(ctx.window.ATLAS[kind] || {})) {
    if (!before[kind].has(id)) origin[kind][id] = file;
    else if (before[kind].get(id) !== card) replaced.push({kind, id, first: origin[kind][id], replacedBy: file});
  }
}
const A = ctx.window.ATLAS;
const findings = [];
const add = (severity, type, id, detail) => findings.push({severity, type, id, detail});

const sideFromId = id => /(_left|_l)$/.test(id) || /_left_/.test(id) ? 'left' : /(_right|_r)$/.test(id) || /_right_/.test(id) ? 'right' : null;
const sideFromRu = ru => /слева|левая|левый|левое|левой/i.test(ru) ? 'left' : /справа|правая|правый|правое|правой/i.test(ru) ? 'right' : null;
const sideFromLat = lat => /\bsinist/i.test(lat) ? 'left' : /\bdext/i.test(lat) ? 'right' : null;
// Cards without an explicit side: a paired *_left card implies this one is the right member.
function implicitSide(collection, id, card) {
  if (card.side) return card.side;
  const s = sideFromId(id);
  if (s) return s;
  return collection[id + '_left'] ? 'right' : null;
}

function cardChecks(kind, collection) {
  for (const [id, card] of Object.entries(collection)) {
    const explicit = card.side ?? null, byId = sideFromId(id), byRu = sideFromRu(card.ru || ''), byLat = sideFromLat(card.lat || '');
    for (const [label, value] of [['id', byId], ['ru', byRu], ['lat', byLat]])
      if (explicit && value && value !== explicit) add('P1', `${kind}-side-contradiction`, id, `side=${explicit}, ${label} says ${value}`);
    if (!explicit && byRu && byId && byRu !== byId) add('P1', `${kind}-side-contradiction`, id, `id says ${byId}, ru says ${byRu}`);
    for (const field of ['ru', 'lat']) if (!String(card[field] || '').trim()) add('P1', `${kind}-missing-${field}`, id, '');
    if (/[a-z]{3,}/i.test(card.ru || '') && !/[а-яё]/i.test(card.ru || '')) add('P2', `${kind}-ru-not-russian`, id, card.ru);
    if (/[а-яё]/i.test(card.lat || '')) add('P1', `${kind}-lat-has-cyrillic`, id, card.lat);
    if (card.noModel && card.modelFile) add('P1', `${kind}-noModel-with-modelFile`, id, card.modelFile);
    if (card.modelFile && !fs.existsSync(path.join('site', card.modelFile))) add('P0', `${kind}-modelFile-missing`, id, card.modelFile);
    if (card.modelLicense && !fs.existsSync(path.join('site', card.modelLicense))) add('P1', `${kind}-license-file-missing`, id, card.modelLicense);
    for (const rel of card.relatedMuscles || []) if (!A.muscles[rel]) add('P1', `${kind}-related-missing`, id, rel);
    if (kind === 'muscle') {
      for (const field of ['o', 'i', 'a', 'n']) if (!String(card[field] || '').trim()) add('P1', `muscle-missing-${field}`, id, '');
      if (!A.groups.some(g => g.id === card.g)) add('P1', 'muscle-group-missing', id, String(card.g));
      for (const [part, p] of Object.entries(card.parts || {})) {
        if (!String(p.ru || '').trim() || !String(p.lat || '').trim()) add('P2', 'muscle-part-name-missing', `${id}:${part}`, '');
        if (/[а-яё]/i.test(p.lat || '')) add('P1', 'muscle-part-lat-has-cyrillic', `${id}:${part}`, p.lat);
      }
      // Paired left/right cards must carry mirrored side words in the Russian label.
      const right = id.endsWith('_left') ? id.slice(0, -5) : null;
      if (right && A.muscles[right] && A.muscles[right].lat !== card.lat) add('P2', 'muscle-pair-lat-differs', id, `${A.muscles[right].lat} | ${card.lat}`);
    }
    if (kind === 'bone' && !A.boneGroups.some(g => g.id === card.g)) add('P1', 'bone-group-missing', id, String(card.g));
  }
}
cardChecks('bone', A.bones);
cardChecks('muscle', A.muscles);

// Landmarks.
const pinIds = new Map();
const MIDLINE = 0.004; // metres; BodyParts3D is not exactly symmetric about X=0.
const pinRows = [];
for (const pin of A.pins) {
  if (pinIds.has(pin.id)) add('P1', 'pin-duplicate-id', pin.id, `${pinIds.get(pin.id)} / ${pin.b}`);
  pinIds.set(pin.id, pin.b);
  const bone = A.bones[pin.b];
  if (!bone) { add('P0', 'pin-owner-missing', pin.id, pin.b); continue; }
  const boneSide = implicitSide(A.bones, pin.b, bone);
  if (pin.side && boneSide && pin.side !== boneSide) add('P0', 'pin-side-vs-owner', pin.id, `pin ${pin.side}, owner ${pin.b} ${boneSide}`);
  const ruSide = sideFromRu(pin.ru || '');
  if (ruSide && boneSide && ruSide !== boneSide) add('P1', 'pin-ru-side-vs-owner', pin.id, `${pin.ru} on ${pin.b}`);
  if (pin.p) {
    if (pin.p.length !== 3 || !pin.p.every(Number.isFinite)) add('P0', 'pin-bad-coordinates', pin.id, JSON.stringify(pin.p));
    else {
      const side = pin.side || boneSide;
      if (side === 'right' && pin.p[0] > MIDLINE) add('P0', 'pin-x-on-wrong-side', pin.id, `right pin at x=${pin.p[0]}`);
      if (side === 'left' && pin.p[0] < -MIDLINE) add('P0', 'pin-x-on-wrong-side', pin.id, `left pin at x=${pin.p[0]}`);
    }
    if (!pin.n) add('P2', 'pin-without-normal', pin.id, '');
    else if (Math.abs(Math.hypot(...pin.n) - 1) > 0.02) add('P2', 'pin-normal-not-unit', pin.id, JSON.stringify(pin.n));
  }
  for (const [muscle, role, part] of pin.m || []) {
    const card = A.muscles[muscle];
    if (!card) { add('P0', 'pin-muscle-missing', pin.id, muscle); continue; }
    if (!['o', 'i'].includes(role)) add('P1', 'pin-muscle-role-invalid', pin.id, `${muscle}:${role}`);
    if (part && !card.parts?.[part]) add('P1', 'pin-muscle-part-missing', pin.id, `${muscle}:${part}`);
    const muscleSide = implicitSide(A.muscles, muscle, card);
    if (muscleSide && boneSide && muscleSide !== boneSide) add('P0', 'pin-muscle-side-vs-owner', pin.id, `${muscle} (${muscleSide}) on ${pin.b} (${boneSide})`);
  }
  pinRows.push({id: pin.id, b: pin.b, side: pin.side || boneSide || null, c: pin.c || null, t: pin.t, hasP: !!pin.p,
    p: pin.p || null, n: pin.n || null, m: pin.m || [], geometryKind: pin.geometryKind || null, anchorStatus: pin.anchorStatus || null, loc: pin.loc || null});
}

// Coverage per side for paired limbs: left landmarks with a right counterpart that has coordinates.
const key = pin => `${pin.c || ''}|${pin.lat}|${(pin.m || []).map(x => x.join(':')).join(',')}`;
const counterpartBone = b => b.endsWith('_left') ? b.slice(0, -5) : null;
const rightByBone = new Map();
for (const pin of A.pins) if (pin.p) {
  const k = pin.b + '|' + (pin.c || pin.lat);
  if (!rightByBone.has(k)) rightByBone.set(k, []);
  rightByBone.get(k).push(pin);
}
const leftCoverage = {leftPins: 0, withP: 0, withoutP: 0, withoutPButRightHasP: 0};
for (const pin of A.pins) {
  const bone = A.bones[pin.b];
  if (!bone || implicitSide(A.bones, pin.b, bone) !== 'left') continue;
  leftCoverage.leftPins++;
  if (pin.p) { leftCoverage.withP++; continue; }
  leftCoverage.withoutP++;
  const rb = counterpartBone(pin.b);
  if (rb && rightByBone.has(rb + '|' + (pin.c || pin.lat))) leftCoverage.withoutPButRightHasP++;
}

const muscles = Object.entries(A.muscles);
const pinned = new Set(A.pins.flatMap(p => (p.m || []).map(x => x[0])));
const counts = {
  bones: Object.keys(A.bones).length,
  bonesNoModel: Object.values(A.bones).filter(c => c.noModel).length,
  bonesBySide: Object.fromEntries(['left', 'right', null].map(s => [String(s), Object.entries(A.bones).filter(([id, c]) => implicitSide(A.bones, id, c) === s).length])),
  muscles: muscles.length,
  musclesNoModel: muscles.filter(([, c]) => c.noModel).length,
  musclesBySide: Object.fromEntries(['left', 'right', null].map(s => [String(s), muscles.filter(([id, c]) => implicitSide(A.muscles, id, c) === s).length])),
  muscleParts: muscles.reduce((n, [, c]) => n + Object.keys(c.parts || {}).length, 0),
  musclePartsNoModel: muscles.reduce((n, [, c]) => n + Object.values(c.parts || {}).filter(p => p.noModel).length, 0),
  musclesWithoutFieldRefs: muscles.filter(([, c]) => !c.fieldRefs).length,
  musclesWithoutAnyRefs: muscles.filter(([, c]) => !c.refs && !c.fieldRefs).length,
  musclesWithoutPins: muscles.filter(([id]) => !pinned.has(id)).length,
  leftMusclesWithoutPins: muscles.filter(([id, c]) => implicitSide(A.muscles, id, c) === 'left' && !pinned.has(id)).length,
  pins: A.pins.length, pinsWithP: A.pins.filter(p => p.p).length, pinsWithoutP: A.pins.filter(p => !p.p).length,
  pinsWithMuscle: A.pins.filter(p => p.m?.length).length,
  leftCoverage,
  replacedDefinitions: replaced.length,
};
const byType = {};
for (const f of findings) byType[f.type] = (byType[f.type] || 0) + 1;
const report = {created: new Date().toISOString(), method: 'vm load of generated data in page order; structural checks only',
  files: FILES, counts, byType, replaced, findings};
fs.writeFileSync(path.join(run, 'catalogue-audit.json'), JSON.stringify(report, null, 1) + '\n', {flag: 'wx'});
fs.writeFileSync(path.join(run, 'catalogue-pins.json'), JSON.stringify(pinRows) + '\n', {flag: 'wx'});
const cardRows = [...Object.entries(A.bones).map(([id, c]) => ['bone', id, c]), ...Object.entries(A.muscles).map(([id, c]) => ['muscle', id, c])]
  .map(([kind, id, c]) => ({kind, id, ru: c.ru, lat: c.lat, side: implicitSide(kind === 'bone' ? A.bones : A.muscles, id, c), g: c.g,
    noModel: !!c.noModel, modelFile: c.modelFile || null, modelStatus: c.modelStatus || null,
    parts: Object.fromEntries(Object.entries(c.parts || {}).map(([k, p]) => [k, {ru: p.ru, lat: p.lat, noModel: !!p.noModel}])),
    hasFieldRefs: !!c.fieldRefs, pinned: kind === 'muscle' ? pinned.has(id) : null}));
fs.writeFileSync(path.join(run, 'catalogue-cards.json'), JSON.stringify(cardRows) + '\n', {flag: 'wx'});
console.log(JSON.stringify({counts, byType}, null, 1));
