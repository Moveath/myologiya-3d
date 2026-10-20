// Run the exported checks through Playwright MCP against the local server.
// No production debug API and no dependency installation are required.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {indexLandmarks, relatedBoneIds, isOwnBoneTerm, landmarkSearchOwner, contributingBoneIds, hasLandmarkPosition} from '../site/atlas-landmarks.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scripts = ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
  'pins','pins-leg','pins-head','pins-neck','pins-thorax','pins-context-bones','pins-shared'];

export async function checkData() {
  const box = {window:{}};
  vm.createContext(box);
  for (const name of scripts.filter(n=>n!=='pins-shared')) vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
  const baseline=JSON.parse(JSON.stringify(box.window.ATLAS)), oldIndex=indexLandmarks(baseline.pins);
  vm.runInContext(await fs.readFile(path.join(root,'site/pins-shared.js'),'utf8'),box);
  const a = JSON.parse(JSON.stringify(box.window.ATLAS)), index = indexLandmarks(a.pins);
  const shared = a.pins.filter(p=>p.concept==='skull-whole-054');
  assert.equal(shared.length,2);
  assert.equal(index.byBone.occipital.filter(p=>isOwnBoneTerm(p,'occipital')).length,36);
  for (const p of shared) {
    assert.deepEqual(relatedBoneIds(p),['temporal_'+p.side,'occipital']);
    assert.equal(p.c,'A02.1.00.054');
    assert.equal(p.anchors.length,1);
    assert.deepEqual(p.p,index.byId[p.anchors[0].sourcePin].p);
    for (const bone of relatedBoneIds(p)) {
      assert.ok(a.bones[bone]);
      assert.equal(index.byBone[bone].filter(q=>q.id===p.id).length,1);
      assert.equal(index.byBone[bone].find(q=>q.id===p.id),p,'Keep one object, not a bone-specific copy');
      assert.equal(landmarkSearchOwner(p,bone),bone);
    }
    assert.ok(!index.byBone['temporal_'+(p.side==='left'?'right':'left')].includes(p));
    for (const r of p.relations) for (const ref of r.refs) assert.ok(p.refs.some(s=>s.id===ref&&s.locator));
  }
  for (const p of a.pins.filter(p=>p.sh)) for (const b of p.sh) assert.ok(index.byBone[b].includes(p));
  const reviewed=a.pins.filter(p=>p.relations?.length);
  for(const p of reviewed){
    assert.equal(new Set(p.relations.map(r=>r.bone)).size,p.relations.length);
    for(const r of p.relations){
      assert.ok(a.bones[r.bone]);
      assert.equal(index.byBone[r.bone].filter(q=>q.id===p.id).length,1);
      assert.equal(index.byBone[r.bone].find(q=>q.id===p.id),p);
      const refs=r.refs.map(id=>p.refs.find(s=>s.id===id));
      assert.ok(refs.every(s=>s?.url&&s?.locator));
      assert.ok(new Set(refs.map(s=>s.authorGroup)).size>=2);
    }
  }
  let cards=0;
  for(const [id,bone] of Object.entries(a.bones)){
    if(bone.g.startsWith('b_soft'))continue;cards++;
    assert.deepEqual((index.byBone[id]||[]).filter(p=>isOwnBoneTerm(p,id)).map(p=>p.id),
      (oldIndex.byBone[id]||[]).filter(p=>isOwnBoneTerm(p,id)).map(p=>p.id),'Own catalogue changed: '+id);
  }
  assert.equal(cards,141);
  for(const old of baseline.pins){
    const p=index.byId[old.id];assert.ok(p,'Lost ID: '+old.id);
    for(const field of ['b','c','t','lat','ru','x','p','n','m','loc','part','sh'])assert.deepEqual(p[field],old[field],old.id+': '+field);
    for(const ref of old.refs||[])assert.ok(p.refs.some(r=>JSON.stringify(r)===JSON.stringify(ref)));
  }
  assert.equal(hasLandmarkPosition(index.byId.cal_sinus_tarsi),false);
  assert.deepEqual(relatedBoneIds(index.byId.cal_sinus_tarsi),['calcaneus','talus']);
  assert.deepEqual(contributingBoneIds(index.byId.carp_os_centrale),[],'A contextual variant is not formed by eight bones');
  const whole=JSON.parse(await fs.readFile(path.join(root,'site/skull-whole.json'),'utf8')).rows.find(r=>r.c===shared[0].c);
  assert.deepEqual(whole.mainPinInstances.map(p=>p.id).sort(),shared.map(p=>p.id).sort());
  return {reviewedInstances:reviewed.length,reviewedConcepts:new Set(reviewed.map(p=>p.concept)).size,boneCardsChecked:cards,
    totalPins:a.pins.length,unlocated:a.pins.filter(p=>!p.p).length,suppressedUnverified:a.pins.filter(p=>p.p&&!hasLandmarkPosition(p)).length,
    preservedOriginalIDs:baseline.pins.length,ownOccipitalTerms:36,legacyShared:a.pins.filter(p=>p.sh).length};
}

