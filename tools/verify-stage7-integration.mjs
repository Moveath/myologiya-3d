import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {Raycaster,Vector3,DoubleSide} from 'three';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
const run=process.argv[2],box={window:{}};vm.createContext(box);let checks=0;
const check=(v,msg)=>{assert.ok(v,msg);checks++;};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones'])vm.runInContext(await fs.readFile('site/'+name+'.js','utf8'),box);
const before=JSON.parse(JSON.stringify(box.window.ATLAS.muscles));
vm.runInContext(await fs.readFile('site/data-muscle-recovery.js','utf8'),box);const A=box.window.ATLAS;
check(Object.keys(A.muscles).length===257,'255 original + 2 confirmed components');
check(Object.values(A.bones).filter(b=>b.noModel).length===20,'20 bone noModel retained');
for(const [id,m]of Object.entries(before)){
 if(id==='levator_ani'){for(const key of Object.keys(m).filter(k=>k!=='note'))check(JSON.stringify(m[key])===JSON.stringify(A.muscles[id][key]),'old field retained '+key);}
 else check(JSON.stringify(m)===JSON.stringify(A.muscles[id]),'old card retained '+id);
}
check(Object.values(A.muscles).filter(m=>m.noModel).length===13,'Original 13 whole muscle blockers preserved');
check(Object.values(A.muscles).flatMap(m=>Object.values(m.parts||{})).filter(p=>p.noModel).length===21,'21 part blockers preserved');
const provenance=JSON.parse(await fs.readFile('site/models/bodyparts3d-3.0/muscles-stage7/provenance.json'));
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const models=[];
for(const row of provenance){
 const card=A.muscles[row.id],bytes=await fs.readFile(row.derivedFile);check(hash(bytes)===row.sha256,'Derivative hash');
 check(A.supplementalMuscles.leg.includes(row.id),'Registered for lazy loading');check(!card.noModel&&card.modelStatus==='educational_limited','Limited admission explicit');
 check(card.refs.length>=3&&card.fieldRefs.o.length>=2,'Field-specific sources');check(card.relatedMuscles.every(id=>A.muscles[id]),'Related muscle IDs exist');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');let mesh;gltf.scene.traverse(m=>{if(m.isMesh)mesh=m;});gltf.scene.updateMatrixWorld(true);
 check(mesh.name===`m|${row.id}|`,'Stable owner');const g=mesh.geometry;check(g.index.count===row.triangles*3,'All triangles present');
 g.computeBoundingBox();check((g.boundingBox.min.x+g.boundingBox.max.x)*(card.side==='right'?-1:1)>0,'Side');
 const p=g.attributes.position,n=g.attributes.normal;check([...p.array,...n.array].every(Number.isFinite),'Finite coordinates/normals');
 check(Array.from({length:n.count},(_,i)=>new Vector3().fromBufferAttribute(n,i).length()).every(l=>Math.abs(l-1)<1e-5),'Unit normals');
 const idx=hash(Buffer.from(g.index.array.buffer));g.boundsTree=new MeshBVH(g,{indirect:true,verbose:false});check(hash(Buffer.from(g.index.array.buffer))===idx,'BVH leaves indices unchanged');
 mesh.material.side=DoubleSide;const native=mesh.raycast,center=g.boundingBox.getCenter(new Vector3());let hits=0;
 for(const d of [new Vector3(1,0,0),new Vector3(0,1,0),new Vector3(0,0,1),new Vector3(1,1,1).normalize()]){
  const ray=new Raycaster(center.clone().addScaledVector(d,.2),d.clone().negate());const a=[],b=[];native.call(mesh,ray,a);acceleratedRaycast.call(mesh,ray,b);
  a.sort((x,y)=>x.distance-y.distance);b.sort((x,y)=>x.distance-y.distance);check(a.length===b.length,'Ray hit count equivalence');if(a.length){hits++;check(Math.abs(a[0].distance-b[0].distance)<1e-8&&a[0].faceIndex===b[0].faceIndex,'Ray faceIndex/distance equivalence');}
 }
 check(hits>0,'Real ray intersections');models.push({id:row.id,triangles:row.triangles,hits});
}
const original=JSON.parse(await fs.readFile(run+'/muscle-inventory-before.json'));
for(const [file,h]of Object.entries(original.hashes))check(hash(await fs.readFile(file))===h,'Original unchanged '+file);
await fs.writeFile(run+'/node-integration.json',JSON.stringify({status:'passed',checks,models},null,2),{flag:'wx'});console.log(JSON.stringify({status:'passed',checks,models}));
