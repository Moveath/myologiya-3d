// Classify every landmark record without a shown position (PIN-001 / LOG-20261026-02) by what it needs.
// Read-only over the published data; writes one JSON into a new evidence run.
// Classes (first matching rule wins, in this order):
//   blocked      — the data needed to place it do not exist in the project (variant presence, age/ossification
//                  images, cartilage/disc/ligament boundaries, coccyx boundary, missing participant models,
//                  structures below the resolution of the surface mesh);
//   approximate  — a left record whose paired right record has a reviewed position: an approximate point may be
//                  transferred to the left mesh (never as independent left annotation);
//   not_needed   — joints and other relations between bones: the interface shows them by their participating
//                  bones and relation chips, so no own coordinate is required now;
//   exact_pin    — point-like features (craniometric points, tubercles, processes, spines, apices, small pits,
//                  openings, notches): one accepted marker is the right representation;
//   region       — surfaces, lines, canals, spaces and bone parts: must be shown as a mask, line or volume,
//                  a single marker would misstate their extent.
// Usage: node tools/classify-unplaced-landmarks.mjs
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {hasLandmarkPosition} from '../site/atlas-landmarks.js';
import {createEvidenceRun} from './evidence-run.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = await fs.readFile(path.join(root, 'site/index.html'), 'utf8');
const box = {window: {}}; box.window.window = box.window; vm.createContext(box);
for (const src of [...html.matchAll(/<script src="((?:data|pins)[\w-]*\.js)"/g)].map(m => m[1]))
  vm.runInContext(await fs.readFile(path.join(root, 'site', src), 'utf8'), box);
const A = box.window.ATLAS;

