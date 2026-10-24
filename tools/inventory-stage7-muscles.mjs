// Read-only inventory of published meshes, including hierarchy after gltfpack.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Box3} from 'three';
const run=process.argv[2]; if(!run)throw Error('Evidence run required');
const box={window:{}};vm.createContext(box);const hashes={};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',...(process.argv[3]==='after'?['data-muscle-recovery','data-neck-recovery']:[])]) {
 const file='site/'+name+'.js',bytes=await fs.readFile(file);hashes[file]=hash(bytes);vm.runInContext(bytes.toString(),box);
}
const A=box.window.ATLAS,rows=[];
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
for(const file of ['arm','leg','head','neck','thorax','arm-extra','leg-extra']) {
 const raw=await fs.readFile(`site/${file}-glb.txt`),bytes=Buffer.from(raw.toString(),'base64');hashes[`site/${file}-glb.txt`]=hash(raw);
 const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
 gltf.scene.updateMatrixWorld(true);
 gltf.scene.traverse(m=>{if(!m.isMesh)return;let owner=m;while(owner&&!owner.name.startsWith('m|'))owner=owner.parent;if(!owner)return;
  const [,id,part]=owner.name.split('|'),b=new Box3().setFromObject(m);
  rows.push({file,id,part:part||null,mesh:m.name,triangles:(m.geometry.index?.count||m.geometry.attributes.position.count)/3,bounds:[b.min.toArray(),b.max.toArray()]});
 });
}
if(process.argv[3]==='after')for(const [id,card]of Object.entries(A.muscles).filter(([,c])=>c.modelFile)){
 const raw=await fs.readFile('site/'+card.modelFile);hashes['site/'+card.modelFile]=hash(raw);
 const gltf=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.length),'');gltf.scene.updateMatrixWorld(true);
 gltf.scene.traverse(m=>{if(!m.isMesh)return;let owner=m;while(owner&&!owner.name.startsWith('m|'))owner=owner.parent;if(owner?.name!==`m|${id}|`)throw Error('Unexpected owner');const b=new Box3().setFromObject(m);rows.push({file:card.modelFile,id,part:null,mesh:m.name,triangles:m.geometry.index.count/3,bounds:[b.min.toArray(),b.max.toArray()]});});
}
const missing=[],parts=[],mismatch=[];
for(const [id,m]of Object.entries(A.muscles)){
 const actual=rows.filter(r=>r.id===id);
 if(!actual.length)missing.push({id,ru:m.ru,lat:m.lat,flag:!!m.noModel,group:m.g});
 if(!!m.noModel!==!actual.length)mismatch.push({id,flag:!!m.noModel,meshes:actual.length});
 for(const [part,p]of Object.entries(m.parts||{}))if(!actual.some(r=>r.part===part))parts.push({id,part,ru:p.ru,flag:!!p.noModel,wholePresent:!!actual.length});
}
const result={hashes,cards:Object.keys(A.muscles).length,boneNoModel:Object.entries(A.bones).filter(([,b])=>b.noModel).map(([id])=>id),rows,missing,parts,mismatch};
await fs.writeFile(run+`/muscle-inventory-${process.argv[3]==='after'?'after':'before'}.json`,JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify({cards:result.cards,meshes:rows.length,missing,parts,mismatch,boneNoModel:result.boneNoModel.length}));
