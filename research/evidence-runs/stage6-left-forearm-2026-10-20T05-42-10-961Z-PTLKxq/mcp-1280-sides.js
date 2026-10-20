async(page)=>(async function exercise(page,{width,phase,dir,probe}){
 const checks=[],errors=[];let timer;
 const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error'&&!m.text().includes('favicon'))errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);
 page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(20000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{
  if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();
 };
 const side=async value=>{
  await close();
  if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();
  await page.locator('[data-side-view="'+value+'"]').click();
  if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
 };
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});
   await page.setViewportSize({width,height:width===390?844:900});
   await page.emulateMedia({colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/stage6-trial/local.html*',async r=>{
    const response=await r.fetch();
    await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});
   });
   await page.goto('http://127.0.0.1:8784/stage6-trial/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>localStorage.removeItem('myo3d'));await page.reload({waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('radius_left');});
   check(await page.locator('#trialNotice').isVisible(),'Explicit trial banner');
   check(await page.evaluate(()=>__forearmCheck.snapshot().visible.includes('radius_left')&&__forearmCheck.snapshot().visible.includes('ulna_left')),'Both trial models loaded');
  }else if(phase==='sides'){
   await page.evaluate(()=>__atlas.setSub('forearm'));
   for(const s of ['both','right','left']){
    await side(s);
    const visible=await page.evaluate(()=>__forearmCheck.snapshot().visible);
    check(s==='both'?['radius','ulna','radius_left','ulna_left'].every(id=>visible.includes(id)):
     s==='left'?visible.includes('radius_left')&&visible.includes('ulna_left')&&!visible.some(id=>['radius','ulna','humerus','scapula','clavicle'].includes(id)):
     visible.includes('radius')&&visible.includes('ulna')&&!visible.some(id=>id.endsWith('_left')),'Consistent side '+s);
   }
   check((await page.locator('#modelCoverage').textContent()).includes('кист'),'Missing left hand remains explicit');
   await page.screenshot({path:dir+'/ui-'+width+'-sides.png'});
  }else if(phase==='cards'){
   await side('left');
   for(const id of ['radius_left','ulna_left']){
    await close();await page.locator('#bList').click();
    await page.locator('#q').fill(id==='radius_left'?'Левая лучевая кость':'Левая локтевая кость');
    await page.locator('#dlist [data-id="'+id+'"]').first().click();
    check(await page.evaluate(()=>__atlas.state.sel)===id,'Search selects '+id);
    await card();
    check((await page.locator('#sheet').textContent()).includes('ПРОБНАЯ МОДЕЛЬ'),'Model qualification '+id);
    await page.locator('#bIso').click();
    check(JSON.stringify(await page.evaluate(()=>__forearmCheck.snapshot().visible))===JSON.stringify([id]),'Isolate '+id);
    await card();await page.locator('#bIso').click();
   }
   await close();
  }else if(phase==='joint'){
   await page.evaluate(()=>__atlas.activatePin('extra_radius_left_proximal_radioulnar_joint'));await card();
   check((await page.locator('.pinbox').textContent()).includes('лучелоктевой'),'Shared joint card');
   await page.locator('#bIso').click();
   check(JSON.stringify((await page.evaluate(()=>__forearmCheck.snapshot().visible)).sort())===JSON.stringify(['radius_left','ulna_left']),'Only linked trial bones isolated');
   await card();await page.locator('#bBoneXray').click();
   check((await page.evaluate(()=>__forearmCheck.snapshot().xray)).length===2,'Both linked bones transparent');
   await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
   check(await page.evaluate(()=>ATLAS.pins.filter(p=>p.b==='radius_left'||p.b==='ulna_left').every(p=>!p.p)),'No invented left pins');
   await page.screenshot({path:dir+'/ui-'+width+'-joint.png'});
  }else if(phase==='rays'){
   await close();await page.evaluate(()=>__atlas.goTo('radius_left'));await card();await page.locator('#bIso').click();await close();
   await page.waitForFunction(()=>!!__forearmCheck.clickPoint('radius_left'),undefined,{timeout:6000});
   const point=await page.evaluate(()=>__forearmCheck.clickPoint('radius_left'));
   const comparison=await page.evaluate(p=>__forearmCheck.compare(p),point);
   check(comparison.bvh>=1&&comparison.rays.some(r=>r.hits>0),'BVH/native matching hits and faceIndex');
   await page.mouse.click(point.x,point.y);
   check(await page.evaluate(()=>__atlas.state.sel)==='radius_left','Real canvas click selects left radius');
   await close();await card();await page.locator('#bIso').click();await close();
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
  }
  check(errors.length===0,'No page/console errors');
  return {status:'passed',width,phase,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline; this test page closed'));},40000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);page.off('console',onConsole);}
})(page,{"width":1280,"phase":"sides","dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-left-forearm-2026-10-20T05-42-10-961Z-PTLKxq","probe":"window.__forearmCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})