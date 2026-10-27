// Textbook catalogue (CAT-STRUCTURE-TEXTBOOK): every bone and muscle record is listed exactly once
// or is a declared alternate of a canonical record; pair names agree; alternates share the Latin name.
// Node only, reads the published data files; evidence goes to a new run.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {CATALOGUE, ALTERNATES, buildCatalogue, catalogueLeaves, pairBase, pairName} from '../site/atlas-taxonomy.js';
import {structureSide} from '../site/atlas-visibility.js';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = await fs.readFile(path.join(root, 'site/index.html'), 'utf8');
const box = {window: {}}; vm.createContext(box);
for (const src of [...html.matchAll(/<script src="([^"]+\.js)"/g)].map(m => m[1]).filter(s => /^(data|pins)/.test(s)))
  vm.runInContext(await fs.readFile(path.join(root, 'site', src), 'utf8'), box);
const A = box.window.ATLAS;
const card = id => A.muscles[id] || A.bones[id];
const {tree, unplaced} = buildCatalogue(A, (id, sec) => structureSide(sec, id, card(id)));
const tests = [];
const test = (name, fn) => {fn(); tests.push(name);};
const pairs = tree.flatMap(r => r.groups.flatMap(g => g.parts.flatMap(p => p.pairs.map(x => ({...x, region: r.id, group: g.id, part: p.id})))));
const listed = pairs.flatMap(p => Object.values(p.members));
const alternates = pairs.flatMap(p => p.alternates.flatMap(a => Object.values(a.members)));

test('Every bone and muscle record is listed once or as an alternate', () => {
  assert.deepEqual(unplaced, []);
  assert.equal(new Set(listed).size, listed.length, 'duplicate listing');
  const all = [...Object.keys(A.muscles), ...Object.keys(A.bones)].sort();
  assert.deepEqual([...listed, ...alternates].sort(), all);
});
// Left hand phalanges number the fingers ("I пальца") where the right ones name them ("большого пальца");
// both are correct, the row uses the right name. Only these 14 differ, and only in wording.
let namingStyle = [];
test('Paired members share one Latin term; names differ only by finger naming style', () => {
  const both = pairs.filter(p => p.members.left && p.members.right);
  assert.deepEqual(both.filter(p => card(p.members.left).lat !== card(p.members.right).lat).map(p => p.key), []);
  namingStyle = both.filter(p => pairName(card(p.members.left).ru) !== pairName(card(p.members.right).ru))
    .map(p => ({right: p.members.right, left: p.members.left, rightName: card(p.members.right).ru, leftName: card(p.members.left).ru}));
  assert.ok(namingStyle.every(x => /^phalanx_/.test(x.right) && /[IV]+ пальца слева$/.test(x.leftName)), JSON.stringify(namingStyle));
  assert.ok(pairs.every(p => p.name && !/(справа|слева|правая|левая|правый|левый|правое|левое)$/i.test(p.name)), 'side word left in a name');
});
test('Alternates are the same muscle (same Latin name) in other sections', () => {
  for (const [canonical, others] of Object.entries(ALTERNATES)) {
    const pair = pairs.find(p => p.base === canonical);
    assert.ok(pair, canonical);
    assert.equal(pair.alternates.length, others.length, canonical);
    for (const alt of pair.alternates) {
      assert.notEqual(alt.sec, pair.sec);
      for (const id of Object.values(alt.members)) assert.equal(A.muscles[id].lat, pair.lat, id);
    }
  }
});
test('Hyoid is a bone of the facial skull; sacrum belongs to the vertebral column', () => {
  assert.equal(pairs.find(p => p.members.single === 'hyoid' || p.members.right === 'hyoid').group, 'viscerocranium');
  assert.equal(pairs.find(p => p.base === 'sacrum').group, 'spine');
  assert.equal(pairs.find(p => p.base === 'hip_bone').group, 'lower-girdle-bones');
});
test('Mixed data groups are split by textbook group', () => {
  const groupOf = base => pairs.find(p => p.base === base).group;
  assert.equal(groupOf('humerus'), 'humerus');
  assert.deepEqual(['radius', 'ulna'].map(groupOf), ['forearm-bones', 'forearm-bones']);
  assert.deepEqual(['femur', 'patella', 'tibia', 'fibula'].map(groupOf), ['femur-patella', 'femur-patella', 'leg-bones', 'leg-bones']);
  assert.equal(pairs.find(p => p.base === 'sesamoid_pedis').part, 'foot-sesamoids');
  assert.equal(pairs.find(p => p.base === 'splenius_capitis').region, 'back-muscles');
  assert.equal(pairs.find(p => p.base === 'rectus_capitis_posterior_major').region, 'back-muscles');
});
test('Placeholder groups carry a visible note and no structures', () => {
  const empty = tree.flatMap(r => r.groups.filter(g => !g.parts.some(p => p.pairs.length)).map(g => [r.id, g.id, !!g.missing]));
  assert.deepEqual(empty, [['perineum-muscles', 'perineum-other', true]]);
});
test('Abdominal muscles follow Gray/Loyola: anterolateral and posterior walls (ABD-MUSCLES)', () => {
  const rowsOf = id => pairs.filter(p => p.group === id).map(p => p.base);
  assert.deepEqual(rowsOf('abdomen-anterolateral'), ['abdomen_obliquus_externus_abdominis', 'abdomen_obliquus_internus_abdominis',
    'abdomen_transversus_abdominis', 'abdomen_rectus_abdominis', 'abdomen_pyramidalis']);
  assert.deepEqual(rowsOf('abdomen-posterior'), ['abdomen_quadratus_lumborum']);
  assert.ok(pairs.filter(p => p.base.startsWith('abdomen_')).every(p => p.members.right && p.members.left && p.sec === 'trunk'));
});
test('Bones of every catalogue leaf are coloured as one group', () => {
  const leaves = catalogueLeaves(tree).filter(l => l.system !== 'muscles');
  const ids = leaves.flatMap(l => l.ids);
  assert.equal(new Set(ids).size, ids.length);
});
test('Side-free names', () => {
  assert.equal(pairName('Жевательная мышца · правая'), 'Жевательная мышца');
  assert.equal(pairName('1-е ребро, правое'), '1-е ребро');
  assert.equal(pairName('Левая ключица'), 'Ключица');
  assert.equal(pairName('I пястная кость слева'), 'I пястная кость');
  assert.equal(pairName('Таранная кость · справа'), 'Таранная кость');
  assert.equal(pairBase('humerus_left'), 'humerus');
});

const rows = pairs.length, records = listed.length + alternates.length;
const run = await createEvidenceRun(root, 'catalogue-taxonomy-unit');
await run.write('result.json', {status: 'passed', tests, records, rows, alternates: alternates.length, namingStyle,
  regions: tree.map(r => ({id: r.id, system: r.system, ru: r.ru, groups: r.groups.map(g => ({id: g.id, ru: g.ru, rows: g.parts.reduce((n, p) => n + p.pairs.length, 0), missing: g.missing || g.parts.find(p => p.missing)?.missing || null}))}))});
console.log(JSON.stringify({status: 'passed', tests: tests.length, records, rows, alternates: alternates.length, run: path.relative(root, run.dir)}));
