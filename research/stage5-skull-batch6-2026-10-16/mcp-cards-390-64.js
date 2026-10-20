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
  for(const id of (finish?['head_maxilla_right_A02_1_12_021','head_maxilla_left_A02_1_12_021','head_palatine_right_A02_1_13_017','head_palatine_left_A02_1_13_017']:[])){
   if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
   await page.locator('#bList').click();await page.locator('#q').fill(id.includes('maxilla')?'A02.1.12.021':'A02.1.13.017');
   const hit=page.locator('#dlist [data-pinjump="'+id+'"]');if(await hit.count()!==1)throw Error('Search identity '+id);
   await hit.click();await card(page);if(await page.evaluate(()=>__atlas.state.pin)!==id)throw Error('Search selection '+id);
  }
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');
  if(errors.length)throw Error(errors.join(';'));
  if(finish){await page.locator('.pinbox').scrollIntoViewIfNeeded();await page.screenshot({path:shot,timeout:10000});}
  return {status:'passed',width,classifiedCards:rows.length,testedIDs:rows.map(p=>p.id),historicalLabels,searchedInstances:finish?4:0,errors,shot:finish?shot:null};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
})(page,{"width":390,"rows":[{"id":"head_palatine_right_A02_1_13_011","bone":"palatine_right","code":"A02.1.13.011","kind":"volume","reason":"Глазничный отросток имеет несколько соединительных и свободных поверхностей; только верхняя глазничная грань участвует в дне глазницы."},{"id":"head_palatine_right_A02_1_13_012","bone":"palatine_right","code":"A02.1.13.012","kind":"volume","reason":"Клиновидный отросток — собственная костная пластинка с несколькими гранями; не весь нёбно-влагалищный канал."},{"id":"head_palatine_right_A02_1_13_013","bone":"palatine_right","code":"A02.1.13.013","kind":"volume","reason":"Горизонтальная пластинка — костная часть с двумя гранями и краями; не всё твёрдое нёбо и не одна поверхность."},{"id":"head_palatine_right_A02_1_13_016","bone":"palatine_right","code":"A02.1.13.016","kind":"space","reason":"Малые нёбные отверстия — группа выходов каналов на нижней стороне пирамидального отростка, не сами каналы."},{"id":"head_palatine_right_A02_1_13_017","bone":"palatine_right","code":"A02.1.13.017","kind":"volume","reason":"Костный вклад горизонтальной пластинки в общую заднюю носовую ость; не отдельная математическая вершина справа или слева."},{"id":"head_palatine_right_A02_1_13_018","bone":"palatine_right","code":"A02.1.13.018","kind":"volume","reason":"Носовой гребень — возвышающийся костный край пластинки для соединения с сошником; не сам сошник или срединный шов."},{"id":"head_palatine_right_A02_1_13_019","bone":"palatine_right","code":"A02.1.13.019","kind":"volume","reason":"Нёбный гребень — поперечный костный рельеф у заднего края ротовой поверхности; не линия свободного заднего края нёба."},{"id":"head_palatine_left_A02_1_13_002","bone":"palatine_left","code":"A02.1.13.002","kind":"volume","reason":"Перпендикулярная пластинка имеет толщину, носовую и верхнечелюстную поверхности; одна грань не представляет всю пластинку."},{"id":"head_palatine_left_A02_1_13_005","bone":"palatine_left","code":"A02.1.13.005","kind":"space","reason":"Промежуток между глазничным и клиновидным отростками — собственная открытая вырезка; не автоматически весь контур собранного клиновидно-нёбного отверстия."},{"id":"head_palatine_left_A02_1_13_006","bone":"palatine_left","code":"A02.1.13.006","kind":"area","reason":"Большая нёбная борозда — открытое ложе на верхнечелюстной стороне пластинки; не вся полость общего канала."},{"id":"head_palatine_left_A02_1_13_007","bone":"palatine_left","code":"A02.1.13.007","kind":"volume","reason":"Пирамидальный отросток — костная часть на соединении пластинок с поверхностями и внутренними каналами."},{"id":"head_palatine_left_A02_1_13_009","bone":"palatine_left","code":"A02.1.13.009","kind":"volume","reason":"Нижний раковинный гребень — костный рельеф носовой поверхности для нижней раковины, не сама раковина."},{"id":"head_palatine_left_A02_1_13_010","bone":"palatine_left","code":"A02.1.13.010","kind":"volume","reason":"Верхний решётчатый гребень — костный рельеф для средней раковины; не линия границы всего среднего носового хода."},{"id":"head_palatine_left_A02_1_13_011","bone":"palatine_left","code":"A02.1.13.011","kind":"volume","reason":"Глазничный отросток имеет несколько соединительных и свободных поверхностей; только верхняя глазничная грань участвует в дне глазницы."},{"id":"head_palatine_left_A02_1_13_012","bone":"palatine_left","code":"A02.1.13.012","kind":"volume","reason":"Клиновидный отросток — собственная костная пластинка с несколькими гранями; не весь нёбно-влагалищный канал."},{"id":"head_palatine_left_A02_1_13_013","bone":"palatine_left","code":"A02.1.13.013","kind":"volume","reason":"Горизонтальная пластинка — костная часть с двумя гранями и краями; не всё твёрдое нёбо и не одна поверхность."}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch6\\390-cards.png"});}
