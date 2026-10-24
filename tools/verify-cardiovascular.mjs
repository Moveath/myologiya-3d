import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Vector3,Raycaster,DoubleSide} from 'three';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
const run=process.argv[2],mode=process.argv[3]||'trial';let checks=0;
const check=(x,msg)=>{assert.ok(x,msg);checks++;};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const context={window:{}};vm.createContext(context);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','data-muscle-recovery','data-neck-recovery','data-cardiovascular'])vm.runInContext(await fs.readFile('site/'+name+'.js','utf8'),context);
const A=context.window.ATLAS;
check(Object.values(A.bones).filter(x=>x.noModel).length===20,'20 bone blockers preserved');
check(Object.values(A.muscles).filter(x=>x.noModel).length===14,'14 muscle blockers preserved');
check(Object.values(A.muscles).flatMap(x=>Object.values(x.parts||{})).filter(x=>x.noModel).length===21,'21 part blockers preserved');
const all=[...Object.keys(A.bones),...Object.keys(A.muscles),...Object.keys(A.structures)];check(new Set(all).size===all.length,'No cross-system ID collisions');
for(const [id,c]of Object.entries(A.structures)){
 for(const k of ['partOf','origin','drainsTo'])if(c[k])check(!!A.structures[c[k]],id+' typed link '+k);
 check(c.refs.length>=2,id+' sources');
 check(!c.noModel||!c.modelFile,id+' no false model path');
}
const html=await fs.readFile('site/index.html','utf8');
const script=html.match(/<script type="module"[^>]*>([\s\S]*?)<\/script>/)[1];
new vm.Script(script.replace(/^import .*;$/gm,''));check(true,'Main module syntax');
const records=[];
for(const file of (await fs.readdir('build_cardiovascular/bp3d-3.0-v1')).filter(x=>x.endsWith('.json'))){
 const r=JSON.parse(await fs.readFile('build_cardiovascular/bp3d-3.0-v1/'+file));
 const card=A.structures[r.id];if(mode==='production'&&card.noModel)continue;
 const filename=mode==='production'?'site/'+card.modelFile:r.trial;
 const bytes=await fs.readFile(filename);check(hash(bytes)===r.sha256,r.id+' GLB hash');
 check(hash(await fs.readFile(r.source.file))===r.source.sha256,r.id+' original untouched');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
 const meshes=[];gltf.scene.traverse(m=>{if(m.isMesh)meshes.push(m);});check(meshes.length===1,r.id+' one owner');
 const mesh=meshes[0],g=mesh.geometry;check(mesh.name==='s|'+r.id,'Stable node ID');gltf.scene.updateMatrixWorld(true);
 check(g.index.count===r.triangles*3,'No lost triangles');check([...g.attributes.normal.array].every(Number.isFinite),'Finite normals');
 g.computeBoundingBox();const b=g.boundingBox;check(Math.abs(b.min.y-r.boundsM[0][1])<1e-6,'No scale drift');
 if(card.side!=='unseparated'&&!r.id.startsWith('cv_valve_'))check((b.min.x+b.max.x)*(card.side==='left'?1:-1)>0,r.id+' correct anatomical side');
 if(r.id==='cv_valve_tricuspid'){
   const other=JSON.parse(await fs.readFile('build_cardiovascular/bp3d-3.0-v1/cv_valve_mitral.json'));
   check(b.min.x+b.max.x<other.boundsM[0][0]+other.boundsM[1][0],'Right AV valve rightward of left AV valve, not of body midline');
 }
 const idx=hash(Buffer.from(g.index.array.buffer));g.boundsTree=new MeshBVH(g,{indirect:true});check(hash(Buffer.from(g.index.array.buffer))===idx,'BVH indirect preserves indices');
 const native=mesh.raycast;mesh.material.side=DoubleSide;
 let rayHits=0;
 for(const face of [Math.floor(r.triangles*.23),Math.floor(r.triangles*.61),Math.floor(r.triangles*.83)]){
  const t=[0,1,2].map(i=>new Vector3().fromBufferAttribute(g.attributes.position,g.index.getX(face*3+i)));
  const n=t[1].clone().sub(t[0]).cross(t[2].clone().sub(t[0])).normalize();if(!n.length())continue;
  const center=t[0].clone().add(t[1]).add(t[2]).multiplyScalar(1/3);
  const ray=new Raycaster(center.clone().addScaledVector(n,.03),n.negate()),a=[],b=[];
  native.call(mesh,ray,a);acceleratedRaycast.call(mesh,ray,b);a.sort((a,b)=>a.distance-b.distance);b.sort((a,b)=>a.distance-b.distance);
  check(a.length===b.length,r.id+' BVH/native hits');check(a.length>0,r.id+' real ray');rayHits++;
  check(Math.abs(a[0].distance-b[0].distance)<1e-7,'Same first-hit distance');
  check(a.some(x=>x.faceIndex===b[0].faceIndex&&Math.abs(x.distance-b[0].distance)<1e-7),'Same faceIndex (including duplicate-face ties)');
 }
 check(rayHits>0,r.id+' ray coverage');records.push({id:r.id,triangles:r.triangles,rayHits});g.dispose();mesh.material.dispose();
}
const snapshot=JSON.parse(await fs.readFile(run+'/checkpoint.json'));
const untouched=snapshot.filesManifest.filter(r=>/^site\/(?:.*-glb\.txt|pins.*\.js|data-(?!cardiovascular).*\.js|models\/.*\.glb)$/.test(r.path));
for(const item of untouched)check(hash(await fs.readFile(item.path))===item.sha256,'Original/card/pin unchanged '+item.path);
const result={status:'passed',mode,checks,models:records,retainedOriginalFiles:untouched.length,oldCounts:{boneNoModel:20,muscleNoModel:14,partNoModel:21}};
await fs.writeFile(path.join(run,'node-'+mode+'.json'),JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify({status:'passed',mode,checks,models:records.length,retainedOriginalFiles:untouched.length}));
