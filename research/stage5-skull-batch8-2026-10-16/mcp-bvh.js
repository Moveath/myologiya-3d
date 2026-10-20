async(page)=>{
 const probe="window.__perfCheck={info:()=>({frames:perfFrames,ratio:renderer.getPixelRatio(),distance:camera.position.distanceTo(controls.target),triangles:renderer.info.render.triangles,models:Object.keys(models),pins:pinEls.length}),async compare(){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[];for(const clip of [false,true]){state.headCut.active=clip;updateHeadCut();scene.updateMatrixWorld(true);for(const x of [-.5,0,.5])for(const y of [-.5,0,.5]){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex,p:h.point.toArray()}));};ray.firstHitOnly=false;const fast=cast();meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();meshes.forEach((m,i)=>m.raycast=functions[i]);if(fast.length!==slow.length)throw Error('Intersection count mismatch');for(let i=0;i<fast.length;i++){if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray/face mismatch');}if(!clip){ray.firstHitOnly=true;const first=cast()[0];if(!!first!==!!slow[0]||first&&(first.id!==slow[0].id||Math.abs(first.d-slow[0].d)>1e-7))throw Error('Nearest hit mismatch');}results.push({clip,x,y,hits:fast.length});}}state.headCut.active=false;updateHeadCut();return results;}};\nwindow.__batchBVH=(id)=>structs.get(id).meshes.map(m=>({tree:!!m.geometry.boundsTree,indirect:!!m.geometry.boundsTree?._indirectBuffer}));\n",errors=[];const onError=e=>errors.push(String(e));page.on('pageerror',onError);
 await page.route('**/local.html*',async route=>{const r=await route.fetch();await route.fulfill({response:r,body:(await r.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
 try{
  await page.setViewportSize({width:390,height:844});
  await page.goto('http://127.0.0.1:8782/local.html?theme=light',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.__ready);await page.evaluate(()=>__atlas.enterSection('head'));
  const cases=[];
  for(const bone of ['mandible','occipital','ethmoid']){
   await page.evaluate(b=>__atlas.goTo(b),bone);await page.waitForTimeout(650);
   const trees=await page.evaluate(b=>__batchBVH(b),bone);
   if(!trees.length||trees.some(t=>!t.tree||!t.indirect))throw Error('Missing indirect BVH '+bone);
   const rays=await page.evaluate(()=>__perfCheck.compare());
   if(!rays.some(r=>r.hits>0))throw Error('Vacuous ray sample '+bone);
   cases.push({bone,indirectMeshes:trees.length,rays});
  }
  if(errors.length)throw Error(errors.join(';'));
  return {status:'passed',width:390,method:'Existing verify-atlas-performance.mjs differential ray probe: accelerated/native hit counts, distances and faceIndex, with/without cuts; indirect buffer present. No benchmark or full buffer-hash rerun.',cases,errors};
 }finally{page.off('pageerror',onError);await page.unroute('**/local.html*');}
}