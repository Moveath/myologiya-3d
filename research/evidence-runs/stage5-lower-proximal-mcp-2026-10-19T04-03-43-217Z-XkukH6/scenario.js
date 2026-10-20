async(page)=>(async function browser(page,{width,theme,dir,probe}){
 const errors=[],checks=[];let phase='load';
 const check=(v,m)=>{if(!v)throw Error(m);checks.push(m);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(12000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const side=async value=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator('[data-side-view="'+value+'"]').click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>localStorage.removeItem('myo3d'));await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('femur');});
  phase='all-cards';const cards=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>p.lowerProximalReview);
   for(const b of new Set(rows.map(p=>p.b))){await __atlas.goTo(b);for(const p of rows.filter(p=>p.b===b)){
    __atlas.activatePin(p.id);const el=document.querySelector('.pinbox');
    if(!el?.textContent.includes(p.x)||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind)throw Error('Card '+p.id);
    if(!el.querySelector('[data-geometry-status="unverified_extent"]'))throw Error('Missing geometry limit '+p.id);
   }}return rows.length;
  });check(cards===173,'173 catalogue cards and representation limits');
  phase='shared';const joints=await page.evaluate(()=>ATLAS.pins.filter(p=>p.lowerProximalReview&&p.relations).map(p=>({id:p.id,owners:p.relations.map(r=>r.bone)})));let edges=0;
  for(const j of joints)for(const b of j.owners){await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();
   const chip=page.locator('#sheet [data-pinid="'+j.id+'"]');check(await chip.count()===1,'Single shared chip '+b+'/'+j.id);await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===j.id,'Shared selection '+b+'/'+j.id);check(await page.locator('.pin[data-pinid="'+j.id+'"]').count()===0,'No invented joint marker '+j.id);edges++;
  }check(edges===18,'18 shared links');
  phase='left-search';await close();await page.locator('#bList').click();await page.locator('#q').fill('Левая большеберцовая кость');
  const hit=page.locator('#dlist [data-id="tibia_left"]');check(await hit.count()===1,'One left tibia search result');await hit.click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='tibia_left','Search selects left tibia');
  check((await page.locator('#sheet').textContent()).includes('Подтверждённой левой модели'),'Missing geometry explicit');
  check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).every(id=>!['femur_left','tibia_left','fibula_left','patella_left'].includes(id)),'No invented left meshes');
  await page.screenshot({path:dir+'/left-no-model.png'});
  phase='right-isolation';await side('right');await page.evaluate(async()=>{await __atlas.goTo('tibia');__atlas.activatePin('extra_femur_knee_joint');});await card();await page.locator('#bIso').click();
  check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['femur','patella','tibia']),'Knee isolates three participants, excludes fibula');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===3,'Three participants transparent');
  await page.screenshot({path:dir+'/knee-shared.png'});await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='variant';await page.evaluate(async()=>{await __atlas.goTo('femur');__atlas.activatePin('fem_trochanter_tertius');});await card();
  check(await page.locator('.pin[data-pinid="fem_trochanter_tertius"]').count()===0,'Unverified third trochanter hidden');check((await page.locator('.pinbox').textContent()).includes('не установлено'),'Variant warning');
  phase='canvas';await page.evaluate(()=>__atlas.activatePin(null));await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('femur'));check(!!target,'Visible femur ray target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='femur','Real canvas click');
  const bvh=await page.evaluate(target=>__thoraxCheck.compare(target),target);check(bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'BVH/native faces and distances match on ten rays');
  check(await page.evaluate(()=>__thoraxCheck.snapshot().cut)===false,'Skull cuts inactive in leg');
  await side('left');check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).every(id=>!['femur','tibia','fibula','patella'].includes(id)),'Left view excludes right proximal bones');await side('both');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,'No console errors');
  return {status:'passed',width,theme,cards,sharedEdges:edges,checks,bvh,consoleErrors:errors};
 }catch(e){return {status:'failed',width,theme,phase,error:String(e),checks,consoleErrors:errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
})(page,{"width":1280,"theme":"light","dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-lower-proximal-mcp-2026-10-19T04-03-43-217Z-XkukH6","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})