// Each phase has a deadline and an exclusive evidence file. No production mutation.
import fs from 'node:fs/promises';
import path from 'node:path';
const run=path.resolve(process.argv[2]),revision=process.argv[3]||'v1';
if(!/^v\d+$/.test(revision))throw Error('Invalid revision');
const prior=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=prior.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__pbCheck').replaceAll('\\n','\n')+`window.__pbIdle=()=>!tween;window.__pbSnapshot=()=>({selection:state.sel,isolate:state.isolate,side:curSide(),items:[...structs.values()].map(s=>({id:s.id,side:s.side,visible:s.meshes.some(m=>m.visible),bvh:s.meshes.every(m=>!!m.geometry.boundsTree),opacity:s.meshes.map(m=>m.material.opacity)}))});\n`;
async function test(page,{run,revision,width,phase,probe}){
 const checks=[],errors=[];let timer;const name=`palmaris-${revision}-${width}-${phase}`;
 const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const onError=e=>errors.push(String(e));page.on('pageerror',onError);page.setDefaultTimeout(6000);
 const snap=()=>page.evaluate(()=>__pbSnapshot());
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();};
 const controls=async()=>{await close();if(width===390&&!(await page.locator('[data-side-view="both"]').isVisible()))await page.locator('#bOptions').click();};
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/trial.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8785/trial.html?region=arm&entry=palmaris_brevis&theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:15000});
   await page.waitForFunction(()=>window.__palmarisTrialReady);await page.evaluate(()=>__atlas.setSide('both'));
   await controls();await page.locator('[data-peel="0"]').click();
   if(await page.locator('#bMuscleBones').getAttribute('aria-pressed')==='true')await page.locator('#bMuscleBones').click();
   if(await page.locator('#bContext').getAttribute('aria-pressed')==='false')await page.locator('#bContext').click();
   check((await snap()).items.some(m=>m.id==='palmaris_brevis'&&m.visible&&m.bvh),'Trial GLB loaded, visible, BVH built');
   check(await page.evaluate(()=>ATLAS.muscles.palmaris_brevis.modelStatus)==='technical_prototype_not_admitted','No educational admission claimed');
   check((await page.locator('#trialBanner').innerText()).includes('без анатомического допуска'),'Persistent trial notice');
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 bone blockers retained');
  }else if(phase==='cards'){
   await close();await page.locator('#bList').click();await page.locator('#q').fill('palmaris brevis');
   check(await page.locator('#dlist [data-id="palmaris_brevis"]').count()===1,'Latin search, single ID');
   await page.locator('#q').fill('короткая ладонная');check(await page.locator('#dlist [data-id="palmaris_brevis"]').count()===1,'Russian search');
   await page.locator('#dlist [data-id="palmaris_brevis"]').click();await card();
   check((await page.locator('#sheet').innerText()).includes('Границы, глубина и прикрепления не подтверждены'),'Limits visible in card');
   await page.locator('#bIso').click();await close();await page.waitForFunction(()=>__pbIdle());
   let s=await snap();check(s.isolate==='palmaris_brevis'&&s.items.filter(m=>m.visible).every(m=>m.id==='palmaris_brevis'),'Isolate only prototype');
   const point=await page.evaluate(()=>__pbCheck.clickPoint('palmaris_brevis'));check(!!point,'Visible canvas target');
   const ray=await page.evaluate(p=>__pbCheck.compare(p),point);check(ray.rays.length===10&&ray.bvh>0&&ray.rays.some(x=>x.hits>0),'Native and BVH rays agree');
   await page.mouse.click(point.x,point.y);check((await snap()).selection==='palmaris_brevis','Real canvas click');
   await card();await page.locator('#bIso').click();await close();
  }else if(phase==='sides'){
   await controls();for(const side of ['right','left','both']){
    await page.locator(`[data-side-view="${side}"]`).click();const s=await snap();check(s.side===side,'Side '+side);
    check(s.items.filter(m=>m.visible&&['left','right'].includes(m.side)).every(m=>side==='both'||m.side===side),'No opposite-side leak '+side);
    check(s.items.some(m=>m.id==='palmaris_brevis'&&m.visible)===(side!=='left'),'Prototype exists only on right '+side);
   }
   await page.evaluate(()=>__atlas.goTo('palmaris_brevis'));await controls();
   const s=await snap();check(s.items.some(m=>m.visible&&m.opacity.some(x=>x<1)),'Transparent neighboring context');
   const previous=await page.locator('#bContext').getAttribute('aria-pressed');await page.locator('#bContext').click();check(await page.locator('#bContext').getAttribute('aria-pressed')!==previous,'Context control works');await page.locator('#bContext').click();
   await close();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
   await page.reload({waitUntil:'domcontentloaded',timeout:15000});await page.waitForFunction(()=>window.__palmarisTrialReady);check(await page.evaluate(()=>__atlas.state.sel)==='palmaris_brevis','Test entry selected after reload');
   check((await page.locator('#trialBanner').innerText()).includes('ТЕСТОВАЯ СБОРКА'),'Trial status survives reload');
  }
  check(!errors.length,'No page errors');await page.screenshot({path:run+'/'+name+'.png'});
  return {status:'passed',width,phase,checks,errors};
 };
 let result;try{result=await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35 s phase deadline'));},35000);})]);}
 catch(e){result={status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);}
 return result;
}
for(const width of [1280,390])for(const phase of ['setup','cards','sides']){
 const args={run,revision,width,phase,probe};
 // MCP VM does not expose dynamic imports. The caller saves the returned result
 // exclusively after EACH phase; never wait until all widths have completed.
 await fs.writeFile(run+`/mcp-palmaris-${revision}-${width}-${phase}.txt`,`async page=>(${test.toString()})(page,${JSON.stringify(args)})`,{flag:'wx'});
}
