// Read-only world-space context for registering the authored Z-Anatomy parts.
import fs from 'node:fs/promises';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3} from 'three';
const run=process.argv[2];
if(!run)throw Error('Unique evidence directory required');
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const raw=await fs.readFile('site/thorax-glb.txt','utf8'),bytes=Buffer.from(raw,'base64');
const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
gltf.scene.updateMatrixWorld(true);
const rows=[];
gltf.scene.traverse(m=>{
 if(!m.isMesh)return;
 let owner=m;while(owner&&!/^[mboc]\|/.test(owner.name))owner=owner.parent;
 if(!owner||!(/^(b\|thoracic_|m\|thorax_multifidus_|m\|thorax_semispinalis_thoracis_|m\|thorax_rotatores_thoracis)/.test(owner.name)))return;
 const p=m.geometry.attributes.position,ix=m.geometry.index,v=new Vector3(),vertices=[],faces=[];
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);vertices.push(v.toArray());}
 for(let i=0;i<(ix?.count??p.count);i+=3)faces.push([0,1,2].map(k=>ix?ix.getX(i+k):i+k));
 rows.push({name:owner.name,vertices,faces});
});
await fs.writeFile(run+'/atlas-multifidus-context.json',JSON.stringify(rows),{flag:'wx'});
console.log(rows.map(r=>({name:r.name,vertices:r.vertices.length,triangles:r.faces.length})));
