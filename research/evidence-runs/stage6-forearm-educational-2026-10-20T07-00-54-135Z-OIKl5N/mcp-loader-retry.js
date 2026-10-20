async(page)=>{
 let timer,blocked=false;const checks=[];
 const job=async()=>{
  page.setDefaultTimeout(5000);page.setDefaultNavigationTimeout(15000);
  await page.route('**/models/bodyparts3d-3.0/left-forearm/radius_left.glb',async r=>{blocked=true;await r.fulfill({status:503,body:'deliberate regression fixture'});});
  await page.goto('http://127.0.0.1:8783/local.html?theme=light',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.__ready);
  const failed=await page.evaluate(()=>__atlas.enterSection('arm'));
  if(failed!==false||!blocked||!await page.locator('#veilText').textContent().then(t=>t.includes('Не удалось')))throw Error('Failed load not exposed');
  checks.push('Missing supplemental asset produces explicit section error, not a false loaded model');
  await page.unroute('**/models/bodyparts3d-3.0/left-forearm/radius_left.glb');
  const loaded=await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('radius_left');return __forearmCheck.snapshot().visible;});
  if(!loaded.includes('radius_left')||!loaded.includes('ulna_left'))throw Error('Retry did not load both actual bones');
  checks.push('Failed cache cleared: retry loads both real supplemental bones');
  return {status:'passed',checks,intentionalHTTP503:true};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>{timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline'));},40000);})]);}
 catch(e){return {status:'failed',checks,error:String(e)};}
 finally{clearTimeout(timer);}
}