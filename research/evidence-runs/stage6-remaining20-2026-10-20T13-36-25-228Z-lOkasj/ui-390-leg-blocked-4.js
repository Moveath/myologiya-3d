async(page)=>(async function test(page,{run,width,region,phase,ids,probe}){
 const checks=[],errors=[];let timer;
 const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
 const onerror=e=>errors.push(String(e));page.on('pageerror',onerror);
 page.setDefaultTimeout(4000);page.setDefaultNavigationTimeout(15000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const side=async s=>{await close();if(width===390&&!await page.locator('[data-side-view="left"]').isVisible())await page.locator('#bOptions').click();await page.locator(`[data-side-view="${s}"]`).click();if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const card=async()=>{if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const visible=()=>page.evaluate(()=>__remainingCheck.snapshot().visible);
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(async r=>{await __atlas.enterSection(r);__atlas.setSub('all');},region);
   check(await page.evaluate(()=>Object.values(ATLAS.bones).filter(b=>b.noModel).length)===20,'20 missing owners retained');
  }else if(phase==='working'){
   const id=region==='arm'?'metacarpal_2_left':'toe_prox_2_left',right=id.replace('_left','');
   for(const s of ['both','right','left']){await side(s);const v=await visible();check(s==='both'?v.includes(id)&&v.includes(right):s==='left'?v.includes(id)&&!v.includes(right):!v.includes(id)&&v.includes(right),'Side '+s);}
   await page.locator('#bList').click();await page.locator('#q').fill(await page.evaluate(id=>ATLAS.bones[id].ru,id));await page.locator(`#dlist [data-id="${id}"]`).first().click();
   check(await page.evaluate(()=>__atlas.state.sel)===id,'Search and selection');await card();await page.locator('#bIso').click();check(JSON.stringify(await visible())===JSON.stringify([id]),'Isolation');
   await close();await page.waitForTimeout(600);
   const p=await page.evaluate(id=>__remainingCheck.clickPoint(id),id);check(!!p,'Ray point');
   const ray=await page.evaluate(p=>__remainingCheck.compare(p),p);check(ray.bvh>0&&ray.rays.some(r=>r.hits>0),'BVH/native ray agreement');
   await page.mouse.click(p.x,p.y);check(await page.evaluate(()=>__atlas.state.sel)===id,'Canvas selection');
   const shared=await page.evaluate(id=>ATLAS.pins.find(p=>p.relations?.length>1&&p.relations.some(r=>r.bone===id))?.id,id);
   check(!!shared,'Shared card available');await page.evaluate(p=>__atlas.activatePin(p),shared);await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__remainingCheck.snapshot().xray)).includes(id),'Transparency');
   await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No overflow');
   await page.screenshot({path:run+`/ui-${width}-${region}-${phase}.png`});
  }else{
   for(const id of ids){await close();await side(id.endsWith('_right')?'right':'left');await page.evaluate(async id=>{await __atlas.goTo(id);},id);await card();
    check(await page.evaluate(()=>__atlas.state.sel)===id,'Card selection '+id);
    check(await page.evaluate(id=>ATLAS.bones[id].noModel&&!ATLAS.bones[id].modelFile,id),'No trial substituted '+id);
    check(!(await visible()).includes(id),'No unaccepted mesh '+id);
   }
   await page.screenshot({path:run+`/ui-${width}-${region}-${phase}.png`});
  }
  check(!errors.length,'No JS errors');return {status:'passed',width,region,phase,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000ms deadline; page closed'));},35000);})]);}
 catch(e){return {status:'failed',width,region,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onerror);}
})(page,{"run":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj","width":390,"region":"leg","phase":"blocked-4","ids":["metatarsal_1_left","toe_prox_1_left","toe_dist_1_left","metatarsal_2_left"],"probe":"window.__remainingCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n"})