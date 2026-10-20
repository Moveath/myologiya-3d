// Scientific decisions are in the review; these checks prevent data/UI regressions.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {indexLandmarks,relatedBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
import {mcpScript as baseScript} from './verify-stage5-skull.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'research/stage5-skull-batch2-2026-10-16');
const ids=['shared_skull_038','shared_skull_052_right','shared_skull_052_left','shared_skull_085_right','shared_skull_085_left'];
async function data(){
 const box={window:{}};vm.createContext(box);
 for(const f of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
  vm.runInContext(await fs.readFile(path.join(root,'site',f+'.js'),'utf8'),box);
 const pins=JSON.parse(JSON.stringify(box.window.ATLAS.pins)),index=indexLandmarks(pins);
 const expected={shared_skull_038:['frontal','parietal_right','parietal_left','occipital'],shared_skull_085_right:['maxilla_right','lacrimal_right','inferior_concha_right'],shared_skull_085_left:['maxilla_left','lacrimal_left','inferior_concha_left']};
 for(const side of ['right','left'])expected['shared_skull_052_'+side]=['occipital','temporal_'+side];
 const education=JSON.parse(await fs.readFile(path.join(root,'site/skull-education.json'),'utf8'));
 for(const id of ids){
  const p=index.byId[id];assert.deepEqual(relatedBoneIds(p),expected[id]);assert.equal(hasLandmarkPosition(p),false);
  assert.equal(Object.hasOwn(p,'p'),false);assert.equal(Object.hasOwn(p,'n'),false);
  assert.ok(education.entries.some(e=>e.id==='whole:'+p.c));
  assert.ok(new Set(p.refs.map(r=>r.authorGroup)).size>=2);
  for(const b of expected[id])assert.equal(index.byBone[b].filter(x=>x.id===id).length,1);
 }
 const local=['head_frontal_A02_1_03_017','head_parietal_right_A02_1_02_004','head_parietal_left_A02_1_02_004'];
 for(const id of local){assert.equal(index.byId[id].partOf,'shared_skull_038');assert.equal(index.byId[id].geometryKind,'area');}
 for(const side of ['right','left'])assert.equal(index.byId['head_temporal_'+side+'_A02_1_06_038'].partOf,'shared_skull_052_'+side);
 assert.equal(index.byId.head_occipital_A02_1_04_008.partOf,undefined,'Do not invent the side of the occipital coordinate');
 assert.equal(index.byId.head_occipital_A02_1_04_002.geometryKind,'space');
 assert.equal(index.byId.head_occipital_A02_1_04_014.geometryKind,'volume');
 assert.equal(index.byId.head_occipital_A02_1_04_018.geometryKind,'volume');
 assert.equal(index.byId.head_occipital_A02_1_04_019.geometryKind,'area');
 const nomenclature=JSON.parse(await fs.readFile(path.join(out,'fipat-occipital.json'),'utf8'));
 const bilateral=nomenclature.rows.filter(p=>p.bilateral).map(p=>'head_occipital_'+p.code.replaceAll('.','_'));
 assert.equal(bilateral.length,19);
 for(const id of bilateral){const p=index.byId[id];assert.equal(p.lateralityReview.pattern,'bilateral');assert.deepEqual(p.lateralityReview.verifiedModelSides,[]);assert.equal(p.side,undefined);assert.ok(p.lateralityReview.note.includes('не подтверждают обе стороны'));}
 const jug=index.byId.head_occipital_A02_1_04_018;
 assert.equal(jug.lat,'tuberculum jugulare');assert.equal(jug.ru,'Яремный бугорок');
 assert.ok(jug.refs.some(r=>r.url.includes('anatomystandard')&&r.locator.includes('ошибочна')));
 const first=JSON.parse(await fs.readFile(path.join(root,'research/stage5-skull-2026-10-16/catalog-review.json'),'utf8'));
 const refined=first.records.filter(p=>p.geometryKind==='unknown'&&index.byId[p.id].geometryKind!=='unknown').map(p=>({id:p.id,code:p.code,bone:p.boneId,kind:index.byId[p.id].geometryKind}));
 assert.equal(refined.length,31);
 const remaining=first.records.filter(p=>index.byId[p.id].geometryKind==='unknown').map(p=>p.id);assert.equal(remaining.length,371);
 const result={status:'passed',newSharedInstances:5,newRelationEdges:14,localPartsLinked:5,bilateralTerms:bilateral,classified:refined,remainingUnknown:remaining,geometryAcceptance:false,newCoordinates:0};
 await fs.writeFile(path.join(out,'data-batch2.json'),JSON.stringify(result,null,2)+'\n');return {status:result.status,classified:refined.length,remainingUnknown:remaining.length,newSharedInstances:5,newRelationEdges:14,bilateralTerms:bilateral.length};
}
async function bilateralBrowser(page,{width,ids,shot}){
 const errors=[],onError=e=>errors.push(String(e));page.on('pageerror',onError);
 async function card(){
  if(await page.locator('#mobileCard').isVisible()&&(await page.locator('#app').getAttribute('data-card-open'))!=='true')await page.locator('#mobileCard').click();
  const more=page.locator('#bMore');if(await more.isVisible()&&(await more.textContent())==='Подробнее')await more.click();
 }
 try{
  await page.setViewportSize({width,height:900});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(()=>{__atlas.activatePin(null);return __atlas.goTo('occipital');});await card();
  for(const id of ids){
   const chip=page.locator('#sheet [data-pinid="'+id+'"]');if(await chip.count()!==1)throw Error('Missing/duplicate own record '+id);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card();
   const note=page.locator('.pinbox [data-laterality="bilateral"]');
   if(await note.count()!==1||!(await note.textContent()).includes('не подтверждают обе стороны'))throw Error('Missing bilateral limitation '+id);
   if(await page.evaluate(()=>__atlas.state.pin)!==id)throw Error('Selection changed');
  }
  const chip=page.locator('#sheet [data-pinid="head_occipital_A02_1_04_002"]');await chip.scrollIntoViewIfNeeded();await chip.click();await card();
  const text=await page.locator('.pinbox .landmark-geometry').textContent();
  if(!text.includes('Пространство или отверстие')||text.includes('между костями'))throw Error('Foramen magnum incorrectly described as interbone');
  if(await page.locator('.pinbox .landmark-laterality').count())throw Error('Unpaired opening inherited bilateral label');
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  await page.screenshot({path:shot,timeout:10000});return {status:'passed',width,bilateralCards:ids.length,foramenMagnumScope:'own_occipital',errors,shot};
 }finally{page.off('pageerror',onError);}
}
if(process.argv[2]==='--mcp-laterality'){
 const r=JSON.parse(await fs.readFile(path.join(out,'data-batch2.json'),'utf8')),width=Number(process.argv[3]||390);
 const options={width,ids:r.bilateralTerms,shot:path.join(root,'shots/stage5-skull-batch2',width+'-laterality.png')};
 console.log('async(page)=>('+bilateralBrowser.toString()+')(page,'+JSON.stringify(options)+')');
}else if(process.argv[2]==='--mcp'){
 await fs.mkdir(path.join(root,'shots/stage5-skull-batch2'),{recursive:true});
 const code=await baseScript({ids,width:Number(process.argv[3]||1280),theme:process.argv[4]||'dark',finalChecks:true});
 // Separate output directory preserves first-batch screenshots/history.
 console.log(code.replaceAll('shots/stage5-skull','shots/stage5-skull-batch2'));
}else console.log(JSON.stringify(await data()));
