// Addressed regression: old identities, new catalogue entities, no invented geometry.
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {mcpScript} from './verify-stage5-skull.mjs';
import {createEvidenceRun} from './evidence-run.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-targeted-2026-10-17');
const before=JSON.parse(await fs.readFile(path.join(out,'inventory-before.json'),'utf8'));
const box={window:{}};vm.createContext(box);let own;
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared']){
 vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
 if(name==='pins-head')own=JSON.parse(JSON.stringify(box.window.ATLAS.pins)).filter(p=>before.own.some(q=>q.id===p.id));
}
const a=JSON.parse(JSON.stringify(box.window.ATLAS));
const byId=new Map(a.pins.map(p=>[p.id,p]));assert.equal(byId.size,a.pins.length);
const bones=before.bones.map(b=>({id:b.id,...a.bones[b.id]}));
assert.deepEqual(bones,before.bones);assert.deepEqual(own,before.own);
for(const p of before.liveOwn)assert.deepEqual(byId.get(p.id),p);
for(const p of before.extras)assert.deepEqual(byId.get(p.id),p);
const changed=[];
for(const old of before.shared){
 const p=byId.get(old.id);assert.ok(p);
 if(old.geometryKind!=='unknown'){assert.deepEqual(p,old);continue;}
 for(const [key,value] of Object.entries(old))if(!['geometryKind','modelNote','geometryReview','geometryKindReason'].includes(key))assert.deepEqual(p[key],value,old.id+': '+key);
 assert.ok(['point','line','area','space','volume'].includes(p.geometryKind));
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 assert.ok(p.modelNote.startsWith(old.modelNote));assert.ok(p.geometryKindReason);changed.push(p);
}
assert.equal(changed.length,32);
const added=a.pins.filter(p=>p.id.startsWith('extra_')&&!before.extras.some(q=>q.id===p.id));
const newShared=a.pins.filter(p=>p.id.startsWith('shared_skull_')&&!before.shared.some(q=>q.id===p.id));
assert.equal(added.length,40);assert.equal(newShared.length,3);
for(const p of [...added,...newShared]){
 for(const k of ['p','n','noModel'])assert.equal(Object.hasOwn(p,k),false,p.id+': '+k);
 assert.ok(new Set(p.refs.map(r=>r.authorGroup)).size>=2,p.id+' independent sources');
 assert.ok(a.bones[p.b]);assert.equal(a.pins.filter(q=>q.b===p.b&&q.ru===p.ru).length,1,p.id+' semantic duplicate');
 for(const id of p.relatedLandmarks||[])assert.ok(byId.has(id),id);
 if(p.partOf)assert.ok(byId.has(p.partOf));
 for(const r of p.relations||[])assert.ok(a.bones[r.bone]);
}
for(const p of added){assert.ok(!p.c);assert.equal(p.educationAvailable,false);assert.equal(p.geometryReview.coordinateAcceptance,false);}
assert.equal(newShared.find(p=>p.id==='shared_skull_050').relations.length,6);
assert.equal(newShared.find(p=>p.id==='shared_skull_087').relations.length,10);
assert.equal(newShared.find(p=>p.id==='shared_skull_nasal_bone_crest').relations.length,2);
assert.equal(added.filter(p=>p.anatomicalVariation).length,2);
const shared=[...before.shared.map(p=>byId.get(p.id)),...newShared],extras=[...before.extras,...added];
assert.equal(shared.filter(p=>p.geometryKind==='unknown').length,0);
assert.equal(a.pins.length,1922);assert.equal(a.pins.filter(p=>!p.p).length,596);
const result={status:'passed',boneCards:22,own:521,shared:72,extras:79,skullLandmarks:672,classifiedShared:32,
 newCatalogueEntities:41,newSharedCandidates:2,newRecords:43,newCoordinates:0,totalPins:a.pins.length,withoutPosition:596,
 preservedOwn:521,preservedOldExtra:39,oldSharedIdentitiesAndRelationsPreserved:69,
 changedShared:changed.map(p=>({id:p.id,kind:p.geometryKind,reason:p.geometryKindReason,refs:p.refs})),
 added:[...added,...newShared],newRelationEdges:newShared.reduce((n,p)=>n+p.relations.length,0)};
const run=await createEvidenceRun(root,'skull-targeted-data');await run.write('result.json',result);
await run.write('inventory.json',{bones,own,liveOwn:before.liveOwn,shared,extras,totalPins:a.pins.length,withoutPosition:596});
if(process.argv.includes('--prepare')){
 const prior=await fs.readFile(path.join(root,'tools/verify-skull-batch8.mjs'),'utf8');
 const funcs=prior.slice(prior.indexOf('async function card(page)'),prior.indexOf("if(['--mcp-load'"));
 const cards=added.map(p=>({id:p.id,bone:p.b,ru:p.ru,kind:p.geometryKind,extra:true,related:p.relatedLandmarks}));
 for(const width of [1280,390]){
  const ids=[...changed,...newShared].map(p=>p.id);
  for(let offset=0;offset<ids.length;offset+=4)await run.write(`shared-${width}-${offset}.js`,await mcpScript({width,theme:width===1280?'dark':'light',ids,offset,limit:4,finalChecks:false,budgetMs:55000}));
  for(let offset=0;offset<cards.length;offset+=5){
   const rows=cards.slice(offset,offset+5),cfg={width,rows,finish:offset+rows.length===cards.length,shot:path.join(run.dir,width+'-cards.png')};
   await run.write(`cards-${width}-${offset}.js`,'async(page)=>{'+funcs+';return cardsBrowser(page,'+JSON.stringify(cfg)+');}');
  }
 }
}
console.log(JSON.stringify({status:'passed',run:run.dir,classified:32,new:43,skull:672,total:1922,withoutP:596}));
