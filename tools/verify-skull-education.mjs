import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),shots=path.join(root,'shots/skull-education');
await fs.mkdir(shots,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(site,'skull-education.json'),'utf8'));
const server=http.createServer(async(req,res)=>{const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}try{res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'application/octet-stream');res.end(await fs.readFile(file));}catch{res.writeHead(404).end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created:new Date().toISOString(),cases:[],coverage:data.counts};
try{
 for(const width of (process.argv.includes('--failures-only')?[]:[390,1280]))for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:width===390?844:860},colorScheme:theme,reducedMotion:'reduce'});await context.route(/^https:\/\//,r=>r.abort());
  const page=await context.newPage(),errors=[];page.setDefaultTimeout(120000);page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(`${base}/skull-education.html?entry=local&theme=${theme}&category=muscles`);await page.waitForFunction(()=>window.__education);
  assert.equal(await page.locator('[data-entry]').count(),19);
  const downloads=[];page.on('request',r=>downloads.push(r.url()));
  const muscle=data.entries.find(r=>r.category==='muscles');await page.evaluate(id=>window.__education.select(id),muscle.id);
  assert.equal(await page.locator('canvas').count(),0);assert.equal(await page.locator('[data-atlas-view]').count(),1);
  await page.screenshot({path:path.join(shots,`${width}-${theme}-muscle.png`)});
  const variant=data.entries.find(r=>r.category==='variants');await page.evaluate(id=>window.__education.select(id),variant.id);
  assert.equal(await page.locator('[data-atlas-view]').count(),1);assert.ok(!downloads.some(url=>/\.glb|three\.module|skull-education-model/.test(url)));
  await page.screenshot({path:path.join(shots,`${width}-${theme}-variant.png`)});
  assert.ok(data.entries.every(r=>r.models.length===0));
  const bone=data.entries.find(r=>r.category==='bones'&&r.id.startsWith('sphenoid:'));await page.evaluate(id=>window.__education.select(id),bone.id);await page.locator('[data-atlas-view]').click();await page.waitForFunction(()=>window.__atlas?.state.sec==='head'&&window.__atlas.state.pin);assert.equal(await page.evaluate(()=>__atlas.state.sel),'sphenoid');assert.equal(await page.evaluate(()=>__atlas.state.pin),new URL(bone.atlasView.href,base).searchParams.get('value'));await page.goBack();await page.waitForFunction(()=>window.__education);
  await page.locator('#category').selectOption('attachments');assert.equal(await page.locator('[data-entry]').count(),78);
  const inherited=data.entries.find(r=>r.attachment?.origin.evidenceAppliesTo==='parent_muscle'||r.attachment?.insertion.evidenceAppliesTo==='parent_muscle');await page.evaluate(id=>window.__education.select(id),inherited.id);assert.ok(await page.locator('.relations .badge').count()>0);assert.equal(await page.locator('canvas').count(),0);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(shots,`${width}-${theme}-attachment.png`)});
  await page.locator('#search').fill('НЕСУЩЕСТВУЮЩАЯ СТРУКТУРА');assert.equal(await page.locator('[data-entry]').count(),0);await page.locator('#search').fill('');
  await page.evaluate(()=>window.__education.select('muscle:transversus_menti'));assert.equal(await page.locator('canvas').count(),0);assert.ok((await page.locator('#card').innerText()).includes('не подтвержден'));
  const source=data.entries.find(r=>r.category==='ossicles');await page.evaluate(id=>window.__education.select(id),source.id);await page.locator('#card a[href*="skull-detail"]').click();await page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error);assert.equal(await page.evaluate(()=>__detail.state.error),null);await page.locator('.back').click();await page.waitForFunction(()=>window.__education);assert.equal(await page.evaluate(()=>window.__education.selected.id),source.id);assert.ok(page.url().includes('entry=local'));assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
  await page.goto(`${base}/local.html?theme=${theme}#head`);await page.waitForFunction(()=>window.__ready);await page.evaluate(async()=>{await window.__atlas.enterSection('head');window.__atlas.goTo('auricularis_anterior_right');});
  if(width===390)await page.locator('#bMore').click();await page.locator('[data-detail-mode="education"][data-detail-part="muscle:auricularis_anterior_right"]').click();const frame=page.frameLocator('#headDetailFrame');await frame.locator('#card h2').waitFor();assert.ok((await frame.locator('#card h2').innerText()).includes('Передняя ушная'));await frame.locator('[data-atlas-view]').click();assert.equal(await page.locator('#headDetailDialog').evaluate(e=>e.open),false);assert.equal(await page.evaluate(()=>window.__atlas.state.sel),'auricularis_anterior_right');
  assert.deepEqual(errors,[]);report.cases.push({width,theme,passed:true,sourceReturn:true,embeddedReturn:true,atlasNavigation:true,noStandaloneModels:true});await context.close();
 }
 const context=await browser.newContext(),page=await context.newPage();let calls=0;await page.route('**/skull-education.json',r=>calls++===0?r.abort():r.continue());await page.goto(`${base}/skull-education.html`);await page.locator('#retryData').waitFor({state:'visible'});await page.locator('#retryData').click();await page.waitForFunction(()=>window.__education);assert.equal(calls,2);await context.close();
 const noGL=await browser.newContext();await noGL.addInitScript(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...args){return /webgl/i.test(kind)?null:original.call(this,kind,...args);};});const noGLPage=await noGL.newPage();await noGLPage.goto(`${base}/skull-education.html?id=muscle:auricularis_anterior_right`);await noGLPage.waitForFunction(()=>window.__education);assert.ok((await noGLPage.locator('#card').innerText()).includes('Что известно'));assert.equal(await noGLPage.locator('canvas').count(),0);await noGL.close();
 const noModule=await browser.newContext(),noModulePage=await noModule.newPage();await noModulePage.route('**/skull-education.js',r=>r.abort());await noModulePage.goto(`${base}/skull-education.html`);await noModulePage.locator('#retryData').waitFor({state:'visible'});assert.ok((await noModulePage.locator('#loading').innerText()).includes('Не удалось загрузить программу'));await noModule.close();
 report.dataRetry=true;report.noStandaloneModels=true;report.noWebGLTextFallback=true;report.moduleFailureNotice=true;report.status='passed';
}catch(e){report.status='failed';report.error=String(e.stack||e);throw e;}finally{await fs.writeFile(path.join(root,process.argv.includes('--failures-only')?'verify/ui-skull-education-failures-report.json':'verify/ui-skull-education-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
console.log(JSON.stringify(report));
