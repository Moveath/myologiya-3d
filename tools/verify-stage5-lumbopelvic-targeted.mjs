import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const tag=process.argv[3]||'';assert.ok(!tag||/^[a-z0-9-]+$/.test(tag));const suffix=tag?'-'+tag:'';
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')),idx=indexLandmarks(A.pins);
const old=new Map(before.pins.map(p=>[p.id,p])),changed=[],added=A.pins.filter(p=>!old.has(p.id));
assert.equal(added.length,8);assert.equal(A.pins.length,2073);
for(const p of before.pins){
 const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['id','b','c','t','ru','lat','p','n','m','inc','loc','secondaryMarkers'])assert.deepEqual(q[k],p[k],p.id+':'+k);
 if(JSON.stringify(p)!==JSON.stringify(q)){
  assert.ok(q.targetedReview,p.id);assert.equal(q.targetedReview.specimenPresenceAccepted,false);changed.push(q);
 }
}
assert.equal(changed.length,23);assert.deepEqual(A.bones,before.bones);assert.deepEqual(A.muscles,before.muscles);
for(const p of [...changed,...added]){
 assert.ok(new Set(p.refs.filter(r=>r.authorGroup).map(r=>r.authorGroup)).size>=2,p.id);
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],p.id+' -> '+id);
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.partOf);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
}
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.equal(p.educationAvailable,false);}
for(const b of ['hip_bone','hip_bone_left']){
 const p=idx.byId['extra_'+b+'_greater_sciatic_foramen'];assert.deepEqual(relatedBoneIds(p),[b,'sacrum']);
 for(const bone of [b,'sacrum'])assert.equal(idx.byBone[bone].filter(q=>q.id===p.id).length,1);
 assert.equal(idx.byId['extra_'+b+'_preauricular_sulcus'].applicability,'variant_presence_unverified');
}
for(const id of ['cox_tuberculum_obturatorium_posterius','context_hip_bone_left_A02_5_01_312']){
 const p=idx.byId[id];assert.equal(p.partOf,'extra_'+p.b+'_ischium');assert.equal(p.nomenclatureGroup,'A02.5.01.301');
}
const allowed=new Set(['scripts/pelvis_stage5_review.py','scripts/lumbar_stage5_review.py','site/pins-leg.js','site/pins-context-bones.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
const hashes=JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'));let protectedFiles=0;
for(const [file,sha] of Object.entries(hashes))if(!allowed.has(file)){assert.equal(createHash('sha256').update(await fs.readFile(file)).digest('hex'),sha,file);protectedFiles++;}
const result={status:'passed',pins:A.pins.length,withoutPosition:A.pins.filter(p=>!p.p).length,addedIds:added.map(p=>p.id),changedIds:changed.map(p=>p.id),unchangedPins:before.pins.length-changed.length,sharedInstancesExtended:2,newBoneMemberships:2,protectedFiles,newCoordinates:0};
const nop=A.pins.filter(p=>!p.p);result.withoutPositionGroups={original:nop.filter(p=>p.t!=='additional'&&!p.relations).length,shared:nop.filter(p=>p.relations).length,additionalOwn:nop.filter(p=>p.t==='additional'&&!p.relations).length};
assert.deepEqual(result.withoutPositionGroups,{original:447,shared:151,additionalOwn:149});
await fs.writeFile(out+'/data-regression'+suffix+'.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
await fs.writeFile(out+'/targeted-records'+suffix+'.json',JSON.stringify([...changed,...added],null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,addedIds:added.length,changedIds:changed.length}));
