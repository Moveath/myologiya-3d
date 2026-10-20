async (page) => {
    const root="C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D",path={join:(...parts)=>parts.join('/')},fs={mkdir:async()=>{}};
    const assert={ok:(v,m)=>{if(!v)throw Error(m||'Expected truthy value');},equal:(a,b,m)=>{if(a!==b)throw Error(m||JSON.stringify({actual:a,expected:b}));},deepEqual:(a,b,m)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(m||JSON.stringify({actual:a,expected:b}));}};
    async function openCard(page){
  if(await page.locator('#mobileCard').isVisible()&&(await page.locator('#app').getAttribute('data-card-open',{timeout:7000}))!=='true')await page.locator('#mobileCard').click({timeout:7000});
  const more=page.locator('#bMore');if(await more.isVisible()&&(await more.textContent({timeout:7000}))==='Подробнее')await more.click({timeout:7000});
  await page.locator('#sheet').waitFor({state:'visible',timeout:7000});
}
    async function checkBrowser(page,{base='http://127.0.0.1:8782',width=1280,theme='dark',ids,offset=0,limit=null,finalChecks=true,budgetMs=45000,evidenceDir}={}){
  assert.ok(Array.isArray(ids)&&ids.length,'Pass implemented manifest IDs, not guessed candidates');
  const started=Date.now(),progress={status:'running',phase:'setup',width,theme,offset,completedEdges:0,completedInstances:0,lastPin:null,lastBone:null};
  const mark=async(phase,fields={})=>{Object.assign(progress,fields,{phase,elapsedMs:Date.now()-started});await page.evaluate(value=>{window.__stage5SkullProgress=value;},progress);};
  let actionsStarted;
  const checkBudget=()=>{if(Date.now()-actionsStarted>budgetMs)throw Error('Action budget exceeded ('+budgetMs+' ms); completed edges remain in progress, batch is not passed');};
  const errors=[],onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
  page.on('pageerror',onError);page.on('console',onConsole);
  await page.setViewportSize({width,height:width===390?844:860});
  await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const shots=evidenceDir || (await createEvidenceRun(root,'skull-browser')).dir;
  try{
    progress.phase='goto';
    await page.goto(base+'/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});
    await mark('app-ready');
    await page.waitForFunction(()=>window.__ready,undefined,{timeout:30000});
    await mark('head-loading');
    // enterSection is genuinely async; do not leave page.evaluate awaiting an
    // unbounded model fetch. Expose its result and bound the readiness wait.
    await page.evaluate(()=>{
      window.__stage5HeadLoad={status:'loading'};
      Promise.resolve(__atlas.enterSection('head')).then(ok=>{window.__stage5HeadLoad={status:ok?'ready':'failed'};},error=>{window.__stage5HeadLoad={status:'failed',error:String(error)};});
    });
    await page.waitForFunction(()=>window.__stage5HeadLoad?.status!=='loading',undefined,{timeout:30000});
    const loaded=await page.evaluate(()=>window.__stage5HeadLoad);assert.equal(loaded.status,'ready','Head load failed: '+JSON.stringify(loaded));
    actionsStarted=Date.now();await mark('read-manifest-records');
    const all=await page.evaluate(ids=>ids.map(id=>{
      const p=ATLAS.pins.find(p=>p.id===id);if(!p)throw Error('Missing implemented pin '+id);
      return {id:p.id,c:p.c,b:p.b,bones:p.relations.map(r=>r.bone),geometryKind:p.geometryKind,educationAvailable:p.educationAvailable!==false};
    }),ids);
    const records=all.slice(offset,limit===null?undefined:offset+limit);let edges=0,transitions=0;
    for(const pin of records){
      for(const bone of pin.bones){
        checkBudget();await mark('select-bone',{lastPin:pin.id,lastBone:bone});
        await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},bone);await openCard(page);
        const chip=page.locator('#sheet [data-pinid="'+pin.id+'"]');assert.equal(await chip.count(),1,'Single card entry: '+pin.id+' on '+bone);
        await mark('click-landmark');await chip.scrollIntoViewIfNeeded({timeout:7000});await chip.click({timeout:7000});await openCard(page);
        assert.deepEqual(await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin})),{sel:bone,pin:pin.id});
        assert.equal(await page.locator('.pin[data-pinid="'+pin.id+'"]').count(),0,'An unlocated catalogue record must not gain a marker');
        assert.equal(await page.locator('.pinbox [data-gobone]').count(),pin.bones.length);
        assert.equal(await page.locator('.pinbox [data-detail-mode="education"]').count(),pin.educationAvailable?1:0,'Educational button must have an existing target or be explicitly omitted: '+pin.id);
        const meta=page.locator('.pinbox .landmark-geometry');assert.equal(await meta.getAttribute('data-geometry-kind',{timeout:7000}),pin.geometryKind);
        assert.ok((await meta.textContent({timeout:7000})).includes('маркер не показан'));
        const other=pin.bones.find(b=>b!==bone);
        await mark('related-bone-transition',{targetBone:other});await page.locator('.pinbox [data-gobone="'+other+'"]').click({timeout:7000});await openCard(page);
        assert.deepEqual(await page.evaluate(()=>({sel:__atlas.state.sel,pin:__atlas.state.pin})),{sel:other,pin:pin.id});
        edges++;transitions++;await mark('edge-complete',{completedEdges:edges});
      }
      await mark('instance-complete',{completedInstances:progress.completedInstances+1,nextOffset:offset+progress.completedInstances+1});
    }
    const searched=[];const existingKinds=[];
    if(finalChecks){
      for(const code of [...new Set(all.map(p=>p.c))]){
        checkBudget();await mark('search',{lastCode:code});
        if(width===390&&await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click({timeout:7000});
        await page.locator('#bList').click({timeout:7000});await page.locator('#q').fill(code,{timeout:7000});
        const expected=all.filter(p=>p.c===code);
        for(const pin of expected)assert.equal(await page.locator('#dlist [data-pinjump="'+pin.id+'"]').count(),1,'Search must retain one result per instance');
        await page.locator('#dlist [data-pinjump="'+expected[0].id+'"]').click({timeout:7000});await openCard(page);
        assert.equal(await page.evaluate(()=>__atlas.state.pin),expected[0].id);searched.push(code);
      }
      // Existing coordinates must remain representative anchors, not full extents.
      const representatives=await page.evaluate(()=>{
        const rows=ATLAS.pins.filter(p=>p.id.startsWith('head_')&&p.p&&p.anchorStatus!=='unverified'&&p.geometryKind);
        return [...new Set(rows.map(p=>p.geometryKind))].map(kind=>{const p=rows.find(p=>p.geometryKind===kind);return {id:p.id,b:p.b,kind};});
      });
      for(const pin of representatives){
        checkBudget();await mark('existing-marker-kind',{lastPin:pin.id,lastBone:pin.b,geometryKind:pin.kind});
        await page.evaluate(b=>{__atlas.activatePin(null);return __atlas.goTo(b);},pin.b);await openCard(page);
        const chip=page.locator('#sheet [data-pinid="'+pin.id+'"]');await chip.scrollIntoViewIfNeeded({timeout:7000});await chip.click({timeout:7000});await openCard(page);
        assert.equal(await page.locator('.pin[data-pinid="'+pin.id+'"]').count(),1);
        const meta=page.locator('.pinbox .landmark-geometry');assert.equal(await meta.getAttribute('data-geometry-kind',{timeout:7000}),pin.kind);
        const text=await meta.textContent({timeout:7000});if(['area','line','space','volume'].includes(pin.kind))assert.ok(text.includes('не задаёт полную линию, границы, поверхность или объём'));
        if(pin.kind==='point')assert.ok(text.includes('само по себе не подтверждает точность'));
        if(pin.kind==='unknown')assert.ok(text.includes('требуют уточнения'));
        existingKinds.push(pin.kind);
      }
    }
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    assert.deepEqual(errors,[]);
    await mark('screenshot');
    const nonce=await page.evaluate(()=>crypto.randomUUID());
    const screenshot=path.join(shots,`${width}-${theme}-batch-${offset}-${nonce}.png`);await page.screenshot({path:screenshot,timeout:10000});
    await mark('complete',{status:'passed'});
    return {status:'passed',anatomicalAcceptance:false,geometryAcceptance:false,width,theme,offset,instances:records.length,
      relationEdges:edges,preservedPinTransitions:transitions,searchedCodes:searched,existingMarkerKinds:existingKinds,
      errors,screenshot,elapsedMs:Date.now()-started,coverageNote:'Shared clipping, isolation, xray and BVH are tested separately by verify-shared-landmarks.mjs.'};
  }catch(error){
    const failedPhase=progress.phase;Object.assign(progress,{status:'failed',failedPhase,error:String(error?.message||error),elapsedMs:Date.now()-started});
    try{await page.evaluate(value=>{window.__stage5SkullProgress=value;},progress);}catch{}
    return {...progress,anatomicalAcceptance:false,geometryAcceptance:false,errors};
  }finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('https://fonts.googleapis.com/**');}
}
    return await checkBrowser(page,{"ids":["shared_skull_015","shared_skull_016","shared_skull_017","shared_skull_019_right","shared_skull_019_left","shared_skull_020_right","shared_skull_020_left","shared_skull_023_right","shared_skull_023_left","shared_skull_047_right","shared_skull_047_left","shared_skull_055_right","shared_skull_055_left","shared_skull_056","shared_skull_067_right","shared_skull_067_left","shared_skull_075_right","shared_skull_075_left","shared_skull_076_right","shared_skull_076_left","shared_skull_077_right","shared_skull_077_left","shared_skull_078_right","shared_skull_078_left","shared_skull_079_right","shared_skull_079_left","shared_skull_080_right","shared_skull_080_left","shared_skull_084_right","shared_skull_084_left","shared_skull_097_right","shared_skull_097_left","shared_skull_nasal_bone_crest","shared_skull_050","shared_skull_087"],"width":390,"theme":"light","offset":0,"limit":4,"finalChecks":false,"budgetMs":55000,"evidenceDir":"C:\\Users\\Пользователь\\Desktop\\учеба\\Миология 3D\\research\\evidence-runs\\skull-mcp-2026-10-17T06-23-51-316Z-uaPfdX"});
  }