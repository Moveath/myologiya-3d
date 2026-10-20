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
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('**/*.js',r=>r.continue());await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('clavicle');});
  phase='cards';const cards=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>p.upperGirdleReview);
   for(const b of new Set(rows.map(p=>p.b))){await __atlas.goTo(b);for(const p of rows.filter(p=>p.b===b)){
    __atlas.activatePin(p.id);const el=document.querySelector('.pinbox');
    if(!el?.textContent.includes(p.x)||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind)throw Error('Card '+p.id);
    if(!el.querySelector('[data-geometry-status="unverified_extent"]'))throw Error('Missing limit '+p.id);
   }}return rows.map(p=>p.id);
  });check(cards.length===68,'68 addressed records');
  phase='shared';let edges=0;
  for(const suffix of ['','_left'])for(const owner of ['clavicle'+suffix,'scapula'+suffix]){
   const id='extra_clavicle'+suffix+'_acromioclavicular_joint';await page.evaluate(async owner=>{__atlas.activatePin(null);await __atlas.goTo(owner);},owner);await card();
   const chip=page.locator('#sheet [data-pinid="'+id+'"]');check(await chip.count()===1,'One shared chip');await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===id,'Shared selection');check(await page.locator('.pin[data-pinid="'+id+'"]').count()===0,'No invented marker');edges++;
  }
  phase='search';await close();await page.locator('#bList').click();await page.locator('#q').fill('Акромиально-ключичный сустав');
  check(await page.locator('#dlist [data-pinjump$="_acromioclavicular_joint"]').count()===2,'Two joint instances');
  await page.locator('#dlist [data-pinjump="extra_clavicle_left_acromioclavicular_joint"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='scapula_left','Search keeps participating owner');
  phase='isolation';await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['clavicle_left','scapula_left']),'Both participants isolated');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Both participants transparent');
  await page.screenshot({path:shot+'-shared.png',fullPage:false});await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='new-search';await close();await page.locator('#bList').click();await page.locator('#q').fill('Вырезка между остью');
  check(await page.locator('#dlist [data-pinjump$="_spinoglenoid_notch"]').count()===2,'Two separate notches');
  await page.locator('#dlist [data-pinjump="extra_scapula_spinoglenoid_notch"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='scapula','Right owner');await page.screenshot({path:shot+'-notch.png',fullPage:false});
  phase='canvas';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('scapula');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('scapula'));check(target,'Canvas target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='scapula','Real canvas selection');
  const bvh=await page.evaluate(target=>__thoraxCheck.compare(target),target);check(bvh.rays.length===10&&bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'BVH/native equality');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,errors.join('\n'));
  return {status:'passed',width,theme,cards,sharedEdges:edges,search:true,isolation:true,transparency:true,realCanvasClick:true,bvh,consoleErrors:errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,consoleErrors:errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
}
const run=await createEvidenceRun(process.cwd(),'stage5-upper-girdle-mcp'),width=Number(process.argv[2]||1280),theme=process.argv[3]||'dark';
const fixture=await run.write('scenario.js','async(page)=>('+browser.toString()+')(page,'+JSON.stringify({width,theme,shot:path.join(run.dir,'girdle'),probe})+')');
console.log(JSON.stringify({fixture,run:run.dir}));
