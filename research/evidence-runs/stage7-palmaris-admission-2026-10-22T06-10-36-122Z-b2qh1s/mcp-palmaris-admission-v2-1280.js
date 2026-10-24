async(page)=>await (async function review(page,{width,run,probe,revision}){
 const checks=[],errors=[];let timer;
 const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
 const onError=e=>errors.push(String(e));page.on('pageerror',onError);page.setDefaultTimeout(5000);
 const close=async()=>{for(const id of ['#closeMobileCard','#closeOptions'])if(await page.locator(id).isVisible())await page.locator(id).click();};
 const job=async()=>{
  await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/trial.html*',async r=>{const res=await r.fetch();await r.fulfill({response:res,body:(await res.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8785/trial.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded',timeout:12000});
  await page.waitForFunction(()=>window.__palmarisTrialReady);
  check(await page.evaluate(()=>ATLAS.muscles.palmaris_brevis.modelStatus)==='technical_prototype_not_admitted','Test status retained');
  check((await page.locator('#trialBanner').innerText()).includes('без анатомического допуска'),'Persistent unadmitted notice');
  check(await page.evaluate(()=>__pbSnapshot().items.some(m=>m.id==='palmaris_brevis'&&m.bvh)),'Saved GLB loaded with BVH');
  await close();await page.locator('#bList').click();await page.locator('#q').fill('короткая ладонная');
  check(await page.locator('#dlist [data-id="palmaris_brevis"]').count()===1,'Single searchable PB ID');
  await page.locator('#dlist [data-id="palmaris_brevis"]').click();
  if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();
  check((await page.locator('#sheet').innerText()).includes('Границы, глубина и прикрепления не подтверждены'),'Card limitations visible');
  await page.locator('#bIso').click();await close();
  check(await page.evaluate(()=>__pbSnapshot().items.filter(m=>m.visible).every(m=>m.id==='palmaris_brevis')),'Isolation');
  if(width===390)await page.locator('#mobileCard').click();await page.locator('#bIso').click();await close();
  if(width===390)await page.locator('#bOptions').click();
  for(const side of ['left','right','both']){
   await page.locator(`[data-side-view="${side}"]`).click();
   check(await page.evaluate(side=>__pbSnapshot().items.filter(m=>m.visible&&['left','right'].includes(m.side)).every(m=>side==='both'||m.side===side),side),'Side '+side);
  }
  const context=page.locator('#bContext');if(await context.getAttribute('aria-pressed')==='false')await context.click();
  check(await page.evaluate(()=>__pbSnapshot().items.some(m=>m.visible&&m.id!=='palmaris_brevis'&&m.opacity.some(x=>x<1))),'Transparent context');
  await close();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
  check(!errors.length,'No page errors');
  await page.screenshot({path:run+'/palmaris-admission-'+revision+'-'+width+'.png',timeout:5000});
  return {status:'passed',width,checks,errors,productionModified:false,anatomicalAdmission:false};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('Admission smoke exceeded 30 seconds; test page closed'));},30000);})]);}
 catch(e){return {status:'failed',width,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);}
})(page,{"width":1280,"run":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage7-palmaris-admission-2026-10-22T06-10-36-122Z-b2qh1s","probe":"window.__pbCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\nwindow.__pbSnapshot=()=>({selection:state.sel,isolate:state.isolate,side:curSide(),items:[...structs.values()].map(s=>({id:s.id,side:s.side,visible:s.meshes.some(m=>m.visible),bvh:s.meshes.every(m=>!!m.geometry.boundsTree),opacity:s.meshes.map(m=>m.material.opacity)}))});","revision":"v2"})