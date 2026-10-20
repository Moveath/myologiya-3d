async(page)=>{
 const out=[],errors=[],check=(v,m)=>{if(!v)throw Error(m);};
 const handler=e=>errors.push(String(e));page.on('pageerror',handler);
 const consoleHandler=m=>{if(m.type()==='error')errors.push(m.text());};page.on('console',consoleHandler);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const search=async(q)=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();if(!await page.locator('#q').isVisible())await page.locator('#bList').click();await page.locator('#q').fill(q);};
 try{
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  for(const [width,theme]of [[1280,'light'],[390,'dark']]){
   await page.setViewportSize({width,height:width===390?844:900});
   await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('trunk');await __atlas.goTo('sternum');});
   const records=await page.evaluate(()=>ATLAS.pins.filter(p=>p.id.startsWith('extra_sternum_')).map(p=>({id:p.id,ru:p.ru})));check(records.length===24,'24 additional');
   for(const p of records){
    await search(p.ru);const hit=page.locator('#dlist [data-pinjump="'+p.id+'"]');check(await hit.count()===1,'Unique '+p.id);
    check(await hit.locator('.tag').innerText()==='ориентир','Additional search label '+p.id);await hit.click();
    check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Selected '+p.id);await card();check(await page.locator('.pinbox').innerText().then(t=>t.includes(p.ru)),'Card '+p.id);
   }
   const old=await page.evaluate(()=>{const p=ATLAS.pins.find(p=>p.id.startsWith('extra_thoracic_12_'));return {id:p.id,ru:p.ru};});
   await search(old.ru);const oldHit=page.locator('#dlist [data-pinjump="'+old.id+'"]');check(await oldHit.locator('.tag').innerText()==='ориентир','Existing additional label');await oldHit.click();check(await page.evaluate(()=>__atlas.state.pin)===old.id,'Old additional selection');
   await search('A02.3.03.002');const ta=page.locator('#dlist [data-pinjump="thorax_sternum_A02_3_03_002"]');check(await ta.locator('.tag').innerText()==='TA98','Preserve TA label');await ta.click();await card();
   await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('sternum');});await card();
   const body=await page.locator('#sheet').innerText();check(body.includes('ОБРАЗОВАНИЯ КОСТИ ПО TA98 · 8'),'Eight real TA entries');check(body.includes('ДОПОЛНИТЕЛЬНЫЕ АНАТОМИЧЕСКИЕ ОБРАЗОВАНИЯ · 24'),'24 separate descriptive entries');
   check(await page.locator('#sheet [data-pinid^="extra_sternum_"]').count()===24,'24 unique own chips');check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No overflow');
   const screenshot="C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-ribs-catalogue-ui-2026-10-18T14-57-17-138Z-zKoyoA"+'/catalogue-'+width+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';await page.screenshot({path:screenshot});
   out.push({width,theme,newAdditionalSearchAndClicks:24,oldAdditionalSearchAndClick:true,ta98TagPreserved:true,ownTa98:8,additional:24,screenshot,status:'passed'});
  }
  check(errors.length===0,'No console errors');return {status:'passed',results:out,errors};
 }catch(e){return {status:'failed',results:out,error:String(e),errors};}
 finally{page.off('pageerror',handler);page.off('console',consoleHandler);await page.unroute('https://fonts.googleapis.com/**');}
}
