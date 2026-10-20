import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createEvidenceRun} from './evidence-run.mjs';
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=vm.runInNewContext(source.match(/const probe=([\s\S]*?);\r?\n\r?\nasync function/)[1]);
async function browser(page,{width,theme,dir,probe}){
 const errors=[],checks=[];let phase='load';
 const check=(v,m)=>{if(!v)throw Error(m);checks.push(m);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(12000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const side=async value=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator('[data-side-view="'+value+'"]').click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8783/local.html?theme='+theme,{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>localStorage.removeItem('myo3d'));await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('talus');});
  phase='all-cards';const cards=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>p.footReview);
   for(const b of new Set(rows.map(p=>p.b))){await __atlas.goTo(b);for(const p of rows.filter(p=>p.b===b)){
    __atlas.activatePin(p.id);const el=document.querySelector('.pinbox');
    if(!el?.textContent.includes(p.x)||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind)throw Error('Card '+p.id);
    if(!el.querySelector('[data-geometry-status="unverified_extent"]'))throw Error('Missing geometry limit '+p.id);
   }}return rows.length;
  });check(cards===299,'299 catalogue cards and representation limits');
  phase='shared';const joints=await page.evaluate(()=>ATLAS.pins.filter(p=>p.footReview&&p.relations).map(p=>({id:p.id,owners:p.relations.map(r=>r.bone)})));let edges=0;
  for(const j of joints)for(const b of j.owners){await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();
   const chip=page.locator('#sheet [data-pinid="'+j.id+'"]');check(await chip.count()===1,'Single shared chip '+b+'/'+j.id);await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===j.id,'Shared selection '+b+'/'+j.id);check(await page.locator('.pin[data-pinid="'+j.id+'"]').count()===0,'No invented joint marker '+j.id);edges++;
  }check(edges===126,'126 shared links');
  phase='left-search';await close();await page.locator('#bList').click();await page.locator('#q').fill('Таранная кость');
  const hit=page.locator('#dlist [data-id="talus_left"]');check(await hit.count()===1,'One left talus search result');await hit.click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='talus_left','Search selects left talus');
  check((await page.locator('#sheet').textContent()).includes('Подтверждённой левой модели'),'Missing geometry explicit');
  check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).every(id=>!id.endsWith('_left') || !['talus_left','calcaneus_left'].includes(id)),'No invented left meshes');
  await page.screenshot({path:dir+'/left-no-model.png'});
  phase='right-isolation';await side('right');await page.evaluate(async()=>{await __atlas.goTo('talus');__atlas.activatePin('extra_talus_subtalar_joint');});await card();await page.locator('#bIso').click();
  check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['calcaneus','talus']),'Subtalar joint isolates two participants');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Two participants transparent');
  await page.screenshot({path:dir+'/subtalar-shared.png'});await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='variant';await page.evaluate(async()=>{await __atlas.goTo('talus');__atlas.activatePin('tal_os_trigonum');});await card();
  check(await page.locator('.pin[data-pinid="tal_os_trigonum"]').count()===0,'Unverified os trigonum hidden');check((await page.locator('.pinbox').textContent()).includes('не установлено'),'Variant warning');
  phase='canvas';await page.evaluate(()=>__atlas.activatePin(null));await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('talus'));check(!!target,'Visible talus ray target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='talus','Real canvas click');
  const bvh=await page.evaluate(target=>__thoraxCheck.compare(target),target);check(bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'BVH/native faces and distances match on ten rays');
  check(await page.evaluate(()=>__thoraxCheck.snapshot().cut)===false,'Skull cuts inactive in leg');
  await side('left');check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).every(id=>!['talus','calcaneus','navicular','cuboid','metatarsal_1'].includes(id)),'Left view excludes right foot bones');await side('both');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,'No console errors');
  return {status:'passed',width,theme,cards,sharedEdges:edges,checks,bvh,consoleErrors:errors};
 }catch(e){return {status:'failed',width,theme,phase,error:String(e),checks,consoleErrors:errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
}
const run=await createEvidenceRun(process.cwd(),'stage5-foot-mcp'),width=Number(process.argv[2]||1280),theme=process.argv[3]||'light';
console.log(JSON.stringify({fixture:await run.write('scenario.js','async(page)=>('+browser.toString()+')(page,'+JSON.stringify({width,theme,dir:run.dir,probe})+')'),run:run.dir}));
