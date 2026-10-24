// Catalogue and hash inventory only: unchanged source GLBs are not decoded again.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import crypto from 'node:crypto';
const run=process.argv[2],box={window:{}},hashes={};vm.createContext(box);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const file of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','data-muscle-recovery','data-neck-recovery']){
 const name='site/'+file+'.js',b=await fs.readFile(name);hashes[name]=hash(b);vm.runInContext(b.toString(),box);
}
const A=box.window.ATLAS;
const list=(items)=>Object.entries(items).filter(([,c])=>c.noModel).map(([id,c])=>({id,ru:c.ru,lat:c.lat,side:c.side??null,group:c.g??null}));
const bones=list(A.bones),muscles=list(A.muscles),parts=Object.entries(A.muscles).flatMap(([id,c])=>Object.entries(c.parts||{}).filter(([,p])=>p.noModel).map(([part,p])=>({id,part,ru:p.ru,lat:p.lat,side:c.side??null})));
for(const f of ['arm','leg','head','neck','thorax','arm-extra','leg-extra']){const p='site/'+f+'-glb.txt';hashes[p]=hash(await fs.readFile(p));}
for(const c of Object.values(A.muscles).filter(c=>c.modelFile)){const p='site/'+c.modelFile;hashes[p]=hash(await fs.readFile(p));}
const original=JSON.parse(await fs.readFile('research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT/muscle-inventory-after.json'));
const reuse=Object.keys(hashes).filter(p=>p.endsWith('-glb.txt')).map(p=>({file:p,sha256:hashes[p],matchesPriorRealInventory:hashes[p]===original.hashes[p]}));
if(reuse.some(r=>!r.matchesPriorRealInventory))throw Error('Changed GLB requires targeted real mesh inventory');
const result={date:new Date().toISOString(),method:'Current generated catalogue + hash-guarded reuse of the real published GLB inventory',hashes,unchangedSourceGLBs:reuse,
 cards:{bones:Object.keys(A.bones).length,muscles:Object.keys(A.muscles).length},missing:{bones,muscles,parts},
 counts:{bones:bones.length,muscles:muscles.length,parts:parts.length},
 previousMeshInventory:'research/evidence-runs/stage7-muscle-batch2-2026-10-21T11-24-13-460Z-zNgJ41/node-integration.json'};
await fs.writeFile(run+'/inventory.json',JSON.stringify(result,null,2),{flag:'wx'});
console.log(JSON.stringify({cards:result.cards,counts:result.counts,verifiedUnchangedGLBs:reuse.length}));
