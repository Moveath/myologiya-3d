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
})(page,{"width":1280,"rows":[{"id":"head_temporal_left_A02_1_06_026","bone":"temporal_left","code":"A02.1.06.026","kind":"space","reason":"Расщелина малого каменистого нерва обозначает выход; не смешивается с бороздой или вариабельным выходом нерва из черепа."},{"id":"head_temporal_left_A02_1_06_027","bone":"temporal_left","code":"A02.1.06.027","kind":"area","reason":"Поверхностная борозда малого каменистого нерва имеет ширину ложа; одна линия хода не представляет всю борозду."},{"id":"head_temporal_left_A02_1_06_028","bone":"temporal_left","code":"A02.1.06.028","kind":"area","reason":"Тройничное вдавление — вдавленная костная поверхность; объём узла и полость Меккеля в эту запись не включаются."},{"id":"head_temporal_left_A02_1_06_029","bone":"temporal_left","code":"A02.1.06.029","kind":"line","reason":"Верхний край — граница передней и задней граней; расположенная вдоль него борозда имеет отдельную запись."},{"id":"head_temporal_left_A02_1_06_030","bone":"temporal_left","code":"A02.1.06.030","kind":"area","reason":"Борозда верхнего каменистого синуса — костное ложе вдоль края, не сам край или просвет синуса."},{"id":"head_temporal_left_A02_1_06_031","bone":"temporal_left","code":"A02.1.06.031","kind":"area","reason":"Задняя грань пирамиды — протяжённая костная поверхность; одно внутреннее слуховое отверстие её не заменяет."},{"id":"head_temporal_left_A02_1_06_032","bone":"temporal_left","code":"A02.1.06.032","kind":"space","reason":"Внутреннее слуховое отверстие — вход, отдельно от всего внутреннего слухового прохода и его дна."},{"id":"head_temporal_left_A02_1_06_034","bone":"temporal_left","code":"A02.1.06.034","kind":"area","reason":"Поддуговая ямка в текущем взрослом определении — поверхностное углубление; продолжающий её канал не присоединяется к этой области автоматически."},{"id":"head_temporal_left_A02_1_06_036","bone":"temporal_left","code":"A02.1.06.036","kind":"space","reason":"Апертура канальца преддверия — выходное отверстие; не эндолимфатический мешок и не весь каналец."},{"id":"head_temporal_left_A02_1_06_040","bone":"temporal_left","code":"A02.1.06.040","kind":"area","reason":"Нижняя грань — костная поверхность основания с собственными отверстиями и ямками, не целая пирамида."},{"id":"head_temporal_left_A02_1_06_041","bone":"temporal_left","code":"A02.1.06.041","kind":"area","reason":"Яремная ямка обозначает вогнутое костное ложе луковицы; оно не равно объёму луковицы или всему яремному отверстию."},{"id":"head_temporal_left_A02_1_06_043","bone":"temporal_left","code":"A02.1.06.043","kind":"space","reason":"Апертура канальца улитки — наружное сообщение; отличается от канальца преддверия и всей протяжённости канальца улитки."},{"id":"head_temporal_left_A02_1_06_045","bone":"temporal_left","code":"A02.1.06.045","kind":"area","reason":"Нижний каталожный вид той же яремной вырезки: проверяется костная выемка, не новый отдельный объект и не полное отверстие."},{"id":"head_temporal_left_A02_1_06_046","bone":"temporal_left","code":"A02.1.06.046","kind":"volume","reason":"Внутрияремный отросток — костный выступ края, не произвольная линия разделения всего отверстия."},{"id":"head_temporal_left_A02_1_06_047","bone":"temporal_left","code":"A02.1.06.047","kind":"volume","reason":"Шиловидный отросток — костный объём; его вершина и возможное окостенение связки не заменяют весь отросток."},{"id":"head_temporal_left_A02_1_06_048","bone":"temporal_left","code":"A02.1.06.048","kind":"space","reason":"Шилососцевидное отверстие — выход лицевого канала; не весь лицевой канал и не точка между отростками."}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch5\\1280-cards.png"});}