export const CLASSES = {
  blocked: 'заблокированы отсутствием данных',
  approximate: 'допускают ориентировочную локализацию',
  not_needed: 'не требуют координат в текущем интерфейсе',
  exact_pin: 'требуют точного пина',
  region: 'должны отображаться областью или линией',
};
// What the record itself says is still needed; the general model note is not used (it mentions possible variants
// of constant structures, which does not make them variants).
const need = p => [p.geometryRequirements?.neededEvidence, p.geometryRequirements?.available].filter(Boolean).join(' ');
const head = p => (p.lat || '').toLowerCase().replace(/^[(\s]+/, '').split(/[\s;]+/)[0];
const POINT_HEADS = new Set(['nasion', 'bregma', 'lambda', 'pterion', 'asterion', 'tuberculum', 'tuber', 'processus', 'spina', 'apex',
  'eminentia', 'hamulus', 'uncus', 'trochanter', 'epicondylus', 'protuberantia', 'cornu', 'fovea', 'foveola', 'foramen',
  'incisura', 'porus', 'ostium', 'apertura', 'aditus']);
const POINT_RU = /^(Бугорок|Бугор|Отросток|Ость|Верхушка|Возвышение|Крючок|Ямка|Ямочка|Отверстие|Вырезка|Предугловая вырезка)/;
const JOINT_HEADS = new Set(['articulatio', 'articulationes', 'syndesmosis', 'symphysis', 'junctura', 'sutura', 'synchondrosis']);
const rightOf = bone => bone.endsWith('_left') ? bone.slice(0, -5) : null;
const byId = Object.fromEntries(A.pins.map(p => [p.id, p]));

function pairedRight(p) {
  const rb = rightOf(p.b);
  if (!rb) return null;
  if (p.templateRecord) return byId[p.templateRecord]?.b === rb ? byId[p.templateRecord] : null;
  const found = A.pins.filter(r => r.b === rb && ((p.c && r.c === p.c) || (!p.c && p.lat && r.lat === p.lat && r.t === p.t)));
  if (found.length === 1) return found[0];
  const same = byId[p.id.replace('_left', '')];
  return same?.b === rb ? same : null;
}

const RULES = [
  ['blocked', 'variant', 'Наличие варианта или непостоянной структуры на этом образце не подтверждено',
    p => p.inc || p.anatomicalVariant || p.anatomicalVariation || p.specimenPresence === 'unverified' ||
      ['sesamoid_variant', 'accessory_bone_variant'].includes(p.anatomicalEntity) || /наличие варианта|установить наличие/i.test(need(p))],
  ['blocked', 'ossification', 'Нужны возраст и изображения зон окостенения; наружная сетка взрослого не задаёт эпифиз',
    p => head(p) === 'epiphysis' || /возраст|стади[яи] сращения/i.test(need(p))],
  ['blocked', 'coccyx', 'Нужна граница крестца и копчика на том же образце (GEO-007)', p => p.requiresCoccyxBoundary || /GEO-007/.test(need(p))],
  ['blocked', 'soft_tissue', 'Нужны границы хряща, диска, капсулы или связок, которых нет в модели',
    p => p.softTissueBoundaryRequired && !(p.relations?.length >= 2 && isJoint(p)) || /мягкоткан|некостн|диск/i.test(need(p)) && !isJoint(p)],
  ['blocked', 'missing_participants', 'Нет моделей части участвующих костей', p => p.missingParticipants?.length || p.geometryRequirements?.status === 'missing_model'],
  ['blocked', 'below_mesh_resolution', 'Мелкие отверстия не различимы на упрощённой поверхностной сетке; нужны КТ или исходные изображения',
    p => p.anatomicalEntity === 'foramina_group' || /^Питательн/.test(p.ru)],
  ['approximate', 'contralateral_transfer', 'Есть проверенная точка парной правой записи той же модели; возможен перенос на левую сетку',
    p => {const r = pairedRight(p); return !!r && hasLandmarkPosition(r);}],
  ['not_needed', 'relation', 'Сустав или соединение: показывается костями-участниками и связями карточки; собственная точка не нужна',
    p => isJoint(p) && (p.relations?.length || 0) >= 2],
  ['exact_pin', 'point_feature', 'Точечное образование: правильное представление — один принятый маркер',
    p => p.geometryKind === 'point' || POINT_HEADS.has(head(p)) || (!p.lat && POINT_RU.test(p.ru))],
  ['region', 'extended', 'Протяжённое образование: нужна маска поверхности, линия или объём; одна точка исказила бы протяжённость', () => true],
];
function isJoint(p) {
  return ['joint', 'joint_group', 'fibrous_joint'].includes(p.anatomicalEntity) || JOINT_HEADS.has(head(p)) || /сустав|соединени/i.test(p.ru);
}

export function classify(p) {
  for (const [cls, rule, reason, test] of RULES) if (test(p)) return {cls, rule, reason};
}

const unplaced = A.pins.filter(p => !hasLandmarkPosition(p));
const rows = unplaced.map(p => {
  const {cls, rule, reason} = classify(p);
  const row = {id: p.id, bone: p.b, side: p.side || null, ru: p.ru, lat: p.lat || null, code: p.c || null,
    geometryKind: p.geometryKind || null, class: cls, rule, reason, suppressedOldCoordinate: !!p.p};
  if (cls === 'approximate') row.pairedRight = pairedRight(p).id;
  return row;
});
const count = (key) => rows.reduce((o, r) => (o[r[key]] = (o[r[key]] || 0) + 1, o), {});
const byClassRule = rows.reduce((o, r) => ((o[r.class] ||= {})[r.rule] = (o[r.class][r.rule] || 0) + 1, o), {});
const result = {generated: new Date().toISOString(), records: rows.length, withoutCoordinates: rows.filter(r => !r.suppressedOldCoordinate).length,
  suppressedOldCoordinates: rows.filter(r => r.suppressedOldCoordinate).length, classes: CLASSES, byClass: count('class'), byClassRule,
  rules: RULES.map(([cls, rule, reason]) => ({class: cls, rule, reason})), rows};
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const run = await createEvidenceRun(root, 'unplaced-landmark-classes');
  await run.write('classification.json', result);
  console.log(JSON.stringify({run: path.relative(root, run.dir), records: result.records, withoutCoordinates: result.withoutCoordinates,
    suppressed: result.suppressedOldCoordinates, byClass: result.byClass, byClassRule}, null, 1));
}
