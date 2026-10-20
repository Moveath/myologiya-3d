// Read saved browser evidence and current data; do not repeat anatomy or mesh checks.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
import {createEvidenceRun} from './evidence-run.mjs';
const first=process.argv[2],finish=process.argv[3];
const prior='research/evidence-runs/stage5-foot-2026-10-19T09-33-56-218Z-lia0LB';
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=await read(prior+'/atlas-before.json');
const rows=A.pins.filter(p=>p.footReview),idx=indexLandmarks(A.pins);
assert.deepEqual(rows,await read(prior+'/reviewed-records-final.json'));
assert.equal(Object.keys(idx.byId).length,A.pins.length);
const oldIDs=new Set(before.pins.map(p=>p.id)),added=rows.filter(p=>!oldIDs.has(p.id));
assert.equal(added.length,181);assert.equal(rows.length,299);
for(const p of before.pins){const q=idx.byId[p.id];assert.ok(q);for(const key of ['b','c','p','n','m'])assert.deepEqual(q[key],p[key]);if(!q.footReview)assert.deepEqual(q,p);}
assert.deepEqual(A.muscles,before.muscles);
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);}
for(const p of rows)for(const b of relatedBoneIds(p)){assert.ok(A.bones[b]);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);}
const left=await read(prior+'/left-cards-final.json');for(const b of left){assert.deepEqual({id:b.id,...A.bones[b.id]},b);assert.ok(b.noModel);}
const passed=[];
for(const [dir,limit] of [[first,19],[finish,9]])for(const item of (await read(dir+'/plan.json')).slice(0,limit)){
 const r=await read(dir+'/'+item.name+'.json');assert.equal(r.status,'passed',item.name);assert.deepEqual(r.errors,[]);passed.push({file:dir+'/'+item.name+'.json',...r});
}
const mobile=passed.filter(p=>p.width===390),desktop=passed.filter(p=>p.width===1280);
const cardIDs=rs=>rs.filter(p=>p.phase==='cards').flatMap(p=>p.ids);
const edgeIDs=rs=>rs.filter(p=>p.phase==='links').flatMap(p=>p.links.map(l=>l.id+'/'+l.bone));
assert.deepEqual(new Set(cardIDs(mobile)),new Set(rows.map(p=>p.id)));assert.equal(cardIDs(mobile).length,299);
assert.deepEqual(new Set(edgeIDs(mobile)),new Set(rows.filter(p=>p.relations).flatMap(p=>p.relations.map(r=>p.id+'/'+r.bone))));assert.equal(edgeIDs(mobile).length,126);
const earlier=await read(prior+'/reviewed-records-accepted.json'),delta=rows.filter(p=>!earlier.some(q=>q.id===p.id));
assert.deepEqual(new Set(cardIDs(desktop)),new Set(delta.map(p=>p.id)));assert.equal(cardIDs(desktop).length,6);assert.equal(edgeIDs(desktop).length,18);
for(const set of [mobile,desktop])assert.ok(set.some(p=>p.phase==='workflow')&&set.some(p=>p.phase==='finish'));
const remaining=await read(prior+'/remaining-evidence.json');
remaining['PIN-LOWER-FOOT'].records=rows.map(p=>({id:p.id,bone:p.b,type:p.geometryKind,hasLegacyCoordinate:!!p.p,needs:'independent anatomical localisation and specimen-specific extent annotation'}));
remaining.catalogue_granularity.covered='111 original TA terms plus 7 attachment record types; 54 owner cards (26 ordinary bones and grouped hallux sesamoids per side); 20 extra surface cards, four sesamoid constituent cards and 46 joint/group instances. 299 landmark records; no new coordinates.';
remaining['CO-001']={right:'cal_sinus_tarsi',left:'context_calcaneus_left_A02_5_11_009',needed:'Right specimen-specific independent localisation; left identified model. Right legacy marker remains hidden; left coordinate is null.'};
remaining['SHX-tarsal-canal-vs-sinus']={needed:'Resolve modern canal versus lateral sinus terminology and specimen extent independently; do not merge the two bony grooves or invent canal coordinates.'};
const run=await createEvidenceRun(process.cwd(),'stage5-foot-closure');
const result={status:'passed',footOwnerCards:54,rightModelOwners:27,leftNoModelCards:27,originalRecords:118,addedRecords:added.length,footRecords:rows.length,types:Object.fromEntries(['point','line','area','space','volume'].map(k=>[k,rows.filter(p=>p.geometryKind===k).length])),newJointCards:46,sharedInstances:48,sharedEdges:126,newCoordinates:0,acceptedCoordinates:0,acceptedMasks:0,atlasRecords:A.pins.length,atlasWithoutCoordinates:A.pins.filter(p=>!p.p).length,atlasOwnerCards:Object.keys(A.bones).length,mobile:{status:'passed',cards:cardIDs(mobile).length,edges:edgeIDs(mobile).length},desktop:{status:'passed',cards:cardIDs(desktop).length,edges:edgeIDs(desktop).length},dataMatchesPriorFinal:true,oldCoordinatesAndMuscleLinksUnchanged:true,uniqueIDs:true,passedPhases:passed.map(p=>p.file),preservedFailedAttempt:first+'/19-390-workflow.json'};
await run.write('consistency.json',result);await run.write('remaining-evidence.json',remaining);await run.write('desktop-delta.json',delta);
await run.write('data-hashes.json',Object.fromEntries(await Promise.all(['site/pins-leg.js','site/pins-context-bones.js','site/data-context-bones.js'].map(async p=>[p,createHash('sha256').update(await fs.readFile(p)).digest('hex')]))));
console.log(JSON.stringify({dir:run.dir,...result,passedPhases:passed.length}));
