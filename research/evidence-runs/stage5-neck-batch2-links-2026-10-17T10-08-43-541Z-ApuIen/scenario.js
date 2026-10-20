async(page)=>(async function scenario(page,dir){
 const results=[];const errors=[];const error=e=>errors.push(String(e));
 page.on('pageerror',error);page.setDefaultTimeout(8000);
 await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const check=(v,m)=>{if(!v)throw Error(m);};
 try{
  for(const [width,theme]of [[1280,'light'],[390,'dark']]){
   await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
   await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
   await page.evaluate(async()=>{await __atlas.enterSection('neck');});
   const rows=await page.evaluate(()=>ATLAS.pins.filter(p=>['extra_axis_dens_neck','extra_hyoid_body_border_superior','extra_hyoid_body_border_inferior'].includes(p.id)).map(p=>({id:p.id,b:p.b,ru:p.ru,parent:p.partOf})));
   let parents=0,searches=0;
   for(const p of rows){
    await page.evaluate(async p=>{await __atlas.goTo(p.b,null,p.id);},p);await card();
    await page.locator('.pinbox [data-related-pin="'+p.parent+'"]').click();
    check(await page.evaluate(()=>__atlas.state.pin)===p.parent,'Parent link '+p.id);parents++;
    await close();await page.locator('#bList').click();await page.locator('#q').fill(p.ru);
    const hit=page.locator('#dlist [data-pinjump="'+p.id+'"]');check(await hit.count()===1,'Unique new search '+p.id);await hit.click();await card();
    check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Search selection '+p.id);searches++;
    check(await page.locator('.pin[data-pinid="'+p.id+'"]').count()===0,'No invented marker');
   }
   await page.evaluate(async()=>{await __atlas.goTo('axis',null,'shared_neck_intervertebral_c2_c3_right');});await card();
   await page.locator('.pinbox [data-related-pin="neck_cervical_3_A02_2_01_009"]').click();
   check(await page.evaluate(()=>__atlas.state.sel)==='cervical_3','Related lower vertebra');
   check(await page.evaluate(()=>__atlas.state.pin)==='neck_cervical_3_A02_2_01_009','Related superior notch');
   await page.evaluate(async()=>{await __atlas.goTo('hyoid',null,'extra_hyoid_body_border_superior');});await card();
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Overflow');
   const shot=dir+'/links-'+width+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';await page.screenshot({path:shot});
   results.push({width,theme,status:'passed',parents,searches,notchTransition:true,screenshot:shot});
  }
  check(errors.length===0,'Page errors');return {status:'passed',results,errors};
 }catch(e){return {status:'failed',error:String(e),results,errors};}
 finally{page.off('pageerror',error);await page.unroute('https://fonts.googleapis.com/**');}
})(page,"C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-neck-batch2-links-2026-10-17T10-08-43-541Z-ApuIen")