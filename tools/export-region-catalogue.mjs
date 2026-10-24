// Read-only ID/owner snapshot for the mask builder; no anatomical inference.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import crypto from 'node:crypto';
const box={window:{}};vm.createContext(box);const sources={};
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared']) {
 const file='site/'+name+'.js',bytes=await fs.readFile(file);sources[file]=crypto.createHash('sha256').update(bytes).digest('hex');vm.runInContext(bytes.toString('utf8'),box);
}
const a=box.window.ATLAS;
await fs.writeFile(process.argv[2],JSON.stringify({sources,bones:Object.keys(a.bones),noModel:Object.entries(a.bones).filter(([,b])=>b.noModel).map(([id])=>id),pins:a.pins.map(p=>({id:p.id,b:p.b,hasPosition:!!p.p}))},null,2),{flag:'wx'});
console.log(JSON.stringify({bones:Object.keys(a.bones).length,pins:a.pins.length,noModel:Object.values(a.bones).filter(b=>b.noModel).length}));
