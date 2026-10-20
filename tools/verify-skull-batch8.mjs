// Batch 8 regression: preserved identities, supplementary cards and navigation.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createEvidenceRun} from './evidence-run.mjs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {indexLandmarks,hasLandmarkPosition} from '../site/atlas-landmarks.js';
import {checkData as legacyData,mcpScript as sharedScript} from './verify-stage5-skull.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-batch8-2026-10-16');
const bones=['mandible','occipital','ethmoid'];
const changedDescriptions=new Set([8,12,25,36].map(n=>'head_mandible_A02_1_15_'+String(n).padStart(3,'0')));
const paired=new Set([6,7,8,9,12,14,15,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38]);
async function data(){
 const before=JSON.parse(await fs.readFile(path.join(out,'head-baseline.json'),'utf8'));
 const box={window:{}};vm.createContext(box);let rawHead;
 for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared']){
  vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
  if(name==='pins-head')rawHead=new Map(JSON.parse(JSON.stringify(box.window.ATLAS.pins)).map(p=>[p.id,p]));
 }
 const a=JSON.parse(JSON.stringify(box.window.ATLAS)),index=indexLandmarks(a.pins),changed=[];
 for(const old of before){
  const p=rawHead.get(old.id);assert.ok(p,old.id);
  for(const k of ['b','c','ru','lat','p','n','loc','m','relations','concept','catalogueBones','partOf'])assert.deepEqual(p[k],old[k],old.id+': '+k);
  if(!changedDescriptions.has(p.id))assert.equal(p.x,old.x);else assert.notEqual(p.x,old.x);
  if(p.b==='mandible'&&(paired.has(Number(p.c.slice(-3)))||[10,11].includes(Number(p.c.slice(-3)))))assert.equal(p.lateralityReview.status,'coverage_unconfirmed');
  else assert.deepEqual(p.lateralityReview,old.lateralityReview);
  for(const ref of old.refs)assert.ok(p.refs.some(r=>JSON.stringify(r)===JSON.stringify(ref)),old.id+': removed source');
  if(old.geometryKind!=='unknown')assert.equal(p.geometryKind,old.geometryKind);
  else if(p.geometryKind!=='unknown'){
   assert.ok(bones.includes(p.b));assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
   changed.push(p.id);
  }
 }
 assert.equal(changed.length,37);
 const head=before.map(p=>index.byId[p.id]),target=head.filter(p=>p.b==='mandible'||changed.includes(p.id)),extra=a.pins.filter(p=>p.t==='additional'&&p.b==='mandible');
 assert.equal(head.length,521);assert.equal(target.length,40);assert.equal(extra.length,6);
 assert.equal(target.filter(p=>p.geometryKind==='unknown').length,0);
 const unknown=head.filter(p=>p.geometryKind==='unknown');assert.equal(unknown.length,0);
 for(const p of extra){
  assert.ok(bones.includes(p.b)&&a.bones[p.b]);assert.ok(['right','left'].includes(p.side)&&p.id.includes('_'+p.side+'_'));
  for(const k of ['p','n','c','noModel'])assert.equal(Object.hasOwn(p,k),false,p.id+': '+k);
  assert.equal(hasLandmarkPosition(p),false);assert.equal(p.educationAvailable,false);
  assert.equal(new Set(p.refs.map(r=>r.authorGroup)).size,2);
  assert.equal(a.pins.filter(q=>q.b===p.b&&q.ru===p.ru).length,1,'Semantic duplicate '+p.id);
  assert.ok(p.relatedLandmarks.length>0);
  for(const id of p.relatedLandmarks)assert.ok(index.byId[id],p.id+' -> '+id);
 }
 assert.equal(a.pins.length,1854);assert.equal(a.pins.filter(p=>!p.p).length,528);
 const {instances,...legacy}=await legacyData();
 const cards=[...target,...extra].map(p=>({id:p.id,bone:p.b,code:p.c,ru:p.ru,kind:p.geometryKind,extra:p.t==='additional',related:p.relatedLandmarks||[],bilateral:p.lateralityReview?.pattern==='bilateral_on_unpaired_bone'}));
 const result={status:'passed',classified:37,remainingSkull:unknown.map(p=>p.id),remainingTarget:0,originalIDsAndCoordinatesPreserved:521,previousExplicitKindsPreserved:484,newCards:6,newCoordinates:0,newSharedRelations:0,cards,legacy};
 await (await createEvidenceRun(root,'skull-batch8-data')).write('data-regression.json',result);
 return {status:'passed',classified:37,remaining:0,ownCards:40,newCards:6,total:1854,withoutP:528};
}
async function card(page){
 if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
 if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
}
async function cardsBrowser(page,{width,rows,shot,finish}){
 const errors=[],onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);
 const links=[];
 try{
  await page.setViewportSize({width,height:900});await page.waitForFunction(()=>window.__ready);
  for(const p of rows){
   await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},p.bone);await card(page);
   const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');if(await chip.count()!==1)throw Error('Duplicate/missing '+p.id);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card(page);
   if(await page.locator('.pinbox .landmark-geometry').getAttribute('data-geometry-kind')!==p.kind)throw Error('Wrong type '+p.id);
   if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Lost ID '+p.id);
   if(p.bilateral&&await page.locator('.pinbox [data-laterality="bilateral_on_unpaired_bone"]').count()!==1)throw Error('Bilateral limit '+p.id);
   if(p.extra){
    if(!(await page.locator('.pinbox').textContent()).includes('код TA98 не присвоен'))throw Error('False code '+p.id);
    if(await page.locator('.pinbox [data-detail-mode="education"]').count())throw Error('Undefined education target');
    if(await page.evaluate(id=>ATLAS.pins.find(p=>p.id===id).p!==undefined,p.id))throw Error('Invented coordinate');
    for(const related of p.related){
     await page.evaluate(p=>__atlas.goTo(p.bone,null,p.id),p);await card(page);
     const link=page.locator('.pinbox [data-related-pin="'+related+'"]');await link.scrollIntoViewIfNeeded();await link.click();await card(page);
     const state=await page.evaluate(id=>({pin:__atlas.state.pin,sel:__atlas.state.sel,targetBone:ATLAS.pins.find(p=>p.id===id).b}),related);
     if(state.pin!==related||state.sel!==state.targetBone&&state.sel!==p.bone)throw Error('Related navigation '+JSON.stringify(state));
     links.push({from:p.id,to:related,selectedBone:state.sel});
    }
    if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
    await page.locator('#bList').click();await page.locator('#q').fill(p.ru);
    const hit=page.locator('#dlist [data-pinjump="'+p.id+'"]');if(await hit.count()!==1)throw Error('Search '+p.id);
    await hit.click();await card(page);if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Search selection '+p.id);
   }
  }
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  if(finish){await page.locator('.pinbox').scrollIntoViewIfNeeded();shot=shot.replace(/\.png$/, '-'+await page.evaluate(()=>crypto.randomUUID())+'.png');await page.screenshot({path:shot,timeout:10000});}
  return {status:'passed',width,testedIDs:rows.map(p=>p.id),supplementaryCards:rows.filter(p=>p.extra).length,links,errors,shot:finish?shot:null};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
}
if(['--mcp-load','--mcp-kinds'].includes(process.argv[2])){
 const kinds=process.argv[2]==='--mcp-kinds';
 console.log((await sharedScript({base:'http://127.0.0.1:8782',width:Number(process.argv[3]),theme:process.argv[4],ids:['shared_skull_083_right','shared_skull_083_left'],offset:kinds?2:0,finalChecks:kinds})).replaceAll('shots/stage5-skull','shots/stage5-skull-batch8'));
}else if(process.argv[2]==='--mcp-cards'){
 const result=JSON.parse(await fs.readFile(path.join(out,'data-regression.json'),'utf8')),width=Number(process.argv[3]);
 const offset=Number(process.argv[4]||0),limit=Number(process.argv[5]||12),rows=result.cards.slice(offset,offset+limit);assert.ok(rows.length);
 console.log('async(page)=>{'+card.toString()+';return ('+cardsBrowser.toString()+')(page,'+JSON.stringify({width,rows,finish:offset+rows.length===result.cards.length,shot:path.join((await createEvidenceRun(root,'skull-batch8-cards')).dir,width+'-cards.png')})+');}');
}else console.log(JSON.stringify(await data()));
