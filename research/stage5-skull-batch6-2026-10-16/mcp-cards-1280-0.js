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
})(page,{"width":1280,"rows":[{"id":"head_maxilla_right_A02_1_12_002","bone":"maxilla_right","code":"A02.1.12.002","kind":"volume","reason":"Тело — костная часть с пазухой и несколькими наружными гранями; не сама пазуха и не одна поверхность."},{"id":"head_maxilla_right_A02_1_12_005","bone":"maxilla_right","code":"A02.1.12.005","kind":"area","reason":"Открытое костное ложе на задней части глазничной поверхности переходит в канал; линия хода нерва не заменяет ширину борозды."},{"id":"head_maxilla_right_A02_1_12_008","bone":"maxilla_right","code":"A02.1.12.008","kind":"space","reason":"Наружное устье подглазничного канала отличается от его просвета на всём протяжении и от костного края отверстия."},{"id":"head_maxilla_right_A02_1_12_009","bone":"maxilla_right","code":"A02.1.12.009","kind":"area","reason":"Клыковая ямка — углубление передней костной поверхности, латеральнее клыкового возвышения; не зубная лунка."},{"id":"head_maxilla_right_A02_1_12_010","bone":"maxilla_right","code":"A02.1.12.010","kind":"line","reason":"Определение обозначает вогнутую границу передней поверхности; это собственный край, а не вся грушевидная апертура."},{"id":"head_maxilla_right_A02_1_12_011","bone":"maxilla_right","code":"A02.1.12.011","kind":"volume","reason":"Костный выступ в составе общей передней носовой ости имеет объём; цефалометрическая точка его вершины не равна всей ости."},{"id":"head_maxilla_right_A02_1_12_014","bone":"maxilla_right","code":"A02.1.12.014","kind":"space","reason":"Группа входов задних альвеолярных каналов; одно положение маркера не представляет каждое отверстие."},{"id":"head_maxilla_right_A02_1_12_016","bone":"maxilla_right","code":"A02.1.12.016","kind":"volume","reason":"Бугор — задний костный выступ тела позади зубного ряда; не только его суставная площадка."},{"id":"head_maxilla_right_A02_1_12_018","bone":"maxilla_right","code":"A02.1.12.018","kind":"area","reason":"Собственная слёзная борозда верхней челюсти — костное ложе; не вся ямка мешка или собранный носослёзный канал."},{"id":"head_maxilla_right_A02_1_12_019","bone":"maxilla_right","code":"A02.1.12.019","kind":"volume","reason":"Раковинный гребень — выступающий костный рельеф для нижней раковины; не сама раковина и не одна линия её соединения."},{"id":"head_maxilla_right_A02_1_12_021","bone":"maxilla_right","code":"A02.1.12.021","kind":"space","reason":"Расщелина — крупное отверстие изолированной верхней челюсти в пазуху; не окончательное соустье с мягкими тканями собранной носовой стенки."},{"id":"head_maxilla_right_A02_1_12_022","bone":"maxilla_right","code":"A02.1.12.022","kind":"area","reason":"Собственная большая нёбная борозда — открытое костное ложе для составного канала; не весь канал или его выход."},{"id":"head_maxilla_right_A02_1_12_024","bone":"maxilla_right","code":"A02.1.12.024","kind":"volume","reason":"Лобный отросток — восходящая костная пластинка с несколькими поверхностями и соединениями."},{"id":"head_maxilla_right_A02_1_12_025","bone":"maxilla_right","code":"A02.1.12.025","kind":"volume","reason":"Передний слёзный гребень — костный рельеф, ограничивающий борозду; край гребня не заменяет весь гребень."},{"id":"head_maxilla_right_A02_1_12_026","bone":"maxilla_right","code":"A02.1.12.026","kind":"area","reason":"Слёзная вырезка — собственная выемка медиального глазничного края; не готовый просвет носослёзного канала."},{"id":"head_maxilla_right_A02_1_12_027","bone":"maxilla_right","code":"A02.1.12.027","kind":"volume","reason":"Решётчатый гребень — костный выступ медиальной поверхности лобного отростка для средней раковины; не вся решётчатая кость."}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch6\\1280-cards.png"});}
