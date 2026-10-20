async(page)=>{async function card(page){
 if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
 const more=page.locator('#bMore');if(await more.isVisible()&&await more.textContent()==='Подробнее')await more.click();
};return (async function cardsBrowser(page,{width,rows,shot,finish}){
 const errors=[],onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);
 try{
  await page.setViewportSize({width,height:900});await page.waitForFunction(()=>window.__ready);
  let bone=null,historicalLabels=0;
  for(const p of rows){
   if(bone!==p.bone){await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},p.bone);bone=p.bone;}
   await card(page);const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');
   if(await chip.count()!==1)throw Error('Missing or duplicate '+p.id);
   await chip.scrollIntoViewIfNeeded();await chip.click();await card(page);
   if(await page.locator('.pinbox .landmark-geometry').getAttribute('data-geometry-kind')!==p.kind)throw Error('Wrong type '+p.id);
   if(await page.evaluate(()=>__atlas.state.pin)!==p.id)throw Error('Lost selected ID '+p.id);
   const wasComplete=await page.evaluate(p=>ATLAS.headGeometry?.[p.bone+':'+p.code]==='complete',p);
   if(wasComplete){
    const message=page.locator('.pinbox [data-review-scope="historical"]');
    if(await message.count()!==1||!(await message.textContent()).includes('текущей проверке не принята'))throw Error('Misleading old extent status '+p.id);
    historicalLabels++;
   }
  }
  for(const id of (finish?['head_sphenoid_A02_1_05_052','head_temporal_right_A02_1_06_045','head_temporal_left_A02_1_06_045']:[])){
   if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
   await page.locator('#bList').click();await page.locator('#q').fill(id.includes('sphenoid')?'A02.1.05.052':'A02.1.06.045');
   const hit=page.locator('#dlist [data-pinjump="'+id+'"]');if(await hit.count()!==1)throw Error('Search identity '+id);
   await hit.click();await card(page);if(await page.evaluate(()=>__atlas.state.pin)!==id)throw Error('Search selection '+id);
  }
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  if(finish){await page.locator('.pinbox').scrollIntoViewIfNeeded();await page.screenshot({path:shot,timeout:10000});}
  return {status:'passed',width,classifiedCards:rows.length,testedIDs:rows.map(p=>p.id),historicalLabels,searchedInstances:finish?3:0,errors,shot:finish?shot:null};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
})(page,{"width":1280,"rows":[{"id":"head_temporal_right_A02_1_06_046","bone":"temporal_right","code":"A02.1.06.046","kind":"volume","reason":"Внутрияремный отросток — костный выступ края, не произвольная линия разделения всего отверстия."},{"id":"head_temporal_right_A02_1_06_047","bone":"temporal_right","code":"A02.1.06.047","kind":"volume","reason":"Шиловидный отросток — костный объём; его вершина и возможное окостенение связки не заменяют весь отросток."},{"id":"head_temporal_right_A02_1_06_048","bone":"temporal_right","code":"A02.1.06.048","kind":"space","reason":"Шилососцевидное отверстие — выход лицевого канала; не весь лицевой канал и не точка между отростками."},{"id":"head_temporal_right_A02_1_06_050","bone":"temporal_right","code":"A02.1.06.050","kind":"area","reason":"Каменистая ямочка — небольшое углублённое костное ложе; начинающийся здесь каналец является отдельной записью."},{"id":"head_temporal_right_A02_1_06_037","bone":"temporal_right","code":"A02.1.06.037","kind":"line","reason":"Задний край разграничивает заднюю и нижнюю грани; его борозды и вырезки учитываются отдельными структурами."},{"id":"head_temporal_right_A02_1_06_039","bone":"temporal_right","code":"A02.1.06.039","kind":"area","reason":"Собственная яремная вырезка — участок выемки височной кости у края; не всё совместное яремное отверстие. Два каталожных кода не означают две вырезки."},{"id":"head_temporal_right_A02_1_06_052","bone":"temporal_right","code":"A02.1.06.052","kind":"volume","reason":"Барабанная часть — изогнутая костная пластинка с несколькими поверхностями, не весь наружный слуховой проход."},{"id":"head_temporal_right_A02_1_06_053","bone":"temporal_right","code":"A02.1.06.053","kind":"volume","reason":"Барабанное кольцо в этой карточке костное и незамкнутое; его вещество не равно фиброзному кольцу перепонки или линии борозды."},{"id":"head_temporal_right_A02_1_06_054","bone":"temporal_right","code":"A02.1.06.054","kind":"space","reason":"Наружное слуховое отверстие — вход в костный проход; не весь проход и не наружное ухо."},{"id":"head_temporal_right_A02_1_06_056","bone":"temporal_right","code":"A02.1.06.056","kind":"volume","reason":"Большая барабанная ость — передний костный выступ кольца; отдельный от борозды и места фиксации мягкой ткани."},{"id":"head_temporal_right_A02_1_06_057","bone":"temporal_right","code":"A02.1.06.057","kind":"volume","reason":"Малая барабанная ость — задний костный выступ кольца; не точка и не синоним большой ости."},{"id":"head_temporal_right_A02_1_06_058","bone":"temporal_right","code":"A02.1.06.058","kind":"area","reason":"Барабанная борозда — узкое костное ложе прикрепления кольца перепонки; осевая линия не передаёт ширину ложа."},{"id":"head_temporal_right_A02_1_06_059","bone":"temporal_right","code":"A02.1.06.059","kind":"space","reason":"Барабанная вырезка — незамкнутый верхний промежуток костного кольца; не сама ненатянутая часть перепонки."},{"id":"head_temporal_right_A02_1_06_060","bone":"temporal_right","code":"A02.1.06.060","kind":"volume","reason":"Влагалище шиловидного отростка — костная пластинка барабанной части; не соединительнотканная оболочка и не сам отросток."},{"id":"head_temporal_right_A02_1_06_063","bone":"temporal_right","code":"A02.1.06.063","kind":"area","reason":"Теменная вырезка — собственная углублённая область края на стыке частей височной кости; не вся межкостная линия шва."},{"id":"head_temporal_left_A02_1_06_002","bone":"temporal_left","code":"A02.1.06.002","kind":"volume","reason":"Каменистая часть — костная часть с внутренними полостями и наружными гранями, не одна грань."}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch5\\1280-cards.png"});}
