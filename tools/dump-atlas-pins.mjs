// Print the landmark fields used by left-limb transfer as JSON (read-only).
// Loads data and regional pins in page order but never the generated pins-left-transfer.js patch,
// so the generator always starts from the reviewed source records.
import fs from 'node:fs';
import vm from 'node:vm';
const FILES = ['data', 'data-leg', 'data-head', 'data-neck', 'data-thorax', 'data-context-bones', 'data-muscle-recovery',
  'data-neck-recovery', 'data-left-limb-muscles', 'pins', 'pins-leg', 'pins-head', 'pins-head-extra', 'pins-neck',
  'pins-thorax', 'pins-context-bones', 'pins-shared'];
const ctx = {window: {}};
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const f of FILES) vm.runInContext(fs.readFileSync(`site/${f}.js`, 'utf8'), ctx, {filename: f});
const A = ctx.window.ATLAS;
const KEEP = ['id', 'b', 't', 'c', 'ru', 'lat', 'p', 'n', 'm', 'loc', 'geometryKind', 'anchorStatus', 'templateRecord', 'side', 'part', 'inc',
  'x', 'refs', 'geometryKindReason', 'anatomicalDefinition', 'note', 'modelNote'];
process.stdout.write(JSON.stringify({
  pins: A.pins.map(p => Object.fromEntries(KEEP.filter(k => p[k] !== undefined).map(k => [k, p[k]]))),
  muscles: Object.fromEntries(Object.entries(A.muscles).map(([id, c]) => [id, {ru: c.ru, side: c.side ?? null, parts: Object.fromEntries(Object.entries(c.parts || {}).map(([k, p]) => [k, p.lat])), noModel: !!c.noModel}])),
  bones: Object.fromEntries(Object.entries(A.bones).map(([id, c]) => [id, {ru: c.ru, side: c.side ?? null, noModel: !!c.noModel}])),
}));
