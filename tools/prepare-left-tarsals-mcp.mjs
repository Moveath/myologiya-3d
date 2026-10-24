import fs from 'node:fs/promises';
import path from 'node:path';
const dir=path.resolve(process.argv[2]),revision=process.argv[3]??'v1';
if(!/^v\d+$/.test(revision))throw Error('Invalid revision');
const old=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=old.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__forearmCheck').replaceAll('\\n','\n')+'window.__mcView=()=>[...camera.position.toArray(),...controls.target.toArray()];';
async function exercise(page,{dir,width,phase,probe,revision}){
 const ids=["navicular_left", "cuneiform_med_left", "cuneiform_int_left"];
 const allCarpals=ids;
 const checks=[],errors=[];let timer;
 const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
 const error=e=>errors.push(String(e)),consoleError=m=>{if(m.type()==='error'&&!m.text().includes('favicon'))errors.push(m.text());};
 page.on('pageerror',error);page.on('console',consoleError);
 page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(18000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{
  if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
 };
 const side=async value=>{
  await close();if(width===390&&!await page.locator('[data-side-view="left"]').isVisible())await page.locator('#bOptions').click();
  await page.locator(`[data-side-view="${value}"]`).click();
  if(await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
 };
 const visible=()=>page.evaluate(()=>__forearmCheck.snapshot().visible.sort());
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});
   await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('navicular_left');});
   check(await page.evaluate(()=>["navicular_left", "cuneiform_med_left", "cuneiform_int_left"].every(id=>!ATLAS.bones[id].noModel)),'Three admitted tarsal models');
   await page.evaluate(()=>__atlas.setSub('all'));await side('left');
   check((await visible()).filter(id=>allCarpals.includes(id)).length===3,'All three admitted tarsal meshes visible');
   check((await page.locator('#modelCoverage').textContent()).includes('Учебная 3D-модель'),'Educational scope remains explicit');
  }else if(phase==='sides'){
   for(const s of ['both','right','left']){
    await side(s);const v=await visible();
    check(s==='both'?allCarpals.every(id=>v.includes(id)&&v.includes(id.replace('_left',''))):
     s==='left'?allCarpals.every(id=>v.includes(id))&&v.every(id=>!['talus','calcaneus','navicular','cuboid','cuneiform_med','cuneiform_int','cuneiform_lat'].includes(id)):
     ids.every(id=>v.includes(id.replace('_left','')))&&v.every(id=>!id.endsWith('_left')),'Consistent hand side '+s);
   }
   await page.screenshot({path:dir+`/ui-${revision}-${width}-hand.png`});
  }else if(ids.includes(phase)){
   const id=phase;await close();await side('left');
   await page.locator('#bList').click();
   const name=await page.evaluate(id=>ATLAS.bones[id].ru,id);
   await page.locator('#q').fill(name);await page.locator(`#dlist [data-id="${id}"]`).first().click();
   check(await page.evaluate(()=>__atlas.state.sel)===id,'Search selects '+id);
   await card();check(await page.locator('[data-model-status="educational_limited"]').isVisible(),'Visible educational warning');
   check((await page.locator('[data-model-status] a').getAttribute('href')).includes('left-tarsals/LICENSE-MODELS.txt'),'Attribution link');
   await page.locator('#bIso').click();check(JSON.stringify(await visible())===JSON.stringify([id]),'Only selected bone isolated');
   await close();
   await page.waitForTimeout(1000); // Wait for focus animation before comparing the same screen ray.
   await page.waitForFunction(id=>!!__forearmCheck.clickPoint(id),id,{timeout:6000});
   const point=await page.evaluate(id=>__forearmCheck.clickPoint(id),id);
   const rays=await page.evaluate(p=>__forearmCheck.compare(p),point);
   check(rays.bvh>0&&rays.rays.some(r=>r.hits>0),'BVH/native distances and faceIndex');
   await page.mouse.click(point.x,point.y);
   check(await page.evaluate(()=>__atlas.state.sel)===id,'Real model click');
   await card();await page.screenshot({path:dir+`/ui-${revision}-${width}-${id}.png`});
   await page.locator('#bIso').click();await close();
  }else if(phase==='blocked'){
   for(const id of ["talus_left", "calcaneus_left", "cuboid_left", "cuneiform_lat_left"]){
    await close();await page.evaluate(async id=>{await __atlas.goTo(id);},id);await card();
    check(await page.evaluate(id=>ATLAS.bones[id].noModel&&!ATLAS.bones[id].modelFile&&!ATLAS.bones[id].modelReview.educationalAcceptance,id),'Trial model not admitted '+id);
    check((await page.locator('#sheet').textContent()).includes('не подключена'),'Visible trial-blocker reason '+id);
    check(!(await visible()).includes(id)&&!(await visible()).includes(id.replace('_left','')),'No opposite-side substitution '+id);
   }await close();
  }else if(phase==='state'){
   await close();await page.evaluate(async()=>{await __atlas.goTo('navicular_left');__atlas.activatePin('extra_navicular_left_cuneonavicular_joint');});
   await card();await page.locator('#bIso').click();await card();await page.locator('#bBoneXray').click();await card();
   await page.waitForTimeout(1000);
   check((await page.evaluate(()=>__forearmCheck.snapshot().xray)).length===3,'Shared selection is isolated and transparent before panel toggle');
   const before=await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin,side:__atlas.state.side,visible:__forearmCheck.snapshot(),view:__mcView()}));
   if(width===390){await close();await card();}else{await page.locator('#bList').click();await page.locator('#bCloseList').click();}
   const after=await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin,side:__atlas.state.side,visible:__forearmCheck.snapshot(),view:__mcView()}));
   check(before.sel===after.sel&&before.pin===after.pin&&before.side===after.side,'Card panel preserves selection, shared pin and side');
   check(JSON.stringify(before.visible)===JSON.stringify(after.visible),'Card panel preserves isolation and transparency');
   check(before.view.every((v,i)=>Math.abs(v-after.view[i])<1e-6),'Card panel preserves camera');
   await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
  }else if(phase==='joints'){
   for(const [owner,pin,expected] of [["navicular_left", "extra_navicular_left_cuneonavicular_joint", ["navicular_left", "cuneiform_med_left", "cuneiform_int_left"]], ["cuneiform_int_left", "extra_cuneiform_int_left_intercuneiform_joint", ["cuneiform_med_left", "cuneiform_int_left"]]]){
    await close();await page.evaluate(async({owner,pin})=>{await __atlas.goTo(owner);__atlas.activatePin(pin);},{owner,pin});
    await card();check(await page.locator('.pinbox').isVisible(),'Shared card '+pin);
    await page.locator('#bIso').click();check(JSON.stringify(await visible())===JSON.stringify(expected.sort()),'Only linked loaded bones '+pin);
    await card();await page.locator('#bBoneXray').click();
    check((await page.evaluate(()=>__forearmCheck.snapshot().xray)).length===expected.length,'Linked bone transparency');
    await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
   }
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
  }
  check(!errors.length,'No page or console errors');return {status:'passed',width,phase,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline; test page closed'));},40000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',error);page.off('console',consoleError);}
}
for(const width of [1280,390])for(const phase of ['setup','sides',...["navicular_left", "cuneiform_med_left", "cuneiform_int_left"],'blocked','joints','state'])
 await fs.writeFile(path.join(dir,`mcp-${revision}-${width}-${phase}.js`),`async(page)=>(${exercise.toString()})(page,${JSON.stringify({dir,width,phase,probe,revision})})`,{flag:'wx'});
console.log('Prepared 16 bounded foot MCP phases.');
