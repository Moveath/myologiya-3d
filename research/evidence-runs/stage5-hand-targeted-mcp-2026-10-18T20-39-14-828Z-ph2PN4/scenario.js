async(page)=>(async function browser(page,{width,theme,shot,probe}){
 const check=(v,m)=>{if(!v)throw Error(m);};const errors=[];let phase='load';
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(10000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const find=async term=>{await close();await page.locator('#bList').click();await page.locator('#q').fill(term);};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('metacarpal_1');});
  phase='left-search';const leftBones=await page.evaluate(()=>Object.entries(ATLAS.bones).filter(([id,b])=>b.sub==='hand'&&b.side==='left').map(([id,b])=>({id,ru:b.ru})));
  check(leftBones.length===29,'29 left bones');
  for(const b of leftBones){
   await find(b.ru);const item=page.locator('#dlist [data-id="'+b.id+'"]');check(await item.count()===1,'Unique left search '+b.id);check((await item.textContent()).includes('только карточка'),'NoModel search label');await item.click();await card();
   check(await page.evaluate(()=>__atlas.state.sel)===b.id,'Left selected');check((await page.locator('#sheet').textContent()).includes('Отдельной модели кости нет'),'NoModel notice');
   check(await page.locator('#bIso,#bHide,#bBoneXray,#bFocus').count()===0,'No false left mesh controls');
  }
  phase='targeted-cards';const cards=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>p.targetedHandReview||p.id.startsWith('extra_hand_midcarpal')||/^extra_hand_cmc[2-5]_joint$/.test(p.id)||p.id.startsWith('extra_hand_intermetacarpal_joint_'));
   for(const b of new Set(rows.map(p=>p.b))){await __atlas.goTo(b);for(const p of rows.filter(p=>p.b===b)){
    __atlas.activatePin(p.id);const el=document.querySelector('.pinbox');if(!el||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind)throw Error('Card '+p.id);
    if(!el.textContent.includes(p.modelNote))throw Error('Geometry limitation '+p.id);
    if(!p.p&&document.querySelector('.pin[data-pinid="'+p.id+'"]'))throw Error('Invented marker '+p.id);
   }}return rows.map(p=>p.id);
  });check(cards.length===209,'14 changed + 195 new records');
  phase='shared-membership';let edges=0;
  const shared=await page.evaluate(()=>ATLAS.pins.filter(p=>p.anatomicalEntity==='joint'&&(
   /^extra_hand_(midcarpal|cmc[2-5]|intermetacarpal)/.test(p.id)||['left_hand_extra_hand_radiocarpal_joint','left_hand_extra_hand_mcp1_joint','left_hand_extra_hand_midcarpal_joint'].includes(p.id)
  )).map(p=>({id:p.id,owners:p.relations.map(r=>r.bone)})));
  for(const p of shared)for(const b of p.owners){
   await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');check(await chip.count()===1,'Unique membership '+b+'/'+p.id);await chip.click();await card();check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Shared stable ID');edges++;
  }
  phase='left-shared-search';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('phalanx_prox_1_left');});await find('1 пястно-фаланговый сустав слева');
  const joint=page.locator('#dlist [data-pinjump="left_hand_extra_hand_mcp1_joint"]');check(await joint.count()===1,'Single left shared result');await joint.click();await card();
  check(await page.evaluate(()=>__atlas.state.sel)==='phalanx_prox_1_left','Left participant preserved');
  check(await page.locator('#bIso,#bBoneXray').count()===0,'All-left noModel no mesh actions');
  await page.locator('.pinbox [data-gobone="sesamoid_mcp1_radial_left"]').click();await card();
  check(await page.evaluate(()=>__atlas.state.pin)==='left_hand_extra_hand_mcp1_joint','Left sesamoid transition keeps joint');
  await page.locator('#sheet').evaluate(el=>el.scrollTop=0);await page.screenshot({path:shot+'-left.png',fullPage:false});
  phase='right-conditional-joint';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('metacarpal_4');__atlas.activatePin('extra_hand_cmc4_joint');});await card();
  await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['hamate','metacarpal_4']),'Conditional capitate not forced into joint');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Two confirmed component transparencies');
  await page.locator('#sheet').evaluate(el=>el.scrollTop=0);await page.screenshot({path:shot+'-right-joint.png',fullPage:false});
  phase='canvas';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('metacarpal_1');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('metacarpal_1'));check(target,'Canvas target');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='metacarpal_1','Real right bone hit');
  const bvh=await page.evaluate(target=>__thoraxCheck.compare(target),target);check(bvh.rays.length===10&&bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'BVH/native agreement');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,errors.join('\n'));
  return {status:'passed',width,theme,cardCount:cards.length,cards,leftSearchCount:leftBones.length,sharedEdges:edges,
   leftSharedSearch:true,leftSesamoidTransition:true,noModelControlsHidden:true,conditionalIsolation:true,conditionalTransparency:true,realCanvasClick:true,bvh,consoleErrors:errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,consoleErrors:errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
})(page,{"width":390,"theme":"light","shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-hand-targeted-mcp-2026-10-18T20-39-14-828Z-ph2PN4\\hand","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})