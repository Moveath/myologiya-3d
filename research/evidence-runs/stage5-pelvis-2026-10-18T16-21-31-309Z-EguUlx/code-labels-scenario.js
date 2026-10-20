async(page)=>{
 const errors=[];const onError=e=>errors.push(String(e));page.on('pageerror',onError);const rows=[];
 try{
 await page.route('**/*.js',r=>r.continue());
 for(const [width,theme] of [[1280,'dark'],[390,'light']]){
 await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
 const result=await page.evaluate(async()=>{
 await __atlas.enterSection('leg');await __atlas.goTo('hip_bone');
 const pins=ATLAS.pins.filter(p=>p.geometryReview?.source==='research/stage5-pelvis-report-2026-10-18.md'&&p.t==='additional');
 for(const p of pins){__atlas.activatePin(p.id);const s=document.querySelector('.pinbox .tacode')?.textContent||'';if(p.nomenclatureStatus.startsWith('TA98')?!s.includes('TA98 '+p.educationCode):!s.includes('код TA98 не присвоен'))throw Error('Code label '+p.id);}
 __atlas.activatePin('extra_hip_bone_ilium');
 return {labels:pins.length,verifiedCodes:pins.filter(p=>p.nomenclatureStatus.startsWith('TA98')).length,overflow:document.documentElement.scrollWidth>innerWidth};
 });if(result.overflow)throw Error('Overflow');rows.push({width,theme,...result});
 await page.screenshot({path:"C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-pelvis-2026-10-18T16-21-31-309Z-EguUlx"+'/final-codes-'+width+'.png',fullPage:false});
 }
 if(errors.length)throw Error(errors.join('\n'));return{status:'passed',rows,errors};
 }finally{page.off('pageerror',onError);await page.unrouteAll({behavior:'wait'});}
}
