import fs from 'node:fs/promises';
import path from 'node:path';
const [run,widthText]=process.argv.slice(2),width=Number(widthText);
if(![390,1280].includes(width))throw Error('Expected run directory and 390/1280');
const script=`async(page)=>{
 const dir=${JSON.stringify(path.resolve(run).replaceAll('\\','/'))};
 const started=Date.now(),checks=[],errors=[];page.setDefaultTimeout(6000);
 const onError=e=>errors.push(e.message);page.on('pageerror',onError);
 const checkpoints={};
 const save=async(name,value)=>{checkpoints[name]=value;await page.evaluate(x=>{window.__coverageCheckpoints=x;},checkpoints);};
 const check=(ok,name)=>{checks.push({name,passed:!!ok});if(!ok)throw Error(name);if(Date.now()-started>45000)throw Error('45-second test budget');};
 const snap=()=>page.evaluate(()=>__atlas.inspect());
 const openCard=async()=>{if(${width}<900&&await page.locator('#closeMobileCard').isHidden())await page.locator('#mobileCard').click();};
 const closeCard=async()=>{if(${width}<900&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const settings=async()=>{await closeCard();if(${width}<900&&await page.locator('#systemControls').isHidden())await page.locator('#bOptions').click();};
 const closeSettings=async()=>{if(${width}<900&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 try {
 await page.setViewportSize({width:${width},height:${width===390?844:900}});
 await page.evaluate(async width=>{document.documentElement.dataset.theme=width===390?'dark':'light';await __atlas.enterSection('arm');__atlas.setSub('all');},${width});
 await settings();
 for(const [key,value]of Object.entries({bones:false,muscles:false,heart:false,arteries:true,veins:true})){
   const b=page.locator('[data-system="'+key+'"]');if((await b.getAttribute('aria-pressed'))!==String(value))await b.click();
 }
 await page.locator('[data-side-view="both"]').click();await closeSettings();
 check((await page.locator('#vascularCoverageText').innerText()).includes('только карточек: 16'),'arm explains 16 cards without models');
 check((await snap()).structures.every(s=>!s.visible),'arm scene honestly has no vascular models');
 check(await page.locator('#modelCoverage').isHidden(),'bone coverage not shown in vessels-only view');
 await page.screenshot({path:dir+'/arm-${width}.png'});
 await save('arm-${width}.json',{checks:[...checks],notice:await page.locator('#vascularCoverageText').innerText()});
 await page.locator('[data-system-catalog="arteries"]').click();
 check(await page.locator('[data-list-type="arteries"]').getAttribute('aria-pressed')==='true','catalogue button selects arterial filter');
 await page.locator('#q').fill('плечевая');await page.locator('#dlist [data-id="cv_a_brachial_right"]').click();await openCard();
 check((await page.locator('#sheet').innerText()).includes('Только карточка'),'missing arm vessel card remains honest');
 await page.locator('#bDeselect').click();await closeCard();
 await page.locator('[data-system-region="neck"]').click();
 await page.waitForFunction(()=>__atlas.state.sec==='neck'&&!__atlas.inspect().loading.length,{timeout:18000});
 let s=await snap();check(s.structures.filter(s=>s.visible&&s.kind==='s').length===8,'neck link displays eight vessels');
 check(!Object.keys(s.errors).length,'no model loading errors');
 check(s.structures.filter(s=>s.kind==='s').every(s=>s.bvh),'neck vessels retain BVH');
 await settings();await page.locator('[data-side-view="left"]').click();
 check((await snap()).structures.filter(s=>s.visible).every(s=>s.side!=='right'),'left excludes right');
 check((await page.locator('#vascularCoverageText').innerText()).includes('моделей: 4'),'left coverage reflects four neck models');
 await page.locator('[data-side-view="right"]').click();check((await snap()).structures.filter(s=>s.visible).every(s=>s.side!=='left'),'right excludes left');
 await page.locator('[data-side-view="both"]').click();await closeSettings();
 await page.evaluate(()=>__atlas.setSub('all'));await page.waitForTimeout(750);
 await page.screenshot({path:dir+'/neck-all-${width}.png'});
 await save('neck-${width}.json',{checks:[...checks],visible:(await snap()).structures.filter(s=>s.visible).map(s=>s.id)});
 await page.locator('[data-system-catalog="arteries"]').click();await page.locator('#q').fill('общая сонная');
 await page.locator('#dlist [data-id="cv_a_carotid_common_right"]').click();await openCard();
 await page.locator('#structureOpacity').fill('40');check((await snap()).structures.find(s=>s.id==='cv_a_carotid_common_right').opacity===.4,'vessel transparency');
 await page.locator('#bIso').click();check((await snap()).structures.filter(s=>s.visible).every(s=>s.id==='cv_a_carotid_common_right'),'vessel isolation');
 await closeCard();
 await page.evaluate(async()=>{await __atlas.enterSection('leg');__atlas.setSub('cardiovascular');});
 await page.waitForFunction(()=>!__atlas.inspect().loading.length,{timeout:18000});
 s=await snap();check(s.structures.filter(s=>s.visible&&s.kind==='s').length===12,'leg region displays 12 pelvic vessels');
 check((await page.locator('#vascularCoverageText').innerText()).includes('только карточек: 18'),'leg reports remaining 18 cards without models');
 check(!errors.length,'no JavaScript exceptions');
 check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal page overflow');
 await save('result-${width}.json',{status:'passed',checks,errors,elapsedMs:Date.now()-started});
 return {status:'passed',checks:checks.length,elapsedMs:Date.now()-started,checkpoints};
 }catch(error){await save('failure-${width}.json',{error:error.message,checks,errors,elapsedMs:Date.now()-started});return {status:'failed',error:error.message,checks:checks.length,checkpoints};}
 finally{page.off('pageerror',onError);}
}`;
const file=path.join(run,`coverage-${width}-r3.mcp.js`);
await fs.writeFile(file,script,{flag:'wx'});console.log(path.resolve(file));
