// Read-only extraction of the existing right hand for a research-only reconstruction.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
const run=process.argv[2]; if(!run) throw Error('Evidence run required');
globalThis.ProgressEvent??=class {constructor(type,init){Object.assign(this,init);}};
const ctx={window:{}};vm.createContext(ctx);vm.runInContext(await fs.readFile('site/data.js','utf8'),ctx);
const A=ctx.window.ATLAS;
const file='site/arm-glb.txt',source=await fs.readFile(file),b=Buffer.from(source.toString(),'base64');
const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.length),'');
gltf.scene.updateMatrixWorld(true);const rows=[],names=[];
gltf.scene.traverse(m=>{if(!m.isMesh)return;let o=m;while(o&&!/^[mboc]\|/.test(o.name))o=o.parent;if(!o)return;
 names.push(o.name);const [type,id]=o.name.split('|');
 const handBone=type==='b'&&A.bones[id]?.sub==='hand';
 const handMuscle=type==='m'&&A.muscles[id]?.g?.startsWith('hand_');
 if(!(handBone||handMuscle||id==='flexor_retinaculum'))return;
 const p=m.geometry.attributes.position,ix=m.geometry.index,v=new Vector3(),positions=[],indices=[];
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);positions.push(...v.toArray());}
 for(let i=0;i<(ix?.count??p.count);i++)indices.push(ix?ix.getX(i):i);
 rows.push({name:o.name,id,type,positions,indices});
});
const hashes={};for(const f of ['site/arm-glb.txt','site/data.js','site/index.html','site/local.html','site/data-muscle-recovery.js','site/data-neck-recovery.js'])hashes[f]=crypto.createHash('sha256').update(await fs.readFile(f)).digest('hex');
await fs.writeFile(run+'/hand-context.json',JSON.stringify(rows),{flag:'wx'});
await fs.writeFile(run+'/baseline.json',JSON.stringify({hashes,allArmMeshNames:names,source:{file,sha256:hashes[file]},palmarisCard:A.muscles.palmaris_brevis,selected:rows.map(r=>({id:r.id,type:r.type,triangles:r.indices.length/3}))},null,2),{flag:'wx'});
console.log(JSON.stringify({meshes:rows.length,bones:rows.filter(r=>r.type==='b').length,names:rows.map(r=>r.name)}));
