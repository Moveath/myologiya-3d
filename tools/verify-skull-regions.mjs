import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import crypto from 'node:crypto';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
import {AnatomicalRegions,regionGeometry,regionBindingDigest,admissionValid} from '../site/atlas-regions.js';
const out=path.resolve(process.argv[2]);
const resultName=process.argv[3]||'node-regions-final.json';if(path.basename(resultName)!==resultName)throw Error('Invalid result filename');
const checks=[];const check=(ok,name)=>{assert.ok(ok,name);checks.push(name);};
globalThis.ProgressEvent??=class {constructor(type,init){Object.assign(this,init);}};
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const manifest=JSON.parse(await fs.readFile('site/skull-region-masks.json','utf8'));
const box={window:{}};vm.createContext(box);
try {
 for(const f of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+f+'.js','utf8'),box);
} catch(e) {throw Error('Catalogue loading: '+e.message);}
const atlas=box.window.ATLAS;
check(Object.values(atlas.bones).filter(b=>b.noModel).length===20,'20 noModel unchanged');
check(new Set(atlas.pins.map(p=>p.id)).size===atlas.pins.length,'Unique pin IDs');
for(const r of manifest.regions)check(r.pinIds.every(id=>atlas.pins.some(p=>p.id===id&&p.b===r.bone)),r.id+' existing IDs');
for(const file of ['head-glb.txt','head-q-glb.txt']) {
 const bytes=Buffer.from(await fs.readFile('site/'+file,'utf8'),'base64');
 const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 gltf.scene.updateMatrixWorld(true);const structs=new Map();
 gltf.scene.traverse(m=>{if(!m.isMesh)return;let p=m;while(p&&!p.name.startsWith('b|'))p=p.parent;const id=p?.name.split('|')[1];if(!manifest.regions.some(r=>r.bone===id))return;
  const entry=structs.get(id)||{meshes:[]};entry.meshes.push(m);structs.set(id,entry);
 });
 const fingerprints=()=>[...structs.values()].flatMap(s=>s.meshes).map(m=>sha(Buffer.concat([Buffer.from(m.geometry.attributes.position.array.buffer),Buffer.from(m.geometry.index.array.buffer)])));
 const before=fingerprints(),live=new AnatomicalRegions(manifest,THREE);
 const accepted=manifest.regions.filter(r=>r.admission.level!=='draft');
 const drafts=manifest.regions.filter(r=>r.admission.level==='draft');
 await live.prepare(structs,sha(bytes));check(live.items.size===accepted.length&&live.failures.size===drafts.length,'Only admitted geometry enabled in product');
 for(const r of drafts){live.update(r.pinIds[0]);check([...live.items.values()].every(x=>!x.overlay.visible),'Draft cannot activate '+r.id);}
 for(const side of ['right','left','both']) {
  live.update('head_sphenoid_A02_1_05_036',true,side);
  const shown=[...live.items.values()].filter(x=>x.overlay.visible);
  check(shown.length===(side==='both'?2:1)&&shown.every(x=>side==='both'||x.def.side===side),'Paired regions within unpaired bone: '+side);
 }
 check(live.info('head_sphenoid_A02_1_05_036').notice===accepted.find(r=>r.pinIds.includes('head_sphenoid_A02_1_05_036')).notice,'Paired limitation shown once');
 // Exercise the surface renderer with explicitly synthetic admission in a test fixture.
 // This does NOT approve or change the production anatomical manifest.
 const fixture=structuredClone(manifest);for(const r of fixture.regions){r.admission={level:'confirmed',explicit:true,scope:'synthetic-test-only',reviewId:'synthetic-fixture',bindingHash:await regionBindingDigest(r)};}
 const regions=new AnatomicalRegions(fixture,THREE);
 await regions.prepare(structs,sha(bytes));check(regions.items.size===manifest.regions.length,file+' all masks match');
 const meshes=[...structs.values()].flatMap(s=>s.meshes);
 for(const m of meshes){m.geometry.boundsTree=new MeshBVH(m.geometry,{indirect:true});m.raycast=acceleratedRaycast;}
 for(const r of manifest.regions) {
  regions.update(r.pinIds[0]);check([...regions.items.values()].filter(x=>x.overlay.visible).length===regions.definitions(r.pinIds[0]).length,file+' exclusive selection '+r.id);
  const item=regions.items.get(r.id);check(item.overlay.geometry.attributes.position.count>0,'Nonempty overlay '+r.id);
  const ray=new THREE.Raycaster(),g=item.mesh.geometry;
  const tri=new THREE.Triangle(...[0,1,2].map(i=>new THREE.Vector3().fromBufferAttribute(g.attributes.position,g.index.getX(i)).applyMatrix4(item.mesh.matrixWorld)));
  const center=tri.getMidpoint(new THREE.Vector3()),normal=tri.getNormal(new THREE.Vector3());
  ray.set(center.clone().addScaledVector(normal,.05),normal.clone().negate());
  const hits=ray.intersectObjects(meshes,false);const recursive=ray.intersectObjects(meshes,true);
  check(hits.length>0&&hits.length===recursive.length,'Overlays never add ray hits '+r.id);
  const fast=hits.map(h=>[h.faceIndex,h.distance]);meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);
  const slow=ray.intersectObjects(meshes,false).map(h=>[h.faceIndex,h.distance]);meshes.forEach(m=>m.raycast=acceleratedRaycast);
  assert.deepEqual(fast,slow);checks.push('BVH original faces '+r.id);
  item.mesh.material.opacity=.28;item.mesh.material.transparent=true;regions.update(r.pinIds[0]);check(item.overlay.material.opacity===.28,'Transparency '+r.id);
  item.mesh.visible=false;regions.update(r.pinIds[0]);check(!item.overlay.visible,'Hidden owner '+r.id);item.mesh.visible=true;
 }
 regions.update('head_occipital_A02_1_04_014');check([...regions.items.values()].every(x=>!x.overlay.visible),'Unmapped landmark clears overlay');
 regions.update(manifest.regions[0].pinIds[0],false);check([...regions.items.values()].every(x=>!x.overlay.visible),'Toggle off clears overlay');
 const mismatched=new AnatomicalRegions(manifest,THREE);await mismatched.prepare(structs,'wrong');check(mismatched.items.size===0&&mismatched.failures.size===manifest.regions.length,'Source mismatch fails closed');
 const sharedManifest={regions:fixture.regions.filter(r=>r.id.endsWith('A02.1.06.047')).map(r=>({...r,pinIds:['test-shared']}))};
 for(const r of sharedManifest.regions)r.admission={...r.admission,bindingHash:await regionBindingDigest(r)};
 const shared=new AnatomicalRegions(sharedManifest,THREE);await shared.prepare(structs,sha(bytes));shared.update('test-shared');check([...shared.items.values()].filter(x=>x.overlay.visible).length===2,'Shared multi-bone region');
 shared.items.delete(sharedManifest.regions[0].id);shared.update('test-shared');check([...shared.items.values()].every(x=>!x.overlay.visible),'Incomplete shared mask fails closed');
 assert.deepEqual(fingerprints(),before);checks.push(file+' source buffers unchanged');
 assert.throws(()=>regionGeometry(THREE,meshes[0].geometry,{faces:[-1]}));checks.push('Invalid annotation rejected');
}
// Geometry, owner and ID changes invalidate the explicit admission; a status string is insufficient.
const approved=manifest.regions.find(r=>r.admission.level==='educational');
check(await admissionValid(approved),'Explicit educational admission');
for(const mutate of [r=>delete r.admission,r=>r.admission.level='unknown',r=>r.admission.explicit=false,r=>r.pinIds.push('wrong'),r=>r.bone='wrong',r=>r.variants[0].edges[0].reverse(),r=>r.admission.bindingHash='wrong']) {
 const r=structuredClone(approved);mutate(r);check(!await admissionValid(r),'Unreviewed/tampered binding rejected');
}
const baseline=JSON.parse(await fs.readFile(path.join(out,'baseline.json'),'utf8'));
for(const [file,hash] of Object.entries(baseline).filter(([f])=>f!=='site/index.html'))check(sha(await fs.readFile(file))===hash,file+' unchanged');
await fs.writeFile(path.join(out,resultName),JSON.stringify({passed:checks.length,checks},null,2),{flag:'wx'});
console.log(JSON.stringify({passed:checks.length}));
