async(page)=>(async function test(page,{width,phase,probe,run,revision}) {
 const fs=await import('node:fs/promises');const checks=[],errors=[];let timer;
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
   const s=await snapshot();check(s.items.length===3&&!s.failures.length,'All three source-bound annotations loaded');
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 noModel retained');
  } else if(phase.startsWith('region-')) {
   const id=+phase.slice(7),bone=['occipital','temporal_right','temporal_left'][id],pin='head_'+bone+'_'+(id?'A02_1_06_047':'A02_1_04_002');
   await choose(bone,pin);let s=await snapshot();check(s.pin===pin,'Real card selection');
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
   await close();await page.screenshot({path:run+'/'+revision+'-'+width+'-regions.png',timeout:12000});checks.push('Screenshot saved');
  } else if(phase==='regressions') {
   await close();const point=await page.evaluate(()=>__regionCheck.clickPoint('temporal_left'));check(!!point,'Visible mesh hit');
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
 await fs.writeFile(run+'/'+revision+'-'+width+'-'+phase+'.json',JSON.stringify(result,null,2),{flag:'wx'});return result;
})(page,{"width":390,"phase":"region-1","probe":"window.__regionCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\nwindow.__regionSnapshot=()=>({items:[...(anatomicalRegions?.items.values()||[])].map(x=>({id:x.def.id,bone:x.def.bone,visible:x.overlay.visible,parentVisible:x.mesh.visible,opacity:x.overlay.material.opacity,parentOpacity:x.mesh.material.opacity,bvh:!!x.mesh.geometry.boundsTree,overlayInPickables:pickables.includes(x.overlay),vertices:x.overlay.geometry.attributes.position.count})),failures:[...(anatomicalRegions?.failures||[])],drawCalls:renderer.info.render.calls,clip:renderer.clippingPlanes.length,pin:state.pin});\n","run":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-skull-regions-2026-10-21T07-30-30-791Z-I2eT8L","revision":"v2"})