// Read-only world-space arrays of every left limb bone the atlas loads (extra assets + published left GLBs).
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3, REVISION} from 'three';
const run = path.resolve(process.argv[2]);
if (REVISION !== '170') throw Error('r170 required');
globalThis.ProgressEvent ??= class {constructor(type, init) {Object.assign(this, {type}, init);}};
const arrays = {}, assets = [];
async function add(file, bytes) {
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  loader.register(() => ({name: 'NO_TEXTURES', loadTexture: () => Promise.resolve(null)}));
  const scene = (await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '')).scene;
  scene.updateMatrixWorld(true);
  scene.traverse(mesh => {
    if (!mesh.isMesh) return;
    let owner = mesh;
    while (owner && !owner.name.startsWith('b|')) owner = owner.parent;
    if (!owner) return;
    const id = owner.name.split('|')[1], row = arrays[id] ??= {id, file, vertices: [], faces: []};
    const p = mesh.geometry.attributes.position, index = mesh.geometry.index, v = new Vector3(), offset = row.vertices.length / 3;
    for (let i = 0; i < p.count; i++) {v.fromBufferAttribute(p, i).applyMatrix4(mesh.matrixWorld); row.vertices.push(...v.toArray());}
    for (let i = 0; i < (index?.count ?? p.count); i++) row.faces.push(offset + (index ? index.getX(i) : i));
  });
}
for (const file of ['site/arm-extra-glb.txt', 'site/leg-extra-glb.txt']) {
  const source = await fs.readFile(file);
  await add(file, Buffer.from(source.toString(), 'base64'));
  assets.push({file, sha256: createHash('sha256').update(source).digest('hex')});
}
const base = 'site/models/bodyparts3d-3.0';
for (const dir of (await fs.readdir(base)).filter(d => d.startsWith('left-') || d === 'mirrored-left-foot')) {
  for (const name of (await fs.readdir(path.join(base, dir))).filter(n => n.endsWith('.glb'))) {
    const file = `${base}/${dir}/${name}`, source = await fs.readFile(file);
    await add(file, source);
    assets.push({file, sha256: createHash('sha256').update(source).digest('hex')});
  }
}
await fs.writeFile(path.join(run, 'left-bone-arrays.json'), JSON.stringify(arrays), {flag: 'wx'});
await fs.writeFile(path.join(run, 'left-bone-assets.json'), JSON.stringify(assets, null, 2), {flag: 'wx'});
console.log(JSON.stringify({bones: Object.keys(arrays).length, ids: Object.keys(arrays).sort()}));
