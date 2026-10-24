async(page)=>{
const started=Date.now(),checks=[],errors=[];page.setDefaultTimeout(7000);page.setDefaultNavigationTimeout(12000);
const onError=e=>errors.push(e.message);page.on('pageerror',onError);
const check=(value,name)=>{checks.push({name,passed:!!value});if(!value)throw Error(name);if(Date.now()-started>45000)throw Error('45s scenario budget');};
const openCard=async()=>{if(1280<900&&await page.locator('#closeMobileCard').isHidden())await page.locator('#mobileCard').click();};
const closeCard=async()=>{if(1280<900&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
const settings=async()=>{await closeCard();if(1280<900&&await page.locator('#systemControls').isHidden())await page.locator('#bOptions').click();};
const closeSettings=async()=>{if(1280<900&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
const snap=()=>page.evaluate(()=>__atlas.inspect());
try {
 await page.setViewportSize({width:1280,height:900});
 
 await closeCard();await closeSettings();await page.locator('#bList').click();await page.locator('#q').fill('arteria carotis communis sinistra');
 await page.locator('[data-list-type="arteries"]').click();await page.locator('#dlist [data-id="cv_a_carotid_common_left"]').click();
 await page.waitForFunction(()=>!__atlas.inspect().loading.length,{timeout:18000});
 check(await page.evaluate(()=>__atlas.state.sel==='cv_a_carotid_common_left'),'Latin artery search and region navigation');
 let s=await snap();check(s.structures.filter(x=>x.kind==='s').length===8,'8 neck vessels loaded');
 await openCard();await page.locator('#structureOpacity').fill('55');check((await snap()).structures.find(x=>x.id==='cv_a_carotid_common_left').opacity===.55,'artery opacity');
 await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='cv_a_carotid_common_left'),'artery isolated');
 await settings();await page.locator('[data-side-view="right"]').click();await closeSettings();check((await snap()).structures.filter(x=>x.visible).every(x=>x.side!=='left'),'right side resets isolation');
 await page.locator('#bList').click();await page.locator('[data-list-type="veins"]').click();await page.locator('#q').fill('общая подвздошная вена');
 await page.locator('#dlist [data-id="cv_v_iliac_common_left"]').click();await page.waitForFunction(()=>!__atlas.inspect().loading.length,{timeout:18000});
 s=await snap();check(s.structures.filter(x=>x.kind==='s').length===12,'12 iliac models loaded');check(!Object.keys(s.errors).length,'all 50 models loaded across regions');
 await openCard();check((await page.locator('#sheet').innerText()).includes('Отток в'),'venous directed relation');
 await page.locator('#bIso').click();check((await snap()).structures.filter(x=>x.visible).every(x=>x.id==='cv_v_iliac_common_left'),'vein isolated');await openCard();
 await page.locator('[data-structure-link="cv_v_cava_inferior"]').click();check(await page.evaluate(()=>__atlas.state.sel==='cv_v_cava_inferior'),'venous relation switches region');
 await closeCard();await page.locator('#bList').click();await page.locator('[data-list-type="all"]').click();await page.locator('#q').fill('vena saphena magna dextra');await page.locator('#dlist [data-id="cv_v_saphenous_great_right"]').click();await openCard();
 check((await page.locator('#sheet').innerText()).includes('Только карточка'),'unavailable distal geometry explicit');
 
 check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'no page overflow');
 check(!await page.evaluate(()=>{const s=document.querySelector('#sheet');return s.scrollWidth>s.clientWidth+2;}),'no card overflow');
 check(!errors.length,'no page errors');
 await page.screenshot({path:"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\cardiovascular-first-integration-2026-10-22T11-41-39-801Z-wDXHnD\\cv-vessels-1280.png"});
 return {status:'passed',width:1280,phase:"vessels",checks,errors,elapsedMs:Date.now()-started};
} catch(e) {await page.screenshot({path:"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\cardiovascular-first-integration-2026-10-22T11-41-39-801Z-wDXHnD\\cv-vessels-1280-failure.png"}).catch(()=>{});return {status:'failed',width:1280,phase:"vessels",checks,errors,error:e.message,elapsedMs:Date.now()-started};}
finally{page.off('pageerror',onError);}
}