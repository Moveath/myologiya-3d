async(page)=>(async function test(page,{width,phase,probe,run,version}) {
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
   await page.screenshot({path:run+'/'+version+'-'+width+'-'+phase+'.png',timeout:10000});
  } else if(phase.startsWith('side-')) {
   const value=phase.slice(5);await side(value);check((await snap()).pin===null,'Side button retains existing overview reset');
   await choose('sphenoid','head_sphenoid_A02_1_05_036');const visible=(await snap()).items.filter(x=>x.visible);
   check(visible.length===(value==='both'?2:1)&&visible.every(x=>value==='both'||x.side===value),'Region side '+value);
  } else if(phase==='drafts') {
   await side('both');
   for(const bone of ['temporal_right','temporal_left']) {
    await choose(bone,'head_'+bone+'_A02_1_06_032');check((await snap()).items.every(x=>!x.visible),'Acoustic draft disabled '+bone);
    check(await page.locator('[data-region-status="unmapped"]').count()===1&&await page.locator('[data-region-toggle]').count()===0,'Explicit unaccepted boundary '+bone);
   }
   await choose('frontal','head_frontal_A02_1_03_023');check((await snap()).items.every(x=>!x.visible),'No arbitrary orbital surface mask');
   check(await page.locator('[data-region-status="unmapped"]').count()===1,'Frontal limitation visible');
  } else if(phase==='cuts-rays-shared') {
   const pin='head_sphenoid_A02_1_05_036';await side('both');await choose('sphenoid',pin);await page.locator('[data-region-view]').click();await close();
   const marker=page.locator(`#pinLayer [data-pinid="${pin}"]`);await marker.click();check((await snap()).items.every(x=>!x.visible),'Real marker clears regions');await marker.click();check((await snap()).items.filter(x=>x.visible).length===2,'Real marker restores regions');
   if(width===390)await page.locator('#bOptions').click();await page.locator('#bHeadCut').click();await page.locator('#headCutAxis').selectOption('x');if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
   check((await snap()).clip===1,'Mesh and contours share cut');
   const point=await page.evaluate(()=>__regionCheck.clickPoint('sphenoid'));check(!!point,'Clipped bone ray hit');const rays=await page.evaluate(p=>__regionCheck.compare(p),point);check(rays.rays.some(r=>r.hits>0),'Clipped BVH/native original faceIndex agreement');
   await page.screenshot({path:run+'/'+version+'-'+width+'-cut.png',timeout:10000});
   await page.mouse.click(point.x,point.y);check((await snap()).items.every(x=>!x.visible),'Real bone selection clears contours');
   if(width===390)await page.locator('#bOptions').click();await page.locator('#bHeadCut').click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
   await choose('sphenoid','shared_skull_083_right');check((await snap()).items.every(x=>!x.visible),'Partial sphenoid line not shown as complete shared boundary');
   check(await page.locator('[data-region-status="unmapped"]').count()===1,'Shared boundary still unconfirmed');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
  }
  check(!errors.length,'No page errors');return {status:'passed',width,phase,checks,errors,snapshot:await snap()};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000 ms deadline; test page closed'));},35000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',error);}
})(page,{"width":1280,"phase":"cuts-rays-shared","probe":"window.__regionCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\nwindow.__regionSnapshot=()=>({items:[...(anatomicalRegions?.items.values()||[])].map(x=>({id:x.def.id,side:x.def.side,bone:x.def.bone,visible:x.overlay.visible,opacity:x.overlay.material.opacity,parentOpacity:x.mesh.material.opacity,bvh:!!x.mesh.geometry.boundsTree,overlayInPickables:pickables.includes(x.overlay)})),failures:[...(anatomicalRegions?.failures||[])],clip:renderer.clippingPlanes.length,pin:state.pin,side:curSide(),revision:THREE.REVISION});\n","run":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-skull-regions-expansion-2026-10-21T08-15-07-836Z-IGp5Ll","version":"v3"})