async page=>{
 let timer; const checks=[],errors=[],requests=[];const onError=e=>errors.push(String(e)),onRequest=r=>{if(r.url().includes('/atlas-controls.js'))requests.push(r.url());};
 page.on('pageerror',onError);page.on('request',onRequest);page.setDefaultTimeout(6000);
 const check=(v,s)=>{if(!v)throw Error(s);checks.push(s);};
 try{return await Promise.race([(async()=>{
 await page.unrouteAll({behavior:'ignoreErrors'});
 await page.setViewportSize({width:1280,height:900});
 // A stale unversioned module must never be used by the new document.
 await page.route('**/atlas-controls.js',r=>r.fulfill({contentType:'text/javascript',body:'export class AtlasOrbitControls {}'}));
 await page.goto('http://127.0.0.1:8783/local.html?theme=light',{waitUntil:'domcontentloaded',timeout:12000});
 await page.waitForFunction(()=>window.__ready,{}, {timeout:12000});
 check(await page.locator('.seccard').count()===5,'Five section cards');
 check(await page.locator('.flabel').count()===5,'Five figure labels');
 check(requests.length>0&&requests.every(u=>/\\?v=[a-f0-9]{16}/.test(u)),'Versioned controls bypass stale cache');
 check(!await page.locator('#runtimeFailure').count(),'No startup failure');
 await page.screenshot({path:"C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/local-startup-cache-2026-10-21T10-50-31-385Z-wwMnc4/1280-home.png"});
 for(const id of ["head","neck","trunk","arm","leg"]){
 await page.locator('.seccard[data-sec="'+id+'"]').click();
 await page.waitForFunction(s=>__atlas.state.sec===s&&document.getElementById('home').hidden,id,{timeout:15000});
 check(await page.locator('#subs [data-sub]').count()>0,id+' opens with subsections');
 if(id==='leg')check(await page.evaluate(()=>!!ATLAS.muscles.puborectalis_right&&!ATLAS.muscles.puborectalis_left.noModel),'New muscle catalogue retained');
 await page.locator('#bHome').click();
 check(await page.locator('#home').isVisible(),id+' returns to section selection');
 }
 check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
 check(!errors.length,'No page errors');
 return {status:'passed',width:1280,checks,errors,requests};
 })(),new Promise((_,reject)=>timer=setTimeout(()=>reject(Error('45-second test limit')),45000))]);}
 catch(e){return {status:'failed',error:String(e),width:1280,checks,errors,requests};}
 finally{clearTimeout(timer);page.off('pageerror',onError);page.off('request',onRequest);await page.unrouteAll({behavior:'ignoreErrors'});}
}
