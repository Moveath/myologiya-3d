async(page)=>(async function browser(page,{width,theme,shot,probe,url}){
 const checks=[],errors=[],snapshots={};let phase='start';
 const check=(v,m)=>{if(!v)throw Error(m);checks.push(m);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(15000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const option=async selector=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator(selector).click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const side=async value=>option('[data-side-view="'+value+'"]');
 const snap=async name=>{const s=await page.evaluate(()=>__uxCheck());snapshots[name]=s;check(!s.hiddenPickables,name+': hidden meshes not pickable');if(s.side!=='both')check(s.visible.every(o=>o.side!==(s.side==='left'?'right':'left')),name+': no opposite-side meshes');return s;};
 const find=async term=>{await close();if(!await page.locator('#q').isVisible())await page.locator('#bList').click();await page.locator('#q').fill(term);};
 try{
  await page.unrouteAll({behavior:'wait'});await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto(url+'?theme='+theme,{waitUntil:'domcontentloaded'});await page.evaluate(()=>localStorage.setItem('myo3d',JSON.stringify({peel:0,context:true,muscleBones:false,subs:{arm:'all'}})));await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);await page.evaluate(()=>__atlas.enterSection('arm'));
  phase='side-and-layers';
  for(const view of ['both','right','left']){
   await side(view);
   for(const layer of [0,1,2,3]){await option('[data-peel="'+layer+'"]');const s=await snap(view+'/'+layer);if(view==='both')check(s.visible.some(x=>x.id==='humerus')&&s.visible.some(x=>x.id==='humerus_left'),'Both humeri remain in layer '+layer);}
  }
  check(await page.locator('#modelCoverage').isVisible(),'Missing-model notice visible outside mobile options');check((await page.locator('#modelCoverage').textContent()).includes('Левая кисть и предплечье пока без 3D-моделей'),'Missing left geometry stated explicitly');
  await page.screenshot({path:shot+'-left.png'});
  phase='catalogue-side';await find('');
  const armIds=await page.locator('#dlist [data-id]').evaluateAll(nodes=>nodes.map(n=>n.dataset.id).filter(id=>window.ATLAS.bones[id]?.region==='arm'||window.ATLAS.muscles[id]?.region==='arm'));
  check(!armIds.includes('humerus')&&!armIds.includes('scapula')&&!armIds.includes('biceps_brachii'),'Unsearched left catalogue excludes right arm entries');
  phase='sesamoid-search';
  const typical=['sesamoid_mcp1_radial_right','sesamoid_mcp1_ulnar_right','sesamoid_mcp1_radial_left','sesamoid_mcp1_ulnar_left'];
  for(const term of ['сесамовидная','сесамоид','большой палец','сесамо']){
   await find(term);const first=await page.locator('#dlist button[data-id]').evaluateAll(nodes=>nodes.slice(0,4).map(n=>n.dataset.id));
   check(typical.every(id=>first.includes(id)),'Typical thumb sesamoids first: '+term);check(await page.locator('#dlist [data-primary-sesamoids] button').count()===4,'Exactly four primary side-specific cards: '+term);
  }
  check(await page.locator('#dlist [data-variant-results]').count()===1,'Variable sesamoids in separate final group');
  check((await page.locator('#dlist [data-variant-results]').textContent()).includes('не обязательные структуры'),'Variants labelled optional');
  await page.screenshot({path:shot+'-search.png'});
  await page.locator('#dlist [data-id="sesamoid_mcp1_radial_right"]').click();await card();let s=await snap('sesamoid-right');check(s.side==='right','Global search switches to result side');check((await page.locator('#sheet').textContent()).includes('Отдельной модели кости нет'),'Sesamoid noModel retained');check(await page.locator('#bIso').count()===0,'No fictitious isolation for absent model');
  phase='isolation-reset';await page.evaluate(()=>__atlas.goTo('biceps_brachii'));await card();await page.locator('#bIso').click();check((await snap('isolated')).visible.every(x=>x.id==='biceps_brachii'),'Strict muscle isolation');await side('both');s=await snap('after-both');check(s.isolate===null&&s.selected===null,'Side overview clears old selection and isolation');check(s.visible.some(x=>x.id==='humerus')&&s.visible.some(x=>x.id==='humerus_left'),'Both view restored after isolation');
  phase='trapezius';
  const muscles=await page.evaluate(()=>Object.entries(ATLAS.muscles).filter(([,m])=>m.lat==='m. trapezius').map(([id,m])=>({id,parts:Object.entries(m.parts).map(([key,p])=>({key,lat:p.lat}))})));
  check(muscles.length===5,'All five regional trapezius cards covered');
  for(const muscle of muscles){
   await close();await page.evaluate(id=>__atlas.goTo(id),muscle.id);await card();check(await page.locator('#sheet .lat').first().textContent()==='m. trapezius',muscle.id+': whole muscle Latin retained');
   for(const part of muscle.parts){await page.locator('#sheet [data-part="'+part.key+'"]').click();await card();check(await page.locator('#sheet .lat').first().textContent()==='m. trapezius, '+part.lat,muscle.id+'/'+part.key+': full part Latin');check((await page.locator('#sheet [data-selected-part]').textContent()).includes(part.lat),muscle.id+'/'+part.key+': selected part explained');}
  }
  await page.screenshot({path:shot+'-trapezius.png'});
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,'No page/console errors');
  return {status:'passed',width,theme,checks,snapshots,errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,checks,snapshots,errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
})(page,{"width":1280,"theme":"dark","shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\ux-catalogue-mcp-2026-10-19T07-34-40-469Z-IkG3XL\\ux","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\nwindow.__uxCheck=()=>({side:curSide(),selected:state.sel,isolate:state.isolate,visible:[...structs.values()].filter(s=>s.meshes.some(m=>m.visible)).map(s=>({id:s.id,kind:s.kind,side:s.side})),hiddenPickables:pickables.filter(m=>!m.visible).length});\n","url":"http://127.0.0.1:8000/local.html"})