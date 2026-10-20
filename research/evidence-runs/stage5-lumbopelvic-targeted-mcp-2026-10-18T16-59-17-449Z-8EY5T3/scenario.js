async(page)=>(async function browser(page,{width,theme,shot,probe}){
 const check=(v,m)=>{if(!v)throw Error(m);};const errors=[];let phase='load';
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(10000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('**/*.js',r=>r.continue());await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('hip_bone');});
  phase='targeted-cards';const cards=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>p.targetedReview?.source==='research/stage5-lumbopelvic-targeted-report-2026-10-18.md');
   for(const b of new Set(rows.map(p=>p.b))){await __atlas.goTo(b);for(const p of rows.filter(p=>p.b===b)){
    __atlas.activatePin(p.id);const el=document.querySelector('.pinbox');
    if(!el?.textContent.includes(p.x)||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind)throw Error('Card '+p.id);
   }}return rows.map(p=>p.id);
  });check(cards.length===31,'31 addressed cards');
  phase='shared';let edges=0;
  for(const b of ['hip_bone','hip_bone_left'])for(const owner of [b,'sacrum']){
   const id='extra_'+b+'_greater_sciatic_foramen';await page.evaluate(async owner=>{__atlas.activatePin(null);await __atlas.goTo(owner);},owner);await card();
   const chip=page.locator('#sheet [data-pinid="'+id+'"]');check(await chip.count()===1,'One shared chip');await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===id,'Shared selection');check(await page.locator('.pin[data-pinid="'+id+'"]').count()===0,'No invented marker');edges++;
  }
  phase='search';await close();await page.locator('#bList').click();await page.locator('#q').fill('Большое седалищное отверстие');
  check(await page.locator('#dlist [data-pinjump$="_greater_sciatic_foramen"]').count()===2,'Only two instances in search');
  await page.locator('#dlist [data-pinjump="extra_hip_bone_left_greater_sciatic_foramen"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='sacrum','Preserve participating selected bone after search');
  phase='isolation';await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['hip_bone_left','sacrum']),'Both participants isolated');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Both participants transparent');
  await page.screenshot({path:shot+'-shared.png',fullPage:false});await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='new-search';await close();await page.locator('#bList').click();await page.locator('#q').fill('Базивертебральные');
  check(await page.locator('#dlist [data-pinjump$="_basivertebral_foramina"]').count()===5,'Five grouped entries');
  await page.locator('#dlist [data-pinjump="extra_lumbar_3_basivertebral_foramina"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='lumbar_3','Search selects L3');
  await page.screenshot({path:shot+'-lumbar.png',fullPage:false});
  phase='canvas';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('hip_bone');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('hip_bone'));check(target,'Canvas target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='hip_bone','Real canvas selection');
  const bvh=await page.evaluate(target=>__thoraxCheck.compare(target),target);check(bvh.rays.length===10&&bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'BVH/native equality');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
  check(errors.length===0,errors.join('\n'));
  return {status:'passed',width,theme,cards,sharedEdges:edges,search:true,isolation:true,transparency:true,realCanvasClick:true,bvh,consoleErrors:errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,consoleErrors:errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
})(page,{"width":1280,"theme":"dark","shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-lumbopelvic-targeted-mcp-2026-10-18T16-59-17-449Z-8EY5T3\\targeted","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})