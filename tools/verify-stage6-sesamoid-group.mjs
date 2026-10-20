// Addressed catalogue regression; no anatomical coordinates are generated.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const dir=path.resolve(process.argv[2]),mode=process.argv[3];
assert.ok(dir.startsWith(path.resolve('research/evidence-runs')+path.sep));
assert.ok(['before','after','final'].includes(mode));
const files=['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'];
const box={window:{}};vm.createContext(box);
for(const name of files)vm.runInContext(await fs.readFile(`site/${name}.js`,'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
const write=(name,value)=>fs.writeFile(path.join(dir,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
if(mode==='before'){
  await write('atlas-before.json',atlas);
  await write('missing-owners.json',Object.entries(atlas.bones).filter(([,b])=>b.noModel).map(([id,b])=>({id,...b})));
  const checks=JSON.parse(await fs.readFile('research/evidence-runs/stage5-reconciliation-2026-10-19T18-08-46-283Z-BPI4sH/resource-hash-reconciliation.json','utf8')).checks;
  const hashes={};
  for(const {file,sha256} of checks){
    hashes[file]=createHash('sha256').update(await fs.readFile(file)).digest('hex');
    assert.equal(hashes[file],sha256,file);
  }
  await write('original-model-hashes.json',hashes);
  console.log(JSON.stringify({missingOwners:Object.keys(atlas.bones).filter(id=>atlas.bones[id].noModel).length,pins:atlas.pins.length,unchangedModels:checks.length}));
}else{
  const before=JSON.parse(await fs.readFile(path.join(dir,'atlas-before.json'),'utf8'));
  assert.equal(before.bones.sesamoid_pedis_left.g,'b_tarsus');
  before.bones.sesamoid_pedis_left.g='b_toes';
  assert.deepEqual(atlas,before,'Only the left sesamoid group may change');
  assert.equal(atlas.bones.sesamoid_pedis.g,'b_toes');
  assert.equal(atlas.bones.sesamoid_pedis_left.noModel,true);
  const idx=indexLandmarks(atlas.pins);
  assert.equal(Object.keys(idx.byId).length,atlas.pins.length);
  for(const pin of atlas.pins)for(const id of relatedBoneIds(pin)){
    assert.ok(atlas.bones[id],id);
    assert.equal(idx.byBone[id].filter(x=>x.id===pin.id).length,1);
  }
  const hashes=JSON.parse(await fs.readFile(path.join(dir,'original-model-hashes.json'),'utf8'));
  for(const [file,hash] of Object.entries(hashes))assert.equal(createHash('sha256').update(await fs.readFile(file)).digest('hex'),hash,file);
  const result={status:'passed',changedField:'bones.sesamoid_pedis_left.g',from:'b_tarsus',to:'b_toes',pins:atlas.pins.length,
    missingOwners:Object.values(atlas.bones).filter(b=>b.noModel).length,stableIds:true,coordinatesAndRelationsUnchanged:true,originalModelsUnchanged:Object.keys(hashes).length};
  await write(mode==='final'?'catalogue-regression-final.json':'catalogue-regression.json',result);console.log(JSON.stringify(result));
}