// Test-only access to scene measurements. The actual application is served unchanged on disk.
const probe = `window.__sharedCheck={
 snapshot(){return {sel:state.sel,pin:state.pin,visibleBones:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xrayBones:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),clipped:pinById[state.pin]?.p?pointClipped(new THREE.Vector3(...pinById[state.pin].p)):null};},
 distances(){scene.updateMatrixWorld(true);return PINS.filter(p=>p.concept==='skull-whole-054').map(p=>{const point=new THREE.Vector3(...p.p),triangle=new THREE.Triangle(),closest=new THREE.Vector3();let best=Infinity;for(const mesh of structs.get(p.b).meshes){const g=mesh.geometry,pos=g.attributes.position,idx=g.index;for(let i=0;i<(idx?idx.count:pos.count);i+=3){for(const [j,v] of [triangle.a,triangle.b,triangle.c].entries())v.fromBufferAttribute(pos,idx?idx.getX(i+j):i+j).applyMatrix4(mesh.matrixWorld);triangle.closestPointToPoint(point,closest);best=Math.min(best,point.distanceTo(closest));}}return {id:p.id,mm:best*1000};});},
 clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+35;y<r.height-inset.bottom-15;y+=12)for(let x=24;x<r.width-inset.right-15;x+=12){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;}
};\n`;

async function openCard(page) {
  if(await page.locator('#mobileCard').isVisible() && (await page.locator('#app').getAttribute('data-card-open'))!=='true') await page.locator('#mobileCard').click();
  const more=page.locator('#bMore');
  if(await more.isVisible()&&(await more.textContent())==='Подробнее') await more.click();
}

