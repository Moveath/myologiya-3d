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
const A=JSON.parse(JSON.stringify(box.window.ATLAS)), before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')), idx=indexLandmarks(A.pins);
const old=new Map(before.pins.map(p=>[p.id,p])), added=A.pins.filter(p=>!old.has(p.id)), changed=[];
assert.equal(A.pins.length,2092);assert.equal(added.length,15);
for(const p of before.pins){
 const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['id','b','c','t','ru','lat','p','n','inc','loc','secondaryMarkers'])assert.deepEqual(q[k],p[k],p.id+':'+k);
 if(!['hum_crista_tuberculi_minoris','hum_sulcus_intertubercularis'].includes(p.id))assert.deepEqual(q.m,p.m,p.id+':m');
 if(JSON.stringify(p)!==JSON.stringify(q)){assert.ok(q.armForearmReview,p.id);changed.push(q);}
}
assert.equal(changed.length,95);assert.deepEqual(A.bones,before.bones);assert.deepEqual(A.muscles,before.muscles);
assert.deepEqual(idx.byId.hum_crista_tuberculi_minoris.m,old.get('hum_crista_tuberculi_minoris').m.filter(m=>m[0]!=='latissimus_dorsi'));
assert.deepEqual(idx.byId.hum_sulcus_intertubercularis.m,[...old.get('hum_sulcus_intertubercularis').m,['latissimus_dorsi','i']]);
assert.equal(hasLandmarkPosition(idx.byId.hum_processus_supracondylaris),false);
assert.equal(idx.byId.hum_processus_supracondylaris.specimenPresence,'unverified');
assert.ok(idx.byId.hum_corpus.x.includes('три края'));assert.ok(!idx.byId.rad_facies_articularis_carpalis.x.includes('через суставной диск —'));
const types={};let edges=0;
for(const p of [...changed,...added]){
 assert.ok(['point','line','area','space','volume'].includes(p.geometryKind),p.id);
 assert.ok(new Set(p.refs.map(r=>new URL(r.url).host)).size>=2,p.id);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],id);
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.partOf);
 if(old.has(p.id))types[p.geometryKind]=(types[p.geometryKind]||0)+1;
}
for(const p of added){
 assert.equal(p.p,null);assert.equal(p.n,null);
 for(const bone of relatedBoneIds(p)){assert.ok(A.bones[bone],bone);assert.equal(idx.byBone[bone].filter(q=>q.id===p.id).length,1);assert.equal(idx.byBone[bone].find(q=>q.id===p.id),p);}
 if(p.anatomicalEntity==='joint'){assert.equal(p.nomenclatureStatus,'TA98_term');assert.ok(p.lat);edges+=relatedBoneIds(p).length;}
}
assert.equal(added.filter(p=>p.anatomicalEntity==='joint').length,7);assert.equal(edges,15);
assert.deepEqual(relatedBoneIds(idx.byId.extra_radius_proximal_radioulnar_joint),['radius','ulna']);
assert.deepEqual(relatedBoneIds(idx.byId.extra_humerus_elbow_joint),['humerus','radius','ulna']);
assert.deepEqual(relatedBoneIds(idx.byId.extra_humerus_left_glenohumeral_joint),['humerus_left','scapula_left']);
const allowed=new Set(['scripts/make_pins.py','scripts/make_context_bone_data.py','site/pins.js','site/pins-context-bones.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
const hashes=JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'));let protectedFiles=0;
for(const [file,hash] of Object.entries(hashes))if(!allowed.has(file)){assert.equal(createHash('sha256').update(await fs.readFile(file)).digest('hex'),hash,file);protectedFiles++;}
const armGroups=new Set(A.boneGroups.filter(g=>g.sec==='arm').map(g=>g.id)), armBones=new Set(Object.entries(A.bones).filter(([id,b])=>armGroups.has(b.g)).map(([id])=>id));
const remainder=A.pins.filter(p=>armBones.has(p.b)&&!p.upperGirdleReview&&!p.armForearmReview);assert.equal(remainder.length,81);
const result={status:'passed',pins:A.pins.length,withoutPosition:A.pins.filter(p=>!p.p).length,types,changedIds:changed.map(p=>p.id),addedIds:added.map(p=>p.id),unchangedPins:before.pins.length-changed.length,protectedFiles,remainingRecords:remainder.length,newCoordinates:0,newSharedInstances:7,newSharedMemberships:edges};
for(const [file,value] of [['data-regression',result],['reviewed-records',[...changed,...added]],['remaining-records',remainder]])await fs.writeFile(out+'/'+file+suffix+'.json',JSON.stringify(value,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,changedIds:changed.length,addedIds:added.length}));
