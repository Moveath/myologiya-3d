// Targeted regressions for study navigation and the direction of section presets.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const site=path.join(root,'site'),shots=path.join(root,'shots/head-study');
await fs.mkdir(shots,{recursive:true});
const server=http.createServer(async(req,res)=>{
  const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
  try{res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':file.endsWith('.json')?'application/json':file.endsWith('.webp')?'image/webp':'application/octet-stream');res.end(await fs.readFile(file));}
  catch{res.writeHead(404).end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const base=`http://127.0.0.1:${server.address().port}`;
const report={created_at:new Date().toISOString(),status:'running',scope:'Navigation and clipping regressions; not anatomical certification',cases:[]};
let browser;
try{
  browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const ctx=await browser.newContext({viewport:{width:1280,height:860},colorScheme:'light'});
  await ctx.route('https://cdn.jsdelivr.net/npm/**',r=>r.fulfill({path:path.join(root,'tools/node_modules',r.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
  await ctx.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const ready=()=>page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:120000});
  const atlasReady=()=>page.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden,{},{timeout:120000});

  // Both success and failure may arrive after the catalogue DOM has been removed.
  for(const status of [200,503]){
    let release,requested,finished;
    const gate=new Promise(r=>release=r),requestStarted=new Promise(r=>requested=r),requestDone=new Promise(r=>finished=r);
    const handler=async route=>{requested();await gate;await route.fulfill({status,body:status===200?'[]':'unavailable',contentType:'application/json'});finished();};
    await page.route('**/skull-study-variants.json',handler);
    await page.goto(`${base}/skull-study.html?entry=local&theme=light`);
    await page.locator('[data-group="variants"]').click();await requestStarted;
    await page.locator('#back').click();await page.locator('[data-group="muscles"]').click();
    release();await requestDone;await page.waitForTimeout(150);
    assert.equal(await page.locator('[data-sub]').count(),2);
    assert.equal(await page.locator('#variants').count(),0);
    assert.deepEqual(errors,[]);
    await page.unroute('**/skull-study-variants.json',handler);
    report.cases.push({name:`delayed_variant_response_${status}_after_muscles`,status:'passed'});
  }

  // Inspect both section presets, then return through the actual links.
  await page.goto(`${base}/skull-study.html?entry=local&theme=light`);
  for(const region of ['base','face']){
    await page.locator(`[data-group="${region}"]`).click();await ready();
    assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
    assert.equal(new URL(page.url()).searchParams.get('entry'),'local');
    await page.locator('[data-preset="section"]').click();
    assert.equal(await page.evaluate(()=>window.__detail.state.reverse),false);
    await page.waitForTimeout(250);
    await page.screenshot({path:path.join(shots,`${region}-section-fixed.png`)});
    await page.locator('.back').click();await page.locator('[data-group="muscles"]').waitFor();
    assert.equal(new URL(page.url()).searchParams.get('entry'),'local');
    report.cases.push({name:`${region}_medial_section_and_local_return`,status:'passed',screenshot:`shots/head-study/${region}-section-fixed.png`});
  }
  await page.locator('[data-group="muscles"]').click();
  await page.locator('[data-sub="mastication"]').click();await atlasReady();
  assert.ok(new URL(page.url()).pathname.endsWith('/local.html'));
  await page.waitForFunction(()=>window.__atlas.state.subs.head==='mastication');
  report.cases.push({name:'standalone_local_study_detail_study_muscles',status:'passed'});

  // A saved "points off" preference must not defeat "show this variant".
  await page.evaluate(()=>{window.__atlas.state.pinsOn=false;window.__atlas.select('frontal');});
  assert.equal(await page.locator('.pin').count(),0);
  await page.locator('#bHeadDetail').click();const child=page.frameLocator('#headDetailFrame');
  await child.locator('[data-group="variants"]').click();
  const button=child.locator('[data-pin]').first();await button.waitFor();const id=await button.getAttribute('data-pin');await button.click();
  await page.waitForFunction(id=>!document.querySelector('#headDetailDialog').open&&window.__atlas.state.pin===id&&window.__atlas.state.pinsOn,id);
  await page.locator('.pin.on').waitFor({state:'visible'});await page.locator('.pinlabel').waitFor({state:'visible'});
  assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('myo3d')).pins),true);
  await page.screenshot({path:path.join(shots,'variant-from-pins-off.png')});
  report.cases.push({name:'variant_navigation_reenables_and_shows_marker',status:'passed',id,screenshot:'shots/head-study/variant-from-pins-off.png'});
  assert.deepEqual(errors,[]);report.page_errors=errors;report.status='passed';
  console.log(JSON.stringify(report,null,2));
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{await fs.writeFile(path.join(root,'verify/ui-skull-study-navigation-report.json'),JSON.stringify(report,null,2)+'\n');if(browser)await browser.close();server.close();}
