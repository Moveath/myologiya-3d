async(page)=>(async function browser(page,{dir}){
 const results=[];await page.route('**/*.js',r=>r.continue());
 try{for(const width of [1280,390]){
  const theme=width===1280?'dark':'light';await page.setViewportSize({width,height:width===390?844:900});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('ulna_left');});
  await page.evaluate(()=>{document.querySelector('#sheet').scrollTop=0;});
  if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
  const result=await page.evaluate(()=>{
   const joints=ATLAS.pins.filter(p=>p.leftForearmReview&&p.anatomicalEntity==='joint');
   for(const p of joints){__atlas.activatePin(p.id);if(!document.querySelector('.pinbox')?.textContent.includes('Модели левых лучевой и локтевой костей отсутствуют.'))throw Error(p.id);}
   __atlas.activatePin('extra_humerus_left_elbow_joint');document.querySelector('#sheet').scrollTop=0;
   return {jointNotes:joints.length,selected:__atlas.state.sel,pin:__atlas.state.pin,modelWarning:!!document.querySelector('[data-incomplete-models]')};
  });await page.screenshot({path:dir+'/left-card-top-'+width+'.png',fullPage:false});results.push({width,theme,...result});
 }return {status:'passed',results};}finally{await page.unrouteAll({behavior:'wait'});}
})(page,{"dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-left-forearm-final-mcp-2026-10-18T19-32-18-405Z-fA9jy9"})