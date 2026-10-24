// Read-only extraction of the current neck scene for a bounded review.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3} from 'three';

const run=process.argv[2];
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const asset=await fs.readFile('site/neck-glb.txt');
const bytes=Buffer.from(asset.toString(),'base64');
const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
gltf.scene.updateMatrixWorld(true);
const names=new Set(['b|hyoid','c|FMA13322','c|FMA13323','c|FMA13395','c|FMA13396','m|omohyoid_right|','m|omohyoid_left|','m|sternocleidomastoid_right|','m|sternocleidomastoid_left|']);
const rows=[];
gltf.scene.traverse(m=>{
  if(!m.isMesh)return;
  let owner=m;while(owner&&!/^[bmc]\|/.test(owner.name))owner=owner.parent;
  if(!owner||!names.has(owner.name))return;
  const p=m.geometry.attributes.position,idx=m.geometry.index,v=new Vector3(),positions=[],indices=[];
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);positions.push(...v.toArray());}
  for(let i=0;i<(idx?.count??p.count);i++)indices.push(idx?idx.getX(i):i);
  rows.push({name:owner.name,positions,indices,materialNames:(Array.isArray(m.material)?m.material:[m.material]).map(x=>x.name),groups:m.geometry.groups});
});
if(rows.length!==9)throw Error(`Expected nine context meshes, got ${rows.length}`);
await fs.writeFile(run+'/blender-review-arrays.json',JSON.stringify({source:'site/neck-glb.txt',sha256:crypto.createHash('sha256').update(asset).digest('hex'),units:'metres; Three.js Y up',rows}),{flag:'wx'});
console.log(rows.map(r=>({name:r.name,triangles:r.indices.length/3,materialNames:r.materialNames,groups:r.groups.length})));
