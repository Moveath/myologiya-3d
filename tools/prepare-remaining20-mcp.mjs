// Bounded read-only browser regression: candidates must not leak into the atlas.
import fs from 'node:fs/promises';
import path from 'node:path';
const run=path.resolve(process.argv[2]);
const revision=process.argv[3]??'v3';
if(!/^v\d+$/.test(revision))throw Error('Invalid evidence revision');
const atlas=JSON.parse(await fs.readFile(path.join(run,'atlas-before.json'),'utf8'));
const missing=Object.keys(atlas.bones).filter(id=>atlas.bones[id].noModel);
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=source.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__remainingCheck').replaceAll('\\n','\n');
async function test(page,{run,width,region,phase,ids,probe,revision}){
 const checks=[],errors=[];let timer;
 const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
 const onerror=e=>errors.push(String(e));page.on('pageerror',onerror);
 page.setDefaultTimeout(4000);page.setDefaultNavigationTimeout(15000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const side=async s=>{await close();if(width===390&&!await page.locator('[data-side-view="left"]').isVisible())await page.locator('#bOptions').click();await page.locator(`[data-side-view="${s}"]`).click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const visible=()=>page.evaluate(()=>__remainingCheck.snapshot().visible);
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(async r=>{await __atlas.enterSection(r);__atlas.setSub('all');},region);
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 missing owners retained');
  }else if(phase==='working'){
   const id=region==='arm'?'metacarpal_2_left':'toe_prox_2_left',right=id.replace('_left','');
   for(const s of ['both','right','left']){await side(s);const v=await visible();check(s==='both'?v.includes(id)&&v.includes(right):s==='left'?v.includes(id)&&!v.includes(right):!v.includes(id)&&v.includes(right),'Side '+s);}
   await page.locator('#bList').click();await page.locator('#q').fill(await page.evaluate(id=>ATLAS.bones[id].ru,id));await page.locator(`#dlist [data-id="${id}"]`).first().click();
   check(await page.evaluate(()=>__atlas.state.sel)===id,'Search and selection');await card();await page.locator('#bIso').click();check(JSON.stringify(await visible())===JSON.stringify([id]),'Isolation');
   await close();await page.waitForTimeout(600);
   const p=await page.evaluate(id=>__remainingCheck.clickPoint(id),id);check(!!p,'Ray point');
   const ray=await page.evaluate(p=>__remainingCheck.compare(p),p);check(ray.bvh>0&&ray.rays.some(r=>r.hits>0),'BVH/native ray agreement');
   await page.mouse.click(p.x,p.y);check(await page.evaluate(()=>__atlas.state.sel)===id,'Canvas selection');
   const shared=await page.evaluate(id=>ATLAS.pins.find(p=>p.relations?.length>1&&p.relations.some(r=>r.bone===id))?.id,id);
   check(!!shared,'Shared card available');await page.evaluate(p=>__atlas.activatePin(p),shared);await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__remainingCheck.snapshot().xray)).includes(id),'Transparency');
   await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No overflow');
  }else if(phase==='capture'){
   await page.screenshot({path:run+`/ui-${revision}-${width}-${region}-${phase}.png`,timeout:10000});
   check(true,'Screenshot saved separately from functional checks');
  }else{
   for(const id of ids){await close();await side(id.endsWith('_right')?'right':'left');await page.evaluate(async id=>{await __atlas.goTo(id);},id);await card();
    check(await page.evaluate(()=>__atlas.state.sel)===id,'Card selection '+id);
    check(await page.evaluate(id=>ATLAS.bones[id].noModel&&!ATLAS.bones[id].modelFile,id),'No trial substituted '+id);
    check(!(await visible()).includes(id),'No unaccepted mesh '+id);
   }
  }
  check(!errors.length,'No JS errors');return {status:'passed',width,region,phase,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000ms deadline; page closed'));},35000);})]);}
 catch(e){return {status:'failed',width,region,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onerror);}
}
for(const width of [1280,390])for(const region of ['arm','leg']){
 const blocked=missing.filter(id=>region==='arm'?id.startsWith('metacarpal')||id.startsWith('sesamoid_mcp1'):!id.startsWith('metacarpal')&&!id.startsWith('sesamoid_mcp1'));
 const phases=[['setup',[]],['working',[]],['capture',[]]];for(let i=0;i<blocked.length;i+=4)phases.push(['blocked-'+i,blocked.slice(i,i+4)]);
 for(const [phase,ids] of phases)await fs.writeFile(path.join(run,`ui-${revision}-${width}-${region}-${phase}.js`),`async(page)=>(${test.toString()})(page,${JSON.stringify({run,width,region,phase,ids,probe,revision})})`,{flag:'wx'});
}
