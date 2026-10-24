async(page)=>{
const started=Date.now(),checks=[],errors=[];page.setDefaultTimeout(7000);page.setDefaultNavigationTimeout(12000);
const onError=e=>errors.push(e.message);page.on('pageerror',onError);
const check=(value,name)=>{checks.push({name,passed:!!value});if(!value)throw Error(name);if(Date.now()-started>45000)throw Error('45s scenario budget');};
const openCard=async()=>{if(390<900&&await page.locator('#closeMobileCard').isHidden())await page.locator('#mobileCard').click();};
const closeCard=async()=>{if(390<900&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
const settings=async()=>{await closeCard();if(390<900&&await page.locator('#systemControls').isHidden())await page.locator('#bOptions').click();};
const closeSettings=async()=>{if(390<900&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
const snap=()=>page.evaluate(()=>__atlas.inspect());
try {
 await page.setViewportSize({width:390,height:844});
 
 await page.unrouteAll({behavior:'ignoreErrors'});await page.context().unrouteAll({behavior:'ignoreErrors'});
 await page.goto('http://127.0.0.1:8783/local.html?cv=390&theme=dark',{waitUntil:'domcontentloaded'});
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
 
 check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'no page overflow');
 check(!await page.evaluate(()=>{const s=document.querySelector('#sheet');return s.scrollWidth>s.clientWidth+2;}),'no card overflow');
 check(!errors.length,'no page errors');
 await page.screenshot({path:"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\cardiovascular-ui-r2-2026-10-22T12-24-27-891Z-4dzKc9\\cv-heart-390.png"});
 return {status:'passed',width:390,phase:"heart",checks,errors,elapsedMs:Date.now()-started};
} catch(e) {await page.screenshot({path:"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\cardiovascular-ui-r2-2026-10-22T12-24-27-891Z-4dzKc9\\cv-heart-390-failure.png"}).catch(()=>{});return {status:'failed',width:390,phase:"heart",checks,errors,error:e.message,elapsedMs:Date.now()-started};}
finally{page.off('pageerror',onError);}
}