import fs from 'node:fs/promises';
import path from 'node:path';
const dir=path.resolve(process.argv[2]),config=JSON.parse(await fs.readFile(path.join(dir,'batch.json'),'utf8'));
const ids=Object.keys(config.targets);
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=source.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__footTrialCheck').replaceAll('\\n','\n');
async function exercise(page,{dir,width,phase,ids,probe}){
 const checks=[],errors=[];let timer;
 const check=(v,label)=>{if(!v)throw Error(label);checks.push(label);};
 const error=e=>errors.push(String(e));page.on('pageerror',error);
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
 const visible=()=>page.evaluate(()=>__footTrialCheck.snapshot().visible.sort());
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.goto('http://127.0.0.1:8786/stage6-trial/local-v1.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('leg');__atlas.setSub('all');});
   await side('left');
   check(await page.locator('#trialNotice').isVisible(),'Trial banner visible');
   const v=await visible();check(ids.every(id=>v.includes(id)),'Five trial GLBs actually loaded');
  }else if(phase==='sides'){
   for(const s of ['both','right','left']){
    await side(s);const v=await visible();
    check(s==='both'?ids.every(id=>v.includes(id)&&v.includes(id.replace('_left',''))):
     s==='left'?ids.every(id=>v.includes(id)&&!v.includes(id.replace('_left',''))):
     ids.every(id=>!v.includes(id)&&v.includes(id.replace('_left',''))),'Side '+s);
   }
   await page.screenshot({path:dir+`/trial-${width}-sides.png`});
  }else if(ids.includes(phase)){
   await close();await side('left');await page.locator('#bList').click();
   await page.locator('#q').fill(await page.evaluate(id=>ATLAS.bones[id].ru,phase));
   await page.locator(`#dlist [data-id="${phase}"]`).first().click();
   check(await page.evaluate(()=>__atlas.state.sel)===phase,'Search selects '+phase);
   await card();check((await page.locator('#sheet').innerText()).includes('ПРОБНАЯ ГЕОМЕТРИЯ'),'Trial warning in card');
   await page.locator('#bIso').click();check(JSON.stringify(await visible())===JSON.stringify([phase]),'Only trial bone isolated');
   await close();await page.waitForTimeout(1000);
   const point=await page.evaluate(id=>__footTrialCheck.clickPoint(id),phase);check(!!point,'Visible ray target');
   const rays=await page.evaluate(p=>__footTrialCheck.compare(p),point);
   check(rays.bvh>0&&rays.rays.some(r=>r.hits>0),'BVH/native ray agreement');
   await page.mouse.click(point.x,point.y);check(await page.evaluate(()=>__atlas.state.sel)===phase,'Real model click');
   await card();await page.screenshot({path:dir+`/trial-${width}-${phase}.png`});
   await page.locator('#bIso').click();await close();
  }else if(phase==='joints'){
   await close();await page.evaluate(async()=>{await __atlas.goTo('metatarsal_2_left');__atlas.activatePin('extra_metatarsal_2_left_intermetatarsal_joint');});
   await card();await page.locator('#bIso').click();
   check(JSON.stringify(await visible())===JSON.stringify(ids.slice(1).sort()),'Only four trial intermetatarsal components');
   await card();await page.locator('#bBoneXray').click();
   check((await page.evaluate(()=>__footTrialCheck.snapshot().xray)).length===4,'Four linked trial bones transparent');
   await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
  }else if(phase==='canonical'){
   await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(async()=>{await __atlas.enterSection('leg');});await side('left');
   for(const id of ids){
    await close();await page.evaluate(async id=>{await __atlas.goTo(id);},id);await card();
    check(await page.evaluate(id=>ATLAS.bones[id].noModel&&!ATLAS.bones[id].modelFile&&!ATLAS.bones[id].modelReview.educationalAcceptance,id),'Canonical noModel preserved '+id);
    check((await page.locator('#sheet').innerText()).includes('не подключена'),'Specific pending admission '+id);
    const v=await visible();check(!v.includes(id)&&!v.includes(id.replace('_left','')),'No substitution '+id);
   }
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No overflow');
   await page.unrouteAll({behavior:'ignoreErrors'});
  }
  check(!errors.length,'No JavaScript errors');return {status:'passed',width,phase,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline; test page closed'));},40000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',error);}
}
for(const width of [1280,390])for(const phase of ['setup','sides',...ids,'joints','canonical'])
 await fs.writeFile(path.join(dir,`mcp-v1-${width}-${phase}.js`),`async(page)=>(${exercise.toString()})(page,${JSON.stringify({dir,width,phase,ids,probe})})`,{flag:'wx'});
console.log('Prepared bounded trial + canonical MCP phases.');
