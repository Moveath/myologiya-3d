async(page)=>(async function exercise(page,{dir,width,phase,ids,region,trial,output,probe,blocked}){
 const checks=[],errors=[];let timer;
 const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
 const onerror=e=>errors.push(String(e));page.on('pageerror',onerror);
 page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(18000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{
  if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
 };
 const side=async s=>{
  await close();if(width===390&&!await page.locator('[data-side-view="left"]').isVisible())await page.locator('#bOptions').click();
  await page.locator(`[data-side-view="${s}"]`).click();
  if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
 };
 const visible=()=>page.evaluate(()=>__mirrorCheck.snapshot().visible.sort());
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   if(trial)await page.route('**/stage6-mirror-trial/*.glb',r=>{
    const id=new URL(r.request().url()).pathname.split('/').pop();
    if(!ids.includes(id.replace('.glb','')))throw Error('Unexpected trial asset');
    return r.fulfill({path:output+'/'+id,contentType:'model/gltf-binary'});
   });
   await page.route('**/local.html*',async r=>{
    const response=await r.fetch();let html=await response.text();
    if(trial){
     html=html.replace('const A = window.ATLAS;',`const A = window.ATLAS;
for(const id of ${JSON.stringify(ids)}) A.bones[id]={...A.bones[id],noModel:false,modelFile:'/stage6-mirror-trial/'+id+'.glb',modelStatus:'educational_limited',modelNotice:'ПРОБНАЯ зеркальная учебная реконструкция. Допуск в основной атлас не получен.',modelLicense:'models/bodyparts3d-3.0/left-metacarpals/LICENSE-MODELS.txt'};
document.body.insertAdjacentHTML('beforeend','<div id="mirrorTrial" style="position:fixed;bottom:0;z-index:9999;background:#8b3100;color:white;pointer-events:none">ПРОБНАЯ зеркальная реконструкция</div>');`);
     const re=new RegExp("id: '"+region+"',[^\\n]+supplementalBones: (\\[[^\\]]+\\])");
     const m=html.match(re);if(!m)throw Error('Region anchor');
     html=html.replace(m[0],m[0].replace(m[1],m[1].slice(0,-1)+','+ids.map(JSON.stringify).join(',')+']'));
    }
    await r.fulfill({response,body:html.replace('window.__atlas =',probe+'window.__atlas =')});
   });
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async r=>{await __atlas.enterSection(r);__atlas.setSub('all');},region);
   await side('left');
   check(ids.length>0&&await page.evaluate(ids=>ids.every(id=>!ATLAS.bones[id].noModel),ids),'All admitted/trial flags');
   const v=await visible();check(ids.every(id=>v.includes(id)),'All batch GLBs loaded');
   if(trial)check(await page.locator('#mirrorTrial').isVisible(),'Trial remains explicitly separate');
  }else if(phase==='sides'){
   for(const s of ['both','right','left']){
    await side(s);const v=await visible();
    check(ids.every(id=>s==='both'?v.includes(id)&&v.includes(id.replace('_left','')):
     s==='left'?v.includes(id)&&!v.includes(id.replace('_left','')):
     !v.includes(id)&&v.includes(id.replace('_left',''))),'Correct side '+s);
   }
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
   await page.screenshot({path:dir+`/mirror-${width}-sides.png`});
  }else if(ids.includes(phase)){
   await close();await side('left');await page.locator('#bList').click();
   await page.locator('#q').fill(await page.evaluate(id=>ATLAS.bones[id].ru,phase));
   await page.locator(`#dlist [data-id="${phase}"]`).first().click();
   check(await page.evaluate(()=>__atlas.state.sel)===phase,'Search and selection '+phase);
   await card();check((await page.locator('[data-model-status]').innerText()).toLowerCase().includes('зеркаль'),'Explicit mirrored provenance');
   await page.locator('#bIso').click();check(JSON.stringify(await visible())===JSON.stringify([phase]),'Only selected bone isolated');
   await close();await page.waitForTimeout(800);
   await page.waitForFunction(id=>!!__mirrorCheck.clickPoint(id),phase,{timeout:6000});
   const p=await page.evaluate(id=>__mirrorCheck.clickPoint(id),phase);
   const rays=await page.evaluate(p=>__mirrorCheck.compare(p),p);
   check(rays.bvh>0&&rays.rays.some(r=>r.hits>0),'BVH/native ray agreement');
   await page.mouse.click(p.x,p.y);check(await page.evaluate(()=>__atlas.state.sel)===phase,'Real canvas selection');
   await card();await page.locator('#bBoneXray').click();
   check((await page.evaluate(()=>__mirrorCheck.snapshot().xray)).includes(phase),'Transparency');
   await card();await page.locator('#bBoneXray').click();
   await page.screenshot({path:dir+`/mirror-${width}-${phase}.png`});
   await card();await page.locator('#bIso').click();await close();
  }else if(phase==='blocked'){
   await close();await side('left');
   for(const id of blocked){
    await page.evaluate(async id=>{await __atlas.goTo(id);},id);
    const v=await visible();check(!v.includes(id)&&!v.includes(id.replace('_left','')),'Blocked model not substituted '+id);
    check(await page.evaluate(id=>!!ATLAS.bones[id].noModel,id),'Blocked flag preserved '+id);
   }
  }
  check(errors.length===0,'No JavaScript errors');
  return {status:'passed',width,phase,checks,errors,trial};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000ms deadline; test page closed'));},35000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e),trial};}
 finally{clearTimeout(timer);page.off('pageerror',onerror);}
})(page,{"dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-mirror-upper-v2-2026-10-20T12-11-27-299Z-T0jfz0","width":1280,"phase":"metacarpal_1_left","probe":"window.__mirrorCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),\r\nclickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},\r\ncompare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n","ids":["metacarpal_1_left","metacarpal_3_left"],"region":"arm","trial":true,"output":"C:/Users/Пользователь/Desktop/учеба/Миология 3D/build_stage6/mirror_upper_v2","blocked":[]})