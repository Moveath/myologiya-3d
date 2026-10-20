async (page) => {
  const width=await page.evaluate(()=>innerWidth),results=[],errors=[];
  const onError=e=>errors.push(String(e));page.on('pageerror',onError);
  async function card(){
    if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
    if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
  }
  try {
    for(const bone of ['zygomatic_right','zygomatic_left','nasal_right','nasal_left','lacrimal_right','lacrimal_left','inferior_concha_right','inferior_concha_left','vomer']){
      await page.evaluate(b=>{__atlas.activatePin(null);__atlas.goTo(b);},bone);await card();
      if(await page.evaluate(()=>Boolean(__atlas.state.isolate)))await page.locator('#bIso').click();
      const internal=bone.startsWith('inferior_concha')||bone==='vomer';
      if(internal)await page.locator('#bIso').click();
      if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
      await page.waitForFunction(b=>Boolean(__sharedCheck.clickPoint(b)),bone,{timeout:8000});
      const hit=await page.evaluate(b=>__sharedCheck.clickPoint(b),bone);
      await page.evaluate(()=>__atlas.select(null));
      await page.mouse.click(hit.x,hit.y);
      if(await page.evaluate(()=>__atlas.state.sel)!==bone)throw Error('Ray selection '+bone);
      await card();if(!await page.evaluate(()=>Boolean(__atlas.state.isolate)))await page.locator('#bIso').click();await card();
      let snap=await page.evaluate(()=>__sharedCheck.snapshot());
      if(JSON.stringify(snap.visibleBones)!==JSON.stringify([bone]))throw Error('Isolation '+bone+JSON.stringify(snap));
      await page.locator('#bBoneXray').click();await card();snap=await page.evaluate(()=>__sharedCheck.snapshot());
      if(JSON.stringify(snap.xrayBones)!==JSON.stringify([bone]))throw Error('Transparency '+bone);
      await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
      results.push({bone,realRaySelection:true,rayContext:internal?'isolated: internal bone occluded in assembled skull':'assembled skull',isolation:true,transparency:true});
    }
    if(errors.length)throw Error(errors.join(';'));
    return {status:'passed',width,results,errors};
  }finally{page.off('pageerror',onError);}
}
