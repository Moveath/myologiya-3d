// Abdominal muscles (ABD-MUSCLES): nomenclature against the IFAA fixture and the printed Russian edition,
// two-source evidence of every card field, the published r170/meshopt models (hash, owner, triangles, side,
// BVH indirect indices, BVH/native ray agreement) and unchanged earlier atlas files since CHECKPOINT_DIR.
// Usage: node tools/verify-abdomen-data.mjs CHECKPOINT_DIR   (new evidence run only)
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {BufferGeometry, BufferAttribute, DoubleSide, Mesh, MeshBasicMaterial, Raycaster, Vector3, REVISION} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {MeshBVH, acceleratedRaycast} from 'three-mesh-bvh';
import {createEvidenceRun} from './evidence-run.mjs';
if (REVISION !== '170') throw Error('r170 required');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const checkpointDir = process.argv[2];
if (!checkpointDir) throw Error('Usage: node tools/verify-abdomen-data.mjs CHECKPOINT_DIR');
const sha = b => createHash('sha256').update(b).digest('hex');
let checks = 0;
const check = (ok, label) => {assert.ok(ok, label); checks++;};

const html = await fs.readFile(path.join(root, 'site/index.html'), 'utf8');
const box = {window: {}};
vm.createContext(box);
for (const name of [...html.matchAll(/<script src="((?:data|pins)[\w-]*)\.js"/g)].map(m => m[1]))
  vm.runInContext(await fs.readFile(path.join(root, 'site', name + '.js'), 'utf8'), box, {filename: name});
const A = box.window.ATLAS;
const provenance = JSON.parse(await fs.readFile(path.join(root, 'site/models/bodyparts3d-3.0/abdomen-muscles/provenance.json'), 'utf8'));
const fixture = JSON.parse(await fs.readFile(path.join(root, 'verify/ifaa-abdomen-muscles.json'), 'utf8')).terms;
const ids = provenance.files.map(f => f.id);
const cards = Object.entries(A.muscles).filter(([id]) => id.startsWith('abdomen_'));

// Catalogue registration
check(ids.length === 12 && cards.length === 12 && cards.every(([id]) => ids.includes(id)), '12 cards = 12 published models');
check(JSON.stringify(A.supplementalMuscles.trunk) === JSON.stringify(ids), 'Trunk supplemental muscles are exactly the published models');
const groups = A.groups.filter(g => g.id.startsWith('abdomen_'));
check(groups.length === 2 && groups.every(g => g.sec === 'trunk' && g.region === 'abdomen'), 'Two trunk groups in the abdomen subsection');
check(/id: 'abdomen', ru: 'Мышцы живота'/.test(html), 'Trunk section has the abdomen subsection');

