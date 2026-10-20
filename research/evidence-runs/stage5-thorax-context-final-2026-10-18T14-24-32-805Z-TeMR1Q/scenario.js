async(page)=>{
const probe=`window.__thoraxCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),
clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},
compare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n`;


const check=(v,m)=>{if(!v)throw Error(m)},out=[],errors=[];
const onError=e=>errors.push(String(e));page.on('pageerror',onError);
const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
try{
 await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
 for(const [width,theme] of [[1280,'light'],[390,'dark']]){
  await page.setViewportSize({width,height:width===390?844:900});await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);await page.evaluate(()=>__atlas.enterSection('trunk'));
  for(const owner of ['cervical_7','thoracic_1']){
   const foreign=owner==='cervical_7'?'thoracic_1':'cervical_7';
   await page.evaluate(b=>__atlas.goTo(b,null,'shared_thorax_intervertebral_c7_t1_right'),owner);await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(600);
   check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).length===2,'Two isolated contributors');
   const target=await page.evaluate(b=>__thoraxCheck.clickPoint(b),foreign);check(target,'Foreign context bone pickable');await page.mouse.click(target.x,target.y);check(await page.evaluate(()=>__atlas.state.sel)===foreign,'Canonical selected ID');check(await page.evaluate(()=>__atlas.state.pin)==='shared_thorax_intervertebral_c7_t1_right','Pin retained');await close();await page.waitForTimeout(400);
   const ray=await page.evaluate(b=>__thoraxCheck.compare(__thoraxCheck.clickPoint(b)),foreign);check(ray.bvh===2,'Both BVH trees');
   await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===2,'Two transparent contributors');await card();await page.locator('#bBoneXray').click();
   await page.evaluate(()=>{if(__atlas.state.context)document.querySelector('#bContext').click()});check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).length===2,'Context off preserves contributors');
   await page.evaluate(()=>__atlas.activatePin(null));check((await page.evaluate(()=>__thoraxCheck.snapshot().visible)).includes(foreign),'Selected context bone survives closing pin');
   await page.evaluate(b=>__atlas.goTo(b),owner);check(!(await page.evaluate(()=>__thoraxCheck.snapshot().visible)).includes(foreign),'Unselected bone returns to context');
   await page.evaluate(()=>{if(!__atlas.state.context)document.querySelector('#bContext').click()});
   out.push({width,theme,owner,foreign,isolation:true,transparency:true,canonicalRaySelection:true,pinRetained:true,selectedBonePreserved:true,contextRestored:true,ray});
  }
 }
 check(!errors.length,'Page errors');return{status:'passed',cases:out,errors};
}catch(e){return{status:'failed',error:String(e),cases:out,errors};}finally{page.off('pageerror',onError);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}

}