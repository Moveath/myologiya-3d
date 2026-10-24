import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const [screen,upper,lower,repair,canonical]=process.argv.slice(2).map(x=>path.resolve(x));
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const hash=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const before=await read(path.join(screen,'atlas-before.json')),decision=await read(path.join(lower,'admission.json'));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
 'pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${n}.js`,'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
const strip=(o,fields)=>Object.fromEntries(Object.entries(o).filter(([k])=>!fields.includes(k)));
assert.deepEqual(Object.keys(atlas.bones),Object.keys(before.bones));
for(const key of Object.keys(before).filter(k=>!['bones','pins'].includes(k)))assert.deepEqual(atlas[key],before[key],key);
const changedBones=[];
const candidates=new Set([...Object.keys((await read(path.join(upper,'batch.json'))).targets),
 ...Object.keys((await read(path.join(lower,'batch.json'))).targets)]);
for(const [id,b] of Object.entries(before.bones)){
 const a=atlas.bones[id];
 if(JSON.stringify(a)===JSON.stringify(b))continue;
 assert.ok(candidates.has(id),id);
 assert.deepEqual(strip(a,['noModel','note','refs','modelStatus','modelNotice','modelFile','modelLicense','modelReview','modelRegionLabel','modelOrigin']),
                  strip(b,['noModel','note','refs','modelStatus','modelNotice','modelFile','modelLicense','modelReview','modelRegionLabel','modelOrigin']),id);
 assert.deepEqual(a.sourceId,b.sourceId,'Native source identity must not become opposite FMA');
 changedBones.push(id);
 if(decision.admitted.includes(id)){
  assert.equal(b.noModel,true);assert.equal(a.noModel,false);
  assert.equal(a.modelOrigin.sourceBone,id.replace('_left',''));
  assert.equal(a.modelOrigin.method,'mirrored_educational_reconstruction');
  assert.equal(a.modelReview.educationalAcceptance,true);assert.equal(a.modelReview.fullAnatomicalAcceptance,false);
 }else assert.equal(a.noModel,b.noModel);
}
assert.equal(atlas.pins.length,before.pins.length);
const changedPins=[];
for(let i=0;i<atlas.pins.length;i++){
 const a=atlas.pins[i],b=before.pins[i];
 assert.deepEqual(strip(a,['modelNote','geometryRequirements']),strip(b,['modelNote','geometryRequirements']),a.id);
 if(JSON.stringify(a)!==JSON.stringify(b))changedPins.push(a.id);
}
const indexed=indexLandmarks(atlas.pins);
assert.equal(Object.keys(indexed.byId).length,atlas.pins.length);
for(const pin of atlas.pins)for(const b of relatedBoneIds(pin)){
 assert.ok(atlas.bones[b]);assert.equal(indexed.byBone[b].filter(p=>p.id===pin.id).length,1);
}
const originals=await read('research/evidence-runs/stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq/original-model-hashes.json');
const oldModels=await read(path.join(screen,'existing-educational-model-hashes.json'));
for(const [file,sha] of Object.entries({...originals,...oldModels}))assert.equal(await hash(file),sha,file);
for(const row of decision.files){
 const file='site/'+atlas.bones[row.id].modelFile;
 assert.equal(await hash(file),row.sha256,row.id);
 assert.equal(await hash(file),await hash(path.join((await read(path.join(lower,'batch.json'))).output,row.id+'.glb')));
 const lic=await fs.readFile('site/'+atlas.bones[row.id].modelLicense,'utf8');assert.ok(lic.includes('CC BY-SA 2.1 Japan'));
}
// Negative export fixtures: v1 accidentally retained an unrelated scene.
const glbHeader=async f=>{const b=await fs.readFile(f);return JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());};
let rejectedOld=0,cleanNew=0;
for(const [v1,run] of [['build_stage6/mirror_upper_v1',upper],['build_stage6/mirror_lower_v1',lower]]){
 const cfg=await read(path.join(run,'batch.json'));
 for(const id of Object.keys(cfg.targets)){
  const old=await glbHeader(path.join(v1,id+'.glb'));
  assert.ok(old.scenes.length>1||old.meshes.length>1);rejectedOld++;
  const actual=await glbHeader(path.join(cfg.output,id+'.glb'));
  assert.equal(actual.scenes.length,1);assert.equal(actual.meshes.length,1);cleanNew++;
 }
}
assert.equal((await read(path.join(lower,'coplanar-regression.json'))).status,'passed');
const repaired=await read(path.join(repair,'trimesh-check.json'));
assert.equal(repaired.status,'passed');assert.equal(repaired.rows[0].triangles,274);assert.equal(repaired.rows[0].degenerate,0);
const browser=[];
for(const width of [1280,390]){
 for(const phase of ['setup','sides','sesamoid_pedis_left','canonical','blocked']){
  const file=path.join(canonical,`mcp-v1-${width}-${phase}-result.json`),r=await read(file);
  assert.equal(r.status,'passed',file);browser.push({file,checks:r.checks.length});
 }
}
const absent=Object.entries(atlas.bones).filter(([,b])=>b.noModel).map(([id])=>id);
assert.equal(absent.length,20);assert.equal(30-absent.length,decision.admitted.length);
const result={status:'passed',owners:Object.keys(atlas.bones).length,pins:atlas.pins.length,
 addedModels:decision.admitted,noModel:absent.length,absent,changedBones,changedPins,
 anatomyDefinitionsCoordinatesIdsAndLinksUnchanged:true,nativeSourceIdentitiesUnchanged:true,
 originalsUnchanged:Object.keys(originals).length,previousModelFilesUnchanged:Object.keys(oldModels).length,
 unrelatedSceneExportFixtures:{rejectedOld,cleanNew},repairedToeTriangles:274,
 browser,canonicalChecks:browser.reduce((n,r)=>n+r.checks,0),fullAnatomicalAcceptance:false};
await fs.writeFile(path.join(canonical,'final-consistency.json'),JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify({...result,changedBones:changedBones.length,changedPins:changedPins.length,browser:browser.length,absent:absent.length}));
