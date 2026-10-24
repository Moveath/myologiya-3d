import fs from 'node:fs/promises';
import path from 'node:path';
const [dir,specFile]=process.argv.slice(2),run=path.resolve(dir),spec=JSON.parse(await fs.readFile(specFile));
const old=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=old.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__recoveryRay').replaceAll('\\n','\n')+
`window.__recoverySnapshot=()=>({selection:state.sel,isolate:state.isolate,side:curSide(),idle:!tween,items:[...structs.values()].map(s=>({id:s.id,side:s.side,visible:s.meshes.some(m=>m.visible),bvh:s.meshes.every(m=>!!m.geometry.boundsTree),opacity:s.meshes.map(m=>m.material.opacity)}))});`;
async function review(page,{width,run,probe,spec}){
 const checks=[],errors=[];let timer,phase='setup';const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const onError=e=>errors.push(String(e));page.on('pageerror',onError);page.setDefaultTimeout(5000);
 const close=async()=>{for(const id of ['#closeMobileCard','#closeOptions'])if(await page.locator(id).isVisible())await page.locator(id).click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();};
 const job=async()=>{
  await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/trial.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  phase='load';await page.goto(spec.url+'?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:12000});
  await page.waitForFunction(()=>window.__recoveryTrialReady);
  check(await page.evaluate(id=>ATLAS.muscles[id].modelStatus,spec.id)==='technical_prototype_not_admitted','Unadmitted status retained');
  check((await page.locator('#trialBanner').innerText()).includes('без анатомического допуска'),'Persistent test notice');
  check(await page.evaluate(id=>__recoverySnapshot().items.some(m=>m.id===id&&m.bvh),spec.id),'GLB loaded and BVH built');
  phase='search';await close();await page.locator('#bList').click();await page.locator('#q').fill(spec.search);
  check(await page.locator(`#dlist [data-id="${spec.id}"]`).count()===1,'Single search result for stable ID');
  await page.locator(`#dlist [data-id="${spec.id}"]`).click();await card();
  check((await page.locator('#sheet').innerText()).includes(spec.cardCheck),'Card shows exact limitation');
  phase='isolate';await page.locator('#bIso').click();await close();
  check(await page.evaluate(id=>__recoverySnapshot().items.filter(m=>m.visible).every(m=>m.id===id),spec.id),'Isolation only chosen muscle');
  await page.waitForFunction(()=>__recoverySnapshot().idle);
  const point=await page.evaluate(id=>__recoveryRay.clickPoint(id),spec.id);check(!!point,'Visible raycast target');
  const parity=await page.evaluate(p=>__recoveryRay.compare(p),point);check(parity.rays.length===10,'Ten BVH/native rays agree including faceIndex');
  await page.mouse.click(point.x,point.y);check(await page.evaluate(()=>__recoverySnapshot().selection)===spec.id,'Real canvas click selects ID');
  await card();await page.locator('#bIso').click();await close();
  phase='sides';if(width===390)await page.locator('#bOptions').click();
  for(const side of ['right','left','both']){await page.locator(`[data-side-view="${side}"]`).click();check(await page.evaluate(side=>__recoverySnapshot().items.filter(m=>m.visible&&['left','right'].includes(m.side)).every(m=>side==='both'||m.side===side),side),'Side '+side);}
  const context=page.locator('#bContext');if(await context.getAttribute('aria-pressed')==='false')await context.click();
  check(await page.evaluate(()=>__recoverySnapshot().items.some(m=>m.visible&&m.opacity.some(x=>x<1))),'Transparent context');
  await close();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');check(!errors.length,'No page errors');
  phase='screenshot';await page.screenshot({path:run+'/recovery-trial-'+width+'.png',timeout:5000});
  return {status:'passed',width,checks,errors,parity,productionModified:false,anatomicalAdmission:false};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('Trial exceeded 45 seconds; test page closed'));},45000);})]);}
 catch(e){return {status:'failed',phase,width,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);}
}
for(const width of [1280,390])await fs.writeFile(run+'/mcp-recovery-trial-'+width+'.js',`async(page)=>await (${review.toString()})(page,${JSON.stringify({width,run,probe,spec})})`,{flag:'wx'});
console.log(run);
