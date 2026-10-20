async (page) => {
  const width=await page.evaluate(()=>innerWidth),results=[],errors=[];
  const onError=e=>errors.push(String(e));page.on('pageerror',onError);
  async function card(){
    if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
    if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
  }
  try {
    for(const bone of ['sphenoid','temporal_right','temporal_left']){
      await page.evaluate(b=>{__atlas.activatePin(null);__atlas.goTo(b);},bone);await card();
      if(await page.evaluate(()=>Boolean(__atlas.state.isolate)))await page.locator('#bIso').click();
      if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
      await page.waitForFunction(b=>Boolean(__sharedCheck.clickPoint(b)),bone,{timeout:8000});
      const hit=await page.evaluate(b=>__sharedCheck.clickPoint(b),bone);
      await page.evaluate(()=>__atlas.select(null));
      await page.mouse.click(hit.x,hit.y);
      if(await page.evaluate(()=>__atlas.state.sel)!==bone)throw Error('Ray selection '+bone);
      await card();await page.locator('#bIso').click();await card();
      let snap=await page.evaluate(()=>__sharedCheck.snapshot());
      if(JSON.stringify(snap.visibleBones)!==JSON.stringify([bone]))throw Error('Isolation '+bone+JSON.stringify(snap));
      await page.locator('#bBoneXray').click();await card();snap=await page.evaluate(()=>__sharedCheck.snapshot());
      if(JSON.stringify(snap.xrayBones)!==JSON.stringify([bone]))throw Error('Transparency '+bone);
      await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
      results.push({bone,realRaySelection:true,isolation:true,transparency:true});
    }
    if(errors.length)throw Error(errors.join(';'));
    return {status:'passed',width,results,errors};
  }finally{page.off('pageerror',onError);}
}
