import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);
assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const tag=process.argv[3]||'';assert.ok(!tag||/^[a-z0-9-]+$/.test(tag));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')),idx=indexLandmarks(A.pins);
const inventory=JSON.parse(await fs.readFile(out+'/inventory-before.json','utf8')),owners=new Set(inventory.map(b=>b.id));
assert.equal(owners.size,27);assert.equal(Object.keys(idx.byId).length,A.pins.length);
for(const p of before.pins){const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['b','c','p','n','m'])assert.deepEqual(q[k],p[k],p.id+'/'+k);
 if(!owners.has(p.b))assert.deepEqual(q,p,p.id);}
assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(A.contextBoneSources,before.contextBoneSources);
for(const [id,b] of Object.entries(before.bones))if(!owners.has(id))assert.deepEqual(A.bones[id],b,id);
const addedBones=Object.keys(A.bones).filter(b=>!before.bones[b]);
assert.deepEqual(new Set(addedBones),new Set([...owners].map(b=>b+'_left')));
for(const b of addedBones){assert.ok(A.bones[b].noModel);assert.equal(A.bones[b].side,'left');assert.ok(!A.bones[b].sourceId);}
const rows=A.pins.filter(p=>p.footReview),old=rows.filter(p=>before.pins.some(q=>q.id===p.id)),added=rows.filter(p=>!before.pins.some(q=>q.id===p.id));
assert.equal(old.length,118);assert.equal(old.filter(p=>p.t==='ta').length,111);assert.equal(added.length,181);
assert.equal(added.filter(p=>p.t==='ta').length,111);
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.deepEqual(p.m,[]);}
for(const p of rows){assert.ok(['point','line','area','space','volume'].includes(p.geometryKind),p.id);
 assert.ok(p.refs.length>=2);assert.equal(p.footReview.coordinateAcceptance,false);assert.equal(p.footReview.extentAcceptance,false);
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b],b);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);}}
for(const s of ['','_left']){
 assert.deepEqual(relatedBoneIds(idx.byId['extra_talus'+s+'_ankle_joint']),['talus','tibia','fibula'].map(b=>b+s));
 assert.deepEqual(relatedBoneIds(idx.byId['extra_talus'+s+'_subtalar_joint']),['talus','calcaneus'].map(b=>b+s));
 assert.deepEqual(relatedBoneIds(idx.byId['extra_talus'+s+'_talocalcaneonavicular_joint']),['talus','calcaneus','navicular'].map(b=>b+s));
 assert.equal(A.pins.filter(p=>p.b==='sesamoid_pedis'+s&&p.anatomicalEntity==='bone').length,2);
 assert.deepEqual(relatedBoneIds(idx.byId['extra_metatarsal_2'+s+'_intermetatarsal_joint']),[2,3,4,5].map(i=>'metatarsal_'+i+s));
 const sinus=idx.byId[s?'context_calcaneus_left_A02_5_11_009':'cal_sinus_tarsi'];
 assert.deepEqual(relatedBoneIds(sinus),['calcaneus','talus'].map(b=>b+s));assert.equal(hasLandmarkPosition(sinus),false);
 assert.ok(!A.pins.some(p=>p.b==='toe_mid_1'+s));
}
assert.equal(hasLandmarkPosition(idx.byId.tal_os_trigonum),false);assert.ok(idx.byId.tal_os_trigonum.p);
assert.ok(idx.byId.mt2_basis.x.includes('непостоянна'));assert.ok(idx.byId.mt5_basis.x.includes('IV'));
const changedSite=new Set(['site/pins-leg.js','site/pins-context-bones.js','site/data-context-bones.js']);
for(const [file,hash] of Object.entries(JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8')))){
 const normalized=file.replaceAll('\\','/');if(changedSite.has(normalized))continue;
 assert.equal(createHash('sha256').update(await fs.readFile(file)).digest('hex'),hash,file);
}
const types={};for(const p of old)types[p.geometryKind]=(types[p.geometryKind]||0)+1;
const joints=rows.filter(p=>p.relations),result={status:'passed',originalCards:27,originalRecords:118,oldTypes:types,newBoneCards:addedBones.length,
 addedLandmarks:added.length,newSurfaceCards:added.filter(p=>p.t==='additional'&&p.geometryKind==='area').length,addedAreaRecords:added.filter(p=>p.geometryKind==='area').length,newSesamoidCards:added.filter(p=>p.anatomicalEntity==='bone').length,
 newJointCards:added.filter(p=>['joint','joint_group'].includes(p.anatomicalEntity)).length,
 reviewedRecords:rows.length,totalAtlasPins:A.pins.length,withoutCoordinates:A.pins.filter(p=>!p.p).length,
 sharedInstances:joints.length,sharedEdges:joints.reduce((n,p)=>n+relatedBoneIds(p).length,0),newCoordinates:0,acceptedCoordinates:0,
 originalModelsAndUIUnchanged:true,nonFootRecordsUnchanged:true};
for(const [name,data] of [['data-regression',result],['reviewed-records',rows],['added-records',added],['left-cards',addedBones.map(id=>({id,...A.bones[id]}))]])
 await fs.writeFile(path.join(out,name+(tag?'-'+tag:'')+'.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
