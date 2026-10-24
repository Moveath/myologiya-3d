import fs from 'node:fs/promises';
import path from 'node:path';
const run=path.resolve(process.argv[2]);
const prior=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=prior.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__omCheck').replaceAll('\\n','\n')+
`window.__omIdle=()=>!tween;window.__omSnapshot=()=>({selection:state.sel,part:state.selPart,isolate:state.isolate,side:curSide(),items:[...structs.values()].map(s=>({id:s.id,side:s.side,visible:s.meshes.some(m=>m.visible),bvh:s.meshes.every(m=>!!m.geometry.boundsTree),opacity:s.meshes.map(m=>m.material.opacity)}))});`;
async function review(page,{width,run,probe}){
 const checks=[],errors=[];let timer;
 const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const error=e=>errors.push(String(e));page.on('pageerror',error);page.setDefaultTimeout(5000);
 const close=async()=>{for(const id of ['#closeMobileCard','#closeOptions'])if(await page.locator(id).isVisible())await page.locator(id).click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();};
 const job=async()=>{
  await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8785/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:12000});
  await page.waitForFunction(()=>window.__ready);await page.evaluate(async()=>{await __atlas.enterSection('neck');__atlas.setSide('both');});
  await close();if(width===390)await page.locator('#bOptions').click();await page.locator('[data-peel="0"]').click();
  if(await page.locator('#bMuscleBones').getAttribute('aria-pressed')==='true')await page.locator('#bMuscleBones').click();
  if(await page.locator('#bContext').getAttribute('aria-pressed')==='false')await page.locator('#bContext').click();await close();
  for(const side of ['right','left']){
   const id='omohyoid_'+side;await close();await page.locator('#bList').click();await page.locator('#q').fill('omohyoideus');
   check(await page.locator('#dlist [data-id="'+id+'"]').count()>=1,'Search '+side);
   await page.locator('#dlist .item[data-id="'+id+'"]:not([data-part])').click();await card();
   for(const part of ['superior','inferior']){
    await page.locator('#sheet [data-part="'+part+'"]').click();
    check(await page.evaluate(([id,p])=>__omSnapshot().selection===id&&__omSnapshot().part===p&&ATLAS.muscles[id].parts[p].noModel,[id,part]),'Stable noModel part '+side+'/'+part);
    check((await page.locator('#sheet').innerText()).includes('не выделена отдельной геометрией'),'No false part geometry '+side+'/'+part);
   }
   await page.locator('#sheet [data-part=""]').click();await page.locator('#bIso').click();await close();await page.waitForFunction(()=>__omIdle());
   check(await page.evaluate(id=>__omSnapshot().items.filter(m=>m.visible).every(m=>m.id===id),id),'Isolate whole '+side);
   const point=await page.evaluate(id=>__omCheck.clickPoint(id),id);check(!!point,'Canvas point '+side);
   const ray=await page.evaluate(p=>__omCheck.compare(p),point);check(ray.rays.length===10&&ray.bvh>0,'Native/BVH '+side);
   await page.mouse.click(point.x,point.y);check(await page.evaluate(id=>__omSnapshot().selection===id,id),'Real canvas click '+side);
   await card();await page.locator('#bIso').click();await close();
  }
  if(width===390)await page.locator('#bOptions').click();
  for(const side of ['right','left','both']){
   await page.locator(`[data-side-view="${side}"]`).click();check(await page.evaluate(side=>__omSnapshot().items.filter(m=>m.visible&&['left','right'].includes(m.side)).every(m=>side==='both'||m.side===side),side),'Side '+side);
  }
  await page.evaluate(()=>__atlas.goTo('omohyoid_left'));await close();
  check(await page.evaluate(()=>__omSnapshot().items.some(m=>m.visible&&m.id!=='omohyoid_left'&&m.opacity.some(x=>x<1))),'Transparent context');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');check(!errors.length,'No page errors');
  await page.screenshot({path:run+'/omohyoid-'+width+'.png',timeout:5000});return {status:'passed',width,checks,errors,anatomicalMasks:0};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('Omohyoid review exceeded 40 seconds; test page closed'));},40000);})]);}
 catch(e){return {status:'failed',width,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',error);}
}
for(const width of [1280,390])await fs.writeFile(run+'/mcp-omohyoid-'+width+'.js',`async(page)=>await (${review.toString()})(page,${JSON.stringify({width,run,probe})})`,{flag:'wx'});
console.log(run);
