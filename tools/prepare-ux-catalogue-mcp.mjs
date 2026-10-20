import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createEvidenceRun} from './evidence-run.mjs';
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const rays=vm.runInNewContext(source.match(/const probe=([\s\S]*?);\r?\n\r?\nasync function/)[1]);
const probe=rays+`window.__uxCheck=()=>({side:curSide(),selected:state.sel,isolate:state.isolate,visible:[...structs.values()].filter(s=>s.meshes.some(m=>m.visible)).map(s=>({id:s.id,kind:s.kind,side:s.side})),hiddenPickables:pickables.filter(m=>!m.visible).length});\n`;
async function browser(page,{width,theme,shot,probe,url}){
 const checks=[],errors=[],snapshots={};let phase='start';
 const check=(v,m)=>{if(!v)throw Error(m);checks.push(m);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(15000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const option=async selector=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator(selector).click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const side=async value=>option('[data-side-view="'+value+'"]');
 const snap=async name=>{const s=await page.evaluate(()=>__uxCheck());snapshots[name]=s;check(!s.hiddenPickables,name+': hidden meshes not pickable');if(s.side!=='both')check(s.visible.every(o=>o.side!==(s.side==='left'?'right':'left')),name+': no opposite-side meshes');return s;};
 const find=async term=>{await close();if(!await page.locator('#q').isVisible())await page.locator('#bList').click();await page.locator('#q').fill(term);};
 try{
  await page.unrouteAll({behavior:'wait'});await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto(url+'?theme='+theme,{waitUntil:'domcontentloaded'});await page.evaluate(()=>localStorage.setItem('myo3d',JSON.stringify({peel:0,context:true,muscleBones:false,subs:{arm:'all'}})));await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);await page.evaluate(()=>__atlas.enterSection('arm'));
  phase='side-and-layers';
  for(const view of ['both','right','left']){
   await side(view);
   for(const layer of [0,1,2,3]){await option('[data-peel="'+layer+'"]');const s=await snap(view+'/'+layer);if(view==='both')check(s.visible.some(x=>x.id==='humerus')&&s.visible.some(x=>x.id==='humerus_left'),'Both humeri remain in layer '+layer);}
  }
  check(await page.locator('#modelCoverage').isVisible(),'Missing-model notice visible outside mobile options');check((await page.locator('#modelCoverage').textContent()).includes('Левая кисть и предплечье пока без 3D-моделей'),'Missing left geometry stated explicitly');
  await page.screenshot({path:shot+'-left.png'});
  phase='catalogue-side';await find('');
  const armIds=await page.locator('#dlist [data-id]').evaluateAll(nodes=>nodes.map(n=>n.dataset.id));
  check(armIds.includes('humerus_left')&&armIds.includes('scaphoid_left'),'Unsearched left catalogue includes existing left cards including noModel');
  check(!armIds.includes('humerus')&&!armIds.includes('scapula')&&!armIds.includes('biceps_brachii'),'Unsearched left catalogue excludes right arm entries');
  phase='sesamoid-search';
  const typical=['sesamoid_mcp1_radial_right','sesamoid_mcp1_ulnar_right','sesamoid_mcp1_radial_left','sesamoid_mcp1_ulnar_left'];
  for(const term of ['сесамовидная','сесамоид','большой палец','сесамо']){
   await find(term);const first=await page.locator('#dlist button[data-id]').evaluateAll(nodes=>nodes.slice(0,4).map(n=>n.dataset.id));
   check(typical.every(id=>first.includes(id)),'Typical thumb sesamoids first: '+term);check(await page.locator('#dlist [data-primary-sesamoids] button').count()===4,'Exactly four primary side-specific cards: '+term);
  }
  check(await page.locator('#dlist [data-variant-results]').count()===1,'Variable sesamoids in separate final group');
  check((await page.locator('#dlist [data-variant-results]').textContent()).includes('не обязательные структуры'),'Variants labelled optional');
  await page.screenshot({path:shot+'-search.png'});
  await page.locator('#dlist [data-id="sesamoid_mcp1_radial_right"]').click();await card();let s=await snap('sesamoid-right');check(s.side==='right','Global search switches to result side');check((await page.locator('#sheet').textContent()).includes('Отдельной модели кости нет'),'Sesamoid noModel retained');check(await page.locator('#bIso').count()===0,'No fictitious isolation for absent model');
  phase='isolation-reset';await page.evaluate(()=>__atlas.goTo('biceps_brachii'));await card();await page.locator('#bIso').click();check((await snap('isolated')).visible.every(x=>x.id==='biceps_brachii'),'Strict muscle isolation');await side('both');s=await snap('after-both');check(s.isolate===null&&s.selected===null,'Side overview clears old selection and isolation');check(s.visible.some(x=>x.id==='humerus')&&s.visible.some(x=>x.id==='humerus_left'),'Both view restored after isolation');
  phase='trapezius';
  const muscles=await page.evaluate(()=>Object.entries(ATLAS.muscles).filter(([,m])=>m.lat==='m. trapezius').map(([id,m])=>({id,parts:Object.entries(m.parts).map(([key,p])=>({key,lat:p.lat}))})));
  check(muscles.length===5,'All five regional trapezius cards covered');
  for(const muscle of muscles){
   await close();await page.evaluate(id=>__atlas.goTo(id),muscle.id);await card();check(await page.locator('#sheet .lat').first().textContent()==='m. trapezius',muscle.id+': whole muscle Latin retained');
   for(const part of muscle.parts){await page.locator('#sheet [data-part="'+part.key+'"]').click();await card();check(await page.locator('#sheet .lat').first().textContent()==='m. trapezius, '+part.lat,muscle.id+'/'+part.key+': full part Latin');check((await page.locator('#sheet [data-selected-part]').textContent()).includes(part.lat),muscle.id+'/'+part.key+': selected part explained');}
  }
  await page.screenshot({path:shot+'-trapezius.png'});
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,'No page/console errors');
  return {status:'passed',width,theme,checks,snapshots,errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,checks,snapshots,errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
}
const run=await createEvidenceRun(process.cwd(),'ux-catalogue-mcp'),width=Number(process.argv[2]||1280),theme=process.argv[3]||'dark';
const fixture=await run.write('scenario.js','async(page)=>('+browser.toString()+')(page,'+JSON.stringify({width,theme,shot:path.join(run.dir,'ux'),probe,url:process.env.ATLAS_URL||'http://127.0.0.1:8000/local.html'})+')');
console.log(JSON.stringify({fixture,run:run.dir}));
