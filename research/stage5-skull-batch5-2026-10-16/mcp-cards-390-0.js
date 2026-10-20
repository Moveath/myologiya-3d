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
})(page,{"width":390,"rows":[{"id":"head_sphenoid_A02_1_05_052","bone":"sphenoid","code":"A02.1.05.052","kind":"area","reason":"Борозда крючка — костное ложе у поворота сухожилия; не само сухожилие, бурса или весь крючок."},{"id":"head_sphenoid_A02_1_05_054","bone":"sphenoid","code":"A02.1.05.054","kind":"volume","reason":"Крыловидно-остистый отросток — выступ латеральной пластинки; не весь окостеневший мостик, связка или образуемое ими отверстие."},{"id":"head_temporal_right_A02_1_06_002","bone":"temporal_right","code":"A02.1.06.002","kind":"volume","reason":"Каменистая часть — костная часть с внутренними полостями и наружными гранями, не одна грань."},{"id":"head_temporal_right_A02_1_06_003","bone":"temporal_right","code":"A02.1.06.003","kind":"line","reason":"Собственный задний край сосцевидной области задаёт линию границы кости; это не весь затылочно-сосцевидный шов."},{"id":"head_temporal_right_A02_1_06_004","bone":"temporal_right","code":"A02.1.06.004","kind":"volume","reason":"Сосцевидный отросток — костный выступ с толщиной и внутренним строением; поверхность его вершины не заменяет весь отросток."},{"id":"head_temporal_right_A02_1_06_005","bone":"temporal_right","code":"A02.1.06.005","kind":"area","reason":"Сосцевидная вырезка здесь обозначает углублённое костное ложе на медиальной стороне отростка, не пустой канал."},{"id":"head_temporal_right_A02_1_06_006","bone":"temporal_right","code":"A02.1.06.006","kind":"area","reason":"Собственная сигмовидная борозда височной кости — костное ложе; это не просвет венозного синуса и не весь многокостный ход."},{"id":"head_temporal_right_A02_1_06_007","bone":"temporal_right","code":"A02.1.06.007","kind":"area","reason":"Борозда затылочной артерии — углублённый участок поверхности; артерия и её ось не входят в эту запись."},{"id":"head_temporal_right_A02_1_06_008","bone":"temporal_right","code":"A02.1.06.008","kind":"space","reason":"Сосцевидное отверстие — вариабельный проход; классификация не подтверждает его наличие или постоянную шовную принадлежность."},{"id":"head_temporal_right_A02_1_06_010","bone":"temporal_right","code":"A02.1.06.010","kind":"volume","reason":"Коленце обозначает изгибающийся участок внутреннего лицевого канала с просветом; точка поворота и осевая линия не заменяют этот участок."},{"id":"head_temporal_right_A02_1_06_012","bone":"temporal_right","code":"A02.1.06.012","kind":"volume","reason":"Верхушка пирамиды — переднемедиальная костная область, содержащая апертуру; это не математическая вершина и не единственная крайняя точка."},{"id":"head_temporal_right_A02_1_06_014","bone":"temporal_right","code":"A02.1.06.014","kind":"space","reason":"Наружная апертура — вход в сонный канал; отдельно от костного края и всего внутрикостного хода."},{"id":"head_temporal_right_A02_1_06_015","bone":"temporal_right","code":"A02.1.06.015","kind":"space","reason":"Внутренняя апертура — выход сонного канала у верхушки; старый поверхностный якорь не является центром просвета."},{"id":"head_temporal_right_A02_1_06_020","bone":"temporal_right","code":"A02.1.06.020","kind":"volume","reason":"Перегородка между полуканалами — костная пластинка с толщиной; не один её свободный край и не оба полуканала."},{"id":"head_temporal_right_A02_1_06_021","bone":"temporal_right","code":"A02.1.06.021","kind":"area","reason":"Рассматривается передняя грань каменистой части, а не вся пирамида или средняя черепная ямка."},{"id":"head_temporal_right_A02_1_06_022","bone":"temporal_right","code":"A02.1.06.022","kind":"volume","reason":"Крыша барабанной полости — костная пластинка, разделяющая полости; её нижняя поверхность не заменяет всю пластинку."}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\shots\\stage5-skull-batch5\\390-cards.png"});}
