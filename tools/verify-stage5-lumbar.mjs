import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')),idx=indexLandmarks(A.pins);
const own=A.pins.filter(p=>p.b.startsWith('lumbar_')&&p.id.startsWith('context_'));
assert.equal(own.length,90);assert.equal(A.pins.length,before.pins.length+22);
for(const p of before.pins){
 const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['id','b','c','ru','lat','p','n','m','inc','loc','anchors','relations','secondaryMarkers'])assert.deepEqual(q[k],p[k],p.id+':'+k);
 if(!p.b.startsWith('lumbar_'))assert.deepEqual(q,p,p.id);
}
assert.deepEqual(A.muscles,before.muscles);
for(const [b,card] of Object.entries(before.bones)){
 if(!b.startsWith('lumbar_'))assert.deepEqual(A.bones[b],card,b);
 else {for(const k of Object.keys(card))if(k!=='refs'&&(b!=='lumbar_5'||k!=='x'))assert.deepEqual(A.bones[b][k],card[k],b+':'+k);assert.ok(A.bones[b].refs.every(r=>!r.locator.includes('Cervical Vertebrae')));}
}
assert.ok(A.lumbarWholeTerms.every(t=>t.refs.every(r=>!r.locator.includes('Cervical Vertebrae'))));
for(const p of own){
 assert.ok(['volume','area','space'].includes(p.geometryKind));assert.equal(p.p,null);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 assert.ok(p.modelNote.includes(p.geometryRequirements.neededEvidence));
 assert.ok(p.refs.every(r=>!r.locator.includes('Cervical Vertebrae')));
}
const added=A.pins.filter(p=>!before.pins.some(q=>q.id===p.id)),shared=added.filter(p=>p.relations);
assert.equal(shared.length,12);assert.equal(added.filter(p=>p.t==='additional').length,10);
let edges=0;
for(const p of [...own,...added]){
 assert.ok(!p.p&&!p.n);for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],'Unresolved '+id);
 if(p.partOf)assert.ok(idx.byId[p.partOf]);
}
for(const p of shared){
 assert.equal(p.geometryKind,'space');assert.equal(p.catalogueBones.length,0);
 assert.equal(new Set(p.refs.map(r=>r.authorGroup)).size,p.refs.length);
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b]);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);edges++;}
 assert.equal(p.relations.length,2);assert.ok(!p.relatedLandmarks.includes('sac_foramina_intervertebralia'));
}
assert.equal(edges,24);
const levels=['t12_l1','l1_l2','l2_l3','l3_l4','l4_l5','l5_s1'];
for(const level of levels)for(const side of ['right','left'])assert.ok(idx.byId[`shared_lumbar_intervertebral_${level}_${side}`]);
const hashBefore=JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'));
const allowed=new Set(['scripts/lumbar_terms.py','scripts/make_context_bone_data.py','scripts/make_shared_landmarks.py','site/data-context-bones.js','site/pins-context-bones.js','site/pins-shared.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);let protectedFiles=0;
for(const [f,h]of Object.entries(hashBefore))if(!allowed.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
const remaining=A.pins.filter(p=>['hip_bone','hip_bone_left','sacrum'].includes(p.b));assert.equal(remaining.length,120);
const summary={status:'passed',originalReviewed:90,bonesReviewed:5,kinds:Object.fromEntries(['volume','area','space'].map(k=>[k,own.filter(p=>p.geometryKind===k).length])),newCards:22,newPars:10,newShared:12,newRelations:edges,unchangedOtherPins:before.pins.length-90,protectedFiles,globalPins:A.pins.length,globalUnlocated:A.pins.filter(p=>!p.p).length,anatomicallyAcceptedCoordinates:0,pelvicOriginalRemainder:120};
const suffix=process.argv.includes('--final')?'-final':'';
const write=(file,data)=>fs.writeFile(out+'/'+file.replace('.json',suffix+'.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
await write('data-regression.json',summary);
await write('lumbar-reviewed-records.json',[...own,...added].map(p=>({id:p.id,bone:p.b,ru:p.ru,code:p.c||null,kind:p.geometryKind,point:!!p.p,bones:relatedBoneIds(p),needed:p.geometryRequirements.neededEvidence,geometryIssue:'GEO-LUMBAR-LANDMARKS'})));
await write('pelvic-remainder.json',remaining.map(p=>({id:p.id,bone:p.b,code:p.c||null,name:p.ru,hasPoint:!!p.p,type:p.geometryKind||'unknown',status:'not_reviewed_in_lumbar_batch',issue:'CAT-PELVIS-REVIEW'})));
console.log(JSON.stringify(summary));
