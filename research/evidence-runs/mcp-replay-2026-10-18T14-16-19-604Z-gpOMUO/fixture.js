async(page)=>{
 const screenshots=[],dir="C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/mcp-replay-2026-10-18T14-16-19-604Z-gpOMUO";
 const safePage=new Proxy(page,{get(target,key){
  if(key==='screenshot')return async(options={})=>{
   const nonce=await target.evaluate(()=>crypto.randomUUID());
   const base=String(options.path||'capture.png').split(/[\\/]/).pop().replace(/[^a-zA-Z0-9_.-]/g,'_');
   const actual=dir+'/'+nonce+'-'+base;screenshots.push(actual);
   return target.screenshot({...options,path:actual});
  };
  const value=Reflect.get(target,key);return typeof value==='function'?value.bind(target):value;
 }});
 const result=await (async(page)=>{
 const check=(v,m)=>{if(!v)throw Error(m)},out=[],errors=[];
 const err=e=>errors.push(String(e));page.on('pageerror',err);
 const probe="window.__linkCheck=()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id)});\n";
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 try{
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  for(const [width,theme] of [[1280,'light'],[390,'dark']]){
   await page.setViewportSize({width,height:width===390?844:900});await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
   await page.evaluate(()=>__atlas.enterSection('trunk'));
   let parents=0;
   for(const part of ['superior','inferior','lateral'])for(const side of ['right','left']){
    const id=`extra_thoracic_12_${part}_tubercle_${side}`;
    await page.evaluate(id=>__atlas.goTo('thoracic_12',null,id),id);await card();
    await page.locator('.pinbox [data-related-pin="thorax_thoracic_12_A02_2_01_013"]').click();
    check(await page.evaluate(()=>__atlas.state.pin)==='thorax_thoracic_12_A02_2_01_013','Parent navigation');parents++;
   }
   for(const owner of ['cervical_7','thoracic_1']){
    await page.evaluate(b=>__atlas.goTo(b,null,'shared_thorax_intervertebral_c7_t1_right'),owner);await card();
    await page.locator('#bIso').click();let v=await page.evaluate(()=>__linkCheck());
    check(JSON.stringify(v.visible.sort())===JSON.stringify(['cervical_7','thoracic_1']),'C7/T1 context participants isolated');
    await card();await page.locator('#bBoneXray').click();v=await page.evaluate(()=>__linkCheck());
    check(JSON.stringify(v.xray.sort())===JSON.stringify(['cervical_7','thoracic_1']),'C7/T1 context participants transparent');
    await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
   }
   await card();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Overflow');
   const nonce=await page.evaluate(()=>crypto.randomUUID());const screenshot='C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-thorax-ui-links-2026-10-18T14-13-21-074Z-C39xdj/'+width+'-'+nonce+'.png';await page.screenshot({path:screenshot});
   out.push({width,theme,parentLinks:parents,crossRegionIsolation:2,crossRegionTransparency:2,screenshot});
  }
  check(!errors.length,'Page errors');return{status:'passed',cases:out,errors};
 }catch(e){return{status:'failed',error:String(e),cases:out,errors};}
 finally{page.off('pageerror',err);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
})(safePage);
 return {result,screenshots,evidenceRun:dir};
}