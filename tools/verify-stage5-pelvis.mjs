import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds,contributingBoneIds} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')),idx=indexLandmarks(A.pins);
const oldIds=new Set(before.pins.map(p=>p.id)),target=new Set(['hip_bone','hip_bone_left','sacrum']);
const own=A.pins.filter(p=>oldIds.has(p.id)&&target.has(p.b)&&p.t==='ta'&&!p.relations),added=A.pins.filter(p=>!oldIds.has(p.id));
assert.equal(own.length,114);assert.equal(added.length,26);assert.equal(A.pins.length,2065);
for(const p of before.pins){
 const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['id','b','c','ru','lat','p','n','m','inc','loc','anchors','relations','secondaryMarkers'])assert.deepEqual(q[k],p[k],p.id+':'+k);
 if(!own.some(r=>r.id===p.id))assert.deepEqual(q,p,p.id);
}
assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(Object.keys(A.bones),Object.keys(before.bones));
for(const [id,card]of Object.entries(before.bones)){
 if(!target.has(id))assert.deepEqual(A.bones[id],card,id);
 else for(const k of Object.keys(card))if(!['ru','x','refs','side'].includes(k))assert.deepEqual(A.bones[id][k],card[k],id+':'+k);
}
for(const p of [...own,...added]){
 assert.ok(['point','line','area','space','volume'].includes(p.geometryKind),p.id);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 assert.ok(p.geometryRequirements.neededEvidence&&p.geometryKindReason);
 assert.ok(new Set(p.refs.filter(r=>r.authorGroup).map(r=>r.authorGroup)).size>=2,p.id);
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],id);
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.partOf);
}
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.equal(p.t,'additional');}
const shared=added.filter(p=>p.relations);assert.equal(shared.length,9);let edges=0;
for(const p of shared)for(const bone of relatedBoneIds(p)){
 assert.ok(A.bones[bone]);assert.equal(idx.byBone[bone].filter(q=>q.id===p.id).length,1);assert.equal(idx.byBone[bone].find(q=>q.id===p.id),p);edges++;
}
assert.equal(edges,22);
assert.ok(!contributingBoneIds(idx.byId.shared_pelvis_pelvic_outlet).includes('sacrum'));
assert.ok(idx.byId.shared_pelvis_pelvic_outlet.relatedLandmarks.includes('coc_os_coccygis'));
assert.equal(idx.byId.extra_sacrum_sacrococcygeal_joint.entityKind,'joint');
assert.ok(!idx.byId.extra_sacrum_sacrococcygeal_joint.relations,'No invented coccyx owner');
assert.ok(idx.byId.sac_basis.x.includes('не ограничивается'));
assert.ok(idx.byId.coc_os_coccygis.x.includes('Сращение всех сегментов не обязательно'));
assert.ok(!idx.byId.cox_acetabulum.x.includes('тела трёх костей'));
assert.equal(A.bones.hip_bone.ru,'Правая тазовая кость');
for(const p of own.filter(p=>p.b==='hip_bone_left'))assert.equal(p.p,null);
for(const id of ['cox_tuberculum_obturatorium_posterius','context_hip_bone_left_A02_5_01_312'])assert.equal(idx.byId[id].applicability,'variant_presence_unverified');
const protectedBefore=JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'));
const allowed=new Set(['scripts/make_pins_leg.py','scripts/make_context_bone_data.py','scripts/make_shared_landmarks.py','site/data-context-bones.js','site/pins-leg.js','site/pins-context-bones.js','site/pins-shared.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);let protectedFiles=0;
for(const[f,h]of Object.entries(protectedBefore))if(!allowed.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
const summary={status:'passed',boneOwners:3,anatomicalBones:4,originalTerms:114,unchangedAttachments:6,types:Object.fromEntries(['point','line','area','space','volume'].map(k=>[k,own.filter(p=>p.geometryKind===k).length])),newOwn:17,newShared:9,sharedEdges:edges,globalPins:A.pins.length,globalNoCoordinates:A.pins.filter(p=>!p.p).length,reviewedBoneRecords:140,regionalNoCoordinates:[...own,...added].filter(p=>!p.p).length,acceptedCoordinates:0,protectedFiles,unchangedOtherPins:before.pins.length-114};
const suffix=process.argv.includes('--ui-final')?'-ui-final':process.argv.includes('--final')?'-final':'';
const write=(n,d)=>fs.writeFile(out+'/'+n.replace('.json',suffix+'.json'),JSON.stringify(d,null,2)+'\n',{flag:'wx'});
await write('data-regression.json',summary);
await write('reviewed-records.json',[...own,...added].map(p=>({id:p.id,bone:p.b,c:p.c||p.educationCode||null,ru:p.ru,kind:p.geometryKind,definition:p.geometryKindReason,hasPoint:!!p.p,side:p.side||null,multiplicity:p.anatomicalMultiplicity||'single',bones:relatedBoneIds(p),entityKind:p.entityKind||'bone_landmark',refs:p.refs,needed:p.geometryRequirements.neededEvidence,status:'representation_reviewed_geometry_unverified'})));
console.log(JSON.stringify(summary));
