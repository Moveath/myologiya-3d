// Read-only world-space geometry of every section exactly as loadSection() assembles it:
// main GLB + extra GLB (minus replaced context nodes) + supplemental bones + supplemental muscles.
// Writes research/cache/atlas-geometry/<section>.bin (float32 vertices, uint32 faces) and an index
// with per-node offsets and source hashes; the cache is outside git and never feeds the site.
// Usage: node tools/export-atlas-geometry.mjs [section ...]
import fs from 'node:fs/promises';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3, REVISION} from 'three';
if (REVISION !== '170') throw Error('r170 required');
globalThis.ProgressEvent ??= class {constructor(type, init) {Object.assign(this, {type}, init);}};

const ctx = {window: {}};
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const f of ['data', 'data-leg', 'data-head', 'data-neck', 'data-thorax', 'data-context-bones', 'data-muscle-recovery',
  'data-neck-recovery', 'data-left-limb-muscles'])
  vm.runInContext(readFileSync(`site/${f}.js`, 'utf8'), ctx, {filename: f});
const A = ctx.window.ATLAS;
// Mirrors SECTIONS in site/index.html (file, extraFile, supplementalBones); checked against the HTML below.
const html = readFileSync('site/index.html', 'utf8');
const SECTIONS = {};
for (const m of html.matchAll(/\{ id: '(\w+)', ru: [^\n]*?file: '([\w-]+)'(?:, extraFile: '([\w-]+)')?(?:, supplementalBones: \[([^\]]*)\])?/g))
  SECTIONS[m[1]] = {file: m[2], extra: m[3] || null, bones: (m[4] || '').match(/[\w]+/g) || []};
const wanted = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(SECTIONS);
const sha = b => createHash('sha256').update(b).digest('hex');
const out = path.resolve('research/cache/atlas-geometry');
await fs.mkdir(out, {recursive: true});

async function parse(bytes) {
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  loader.register(() => ({name: 'NO_TEXTURES', loadTexture: () => Promise.resolve(null)}));
  return (await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '')).scene;
}
for (const sec of wanted) {
  const S = SECTIONS[sec];
  if (!S) throw Error('Unknown section ' + sec);
  const sources = [];
  const load = async (file, base64) => {
    const raw = await fs.readFile(file);
    sources.push({file, sha256: sha(raw)});
    return parse(base64 ? Buffer.from(raw.toString(), 'base64') : raw);
  };
  const main = await load(`site/${S.file}-glb.txt`, true);
  if (S.extra) {
    const extra = await load(`site/${S.extra}-glb.txt`, true);
    const replaced = new Set(Object.values(A.contextBoneSources || {}).filter(x => x.sec === sec).map(x => x.sourceId));
    const remove = [];
    main.traverse(o => {if (o.name.startsWith('c|') && replaced.has(o.name.split('|')[1])) remove.push(o);});
    remove.forEach(o => o.removeFromParent());
    main.add(extra);
  }
  for (const id of S.bones) main.add(await load('site/' + A.bones[id].modelFile, false));
  for (const id of A.supplementalMuscles?.[sec] || []) main.add(await load('site/' + A.muscles[id].modelFile, false));
  main.updateMatrixWorld(true);
  const nodes = [], vertexChunks = [], faceChunks = [];
  let vOffset = 0, fOffset = 0;
  main.traverse(mesh => {
    if (!mesh.isMesh) return;
    let owner = mesh;
    while (owner && !/^[mbocs]\|/.test(owner.name)) owner = owner.parent;
    if (!owner) return;
    const p = mesh.geometry.attributes.position, index = mesh.geometry.index, v = new Vector3();
    const vertices = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) {v.fromBufferAttribute(p, i).applyMatrix4(mesh.matrixWorld); vertices.set([v.x, v.y, v.z], i * 3);}
    const count = index ? index.count : p.count, faces = new Uint32Array(count);
    for (let i = 0; i < count; i++) faces[i] = index ? index.getX(i) : i;
    nodes.push({name: owner.name, vertexOffset: vOffset, vertexCount: p.count, faceOffset: fOffset, faceCount: count / 3,
      hasNormals: !!mesh.geometry.attributes.normal});
    vertexChunks.push(Buffer.from(vertices.buffer)); faceChunks.push(Buffer.from(faces.buffer));
    vOffset += p.count; fOffset += count / 3;
  });
  const vertexBytes = Buffer.concat(vertexChunks), faceBytes = Buffer.concat(faceChunks);
  await fs.writeFile(path.join(out, `${sec}.bin`), Buffer.concat([vertexBytes, faceBytes]));
  await fs.writeFile(path.join(out, `${sec}.json`), JSON.stringify({section: sec, three: REVISION, sources,
    vertexBytes: vertexBytes.length, faceBytes: faceBytes.length, nodes}, null, 1));
  console.log(JSON.stringify({sec, nodes: nodes.length, vertices: vOffset, triangles: fOffset, sources: sources.length}));
}
