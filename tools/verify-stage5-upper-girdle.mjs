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
const A=JSON.parse(JSON.stringify(box.window.ATLAS)), before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')), idx=indexLandmarks(A.pins);
const old=new Map(before.pins.map(p=>[p.id,p])), added=A.pins.filter(p=>!old.has(p.id)), changed=[];
assert.equal(A.pins.length,2077);assert.equal(added.length,4);
for(const p of before.pins){
 const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['id','b','c','t','ru','lat','p','n','m','inc','loc','secondaryMarkers'])assert.deepEqual(q[k],p[k],p.id+':'+k);
 if(JSON.stringify(p)!==JSON.stringify(q)){assert.ok(q.upperGirdleReview,p.id);changed.push(q);}
}
assert.equal(changed.length,64);assert.deepEqual(A.bones,before.bones);assert.deepEqual(A.muscles,before.muscles);
const types={};
for(const p of [...changed,...added]){
 assert.ok(['point','line','area','space','volume'].includes(p.geometryKind),p.id);
 assert.ok(new Set(p.refs.map(r=>new URL(r.url).host)).size>=2,p.id);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],id);
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.partOf);
 if(old.has(p.id))types[p.geometryKind]=(types[p.geometryKind]||0)+1;
}
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);}
for(const suffix of ['', '_left']){
 const p=idx.byId['extra_clavicle'+suffix+'_acromioclavicular_joint'];
 assert.deepEqual(relatedBoneIds(p),['clavicle'+suffix,'scapula'+suffix]);
 for(const bone of relatedBoneIds(p))assert.equal(idx.byBone[bone].filter(q=>q.id===p.id).length,1);
 assert.equal(p.anatomicalEntity,'joint');assert.equal(p.educationCode,'A03.5.03.001');
 assert.deepEqual(relatedBoneIds(idx.byId['extra_scapula'+suffix+'_spinoglenoid_notch']),['scapula'+suffix]);
}
const allowed=new Set(['scripts/make_pins.py','scripts/make_context_bone_data.py','site/pins.js','site/pins-context-bones.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
const hashes=JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'));let protectedFiles=0;
for(const [file,hash] of Object.entries(hashes))if(!allowed.has(file)){assert.equal(createHash('sha256').update(await fs.readFile(file)).digest('hex'),hash,file);protectedFiles++;}
const armGroups=new Set(A.boneGroups.filter(g=>g.sec==='arm').map(g=>g.id)), armBones=new Set(Object.entries(A.bones).filter(([id,b])=>armGroups.has(b.g)).map(([id])=>id));
const remainder=A.pins.filter(p=>armBones.has(p.b)&&!p.upperGirdleReview);
const result={status:'passed',pins:A.pins.length,withoutPosition:A.pins.filter(p=>!p.p).length,types,changedIds:changed.map(p=>p.id),addedIds:added.map(p=>p.id),unchangedPins:before.pins.length-changed.length,protectedFiles,remainingRecords:remainder.length,newCoordinates:0,newSharedInstances:2,newSharedMemberships:4};
await fs.writeFile(out+'/data-regression'+suffix+'.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
await fs.writeFile(out+'/reviewed-records'+suffix+'.json',JSON.stringify([...changed,...added],null,2)+'\n',{flag:'wx'});
await fs.writeFile(out+'/remaining-records'+suffix+'.json',JSON.stringify(remainder,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,changedIds:changed.length,addedIds:added.length}));
