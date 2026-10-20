async(page)=>{
 const cases=[],errors=[];page.on('pageerror',e=>errors.push(String(e)));
 for(const [width,theme]of [[1280,'light'],[390,'dark']]){
  await page.setViewportSize({width,height:900});await page.emulateMedia({colorScheme:theme});
  await page.goto('http://127.0.0.1:8782/local.html?theme='+theme);await page.waitForFunction(()=>window.__ready);
  await page.evaluate(async()=>{await __atlas.enterSection('trunk');await __atlas.goTo('rib_12_right');__atlas.activatePin('thorax_rib_12_right_A02_3_02_012');});
  const result=await page.evaluate(()=>{const p=ATLAS.pins.find(p=>p.id==='thorax_rib_12_right_A02_3_02_012');return {refs:p.refs.filter(r=>r.id==='rib_crest_academy').length,links:document.querySelectorAll('.pinbox a[href*="academie-medecine.fr"]').length,kind:p.geometryKind,unresolved:p.anatomyVerification,located:!!p.p};});
  if(result.refs!==1||result.links!==1||result.kind!=='line'||result.unresolved!=='incomplete'||result.located)throw Error('Crest source/limitation mismatch '+JSON.stringify(result));
  const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
  let links=0;
  for(const [id,parent]of [['extra_sternum_costal_notch_2_right','thorax_sternum_A02_3_03_002'],['extra_sternum_costal_notch_7_left','thorax_sternum_A02_3_03_007'],['extra_sternum_foramen_variant','thorax_sternum_A02_3_03_006'],['thorax_rib_7_right_A02_3_02_003','thorax_thoracic_6_A02_2_03_003'],['thorax_rib_7_left_A02_3_02_009','thorax_thoracic_7_A02_2_03_004']]){
   await page.evaluate(async id=>{const p=ATLAS.pins.find(p=>p.id===id);await __atlas.goTo(p.b);__atlas.activatePin(id);},id);await card();
   await page.locator('.pinbox [data-related-pin="'+parent+'"]').click();
   if(await page.evaluate(()=>__atlas.state.pin)!==parent)throw Error('Related navigation '+parent);links++;
  }
  await page.evaluate(async()=>{await __atlas.goTo('sternum');__atlas.activatePin('extra_sternum_costal_notch_2_right');});await card();
  const screenshot='C:/Users/Пользователь/Desktop/учеба/Миология 3D/research/evidence-runs/stage5-ribs-final-links-2026-10-18T14-47-48-331Z-3M1DhT/links-'+width+'-'+await page.evaluate(()=>crypto.randomUUID())+'.png';
  await page.screenshot({path:screenshot});cases.push({width,theme,...result,linksClicked:links,screenshot});
 }
 if(errors.length)throw Error(JSON.stringify(errors));return {status:'passed',cases,errors};
}