export async function checkBrowser(page, {base='http://127.0.0.1:8782',width=1280,theme='light'}={}) {
  const errors=[];
  const errorHandler=e=>errors.push(String(e));
  const consoleHandler=m=>{if(m.type()==='error')errors.push(m.text());};
  page.on('pageerror',errorHandler);page.on('console',consoleHandler);
  await page.setViewportSize({width,height:width===390?844:860});
  await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async route=>{
    const response=await route.fetch();
    await route.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});
  });
  const shots=path.join(root,'shots/shared-landmarks');await fs.mkdir(shots,{recursive:true});
  try {
    await page.goto(base+'/local.html?theme='+theme,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.__ready);
    await page.evaluate(()=>__atlas.enterSection('head'));
    for(const [bone,side] of [['temporal_right','right'],['occipital','right'],['temporal_left','left'],['occipital','left']]){
      const id='shared_jugular_foramen_'+side;
      await page.evaluate(b=>__atlas.goTo(b),bone);await openCard(page);
      const chip=page.locator('#sheet [data-pinid="'+id+'"]');assert.equal(await chip.count(),1);
      await chip.click();
      assert.deepEqual(await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin})),{sel:bone,pin:id});
      assert.equal(await page.locator('#sheet .pinbox [data-gobone]').count(),2);
      assert.equal(await page.locator('.pin[data-pinid="'+id+'"]').count(),1);
      assert.ok((await page.locator('.pinbox').textContent()).includes('не центр просвета'));
      const other=bone==='occipital'?'temporal_'+side:'occipital';
      await page.locator('.pinbox [data-gobone="'+other+'"]').click();
      assert.deepEqual(await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin})),{sel:other,pin:id});
    }
    const distances=await page.evaluate(()=>__sharedCheck.distances());
    assert.ok(distances.every(p=>p.mm<.02),'Point must also lie on the loaded, compressed published GLB');
    await page.evaluate(()=>__atlas.goTo('temporal_left',null,'shared_jugular_foramen_left'));await openCard(page);
    await page.locator('#bIso').click();
    assert.deepEqual((await page.evaluate(()=>__sharedCheck.snapshot().visibleBones)).sort(),['occipital','temporal_left']);
    await openCard(page);
    await page.locator('#bBoneXray').click();
    assert.deepEqual((await page.evaluate(()=>__sharedCheck.snapshot().xrayBones)).sort(),['occipital','temporal_left']);
    await openCard(page);
    await page.locator('#bBoneXray').click();
    if(width===390 && await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();
    // Click the actual overlay in the model, then a real raycast hit on the other bone.
    const marker=page.locator('.pin[data-pinid="shared_jugular_foramen_left"]');
    await marker.click();assert.equal(await page.evaluate(()=>__atlas.state.pin),null);
    await marker.click();assert.equal(await page.evaluate(()=>__atlas.state.pin),'shared_jugular_foramen_left');
    if(width===390 && await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();
    const point=await page.evaluate(()=>__sharedCheck.clickPoint('occipital'));assert.ok(point,'A visible occipital mesh hit is required');
    await page.mouse.click(point.x,point.y);
    assert.deepEqual(await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin})),{sel:'occipital',pin:'shared_jugular_foramen_left'});
    assert.deepEqual((await page.evaluate(()=>__sharedCheck.snapshot().visibleBones)).sort(),['occipital','temporal_left']);
    assert.equal(await page.evaluate(()=>__atlas.state.isolate),'occipital');
    await page.screenshot({path:path.join(shots,`${width}-${theme}-shared.png`)});
    // Clipping hides the same marker; choosing it from a card reveals it again.
    if(width===390)await page.locator('#bOptions').click();
    await page.locator('#bHeadCut').click();await page.locator('#headCutAxis').selectOption('x');
    await page.locator('#headCutPosition').fill('0');
    assert.equal(await page.evaluate(()=>__sharedCheck.snapshot().clipped),true);
    await page.waitForFunction(()=>document.querySelector('.pin.on')?.hidden===true);
    assert.equal(await marker.isVisible(),false);
    await page.locator('#bHeadCut').click();
    if(width===390)await page.locator('#closeOptions').click();
    // Search lists each side once, even with occipital as the current owner.
    await page.locator('#bList').click();await page.locator('#q').fill('foramen jugulare');
    assert.equal(await page.locator('#dlist [data-pinjump^="shared_jugular_"]').count(),2);
    await page.locator('#dlist [data-pinjump="shared_jugular_foramen_right"]').click();
    assert.equal(await page.evaluate(()=>__atlas.state.pin),'shared_jugular_foramen_right');
    // Unlocated records remain selectable but must never acquire a fake marker.
    await page.evaluate(()=>{const p=ATLAS.pins.find(p=>p.id==='shared_jugular_foramen_right');delete p.p;delete p.n;__atlas.activatePin(p.id,true);});
    assert.equal(await page.locator('.pin[data-pinid="shared_jugular_foramen_right"]').count(),0);
    assert.ok((await page.locator('.pinbox').textContent()).includes('Расположение уточняется'));
    await openCard(page);await page.locator('#bDeselect').click();
    assert.equal(await page.evaluate(()=>__atlas.state.pin),null);
    assert.deepEqual(await page.evaluate(()=>__sharedCheck.snapshot().visibleBones),['occipital']);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    assert.deepEqual(errors,[]);
    return {width,theme,status:'passed',distances,errors};
  } finally {
    page.off('pageerror',errorHandler);page.off('console',consoleHandler);
    await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');
  }
}

