import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),shots=path.join(root,'shots/head-geometry');
await fs.mkdir(shots,{recursive:true});
const read=async file=>JSON.parse(await fs.readFile(path.join(site,file),'utf8'));
const data=await read('skull-geometry-review.json');assert.equal(data.rows.length,521);assert.equal(new Set(data.rows.map(r=>r.id)).size,521);
const z=await read('skull-z-detail.json'),ear=await read('skull-openear.json'),channels=await read('skull-temporal-channels.json'),cranial=await read('skull-cranial-channels.json');
const parts={main:new Set(data.rows.map(r=>r.bone)),z:new Set([...z.bones,...z.cavities].map(r=>r.id)),openear:new Set(ear.structures.map(r=>r.id)),channels:new Set(channels.structures.map(r=>r.id)),cranial_channels:new Set(cranial.structures.map(r=>r.id))};
parts.microct=new Set(['microct_surface']);
for(const row of data.rows)for(const assessment of row.assessments){
 const v=assessment.viewer;if(!v)continue;assert.ok(parts[v.mode]?.has(v.part),row.id+': unknown viewer part '+JSON.stringify(v));
 assert.ok(v.view?.d.length===3&&v.view.d.every(Number.isFinite),row.id);assert.ok(Math.hypot(...v.view.d)>0,row.id);
 if(v.cut)assert.ok(v.cut.value>=0&&v.cut.value<=1,row.id);
}
const server=http.createServer(async(req,res)=>{
 const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
 try{res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(await fs.readFile(file));}catch{res.writeHead(404).end();}
});await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created_at:new Date().toISOString(),status:'running',cases:[]};
try{
 for(const width of [390,1280])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:width===390?844:860},colorScheme:theme,reducedMotion:'reduce'});
  await context.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  let geometryModelFailures=0,otherModeFailures=0;
  await page.route('**/skull-z-detail.glb',route=>geometryModelFailures++===0?route.abort('failed'):route.continue());
  await page.route('**/skull-temporal-channels.glb',route=>otherModeFailures++===0?route.abort('failed'):route.continue());
  await page.goto(`${base}/skull-study.html?entry=local&theme=${theme}`);await page.locator('#geometry').click();
  await page.waitForFunction(()=>document.querySelectorAll('[data-geometry-id]').length===521);
  const row=data.rows.find(r=>r.bone==='mandible'&&r.c==='A02.1.15.031'),index=row.assessments.findIndex(a=>a.viewer?.mode==='z');assert.ok(index>=0);
  await page.locator('#geometrySearch').fill(row.c);await page.locator('#geometryBone').selectOption(row.bone);
  assert.equal(await page.locator('[data-geometry-id]').count(),1);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(shots,`${width}-${theme}-review.png`)});
  await page.locator(`[data-geometry-view="${row.id}:${index}"]`).click();
  await page.waitForFunction(()=>window.__detail?.state.error&&!window.__detail.state.loading);
  assert.equal(geometryModelFailures,1);assert.equal(await page.evaluate(()=>window.__detail.state.ready),false);
  await page.locator('#retry').click();await page.waitForFunction(()=>window.__detail?.state.ready);
  await page.waitForFunction(code=>document.querySelector('#selection').textContent.includes(code),row.c);
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),row.assessments[index].viewer.part);
  assert.equal(await page.locator('#view').inputValue(),'evidence');assert.equal(await page.evaluate(()=>window.__detail.state.cut),row.assessments[index].viewer.cut.value);
  await page.locator('#reset').click();assert.equal(await page.locator('#view').inputValue(),'evidence');
  await page.screenshot({path:path.join(shots,`${width}-${theme}-native-view.png`)});
  // A source-specific camera must not retain its evidence label on another bone.
  await page.evaluate(()=>window.__detail.selectPart('maxilla_right',true));
  assert.equal(await page.locator('#view option[value="evidence"]').count(),0);
  assert.equal(await page.locator('#view').inputValue(),'antlat');
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),'maxilla_right');
  await page.evaluate(()=>window.__detail.frame('evidence'));
  assert.equal(await page.locator('#view').inputValue(),'antlat');
  await page.locator('#reset').click();
  assert.equal(await page.locator('#view').inputValue(),'evidence');
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),row.assessments[index].viewer.part);
  // Changing the source clears the option; resetting that source must not revive it.
  await page.locator('[data-mode="channels"]').click();
  await page.waitForFunction(()=>window.__detail.state.mode==='channels'&&window.__detail.state.error&&!window.__detail.state.loading);
  assert.equal(otherModeFailures,1);
  await page.locator('#retry').click();
  await page.waitForFunction(()=>window.__detail.state.ready&&window.__detail.state.mode==='channels');
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),null);
  assert.equal(await page.locator('#view option[value="evidence"]').count(),0);
  assert.equal(await page.locator('#view').inputValue(),'antlat');
  await page.locator('#reset').click();
  assert.equal(await page.locator('#view option[value="evidence"]').count(),0);
  await page.locator('[data-mode="z"]').click();
  await page.waitForFunction(()=>window.__detail.state.ready&&window.__detail.state.mode==='z');
  assert.equal(await page.locator('#view option[value="evidence"]').count(),0);
  await page.locator('#reset').click();
  assert.equal(await page.locator('#view').inputValue(),'evidence');
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),row.assessments[index].viewer.part);
  assert.equal(await page.evaluate(()=>window.__detail.state.cut),row.assessments[index].viewer.cut.value);
  await page.locator('.back').click();await page.waitForSelector(`[data-geometry-id="${row.id}"]`);assert.equal(await page.locator('#geometrySearch').inputValue(),row.c);assert.equal(await page.locator('#geometryBone').inputValue(),row.bone);
  await page.locator(`[data-geometry-pin="${row.pinId}"]`).click();await page.waitForFunction(id=>window.__atlas?.state.pin===id,row.pinId);
  assert.equal(await page.evaluate(()=>window.__atlas.state.pinsOn),true);
  await page.locator('[data-detail-mode="geometry"]').click();const frame=page.frameLocator('#headDetailFrame');
  await frame.locator(`[data-geometry-id="${row.id}"]`).waitFor();assert.equal(await frame.locator('#geometryBone').inputValue(),row.bone);
  await page.locator('#closeHeadDetail').click();assert.equal(await page.evaluate(()=>window.__atlas.state.pin),row.pinId);
  assert.deepEqual(errors,[]);report.cases.push({width,theme,status:'passed',records:521,evidenceContext:{boneChange:true,sourceChange:true,resetRestores:true},retry:{geometryRestored:true,otherModePreserved:true}});await context.close();
 }
 // Direct links use the same retry restoration without a geometry/whole record.
 const native=await read('skull-native-features.json'),marker=native.markers.z[0];
 const retryContext=await browser.newContext({viewport:{width:1280,height:860},reducedMotion:'reduce'});
 await retryContext.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 report.nativeRetry=[];
 for(const target of [{marker:marker.id,part:marker.b},{part:'maxilla_left'}]){
  const page=await retryContext.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));let requests=0;
  await page.route('**/skull-z-detail.glb',route=>requests++===0?route.abort('failed'):route.continue());
  const query=new URLSearchParams({mode:'z',...(target.marker?{marker:target.marker}:{part:target.part})});
  await page.goto(`${base}/skull-detail.html?${query}`);
  await page.waitForFunction(()=>window.__detail?.state.error&&!window.__detail.state.loading);
  assert.equal(requests,1);await page.locator('#retry').click();
  await page.waitForFunction(()=>window.__detail.state.ready);
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),target.part);
  assert.equal(await page.evaluate(()=>window.__detail.state.marker),target.marker||null);
  assert.deepEqual(errors,[]);report.nativeRetry.push({target,status:'passed'});await page.close();
 }
 await retryContext.close();
 const sourceContext=await browser.newContext({viewport:{width:1280,height:860},reducedMotion:'reduce'});
 await sourceContext.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 const candidates=data.rows.flatMap(row=>row.assessments.map((assessment,index)=>({row,assessment,index}))).filter(x=>x.assessment.viewer);
 const targets=[...candidates.filter(x=>x.assessment.viewer.marker),...['microct','channels','cranial_channels'].map(mode=>candidates.find(x=>x.assessment.viewer.mode===mode))];
 report.sourceLaunches=[];
 for(const target of targets){
  assert.ok(target);const {row,assessment,index}=target,v=assessment.viewer,page=await sourceContext.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const query=new URLSearchParams({from:'geometry',bone:row.bone,code:row.c,assessment:String(index),entry:'local'});
  await page.goto(`${base}/skull-detail.html?${query}`);await page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error);
  assert.equal(await page.evaluate(()=>window.__detail.state.error),null);assert.equal(await page.evaluate(()=>window.__detail.state.mode),v.mode);
  await page.waitForFunction(code=>document.querySelector('#selection').textContent.includes(code),row.c);
  assert.equal(await page.evaluate(()=>window.__detail.state.selected),v.part);
  assert.equal(await page.locator('#view').inputValue(),'evidence');
  if(v.marker){assert.equal(await page.evaluate(()=>window.__detail.state.marker),v.marker);assert.equal(await page.locator('#detailPin').isVisible(),true);}
  await page.screenshot({path:path.join(shots,`source-${v.mode}-${row.c}.png`)});
  assert.deepEqual(errors,[]);report.sourceLaunches.push({id:row.id,mode:v.mode,marker:v.marker||null,status:'passed'});await page.close();
 }
 await sourceContext.close();
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{await fs.writeFile(path.join(root,'verify/ui-skull-geometry-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
console.log(JSON.stringify(report));
