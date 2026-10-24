import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
const run=path.resolve(process.argv[2]), box={window:{}};
vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
 'pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(`site/${name}.js`,'utf8'),box);
await fs.writeFile(path.join(run,'atlas-before.json'),JSON.stringify(box.window.ATLAS),{flag:'wx'});
const hashes={};
async function walk(dir){
 for(const e of await fs.readdir(dir,{withFileTypes:true})){
  const file=path.join(dir,e.name);
  if(e.isDirectory())await walk(file);
  else hashes[file.replaceAll('\\','/')]=createHash('sha256').update(await fs.readFile(file)).digest('hex');
 }
}
await walk('site/models');
await fs.writeFile(path.join(run,'existing-educational-model-hashes.json'),JSON.stringify(hashes,null,2),{flag:'wx'});
for(const file of ['site/index.html','scripts/foot_stage5_review.py'])
 await fs.copyFile(file,path.join(run,path.basename(file)+'.before'),fs.constants.COPYFILE_EXCL);
console.log(JSON.stringify({owners:Object.keys(box.window.ATLAS.bones).length,
 pins:box.window.ATLAS.pins.length,noModel:Object.values(box.window.ATLAS.bones).filter(b=>b.noModel).length,
 existingModelFiles:Object.keys(hashes).length}));
