async(page)=>{async function card(page){
 if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
 if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
};return (async function cardsBrowser(page,{width,rows,shot,finish}){
 const errors=[],onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);
 const links=[];
 try{
  await page.setViewportSize({width,height:900});await page.waitForFunction(()=>window.__ready);
  for(const p of rows){
   await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},p.bone);await card(page);
   const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');if(await chip.count()!==1)throw Error('Duplicate/missing '+p.id);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card(page);
   if(await page.locator('.pinbox .landmark-geometry').getAttribute('data-geometry-kind')!==p.kind)throw Error('Wrong type '+p.id);
   if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Lost ID '+p.id);
   if(p.bilateral&&await page.locator('.pinbox [data-laterality="bilateral_on_unpaired_bone"]').count()!==1)throw Error('Bilateral limit '+p.id);
   if(p.extra){
    if(!(await page.locator('.pinbox').textContent()).includes('код TA98 не присвоен'))throw Error('False code '+p.id);
    if(await page.locator('.pinbox [data-detail-mode="education"]').count())throw Error('Undefined education target');
    if(await page.evaluate(id=>ATLAS.pins.find(p=>p.id===id).p!==undefined,p.id))throw Error('Invented coordinate');
    for(const related of p.related){
     await page.evaluate(p=>__atlas.goTo(p.bone,null,p.id),p);await card(page);
     const link=page.locator('.pinbox [data-related-pin="'+related+'"]');await link.scrollIntoViewIfNeeded();await link.click();await card(page);
     const state=await page.evaluate(id=>({pin:__atlas.state.pin,sel:__atlas.state.sel,targetBone:ATLAS.pins.find(p=>p.id===id).b}),related);
     if(state.pin!==related||state.sel!==state.targetBone&&state.sel!==p.bone)throw Error('Related navigation '+JSON.stringify(state));
     links.push({from:p.id,to:related,selectedBone:state.sel});
    }
    if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
    await page.locator('#bList').click();await page.locator('#q').fill(p.ru);
    const hit=page.locator('#dlist [data-pinjump="'+p.id+'"]');if(await hit.count()!==1)throw Error('Search '+p.id);
    await hit.click();await card(page);if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Search selection '+p.id);
   }
  }
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  if(finish){await page.locator('.pinbox').scrollIntoViewIfNeeded();await page.screenshot({path:shot,timeout:10000});}
  return {status:'passed',width,testedIDs:rows.map(p=>p.id),supplementaryCards:rows.filter(p=>p.extra).length,links,errors,shot:finish?shot:null};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
})(page,{"width":390,"rows":[{"id":"head_mandible_A02_1_15_011","bone":"mandible","code":"A02.1.15.011","ru":"Нижняя подбородочная ость","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_012","bone":"mandible","code":"A02.1.15.012","ru":"Челюстно-подъязычная линия","kind":"volume","extra":false,"related":[],"bilateral":true},{"id":"head_mandible_A02_1_15_013","bone":"mandible","code":"A02.1.15.013","ru":"Нижнечелюстной валик","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_014","bone":"mandible","code":"A02.1.15.014","ru":"Подъязычная ямка","kind":"area","extra":false,"related":[],"bilateral":true},{"id":"head_mandible_A02_1_15_015","bone":"mandible","code":"A02.1.15.015","ru":"Поднижнечелюстная ямка","kind":"area","extra":false,"related":[],"bilateral":true},{"id":"head_mandible_A02_1_15_016","bone":"mandible","code":"A02.1.15.016","ru":"Альвеолярная часть","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_017","bone":"mandible","code":"A02.1.15.017","ru":"Альвеолярная дуга","kind":"line","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_018","bone":"mandible","code":"A02.1.15.018","ru":"Зубные альвеолы","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_019","bone":"mandible","code":"A02.1.15.019","ru":"Межальвеолярные перегородки","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_020","bone":"mandible","code":"A02.1.15.020","ru":"Межкорневые перегородки","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_021","bone":"mandible","code":"A02.1.15.021","ru":"Альвеолярные возвышения","kind":"volume","extra":false,"related":[],"bilateral":false},{"id":"head_mandible_A02_1_15_022","bone":"mandible","code":"A02.1.15.022","ru":"Позадимолярный треугольник","kind":"area","extra":false,"related":[],"bilateral":true}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch8\\390-cards.png"});}
