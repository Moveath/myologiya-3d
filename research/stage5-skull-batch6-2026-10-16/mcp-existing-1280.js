async (page) => {
    const root="C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D", probe="window.__sharedCheck={\n snapshot(){return {sel:state.sel,pin:state.pin,visibleBones:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xrayBones:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),clipped:pinById[state.pin]?.p?pointClipped(new THREE.Vector3(...pinById[state.pin].p)):null};},\n distances(){scene.updateMatrixWorld(true);return PINS.filter(p=>p.concept==='skull-whole-054').map(p=>{const point=new THREE.Vector3(...p.p),triangle=new THREE.Triangle(),closest=new THREE.Vector3();let best=Infinity;for(const mesh of structs.get(p.b).meshes){const g=mesh.geometry,pos=g.attributes.position,idx=g.index;for(let i=0;i<(idx?idx.count:pos.count);i+=3){for(const [j,v] of [triangle.a,triangle.b,triangle.c].entries())v.fromBufferAttribute(pos,idx?idx.getX(i+j):i+j).applyMatrix4(mesh.matrixWorld);triangle.closestPointToPoint(point,closest);best=Math.min(best,point.distanceTo(closest));}}return {id:p.id,mm:best*1000};});},\n clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+35;y<r.height-inset.bottom-15;y+=12)for(let x=24;x<r.width-inset.right-15;x+=12){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;}\n};\n";
    const path={join:(...parts)=>parts.join('/')}, fs={mkdir:async()=>{}};
    const assert={
      ok:(v,m)=>{if(!v)throw Error(m||'Expected truthy value');},
      equal:(a,b,m)=>{if(a!==b)throw Error(m||JSON.stringify({actual:a,expected:b}));},
      deepEqual:(a,b,m)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(m||JSON.stringify({actual:a,expected:b}));}
    };
    async function openCard(page) {
  if(await page.locator('#mobileCard').isVisible() && (await page.locator('#app').getAttribute('data-card-open'))!=='true') await page.locator('#mobileCard').click();
  const more=page.locator('#bMore');
  if(await more.isVisible()&&(await more.textContent())==='Подробнее') await more.click();
}
    async function checkBrowser(page, {base='http://127.0.0.1:8782',width=1280,theme='light'}={}) {
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
  const shots=path.join(root,'shots/stage5-skull-batch6/legacy');await fs.mkdir(shots,{recursive:true});
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
    async function checkExpansionBrowser(page,{base='http://127.0.0.1:8782',width=1280,theme='light',offset=0,limit=null,finalChecks=true}={}){
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
    await page.screenshot({path:path.join(root,'shots/stage5-skull-batch6/legacy',`${width}-${theme}-sinus.png`)});
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
    await page.screenshot({path:path.join(root,'shots/stage5-skull-batch6/legacy',`${width}-${theme}-unlocated.png`)});
    await openList();await page.locator('#q').fill('A02.1.00.051');
    assert.equal(await page.locator('#dlist [data-pinjump="head_occipital_A02_1_04_006"]').count(),1);
    await page.locator('#dlist [data-pinjump="head_occipital_A02_1_04_006"]').click();await openCard(page);
    assert.equal(await page.locator('[data-detail-part="whole:A02.1.00.051"]').count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    assert.deepEqual(errors,[]);
    return {status:'passed',width,theme,offset,instances:records.length,ownerCardEdges:edges,finalChecks:true,errors};
  }finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
}
    return await checkBrowser(page,{"width":1280,"theme":"dark","expansion":false,"offset":0,"limit":null,"finalChecks":true});
  }
