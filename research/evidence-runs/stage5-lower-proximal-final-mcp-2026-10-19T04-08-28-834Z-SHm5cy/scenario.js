async(page)=>(async function browser(page,{dir}){
 const rows=[];
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:width===390?844:900});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+(width===390?'dark':'light'),{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
  const row=await page.evaluate(async()=>{
   await __atlas.enterSection('leg');let checked=0;
   for(const p of ATLAS.pins.filter(p=>p.lowerProximalReview&&(p.relations||['A02.5.04.021','A02.5.04.024'].includes(p.c)))){
    await __atlas.goTo(p.b);__atlas.activatePin(p.id);
    const box=document.querySelector('.pinbox');if(!box?.textContent.includes(p.x))throw Error(p.id);
    if(p.relations&&(!box.textContent.includes(p.educationCode)||p.nomenclatureStatus!=='TA98_term'))throw Error('Nomenclature '+p.id);
    checked++;
   }
   return {checked,variantPointRetained:!!ATLAS.pins.find(p=>p.id==='fem_trochanter_tertius').p};
  });
  if(row.checked!==12)throw Error('Expected 8 joints + 4 condyle descriptions');
  await page.evaluate(async()=>{await __atlas.goTo('tibia');__atlas.activatePin('extra_femur_knee_joint');document.querySelector('#sheet').scrollTop=0;});
  if(width===390&&await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();
  await page.screenshot({path:dir+'/final-card-'+width+'.png'});rows.push({width,...row});
 }
 return {status:'passed',rows};
})(page,{"dir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\stage5-lower-proximal-final-mcp-2026-10-19T04-08-28-834Z-SHm5cy"})