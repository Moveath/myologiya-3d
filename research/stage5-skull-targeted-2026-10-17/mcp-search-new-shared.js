async(page)=>{
 const result=[],errors=[],onError=e=>errors.push(String(e));page.on('pageerror',onError);
 async function card(){
  if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
  if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
 }
 try{
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:900});
   for(const id of ['shared_skull_nasal_bone_crest','shared_skull_050','shared_skull_087']){
    const p=await page.evaluate(id=>{const p=ATLAS.pins.find(p=>p.id===id);return {id:p.id,ru:p.ru,b:p.b,bones:p.relations.map(r=>r.bone).sort()};},id);
    if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
    await page.locator('#bList').click();await page.locator('#q').fill(p.ru);
    const hit=page.locator('#dlist [data-pinjump="'+id+'"]');if(await hit.count()!==1)throw Error('Search duplicate/missing '+id);
    await hit.click();await card();if(await page.evaluate(()=>__atlas.state.pin)!==id)throw Error('Lost selection');
    if(await page.evaluate(()=>Boolean(__atlas.state.isolate)))await page.locator('#bIso').click();
    await page.locator('#bIso').click();await card();
    const selected=await page.evaluate(()=>__atlas.state.sel),iso=await page.evaluate(()=>__sharedCheck.snapshot());
    if(JSON.stringify(iso.visibleBones.sort())!==JSON.stringify(p.bones))throw Error('Isolation must retain all contributing bones '+id);
    await page.locator('#bBoneXray').click();await card();const xray=await page.evaluate(()=>__sharedCheck.snapshot());
    if(JSON.stringify(xray.xrayBones.sort())!==JSON.stringify(p.bones))throw Error('Transparency must retain all contributing bones '+id);
    await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await card();
    if(await page.locator('.pin[data-pinid="'+id+'"]').count()!==0)throw Error('Invented marker');
    result.push({width,id,search:true,isolation:true,transparency:true,noInventedMarker:true});
   }
  }
  if(errors.length)throw Error(errors.join(';'));
  return {status:'passed',result,errors};
 }finally{page.off('pageerror',onError);}
}
