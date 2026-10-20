// Stage-5 skull regression: metadata and UI contracts, never anatomical acceptance.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {indexLandmarks, relatedBoneIds, hasLandmarkPosition} from '../site/atlas-landmarks.js';
import {checkData as checkSharedData} from './verify-shared-landmarks.mjs';
import {createEvidenceRun} from './evidence-run.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const research=path.join(root,'research/stage5-skull-2026-10-16');
const kinds=['point','area','line','space','volume','unknown'];
const scripts=['data','data-leg','data-head','data-neck','data-thorax','data-context-bones',
  'pins','pins-leg','pins-head','pins-neck','pins-thorax','pins-context-bones','pins-shared'];
const digest=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
export async function readManifest(){
  const manifest=JSON.parse(await fs.readFile(path.join(research,'implemented-manifest.json'),'utf8'));
  assert.ok(Array.isArray(manifest.newSharedIds)&&manifest.newSharedIds.length>0,'Manifest must list the scientifically accepted implemented instances');
  assert.equal(new Set(manifest.newSharedIds).size,manifest.newSharedIds.length,'Manifest duplicate ID');
  return manifest;
}

export async function checkData(){
  const manifest=await readManifest();
  const baseline=JSON.parse(await fs.readFile(path.join(research,'head-pin-baseline.json'),'utf8'));
  assert.equal(baseline.records.length,521);
  const box={window:{}};vm.createContext(box);
  for(const name of scripts)vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
  const a=JSON.parse(JSON.stringify(box.window.ATLAS)),index=indexLandmarks(a.pins);
  const baselineIDs=new Set(baseline.records.map(p=>p.id));
  assert.equal(baselineIDs.size,521);
  const head=a.pins.filter(p=>baselineIDs.has(p.id));assert.equal(head.length,521);
  for(const old of baseline.records){
    const pin=index.byId[old.id];assert.ok(pin,'Lost skull ID: '+old.id);
    assert.equal(digest([pin.b,pin.c,pin.p,pin.n,pin.loc]),old.positionSha256,'Changed bone/code/coordinate/localization: '+old.id);
    assert.ok(kinds.includes(pin.geometryKind),'Missing/invalid explicit geometryKind: '+pin.id);
  }
  const counts={explicit:head.filter(p=>p.geometryKind!=='unknown').length,unknown:head.filter(p=>p.geometryKind==='unknown').length};
  // Later reviewed batches may refine unknowns, but must not erase accepted kinds.
  const firstReview=JSON.parse(await fs.readFile(path.join(research,'catalog-review.json'),'utf8'));
  for(const row of firstReview.records.filter(p=>p.geometryKind!=='unknown'))
    assert.equal(index.byId[row.id].geometryKind,row.geometryKind,'Previously reviewed kind changed: '+row.id);
  assert.ok(counts.unknown<=manifest.headGeometryKindCounts.unknown,'Unreviewed kinds increased');
  for(const side of ['right','left']){
    const local=index.byId['head_maxilla_'+side+'_A02_1_12_006'];
    assert.equal(local.partOf,'shared_skull_072_'+side,'Local rim must retain its common parent');
    const common=index.byId[local.partOf];
    assert.equal(common.c,'A02.1.00.072');
    assert.deepEqual(relatedBoneIds(common),['maxilla_'+side,'zygomatic_'+side]);
    assert.equal(Object.hasOwn(common,'p'),false,'Local representative point is not the full common rim');
    assert.ok(local.modelNote.includes('локальный верхнечелюстной участок'));
  }
  const education=JSON.parse(await fs.readFile(path.join(root,'site/skull-education.json'),'utf8'));
  const educationIds=new Set(education.entries.map(row=>row.id)),educationOptouts=[];
  const instances=[];
  for(const id of manifest.newSharedIds){
    const pin=index.byId[id];assert.ok(pin,'Missing implemented instance: '+id);
    assert.equal(Object.hasOwn(pin,'p'),false,'No coordinates authorized for '+id);
    assert.equal(Object.hasOwn(pin,'n'),false,'No normal authorized for '+id);
    assert.equal(hasLandmarkPosition(pin),false);
    assert.ok(kinds.includes(pin.geometryKind)&&pin.geometryKind!=='unknown','Reviewed geometryKind required: '+id);
    const educationTarget=pin.educationCode?'whole:'+pin.educationCode:pin.concept?.startsWith('skull-whole-')?'whole:'+pin.c:pin.b+':'+pin.c;
    if(pin.educationAvailable===false)educationOptouts.push(id);
    else assert.ok(educationIds.has(educationTarget),'Missing educational target (would silently select another structure): '+educationTarget);
    const bones=relatedBoneIds(pin);assert.ok(bones.length>=2);
    assert.ok(bones.includes(pin.b),'Legacy owner must belong to related bones: '+id);
    for(const bone of bones){
      assert.ok(a.bones[bone],id+': unknown bone '+bone);
      const matches=index.byBone[bone].filter(p=>p.id===id);assert.equal(matches.length,1);
      assert.equal(matches[0],pin,'Canonical object must be shared, not copied');
    }
    instances.push({id,c:pin.c,b:pin.b,bones,geometryKind:pin.geometryKind});
  }
  for(const side of ['right','left'])assert.equal(index.byId['shared_temporozygomatic_suture_'+side].educationAvailable,false,'No unrelated educational fallback for the new suture');
  const shared=await checkSharedData();
  return {status:'passed',anatomicalAcceptance:false,geometryAcceptance:false,baselineIDs:521,
    baselineSourceSha256:baseline.sourceSha256,headGeometryKindCounts:counts,newSharedInstances:instances.length,
    newRelationEdges:instances.reduce((n,p)=>n+p.bones.length,0),educationTargetsVerified:instances.length-educationOptouts.length,
    educationOptouts,instances,existingSharedChecks:shared};
}

