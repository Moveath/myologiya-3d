// Local UI checks for native wall geometry and actual source CT reslices.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),shots=path.join(root,'shots/head-channels');
await fs.mkdir(shots,{recursive:true});
const metadata=JSON.parse(await fs.readFile(path.join(site,'skull-temporal-channels.json'),'utf8'));
const slices=JSON.parse(await fs.readFile(path.join(site,metadata.slicesFile),'utf8'));
const cranialMetadata=JSON.parse(await fs.readFile(path.join(site,'skull-cranial-channels.json'),'utf8'));
const cranialSlices=JSON.parse(await fs.readFile(path.join(site,cranialMetadata.slicesFile),'utf8'));
const server=http.createServer(async(req,res)=>{
 const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
 if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
 try{res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript','.json':'application/json','.png':'image/png','.webp':'image/webp'})[path.extname(file)]||'application/octet-stream');res.end(await fs.readFile(file));}catch{res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created_at:new Date().toISOString(),status:'running',cases:[],scope:'Rendering, selection and CT navigation; not a claim of complete channel anatomy.'};
async function checkFrame(page,frame){
 const actual=await page.evaluate(()=>window.__detail.scanPlane());
 assert.equal(actual.visible,true);assert.equal(actual.frame,frame.index);assert.equal(actual.vertices.length,12);
 const dot=(a,b)=>a.reduce((n,x,i)=>n+x*b[i],0),norm=a=>Math.sqrt(dot(a,a));
 for(const axis of [frame.u,frame.v,frame.normal])assert.ok(Math.abs(norm(axis)-1)<1e-6);
 assert.ok(Math.abs(dot(frame.u,frame.v))<1e-6);assert.ok(Math.abs(dot(frame.u,frame.normal))<1e-6);assert.ok(Math.abs(dot(frame.v,frame.normal))<1e-6);
 const corners=Array.from({length:4},(_,i)=>actual.vertices.slice(i*3,i*3+3));
 const center=[0,1,2].map(i=>corners.reduce((n,p)=>n+p[i]/4,0));
 assert.ok(norm(center.map((x,i)=>x-frame.center_m[i]))<1e-7,'Displayed CT rectangle must use source center in metres');
 const axes=[[-1,-1],[1,-1],[1,1],[-1,1]];
 corners.forEach((point,index)=>{const offset=point.map((x,i)=>x-frame.center_m[i]);assert.ok(Math.abs(dot(offset,frame.normal))<1e-7,'Every corner must lie in the source plane');[frame.u,frame.v].forEach((axis,i)=>assert.ok(Math.abs(dot(offset,axis)-axes[index][i]*frame.field_mm/2000)<1e-7,'Source image orientation and field size must match the rectangle'));});
}
try{
 for(const width of [390,1280])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:width===390?844:860},deviceScaleFactor:1,colorScheme:theme});
  await context.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
  await context.route('https://fonts.googleapis.com/**',route=>route.fulfill({body:'',contentType:'text/css'}));
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(`${base}/skull-study.html?entry=local&theme=${theme}`);
  assert.equal(await page.locator('[data-group]').count(),8);
  await page.locator('#channels').click();
  assert.ok(page.url().includes('entry=local'));
  await page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,null,{timeout:180000});
  assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
  assert.equal(await page.evaluate(()=>window.__detail.counts().parts),3);
  for(const row of metadata.structures){
   await page.evaluate(id=>window.__detail.selectPart(id,true),row.id);
   await page.locator('#scanPanel').scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>document.querySelector('#scanPanel canvas').dataset.loaded==='true');
   const series=slices.series.find(s=>s.id===row.id),slider=page.locator('#scanPanel input[type=range]');
   assert.equal(await slider.getAttribute('max'),String(series.frames.length-1));
   for(const i of [0,Math.floor(series.frames.length/2),series.frames.length-1]){
    await slider.fill(String(i));await slider.dispatchEvent('input');
    await page.waitForFunction(index=>document.querySelector('#scanPanel canvas').dataset.frame===String(index),series.frames[i].index);
    await checkFrame(page,series.frames[i]);
   }
   await page.locator('#scanPanel [data-overlay]').check();
   await page.waitForFunction(()=>document.querySelector('#scanPanel [data-status]').textContent.includes('Красный'));
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.screenshot({path:path.join(shots,`${width}-${theme}-${row.id}.png`)});
   await page.locator('#scanPanel [data-overlay]').uncheck();
   await page.evaluate(()=>window.__detail.setCut('sagittal',.45));
   assert.equal(await page.locator('#scanPanel').isVisible(),true);
   await page.evaluate(()=>window.__detail.setCut('off'));
  }
  await page.evaluate(()=>window.__detail.selectPart('temporal_context'));
  assert.equal(await page.locator('#scanPanel').isVisible(),false);
  assert.equal(await page.evaluate(()=>window.__detail.scanPlane().visible),false);
  await page.evaluate(()=>window.__detail.selectPart('facial_canal_wall'));
  await page.locator('#channelContext').check();
  await page.locator('#onlyPart').click();
  assert.equal(await page.locator('#channelContext').isChecked(),false,'Hidden context must not retain a checked display toggle');
  if(width===390){
   await page.locator('#scanPanel [data-expand]').click();
   assert.equal(await page.locator('.viewer').isVisible(),false);
   assert.ok((await page.locator('#scanPanel h3').innerText()).includes('Лицевой'));
   await page.screenshot({path:path.join(shots,`${width}-${theme}-ct-expanded.png`)});
   await page.locator('#scanPanel [data-expand]').click();
  }
  if(width===1280&&theme==='light'){
   await page.route('**/skull-channel-carotid-*.png',route=>route.abort());
   await page.reload();await page.waitForFunction(()=>window.__detail?.state.ready);
   await page.evaluate(()=>window.__detail.selectPart('facial_canal_wall'));
   await page.waitForFunction(()=>document.querySelector('#scanPanel canvas').dataset.loaded==='true');
   await page.evaluate(()=>window.__detail.selectPart('carotid_canal_wall'));
   await page.waitForFunction(()=>document.querySelector('#scanPanel [data-status]').textContent.includes('не загрузился'));
   assert.ok(await page.locator('#scanPanel canvas').evaluate(canvas=>!canvas.dataset.frame&&canvas.dataset.loaded==='false'&&canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data.every(value=>value===0)),'Failed CT load must clear previous anatomy');
   assert.equal(await page.evaluate(()=>window.__detail.scanPlane().visible),false,'Failed CT load must clear the 3D frame');
   await page.unroute('**/skull-channel-carotid-*.png');
  }
  await page.evaluate(()=>window.__detail.setMode('cranial_channels'));
  await page.waitForFunction(()=>window.__detail.state.ready||window.__detail.state.error);
  assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
  assert.equal(await page.evaluate(()=>window.__detail.counts().parts),2);
  await page.evaluate(()=>window.__detail.selectPart('halle_hypoglossal',true));
  await page.waitForFunction(()=>document.querySelector('#scanPanel canvas').dataset.loaded==='true');
  const halleSeries=cranialSlices.series[0];
  for(const i of [0,Math.floor(halleSeries.frames.length/2),halleSeries.frames.length-1]){
   const slider=page.locator('#scanPanel input[type=range]');await slider.fill(String(i));await slider.dispatchEvent('input');
   await page.waitForFunction(index=>document.querySelector('#scanPanel canvas').dataset.frame===String(index),halleSeries.frames[i].index);
   await checkFrame(page,halleSeries.frames[i]);
  }
  assert.ok((await page.locator('#scanPanel [data-source]').innerText()).includes('0,125'));
  assert.equal(await page.locator('[data-part-view]').count(),2);
  await page.locator('[data-part-view="1"]').click();
  await page.screenshot({path:path.join(shots,`${width}-${theme}-halle-extracranial.png`)});
  await page.locator('[data-part-view="0"]').click();
  await page.locator('#scanPanel').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(shots,`${width}-${theme}-halle-ct.png`)});
  await page.evaluate(()=>window.__detail.setMode('z'));
  await page.waitForFunction(()=>window.__detail.state.ready);
  assert.equal(await page.evaluate(()=>window.__detail.counts().parts),30);
  assert.equal(await page.evaluate(()=>window.__detail.scanPlane().visible),false,'Changing the model must remove CT coordinates from the previous specimen');
  assert.deepEqual(errors,[]);report.cases.push({width,theme,status:'passed',structures:metadata.structures.length+cranialMetadata.structures.length,ct_frames:[...slices.series,...cranialSlices.series].reduce((n,s)=>n+s.frames.length,0)});
  await context.close();
 }
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{await fs.writeFile(path.join(root,'verify/ui-skull-channels-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
console.log(JSON.stringify(report));
