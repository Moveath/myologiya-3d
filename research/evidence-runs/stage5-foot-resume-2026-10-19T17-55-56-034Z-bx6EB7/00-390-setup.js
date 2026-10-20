async(page)=>(async function exercise(page,opt){
 const {phase,width,dir,ids=[],links=[],probe}=opt,checks=[],errors=[];let timer;
 const check=(v,m)=>{if(!v)throw Error(m);checks.push(m);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(6000);page.setDefaultNavigationTimeout(20000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{if(width===390&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();};
 const side=async value=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator('[data-side-view="'+value+'"]').click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const job=async()=>{
  if(phase==='setup'){
   await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>localStorage.removeItem('myo3d'));await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready,undefined,{timeout:20000});
   await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('talus');});
   check(await page.evaluate(()=>ATLAS.pins.filter(p=>p.footReview).length)===299,'Final 299 records loaded');
  }else if(phase==='cards'){
   for(const id of ids){
    await page.evaluate(async id=>{const p=ATLAS.pins.find(p=>p.id===id);await __atlas.goTo(p.b);__atlas.activatePin(id);const el=document.querySelector('.pinbox');
     if(!el?.textContent.includes(p.x)||el.querySelector('.landmark-geometry')?.dataset.geometryKind!==p.geometryKind||!el.querySelector('[data-geometry-status="unverified_extent"]'))throw Error('Card/limit '+id);
    },id);checks.push(id);
   }
  }else if(phase==='links'){
   for(const link of links){await page.evaluate(async b=>{__atlas.activatePin(null);await __atlas.goTo(b);},link.bone);
    const chip=page.locator('#sheet [data-pinid="'+link.id+'"]');check(await chip.count()===1,'Unique '+link.bone+'/'+link.id);await chip.click();
    check(await page.evaluate(()=>__atlas.state.pin)===link.id,'Selected '+link.id);check(await page.locator('.pin[data-pinid="'+link.id+'"]').count()===0,'No fabricated marker '+link.id);
   }
  }else if(phase==='workflow'){
   await side('both');await close();await page.locator('#bList').click();await page.locator('#q').fill('Таранная кость');
   check(await page.locator('#dlist [data-id="talus"]').count()===1,'Right search result');check(await page.locator('#dlist [data-id="talus_left"]').count()===1,'Left search result');
   await page.locator('#dlist [data-id="talus_left"]').click();check(await page.evaluate(()=>__atlas.state.sel)==='talus_left','Left card selection');
   check((await page.locator('#sheet').textContent()).includes('Подтверждённой левой модели'),'Left noModel explanation');
   await page.screenshot({path:dir+'/left-'+width+'.png'});
   await side('right');await page.evaluate(async()=>{await __atlas.goTo('talus');__atlas.activatePin('extra_talus_subtalar_joint');});await page.locator('#bIso').click();
   check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(['calcaneus','talus']),'Only two joint participants isolated');
   await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Both participants transparent');
   await page.screenshot({path:dir+'/isolation-'+width+'.png'});await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
   await side('left');check(await page.evaluate(()=>{const right=new Set(ATLAS.pins.filter(p=>p.footReview&&!p.b.endsWith('_left')).map(p=>p.b));return __thoraxCheck.snapshot().visible.every(id=>!right.has(id));}),'Left excludes all right foot owners');
   await side('both');await page.evaluate(async()=>{await __atlas.goTo('talus');__atlas.activatePin('tal_os_trigonum');});
   check(await page.locator('.pin[data-pinid="tal_os_trigonum"]').count()===0,'Unverified variant marker hidden');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
  }else if(phase==='delta-isolation'){
   for(const id of ids){const p=await page.evaluate(id=>ATLAS.pins.find(p=>p.id===id),id);await side(p.side);await page.evaluate(async p=>{await __atlas.goTo(p.b);__atlas.activatePin(p.id);},p);
    if(p.side==='left'){check(await page.locator('#bIso').count()===0,'No fictitious noModel isolation '+id);check(await page.locator('#bBoneXray').count()===0,'No fictitious noModel transparency '+id);continue;}
    await page.locator('#bIso').click();
    const expected=p.side==='left'?[]:p.relations.map(r=>r.bone).sort();
    check(JSON.stringify((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).sort())===JSON.stringify(expected),'Isolation '+id);
    await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===expected.length,'Transparency '+id);
    await page.locator('#bBoneXray').click();await page.locator('#bIso').click();
   }await side('both');await page.screenshot({path:dir+'/delta-'+width+'.png'});
  }else if(phase==='finish'){
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No overflow');
   await page.unrouteAll({behavior:'ignoreErrors'});
  }
  check(errors.length===0,'No console/page errors');return {status:'passed',phase,width,ids,links,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close({runBeforeUnload:false}).catch(()=>{});reject(Error('45000ms phase deadline; only this test page closed'));},45000);})]);}
 catch(e){return {status:'failed',phase,width,ids,links,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);page.off('console',onConsole);}
})(page,{"width":390,"phase":"setup","dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-foot-resume-2026-10-19T17-55-56-034Z-bx6EB7","probe":"window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})