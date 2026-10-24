// Exact published geometry for source-bound annotations; never rewrites models.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3} from 'three';
const dir=path.resolve(process.argv[2]);
const bones=process.argv.slice(3);
if(!bones.length)bones.push('occipital','temporal_right','temporal_left');
globalThis.ProgressEvent??=class {constructor(type,init){Object.assign(this,init);}};
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const baseline={};
for(const file of ['site/head-glb.txt','site/head-q-glb.txt','site/data-head.js','site/pins-head.js','site/index.html']) {
 try {baseline[file]=hash(await fs.readFile(file));} catch {}
}
await fs.writeFile(path.join(dir,'baseline.json'),JSON.stringify(baseline,null,2),{flag:'wx'});
for(const file of ['head-glb.txt','head-q-glb.txt']) {
 const bytes=Buffer.from(await fs.readFile('site/'+file,'utf8'),'base64');
 const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
 const gltf=await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 gltf.scene.updateMatrixWorld(true); const rows=[];
 gltf.scene.traverse(m=>{
  if(!m.isMesh)return;let owner=m;while(owner&&!owner.name.startsWith('b|'))owner=owner.parent;
  const id=owner?.name.split('|')[1]; if(!bones.includes(id))return;
  const p=m.geometry.attributes.position, idx=m.geometry.index, v=new Vector3(),positions=[],local=[],indices=[];
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);local.push(...v.toArray());v.applyMatrix4(m.matrixWorld);positions.push(...v.toArray());}
  for(let i=0;i<(idx?.count??p.count);i++)indices.push(idx?idx.getX(i):i);
  rows.push({bone:id,mesh:m.name,positions,local,indices,matrix:m.matrixWorld.toArray(),geometryHash:hash(JSON.stringify({positions:local,indices})),materials:Array.isArray(m.material)?m.material.map(x=>x.name):[m.material.name]});
 });
 await fs.writeFile(path.join(dir,file.replace('.txt','-source.json')),JSON.stringify({file,sha256:hash(bytes),rows}),{flag:'wx'});
 console.log(file,rows.map(r=>({bone:r.bone,vertices:r.local.length/3,triangles:r.indices.length/3,materials:r.materials})));
}
