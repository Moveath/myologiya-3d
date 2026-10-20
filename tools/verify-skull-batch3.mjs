// Data/UI contracts. Source judgments and specimen acceptance remain separate.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {indexLandmarks,relatedBoneIds,isOwnBoneTerm,hasLandmarkPosition} from '../site/atlas-landmarks.js';
import {checkData as previousData,mcpScript as previousBrowser} from './verify-stage5-skull.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-batch3-2026-10-16');
const newIds=['shared_skull_083_right','shared_skull_083_left'];
async function loadHead(file){const box={window:{ATLAS:{pins:[]}}};vm.createContext(box);vm.runInContext(await fs.readFile(file,'utf8'),box);return JSON.parse(JSON.stringify(box.window.ATLAS.pins));}
async function data(){
 const baseline=JSON.parse(await fs.readFile(path.join(out,'head-baseline.json'),'utf8'));
 const head=await loadHead(path.join(root,'site/pins-head.js'));
 const box={window:{}};vm.createContext(box);
 for(const f of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile(path.join(root,'site',f+'.js'),'utf8'),box);
 const pins=JSON.parse(JSON.stringify(box.window.ATLAS.pins)),index=indexLandmarks(pins);
 assert.equal(head.length,521);assert.equal(baseline.length,521);
 const refined=[];
 for(const old of baseline){
  const p=index.byId[old.id];assert.ok(p);
  for(const k of ['b','c','ru','lat','x','p','n','loc','m','partOf'])assert.deepEqual(p[k],old[k],old.id+': '+k);
  for(const ref of old.refs)assert.ok(p.refs.some(r=>JSON.stringify(r)===JSON.stringify(ref)),old.id+': retained source');
  if(old.geometryKind!=='unknown')assert.equal(p.geometryKind,old.geometryKind,old.id);
  else if(p.geometryKind!=='unknown')refined.push({id:p.id,bone:p.b,code:p.c,kind:p.geometryKind,reason:p.geometryKindReason});
 }
 assert.equal(refined.length,54);assert.ok(refined.every(p=>p.reason));
 const unknown=head.filter(p=>p.geometryKind==='unknown').map(p=>p.id);assert.equal(unknown.length,317);
 for(const id of newIds){const p=index.byId[id];assert.deepEqual(relatedBoneIds(p),['sphenoid','frontal']);assert.equal(hasLandmarkPosition(p),false);assert.equal(Object.hasOwn(p,'p'),false);assert.equal(Object.hasOwn(p,'n'),false);assert.equal(p.geometryKind,'space');}
 const caecum=index.byId.head_frontal_A02_1_03_018;
 assert.deepEqual(relatedBoneIds(caecum),['frontal','ethmoid']);assert.equal(isOwnBoneTerm(caecum,'frontal'),true);assert.equal(isOwnBoneTerm(caecum,'ethmoid'),false);assert.equal(caecum.loc,'projection');
 assert.equal(index.byId.head_sphenoid_A02_1_05_023.partOf,undefined);
 assert.deepEqual(index.byId.head_sphenoid_A02_1_05_023.lateralityReview.verifiedModelSides,[]);
 for(const id of [...newIds,caecum.id])for(const bone of relatedBoneIds(index.byId[id]))assert.equal(index.byBone[bone].filter(p=>p.id===id).length,1);
 const previous=await previousData();const {instances,...previousSummary}=previous;
 const related=pins.filter(p=>p.relations?.length);
 const result={status:'passed',classified:refined,remainingUnknown:unknown,previousExplicitKindsPreserved:150,
  originalCoordinatesPreserved:521,originalIDsPreserved:1771,newSharedIDs:newIds,existingRecordLinked:caecum.id,newRelationshipEdges:6,
  current:{totalPins:pins.length,sharedInstances:related.length,sharedConcepts:new Set(related.map(p=>p.concept)).size,
    sharedEdges:related.reduce((n,p)=>n+p.relations.length,0),sharedBoneCards:new Set(related.flatMap(p=>p.relations.map(r=>r.bone))).size,
    noCoordinates:pins.filter(p=>!p.p).length,sharedNoCoordinates:related.filter(p=>!p.p).map(p=>p.id)},
  previousRegression:previousSummary,anatomicalCoordinatesAccepted:0,contoursAccepted:0};
 await fs.writeFile(path.join(out,'data-regression.json'),JSON.stringify(result,null,2)+'\n');
 return {status:'passed',classified:refined.length,remaining:unknown.length,newShared:2,existingLinked:1,newEdges:6,current:result.current};
}
async function card(page){if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();const more=page.locator('#bMore');if(await more.isVisible()&&await more.textContent()==='Подробнее')await more.click();}
async function cardsBrowser(page,{width,rows,shot}){
 const errors=[],onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};page.on('pageerror',onError);page.on('console',onConsole);
 try{
  await page.setViewportSize({width,height:900});await page.waitForFunction(()=>window.__ready);
  let currentBone=null;
  for(const p of rows){
   if(currentBone!==p.bone){await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},p.bone);currentBone=p.bone;}
   await card(page);const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');if(await chip.count()!==1)throw Error('Missing/duplicate '+p.id);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card(page);
   if(await page.locator('.pinbox .landmark-geometry').getAttribute('data-geometry-kind')!==p.kind)throw Error('Wrong kind '+p.id);
   if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Selection lost '+p.id);
  }
  // One old object remains selectable under both anatomical owners.
  const caecum='head_frontal_A02_1_03_018';
  for(const bone of ['frontal','ethmoid']){
   await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},bone);await card(page);
   const chip=page.locator('#sheet [data-pinid="'+caecum+'"]');if(await chip.count()!==1)throw Error('Caecum missing/duplicate on '+bone);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card(page);
   const other=bone==='frontal'?'ethmoid':'frontal';await page.locator('.pinbox [data-gobone="'+other+'"]').click();await card(page);
   const state=await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin}));if(state.sel!==other||state.pin!==caecum)throw Error('Shared navigation lost old ID');
   if(!(await page.locator('.pinbox').textContent()).includes('ориентировочный участок'))throw Error('Missing localization limit');
  }
  if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
  await page.locator('#bList').click();await page.locator('#q').fill('A02.1.03.018');
  const hit=page.locator('#dlist [data-pinjump="'+caecum+'"]');if(await hit.count()!==1)throw Error('Search duplicated old object');await hit.click();await card(page);
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  await page.screenshot({path:shot,timeout:10000});return {status:'passed',width,classifiedCards:rows.length,caecumOwners:2,caecumSearchResults:1,errors,shot};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
}
if(process.argv[2]==='--mcp'){
 await fs.mkdir(path.join(root,'shots/stage5-skull-batch3'),{recursive:true});
 console.log((await previousBrowser({ids:newIds,width:Number(process.argv[3]||1280),theme:process.argv[4]||'dark',finalChecks:true})).replaceAll('shots/stage5-skull','shots/stage5-skull-batch3'));
}else if(process.argv[2]==='--mcp-cards'){
 const result=JSON.parse(await fs.readFile(path.join(out,'data-regression.json'),'utf8')),width=Number(process.argv[3]||1280);
 console.log('async(page)=>{'+card.toString()+';return ('+cardsBrowser.toString()+')(page,'+JSON.stringify({width,rows:result.classified,shot:path.join(root,'shots/stage5-skull-batch3',width+'-cards.png')})+');}');
}else{const result=await data();console.log(JSON.stringify({...result,current:{...result.current,sharedNoCoordinates:result.current.sharedNoCoordinates.length}}));}
