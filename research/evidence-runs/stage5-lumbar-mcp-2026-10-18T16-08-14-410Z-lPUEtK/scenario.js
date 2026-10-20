async(page)=>(async function browser(page,{width,theme,shot,probe}){
 const check=(v,m)=>{if(!v)throw Error(m);};let phase='start';const errors=[];
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(10000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('**/*.js',r=>r.continue());
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  phase='load';await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('lumbar_1');});
  const rows=await page.evaluate(()=>ATLAS.pins.filter(p=>/^(context_lumbar_|extra_lumbar_|shared_lumbar_)/.test(p.id)).map(p=>({id:p.id,b:p.b,kind:p.geometryKind,bones:p.relations?.map(r=>r.bone)||[p.b]})));
  check(rows.length===112,'112 reviewed lumbar rows');
  phase='types';const typeChecks=await page.evaluate(async rows=>{
   for(const p of rows){await __atlas.goTo(p.b);__atlas.activatePin(p.id);const el=document.querySelector('.pinbox .landmark-geometry');if(el?.dataset.geometryKind!==p.kind)throw Error('Kind '+p.id);const full=ATLAS.pins.find(q=>q.id===p.id);if(!document.querySelector('.pinbox')?.textContent.includes(full.geometryRequirements.neededEvidence))throw Error('Missing limitation '+p.id);}
   return rows.length;
  },rows);
  phase='shared-and-extra-clicks';let edges=0,extraClicks=0;
  for(const p of rows.filter(p=>!p.id.startsWith('context_'))){
   for(const b of p.bones){
    await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();
    const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');check(await chip.count()===1,'One chip '+p.id+' at '+b);await chip.click();await card();
    check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Click selected '+p.id);
    check(await page.locator('.pin[data-pinid="'+p.id+'"]').count()===0,'No invented marker');
    if(p.bones.length===2){const other=p.bones.find(x=>x!==b);await page.locator('.pinbox [data-gobone="'+other+'"]').click();await page.waitForFunction(({other,id})=>__atlas.state.sel===other&&__atlas.state.pin===id,{other,id:p.id});edges++;}else extraClicks++;
   }
  }
  phase='search';await page.evaluate(()=>__atlas.goTo('lumbar_3'));await close();await page.locator('#bList').click();await page.locator('#q').fill('Межсуставная часть');
  check(await page.locator('#dlist [data-pinjump^="extra_lumbar_"]').count()===10,'10 unique pars search results');
  await page.locator('#dlist [data-pinjump="extra_lumbar_3_pars_interarticularis_left"]').click();await card();
  await close();await page.locator('#bList').click();await page.locator('#q').fill('L5–S1');check(await page.locator('#dlist [data-pinjump^="shared_lumbar_"]').count()===2,'Two sided foramina');
  await page.locator('#dlist [data-pinjump="shared_lumbar_intervertebral_l5_s1_right"]').click();await card();
  phase='isolation';await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['lumbar_5','sacrum']),'L5 and sacrum isolation');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Both contributors transparent');
  await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='canvas';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('lumbar_3');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('lumbar_3'));check(target,'Lumbar canvas target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='lumbar_3','Real ray selection');await close();await page.waitForTimeout(500);
  phase='bvh';const ray=await page.evaluate(()=>__thoraxCheck.compare(__thoraxCheck.clickPoint('lumbar_3')));check(ray.bvh>0&&ray.rays.some(r=>r.hits),'BVH and nonempty rays');
  check(await page.evaluate(()=>__thoraxCheck.snapshot().cut)===false,'Skull cut inactive in lumbar region');
  await card();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');check(errors.length===0,'Console errors');
  const screenshot=shot+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';await page.screenshot({path:screenshot});
  return {status:'passed',width,theme,typeChecks,edges,extraClicks,ray,errors,screenshot,anatomicalAcceptance:false,clipping:'Lumbar clipping unsupported; unchanged skull clipping not rerun'};
 }catch(e){return {status:'failed',phase,width,theme,error:String(e),errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('**/*.js');await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
})(page,{"width":390,"theme":"light","shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-lumbar-mcp-2026-10-18T16-08-14-410Z-lPUEtK\\lumbar","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})