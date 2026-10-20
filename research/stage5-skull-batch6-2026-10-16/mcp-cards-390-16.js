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
})(page,{"width":390,"rows":[{"id":"head_maxilla_right_A02_1_12_028","bone":"maxilla_right","code":"A02.1.12.028","kind":"volume","reason":"Скуловой отросток — костный выступ с толщиной; его шовная поверхность является только частью."},{"id":"head_maxilla_right_A02_1_12_029","bone":"maxilla_right","code":"A02.1.12.029","kind":"volume","reason":"Нёбный отросток — горизонтальная костная пластинка; его носовая и ротовая поверхности не заменяют весь объём."},{"id":"head_maxilla_right_A02_1_12_030","bone":"maxilla_right","code":"A02.1.12.030","kind":"volume","reason":"Носовой гребень на медиальном крае отростка — костный рельеф, а не сам сошник или линия срединного шва."},{"id":"head_maxilla_right_A02_1_12_031","bone":"maxilla_right","code":"A02.1.12.031","kind":"volume","reason":"Резцовая кость здесь обозначает переднюю резцовую часть верхней челюсти; не независимую дополнительную кость каждого взрослого."},{"id":"head_maxilla_right_A02_1_12_032","bone":"maxilla_right","code":"A02.1.12.032","kind":"line","reason":"Резцовый шов — линия соединения резцовой части с остальной верхней челюстью; его наличие и протяжённость на образце отдельно не приняты."},{"id":"head_maxilla_right_A02_1_12_033","bone":"maxilla_right","code":"A02.1.12.033","kind":"volume","reason":"Нёбные ости — множественные костные выступы возле борозд, не одиночная точка и не нервно-сосудистый пучок."},{"id":"head_maxilla_right_A02_1_12_034","bone":"maxilla_right","code":"A02.1.12.034","kind":"area","reason":"Нёбные борозды — открытые ложа нижней поверхности отростка; не внутренние малые нёбные каналы."},{"id":"head_maxilla_right_A02_1_12_035","bone":"maxilla_right","code":"A02.1.12.035","kind":"volume","reason":"Альвеолярный отросток — зубоносная часть кости с лунками, стенками и перегородками; не только свободный край дуги."},{"id":"head_maxilla_right_A02_1_12_037","bone":"maxilla_right","code":"A02.1.12.037","kind":"volume","reason":"Зубные альвеолы — лунки для корней с глубиной и стенками; их входы или точки на соседней кости не заменяют весь объём."},{"id":"head_maxilla_right_A02_1_12_038","bone":"maxilla_right","code":"A02.1.12.038","kind":"volume","reason":"Межальвеолярные перегородки — костное вещество между соседними лунками, а не линия между зубами."},{"id":"head_maxilla_right_A02_1_12_039","bone":"maxilla_right","code":"A02.1.12.039","kind":"volume","reason":"Межкорневые перегородки — костные разделители внутри лунки многокорневого зуба; отличны от межальвеолярных."},{"id":"head_maxilla_right_A02_1_12_040","bone":"maxilla_right","code":"A02.1.12.040","kind":"volume","reason":"Альвеолярные возвышения — наружный костный рельеф, соответствующий корням; не сами зубы и не осевые линии корней."},{"id":"head_maxilla_right_A02_1_00_062","bone":"maxilla_right","code":"A02.1.00.062","kind":"space","reason":"Устья резцовых каналов в переднем нёбе — отверстия; не вся резцовая ямка и не полный разветвлённый ход каналов. Число и объединение устьев вариабельны и на образце не приняты."},{"id":"head_maxilla_left_A02_1_12_002","bone":"maxilla_left","code":"A02.1.12.002","kind":"volume","reason":"Тело — костная часть с пазухой и несколькими наружными гранями; не сама пазуха и не одна поверхность."},{"id":"head_maxilla_left_A02_1_12_005","bone":"maxilla_left","code":"A02.1.12.005","kind":"area","reason":"Открытое костное ложе на задней части глазничной поверхности переходит в канал; линия хода нерва не заменяет ширину борозды."},{"id":"head_maxilla_left_A02_1_12_008","bone":"maxilla_left","code":"A02.1.12.008","kind":"space","reason":"Наружное устье подглазничного канала отличается от его просвета на всём протяжении и от костного края отверстия."}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch6\\390-cards.png"});}
