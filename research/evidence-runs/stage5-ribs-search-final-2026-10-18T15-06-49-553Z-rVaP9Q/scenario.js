async(page)=>{
 const result=[],errors=[],check=(v,m)=>{if(!v)throw Error(m);};
 const onErr=e=>errors.push(String(e));page.on('pageerror',onErr);page.setDefaultTimeout(5000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 try{
  for(const [width,theme] of [[1280,'light'],[390,'dark']]){
   await page.setViewportSize({width,height:width===390?844:900});
   await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('trunk');await __atlas.goTo('sternum');});await card();
   const sheet=await page.locator('#sheet').innerText();check(sheet.includes('ОБРАЗОВАНИЯ КОСТИ ПО TA98 · 8'),'TA8');check(sheet.includes('ДОПОЛНИТЕЛЬНЫЕ АНАТОМИЧЕСКИЕ ОБРАЗОВАНИЯ · 24'),'Additional24');
   const records=await page.evaluate(()=>{
    const extra=ATLAS.pins.filter(p=>p.id.startsWith('extra_sternum_')),old=ATLAS.pins.find(p=>p.id.startsWith('extra_thoracic_12_'));
    const rows=[...extra,old,ATLAS.pins.find(p=>p.id==='thorax_sternum_A02_3_03_002')];
    for(const p of rows){const q=document.querySelector('#q');q.value=p.c||p.ru;q.dispatchEvent(new Event('input',{bubbles:true}));const hits=document.querySelectorAll('#dlist [data-pinjump="'+p.id+'"]');if(hits.length!==1)throw Error('Unique '+p.id);const expected=p.t==='ta'?'TA98':'ориентир';if(hits[0].querySelector('.tag').textContent!==expected)throw Error('Tag '+p.id);}
    return {additional:extra.length,old:old.id,checks:rows.length};
   });
   check(records.additional===24,'24 additional');if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();if(!await page.locator('#q').isVisible())await page.locator('#bList').click();
   await page.locator('#q').fill('Раздвоенный мечевидный отросток');await page.locator('#dlist [data-pinjump="extra_sternum_bifid_xiphoid_variant"]').click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)==='extra_sternum_bifid_xiphoid_variant','Real search selection');check((await page.locator('.pinbox').innerText()).includes('вариант'),'Variant card');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No overflow');
   const screenshot="C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-ribs-search-final-2026-10-18T15-06-49-553Z-rVaP9Q"+'/search-'+width+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';await page.screenshot({path:screenshot});
   result.push({width,theme,status:'passed',...records,ta98Count:8,realSearchClick:true,screenshot});
  }
  check(errors.length===0,'No page errors');return {status:'passed',results:result,errors,scope:'DOM input events for all 24 new + one old additional + TA98; one real search click per width. Earlier full UI covers all card links.'};
 }catch(e){return {status:'failed',results:result,error:String(e),errors};}finally{page.off('pageerror',onErr);}
}
