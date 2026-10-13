import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),shots=path.join(root,'shots/head-catalogues');
await fs.mkdir(shots,{recursive:true});
const whole=JSON.parse(await fs.readFile(path.join(site,'skull-whole.json'),'utf8'));
const server=http.createServer(async(req,res)=>{
 const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
 if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
 try{res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(await fs.readFile(file));}catch{res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created_at:new Date().toISOString(),status:'running',cases:[]};
try{
 for(const width of [390,1280])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:width===390?844:860},colorScheme:theme,reducedMotion:'reduce'});
  await context.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  let wholeModelRequests=0;
  await page.route('**/skull-z-detail.glb',route=>wholeModelRequests++===0?route.abort('failed'):route.continue());
  await page.goto(`${base}/skull-study.html?entry=local&theme=${theme}`);await page.locator('#whole').click();
  await page.waitForFunction(()=>document.querySelectorAll('[data-whole-code]').length===89);
  await page.locator('#wholeFuture').check();assert.equal(await page.locator('[data-whole-code]').count(),97);
  await page.locator('#wholeFuture').uncheck();await page.screenshot({path:path.join(shots,`${width}-${theme}-whole.png`)});
  const norms=whole.rows.filter(r=>r.requirementType==='view'&&r.launch);assert.equal(norms.length,5);
  for(const [normIndex,row] of norms.entries()){
   await page.locator('#wholeSearch').fill(row.c);await page.locator(`[data-whole-view="${row.c}"]`).click();
   if(normIndex===0){
    await page.waitForFunction(()=>window.__detail?.state.error&&!window.__detail.state.loading);
    assert.equal(wholeModelRequests,1);assert.equal(await page.evaluate(()=>window.__detail.state.ready),false);
    await page.locator('#retry').click();
   }
   await page.waitForFunction(()=>window.__detail?.state.ready);
   await page.waitForFunction(code=>document.querySelector('#selection').textContent.includes(code),row.c);
   assert.ok(page.url().includes('entry=local'));assert.ok(page.url().includes('theme='+theme));
   if(row.launch.parts)assert.deepEqual((await page.evaluate(()=>window.__detail.visibleIds())).sort(),row.launch.parts.slice().sort());
   assert.equal(await page.locator('#view').inputValue(),row.launch.view);
   await page.locator('#reset').click();assert.ok((await page.locator('#selection').innerText()).includes(row.ru));
   if(row.launch.view==='inf')await page.screenshot({path:path.join(shots,`${width}-${theme}-inferior.png`)});
   await page.locator('.back').click();await page.waitForSelector('#wholeSearch');assert.equal(await page.locator('#wholeSearch').inputValue(),row.c);
  }
  await page.locator('#back').click();await page.locator('[data-group="muscles"]').click();await page.locator('#attachments').click();
  await page.waitForFunction(()=>document.querySelectorAll('[data-attachment-id]').length===78);
  await page.locator('#attachmentSearch').fill('A04.1.03.011');
  assert.ok(await page.locator('[data-attachment-id]').count()>0);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(shots,`${width}-${theme}-attachments.png`)});
  await page.locator('#attachmentSearch').fill('');await page.locator('[data-muscle-card="orbicularis_oculi_right:deep"]').click();
  await page.waitForFunction(()=>window.__atlas?.state.sel==='orbicularis_oculi_right'&&window.__atlas.state.selPart==='deep');
  assert.ok(page.url().includes('local.html'));assert.equal(await page.locator('[data-field="n"][data-scope="whole_muscle"]').count(),1);
  assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
  assert.equal(await page.locator('[data-field="s"][data-scope="whole_muscle"]').count(),1);
  assert.equal(await page.locator('.field-sources').count(),5);
  await page.evaluate(()=>window.__atlas.goTo('transversus_menti'));
  if(width===390&&await page.locator('#sheet').getAttribute('data-state')==='peek')await page.locator('#sheet .togglemore').first().click();
  assert.ok((await page.locator('[data-field="a"]').innerText()).toLocaleLowerCase('ru').includes('не подтверждено'));
  assert.ok((await page.locator('[data-field="s"]').innerText()).toLocaleLowerCase('ru').includes('не подтверждено'));
  assert.deepEqual(errors,[]);report.cases.push({width,theme,status:'passed',whole:97,current:89,views:norms.length,attachmentRecords:78,wholeLaunchRestoredAfterRetry:true});await context.close();
 }
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{await fs.writeFile(path.join(root,'verify/ui-skull-catalogues-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
console.log(JSON.stringify(report));