export async function checkExpansionBrowser(page,{base='http://127.0.0.1:8782',width=1280,theme='light',offset=0,limit=null,finalChecks=true}={}){
  const errors=[];const onError=e=>errors.push(String(e));const onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
  page.on('pageerror',onError);page.on('console',onConsole);
  await page.setViewportSize({width,height:width===390?844:860});
  await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  try{
    await page.goto(base+'/local.html?theme='+theme,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.__ready);
    const allRecords=await page.evaluate(()=>ATLAS.pins.filter(p=>p.relations?.length).map(p=>({id:p.id,b:p.b,bones:p.relations.map(r=>r.bone),located:!!p.p&&p.anchorStatus!=='unverified'})));
    const records=allRecords.slice(offset,limit===null?undefined:offset+limit);
    let edges=0;
    for(const p of records){
      for(const bone of p.bones){
        await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},bone);await openCard(page);
        const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');assert.equal(await chip.count(),1,'Duplicate/missing chip '+p.id+' on '+bone);
        await chip.scrollIntoViewIfNeeded();await chip.click();await openCard(page);
        assert.deepEqual(await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin})),{sel:bone,pin:p.id});
        assert.equal(await page.locator('.pinbox [data-gobone]').count(),p.bones.length);
        assert.equal(await page.locator('.pin[data-pinid="'+p.id+'"]').count(),p.located?1:0);
        edges++;
      }
    }
    if(!finalChecks){assert.deepEqual(errors,[]);return {status:'passed',width,theme,offset,instances:records.length,ownerCardEdges:edges,errors};}
    const openList=async()=>{if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();await page.locator('#bList').click();};
    // Region change and two-bone controls on the leg, including the suppressed old coordinate.
    await page.evaluate(()=>{__atlas.activatePin(null);return __atlas.goTo('calcaneus');});await openCard(page);
    await page.locator('#sheet [data-pinid="cal_sinus_tarsi"]').click();await openCard(page);
    await page.locator('#bIso').click();await openCard(page);
    assert.deepEqual((await page.evaluate(()=>__sharedCheck.snapshot().visibleBones)).sort(),['calcaneus','talus']);
    await page.locator('#bBoneXray').click();await openCard(page);
    assert.deepEqual((await page.evaluate(()=>__sharedCheck.snapshot().xrayBones)).sort(),['calcaneus','talus']);
    await page.locator('.pinbox [data-gobone="talus"]').click();await openCard(page);
    assert.equal(await page.evaluate(()=>__atlas.state.pin),'cal_sinus_tarsi');
    assert.equal(await page.locator('.pin[data-pinid="cal_sinus_tarsi"]').count(),0);
    await page.locator('#bBoneXray').click();await openCard(page);
    await page.screenshot({path:path.join(root,'shots/shared-landmarks',`${width}-${theme}-sinus.png`)});
    await openList();await page.locator('#q').fill('sinus tarsi');
    assert.equal(await page.locator('#dlist [data-pinjump="cal_sinus_tarsi"]').count(),1);
    await page.locator('#dlist [data-pinjump="cal_sinus_tarsi"]').click();
    assert.equal(await page.evaluate(()=>__atlas.state.sel),'talus');
    // A newly created unlocated structure has one card per side, never a made-up marker.
    await page.evaluate(()=>{__atlas.activatePin(null);return __atlas.goTo('frontal');});await openCard(page);
    await page.locator('#sheet [data-pinid="shared_skull_079_right"]').click();await openCard(page);
    await page.locator('.pinbox [data-gobone="ethmoid"]').click();await openCard(page);
    assert.equal(await page.evaluate(()=>__atlas.state.pin),'shared_skull_079_right');
    await openList();await page.locator('#q').fill('A02.1.00.079');
    assert.equal(await page.locator('#dlist [data-pinjump^="shared_skull_079_"]').count(),2);
    await page.locator('#dlist [data-pinjump="shared_skull_079_left"]').click();await openCard(page);
    assert.equal(await page.locator('.pin[data-pinid^="shared_skull_079_"]').count(),0);
    await page.screenshot({path:path.join(root,'shots/shared-landmarks',`${width}-${theme}-unlocated.png`)});
    await openList();await page.locator('#q').fill('A02.1.00.051');
    assert.equal(await page.locator('#dlist [data-pinjump="head_occipital_A02_1_04_006"]').count(),1);
    await page.locator('#dlist [data-pinjump="head_occipital_A02_1_04_006"]').click();await openCard(page);
    assert.equal(await page.locator('[data-detail-part="whole:A02.1.00.051"]').count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    assert.deepEqual(errors,[]);
    return {status:'passed',width,theme,offset,instances:records.length,ownerCardEdges:edges,finalChecks:true,errors};
  }finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
}

// Playwright MCP's VM does not expose Node imports. Supply only the tiny helpers
// used by this same browser check; screenshots are written by Playwright itself.
export function mcpScript(options) {
  return `async (page) => {
    const root=${JSON.stringify(root)}, probe=${JSON.stringify(probe)};
    const path={join:(...parts)=>parts.join('/')}, fs={mkdir:async()=>{}};
    const assert={
      ok:(v,m)=>{if(!v)throw Error(m||'Expected truthy value');},
      equal:(a,b,m)=>{if(a!==b)throw Error(m||JSON.stringify({actual:a,expected:b}));},
      deepEqual:(a,b,m)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(m||JSON.stringify({actual:a,expected:b}));}
    };
    ${openCard.toString()}
    ${checkBrowser.toString()}
    ${checkExpansionBrowser.toString()}
    return await ${options.expansion?'checkExpansionBrowser':'checkBrowser'}(page,${JSON.stringify(options)});
  }`;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv[2]?.startsWith('--mcp')) console.log(mcpScript({width:Number(process.argv[3] || 1280),theme:process.argv[4] || 'light',expansion:process.argv[2]==='--mcp-expansion',offset:Number(process.argv[5]||0),limit:process.argv[6]?Number(process.argv[6]):null,finalChecks:process.argv[7]!=='skip'}));
  else console.log(JSON.stringify({data:await checkData(),ui:'Run the exported checkBrowser or --mcp output through Playwright MCP'}));
}
