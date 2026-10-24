import fs from 'node:fs/promises';
import path from 'node:path';
const run=path.resolve(process.argv[2]),version=process.argv[3]||'v1';
if(!/^v\d+$/.test(version))throw Error('Invalid version');
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
let probe=source.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__regionCheck').replaceAll('\\n','\n');
probe+=`window.__regionSnapshot=()=>({items:[...(anatomicalRegions?.items.values()||[])].map(x=>({id:x.def.id,side:x.def.side,bone:x.def.bone,visible:x.overlay.visible,opacity:x.overlay.material.opacity,parentOpacity:x.mesh.material.opacity,bvh:!!x.mesh.geometry.boundsTree,overlayInPickables:pickables.includes(x.overlay)})),failures:[...(anatomicalRegions?.failures||[])],clip:renderer.clippingPlanes.length,pin:state.pin,side:curSide(),revision:THREE.REVISION,moving:!!tween});\n`;
probe+=`window.__regionPerformance=()=>({calls:renderer.info.render.calls,geometries:renderer.info.memory.geometries});\n`;
async function test(page,{width,phase,probe,run,version}) {
 const checks=[],errors=[];let timer;const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const error=e=>errors.push(String(e));page.on('pageerror',error);page.setDefaultTimeout(5500);
 const snap=()=>page.evaluate(()=>__regionSnapshot());
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const choose=async(bone,pin)=>{
  await close();await page.locator('#bList').click();await page.locator('#q').fill(await page.evaluate(id=>ATLAS.bones[id].ru,bone));
  await page.locator(`#dlist [data-id="${bone}"]`).first().click();await card();
  const chip=page.locator(`#sheet [data-pinid="${pin}"]`).first();
  await chip.evaluate(el=>{for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;});await chip.click();
 };
 const side=async(value)=>{
  await close();if(!await page.locator(`[data-side-view="${value}"]`).isVisible())await page.locator('#bOptions').click();
  await page.locator(`[data-side-view="${value}"]`).click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
 };
 const job=async()=>{
  if(phase==='setup') {
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?expansion='+version+'&theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:18000});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(async()=>{await __atlas.enterSection('head');__atlas.setSub('all');__atlas.setSide('both');});
   const s=await snap();check(s.items.length===7&&s.failures.length===4,'Seven accepted contours, four disabled drafts');check(s.revision==='170','Three.js r170');
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 noModel retained');
  } else if(phase==='pipeline') {
   await side('both');await choose('sphenoid','head_sphenoid_A02_1_05_036');
   check((await page.locator('[data-region-status]').innerText()).includes('Предварительная учебная разметка'),'Educational scope explicitly visible');
   const admissions=await page.evaluate(async()=>{const m=await(await fetch('skull-region-masks.json')).json();return m.regions.map(r=>r.admission.level);});
   check(admissions.filter(x=>x==='educational').length===7&&admissions.filter(x=>x==='draft').length===4,'Explicit decision levels retained');
   if(await page.locator('[data-region-toggle]').getAttribute('aria-pressed')==='false')await page.locator('[data-region-toggle]').click();
   await page.locator('[data-region-view]').click();await close();await page.waitForFunction(()=>!__regionSnapshot().moving);
   await card();await page.waitForFunction(()=>!__regionSnapshot().moving);
   const stats=()=>page.evaluate(()=>__regionPerformance());
   const frames=()=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   await frames();const on=await stats();await page.locator('[data-region-toggle]').click();await frames();const off=await stats();
   await page.locator('[data-region-toggle]').click();await frames();const restored=await stats();
   check(on.geometries===off.geometries&&off.geometries===restored.geometries,'No geometry allocation on selection/reset');
   check(on.calls-off.calls>=0&&on.calls-off.calls<=2&&restored.calls===on.calls,'At most two visible contours add draw calls: '+JSON.stringify({on,off,restored}));
   const payload=await page.evaluate(async()=>{const r=await fetch('skull-region-masks.json');return (await r.arrayBuffer()).byteLength;});
   check(payload<100000,'Compact manifest below 100 kB; no mesh duplication');
   await page.screenshot({path:run+'/'+version+'-'+width+'-pipeline.png',timeout:10000});
   checks.push('Stats '+JSON.stringify({on,off,restored,payload}));
  } else if(phase.startsWith('sphenoid-')) {
   const code=phase.slice(9),pin='head_sphenoid_A02_1_05_'+code;
   await side('both');await choose('sphenoid',pin);check((await snap()).pin===pin,'Search and real card click');
   if(await page.locator('[data-region-toggle]').getAttribute('aria-pressed')==='false')await page.locator('[data-region-toggle]').click();
   let s=await snap();check(s.items.filter(x=>x.visible).length===2,'Both reviewed sides');
   check(s.items.filter(x=>x.visible).every(x=>x.bvh&&!x.overlayInPickables),'Source BVH retained; overlays excluded');
   await page.locator('[data-region-view]').click();
   const saved=await page.evaluate(()=>[__atlas.state.pin,__atlas.state.isolate]);await page.locator('[data-region-toggle]').click();
   check((await snap()).items.every(x=>!x.visible),'Highlight reset');check(JSON.stringify(saved)===JSON.stringify(await page.evaluate(()=>[__atlas.state.pin,__atlas.state.isolate])),'Reset preserves state');
   await page.locator('[data-region-toggle]').click();
   if(!await page.evaluate(()=>__atlas.state.isolate))await page.locator('#bIso').click();
   check(JSON.stringify(await page.evaluate(()=>__regionCheck.snapshot().visible))===JSON.stringify(['sphenoid']),'Isolation');
   await card();await page.locator('#bBoneXray').click();s=await snap();check(s.items.filter(x=>x.visible).every(x=>x.opacity===x.parentOpacity&&x.opacity<1),'Transparency inherited');await page.locator('#bBoneXray').click();
   await page.locator('[data-region-view]').click();await close();
   await page.waitForFunction(()=>!__regionSnapshot().moving);
   await page.screenshot({path:run+'/'+version+'-'+width+'-'+phase+'.png',timeout:10000});
  } else if(phase.startsWith('side-')) {
   const value=phase.slice(5);await side(value);check((await snap()).pin===null,'Side button retains existing overview reset');
   await choose('sphenoid','head_sphenoid_A02_1_05_036');const visible=(await snap()).items.filter(x=>x.visible);
   check(visible.length===(value==='both'?2:1)&&visible.every(x=>value==='both'||x.side===value),'Region side '+value);
  } else if(phase.startsWith('drafts')) {
   await side('both');
   for(const bone of ['temporal_right','temporal_left'].filter(b=>phase==='drafts'||b.endsWith(phase.slice(7)))) for(const code of ['032','047']) {
    await choose(bone,'head_'+bone+'_A02_1_06_'+code);check((await snap()).items.every(x=>!x.visible),'Draft disabled '+bone+' '+code);
    check(await page.locator('[data-region-status="unmapped"]').count()===1&&await page.locator('[data-region-toggle]').count()===0,'Explicit unaccepted boundary '+bone);
   }
   if(phase==='drafts'){
    await choose('frontal','head_frontal_A02_1_03_023');check((await snap()).items.every(x=>!x.visible),'No arbitrary orbital surface mask');
    check(await page.locator('[data-region-status="unmapped"]').count()===1,'Frontal limitation visible');
   }
  } else if(phase==='pin-click') {
   const pin='head_sphenoid_A02_1_05_036';await side('both');await choose('sphenoid',pin);
   if(!await page.evaluate(()=>__atlas.state.isolate))await page.locator('#bIso').click();await card();
   // The projection view frames the whole bone, and its pin may be outside the usable viewport.
   // Focus the actual pin through the existing UI before testing a real pointer click.
   await page.locator('#bFocus').click();await close();await page.waitForFunction(()=>!__regionSnapshot().moving);
   const marker=page.locator(`#pinLayer [data-pinid="${pin}"]`);await marker.click();check((await snap()).items.every(x=>!x.visible),'Real marker clears regions');
   // Clearing a pin can occlude its old surface marker. Restore via its real card, not force-click.
   await choose('sphenoid',pin);check((await snap()).items.filter(x=>x.visible).length===2,'Real card restores regions');
  } else if(phase==='cuts-rays-shared') {
   await side('both');await choose('sphenoid','head_sphenoid_A02_1_05_036');
   if(!await page.evaluate(()=>__atlas.state.isolate))await page.locator('#bIso').click();await card();
   await page.locator('[data-region-view]').click();await close();await page.waitForFunction(()=>!__regionSnapshot().moving);
   if(width===390)await page.locator('#bOptions').click();await page.locator('#bHeadCut').click();await page.locator('#headCutAxis').selectOption('x');if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
   check((await snap()).clip===1,'Mesh and contours share cut');
   const point=await page.evaluate(()=>__regionCheck.clickPoint('sphenoid'));check(!!point,'Clipped bone ray hit');const rays=await page.evaluate(p=>__regionCheck.compare(p),point);check(rays.rays.some(r=>r.hits>0),'Clipped BVH/native original faceIndex agreement');
   await page.screenshot({path:run+'/'+version+'-'+width+'-cut.png',timeout:10000});
   await page.mouse.click(point.x,point.y);check((await snap()).items.every(x=>!x.visible),'Real bone selection clears contours');
   if(width===390)await page.locator('#bOptions').click();await page.locator('#bHeadCut').click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
  } else if(phase==='shared') {
   await side('both');await choose('sphenoid','shared_skull_083_right');check((await snap()).items.every(x=>!x.visible),'Partial sphenoid line not shown as complete shared boundary');
   check(await page.locator('[data-region-status="unmapped"]').count()===1,'Shared boundary still unconfirmed');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
  }
  check(!errors.length,'No page errors');return {status:'passed',width,phase,checks,errors,snapshot:await snap()};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000 ms deadline; test page closed'));},35000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',error);}
}
for(const width of [1280,390])for(const phase of ['setup','pipeline','sphenoid-036','sphenoid-035','sphenoid-023','side-right','side-left','side-both','drafts','drafts-right','drafts-left','pin-click','cuts-rays-shared','shared'])await fs.writeFile(path.join(run,`${version}-${width}-${phase}.js`),`async(page)=>(${test.toString()})(page,${JSON.stringify({width,phase,probe,run,version})})`,{flag:'wx'});
