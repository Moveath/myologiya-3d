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
 
 check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'no page overflow');
 check(!await page.evaluate(()=>{const s=document.querySelector('#sheet');return s.scrollWidth>s.clientWidth+2;}),'no card overflow');
 check(!errors.length,'no page errors');
 await page.screenshot({path:"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\cardiovascular-ui-r2-2026-10-22T12-24-27-891Z-4dzKc9\\cv-regression-1280.png"});
 return {status:'passed',width:1280,phase:"regression",checks,errors,elapsedMs:Date.now()-started};
} catch(e) {await page.screenshot({path:"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\cardiovascular-ui-r2-2026-10-22T12-24-27-891Z-4dzKc9\\cv-regression-1280-failure.png"}).catch(()=>{});return {status:'failed',width:1280,phase:"regression",checks,errors,error:e.message,elapsedMs:Date.now()-started};}
finally{page.off('pageerror',onError);}
}