async(page)=>{
 const screenshots=[],dir="C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/mcp-replay-2026-10-17T06-24-27-098Z-uclUkJ";
 const safePage=new Proxy(page,{get(target,key){
  if(key==='screenshot')return async(options={})=>{
   const nonce=await target.evaluate(()=>crypto.randomUUID());
   const base=String(options.path||'capture.png').split(/[\\/]/).pop().replace(/[^a-zA-Z0-9_.-]/g,'_');
   const actual=dir+'/'+nonce+'-'+base;screenshots.push(actual);
   return target.screenshot({...options,path:actual});
  };
  const value=Reflect.get(target,key);return typeof value==='function'?value.bind(target):value;
 }});
 const result=await (async(page)=>{async function card(page){
 if(await page.locator('#mobileCard').isVisible()&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
 if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
}
async function cardsBrowser(page,{width,rows,shot,finish}){
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
  if(finish){await page.locator('.pinbox').scrollIntoViewIfNeeded();shot=shot.replace(/\.png$/, '-'+await page.evaluate(()=>crypto.randomUUID())+'.png');await page.screenshot({path:shot,timeout:10000});}
  return {status:'passed',width,testedIDs:rows.map(p=>p.id),supplementaryCards:rows.filter(p=>p.extra).length,links,errors,shot:finish?shot:null};
 }finally{page.off('pageerror',onError);page.off('console',onConsole);}
}
;return cardsBrowser(page,{"width":1280,"rows":[{"id":"extra_inferior_concha_right_end_posterior","bone":"inferior_concha_right","ru":"Задний конец справа","kind":"volume","extra":true,"related":[]},{"id":"extra_inferior_concha_left_surface_medial","bone":"inferior_concha_left","ru":"Медиальная поверхность слева","kind":"area","extra":true,"related":[]},{"id":"extra_inferior_concha_left_surface_lateral","bone":"inferior_concha_left","ru":"Латеральная поверхность слева","kind":"area","extra":true,"related":[]},{"id":"extra_inferior_concha_left_border_superior","bone":"inferior_concha_left","ru":"Верхний край слева","kind":"line","extra":true,"related":[]},{"id":"extra_inferior_concha_left_border_inferior","bone":"inferior_concha_left","ru":"Нижний край слева","kind":"line","extra":true,"related":[]}],"finish":false,"shot":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\skull-targeted-data-2026-10-17T06-23-51-232Z-rqCZ6e\\1280-cards.png"});})(safePage);
 return {result,screenshots,evidenceRun:dir};
}