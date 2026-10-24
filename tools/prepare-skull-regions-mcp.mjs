import fs from 'node:fs/promises';
import path from 'node:path';
const run=path.resolve(process.argv[2]);
const revision=process.argv[3]||'v1';if(!/^v\d+$/.test(revision))throw Error('Invalid revision');
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
let probe=source.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__regionCheck').replaceAll('\\n','\n');
probe+=`window.__regionSnapshot=()=>({items:[...(anatomicalRegions?.items.values()||[])].map(x=>({id:x.def.id,bone:x.def.bone,visible:x.overlay.visible,parentVisible:x.mesh.visible,opacity:x.overlay.material.opacity,parentOpacity:x.mesh.material.opacity,bvh:!!x.mesh.geometry.boundsTree,overlayInPickables:pickables.includes(x.overlay),vertices:x.overlay.geometry.attributes.position.count})),failures:[...(anatomicalRegions?.failures||[])],drawCalls:renderer.info.render.calls,clip:renderer.clippingPlanes.length,pin:state.pin});\n`;
async function test(page,{width,phase,probe,run,revision}) {
 const checks=[],errors=[];let timer;
 const check=(v,name)=>{if(!v)throw Error(name);checks.push(name);};
 const onerror=e=>errors.push(String(e));page.on('pageerror',onerror);page.setDefaultTimeout(6500);
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const snapshot=()=>page.evaluate(()=>__regionSnapshot());
 const choose=async(bone,pin)=>{
  await close();await page.locator('#bList').click();await page.locator('#q').fill(await page.evaluate(id=>ATLAS.bones[id].ru,bone));
  await page.locator(`#dlist [data-id="${bone}"]`).first().click();await card();
  const chip=page.locator(`#sheet [data-pinid="${pin}"]`).first();
  await chip.evaluate(el=>{for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;});await chip.click();
 };
 const job=async()=>{
  if(phase==='setup') {
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:18000});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(async()=>{await __atlas.enterSection('head');__atlas.setSub('all');__atlas.setSide('both');});
   const s=await snapshot();check(s.items.length===1&&s.failures.length===2,'Accepted contour loaded; both drafts disabled');
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 noModel retained');
  } else if(phase.startsWith('region-')) {
   const id=+phase.slice(7),bone=['occipital','temporal_right','temporal_left'][id],pin='head_'+bone+'_'+(id?'A02_1_06_047':'A02_1_04_002');
   await choose(bone,pin);let s=await snapshot();check(s.pin===pin,'Real card selection');
   if(id>0) {
    check(s.items.every(x=>!x.visible),'Unaccepted process mask not shown');
    check(await page.locator('[data-region-status="unmapped"]').count()===1,'Process boundary limitation visible');
    check(await page.locator('[data-region-toggle]').count()===0,'Draft cannot be enabled through card');
    check(!errors.length,'No page errors');return {status:'passed',width,phase,checks,errors,snapshot:s};
   }
   // Persistent preference may be off after a previous run: use the visible control.
   if(await page.locator('[data-region-toggle]').getAttribute('aria-pressed')==='false')await page.locator('[data-region-toggle]').click();
   s=await snapshot();check(s.items.filter(x=>x.visible).length===1,'Only selected anatomical region');
   check(s.items.filter(x=>x.visible).every(x=>x.bvh&&!x.overlayInPickables),'BVH retained; overlay excluded from picking');
   const saved=await page.evaluate(()=>({pin:__atlas.state.pin,isolate:__atlas.state.isolate}));
   await page.locator('[data-region-toggle]').click();check((await snapshot()).items.every(x=>!x.visible),'Reset overlay');
   check(JSON.stringify(saved)===JSON.stringify(await page.evaluate(()=>({pin:__atlas.state.pin,isolate:__atlas.state.isolate}))),'Reset preserves selection/isolation');
   await page.locator('[data-region-toggle]').click();
   if(!await page.evaluate(()=>__atlas.state.isolate))await page.locator('#bIso').click();
   check(JSON.stringify(await page.evaluate(()=>__regionCheck.snapshot().visible))===JSON.stringify([bone]),'Bone isolation');
   await card();await page.locator('#bBoneXray').click();s=await snapshot();check(s.items.filter(x=>x.visible).every(x=>x.opacity===x.parentOpacity&&x.opacity<1),'Overlay respects transparency');
   await page.locator('#bBoneXray').click();await page.locator('[data-region-view]').click();await close();
   await page.waitForTimeout(250);check((await snapshot()).items.filter(x=>x.visible).length===1,'Overlay remains after view/card changes');
  } else if(phase==='capture') {
   await choose('occipital','head_occipital_A02_1_04_002');await page.locator('[data-region-view]').click();
   await close();await page.screenshot({path:run+'/'+revision+'-'+width+'-regions.png',timeout:12000});checks.push('Screenshot saved');
  } else if(phase==='pin-cut-shared') {
   const pin='head_occipital_A02_1_04_002';await choose('occipital',pin);await page.locator('[data-region-view]').click();await close();
   const marker=page.locator(`#pinLayer [data-pinid="${pin}"]`);
   await marker.click();check((await snapshot()).items.every(x=>!x.visible),'Real pin click clears overlay');
   await marker.click();check((await snapshot()).items.filter(x=>x.visible).length===1,'Real pin click restores overlay');
   if(width===390)await page.locator('#bOptions').click();
   await page.locator('#bHeadCut').click();await page.locator('#headCutAxis').selectOption('x');
   if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
   check((await snapshot()).clip===1,'Global clipping enabled for mesh and overlay');
   const point=await page.evaluate(()=>__regionCheck.clickPoint('occipital'));check(!!point,'Clipped mesh remains selectable');
   const ray=await page.evaluate(p=>__regionCheck.compare(p),point);check(ray.rays.some(r=>r.hits>0),'Clipped native/BVH face agreement');
   await page.screenshot({path:run+'/'+revision+'-'+width+'-contour-cut.png',timeout:10000});
   if(width===390)await page.locator('#bOptions').click();await page.locator('#bHeadCut').click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
   await choose('temporal_right','shared_jugular_foramen_right');check((await snapshot()).items.every(x=>!x.visible),'Unconfirmed jugular contour not invented');
   await page.locator('#bIso').click();await card();await page.locator('[data-gobone="occipital"]').click();
   check((await snapshot()).pin==='shared_jugular_foramen_right','Shared card keeps stable pin ID');
   const visible=await page.evaluate(()=>__regionCheck.snapshot().visible);check(visible.includes('occipital')&&visible.includes('temporal_right'),'Both contributing bones retained');
   check(await page.locator('[data-region-status="unmapped"]').count()===1,'Shared unsegmented structure explicitly labelled');
  } else if(phase==='regressions') {
   await close();const point=await page.evaluate(()=>__regionCheck.clickPoint('occipital'));check(!!point,'Visible mesh hit');
   const rays=await page.evaluate(p=>__regionCheck.compare(p),point);check(rays.bvh>0&&rays.rays.some(r=>r.hits>0),'BVH/native hits and original faceIndex agree');
   await page.mouse.click(point.x,point.y);check((await snapshot()).items.every(x=>!x.visible),'Mesh selection clears previous region');
   for(const side of ['right','left','both']) {
    if(width===390&&!await page.locator('[data-side-view="left"]').isVisible())await page.locator('#bOptions').click();
    await page.locator(`[data-side-view="${side}"]`).click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
    const v=await page.evaluate(()=>__regionCheck.snapshot().visible);check(!v.includes(side==='right'?'temporal_left':side==='left'?'temporal_right':'nonexistent'),'Side filter '+side);
   }
   await choose('occipital','head_occipital_A02_1_04_014');check((await snapshot()).items.every(x=>!x.visible),'Unsegmented articular surface has no fabricated overlay');
   check(await page.locator('[data-region-status="unmapped"]').count()===1,'Explicit unmapped notice');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
  }
  check(!errors.length,'No page errors');return {status:'passed',width,phase,checks,errors,snapshot:await snapshot()};
 };
 let result;
 try {result=await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000 ms deadline; only test page closed'));},35000);})]);}
 catch(e){result={status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onerror);}
 return result;
}
for(const width of [1280,390])for(const phase of ['setup','region-0','region-1','region-2','capture','regressions','pin-cut-shared'])await fs.writeFile(path.join(run,`${revision}-${width}-${phase}.js`),`async(page)=>(${test.toString()})(page,${JSON.stringify({width,phase,probe,run,revision})})`,{flag:'wx'});