// Nomenclature: IFAA Latin, printed Russian equivalent (Kolesnikov 2003)
const latin = s => s.toLowerCase().replace(/[♂▲*]/g, '').replace(/^m\.\s*/, 'musculus ').replace(/^lig\.\s*/, 'ligamentum ').split(';')[0].trim();
const term = (d, label, ru) => {
  const t = fixture[d.code];
  check(!!t, label + ' IFAA code');
  check(latin(d.lat) === latin(t.lat), `${label} TA98 Latin ${d.lat} / ${t.lat}`);
  check(ru.startsWith(t.ruPrinted.split(';')[0]), `${label} printed Russian ${ru} / ${t.ruPrinted}`);
};
// Every field: text, status and two independent https sources with locators
const evidence = (refs, label) => {
  check(Array.isArray(refs) && new Set(refs.map(r => r.url.split('#')[0])).size >= 2, label + ' two sources');
  check(refs.every(r => /^https:\/\//.test(r.url) && r.locator && r.title), label + ' locators');
};
for (const [id, m] of cards) {
  const side = id.endsWith('_left') ? 'left' : 'right';
  check(m.side === side && m.ru.endsWith(side === 'left' ? ' · слева' : ' · справа'), id + ' side label');
  term(m, id, m.ru);
  for (const f of ['o', 'i', 'a', 'n', 's']) {
    check(typeof m[f] === 'string' && m[f].length > 5 && m.fieldStatus[f] === 'checked_two_sources', `${id}:${f} text`);
    evidence(m.fieldRefs[f], `${id}:${f}`);
  }
  check(m.note && m.noteRefs.length >= 2, id + ' disagreements kept in the note');
  for (const f of m.features || []) {term(f, `${id}:${f.code}`, f.ru); evidence(f.refs, `${id}:${f.code}`); check(f.noModel && !f.geometryValidated, `${id}:${f.code} no geometry claimed`);}
  check(m.refs.some(r => r.url.includes('ifaa.unifr.ch')) && m.refs.some(r => r.locator.startsWith('С. 48–49')), id + ' nomenclature references');
  check(m.relatedMuscles.length === 1 && A.muscles[m.relatedMuscles[0]], id + ' paired card');
  check(m.modelStatus === 'educational_limited' && m.modelReview.fullAnatomicalAcceptance === false && m.modelNotice, id + ' model limits');
  check(!A.pins.some(p => (p.m || []).some(e => (e.id || e) === id)), id + ' no fabricated attachment markers');
}

// Models: real r170 + meshopt loading, owner, triangles, side, BVH indices and ray agreement
await MeshoptDecoder.ready;
const licence = await fs.readFile(path.join(root, 'site/models/bodyparts3d-3.0/abdomen-muscles/LICENSE-MODELS.txt'), 'utf8');
const models = [];
for (const f of provenance.files) {
  const card = A.muscles[f.id];
  check(card.modelFile === f.file && licence.includes(`${f.id}.glb (${f.fma})`), f.id + ' card file and licence');
  const bytes = await fs.readFile(path.join(root, 'site', f.file));
  check(sha(bytes) === f.sha256, f.id + ' GLB hash');
  const gltf = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.length), '');
  const meshes = [];
  gltf.scene.traverse(o => {if (o.isMesh) meshes.push(o);});
  check(meshes.length === 1, f.id + ' one mesh');
  let owner = meshes[0];
  while (owner && !owner.name.startsWith('m|')) owner = owner.parent;
  check(owner?.name === `m|${f.id}|`, f.id + ' owner node');
  const g = meshes[0].geometry;
  check(g.index.count === f.triangles * 3, f.id + ' triangles');
  check([...g.attributes.normal.array].every(Number.isFinite) && [...g.attributes.position.array].every(Number.isFinite), f.id + ' finite');
  g.computeBoundingBox();
  const c = g.boundingBox.getCenter(new Vector3());
  check(f.id.endsWith('_left') ? c.x > 0 : c.x < 0, f.id + ' side (body right is -x)');
  const before = sha(Buffer.from(g.index.array.buffer, g.index.array.byteOffset, g.index.array.byteLength));
  g.boundsTree = new MeshBVH(g, {indirect: true});
  check(sha(Buffer.from(g.index.array.buffer, g.index.array.byteOffset, g.index.array.byteLength)) === before, f.id + ' BVH keeps indices');
  const mesh = new Mesh(g, new MeshBasicMaterial({side: DoubleSide}));
  let agree = 0;
  for (const k of [0.17, 0.43, 0.71]) {
    const fi = Math.floor(f.triangles * k), t = [0, 1, 2].map(i => new Vector3().fromBufferAttribute(g.attributes.position, g.index.array[fi * 3 + i]));
    const n = t[1].clone().sub(t[0]).cross(t[2].clone().sub(t[0])).normalize(), p = t[0].clone().add(t[1]).add(t[2]).multiplyScalar(1 / 3);
    const ray = new Raycaster(p.clone().addScaledVector(n, 0.05), n.clone().negate()), fast = [], slow = [];
    acceleratedRaycast.call(mesh, ray, fast);
    Mesh.prototype.raycast.call(mesh, ray, slow);
    fast.sort((a, b) => a.distance - b.distance); slow.sort((a, b) => a.distance - b.distance);
    check(fast.length === slow.length && fast.every((h, i) => h.faceIndex === slow[i].faceIndex && Math.abs(h.distance - slow[i].distance) < 1e-9), f.id + ' BVH/native rays');
    agree += fast.some(h => h.faceIndex === fi);
  }
  check(agree >= 2, f.id + ' rays find their sampled faces');
  models.push({id: f.id, triangles: f.triangles, bytes: f.bytes, centreM: c.toArray().map(x => +x.toFixed(4))});
}

// Earlier bone/muscle files and models are unchanged since the checkpoint; the only new site files are ours.
const manifest = JSON.parse(await fs.readFile(path.join(root, checkpointDir, 'manifest.json'), 'utf8'));
const guarded = manifest.filesManifest.filter(r => /^site\/(?:.*-glb\.txt|pins.*\.js|data-.*\.js|models\/.*\.glb)$/.test(r.path));
for (const r of guarded) check(sha(await fs.readFile(path.join(root, r.path))) === r.sha256, r.path + ' unchanged since checkpoint');
const known = new Set(manifest.filesManifest.map(r => r.path));
const top = (await fs.readdir(path.join(root, 'site'), {withFileTypes: true})).filter(e => e.isFile()).map(e => 'site/' + e.name);
const nested = (await fs.readdir(path.join(root, 'site/models'), {recursive: true})).map(p => 'site/models/' + p.replaceAll('\\', '/'));
const added = [...top, ...nested].filter(p => /\.(js|glb|txt)$/.test(p) && !known.has(p));
check(added.every(p => p === 'site/data-abdomen.js' || p.startsWith('site/models/bodyparts3d-3.0/abdomen-muscles/')), 'No other new site data: ' + added.join(', '));

const run = await createEvidenceRun(root, 'abdomen-data');
const result = {status: 'passed', checks, models, guardedUnchanged: guarded.length, newSiteFiles: added, checkpoint: checkpointDir,
  scope: 'Node/three r170; nomenclature and evidence contracts, published geometry, unchanged earlier files. Not an anatomist review.'};
await run.write('result.json', result);
console.log(JSON.stringify({...result, models: models.length, run: path.relative(root, run.dir)}));
