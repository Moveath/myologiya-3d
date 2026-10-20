// Validate actual decoded output, not only a generator's pre-export counters.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3, REVISION} from 'three';

export async function inspectGeometry(filename) {
  const source = await fs.readFile(filename);
  const bytes = filename.endsWith('.txt') ? Buffer.from(source.toString('utf8'), 'base64') : source;
  globalThis.ProgressEvent ??= class { constructor(type, init) { Object.assign(this, {type}, init); } };
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  loader.register(() => ({name:'EXPORT_GEOMETRY_CHECK', loadTexture:() => Promise.resolve(null)}));
  const gltf = await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  const meshes = [];
  gltf.scene.traverse(mesh => {
    if (!mesh.isMesh) return;
    let owner = mesh;
    while (owner && !/^[mboc]\|/.test(owner.name)) owner = owner.parent;
    const p = mesh.geometry.attributes.position, n = mesh.geometry.attributes.normal, index = mesh.geometry.index;
    const count = index?.count ?? p.count;
    const bone = owner?.name.startsWith('b|');
    const triangleKeys = [];
    const a = new Vector3(), b = new Vector3(), c = new Vector3(), ab = new Vector3(), ac = new Vector3();
    let zeroFaces = 0, invalidPositions = 0, invalidNormals = 0;
    const used = new Set();
    for (let i = 0; i < count; i += 3) {
      const ids = [0,1,2].map(j => index ? index.getX(i+j) : i+j);
      a.fromBufferAttribute(p,ids[0]); b.fromBufferAttribute(p,ids[1]); c.fromBufferAttribute(p,ids[2]);
      ab.subVectors(b,a); ac.subVectors(c,a);
      if (ab.cross(ac).lengthSq() === 0) zeroFaces++;
      else ids.forEach(id => used.add(id));
      if (bone) {
        const corners=[a,b,c].map(v=>{
          const q=v.clone().applyMatrix4(mesh.matrixWorld),bytes=Buffer.alloc(12);
          [q.x,q.y,q.z].forEach((x,j)=>bytes.writeFloatLE(x===0?0:x,j*4));
          return bytes;
        });
        // Cyclic rotations preserve winding; reversed faces remain distinct.
        const cyclic=[0,1,2].map(i=>Buffer.concat([corners[i],corners[(i+1)%3],corners[(i+2)%3]]));
        cyclic.sort(Buffer.compare);triangleKeys.push(cyclic[0]);
      }
    }
    for (let i = 0; i < p.count; i++) {
      a.fromBufferAttribute(p,i);
      if (![a.x,a.y,a.z].every(Number.isFinite)) invalidPositions++;
      if (used.has(i)) {
        const length = n ? b.fromBufferAttribute(n,i).length() : NaN;
        if (!Number.isFinite(length) || Math.abs(length-1) > 0.02) invalidNormals++;
      }
    }
    meshes.push({owner:owner?.name ?? mesh.name, faces:count/3, vertices:p.count, zeroFaces,
      invalidPositions, invalidNormals, determinant:mesh.matrixWorld.determinant(),
      ...(bone?{orientedTrianglesFloat32SHA256:crypto.createHash('sha256').update(Buffer.concat(triangleKeys.sort(Buffer.compare))).digest('hex')}: {})});
    mesh.geometry.dispose();
    for (const material of [mesh.material].flat()) material?.dispose();
  });
  return {file:filename, sha256:crypto.createHash('sha256').update(source).digest('hex'), three:REVISION,
    imagesSkipped:true, meshes};
}

export function validateExport(reference, output) {
  const errors = [];
  const byOwner = report => {
    const map = new Map();
    for (const row of report.meshes) {
      const value = map.get(row.owner) ?? {faces:0, zeroFaces:0, instances:0,triangleHashes:[]};
      value.faces += row.faces; value.zeroFaces += row.zeroFaces; value.instances++;
      value.triangleHashes.push(row.orientedTrianglesFloat32SHA256 ?? null);
      map.set(row.owner,value);
    }
    return map;
  };
  const before = byOwner(reference), after = byOwner(output);
  for (const [owner, old] of before) {
    const next = after.get(owner);
    if (!next) { errors.push(`${owner}: owner lost`); continue; }
    if (next.instances !== old.instances) errors.push(`${owner}: mesh instance count changed`);
    if (owner.startsWith('b|') && next.faces !== old.faces) errors.push(`${owner}: bone triangle count changed`);
    if (owner.startsWith('b|') && JSON.stringify(next.triangleHashes.sort()) !== JSON.stringify(old.triangleHashes.sort()))
      errors.push(`${owner}: bone triangle positions/winding changed at float32 world precision`);
    if (next.zeroFaces > old.zeroFaces) errors.push(`${owner}: new zero-area triangles`);
  }
  for (const [owner] of after) if (!before.has(owner)) errors.push(`${owner}: unexpected owner`);
  for (const row of output.meshes) {
    if (row.invalidPositions || row.invalidNormals || !Number.isFinite(row.determinant) || row.determinant <= 0)
      errors.push(`${row.owner}: invalid positions/normals/transform`);
  }
  return errors;
}
