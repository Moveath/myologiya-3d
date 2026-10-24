// One bounded phase per invocation; caller persists every result before continuing.
import fs from 'node:fs/promises';
import path from 'node:path';
const dir=path.resolve(process.argv[2]),settings=JSON.parse(await fs.readFile(path.join(dir,'ui-config.json'),'utf8'));
const revision=process.argv[3]??'v1';
if(!/^v\d+$/.test(revision))throw Error('Invalid evidence revision');
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=source.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__mirrorCheck').replaceAll('\\n','\n')+`
const coarseMirrorPoint=__mirrorCheck.clickPoint;
__mirrorCheck.clickPoint=id=>{
 const s=structs.get(id),r=canvas.getBoundingClientRect(),box=new THREE.Box3();
 if(s?.meshes?.length){
  scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);
  for(const m of s.meshes)if(m.visible)box.union(new THREE.Box3().setFromObject(m));
  if(!box.isEmpty()){
   const p=box.getCenter(new THREE.Vector3()).project(camera);
   const cx=r.left+(p.x+1)*r.width/2,cy=r.top+(1-p.y)*r.height/2;
   for(const dy of [0,-1,1,-2,2,-4,4,-8,8])for(const dx of [0,-1,1,-2,2,-4,4,-8,8]){
    const x=cx+dx,y=cy+dy;
    if(document.elementFromPoint(x,y)===canvas&&hitAt(x,y)?.sid===id)return {x,y};
   }
  }
 }
 return coarseMirrorPoint(id);
};
`;
async function exercise(page,{dir,width,phase,ids,region,trial,output,probe,blocked,revision}){
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
   await page.screenshot({path:dir+`/mirror-${revision}-${width}-sides.png`});
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
   const shared=await page.evaluate(id=>ATLAS.pins.find(p=>p.relations?.length>1&&p.relations.some(r=>r.bone===id))?.id,phase);
   check(!!shared,'Existing shared structure');
   await page.evaluate(p=>__atlas.activatePin(p),shared);
   await card();await page.locator('#bBoneXray').click();
   check((await page.evaluate(()=>__mirrorCheck.snapshot().xray)).includes(phase),'Transparency');
   await card();await page.locator('#bBoneXray').click();
   await page.screenshot({path:dir+`/mirror-${revision}-${width}-${phase}.png`});
   await card();await page.locator('#bIso').click();await close();
  }else if(phase==='blocked'){
   await close();await side('left');
   for(const id of blocked){
    await page.evaluate(async id=>{await __atlas.goTo(id);},id);
    const v=await visible();check(!v.includes(id)&&!v.includes(id.replace('_left','')),'Blocked model not substituted '+id);
    check(await page.evaluate(id=>!!ATLAS.bones[id].noModel,id),'Blocked flag preserved '+id);
   }
  }else if(phase==='canonical'){
   check(!trial,'Canonical build');
   for(const id of ids){
    await close();await page.evaluate(async id=>{await __atlas.goTo(id);},id);await card();
    check(await page.evaluate(id=>!ATLAS.bones[id].noModel&&
     ATLAS.bones[id].modelOrigin?.method==='mirrored_educational_reconstruction'&&
     ATLAS.bones[id].modelReview.educationalAcceptance&&!ATLAS.bones[id].modelReview.fullAnatomicalAcceptance,id),'Actual educational admission '+id);
    check((await page.locator('[data-model-status]').innerText()).includes('Зеркальная учебная реконструкция'),'Canonical provenance '+id);
    const link=await page.locator('[data-model-status] a').getAttribute('href');
    check(link.includes('mirrored-left-foot/LICENSE-MODELS.txt'),'Derivative licence '+id);
    check((await visible()).includes(id),'Canonical loaded mesh '+id);
   }
   await close();await page.screenshot({path:dir+`/canonical-${revision}-${width}.png`});
  }
  check(errors.length===0,'No JavaScript errors');
  return {status:'passed',width,phase,checks,errors,trial};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('35000ms deadline; test page closed'));},35000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e),trial};}
 finally{clearTimeout(timer);page.off('pageerror',onerror);}
}
for(const width of [1280,390])for(const phase of ['setup','sides',...settings.ids,...(settings.blocked?.length?['blocked']:[]),...(!settings.trial?['canonical']:[])])
 await fs.writeFile(path.join(dir,`mcp-${revision}-${width}-${phase}.js`),`async(page)=>(${exercise.toString()})(page,${JSON.stringify({dir,width,phase,probe,revision,...settings})})`,{flag:'wx'});
console.log('Bounded mirror phases prepared.');
