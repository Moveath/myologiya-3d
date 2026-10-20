import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {catalogueMatches, typicalThumbSesamoid, musclePartLatin} from '../site/atlas-catalogue.js';
import {createEvidenceRun} from './evidence-run.mjs';

const beforeDir = process.argv[2];
assert(beforeDir, 'Pass the saved baseline evidence directory');
const before = JSON.parse(await fs.readFile(beforeDir+'/atlas-before.json','utf8'));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
  vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
assert.deepEqual(atlas.pins,before.pins,'All landmark fields, coordinates and relations preserved');
assert.deepEqual(atlas.muscles,before.muscles,'Muscle facts and part names unchanged');
const changes=[];
for(const [id,old] of Object.entries(before.bones)){
  const current=atlas.bones[id];
  if(typicalThumbSesamoid(current)){
    for(const key of new Set([...Object.keys(old),...Object.keys(current)]))
      if(!['ru','searchAliases','catalogueRole'].includes(key))assert.deepEqual(current[key],old[key],id+'/'+key);
    assert(current.ru.includes('большого пальца кисти'));assert(current.noModel);
    for(const term of ['сесамовидная','сесамоид','большой палец','I пястно-фалангового'])assert(catalogueMatches(current,term),id+'/'+term);
    changes.push(id);
  } else assert.deepEqual(current,old,id);
}
assert.equal(changes.length,4);assert.deepEqual(Object.keys(atlas.bones),Object.keys(before.bones));
let parts=0;
for(const muscle of Object.values(atlas.muscles).filter(m=>m.lat==='m. trapezius')){
  assert.equal(musclePartLatin(muscle,null),'m. trapezius');
  for(const part of Object.values(muscle.parts)){
    assert(['pars descendens','pars transversa','pars ascendens'].includes(part.lat));
    assert.equal(musclePartLatin(muscle,part),'m. trapezius, '+part.lat);parts++;
  }
}
assert.equal(parts,15);
const hashes=JSON.parse(await fs.readFile(beforeDir+'/hashes-before.json','utf8'));
const changedFiles=[];
for(const [name,hash] of Object.entries(hashes)){
  const after=createHash('sha256').update(await fs.readFile('site/'+name)).digest('hex');
  if(hash!==after){assert(['index.html','local.html','data-context-bones.js'].includes(name),name);changedFiles.push(name);}
}
const run=await createEvidenceRun(process.cwd(),'ux-catalogue-unit');
await run.write('result.json',{status:'passed',renamedCards:changes,partLabels:parts,unchangedPins:atlas.pins.length,unchangedMuscles:Object.keys(atlas.muscles).length,changedFiles,originalModelsUnchanged:true});
console.log(JSON.stringify({status:'passed',run:run.dir,partLabels:parts,renamedCards:changes.length}));
