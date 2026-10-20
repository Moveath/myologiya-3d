// Reuse pilot baselines without rerunning exports or intersection scans.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const run=path.resolve(process.argv[2]);
const previous=path.resolve('research/evidence-runs/stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq');
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const hash=async p=>createHash('sha256').update(await fs.readFile(p)).digest('hex');
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
 'pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${name}.js`,'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
assert.deepEqual(atlas,await read(path.join(previous,'atlas-before.json')));
const index=indexLandmarks(atlas.pins);
assert.equal(Object.keys(index.byId).length,atlas.pins.length);
for(const p of atlas.pins)for(const bone of relatedBoneIds(p)){
 assert.ok(atlas.bones[bone]);
 assert.equal(index.byBone[bone].filter(x=>x.id===p.id).length,1);
}
const originals=await read(path.join(previous,'original-model-hashes.json'));
for(const [file,expected] of Object.entries(originals))assert.equal(await hash(file),expected,file);
const exported=await read(path.join(previous,'blender-export.json'));
for(const row of exported.rows){
 assert.equal(await hash(`research/cache/stage6-sources/${row.sourceId}.obj`),row.sourceSHA256);
 assert.equal(await hash(row.derivative),row.derivativeSHA256);
}
const manifest=await read('build_stage6/left_forearm_v1/browser/local-v2.html.manifest.json');
assert.equal(await hash('site/local.html'),manifest.sourceHTMLSHA256);
const results=[];
for(const width of [1280,390])for(const phase of ['setup','sides','cards','joint','rays'])
 results.push(`mcp-v2-${width}-${phase}-result.json`);
results.push('mcp-joint-acceptance-v2-390-result.json','mcp-joint-acceptance-v3-1280-result.json');
let checks=0;
for(const file of results){
 const result=await read(path.join(run,file));assert.equal(result.status,'passed',file);
 checks+=result.checks.length;
}
assert.equal(atlas.bones.radius_left.noModel,true);
assert.equal(atlas.bones.ulna_left.noModel,true);
const result={status:'passed',catalogueUnchanged:true,uniquePinIds:atlas.pins.length,
 validSharedLinks:true,originalModelHashesUnchanged:Object.keys(originals).length,
 sourceOBJsUnchanged:exported.rows.length,pilotGLBsUnchanged:exported.rows.length,
 productionHTMLUnchanged:true,noModelEliminated:0,
 noModelOwners:Object.values(atlas.bones).filter(b=>b.noModel).length,
 browserPhases:results.length,browserChecks:checks,browserResults:results,
 reusedIntersectionEvidence:path.relative(process.cwd(),previous).replaceAll('\\','/'),
 anatomicalAcceptance:false};
await fs.writeFile(path.join(run,'final-consistency.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
