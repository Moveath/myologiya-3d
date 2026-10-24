import fs from 'node:fs/promises';
import path from 'node:path';
const run=path.resolve(process.argv[2]),revision=process.argv[3]||'v1';
if(!/^v\d+$/.test(revision))throw Error('Invalid revision');
const prior=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const inherited=prior.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__neckCheck').replaceAll('\\n','\n');
const probe=inherited+`window.__neckIdle=()=>!tween;window.__neckSnapshot=()=>({selection:state.sel,isolate:state.isolate,side:curSide(),items:[...structs.values()].map(s=>({id:s.id,side:s.side,visible:s.meshes.some(m=>m.visible),bvh:s.meshes.every(m=>!!m.geometry.boundsTree),opacity:s.meshes.map(m=>m.material.opacity)}))});\n`;
async function test(page,{run,revision,width,phase,probe}){
 const checks=[],errors=[];let timer;
 const name=`neck-${revision}-${width}-${phase}`;
 const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const onError=e=>errors.push(String(e));page.on('pageerror',onError);page.setDefaultTimeout(6000);
 const snap=()=>page.evaluate(()=>__neckSnapshot());
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();};
 const controls=async()=>{await close();if(width===390&&!(await page.locator('[data-side-view="both"]').isVisible()))await page.locator('#bOptions').click();};
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?stage7=neck&theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:15000});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(async()=>{await __atlas.enterSection('neck');__atlas.setSide('both');});
   await controls();await page.locator('[data-peel="0"]').click();
   if(await page.locator('#bMuscleBones').getAttribute('aria-pressed')==='true')await page.locator('#bMuscleBones').click();
   if(await page.locator('#bContext').getAttribute('aria-pressed')==='false')await page.locator('#bContext').click();
   const s=await snap();check(s.items.some(m=>m.id==='interspinales_cervicis_right'&&m.visible&&m.bvh),'Right partial model loaded with BVH');
   check(!s.items.some(m=>m.id==='interspinales_cervicis_left'),'Left model not fabricated');
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 bone blockers retained');
  }else if(phase==='cards'){
   await close();await page.locator('#bList').click();await page.locator('#q').fill('межостистые мышцы шеи');
   check(await page.locator('#dlist [data-id="interspinales_cervicis_right"]').count()===1,'Right search entry');
   check(await page.locator('#dlist [data-id="interspinales_cervicis_left"]').count()===1,'Left noModel search entry');
   await page.locator('#dlist [data-id="interspinales_cervicis_right"]').click();await card();
   check((await page.locator('#sheet').innerText()).includes('C7–T1 отсутствует'),'Explicit incomplete coverage');
   check((await page.locator('#sheet').innerText()).includes('mm. interspinales cervicis'),'Latin name');
   await page.locator('#bIso').click();await close();await page.waitForFunction(()=>__neckIdle());
   let s=await snap();check(s.isolate==='interspinales_cervicis_right'&&s.items.filter(m=>m.visible).every(m=>m.id===s.isolate),'Isolation');
   const target=await page.evaluate(()=>__neckCheck.clickPoint('interspinales_cervicis_right'));check(!!target,'Visible target');
   const r=await page.evaluate(p=>__neckCheck.compare(p),target);check(r.rays.length===10&&r.bvh>0,'Native/BVH rays');
   await page.mouse.click(target.x,target.y);check((await snap()).selection==='interspinales_cervicis_right','Real canvas selection');
   await card();await page.locator('#bIso').click();await card();
   await page.locator('#sheet [data-go="interspinales_cervicis_left"]').click();await card();
   check((await snap()).selection==='interspinales_cervicis_left','Related left card');
   check((await page.locator('#sheet').innerText()).includes('1,45 мм'),'Left limitation visible');
   check(await page.locator('#bIso').count()===0||!(await page.locator('#bIso').isEnabled()),'No fake isolation for absent model');
   await page.locator('#sheet [data-go="interspinales_cervicis_right"]').click();check((await snap()).selection==='interspinales_cervicis_right','Reverse relation');
  }else if(phase==='sides'){
   await controls();for(const side of ['right','left','both']){
    await page.locator(`[data-side-view="${side}"]`).click();const s=await snap();check(s.side===side,'Side '+side);
    check(s.items.filter(m=>m.visible&&['left','right'].includes(m.side)).every(m=>side==='both'||m.side===side),'No opposite leak '+side);
    check(s.items.some(m=>m.id==='interspinales_cervicis_right'&&m.visible)===(side!=='left'),'Right coverage '+side);
   }
   const s=await snap();check(s.items.some(m=>m.visible&&m.opacity.some(x=>x<1)),'Transparent context');
   const v=await page.locator('#bContext').getAttribute('aria-pressed');await page.locator('#bContext').click();check(await page.locator('#bContext').getAttribute('aria-pressed')!==v,'Context control');await page.locator('#bContext').click();
   await close();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
  }
  check(!errors.length,'No page errors');await page.screenshot({path:run+'/'+name+'.png'});
  return {status:'passed',width,phase,checks,errors};
 };
 let result;try{result=await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35 s phase deadline'));},35000);})]);}
 catch(e){result={status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);}
 return result;
}
for(const width of [1280,390])for(const phase of ['setup','cards','sides'])await fs.writeFile(run+`/mcp-neck-${revision}-${width}-${phase}.txt`,`async page=>(${test.toString()})(page,${JSON.stringify({run,revision,width,phase,probe})})`,{flag:'wx'});
