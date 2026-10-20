import fs from 'node:fs/promises';
import path from 'node:path';
const dir=path.resolve(process.argv[2]);
const revision=process.argv[3]??'v1';
const educational=process.argv[4]==='educational';
if(!/^v[0-9]+$/.test(revision))throw Error('Invalid revision');
// Reuse the established diagnostic probe without executing its historical test.
const old=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=old.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__forearmCheck').replaceAll('\\n','\n');
async function exercise(page,{width,phase,dir,probe,revision,educational}){
 const checks=[],errors=[];let timer;
 const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error'&&!m.text().includes('favicon'))errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);
 page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(20000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{
  if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&(await page.locator('#bMore').textContent())==='Подробнее')await page.locator('#bMore').click();
 };
 const side=async value=>{
  await close();
  if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();
  await page.locator('[data-side-view="'+value+'"]').click();
  if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();
 };
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});
   await page.setViewportSize({width,height:width===390?844:900});
   await page.emulateMedia({colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   await page.route(educational?'**/local.html*':'**/stage6-trial/local*.html*',async r=>{
    const response=await r.fetch();
    await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});
   });
   await page.goto((educational?'http://127.0.0.1:8783/local.html':'http://127.0.0.1:8784/stage6-trial/local-'+revision+'.html')+'?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>localStorage.removeItem('myo3d'));await page.reload({waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('radius_left');});
   check(educational?(await page.locator('#modelCoverage').textContent()).includes('Учебная 3D-модель'):await page.locator('#trialNotice').isVisible(),educational?'Explicit educational limitation':'Explicit trial banner');
   check(await page.evaluate(()=>__forearmCheck.snapshot().visible.includes('radius_left')&&__forearmCheck.snapshot().visible.includes('ulna_left')),'Both trial models loaded');
  }else if(phase==='sides'){
   await page.evaluate(()=>__atlas.setSub('forearm'));
   for(const s of ['both','right','left']){
    await side(s);
    const visible=await page.evaluate(()=>__forearmCheck.snapshot().visible);
    check(s==='both'?['radius','ulna','radius_left','ulna_left'].every(id=>visible.includes(id)):
     s==='left'?visible.includes('radius_left')&&visible.includes('ulna_left')&&!visible.some(id=>['radius','ulna','humerus','scapula','clavicle'].includes(id)):
     visible.includes('radius')&&visible.includes('ulna')&&!visible.some(id=>id.endsWith('_left')),'Consistent side '+s);
   }
   await page.evaluate(()=>__atlas.setSub('all'));
   check((await page.locator('#modelCoverage').textContent()).includes('кист'),'Missing left hand remains explicit in whole arm');
   await page.evaluate(()=>__atlas.setSub('forearm'));
   await page.screenshot({path:dir+'/ui-'+(educational?'edu-':'')+revision+'-'+width+'-sides.png'});
  }else if(phase==='cards'){
   await side('left');
   for(const id of ['radius_left','ulna_left']){
    await close();await page.locator('#bList').click();
    await page.locator('#q').fill(id==='radius_left'?'Левая лучевая кость':'Левая локтевая кость');
    await page.locator('#dlist [data-id="'+id+'"]').first().click();
    check(await page.evaluate(()=>__atlas.state.sel)===id,'Search selects '+id);
    await card();
    check((await page.locator('#sheet').textContent()).includes(educational?'Учебная 3D-модель. Точная геометрия суставных поверхностей и зазоров не подтверждена.':'ПРОБНАЯ МОДЕЛЬ'),'Model qualification '+id);
    if(educational){
     check(await page.locator('[data-model-status="educational_limited"]').isVisible(),'Visible educational notice '+id);
     check((await page.locator('[data-model-status] a').getAttribute('href')).endsWith('/LICENSE-MODELS.txt'),'Published licence link '+id);
    }
    await page.locator('#bIso').click();
    check(JSON.stringify(await page.evaluate(()=>__forearmCheck.snapshot().visible))===JSON.stringify([id]),'Isolate '+id);
    await card();await page.locator('#bIso').click();
   }
   await close();
  }else if(phase==='joint'){
   await page.evaluate(()=>__atlas.activatePin('extra_radius_left_proximal_radioulnar_joint'));await card();
   check((await page.locator('.pinbox').textContent()).includes('лучелоктевой'),'Shared joint card');
   await page.locator('#bIso').click();
   check(JSON.stringify((await page.evaluate(()=>__forearmCheck.snapshot().visible)).sort())===JSON.stringify(['radius_left','ulna_left']),'Only linked trial bones isolated');
   await card();await page.locator('#bBoneXray').click();
   check((await page.evaluate(()=>__forearmCheck.snapshot().xray)).length===2,'Both linked bones transparent');
   await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
   check(await page.evaluate(()=>ATLAS.pins.filter(p=>p.b==='radius_left'||p.b==='ulna_left').every(p=>!p.p)),'No invented left pins');
   await page.screenshot({path:dir+'/ui-'+(educational?'edu-':'')+revision+'-'+width+'-joint.png'});
  }else if(phase==='rays'){
   await close();await page.evaluate(()=>__atlas.goTo('radius_left'));await card();await page.locator('#bIso').click();await close();
   await page.waitForFunction(()=>!!__forearmCheck.clickPoint('radius_left'),undefined,{timeout:6000});
   const point=await page.evaluate(()=>__forearmCheck.clickPoint('radius_left'));
   const comparison=await page.evaluate(p=>__forearmCheck.compare(p),point);
   check(comparison.bvh>=1&&comparison.rays.some(r=>r.hits>0),'BVH/native matching hits and faceIndex');
   await page.mouse.click(point.x,point.y);
   check(await page.evaluate(()=>__atlas.state.sel)==='radius_left','Real canvas click selects left radius');
   await close();await card();await page.locator('#bIso').click();await close();
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
  }
  check(errors.length===0,'No page/console errors');
  return {status:'passed',width,phase,checks,errors};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline; this test page closed'));},40000);})]);}
 catch(e){return {status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);page.off('console',onConsole);}
}
const plan=[];
for(const width of [1280,390])for(const phase of ['setup','sides','cards','joint','rays']){
 const file=path.join(dir,`mcp-${educational?'edu-':''}${revision}-${width}-${phase}.js`);
 await fs.writeFile(file,`async(page)=>(${exercise.toString()})(page,${JSON.stringify({width,phase,dir,probe,revision,educational})})`,{flag:'wx'});
 plan.push({width,phase,file});
}
await fs.writeFile(path.join(dir,'mcp-plan-'+(educational?'edu-':'')+revision+'.json'),JSON.stringify(plan,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({phases:plan.length,dir}));
