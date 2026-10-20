async(page)=>(async function exercise(page,{width,phase,dir}){
 const checks=[],errors=[];let timer;
 const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(6000);page.setDefaultNavigationTimeout(20000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{if(width===390&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();};
 const side=async value=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator('[data-side-view="'+value+'"]').click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const job=async()=>{
  if(phase==='setup'){
   await page.unrouteAll({behavior:'ignoreErrors'});
   await page.setViewportSize({width,height:width===390?844:900});
   await page.emulateMedia({colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
   await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
   const probe=`window.__stage6Check=()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id)});`;
   await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
   await page.goto('http://127.0.0.1:8783/local.html',{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>localStorage.removeItem('myo3d'));await page.reload({waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__ready,undefined,{timeout:20000});
   await page.evaluate(async()=>{await __atlas.enterSection('leg');await __atlas.goTo('sesamoid_pedis');});
   check(await page.evaluate(()=>ATLAS.bones.sesamoid_pedis_left.g)==='b_toes','Current regenerated group loaded');
  }else{
   await side('both');
   for(const id of ['sesamoid_pedis','sesamoid_pedis_left']){
    await close();await page.locator('#bList').click();await page.locator('#q').fill('Сесамовидные кости большого пальца стопы');
    const item=page.locator('#dlist [data-id="'+id+'"]').filter({hasNot:page.locator('[data-pinid]')}).first();
    check(await item.count()===1,'Search '+id);
    const group=await item.evaluate(el=>el.closest('details')?.querySelector('summary')?.textContent);
    check(group.includes(await page.evaluate(()=>ATLAS.boneGroups.find(g=>g.id==='b_toes').title)),'Toe group '+id);
    await item.click();check(await page.evaluate(()=>__atlas.state.sel)===id,'Selection '+id);await card();
    const ids=await page.evaluate(id=>ATLAS.pins.filter(p=>p.b===id&&p.anatomicalEntity==='bone').map(p=>p.id),id);
    check(ids.length===2,'Two existing children '+id);
    for(const pin of ids){await page.evaluate(pin=>__atlas.activatePin(pin),pin);check((await page.locator('.pinbox').textContent()).length>0,'Child card '+pin);}
    if(id.endsWith('_left')){
     check(await page.locator('#bIso').count()===0,'No fictitious left isolation');
     check(await page.locator('#bBoneXray').count()===0,'No fictitious left transparency');
     check((await page.locator('#sheet').textContent()).includes('левой модели'),'Left geometry limitation');
    }else{
     await page.evaluate(()=>__atlas.goTo('sesamoid_pedis'));await card();
     await page.locator('#bIso').click();
     check(JSON.stringify(await page.evaluate(()=>__stage6Check().visible))===JSON.stringify(['sesamoid_pedis']),'Right group isolated');
     await card();await page.locator('#bBoneXray').click();
     check((await page.evaluate(()=>__stage6Check().xray)).includes('sesamoid_pedis'),'Right transparency');
     await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
    }
   }
   await side('left');
   check(!(await page.evaluate(()=>__stage6Check().visible)).includes('sesamoid_pedis'),'No opposite sesamoid replacement');
   await side('both');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
   await page.screenshot({path:dir+'/sesamoid-'+width+'.png'});
  }
  check(errors.length===0,'No console/page errors');
  return {status:'passed',width,phase,checks,errors};
 };
 let result;
 try{result=await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('45000ms deadline; only test page closed'));},45000);})]);}
 catch(e){result={status:'failed',width,phase,checks,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);page.off('console',onConsole);}
 return result;
})(page,{"width":390,"phase":"workflow","dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-sesamoid-ui-2026-10-20T05-08-51-574Z-LvRt9U"})