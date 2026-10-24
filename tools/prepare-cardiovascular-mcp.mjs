// Generate bounded MCP scenarios with unique evidence paths, not historical paths.
import fs from 'node:fs/promises';
import path from 'node:path';
const [run,widthText,phase]=process.argv.slice(2),width=Number(widthText);
if(![1280,390].includes(width)||!['heart','vessels','regression'].includes(phase))throw Error('run 1280|390 heart|vessels|regression');
const script=`async(page)=>{
const started=Date.now(),checks=[],errors=[];page.setDefaultTimeout(7000);page.setDefaultNavigationTimeout(12000);
const onError=e=>errors.push(e.message);page.on('pageerror',onError);
const check=(value,name)=>{checks.push({name,passed:!!value});if(!value)throw Error(name);if(Date.now()-started>45000)throw Error('45s scenario budget');};
const openCard=async()=>{if(${width}<900&&await page.locator('#closeMobileCard').isHidden())await page.locator('#mobileCard').click();};
const closeCard=async()=>{if(${width}<900&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
const settings=async()=>{await closeCard();if(${width}<900&&await page.locator('#systemControls').isHidden())await page.locator('#bOptions').click();};
const closeSettings=async()=>{if(${width}<900&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
const snap=()=>page.evaluate(()=>__atlas.inspect());
try {
 await page.setViewportSize({width:${width},height:${width===390?844:900}});
 ${phase==='heart'?`
 await page.unrouteAll({behavior:'ignoreErrors'});await page.context().unrouteAll({behavior:'ignoreErrors'});
 await page.goto('http://127.0.0.1:8783/local.html?cv=${width}&theme=${width===390?'dark':'light'}',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__ready,{timeout:10000});
 await page.locator('#bCardiovascular').click();
 await page.waitForFunction(()=>__atlas.state.sel==='cv_heart'&&!__atlas.inspect().loading.length,{timeout:22000});
 await openCard();check((await page.locator('#sheet').innerText()).includes('Учебная модель'),'educational notice');
 let s=await snap();check(s.structures.filter(x=>x.kind==='s').length===30,'30 thoracoabdominal models loaded');check(!Object.keys(s.errors).length,'no supplemental load errors');
 check(s.structures.filter(x=>x.kind==='s').every(x=>x.bvh),'real BVH on cardiovascular meshes');
 await page.locator('#structureOpacity').fill('40');check((await snap()).structures.find(x=>x.id==='cv_heart').opacity===.4,'selected structure transparency');
 await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='cv_heart'),'heart isolation excludes all other systems');
 await openCard();await page.locator('#bIso').click();await openCard();
 await page.locator('[data-structure-link="cv_valve_mitral"]').click();
 check(await page.evaluate(()=>__atlas.state.sel==='cv_valve_mitral'),'hierarchy link opens mitral valve');
 await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='cv_valve_mitral'),'valve isolation');
 await closeCard();await page.locator('#bList').click();await page.locator('#q').fill('ventriculus sinister');
 await page.locator('#dlist [data-id="cv_ventricle_left"]').click();await openCard();
 check((await page.locator('#sheet').innerText()).includes('Только карточка'),'unsegmented chamber stays noModel');check(await page.locator('#bIso').count()===0,'no fake isolation for chamber');
 await closeCard();await settings();await page.locator('[data-side-view="left"]').click();await closeSettings();
 check((await snap()).structures.filter(x=>x.visible).every(x=>x.side!=='right'),'left side consistent across systems');
 await settings();await page.locator('[data-side-view="both"]').click();await closeSettings();
 await page.evaluate(()=>__atlas.goTo('cv_heart'));await closeCard();await settings();
 await page.locator('[data-system="bones"]').click();await page.locator('[data-system="muscles"]').click();await page.locator('[data-peel="0"]').click();await closeSettings();
 s=await snap();check(['bones','muscles','heart','arteries','veins'].every(k=>s.structures.some(x=>x.visible&&x.system===k)),'all five systems can coexist');
 await page.evaluate(()=>__atlas.setSystem('muscles',false));await page.evaluate(()=>__atlas.setSystem('bones',false));
 await page.evaluate(()=>__atlas.goTo('cv_heart'));await closeCard();
 `:phase==='vessels'?`
 await closeCard();await closeSettings();await page.locator('#bList').click();await page.locator('#q').fill('arteria carotis communis sinistra');
 await page.locator('[data-list-type="arteries"]').click();await page.locator('#dlist [data-id="cv_a_carotid_common_left"]').click();
 await page.waitForFunction(()=>__atlas.state.sel==='cv_a_carotid_common_left'&&!__atlas.inspect().loading.length,{timeout:18000});
 check(await page.evaluate(()=>__atlas.state.sel==='cv_a_carotid_common_left'),'Latin artery search and region navigation');
 let s=await snap();check(s.structures.filter(x=>x.kind==='s').length===8,'8 neck vessels loaded');
 await openCard();await page.locator('#structureOpacity').fill('55');check((await snap()).structures.find(x=>x.id==='cv_a_carotid_common_left').opacity===.55,'artery opacity');
 await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='cv_a_carotid_common_left'),'artery isolated');
 await settings();await page.locator('[data-side-view="right"]').click();await closeSettings();check((await snap()).structures.filter(x=>x.visible).every(x=>x.side!=='left'),'right side resets isolation');
 await page.locator('#bList').click();await page.locator('[data-list-type="veins"]').click();await page.locator('#q').fill('общая подвздошная вена');
 await page.locator('#dlist [data-id="cv_v_iliac_common_left"]').click();await page.waitForFunction(()=>__atlas.state.sel==='cv_v_iliac_common_left'&&!__atlas.inspect().loading.length,{timeout:18000});
 s=await snap();check(s.structures.filter(x=>x.kind==='s').length===12,'12 iliac models loaded');check(!Object.keys(s.errors).length,'all 50 models loaded across regions');
 await openCard();check((await page.locator('#sheet').innerText()).includes('Отток в'),'venous directed relation');
 await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='cv_v_iliac_common_left'),'vein isolated');await openCard();
 await page.locator('[data-structure-link="cv_v_cava_inferior"]').click();await page.waitForFunction(()=>__atlas.state.sel==='cv_v_cava_inferior');check(true,'venous relation switches region');
 await closeCard();await page.locator('#bList').click();await page.locator('[data-list-type="all"]').click();await page.locator('#q').fill('vena saphena magna dextra');await page.locator('#dlist [data-id="cv_v_saphenous_great_right"]').click();await openCard();
 await page.waitForFunction(()=>__atlas.state.sel==='cv_v_saphenous_great_right');check((await page.locator('#sheet').innerText()).includes('Только карточка'),'unavailable distal geometry explicit');
 `:`
 await closeCard();await closeSettings();await page.evaluate(()=>__atlas.goTo('radius_left'));await openCard();
 check(await page.locator('#bIso').count()===1,'existing educational radius selectable');await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='radius_left'),'bone isolation');
 await settings();await page.locator('[data-side-view="both"]').click();await closeSettings();
 await page.locator('#bList').click();await page.locator('[data-list-type="all"]').click();await page.locator('#q').fill('сесамовидная');
 check(await page.locator('[data-primary-sesamoids]').count()===1,'thumb sesamoid ranking preserved');
 await page.locator('#q').fill('biceps brachii');await page.locator('#dlist [data-id="biceps_brachii"]').first().click();await page.waitForFunction(()=>__atlas.state.sel==='biceps_brachii');await openCard();
 check((await page.locator('#sheet').innerText()).includes('biceps brachii'),'existing muscle search/card');await page.locator('#bIso').click();
 check((await snap()).structures.some(x=>x.visible&&x.id==='biceps_brachii'),'muscle isolation visible');
 await closeCard();await page.evaluate(()=>__atlas.goTo('frontal'));await openCard();
 check(await page.locator('#bBoneXray').count()===1,'bone transparency control retained');await page.locator('#bBoneXray').click();check(await page.evaluate(()=>__atlas.state.xrayBone==='frontal'),'bone xray state');
 await settings();await page.locator('#bHeadCut').click();await closeSettings();check(await page.evaluate(()=>__atlas.state.headCut.active),'skull cut control');
 check((await snap()).structures.filter(x=>x.visible).every(x=>x.bvh),'existing BVH retained');
 await page.evaluate(()=>__atlas.goTo('cv_heart'));await closeCard();
 `}
 check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'no page overflow');
 check(!await page.evaluate(()=>{const s=document.querySelector('#sheet');return s.scrollWidth>s.clientWidth+2;}),'no card overflow');
 check(!errors.length,'no page errors');
 await page.screenshot({path:${JSON.stringify(path.join(run,`cv-${phase}-${width}.png`))}});
 return {status:'passed',width:${width},phase:${JSON.stringify(phase)},checks,errors,elapsedMs:Date.now()-started};
} catch(e) {await page.screenshot({path:${JSON.stringify(path.join(run,`cv-${phase}-${width}-failure.png`))}}).catch(()=>{});return {status:'failed',width:${width},phase:${JSON.stringify(phase)},checks,errors,error:e.message,elapsedMs:Date.now()-started};}
finally{page.off('pageerror',onError);}
}`;
const filename=path.join(run,`cv-${phase}-${width}.mcp.js`);await fs.writeFile(filename,script,{flag:'wx'});console.log(filename);
