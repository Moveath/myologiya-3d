// Node/Three r170 check of every cardiovascular model: hashes, owners, triangle counts, scale, side, BVH indices and
// native/BVH ray agreement; face masks against the hash and face count of their parent model. The bone and muscle
// data, pins and GLBs must be unchanged since the given checkpoint (QA-STALE-TESTS, LOG-20261026-03).
// Usage: node tools/verify-cardiovascular.mjs RUN [production|trial] [CHECKPOINT_JSON]
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Vector3,Raycaster,DoubleSide} from 'three';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
const run=process.argv[2],mode=process.argv[3]||'trial',checkpointFile=process.argv[4]||path.join(run,'checkpoint.json');let checks=0;
// Current blockers of the bone/muscle atlas (research/BONES_MUSCLES_FULL_AUDIT.md); the cardiovascular work must not change them.
const LEGACY={boneNoModel:0,muscleNoModel:14,partNoModel:21};
const check=(x,msg)=>{assert.ok(x,msg);checks++;};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const context={window:{}};vm.createContext(context);
const html=await fs.readFile('site/index.html','utf8');
for(const name of [...html.matchAll(/<script src="(data[\w-]*)\.js"/g)].map(m=>m[1]))vm.runInContext(await fs.readFile('site/'+name+'.js','utf8'),context);
const A=context.window.ATLAS;
check(Object.values(A.bones).filter(x=>x.noModel).length===LEGACY.boneNoModel,'Bone blockers preserved');
check(Object.values(A.muscles).filter(x=>x.noModel).length===LEGACY.muscleNoModel,'Muscle blockers preserved');
check(Object.values(A.muscles).flatMap(x=>Object.values(x.parts||{})).filter(x=>x.noModel).length===LEGACY.partNoModel,'Part blockers preserved');
const all=[...Object.keys(A.bones),...Object.keys(A.muscles),...Object.keys(A.structures)];check(new Set(all).size===all.length,'No cross-system ID collisions');
for(const [id,c]of Object.entries(A.structures)){
 for(const k of ['partOf','origin','drainsTo'])if(c[k])check(!!A.structures[c[k]],id+' typed link '+k);
 check(c.refs.length>=2,id+' sources');
 check(!c.noModel||!c.modelFile,id+' no false model path');
}
const script=html.match(/<script type="module"[^>]*>([\s\S]*?)<\/script>/)[1];
new vm.Script(script.replace(/^import .*;$/gm,''));check(true,'Main module syntax');
const records=[],admissions=JSON.parse(await fs.readFile('scripts/cardiovascular_admissions.json','utf8'));
const sources=[];
for(const file of (await fs.readdir('build_cardiovascular/bp3d-3.0-v1')).filter(x=>x.endsWith('.json'))){
 const r=JSON.parse(await fs.readFile('build_cardiovascular/bp3d-3.0-v1/'+file));
 if(mode==='production'&&A.structures[r.id].noModel)continue;
 check(hash(await fs.readFile(r.source.file))===r.source.sha256,r.id+' original untouched');
 sources.push({id:r.id,file:mode==='production'?'site/'+A.structures[r.id].modelFile:r.trial,sha256:r.sha256,triangles:r.triangles,boundsM:r.boundsM,kind:'bodyparts3d'});
}
if(mode==='production')for(const [id,a]of Object.entries(admissions).filter(([,a])=>a.kind==='z-anatomy')){
 check(A.structures[id].modelFile===a.modelFile&&A.structures[id].modelKind==='z-anatomy',id+' Z-Anatomy card admitted');
 sources.push({id,file:'site/'+a.modelFile,sha256:a.sha256,kind:'z-anatomy'});
}
const HEART_BOX=JSON.parse(await fs.readFile('build_cardiovascular/bp3d-3.0-v1/cv_heart.json','utf8')).boundsM;
for(const r of sources){
 const card=A.structures[r.id];
 const bytes=await fs.readFile(r.file);check(hash(bytes)===r.sha256,r.id+' GLB hash');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
 const meshes=[];gltf.scene.traverse(m=>{if(m.isMesh)meshes.push(m);});check(meshes.length===1,r.id+' one owner');
 const mesh=meshes[0],g=mesh.geometry;check(mesh.name==='s|'+r.id,'Stable node ID');gltf.scene.updateMatrixWorld(true);
 if(r.triangles)check(g.index.count===r.triangles*3,'No lost triangles');check([...g.attributes.normal.array].every(Number.isFinite),'Finite normals');
 g.computeBoundingBox();const b=g.boundingBox;if(r.boundsM)check(Math.abs(b.min.y-r.boundsM[0][1])<1e-6,'No scale drift');
 // Body side applies outside the heart; inside or on the heart "right/left" names the half of the heart (the right
 // marginal branch and right-ventricular papillary muscles lie left of the body midline).
 const centre=[(b.min.x+b.max.x)/2,(b.min.y+b.max.y)/2,(b.min.z+b.max.z)/2],onHeart=centre.every((v,i)=>v>=HEART_BOX[0][i]-.005&&v<=HEART_BOX[1][i]+.005);
 if(card.side!=='unseparated'&&!onHeart)check((b.min.x+b.max.x)*(card.side==='left'?1:-1)>0,r.id+' correct anatomical side');
 if(r.id==='cv_valve_tricuspid'){
   const other=JSON.parse(await fs.readFile('build_cardiovascular/bp3d-3.0-v1/cv_valve_mitral.json'));
   check(b.min.x+b.max.x<other.boundsM[0][0]+other.boundsM[1][0],'Right AV valve rightward of left AV valve, not of body midline');
 }
 const idx=hash(Buffer.from(g.index.array.buffer));g.boundsTree=new MeshBVH(g,{indirect:true});check(hash(Buffer.from(g.index.array.buffer))===idx,'BVH indirect preserves indices');
 const native=mesh.raycast;mesh.material.side=DoubleSide;
 let rayHits=0;
 const triangles=r.triangles||g.index.count/3;
 for(const face of [Math.floor(triangles*.23),Math.floor(triangles*.61),Math.floor(triangles*.83)]){
  const t=[0,1,2].map(i=>new Vector3().fromBufferAttribute(g.attributes.position,g.index.getX(face*3+i)));
  const n=t[1].clone().sub(t[0]).cross(t[2].clone().sub(t[0])).normalize();if(!n.length())continue;
  const center=t[0].clone().add(t[1]).add(t[2]).multiplyScalar(1/3);
  const ray=new Raycaster(center.clone().addScaledVector(n,.03),n.negate()),a=[],b=[];
  native.call(mesh,ray,a);acceleratedRaycast.call(mesh,ray,b);a.sort((a,b)=>a.distance-b.distance);b.sort((a,b)=>a.distance-b.distance);
  check(a.length===b.length,r.id+' BVH/native hits');check(a.length>0,r.id+' real ray');rayHits++;
  check(Math.abs(a[0].distance-b[0].distance)<1e-7,'Same first-hit distance');
  check(a.some(x=>x.faceIndex===b[0].faceIndex&&Math.abs(x.distance-b[0].distance)<1e-7),'Same faceIndex (including duplicate-face ties)');
 }
 check(rayHits>0,r.id+' ray coverage');records.push({id:r.id,kind:r.kind,triangles,rayHits});g.dispose();mesh.material.dispose();
}
// Face masks: parent hash and face count, sorted unique faces in range; the masked sub-geometry keeps BVH indices.
const masks=[];
if(mode==='production')for(const [id,a]of Object.entries(admissions).filter(([,a])=>a.kind==='face-mask')){
 const card=A.structures[id],raw=await fs.readFile('site/'+a.maskFile),mask=JSON.parse(raw);
 check(hash(raw)===a.sha256&&card.modelKind==='face-mask'&&card.segmentOf===mask.parent,id+' mask admitted');
 const parent=await fs.readFile('site/'+A.structures[mask.parent].modelFile);
 check(hash(parent)===mask.parentSha256,id+' parent hash');
 const gltf=await new GLTFLoader().parseAsync(parent.buffer.slice(parent.byteOffset,parent.byteOffset+parent.length),'');
 let source;gltf.scene.traverse(m=>{if(m.isMesh)source=m;});
 const index=source.geometry.index.array,faces=mask.faces;
 check(mask.parentFaces===index.length/3,id+' parent face count');
 check(faces.every((f,i)=>Number.isInteger(f)&&f>=0&&f<mask.parentFaces&&(i===0||f>faces[i-1]))&&faces.length===mask.faceCount,id+' sorted unique faces');
 const sub=new Uint32Array(faces.length*3);faces.forEach((f,i)=>sub.set(index.subarray(f*3,f*3+3),i*3));
 const {BufferGeometry,BufferAttribute,Mesh}=await import('three');
 const g=new BufferGeometry();for(const [n,attr]of Object.entries(source.geometry.attributes))g.setAttribute(n,attr);g.setIndex(new BufferAttribute(sub,1));
 const before=hash(Buffer.from(sub.buffer));g.boundsTree=new MeshBVH(g,{indirect:true});check(hash(Buffer.from(g.index.array.buffer))===before,id+' BVH keeps mask indices');
 const mesh=new Mesh(g);mesh.material.side=DoubleSide;const f=Math.floor(faces.length/2);
 const t=[0,1,2].map(i=>new Vector3().fromBufferAttribute(g.attributes.position,sub[f*3+i]));const n=t[1].clone().sub(t[0]).cross(t[2].clone().sub(t[0])).normalize();
 const c=t[0].clone().add(t[1]).add(t[2]).multiplyScalar(1/3),ray=new Raycaster(c.clone().addScaledVector(n,.03),n.negate()),hits=[];
 acceleratedRaycast.call(mesh,ray,hits);check(hits.some(h=>h.faceIndex===f),id+' BVH ray finds the masked face');
 masks.push({id,parent:mask.parent,faces:faces.length});
}
const snapshot=JSON.parse(await fs.readFile(checkpointFile));
const untouched=snapshot.filesManifest.filter(r=>/^site\/(?:.*-glb\.txt|pins.*\.js|data-(?!cardiovascular).*\.js|models\/.*\.glb)$/.test(r.path));
for(const item of untouched)check(hash(await fs.readFile(item.path))===item.sha256,'Original/card/pin unchanged '+item.path);
const result={status:'passed',mode,checks,models:records,masks,retainedOriginalFiles:untouched.length,checkpoint:checkpointFile,legacyCounts:LEGACY};
await fs.writeFile(path.join(run,'node-'+mode+'.json'),JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify({status:'passed',mode,checks,models:records.length,masks:masks.length,retainedOriginalFiles:untouched.length}));
