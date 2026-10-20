// Final skull catalogue additions: preserve every prior record and exercise new cards.
import fs from 'node:fs/promises';
import {createEvidenceRun} from './evidence-run.mjs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-final-2026-10-17');
const read=async name=>JSON.parse(await fs.readFile(path.join(out,name),'utf8'));
const before=await read('inventory-before-complete.json'),now=await read('inventory-current.json');
assert.deepEqual(now.own,before.own,'All 521 original records must be unchanged');
const pendingShared=[];
for(const old of before.shared){
 const p=now.shared.find(q=>q.id===old.id);assert.ok(p);
 if(!old.geometryKind){
  assert.equal(p.geometryKind,'unknown');
  const {geometryKind,...rest}=p;assert.deepEqual(rest,old);
  pendingShared.push(p.id);
 }else assert.deepEqual(p,old);
}
assert.equal(pendingShared.length,32);
assert.deepEqual(now.bones,before.bones,'All 22 bone cards must be unchanged');
for(const old of before.extras)assert.deepEqual(now.extras.find(p=>p.id===old.id),old);
const rows=now.extras.filter(p=>!before.extras.some(q=>q.id===p.id));
assert.equal(rows.length,25);assert.equal(now.totalPins,1879);assert.equal(now.withoutPosition,553);
const all=[...now.own,...now.shared,...now.extras];
assert.equal(new Set(all.map(p=>p.id)).size,all.length);
for(const p of rows){
 assert.ok(now.bones.some(b=>b.id===p.b));
 for(const key of ['p','n','c','noModel'])assert.equal(Object.hasOwn(p,key),false);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 assert.ok(p.candidateId&&p.refs.length>=2);assert.equal(p.educationAvailable,false);
 assert.ok(new Set(p.refs.map(r=>r.authorGroup)).size>=2);
 for(const id of p.relatedLandmarks)assert.ok(all.some(q=>q.id===id),id);
 assert.equal(all.filter(q=>q.b===p.b&&q.ru===p.ru).length,1,p.id+' duplicate');
}
const cards=rows.map(p=>({id:p.id,bone:p.b,ru:p.ru,kind:p.geometryKind,extra:true,related:p.relatedLandmarks}));
if(process.argv[2]==='--prepare'){
 const previous=await fs.readFile(path.join(root,'tools/verify-skull-batch8.mjs'),'utf8');
 const funcs=previous.slice(previous.indexOf('async function card(page)'),previous.indexOf("if(['--mcp-load'"));
 const run=await createEvidenceRun(root,'skull-final-cards');
 for(const width of [1280,390])for(let offset=0;offset<cards.length;offset+=5){
  const chunk=cards.slice(offset,offset+5),config={width,rows:chunk,finish:offset+chunk.length===cards.length,shot:path.join(run.dir,width+'-cards.png')};
  await run.write(`mcp-cards-${width}-${offset}.js`,'async(page)=>{'+funcs+';return cardsBrowser(page,'+JSON.stringify(config)+');}');
 }
}
const result={status:'passed',oldOwnRecordsPreserved:521,oldSharedPreserved:69,oldExtrasPreserved:14,
 boneCards:22,ownLandmarks:521,sharedLandmarks:69,extraLandmarks:39,skullLandmarks:all.length,pendingShared,
 newCards:25,newCoordinates:0,totalPins:now.totalPins,withoutPosition:now.withoutPosition,cards};
await (await createEvidenceRun(root,'skull-final-data')).write('data-regression.json',result);
console.log(JSON.stringify({...result,cards:undefined,pendingShared:pendingShared.length}));
