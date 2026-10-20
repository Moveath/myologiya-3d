// Resume only the unfinished foot UI checks. Each MCP call is bounded and saved separately.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {createEvidenceRun} from './evidence-run.mjs';
const prior='research/evidence-runs/stage5-foot-2026-10-19T09-33-56-218Z-lia0LB';
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=vm.runInNewContext(source.match(/const probe=([\s\S]*?);\r?\n\r?\nasync function/)[1]);
const records=JSON.parse(await fs.readFile(prior+'/reviewed-records-final.json','utf8'));
const earlier=JSON.parse(await fs.readFile(prior+'/reviewed-records-accepted.json','utf8'));
const delta=records.filter(p=>!earlier.some(q=>q.id===p.id));
if(delta.length!==6)throw Error('Unexpected desktop delta');
const edges=rows=>rows.filter(p=>p.relations).flatMap(p=>p.relations.map(r=>({id:p.id,bone:r.bone})));
async function exercise(page,opt){
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
}
const run=await createEvidenceRun(process.cwd(),'stage5-foot-resume');
const plan=[];
const add=async(width,phase,data={})=>{const name=String(plan.length).padStart(2,'0')+'-'+width+'-'+phase;const opt={width,phase,dir:run.dir,...data,...(phase==='setup'?{probe}:{})};const file=await run.write(name+'.js','async(page)=>('+exercise.toString()+')(page,'+JSON.stringify(opt)+')');plan.push({name,file,width,phase,ids:data.ids||[],links:data.links||[]});};
await add(390,'setup');
const allEdges=edges(records);
if(!process.argv.includes('--finish-only')){
 for(let i=0;i<records.length;i+=30)await add(390,'cards',{ids:records.slice(i,i+30).map(p=>p.id)});
 for(let i=0;i<allEdges.length;i+=16)await add(390,'links',{links:allEdges.slice(i,i+16)});
}
await add(390,'workflow');await add(390,'finish');
await add(1280,'setup');await add(1280,'cards',{ids:delta.map(p=>p.id)});await add(1280,'links',{links:edges(delta)});await add(1280,'delta-isolation',{ids:delta.map(p=>p.id)});await add(1280,'workflow');await add(1280,'finish');
await run.write('plan.json',plan);
await run.write('before-documents.json',Object.fromEntries(await Promise.all(['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','CURRENT_PROJECT_STATUS.md'].map(async p=>[p,await fs.readFile(p,'utf8')]))));
console.log(JSON.stringify({dir:run.dir,phases:plan.length,mobileCards:records.length,mobileEdges:allEdges.length,desktopDelta:delta.map(p=>p.id)}));
