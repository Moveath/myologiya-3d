// Data preservation and real card selections; no anatomical acceptance by test.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkData as legacyData,mcpScript as sharedScript} from './verify-stage5-skull.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-batch4-2026-10-16');
async function data(){
 const before=JSON.parse(await fs.readFile(path.join(out,'head-baseline.json'),'utf8'));
 const box={window:{ATLAS:{pins:[]}}};vm.createContext(box);
 vm.runInContext(await fs.readFile(path.join(root,'site/pins-head.js'),'utf8'),box);
 const head=JSON.parse(JSON.stringify(box.window.ATLAS.pins)),byId=new Map(head.map(p=>[p.id,p]));
 assert.equal(head.length,521);assert.equal(byId.size,521);
 const changed=[];
 for(const old of before){
  const p=byId.get(old.id);assert.ok(p,old.id);
  for(const k of ['b','c','ru','lat','x','p','n','loc','m','relations','concept','catalogueBones','partOf','lateralityReview'])assert.deepEqual(p[k],old[k],old.id+': '+k);
  for(const ref of old.refs)assert.ok(p.refs.some(r=>JSON.stringify(r)===JSON.stringify(ref)),old.id+': source removed');
  if(old.geometryKind!=='unknown')assert.equal(p.geometryKind,old.geometryKind,old.id);
  else if(p.geometryKind!=='unknown'){
   assert.ok(['sphenoid','temporal_right','temporal_left'].includes(p.b));
   assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
   assert.ok(p.geometryReview.rationale.length>30);
   changed.push({id:p.id,bone:p.b,code:p.c,kind:p.geometryKind,reason:p.geometryReview.rationale});
  }
 }
 assert.equal(changed.length,70);assert.equal(changed.filter(p=>p.bone==='sphenoid').length,36);
 for(const side of ['right','left'])assert.equal(changed.filter(p=>p.bone==='temporal_'+side).length,17);
 for(const code of ['052','054'])assert.equal(byId.get('head_sphenoid_A02_1_05_'+code).geometryKind,'unknown');
 const unknown=head.filter(p=>p.geometryKind==='unknown').map(p=>p.id);
 const pendingTarget=head.filter(p=>['sphenoid','temporal_right','temporal_left'].includes(p.b)&&p.geometryKind==='unknown').map(p=>p.id);
 assert.equal(unknown.length,247);assert.equal(pendingTarget.length,92);
 // A historical complete review must not override an explicit current limit.
 const html=await fs.readFile(path.join(root,'site/index.html'),'utf8');
 const fn=html.slice(html.indexOf('function geometryReviewLink(p){'),html.indexOf('function detailLinks(p)'));
 const fixture={A:{headGeometry:{'bone:code':'complete'}},esc:s=>String(s)};vm.createContext(fixture);vm.runInContext(fn,fixture);
 const reviewed={b:'bone',c:'code',geometryReview:{extentAcceptance:false}};
 assert.match(fixture.geometryReviewLink(reviewed),/data-review-scope="historical"/);
 assert.match(fixture.geometryReviewLink(reviewed),/текущей проверке не принята/);
 assert.match(fixture.geometryReviewLink(reviewed),/data-detail-marker="code"/);
 assert.match(fixture.geometryReviewLink({b:'bone',c:'code'}),/Форма прослежена в указанном объёме/);
 fixture.A.headGeometry['bone:code']='partial';assert.match(fixture.geometryReviewLink(reviewed),/Форма подтверждена частично/);
 assert.equal(fixture.geometryReviewLink({b:'missing',c:'code'}),'');
 const {instances,...legacy}=await legacyData();
 const result={status:'passed',classified:changed,remainingUnknown:unknown,pendingTarget,
  originalCoordinatesPreserved:521,previousExplicitKindsPreserved:204,originalHeadIDsPreserved:521,
  sharedRelationsUnchanged:true,newSharedRelations:0,anatomicalCoordinatesAccepted:0,contoursAccepted:0,historicalMessageContract:'passed',legacy};
 await fs.writeFile(path.join(out,'data-regression.json'),JSON.stringify(result,null,2)+'\n');
 return {status:'passed',classified:70,remainingTarget:92,remainingSkull:247,oldExplicitPreserved:204};
}
async function card(page){
 if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
 const more=page.locator('#bMore');if(await more.isVisible()&&await more.textContent()==='Подробнее')await more.click();
}
async function cardsBrowser(page,{width,rows,shot}){
 const errors=[],onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);
 try{
  await page.setViewportSize({width,height:900});await page.waitForFunction(()=>window.__ready);
  let bone=null,historicalLabels=0;
  for(const p of rows){
   if(bone!==p.bone){await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},p.bone);bone=p.bone;}
   await card(page);const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');
   if(await chip.count()!==1)throw Error('Missing or duplicate '+p.id);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card(page);
   if(await page.locator('.pinbox .landmark-geometry').getAttribute('data-geometry-kind')!==p.kind)throw Error('Wrong type '+p.id);
   if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Lost selected ID '+p.id);
   const wasComplete=await page.evaluate(p=>ATLAS.headGeometry?.[p.bone+':'+p.code]==='complete',p);
   if(wasComplete){
    const message=page.locator('.pinbox [data-review-scope="historical"]');
    if(await message.count()!==1||!(await message.textContent()).includes('текущей проверке не принята'))throw Error('Misleading old extent status '+p.id);
    historicalLabels++;
   }
  }
  for(const id of ['head_sphenoid_A02_1_05_035','head_temporal_right_A02_1_06_071','head_temporal_left_A02_1_06_071']){
   if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
   await page.locator('#bList').click();await page.locator('#q').fill(id.includes('sphenoid')?'A02.1.05.035':'A02.1.06.071');
   const hit=page.locator('#dlist [data-pinjump="'+id+'"]');if(await hit.count()!==1)throw Error('Search identity '+id);
   await hit.click();await card(page);if(await page.evaluate(()=>__atlas.state.pin)!==id)throw Error('Search selection '+id);
  }
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  await page.locator('.pinbox').scrollIntoViewIfNeeded();await page.screenshot({path:shot,timeout:10000});
  return {status:'passed',width,classifiedCards:rows.length,historicalLabels,searchedInstances:3,errors,shot};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
}
if(process.argv[2]==='--mcp-load'){
 console.log((await sharedScript({base:'http://127.0.0.1:8782',width:Number(process.argv[3]),theme:process.argv[4],ids:['shared_skull_083_right','shared_skull_083_left'],finalChecks:true})).replaceAll('shots/stage5-skull','shots/stage5-skull-batch4'));
}else if(process.argv[2]==='--mcp-cards'){
 const result=JSON.parse(await fs.readFile(path.join(out,'data-regression.json'),'utf8')),width=Number(process.argv[3]);
 console.log('async(page)=>{'+card.toString()+';return ('+cardsBrowser.toString()+')(page,'+JSON.stringify({width,rows:result.classified,shot:path.join(root,'shots/stage5-skull-batch4',width+'-cards.png')})+');}');
}else console.log(JSON.stringify(await data()));
