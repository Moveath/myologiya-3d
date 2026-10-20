// Read-only inventory used by the final skull review; raw and enriched records are distinct.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-final-2026-10-17');
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
 vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
const atlas=JSON.parse(JSON.stringify(box.window.ATLAS));
const source=await fs.readFile(path.join(root,'site/pins-head.js'),'utf8');
const own=JSON.parse(source.slice(source.indexOf('push(...')+8,source.lastIndexOf(');')));
const owners=[...new Set(own.map(p=>p.b))];
const shared=atlas.pins.filter(p=>p.id.startsWith('shared_')&&owners.includes(p.b));
const extras=atlas.pins.filter(p=>p.t==='additional'&&owners.includes(p.b));
const result={bones:owners.map(id=>({id,...atlas.bones[id]})),own,liveOwn:atlas.pins.filter(p=>own.some(q=>q.id===p.id)),shared,extras,totalPins:atlas.pins.length,withoutPosition:atlas.pins.filter(p=>!p.p).length};
await fs.writeFile(path.join(out,'inventory-current.json'),JSON.stringify(result,null,2)+'\n');
try{await fs.writeFile(path.join(out,'inventory-before.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});}catch(e){if(e.code!=='EEXIST')throw e;}
// The initial prefix filter missed the two temporozygomatic canonical records.
// Recover their exact before-state only if reversing this task's sole shared-data
// addition reproduces the protected original SHA256; retain the first inventory.
const old=JSON.parse(await fs.readFile(path.join(out,'inventory-before.json'),'utf8'));
if(old.shared.length===67){
 const protectedFiles=JSON.parse(await fs.readFile(path.join(out,'protected-before.json'),'utf8'));
 const current=await fs.readFile(path.join(root,'site/pins-shared.js'),'utf8');
 const reconstructed=current.replaceAll(',"geometryKind":"unknown"','');
 const hash=createHash('sha256').update(reconstructed).digest('hex');
 if(hash!==protectedFiles['site/pins-shared.js'])throw Error('Cannot reconstruct complete original shared inventory');
 const priorShared=shared.map(p=>{const q=structuredClone(p);if(q.geometryKind==='unknown')delete q.geometryKind;return q;});
 const complete={...old,shared:priorShared,baselineSupplement:{reason:'Original filter omitted temporozygomatic IDs',reconstructedSharedSourceSha256:hash,originalHashMatched:true}};
 await fs.writeFile(path.join(out,'inventory-before-complete.json'),JSON.stringify(complete,null,2)+'\n');
}
console.log(JSON.stringify({bones:owners.length,own:own.length,shared:shared.length,extras:extras.length,total:atlas.pins.length,withoutPosition:result.withoutPosition}));
