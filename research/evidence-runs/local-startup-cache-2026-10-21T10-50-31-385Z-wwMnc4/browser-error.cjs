async page=>{
const errors=[];const capture=e=>errors.push(String(e));page.on('pageerror',capture);
try {
 await page.unrouteAll({behavior:'ignoreErrors'});
 await page.route('**/atlas-controls.js?*',r=>r.fulfill({contentType:'text/javascript',body:'export class AtlasOrbitControls {}'}));
 await page.goto('http://127.0.0.1:8783/local.html',{waitUntil:'domcontentloaded',timeout:12000});
 await page.locator('#runtimeFailure').waitFor({state:'visible',timeout:6000});
 const text=await page.locator('#runtimeFailure').innerText();
 if(!text.includes('Не удалось загрузить программу просмотра')||!errors.some(e=>e.includes('framingBasis')))throw Error('Missing startup failure guard');
 await page.screenshot({path:"C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/local-startup-cache-2026-10-21T10-50-31-385Z-wwMnc4/module-error-message.png"});
 return {status:'passed',scenario:'missing module export',expectedError:errors,visibleMessage:text};
}finally{page.off('pageerror',capture);await page.unrouteAll({behavior:'ignoreErrors'});}
}
