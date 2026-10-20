import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createEvidenceRun} from './evidence-run.mjs';
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=vm.runInNewContext(source.match(/const probe=([\s\S]*?);\r?\n\r?\nasync function/)[1]);
async function browser(page,{width,theme,shot,probe}){
 const check=(v,m)=>{if(!v)throw Error(m);};const errors=[];let phase='load';
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(10000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const find=async term=>{await close();await page.locator('#bList').click();await page.locator('#q').fill(term);};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('**/*.js',r=>r.continue());await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('humerus_left');});
  phase='bone-search';for(const [bone,term,count] of [['radius_left','Левая лучевая кость',19],['ulna_left','Левая локтевая кость',16]]){
   await find(term);const item=page.locator('#dlist [data-id="'+bone+'"]');check(await item.count()===1,'One bone '+bone);check((await item.textContent()).includes('только карточка'),'Search model limitation');await item.click();await card();
   check(await page.evaluate(()=>__atlas.state.sel)===bone,'Left side selected');check((await page.locator('#sheet').textContent()).includes('Отдельной модели кости нет'),'Bone context wording');
   check(!(await page.locator('#sheet').textContent()).includes('отсутствующей мышцы'),'No muscle wording');
   check(await page.locator('#sheet [data-pinid^="context_'+bone+'_"]').count()===count,'TA catalogue '+bone);
   check(await page.locator('#bIso,#bHide,#bBoneXray,#bFocus').count()===0,'No controls for missing geometry');
  }
  phase='all-records';const cards=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>p.leftForearmReview);
   for(const bone of new Set(rows.map(p=>p.b))){await __atlas.goTo(bone);for(const p of rows.filter(p=>p.b===bone)){
    __atlas.activatePin(p.id);const el=document.querySelector('.pinbox');
    if(!el?.textContent.includes(p.x)||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind)throw Error('Card '+p.id);
    if(!el.textContent.includes('Геометрия правой стороны не отражалась'))throw Error('Missing limit '+p.id);
    if(document.querySelector('.pin[data-pinid="'+p.id+'"]'))throw Error('Invented marker '+p.id);
   }}return rows.map(p=>p.id);
  });check(cards.length===44,'44 new records');
  phase='shared';let edges=0;
  const joints=await page.evaluate(()=>ATLAS.pins.filter(p=>p.leftForearmReview&&p.anatomicalEntity==='joint').map(p=>({id:p.id,owners:p.relations.map(r=>r.bone)})));
  for(const joint of joints)for(const owner of joint.owners){
   await page.evaluate(async owner=>{__atlas.activatePin(null);await __atlas.goTo(owner);},owner);await card();
   const chip=page.locator('#sheet [data-pinid="'+joint.id+'"]');check(await chip.count()===1,'Unique joint chip');await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===joint.id,'Joint selected');check(await page.locator('[data-incomplete-models]').count()===1,'Incomplete joint warning');edges++;
  }check(edges===11,'11 joint memberships');
  phase='shared-search';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('ulna_left');});await find('Локтевой сустав слева');
  check(await page.locator('#dlist [data-pinjump="extra_humerus_left_elbow_joint"]').count()===1,'One shared search result');await page.locator('#dlist [data-pinjump="extra_humerus_left_elbow_joint"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='ulna_left','Preserve noModel participant');
  await page.screenshot({path:shot+'-left-card.png',fullPage:false});
  phase='partial-isolation';await page.locator('.pinbox [data-gobone="humerus_left"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.pin)==='extra_humerus_left_elbow_joint','Shared transition keeps ID');
  await page.locator('#bIso').click();check(JSON.stringify(await page.evaluate(()=>__thoraxCheck.snapshot().visible))===JSON.stringify(['humerus_left']),'Only available left participant');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===1,'Available model transparency');
  await page.screenshot({path:shot+'-available-model.png',fullPage:false});
  await card();await page.locator('.pinbox [data-gobone="radius_left"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='radius_left','Back to noModel participant');check(await page.evaluate(()=>__atlas.state.isolate===null&&__atlas.state.xrayBone===null),'No stale isolation/xray');
  phase='right-regression';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('ulna');__atlas.activatePin('extra_humerus_elbow_joint');});await card();
  await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['humerus','radius','ulna']),'Right three-bone isolation');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===3,'Right three-bone transparency');
  await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='canvas';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('humerus_left');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('humerus_left'));check(target,'Canvas target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='humerus_left','Real canvas selection');
  const bvh=await page.evaluate(target=>__thoraxCheck.compare(target),target);check(bvh.rays.length===10&&bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'BVH/native equality');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,errors.join('\n'));
  return {status:'passed',width,theme,cards,sharedEdges:edges,leftBoneSearch:true,sidePreserved:true,noModelControlsHidden:true,
   incompleteModelsWarning:true,partialIsolation:true,partialTransparency:true,sharedTransitions:true,rightIsolationRegression:true,rightTransparencyRegression:true,realCanvasClick:true,bvh,consoleErrors:errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,consoleErrors:errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
}
const run=await createEvidenceRun(process.cwd(),'stage5-left-forearm-mcp'),width=Number(process.argv[2]||1280),theme=process.argv[3]||'dark';
const fixture=await run.write('scenario.js','async(page)=>('+browser.toString()+')(page,'+JSON.stringify({width,theme,shot:path.join(run.dir,'left-forearm'),probe})+')');
console.log(JSON.stringify({fixture,run:run.dir}));
