async(page)=>(async function browser(page,{width,theme,shot,probe}){
 const check=(v,m)=>{if(!v)throw Error(m);};let phase='start';const errors=[];
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(8000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  phase='load';await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(()=>{window.__thoraxReady=false;__atlas.enterSection('trunk').then(ok=>window.__thoraxReady=ok);});
  await page.waitForFunction(()=>window.__thoraxReady,undefined,{timeout:30000});
  const rows=await page.evaluate(()=>ATLAS.pins.filter(p=>p.id.startsWith('thorax_thoracic_')||p.id.startsWith('shared_thorax_')||p.id.startsWith('extra_thoracic_')).map(p=>({id:p.id,b:p.b,kind:p.geometryKind,p:!!p.p,bones:p.relations?.map(r=>r.bone)||[p.b]})));
  check(rows.length===242,'Expected 242 vertebral batch cards');
  const seen=new Set();const sampled=rows.filter(p=>{if(p.id.startsWith('extra_'))return true;if(p.id.startsWith('shared_'))return /_(c7_t1|t5_t6|t11_t12)_/.test(p.id);const code=p.id.slice(p.id.indexOf('_A02'));if(seen.has(code))return false;seen.add(code);return true;});
  phase='all-types';const typeChecks=await page.evaluate(rows=>{
   const results=[];for(const p of rows){__atlas.goTo(p.b);__atlas.activatePin(p.id);const el=document.querySelector('.pinbox .landmark-geometry');if(el?.dataset.geometryKind!==p.kind)throw Error('Card kind '+p.id);results.push(p.id);}return results.length;
  },sampled);
  phase='unlocated-requirements';const requirements=await page.evaluate(rows=>{
   let count=0;for(const p of rows.filter(p=>!p.p)){__atlas.goTo(p.b);__atlas.activatePin(p.id);const source=ATLAS.pins.find(r=>r.id===p.id);if(!document.querySelector('.pinbox')?.textContent.includes(source.geometryRequirements.neededEvidence))throw Error('Missing requirements '+p.id);count++;}return count;
  },sampled);check(requirements>0,'Explicit limitations in representative cards');
  phase='bone-cards';const boneChecks=[];
  for(const b of [...new Set(rows.map(p=>p.b))]){
   await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();
   const row=rows.find(p=>p.b===b&&p.p);const chip=page.locator('#sheet [data-pinid="'+row.id+'"]');check(await chip.count()===1,'Single original chip');await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===row.id,'Original pin selected');boneChecks.push(b);
  }
  phase='new-cards';let edges=0;
  for(const p of sampled.filter(p=>!p.id.startsWith('thorax_thoracic_'))){
   for(const b of p.bones){
    await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();
    const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');check(await chip.count()===1,'Canonical card '+p.id);await chip.click();await card();
    check(await page.evaluate(()=>__atlas.state.pin)===p.id,'New pin selected');check(await page.locator('.pin[data-pinid="'+p.id+'"]').count()===0,'No invented marker');
    if(p.bones.length>1){const other=p.bones.find(x=>x!==b);await page.locator('.pinbox [data-gobone="'+other+'"]').click();await page.waitForFunction(({other,id})=>__atlas.state.sel===other&&__atlas.state.pin===id,{other,id:p.id});edges++;}
   }
  }
  phase='search';await close();await page.locator('#bList').click();await page.locator('#q').fill('A02.2.01.008');
  check(await page.locator('#dlist [data-pinjump^="shared_thorax_"]').count()===24,'24 unique shared results');
  await page.locator('#dlist [data-pinjump="shared_thorax_intervertebral_t5_t6_right"]').click();await card();
  phase='isolation';await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['thoracic_5','thoracic_6']),'Both boundary contributors isolated');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Both contributors transparent');
  await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='canvas';await page.evaluate(()=>{__atlas.activatePin(null);__atlas.goTo('thoracic_5');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('thoracic_5'));check(target,'Visible canvas point for atlas');await page.mouse.click(target.x,target.y);
  check(await page.evaluate(()=>__atlas.state.sel)==='thoracic_5','Real canvas ray selection');await close();
  phase='bvh';await page.waitForTimeout(800);const ray=await page.evaluate(()=>__thoraxCheck.compare(__thoraxCheck.clickPoint('thoracic_5')));check(ray.bvh>0,'BVH present');check(ray.rays.some(r=>r.hits>0),'Nonempty ray coverage');
  check(await page.evaluate(()=>__thoraxCheck.snapshot().cut)===false,'Skull-only clipping inactive in neck');
  phase='screenshot';check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');check(errors.length===0,'Console errors');await card();
  const nonce=await page.evaluate(()=>crypto.randomUUID());const screenshot=shot+'-'+nonce+'.png';await page.screenshot({path:screenshot});
  return {status:'passed',width,theme,typeChecks,boneChecks,requirements,catalogueNewCards:30,newCardsClicked:12,sharedEdges:edges,searchResults:24,ray,errors,screenshot,anatomicalAcceptance:false,clipping:'Not supported for thorax; existing skull implementation unchanged'};
 }catch(e){return {status:'failed',phase,width,theme,error:String(e),errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
})(page,{"width":390,"theme":"light","shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-thorax-mcp-2026-10-18T14-17-43-850Z-Di4ew8\\thorax","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})