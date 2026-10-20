// Verify educational admission without weakening the historical pilot tests.
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const run=path.resolve(process.argv[2]);
const pilot='research/evidence-runs/stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq';
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const hash=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
 'pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${name}.js`,'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
const before=await read(path.join(run,'atlas-before.json'));
const ids=['radius_left','ulna_left'];
for(const key of Object.keys(before).filter(k=>!['bones','pins','contextBoneSources'].includes(k)))
 assert.deepEqual(atlas[key],before[key],key);
assert.deepEqual(Object.keys(atlas.bones),Object.keys(before.bones));
for(const [id,bone] of Object.entries(before.bones)){
 const after=atlas.bones[id];
 if(!ids.includes(id)){assert.deepEqual(after,bone,id);continue;}
 assert.equal(bone.noModel,true);assert.equal(after.noModel,false);
 assert.equal(after.modelStatus,'educational_limited');
 assert.equal(after.modelReview.educationalAcceptance,true);
 assert.equal(after.modelReview.fullAnatomicalAcceptance,false);
 assert.equal(after.modelNotice,'Учебная 3D-модель. Точная геометрия суставных поверхностей и зазоров не подтверждена.');
 const allowed=['noModel','note','refs','sourceId','modelStatus','modelNotice','modelFile','modelLicense','modelReview'];
 for(const key of Object.keys(bone).filter(k=>!allowed.includes(k)))
  assert.deepEqual(after[key],bone[key],id+'.'+key);
 for(const ref of bone.refs)assert.ok(after.refs.some(x=>JSON.stringify(x)===JSON.stringify(ref)));
}
const expectedSources={...before.contextBoneSources};
for(const id of ids)expectedSources[id]={sourceId:atlas.bones[id].sourceId,sec:'arm'};
assert.deepEqual(atlas.contextBoneSources,expectedSources);
assert.deepEqual(atlas.pins.map(p=>p.id),before.pins.map(p=>p.id));
const changed=[];
const metadata=new Set(['geometryRequirements','geometryReview','leftForearmReview','modelNote','note']);
for(let i=0;i<atlas.pins.length;i++){
 const p=atlas.pins[i],old=before.pins[i];
 if(JSON.stringify(p)===JSON.stringify(old))continue;
 assert.ok(p.id.includes('_left_'),p.id);
 changed.push(p.id);
 for(const key of new Set([...Object.keys(old),...Object.keys(p)]))
  if(!metadata.has(key))assert.deepEqual(p[key],old[key],p.id+'.'+key);
 assert.equal(p.geometryRequirements.status,'unverified_extent');
 assert.equal(p.geometryReview.coordinateAcceptance,false);
 assert.equal(p.geometryReview.extentAcceptance,false);
 assert.ok(!p.p&&!p.n,p.id);
}
assert.equal(changed.length,44);
const index=indexLandmarks(atlas.pins);
assert.equal(Object.keys(index.byId).length,atlas.pins.length);
for(const p of atlas.pins)for(const bone of relatedBoneIds(p)){
 assert.ok(atlas.bones[bone],bone);
 assert.equal(index.byBone[bone].filter(x=>x.id===p.id).length,1);
}
const originals=await read(pilot+'/original-model-hashes.json');
for(const [file,sha] of Object.entries(originals))assert.equal(await hash(file),sha,file);
const exported=await read(pilot+'/blender-export.json');
const published=await read('site/models/bodyparts3d-3.0/left-forearm/provenance.json');
assert.equal(published.fullAnatomicalAcceptance,false);
for(const row of exported.rows){
 assert.equal(await hash(`research/cache/stage6-sources/${row.sourceId}.obj`),row.sourceSHA256);
 assert.equal(await hash(row.derivative),row.derivativeSHA256);
 assert.equal(await hash('site/'+atlas.bones[row.id].modelFile),row.derivativeSHA256);
 const licence=await fs.readFile('site/'+atlas.bones[row.id].modelLicense,'utf8');
 assert.ok(licence.includes('CC Attribution-Share Alike 2.1 Japan')&&licence.includes('Commercial use'));
}
const results=[];
for(const width of [1280,390])for(const phase of ['setup','sides','cards','joint','rays'])
 results.push(`mcp-edu-v2-${width}-${phase}-result.json`);
for(const width of [1280,390])results.push(`mcp-joint-acceptance-v3-${width}-result.json`);
let checks=0;
for(const file of results){
 const result=await read(path.join(run,file));assert.equal(result.status,'passed',file);
 checks+=result.checks.length;
}
const absent=Object.entries(atlas.bones).filter(([,b])=>b.noModel).map(([id])=>id);
assert.equal(absent.length,62);
const result={status:'passed',boneCards:Object.keys(atlas.bones).length,uniquePinIds:atlas.pins.length,
 anatomicalContentCoordinatesAndLinksUnchanged:true,metadataUpdated:changed,
 originalModelHashesUnchanged:Object.keys(originals).length,sourceOBJsUnchanged:2,pilotGLBsUnchanged:2,
 publishedGLBsByteIdentical:true,noModelEliminated:2,noModelOwners:absent.length,absent,
 browserPhases:results.length,browserChecks:checks,browserResults:results,
 educationalAcceptance:true,fullAnatomicalAcceptance:false};
await fs.writeFile(path.join(run,'final-consistency.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,metadataUpdated:changed.length,absent:absent.length,browserResults:results.length}));
