async(page)=>(async function exercise(page,{dir,width,revision}){
 const checks=[],errors=[],views=[];let timer;
 const check=(value,label)=>{if(!value)throw Error(label);checks.push(label);};
 const onError=e=>errors.push(String(e));
 page.on('pageerror',onError);page.setDefaultTimeout(5000);
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const card=async()=>{
  if(width===390){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}
  else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
 };
 const job=async()=>{
  await page.setViewportSize({width,height:width===390?844:900});
  await page.emulateMedia({colorScheme:width===390?'dark':'light',reducedMotion:'reduce'});
  await close();
  await page.evaluate(async()=>{__atlas.setSub('all');__atlas.setSide('left');await __atlas.goTo('humerus_left');__atlas.activatePin('extra_humerus_left_elbow_joint');});
  await card();await page.locator('#bIso').click();await close();
  const visible=await page.evaluate(()=>__forearmCheck.snapshot().visible.sort());
  check(JSON.stringify(visible)===JSON.stringify(['humerus_left','radius_left','ulna_left']),'Elbow card isolates actual three left bones');
  for(let i=0;i<3;i++){
   if(!await page.locator('#bView').isVisible())await page.locator('#bOptions').click();
   await page.locator('#bView').click();
   const label=await page.locator('#viewLabel').textContent();
   check(['Спереди','Снаружи','Сзади'][i]===label,'Real view control '+label);
   // Allow the existing camera tween to finish before capturing evidence.
   await page.waitForTimeout(650);
   const file=dir+'/browser-joints-'+revision+'-'+width+'-view-'+i+'.png';
   await page.screenshot({path:file});views.push({label,file});
  }
  await card();await page.locator('#bIso').click();await close();
  await page.evaluate(async()=>{await __atlas.goTo('radius_left');__atlas.activatePin('extra_radius_left_distal_radioulnar_joint');});
  await card();await page.locator('#bIso').click();
  check(JSON.stringify((await page.evaluate(()=>__forearmCheck.snapshot().visible)).sort())===JSON.stringify(['radius_left','ulna_left']),'Distal joint isolates only its two bones');
  await card();await page.locator('#bBoneXray').click();
  check((await page.evaluate(()=>__forearmCheck.snapshot().xray)).length===2,'Distal joint transparency affects both bones');
  await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();await close();
  await page.evaluate(()=>__atlas.goTo('ulna_left'));await card();await page.locator('#bIso').click();await close();
  await page.waitForFunction(()=>!!__forearmCheck.clickPoint('ulna_left'),undefined,{timeout:6000});
  const point=await page.evaluate(()=>__forearmCheck.clickPoint('ulna_left'));
  const rays=await page.evaluate(p=>__forearmCheck.compare(p),point);
  check(rays.bvh>0&&rays.rays.some(r=>r.hits>0),'Ulna BVH/native distances and faceIndex agree');
  await page.mouse.click(point.x,point.y);
  check(await page.evaluate(()=>__atlas.state.sel)==='ulna_left','Actual canvas click selects left ulna');
  await card();await page.locator('#bIso').click();await close();
  check(errors.length===0,'No page errors');
  return {status:'passed',width,checks,views,rayComparison:rays,errors,
          anatomicalCongruenceClaim:false};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{
  timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline; test page closed'));},40000);
 })]);}
 catch(e){return {status:'failed',width,checks,views,errors,error:String(e)};}
 finally{clearTimeout(timer);page.off('pageerror',onError);}
})(page,{"dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage6-forearm-educational-2026-10-20T07-00-54-135Z-OIKl5N","width":390,"revision":"v3"})