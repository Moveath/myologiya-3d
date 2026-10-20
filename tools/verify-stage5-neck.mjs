// Scope/preservation checks plus a Playwright MCP fixture; no anatomy acceptance.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {indexLandmarks,relatedBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
import {createEvidenceRun} from './evidence-run.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const baselineDir=path.join(root,'research/evidence-runs/stage5-neck-2026-10-17T08-47-16-476Z-I01uyt');
const scripts=['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'];
const bones=['hyoid','atlas','axis','cervical_3','cervical_4','cervical_5','cervical_6','cervical_7'];
async function data(){
 const box={window:{}};vm.createContext(box);
 for(const name of scripts)vm.runInContext(await fs.readFile(path.join(root,'site',name+'.js'),'utf8'),box);
 const A=JSON.parse(JSON.stringify(box.window.ATLAS)),before=JSON.parse(await fs.readFile(path.join(baselineDir,'atlas-before.json'),'utf8'));
 const idx=indexLandmarks(A.pins),oldIds=new Set(before.pins.map(p=>p.id)),own=A.pins.filter(p=>p.id.startsWith('neck_'));
 assert.equal(own.length,138);assert.deepEqual(A.bones,before.bones);assert.deepEqual(A.muscles,before.muscles);
 for(const old of before.pins){
  const now=idx.byId[old.id];assert.ok(now,'Lost ID '+old.id);
  if(!old.id.startsWith('neck_'))assert.deepEqual(now,old,'Unrelated record changed '+old.id);
  else {
   for(const key of ['id','b','c','ru','lat','p','n','loc','secondaryMarkers','refs','m','inc','taParen'])assert.deepEqual(now[key],old[key],old.id+': '+key);
   assert.ok(['point','line','area','space','volume'].includes(now.geometryKind));
   assert.ok(now.geometryKindReason);assert.equal(now.geometryReview.coordinateAcceptance,false);assert.equal(now.geometryReview.extentAcceptance,false);
  }
 }
 const added=A.pins.filter(p=>!oldIds.has(p.id)),shared=added.filter(p=>p.id.startsWith('shared_neck_'));
 assert.equal(added.length,17);assert.equal(shared.length,10);
 for(const p of added){
  assert.equal(hasLandmarkPosition(p),false);assert.equal(Object.hasOwn(p,'p'),false);assert.equal(Object.hasOwn(p,'n'),false);
  assert.ok(new Set(p.refs.map(r=>r.authorGroup)).size>=2);assert.ok(p.refs.every(r=>r.url&&r.locator));
  for(const b of relatedBoneIds(p)){assert.ok(bones.includes(b));assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);assert.equal(idx.byBone[b].find(q=>q.id===p.id),p);}
  for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id]);
 }
 for(let n=2;n<=6;n++)for(const side of ['right','left']){
  const p=idx.byId[`shared_neck_intervertebral_c${n}_c${n+1}_${side}`];
  assert.deepEqual(relatedBoneIds(p),[n===2?'axis':`cervical_${n}`,`cervical_${n+1}`]);assert.equal(p.side,side);assert.equal(p.geometryKind,'space');
 }
 for(const c of ['004','005'])assert.equal(idx.byId['neck_cervical_6_A02_2_02_'+c].concept,'c6-anterior-carotid-tubercle');
 const hashes=JSON.parse(await fs.readFile(path.join(baselineDir,'hashes-before.json'),'utf8'));
 const allowed=new Set(['scripts/make_pins_neck.py','scripts/make_shared_landmarks.py','verify/verify_neck_positions.py','tools/verify-neck-data.mjs','site/pins-neck.js','site/pins-shared.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
 let protectedFiles=0;for(const [name,hash] of Object.entries(hashes))if(!allowed.has(name)){
  assert.equal(createHash('sha256').update(await fs.readFile(path.join(root,name))).digest('hex'),hash,'Protected file changed '+name);protectedFiles++;
 }
 const report={status:'passed',bones:bones.length,originalLandmarks:own.length,classified:own.length,
  kinds:Object.fromEntries(['point','line','area','space','volume'].map(k=>[k,own.filter(p=>p.geometryKind===k).length])),
  newCards:added.length,newOwnDetails:7,newSharedInstances:10,newRelationEdges:20,
  unchangedOriginalCoordinates:138,protectedFiles,unchangedOtherPins:before.pins.length-own.length,
  totalPins:A.pins.length,unlocated:A.pins.filter(p=>!p.p).length,
  records:own.concat(added).map(p=>({id:p.id,b:p.b,c:p.c,ru:p.ru,geometryKind:p.geometryKind,reason:p.geometryKindReason||p.x,
    bones:relatedBoneIds(p),paired:p.anatomicalMultiplicity==='paired',located:!!p.p,secondaryMarkers:p.secondaryMarkers?.length||0,
    coordinateAcceptance:false,extentAcceptance:false,refs:p.refs})),
  anatomicalAcceptance:false,geometryAcceptance:false};
 const run=await createEvidenceRun(root,'stage5-neck-data');await run.write('data-regression.json',report);
 console.log(JSON.stringify({...report,records:undefined,evidence:run.dir}));return report;
}

// Instrumentation exists only in the fetched test response, never production.
const probe=`window.__neckCheck={snapshot:()=>({visible:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible)).map(s=>s.id),xray:[...structs.values()].filter(s=>s.kind==='b'&&s.meshes.some(m=>m.visible&&m.material===XRAY)).map(s=>s.id),cut:headCutActive()}),
clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=10)for(let x=15;x<r.width-inset.right-15;x+=10){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},
compare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};\n`;

async function browser(page,{width,theme,shot,probe}){
 const check=(v,m)=>{if(!v)throw Error(m);};let phase='start';const errors=[];
 const onError=e=>errors.push(String(e)),onConsole=m=>{if(m.type()==='error')errors.push(m.text());};
 page.on('pageerror',onError);page.on('console',onConsole);page.setDefaultTimeout(8000);
 const card=async()=>{if(await page.locator('#mobileCard').isVisible()){if(await page.locator('#app').getAttribute('data-card-open')!=='true')await page.locator('#mobileCard').click();}else if(await page.locator('#bMore').isVisible()&&await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();};
 const close=async()=>{if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();};
 try{
  await page.setViewportSize({width,height:width===390?844:900});await page.emulateMedia({colorScheme:theme,reducedMotion:'reduce'});
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.route('**/local.html*',async r=>{const response=await r.fetch();await r.fulfill({response,body:(await response.text()).replace('window.__atlas =',probe+'window.__atlas =')});});
  phase='load';await page.goto('http://127.0.0.1:8782/local.html?theme='+theme,{waitUntil:'domcontentloaded',timeout:30000});await page.waitForFunction(()=>window.__ready);
  await page.evaluate(()=>{window.__neckReady=false;__atlas.enterSection('neck').then(ok=>window.__neckReady=ok);});
  await page.waitForFunction(()=>window.__neckReady,undefined,{timeout:30000});
  const rows=await page.evaluate(()=>ATLAS.pins.filter(p=>p.id.startsWith('neck_')||p.id.startsWith('shared_neck_')||p.id.startsWith('extra_atlas_')||p.id.startsWith('extra_hyoid_')||p.id==='extra_axis_dens_neck').map(p=>({id:p.id,b:p.b,kind:p.geometryKind,p:!!p.p,bones:p.relations?.map(r=>r.bone)||[p.b]})));
  check(rows.length===155,'Expected 155 neck cards');
  phase='all-types';const typeChecks=await page.evaluate(rows=>{
   const results=[];for(const p of rows){__atlas.goTo(p.b);__atlas.activatePin(p.id);const el=document.querySelector('.pinbox .landmark-geometry');if(el?.dataset.geometryKind!==p.kind)throw Error('Card kind '+p.id);results.push(p.id);}return results.length;
  },rows);
  phase='unlocated-requirements';const requirements=await page.evaluate(rows=>{
   let count=0;for(const p of rows.filter(p=>!p.p)){__atlas.goTo(p.b);__atlas.activatePin(p.id);const source=ATLAS.pins.find(r=>r.id===p.id);if(!document.querySelector('.pinbox')?.textContent.includes(source.geometryRequirements.neededEvidence))throw Error('Missing requirements '+p.id);count++;}return count;
  },rows);check(requirements===55,'55 explicit limitations');
  phase='bone-cards';const boneChecks=[];
  for(const b of [...new Set(rows.map(p=>p.b))]){
   await page.evaluate(b=>{__atlas.activatePin(null);__atlas.goTo(b);},b);await card();
   const row=rows.find(p=>p.b===b&&p.p);const chip=page.locator('#sheet [data-pinid="'+row.id+'"]');check(await chip.count()===1,'Single original chip');await chip.click();await card();
   check(await page.evaluate(()=>__atlas.state.pin)===row.id,'Original pin selected');boneChecks.push(b);
  }
  phase='new-cards';let edges=0;
  for(const p of rows.filter(p=>!p.id.startsWith('neck_'))){
   for(const b of p.bones){
    await page.evaluate(b=>{__atlas.activatePin(null);__atlas.goTo(b);},b);await card();
    const chip=page.locator('#sheet [data-pinid="'+p.id+'"]');check(await chip.count()===1,'Canonical card '+p.id);await chip.click();await card();
    check(await page.evaluate(()=>__atlas.state.pin)===p.id,'New pin selected');check(await page.locator('.pin[data-pinid="'+p.id+'"]').count()===0,'No invented marker');
    if(p.bones.length>1){const other=p.bones.find(x=>x!==b);await page.locator('.pinbox [data-gobone="'+other+'"]').click();check(await page.evaluate(()=>__atlas.state.pin)===p.id,'Pin retained across bones');edges++;}
   }
  }
  phase='search';await close();await page.locator('#bList').click();await page.locator('#q').fill('A02.2.01.008');
  check(await page.locator('#dlist [data-pinjump^="shared_neck_"]').count()===10,'Ten unique shared results');
  await page.locator('#dlist [data-pinjump="shared_neck_intervertebral_c2_c3_right"]').click();await card();
  phase='isolation';await page.locator('#bIso').click();check(JSON.stringify((await page.evaluate(()=>__neckCheck.snapshot().visible)).sort())===JSON.stringify(['axis','cervical_3']),'Both boundary contributors isolated');
  await card();await page.locator('#bBoneXray').click();check((await page.evaluate(()=>__neckCheck.snapshot().xray)).length===2,'Both contributors transparent');
  await card();await page.locator('#bBoneXray').click();await card();await page.locator('#bIso').click();
  phase='canvas';await page.evaluate(()=>{__atlas.activatePin(null);__atlas.goTo('atlas');});await card();await page.locator('#bIso').click();await close();await page.waitForTimeout(800);
  const target=await page.evaluate(()=>__neckCheck.clickPoint('atlas'));check(target,'Visible canvas point for atlas');await page.mouse.click(target.x,target.y);
  check(await page.evaluate(()=>__atlas.state.sel)==='atlas','Real canvas ray selection');await close();
  phase='bvh';await page.waitForTimeout(800);const ray=await page.evaluate(()=>__neckCheck.compare(__neckCheck.clickPoint('atlas')));check(ray.bvh>0,'BVH present');check(ray.rays.some(r=>r.hits>0),'Nonempty ray coverage');
  check(await page.evaluate(()=>__neckCheck.snapshot().cut)===false,'Skull-only clipping inactive in neck');
  phase='screenshot';check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');check(errors.length===0,'Console errors');await card();
  const nonce=await page.evaluate(()=>crypto.randomUUID());const screenshot=shot+'-'+nonce+'.png';await page.screenshot({path:screenshot});
  return {status:'passed',width,theme,typeChecks,boneChecks,requirements,newCards:17,sharedEdges:edges,searchResults:10,ray,errors,screenshot,anatomicalAcceptance:false,clipping:'Not supported for neck; existing skull implementation unchanged'};
 }catch(e){return {status:'failed',phase,width,theme,error:String(e),errors};}
 finally{page.off('pageerror',onError);page.off('console',onConsole);await page.unroute('**/local.html*');await page.unroute('https://fonts.googleapis.com/**');}
}
if(process.argv[2]==='--mcp'){
 const run=await createEvidenceRun(root,'stage5-neck-mcp'),width=Number(process.argv[3]||1280),theme=process.argv[4]||'dark';
 const fixture='async(page)=>('+browser.toString()+')(page,'+JSON.stringify({width,theme,shot:path.join(run.dir,'neck'),probe})+')';
 const file=await run.write('scenario.js',fixture);console.log(JSON.stringify({fixture:file,run:run.dir}));
}else await data();
