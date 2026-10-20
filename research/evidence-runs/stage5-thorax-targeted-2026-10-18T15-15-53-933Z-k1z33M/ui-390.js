async(page)=>{
 const results=[],errors=[],check=(x,m)=>{if(!x)throw Error(m);};page.setDefaultTimeout(7000);
 const onErr=e=>errors.push(String(e));const onConsole=m=>{if(m.type()==='error')errors.push(m.text());};page.on('pageerror',onErr);page.on('console',onConsole);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 try{
  // Routing disables page HTTP cache; previous persistent context had old data JS.
  await page.route('**/*.js',r=>r.continue());
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const width=390,theme="dark";
  await page.setViewportSize({width,height:width===390?844:900});await page.goto('http://127.0.0.1:8782/local.html?theme='+theme+'&review=targeted',{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('trunk');});
  const ids=await page.evaluate(async()=>{
   const rows=ATLAS.pins.filter(p=>/^thorax_rib_\d+_(right|left)_A02_3_02_012$/.test(p.id));
   for(const p of rows){await __atlas.goTo(p.b);__atlas.activatePin(p.id);const box=document.querySelector('.pinbox');if(!box.textContent.includes('Наличие и выраженность гребня на этом экземпляре не подтверждены'))throw Error('Presence warning '+p.id);if(p.p||p.inc||p.anatomyVerification!=='incomplete')throw Error('Invented acceptance '+p.id);}
   return rows.map(p=>p.id);
  });check(ids.length===22,'22 crest cases');
  for(const side of ['right','left']){await page.evaluate(async side=>{__atlas.activatePin(null);await __atlas.goTo('thorax_costal_cartilages_'+side);},side);await card();check((await page.locator('#sheet').innerText()).includes('I–VII не включены'),'Cartilage coverage '+side);}
  await close();if(!await page.locator('#q').isVisible())await page.locator('#bList').click();await page.locator('#q').fill('A02.3.02.012');check(await page.locator('#dlist [data-pinjump$="_A02_3_02_012"]').count()===22,'22 unique crest search results');
  await page.locator('#dlist [data-pinjump="thorax_rib_12_left_A02_3_02_012"]').click();await card();check(await page.evaluate(()=>__atlas.state.pin)==='thorax_rib_12_left_A02_3_02_012','XII search click');
  check((await page.locator('.pinbox').innerText()).includes('Для XI–XII ребра нельзя переносить'),'Atypical warning');
  await page.evaluate(async()=>{await __atlas.goTo('thoracic_12');__atlas.activatePin('shared_thorax_inferior_aperture');});await card();
  check((await page.locator('.pinbox').innerText()).includes('BP24/BP28 не покрывают'),'Shared limitation');check(await page.locator('.pinbox a[href="https://pubmed.ncbi.nlm.nih.gov/37982795/"]').count()===1,'Real source link');
  await page.locator('.pinbox [data-gobone="sternum"]').click();await page.waitForFunction(()=>__atlas.state.sel==='sternum'&&__atlas.state.pin==='shared_thorax_inferior_aperture');await card();
  await page.locator('#bIso').click();await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await card();
  const whole=await page.locator('#sheet').textContent();check(whole.includes('В типовой учебной схеме'),'Whole term qualifier');check(whole.includes('фактический состав и соединения вариабельны'),'Arch variation');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No overflow');check(errors.length===0,'No console errors');
  const screenshot="C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-thorax-targeted-2026-10-18T15-15-53-933Z-k1z33M"+'/targeted-'+width+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';await page.screenshot({path:screenshot});
  return {status:'passed',width,theme,crests:ids.length,cartilageCards:2,searchResults:22,realSearchAndSharedClicks:true,isolationTransparencyClicks:true,consoleErrors:errors,screenshot,cacheDisabled:true,acceptedCoordinates:0,scope:'Targeted data/card regression; prior BVH/clipping geometry checks reused, protected files unchanged.'};
 }catch(e){return {status:'failed',error:String(e),errors};}
 finally{page.off('pageerror',onErr);page.off('console',onConsole);await page.unroute('**/*.js');await page.unroute('https://fonts.googleapis.com/**');}
}
