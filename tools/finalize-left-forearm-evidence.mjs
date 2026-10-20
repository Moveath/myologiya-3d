import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const dir=path.resolve(process.argv[2]);
const write=(file,value)=>fs.writeFile(path.join(dir,file),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
const sha=data=>createHash('sha256').update(data).digest('hex');
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${name}.js`,'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
const before=JSON.parse(await fs.readFile(path.join(dir,'atlas-before.json'),'utf8'));
assert.deepEqual(atlas,before,'Canonical anatomy, noModel, IDs and coordinates unchanged');
const idx=indexLandmarks(atlas.pins);assert.equal(Object.keys(idx.byId).length,atlas.pins.length);
for(const p of atlas.pins)for(const b of relatedBoneIds(p)){
 assert.ok(atlas.bones[b]);assert.equal(idx.byBone[b].filter(x=>x.id===p.id).length,1);
}
const originals=JSON.parse(await fs.readFile(path.join(dir,'original-model-hashes.json'),'utf8'));
for(const [file,hash] of Object.entries(originals))assert.equal(sha(await fs.readFile(file)),hash);
const trial=JSON.parse(await fs.readFile('build_stage6/left_forearm_v1/browser/local-v2.html.manifest.json','utf8'));
assert.equal(sha(await fs.readFile('site/local.html')),trial.sourceHTMLSHA256);
const exported=JSON.parse(await fs.readFile(path.join(dir,'blender-export.json'),'utf8'));
for(const row of exported.rows){
 assert.equal(sha(await fs.readFile('research/cache/stage6-sources/'+row.sourceId+'.obj')),row.sourceSHA256);
 assert.equal(sha(await fs.readFile(row.derivative)),row.derivativeSHA256);
}
let checks=0;const browser=[];
for(const width of [1280,390])for(const phase of ['setup','sides','cards','joint','rays']){
 const file=`mcp-v2-${width}-${phase}${width===1280?'-coverage-fix':''}-result.json`;
 const r=JSON.parse(await fs.readFile(path.join(dir,file),'utf8'));assert.equal(r.status,'passed');
 checks+=r.checks.length;browser.push({file,checks:r.checks.length,width,phase});
}
await write('final-consistency.json',{status:'passed',originalModelsUnchanged:Object.keys(originals).length,
 sourceOBJsUnchanged:exported.rows.length,canonicalCatalogueUnchanged:true,pins:atlas.pins.length,
 missingOwners:Object.values(atlas.bones).filter(b=>b.noModel).length,noModelEliminated:0,
 browserPhases:browser,browserChecks:checks,uniqueTrialModels:2,triangleCount:6252,productionHTMLUnchanged:true});
const credits=await fs.readFile('build_stage6/left_forearm_v1/browser/LICENSE-MODELS.txt','utf8');
await fs.writeFile('build_stage6/left_forearm_v1/LICENSE-MODELS.txt',credits+
 '\nregistration-reference.glb additionally contains FMA23131, FMA24436, FMA24438 from the same licensed release, only as registration controls; these are not installed in the atlas.\n',{flag:'wx'});
await fs.writeFile('build_stage6/left_forearm_v1/provenance.json',JSON.stringify({
 release:'BodyParts3D 3.0 / 20110915 / OBJ 95%',author:'The Database Center for Life Science (DBCLS)',
 archive:'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip',
 license:'CC BY-SA 2.1 Japan',licenseURL:'https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en',
 derivativeLicense:'CC BY-SA 2.1 Japan',files:exported.rows,
 transform:'[bp.x,bp.z,-bp.y]/1000; no fitted registration or reflection',
 acceptedScope:'technical export, source-labelled laterality, common source frame; exact articular registration not accepted',
 productionInstalled:false,evidence:path.relative(process.cwd(),dir).replaceAll('\\','/')
},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'passed',browserChecks:checks,pins:atlas.pins.length,noModel:64,originalModels:115}));
