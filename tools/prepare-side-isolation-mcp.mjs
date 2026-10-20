import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createEvidenceRun} from './evidence-run.mjs';
const source=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const rays=vm.runInNewContext(source.match(/const probe=([\s\S]*?);\r?\n\r?\nasync function/)[1]);
const probe=rays+`window.__sideCheck={snapshot:()=>({side:curSide(),sub:curSub(),selected:state.sel,isolate:state.isolate,
 visible:[...structs.values()].filter(s=>s.meshes.some(m=>m.visible)).map(s=>({id:s.id,kind:s.kind,side:s.side,meshes:s.meshes.length})),
 pickable:[...new Set(pickables.map(m=>m.userData.sid))],related:visibilityPolicy().related,
 hiddenPickables:pickables.filter(m=>!m.visible).length,
 quiz:quizPool(),firstHitOnly:ray.firstHitOnly,cut:headCutActive()})};\n`;

async function browser(page,{width,theme,shot,probe,partsOnly}){
 const checks=[],snapshots={},errors=[];let phase='start';
 const check=(v,m)=>{if(!v)throw Error(m);checks.push(m);};
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(12000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 const option=async selector=>{await close();if(width===390&&await page.locator('#app').getAttribute('data-options-open')!=='true')await page.locator('#bOptions').click();await page.locator(selector).click();if(width===390&&await page.locator('#closeOptions').isVisible())await page.locator('#closeOptions').click();};
 const side=async value=>option('[data-side-view="'+value+'"]');
 const snapshot=async name=>{const s=await page.evaluate(()=>__sideCheck.snapshot());snapshots[name]=s;check(!s.hiddenPickables,name+': no hidden pickables');if(s.side!=='both')check(s.visible.every(o=>o.side!== (s.side==='left'?'right':'left')),name+': no opposite-side mesh');return s;};
 const ids=s=>s.visible.map(o=>o.id).sort();
 const exact=(s,expected,m)=>check(JSON.stringify(ids(s))===JSON.stringify([...expected].sort()),m);
 const find=async term=>{await close();await page.locator('#bList').click();await page.locator('#q').fill(term);};
 const sub=async value=>{await close();if(width===390)await page.locator('#mobileSub').selectOption(value);else await page.locator('#subs [data-sub="'+value+'"]').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  const url='http://127.0.0.1:8782/local.html?theme='+theme;
  await page.goto(url,{waitUntil:'domcontentloaded'});await page.evaluate(()=>localStorage.setItem('myo3d',JSON.stringify({peel:0,context:true,muscleBones:false,subs:{arm:'all'}})));
  await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(()=>__atlas.enterSection('arm'));
  if(partsOnly){
   phase='part-evidence-scope';await side('right');await page.evaluate(()=>__atlas.goTo('triceps_brachii'));await option('#bMuscleBones');await card();
   await page.locator('#sheet [data-part="lat"]').click();await card();await page.locator('#bIso').click();
   exact(await snapshot('lateral-head'),['triceps_brachii','humerus'],'Part does not inherit generic whole-muscle insertion');
   await card();await page.locator('#sheet [data-part="long"]').click();
   exact(await snapshot('long-head'),['triceps_brachii','scapula'],'Part switch refreshes bone context');
   await card();await page.locator('#sheet [data-part=""]').click();
   exact(await snapshot('whole-muscle'),['triceps_brachii','scapula','humerus','ulna'],'Whole muscle retains all explicit links');
   await close();await page.waitForTimeout(700);await page.screenshot({path:shot+'-part-context.png'});
   check(errors.length===0,'No console/page errors');return {status:'passed',width,theme,partsOnly,checks,snapshots,errors};
  }
  phase='both-side';let s=await snapshot('both');check(s.visible.some(x=>x.id==='humerus')&&s.visible.some(x=>x.id==='humerus_left'),'Both humeri in general view');
  phase='right-side';await side('right');s=await snapshot('right');check(s.visible.some(x=>x.id==='scapula')&&!s.visible.some(x=>x.id==='scapula_left'),'Right scapula only');
  await page.screenshot({path:shot+'-right.png'});
  phase='left-side';await side('left');s=await snapshot('left');check(s.visible.some(x=>x.id==='humerus_left'),'Existing left humerus retained');check(s.quiz.length===0,'No invented left arm muscles in quiz');
  await sub('hand');s=await snapshot('left-hand');check(!s.visible.some(x=>x.side==='right'),'No substituted right hand');
  await find(await page.evaluate(()=>ATLAS.bones.scaphoid_left.ru));await page.locator('#dlist [data-id="scaphoid_left"]').click();await card();
  check((await page.locator('#sheet').textContent()).includes('Отдельной модели кости нет'),'Left hand noModel notice');check(await page.locator('#bIso').count()===0,'No fake left hand isolation');await snapshot('left-card');
  phase='search-other-side';await find('Двуглавая мышца плеча');await page.locator('#dlist [data-id="biceps_brachii"]:not([data-part])').click();await card();
  s=await snapshot('search-right');check(s.side==='right'&&s.selected==='biceps_brachii','Opposite-side search switches unilateral view');
  await page.locator('#bIso').click();s=await snapshot('strict-muscle');exact(s,['biceps_brachii'],'Strict muscle isolation excludes all bones/background');
  phase='muscle-bones';await option('#bMuscleBones');s=await snapshot('muscle-bones');exact(s,['biceps_brachii','radius','scapula'],'Only attachment bones accompany biceps');
  await card();await page.screenshot({path:shot+'-muscle-bones.png'});
  await option('#bContext');exact(await snapshot('context-off'),['biceps_brachii','radius','scapula'],'General background toggle does not remove explicit muscle bones');
  await card();await page.locator('#bIso').click();s=await snapshot('muscle-unisolated');check(s.visible.filter(x=>x.kind==='b').every(x=>['radius','scapula'].includes(x.id)),'Muscle bone mode also filters non-isolated bone context');
  // A selected muscle part uses its own recorded attachment subset.
  await page.evaluate(()=>__atlas.select('triceps_brachii','lat',true));await card();await page.locator('#bIso').click();s=await snapshot('part');exact(s,['triceps_brachii',...s.related],'Part isolation respects explicit attachment allowlist');
  await option('#bMuscleBones');exact(await snapshot('part-strict'),['triceps_brachii'],'Turning muscle bones off restores strict isolation');
  await option('#bContext');await option('#bRestore');
  phase='shared-joint';await page.evaluate(async()=>{await __atlas.goTo('humerus');__atlas.activatePin('extra_humerus_elbow_joint');});await card();await page.locator('#bIso').click();
  exact(await snapshot('elbow'),['humerus','radius','ulna'],'Shared elbow has precisely three allowed bones');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__thoraxCheck.snapshot().xray)).length===3,'Shared transparency preserved');
  await card();await page.locator('.pinbox [data-gobone="radius"]').click();await card();check(await page.evaluate(()=>__atlas.state.pin)==='extra_humerus_elbow_joint','Shared pin ID survives participant selection');
  phase='bone-canvas';await page.evaluate(async()=>{__atlas.activatePin(null);await __atlas.goTo('humerus_left');});await card();await page.locator('#bIso').click();
  exact(await snapshot('left-bone-isolation'),['humerus_left'],'Single left bone isolation');await close();await page.waitForTimeout(700);
  let target=await page.evaluate(()=>__thoraxCheck.clickPoint('humerus_left'));check(!!target,'Left humerus has real raycast target');await page.mouse.click(target.x,target.y);
  check(await page.evaluate(()=>__atlas.state.sel)==='humerus_left','Real canvas click selects left ID');
  const bvh=await page.evaluate(t=>__thoraxCheck.compare(t),target);check(bvh.bvh>0&&bvh.rays.some(r=>r.hits>0),'Left bone BVH agrees with native rays');
  await option('#bRestore');await side('both');await page.evaluate(()=>__atlas.goTo('humerus'));check((await snapshot('selected-both')).side==='both','Selection preserves explicit both-side mode');
  await side('left');await page.screenshot({path:shot+'-left.png'});
  phase='section-context';await page.evaluate(()=>__atlas.enterSection('neck'));s=await snapshot('neck-default');check(s.side==='both','Side preference is local to each section');
  await page.evaluate(async()=>{await __atlas.goTo('cervical_7');const p=ATLAS.pins.find(p=>p.id.includes('c7_t1')&&p.relations?.some(r=>r.bone==='thoracic_1'));if(!p)throw Error('C7-T1 fixture');__atlas.activatePin(p.id);});await card();await page.locator('#bIso').click();
  exact(await snapshot('c7-t1'),['cervical_7','thoracic_1'],'Cross-section context owner survives shared isolation');
  await option('#bContext');exact(await snapshot('c7-t1-no-background'),['cervical_7','thoracic_1'],'Shared components survive background off');await option('#bContext');
  phase='head-and-cuts';await page.evaluate(()=>__atlas.enterSection('head'));await side('left');
  await page.evaluate(()=>__atlas.goTo('masseter_left'));await card();await page.locator('#bIso').click();exact(await snapshot('masseter'),['masseter_left'],'Left head muscle strict isolation');
  await option('#bMuscleBones');s=await snapshot('masseter-bones');exact(s,['masseter_left'],'Missing attachment relations do not invent bone context');
  await card();check((await page.locator('#sheet').textContent()).includes('нет явных костных связей'),'Missing muscle links are disclosed in card');
  await page.evaluate(()=>__atlas.goTo('temporalis_left'));await card();await page.locator('#bIso').click();s=await snapshot('temporalis-bones');check(s.visible.filter(x=>x.kind==='b').length>0,'Existing left muscle links supply bone context');
  await page.evaluate(()=>__atlas.goTo('temporal_left'));await card();await page.locator('#bIso').click();exact(await snapshot('temporal'),['temporal_left'],'Left temporal isolation');
  await option('#bHeadCut');s=await snapshot('cut');check(s.cut,'Cut is active');await close();await page.waitForTimeout(700);
  target=await page.evaluate(()=>__thoraxCheck.clickPoint('temporal_left'));check(!!target,'Unclipped temporal surface target');
  check((await snapshot('cut-ray')).firstHitOnly===false,'Cut disables firstHitOnly when casting');
  const cutBvh=await page.evaluate(t=>__thoraxCheck.compare(t),target);check(cutBvh.bvh>0,'Cut BVH agrees with native filtered rays');
  await option('#bHeadCut');await page.evaluate(()=>__atlas.enterSection('arm'));check((await snapshot('return-arm')).side==='left','Arm side survives section transitions');
  phase='persistence';await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__ready);await page.evaluate(()=>__atlas.enterSection('arm'));check((await snapshot('reload')).side==='left','Side preference survives reload');
  await side('both');await sub('all');await option('[data-peel="3"]');s=await snapshot('restored-both');check(s.visible.some(x=>x.id==='humerus')&&s.visible.some(x=>x.id==='humerus_left'),'Both sides available after restore/layer switch');
  await page.evaluate(t=>document.documentElement.dataset.theme=t,theme==='dark'?'light':'dark');await page.screenshot({path:shot+'-opposite-theme.png'});
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');check(errors.length===0,'No console/page errors');
  return {status:'passed',width,theme,checks,snapshots,bvh,cutBvh,errors};
 }catch(e){return {status:'failed',phase,error:String(e),width,theme,checks,snapshots,errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unrouteAll({behavior:'wait'});}
}
const run=await createEvidenceRun(process.cwd(),'side-isolation-mcp'),width=Number(process.argv[2]||1280),theme=process.argv[3]||'dark';
const fixture=await run.write('scenario.js','async(page)=>('+browser.toString()+')(page,'+JSON.stringify({width,theme,partsOnly:process.argv[4]==='parts',shot:path.join(run.dir,'side'),probe})+')');
console.log(JSON.stringify({fixture,run:run.dir}));
