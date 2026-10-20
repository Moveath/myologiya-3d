async(page)=>(async function browser(page,{width,theme,dir,probe}){
 const errors=[],check=(v,m)=>{if(!v)throw Error(m);};let phase='load';
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(10000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 let result;
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('trunk');});
  const rows=await page.evaluate(()=>ATLAS.pins.filter(p=>/^thorax_(rib_|sternum_)/.test(p.id)||p.id.startsWith('extra_sternum_')||/^shared_thorax_(intercostal_|superior_aperture|inferior_aperture)/.test(p.id)).map(p=>({id:p.id,b:p.b,kind:p.geometryKind,located:!!p.p,bones:p.relations?.map(r=>r.bone)||[p.b]})));
  check(rows.length===294,'246 + 48 records');
  phase='types-and-limitations';const allTypes=await page.evaluate(rows=>{
   for(const p of rows){__atlas.goTo(p.b);__atlas.activatePin(p.id);const box=document.querySelector('.pinbox');if(box?.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.kind)throw Error('Kind '+p.id);
    const q=ATLAS.pins.find(q=>q.id===p.id);if(!box.textContent.includes(q.geometryRequirements.neededEvidence))throw Error('Limit '+p.id);
   }return rows.length;
  },rows);
  phase='original-bone-cards';let boneClicks=0;
  for(const b of [...new Set(rows.filter(p=>p.id.startsWith('thorax_')).map(p=>p.b))]){
   await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();
   const p=rows.find(p=>p.b===b&&p.located);const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');check(await chip.count()===1,'Own pin '+b);await chip.click();check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Original selection');boneClicks++;
  }
  phase='new-card-links';let newClicks=0,edges=0;
  for(const p of rows.filter(p=>!p.id.startsWith('thorax_')))for(const b of p.bones){
   await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},b);await card();const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');check(await chip.count()===1,'Canonical chip '+p.id);await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Added selected');check(await page.locator('.pin[data-pinid="'+p.id+'"]').count()===0,'No fabricated marker');newClicks++;
   if(p.bones.length>1){const other=p.bones.find(x=>x!==b);await page.locator('.pinbox [data-gobone="'+other+'"]').click();await page.waitForFunction(({other,id})=>__atlas.state.sel===other&&__atlas.state.pin===id,{other,id:p.id});edges++;}
  }
  phase='search';await close();await page.locator('#bList').click();await page.locator('#q').fill('A02.3.04.007');
  check(await page.locator('#dlist [data-pinjump^="shared_thorax_intercostal_"]').count()===22,'22 unique search results');
  await page.locator('#dlist [data-pinjump="shared_thorax_intercostal_5_right"]').click();await card();
  phase='isolation';await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['rib_5_right','rib_6_right']),'Two ribs isolate');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Two ribs transparent');await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='rib-ray';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('rib_5_right');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(600);
  const target=await page.evaluate(()=>__thoraxCheck.clickPoint('rib_5_right'));check(target,'Real rib canvas hit');const ribRay=await page.evaluate(p=>__thoraxCheck.compare(p),target);check(ribRay.bvh>0&&ribRay.rays.some(r=>r.hits),'Rib BVH nonempty');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)==='rib_5_right','Canvas selects rib');
  phase='image';await card();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No overflow');const screenshot=dir+'/ribs-'+width+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';await page.screenshot({path:screenshot});
  phase='region-clipping';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.enterSection('head');await __atlas.goTo('temporal_right');});await close();await page.waitForTimeout(500);
  const cuts=[];
  for(const axis of ['x','y','z'])for(const flip of [false,true]){
   await page.evaluate(({axis,flip})=>__ribsCut.set(true,axis,flip),{axis,flip});check((await page.evaluate(()=>__ribsCut.info())).active,'Cut active');
   const ray=await page.evaluate(()=>__thoraxCheck.compare({x:innerWidth*.5,y:innerHeight*.5}));cuts.push({axis,flip,...ray});
  }
  check(cuts.some(c=>c.rays.some(r=>r.hits>0)),'Clipping comparisons have actual intersections');
  await page.evaluate(async()=>{__ribsCut.set(false,'y',false);await __atlas.enterSection('neck');await __atlas.goTo('cervical_7');__atlas.activatePin('shared_thorax_intervertebral_c7_t1_right');});await card();
  await page.locator('.pinbox [data-gobone="thoracic_1"]').click();await page.waitForFunction(()=>__atlas.state.sel==='thoracic_1'&&__atlas.state.pin==='shared_thorax_intervertebral_c7_t1_right');
  check((await page.evaluate(()=>__thoraxCheck.snapshot())).cut===false,'Cut disabled outside head');check(errors.length===0,'No console errors');
  result={status:'passed',width,theme,allTypes,boneClicks,newClicks,sharedEdgeClicks:edges,searchResults:22,ribRay,cuts,regionTransition:true,errors,screenshot,anatomicalAcceptance:false};
 }catch(e){result={status:'failed',phase,width,theme,error:String(e),errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
 return result;
})(page,{"width":390,"theme":"light","dir":"C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-ribs-mcp-2026-10-18T14-50-24-737Z-Y0xLlh","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\nwindow.__ribsCut={set(active,axis,flip){state.headCut={active,axis,value:50,flip};updateHeadCut();applyVisibility();},info:()=>({active:headCutActive(),axis:state.headCut.axis,flip:state.headCut.flip})};\n"})