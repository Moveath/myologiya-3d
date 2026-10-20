// Addressed vertebral batch. Snapshot protects all other regions and original GLBs.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
import {createEvidenceRun} from './evidence-run.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const baseline='research/evidence-runs/stage5-thorax-2026-10-18T12-51-39-645Z-iyyF5G';
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),idx=indexLandmarks(A.pins);
const before=JSON.parse(await fs.readFile(path.join(root,baseline,'atlas-before.json'),'utf8'));
assert.equal(new Set(A.pins.map(p=>p.id)).size,A.pins.length);
assert.deepEqual(A.bones,before.bones);assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(A.thoraxWholeTerms,before.thoraxWholeTerms);
const own=A.pins.filter(p=>p.id.startsWith('thorax_thoracic_'));
assert.equal(own.length,212);
for(const old of before.pins){const p=idx.byId[old.id];assert.ok(p,old.id);
 if(!old.id.startsWith('thorax_thoracic_'))assert.deepEqual(p,old,old.id);
 else {
  for(const k of ['id','b','c','ru','lat','x','p','n','loc','secondaryMarkers','refs','inc','taParen','m'])assert.deepEqual(p[k],old[k],old.id+':'+k);
  assert.ok(['volume','area','space'].includes(p.geometryKind));assert.ok(p.geometryKindReason);
  assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
  assert.ok(p.modelNote.startsWith(old.modelNote));assert.ok(p.modelNote.includes(p.geometryRequirements.neededEvidence));
 }
}
const oldIds=new Set(before.pins.map(p=>p.id)),added=A.pins.filter(p=>!oldIds.has(p.id));
assert.equal(added.length,30);
for(const p of added){
 assert.ok(!Object.hasOwn(p,'p')&&!Object.hasOwn(p,'n'));assert.ok(new Set(p.refs.map(r=>r.authorGroup)).size>=2);
 assert.ok(p.refs.every(r=>r.url&&r.locator));assert.equal(p.geometryRequirements.coordinateReuse,false);
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b]);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);assert.equal(idx.byBone[b].find(q=>q.id===p.id),p);}
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id]);
}
for(let i=0;i<12;i++)for(const side of ['right','left']){
 const upper=i?`thoracic_${i}`:'cervical_7',lower=`thoracic_${i+1}`,key=i?`t${i}_t${i+1}`:'c7_t1';
 const p=idx.byId[`shared_thorax_intervertebral_${key}_${side}`];
 assert.deepEqual(relatedBoneIds(p),[upper,lower]);assert.equal(p.side,side);assert.equal(p.geometryKind,'space');
 assert.deepEqual(p.relatedLandmarks,[(i?'thorax_':'neck_')+upper+'_A02_2_01_010','thorax_'+lower+'_A02_2_01_009']);
}
for(const part of ['superior','inferior','lateral'])for(const side of ['right','left']){
 const p=idx.byId[`extra_thoracic_12_${part}_tubercle_${side}`];assert.equal(p.partOf,'thorax_thoracic_12_A02_2_01_013');
 assert.equal(p.lat,'');assert.ok(!p.c);assert.equal(p.side,side);assert.equal(p.geometryKind,'volume');
 assert.ok(idx.byId[p.partOf].relatedLandmarks.includes(p.id));
}
// Preserve atypical levels; a classification must not invent absent facets.
for(const n of [11,12])for(const c of ['003','004'])assert.ok(!idx.byId[`thorax_thoracic_${n}_A02_2_03_${c}`]);
assert.equal(idx.byId.thorax_thoracic_9_A02_2_03_003.inc,1);
assert.match(idx.byId.thorax_thoracic_10_A02_2_03_004.x,/если она выражена/);
const hashes=JSON.parse(await fs.readFile(path.join(root,baseline,'hashes-before.json'),'utf8'));
const html=await fs.readFile(path.join(root,'site/index.html'),'utf8');
const previousHtml=await fs.readFile(path.join(root,baseline,'before-index.html'),'utf8');
for(const [start,end] of [['const headCutPlane =','const headBoneGhosts ='],['function pointClipped(','function updateHeadCut()']]){
 const extract=s=>s.slice(s.indexOf(start),s.indexOf(end,s.indexOf(start)));
 assert.ok(extract(html).length>0);assert.equal(extract(html),extract(previousHtml),'Clipping code changed');
}
// The promoted context source nodes are actual identities in the two manifests,
// not a nearest-mesh guess. All other raw context stays anonymous/non-pickable.
const sourceNames=new Map((await fs.readFile(path.join(root,'bp/all_named.tsv'),'utf8')).trim().split(/\r?\n/).map(line=>line.split('\t')));
assert.equal(sourceNames.get('FMA9165'),'first thoracic vertebra');
assert.equal(sourceNames.get('FMA12525'),'seventh cervical vertebra');
const allowed=new Set(['scripts/make_pins_thorax.py','scripts/make_shared_landmarks.py','verify/verify_thorax_positions.py','tools/verify-thorax-data.mjs','site/pins-thorax.js','site/pins-shared.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
let protectedFiles=0;for(const [f,h]of Object.entries(hashes))if(!allowed.has(f)){
 assert.equal(createHash('sha256').update(await fs.readFile(path.join(root,f))).digest('hex'),h,f);protectedFiles++;
}
const rows=[...own,...added],remainder=A.pins.filter(p=>p.id.startsWith('thorax_')&&!p.id.startsWith('thorax_thoracic_'));
assert.equal(remainder.length,246);
const result={status:'passed',originalBonesInventoried:37,vertebraeReviewed:12,originalLandmarksReviewed:212,
 kinds:Object.fromEntries(['area','space','volume'].map(k=>[k,own.filter(p=>p.geometryKind===k).length])),newCards:30,newDetails:6,newSharedSpaces:24,newBoneRelations:48,
 reviewedLocated:own.filter(p=>p.p).length,reviewedUnlocated:rows.filter(p=>!p.p).length,
 originalUnlocated:own.filter(p=>!p.p).length,globalPins:A.pins.length,globalUnlocated:A.pins.filter(p=>!p.p).length,
 protectedFiles,unchangedOtherPins:before.pins.length-own.length,acceptedCoordinates:0,acceptedExtents:0,
 records:rows.map(p=>({id:p.id,bone:p.b,code:p.c||null,name:p.ru,kind:p.geometryKind,located:!!p.p,multiplicity:p.anatomicalMultiplicity||p.side||'single',
  bones:relatedBoneIds(p),related:p.relatedLandmarks||[],requirements:p.geometryRequirements,refs:p.refs})),
 remainingRecords:remainder.map(p=>({id:p.id,bone:p.b,name:p.ru,located:!!p.p,review:'next_rib_sternum_batch'}))};
const run=await createEvidenceRun(root,'stage5-thorax-data');await run.write('data-regression.json',result);
console.log(JSON.stringify({...result,records:undefined,remainingRecords:undefined,evidence:run.dir}));
