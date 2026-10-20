// Targeted preservation/coverage test against the snapshot preceding batch 2.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
import {createEvidenceRun} from './evidence-run.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const baseline='research/evidence-runs/stage5-neck-batch2-2026-10-17T09-34-16-669Z-UI5Ivn';
const read=async p=>JSON.parse(await fs.readFile(path.join(root,p),'utf8'));
const before=await read(baseline+'/atlas-before.json');
const queue=await read('research/stage5-neck-2026-10-17/geometry-queue.json');
const reviewed=new Set([...queue.unlocatedOriginal,...queue.newUnlocated]);assert.equal(reviewed.size,52);
const scripts=['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'];
const box={window:{}};vm.createContext(box);
for(const f of scripts)vm.runInContext(await fs.readFile(path.join(root,'site',f+'.js'),'utf8'),box);
const now=JSON.parse(JSON.stringify(box.window.ATLAS)),idx=indexLandmarks(now.pins);
assert.equal(new Set(now.pins.map(p=>p.id)).size,now.pins.length);
assert.deepEqual(now.bones,before.bones);assert.deepEqual(now.muscles,before.muscles);
let changed=0,links=0;
for(const old of before.pins){
 const p=idx.byId[old.id];assert.ok(p,'Lost '+old.id);
 for(const key of ['id','b','c','ru','lat','p','n','loc','secondaryMarkers','refs','geometryKind','relations','inc','concept'])assert.deepEqual(p[key],old[key],old.id+': '+key);
 if(!reviewed.has(old.id))assert.deepEqual(p,old);
 else {
  assert.ok(!p.p);assert.equal(p.geometryRequirements.coordinateReuse,false);
  assert.ok(p.modelNote.includes(p.geometryRequirements.neededEvidence));
  assert.ok(p.modelNote.startsWith(old.modelNote));
  const stripped={...p};for(const k of ['modelNote','relatedLandmarks','geometryRequirements']){if(k in old)stripped[k]=old[k];else delete stripped[k];}
  assert.deepEqual(stripped,old);changed++;
  links+=(p.relatedLandmarks||[]).filter(id=>!old.relatedLandmarks?.includes(id)).length;
 }
}
const oldIds=new Set(before.pins.map(p=>p.id));const added=now.pins.filter(p=>!oldIds.has(p.id));
assert.deepEqual(added.map(p=>p.id).sort(),['extra_axis_dens_neck','extra_hyoid_body_border_inferior','extra_hyoid_body_border_superior']);
for(const p of added){
 assert.ok(!Object.hasOwn(p,'p')&&!Object.hasOwn(p,'n'));assert.equal(p.lat,'');assert.ok(!p.c);
 assert.ok(new Set(p.refs.map(r=>r.authorGroup)).size>=2);assert.ok(p.refs.every(r=>r.url&&r.locator));
 assert.equal(p.geometryRequirements.coordinateReuse,false);assert.ok(idx.byId[p.partOf]);
}
const neck=now.pins.filter(p=>p.id.startsWith('neck_')||reviewed.has(p.id)||added.includes(p));
assert.equal(neck.length,155);assert.equal(neck.filter(p=>!p.p).length,55);
for(const p of neck){for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],p.id+' bad related '+id);}
for(let n=2;n<=6;n++)for(const side of ['right','left']){
 const id=`shared_neck_intervertebral_c${n}_c${n+1}_${side}`,p=idx.byId[id];
 const upper=n===2?'axis':`cervical_${n}`,lower=`cervical_${n+1}`;
 assert.deepEqual(relatedBoneIds(p),[upper,lower]);assert.equal(p.side,side);
 assert.deepEqual(p.relatedLandmarks,[`neck_${upper}_A02_2_01_010`,`neck_${lower}_A02_2_01_009`]);
 for(const b of [upper,lower]){assert.equal(idx.byBone[b].filter(q=>q.id===id).length,1);assert.equal(idx.byBone[b].find(q=>q.id===id),p);}
}
const markers=await read('pins_neck/ta.json');const coords=new Set(markers.map(p=>'neck_'+p.bone+'_'+p.code.replaceAll('.','_')));
assert.equal(coords.size,100);for(const id of queue.unlocatedOriginal)assert.ok(!coords.has(id));
const hashes=await read(baseline+'/hashes-before.json');
const mutable=new Set(['scripts/make_pins_neck.py','scripts/neck_stage5_review.py','tools/verify-stage5-neck.mjs','site/pins-neck.js','site/pins-shared.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
let protectedFiles=0;for(const [p,h]of Object.entries(hashes))if(!mutable.has(p)){
 assert.equal(createHash('sha256').update(await fs.readFile(path.join(root,p))).digest('hex'),h,p);protectedFiles++;
}
const records=neck.filter(p=>!p.p).map(p=>({id:p.id,bone:p.b,name:p.ru,kind:p.geometryKind,sourceGroup:queue.unlocatedOriginal.includes(p.id)?'original38':queue.newUnlocated.includes(p.id)?'previous14':'new3',
  side:p.side||p.anatomicalMultiplicity||'single',bones:relatedBoneIds(p),related:p.relatedLandmarks||[],
  partOf:p.partOf||null,requirements:p.geometryRequirements,refs:p.refs,
  coordinateFound:false,coordinateReuseAccepted:false,extentAccepted:false}));
const result={status:'passed',reviewedOriginalUnlocated:38,reviewedPreviousAdditions:14,changedPrevious:changed,newCards:added.length,
  newRelatedEdges:links,newParentLinks:3,neckLandmarks:neck.length,unlocated:records.length,globalPins:now.pins.length,
  preservedPreviousPins:before.pins.length,unchangedOtherPins:before.pins.length-changed,protectedFiles,
  acceptedCoordinates:0,acceptedExtents:0,records};
const run=await createEvidenceRun(root,'stage5-neck-batch2-data');await run.write('data-regression.json',result);
console.log(JSON.stringify({...result,records:undefined,evidence:run.dir}));