async function openCard(page){
  if(await page.locator('#mobileCard').isVisible()&&(await page.locator('#app').getAttribute('data-card-open',{timeout:7000}))!=='true')await page.locator('#mobileCard').click({timeout:7000});
  const more=page.locator('#bMore');if(await more.isVisible()&&(await more.textContent({timeout:7000}))==='Подробнее')await more.click({timeout:7000});
  await page.locator('#sheet').waitFor({state:'visible',timeout:7000});
}

export async function checkBrowser(page,{base='http://127.0.0.1:8782',width=1280,theme='dark',ids,offset=0,limit=null,finalChecks=true,budgetMs=45000,evidenceDir}={}){
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

export async function mcpScript(options={}){
  const manifest=await readManifest(),run=await createEvidenceRun(root,'skull-mcp');
  return `async (page) => {
    const root=${JSON.stringify(root)},path={join:(...parts)=>parts.join('/')},fs={mkdir:async()=>{}};
    const assert={ok:(v,m)=>{if(!v)throw Error(m||'Expected truthy value');},equal:(a,b,m)=>{if(a!==b)throw Error(m||JSON.stringify({actual:a,expected:b}));},deepEqual:(a,b,m)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(m||JSON.stringify({actual:a,expected:b}));}};
    ${openCard.toString()}
    ${checkBrowser.toString()}
    return await checkBrowser(page,${JSON.stringify({ids:manifest.newSharedIds,...options,evidenceDir:run.dir})});
  }`;
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  if(process.argv[2]==='--mcp')console.log(await mcpScript({width:Number(process.argv[3]||1280),theme:process.argv[4]||'dark',offset:Number(process.argv[5]||0),limit:process.argv[6]?Number(process.argv[6]):null,finalChecks:process.argv[7]!=='skip'}));
  else {const {instances,...summary}=await checkData();console.log(JSON.stringify(summary,null,2));}
}
