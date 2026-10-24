import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const run=path.resolve(process.argv[2]),read=async f=>JSON.parse(await fs.readFile(f,'utf8'));
const hash=async f=>createHash('sha256').update(await fs.readFile(f)).digest('hex');
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${n}.js`,'utf8'),box);
const a=JSON.parse(JSON.stringify(box.window.ATLAS)),before=await read(path.join(run,'atlas-before.json'));
assert.deepEqual(a,before,'No application anatomy/model flags changed during this review');
const missing=Object.keys(a.bones).filter(id=>a.bones[id].noModel),decisions=await read(path.join(run,'owner-decisions.json'));
assert.deepEqual(missing.sort(),decisions.map(d=>d.id).sort());assert.equal(missing.length,20);
const index=indexLandmarks(a.pins);assert.equal(Object.keys(index.byId).length,a.pins.length);
for(const p of a.pins)for(const b of relatedBoneIds(p)){
 assert.ok(a.bones[b]);assert.equal(index.byBone[b].filter(x=>x.id===p.id).length,1);
}
const originals=await read('research/evidence-runs/stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq/original-model-hashes.json');
const current=await read(path.join(run,'existing-educational-model-hashes.json'));
for(const [f,h] of Object.entries({...originals,...current}))assert.equal(await hash(f),h,f);
const meta=await read(path.join(run,'comparison-metadata.json'));
let sources=0;for(const [k,v] of Object.entries(meta))if(k.startsWith('native__')){assert.equal(await hash(v.source.file),v.source.sha256,k);sources++;}
assert.equal(await hash('site/index.html'),await hash(path.join(run,'index.html.before')));
assert.equal(await hash('scripts/foot_stage5_review.py'),await hash(path.join(run,'foot_stage5_review.py.before')));
const quality=await read(path.join(run,'authored-left-quality.json'));
assert.ok(quality.every(q=>q.winding&&q.watertight&&!q.degenerate&&!q.duplicate&&q.positiveVolume));
const pairs=await read(path.join(run,'comparison-pairs.json')),depth=await read(path.join(run,'comparison-depth.json'));
assert.ok(pairs.cross.every(p=>p.complete));assert.ok(depth.rows.every(p=>p.complete));
for(const f of ['blender-hand.json','blender-foot-joints.json','blender-toe-joints.json'])assert.ok((await read(path.join(run,f))).sceneRestored);
const review=await read(path.join(run,'review-summary.json'));
assert.equal(review.newAdmissions,0);assert.equal(review.browserPhases,22);
const result={status:'passed',owners:Object.keys(a.bones).length,pins:a.pins.length,noModel:missing.length,
 allCatalogCoordinatesIdsLinksAndAdmissionFlagsUnchanged:true,originalsUnchanged:Object.keys(originals).length,
 existingPublicModelFilesUnchanged:Object.keys(current).length,authoredSourcesUnchanged:sources,
 authoredLeftQualityPassed:quality.length,newPairTests:pairs.computed,reusedPairTests:pairs.reused,
 aabbDisjoint:pairs.disjoint,newPenetrationDirections:depth.newDirections,reusedPenetrationDirections:depth.reusedDirections,
 browserPhases:review.browserPhases,browserChecks:review.browserChecks,blenderViews:review.blenderViews};
await fs.writeFile(path.join(run,'final-integrity.json'),JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify(result));
