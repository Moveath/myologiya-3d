import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const tag=process.argv[3]||'';assert.ok(!tag||/^[a-z0-9-]+$/.test(tag));const suffix=tag?'-'+tag:'';
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')),idx=indexLandmarks(A.pins);
const owners=new Set(['femur','patella','tibia','fibula']);
assert.equal(Object.keys(idx.byId).length,A.pins.length);
for(const p of before.pins){const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['b','c','p','n','m'])assert.deepEqual(q[k],p[k],p.id+'/'+k);
 if(!owners.has(p.b))assert.deepEqual(q,p,p.id);}
assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(A.contextBoneSources,before.contextBoneSources);
for(const [id,b] of Object.entries(before.bones))if(!owners.has(id))assert.deepEqual(A.bones[id],b,id);
const newBones=Object.keys(A.bones).filter(b=>!before.bones[b]);assert.deepEqual(new Set(newBones),new Set([...owners].map(b=>b+'_left')));
for(const b of newBones){assert.ok(A.bones[b].noModel);assert.equal(A.bones[b].side,'left');assert.ok(!A.bones[b].sourceId);}
const rows=A.pins.filter(p=>p.lowerProximalReview),old=rows.filter(p=>before.pins.some(q=>q.id===p.id)),added=rows.filter(p=>!before.pins.some(q=>q.id===p.id));
assert.equal(old.length,86);assert.equal(added.length,87);assert.equal(added.filter(p=>p.t==='ta').length,71);
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.deepEqual(p.m,[]);}
for(const p of rows){assert.ok(['point','line','area','space','volume'].includes(p.geometryKind));assert.ok(p.refs.length>=2);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b],b);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);}}
for(const suffix of ['', '_left']){
 assert.deepEqual(relatedBoneIds(idx.byId['extra_femur'+suffix+'_knee_joint']),['femur','tibia','patella'].map(b=>b+suffix));
 assert.deepEqual(relatedBoneIds(idx.byId['extra_tibia'+suffix+'_proximal_tibiofibular_joint']),['tibia','fibula'].map(b=>b+suffix));
 assert.equal(idx.byId['extra_tibia'+suffix+'_distal_tibiofibular_syndesmosis'].anatomicalEntity,'fibrous_joint');}
assert.equal(hasLandmarkPosition(idx.byId.fem_trochanter_tertius),false);assert.ok(idx.byId.fem_trochanter_tertius.p);
assert.ok(idx.byId.pat_facies_articularis.x.includes('несуставной'));assert.ok(idx.byId.tib_facies_articularis_superior.x.includes('частично'));
for(const [f,h] of Object.entries(JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'))))assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);
const types={};for(const p of old)types[p.geometryKind]=(types[p.geometryKind]||0)+1;
const joints=rows.filter(p=>p.relations),foot=Object.entries(A.bones).filter(([id,b])=>b.sub==='foot'&&!b.g.includes('soft')).map(([id,b])=>({id,ru:b.ru,pins:A.pins.filter(p=>p.b===id).map(p=>p.id)}));
const result={status:'passed',oldRecords:old.length,oldTypes:types,newBoneCards:newBones,addedLandmarks:added.length,totalAtlasPins:A.pins.length,withoutCoordinates:A.pins.filter(p=>!p.p).length,reviewedRecords:rows.length,joints:joints.length,sharedEdges:joints.reduce((n,p)=>n+relatedBoneIds(p).length,0),newCoordinates:0,anatomicallyAcceptedCoordinates:0,originalModelsUnchanged:true};
for(const [file,data] of [['data-regression',result],['reviewed-records',rows],['added-records',added],['foot-remainder',foot]])await fs.writeFile(path.join(out,file+suffix+'.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
