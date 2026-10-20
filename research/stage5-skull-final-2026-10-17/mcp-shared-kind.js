async(page)=>{
 const results=[],errors=[];const onError=e=>errors.push(String(e));page.on('pageerror',onError);
 await page.route('**/pins-shared.js',async route=>{
  const response=await route.fetch({url:route.request().url()+'?audit=20261017-shared-kind'});
  await route.fulfill({response});
 });
 try{
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:900});
   await page.goto('http://127.0.0.1:8782/local.html?theme='+(width===1280?'dark':'light'),{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready);await page.evaluate(()=>__atlas.enterSection('head'));
   const rows=await page.evaluate(()=>ATLAS.pins.filter(p=>p.id.startsWith('shared_')&&p.geometryKind==='unknown').map(p=>({id:p.id,bone:p.b})));
   if(rows.length!==32)throw Error('Expected 32 explicitly unresolved shared types');
   for(const row of rows){
    await page.evaluate(r=>__atlas.goTo(r.bone,null,r.id),row);
    if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
    if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
    const message=page.locator('.pinbox [data-geometry-kind="unknown"]');
    if(await message.count()!==1||!(await message.textContent()).includes('не уточнён'))throw Error('Missing uncertainty notice '+row.id);
    if(await page.evaluate(()=>__atlas.state.pin)!==row.id)throw Error('Lost canonical selection');
   }
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
   results.push({width,testedIDs:rows.map(r=>r.id)});
  }
  if(errors.length)throw Error(errors.join(';'));
  return {status:'passed',results,errors,scientificClassificationAccepted:false};
 }finally{page.off('pageerror',onError);await page.unroute('**/pins-shared.js');}
}
