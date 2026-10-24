import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const run=path.resolve(process.argv[2]),read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const config=await read(path.join(run,'batch.json')),decision=await read(path.join(run,process.argv[3]??'admission.json'));
const hash=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
 'pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${n}.js`,'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS)),before=await read(path.join(run,'atlas-before.json'));
for(const k of Object.keys(before).filter(k=>!['bones','pins','contextBoneSources'].includes(k)))
 assert.deepEqual(atlas[k],before[k],k);
assert.deepEqual(Object.keys(atlas.bones),Object.keys(before.bones));
const allowed=['noModel','note','refs','sourceId','modelStatus','modelNotice','modelFile','modelLicense','modelReview','modelRegionLabel'];
for(const [id,b] of Object.entries(before.bones)){
 const a=atlas.bones[id];
 if(!Object.hasOwn(config.targets,id)){assert.deepEqual(a,b,id);continue;}
 if(decision.admitted.includes(id)){
  assert.equal(b.noModel,true);assert.equal(a.noModel,false);
  assert.equal(a.modelStatus,'educational_limited');
  assert.equal(a.modelReview.educationalAcceptance,true);
  assert.equal(a.modelReview.fullAnatomicalAcceptance,false);
  assert.equal(a.sourceId,config.targets[id]);
  assert.ok(a.modelNotice.includes('не подтверждена'));
 }else{assert.equal(a.noModel,true);assert.ok(!a.modelFile);assert.equal(a.modelReview.educationalAcceptance,false);}
 for(const k of Object.keys(b).filter(k=>!allowed.includes(k)))assert.deepEqual(a[k],b[k],id+'.'+k);
 for(const ref of b.refs)assert.ok(a.refs.some(r=>JSON.stringify(r)===JSON.stringify(ref)));
}
const aliases={...before.contextBoneSources};
for(const id of decision.admitted)aliases[id]={sourceId:config.targets[id],sec:'leg'};
assert.deepEqual(atlas.contextBoneSources,aliases);
assert.deepEqual(atlas.pins.map(p=>p.id),before.pins.map(p=>p.id));
const changed=[],metadata=new Set(['geometryRequirements','modelNote']);
for(let i=0;i<atlas.pins.length;i++){
 const a=atlas.pins[i],b=before.pins[i];
 if(JSON.stringify(a)===JSON.stringify(b))continue;
 assert.ok(Object.hasOwn(config.targets,a.b),a.id);
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))
  if(!metadata.has(k))assert.deepEqual(a[k],b[k],a.id+'.'+k);
 assert.equal(a.footReview.coordinateAcceptance,false);assert.equal(a.footReview.extentAcceptance,false);
 assert.ok(!a.p&&!a.n,a.id);changed.push(a.id);
}
const idx=indexLandmarks(atlas.pins);assert.equal(Object.keys(idx.byId).length,atlas.pins.length);
for(const p of atlas.pins)for(const b of relatedBoneIds(p)){
 assert.ok(atlas.bones[b]);assert.equal(idx.byBone[b].filter(x=>x.id===p.id).length,1);
}
const originals=await read('research/evidence-runs/stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq/original-model-hashes.json');
const prior=await read(path.join(run,'existing-educational-model-hashes.json'));
for(const [f,h] of Object.entries({...originals,...prior}))assert.equal(await hash(f),h,f);
const extraction=await read(path.join(run,'source-extraction.json'));
for(const r of extraction.rows)assert.equal(await hash(`research/cache/stage6-sources/${r.sourceId}.obj`),r.sha256);
const exported=await read(path.join(run,'blender-export.json'));
for(const r of exported.rows){
 assert.equal(await hash(r.derivative),r.derivativeSHA256);
 if(decision.admitted.includes(r.id)){
  assert.equal(await hash('site/'+atlas.bones[r.id].modelFile),r.derivativeSHA256);
  assert.ok((await fs.readFile('site/'+atlas.bones[r.id].modelLicense,'utf8')).includes('CC Attribution-Share Alike 2.1 Japan'));
 }
}
const results=decision.browserResults;assert.ok(results?.length);
let checks=0;
for(const file of results){const r=await read(path.join(run,file));assert.equal(r.status,'passed',file);checks+=r.checks.length;}
const absent=Object.entries(atlas.bones).filter(([,b])=>b.noModel).map(([id])=>id);
assert.equal(Object.values(before.bones).filter(b=>b.noModel).length-absent.length,decision.admitted.length);
const result={status:'passed',boneCards:Object.keys(atlas.bones).length,uniquePinIds:atlas.pins.length,
 anatomicalContentCoordinatesAndLinksUnchanged:true,metadataUpdated:changed,
 originalModelHashesUnchanged:Object.keys(originals).length,previousModelFilesUnchanged:Object.keys(prior).length,
 sourceOBJsUnchanged:extraction.rows.length,publishedModels:decision.admitted,trialOnly:decision.trialOnly,
 noModel:absent.length,absent,browserChecks:checks,browserResults:results,fullAnatomicalAcceptance:false};
await fs.writeFile(path.join(run,'final-consistency.json'),JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify({...result,metadataUpdated:changed.length,absent:absent.length,browserResults:results.length}));
