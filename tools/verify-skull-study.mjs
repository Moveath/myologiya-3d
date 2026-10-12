// Local, isolated browser checks and previews rendered from the actual meshes.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),shots=path.join(root,'shots/head-study');
await fs.mkdir(shots,{recursive:true});
const server=http.createServer(async(req,res)=>{const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}try{res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':file.endsWith('.json')?'application/json':file.endsWith('.webp')?'image/webp':'application/octet-stream');res.end(await fs.readFile(file));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created_at:new Date().toISOString(),status:'running',cases:[],scope:'UI and actual mesh preview rendering; not anatomical certification'};
const cases={whole:{all:22,brain:8,face:14},base:{inside:6,below:6,section:6},face:{front:16,nose:6,section:16},sinuses:{context:11,spaces:8},jaws:{all:3,mandible:1,maxilla:2},ear:{ossicles:3,labyrinth:2,nerves:3,context:13}};
async function setup(width,height,theme){const ctx=await browser.newContext({viewport:{width,height},deviceScaleFactor:1,colorScheme:theme});await ctx.route('https://cdn.jsdelivr.net/npm/**',r=>r.fulfill({path:path.join(root,'tools/node_modules',r.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));await ctx.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));return ctx;}
const ready=page=>page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:120000});
try{
 // The preview is a direct browser rendering, not a synthesized illustration.
 if(process.argv.includes('--previews')||process.argv.includes('--previews-only')){
  const ctx=await setup(560,380,'light'),p=await ctx.newPage();
  for(const id of [...Object.keys(cases),'variants']){
   await p.goto(`${base}/skull-detail.html?region=${id==='variants'?'whole':id}&theme=light`);await ready(p);assert.equal(await p.evaluate(()=>window.__detail.state.error),null);
   await p.addStyleTag({content:'.top,.modebar,.regionbar,.panel,.view-tools,.viewer-caption,.load{display:none!important}.layout{display:block;padding:0;height:100%}.viewer{height:100%;border-radius:0}'});
   await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>{window.__detail.frame();requestAnimationFrame(r);})));await p.locator('#stage').screenshot({path:path.join(shots,`preview-${id}.png`)});
  }
  await p.goto(`${base}/local.html#head`);await p.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden);await p.addStyleTag({content:'#app>:not(#stage){visibility:hidden!important}.tools{position:absolute!important;top:-6px!important;height:0!important;padding:0!important;overflow:hidden!important}#sheet{position:absolute!important;top:100%!important;height:0!important;min-height:0!important;padding:0!important;border:0!important}'});await p.evaluate(()=>{window.dispatchEvent(new Event('resize'));window.__atlas.state.peel=0;window.__atlas.setSub('mimetic');});await p.waitForTimeout(700);await p.addStyleTag({content:'#stage{transform:scale(2.6)}'});await p.screenshot({path:path.join(shots,'preview-muscles.png')});await ctx.close();
 }
 for(const width of (process.argv.includes('--previews-only')?[]:[390,1280]))for(const theme of ['light','dark']){
  const ctx=await setup(width,width===390?844:860,theme),page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(`${base}/skull-study.html?theme=${theme}`);await page.locator('[data-group="ear"]').waitFor();assert.equal(await page.locator('[data-group]').count(),8);
  await page.screenshot({path:path.join(shots,`groups-${width}-${theme}.png`),fullPage:true});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('[data-group="variants"]').click();await page.locator('.variant').first().waitFor();assert.equal(await page.locator('.variant').count(),14);assert.equal(await page.locator('.variant > details > .sources').count(),14);assert.equal(await page.locator('.variant .example').count(),14);assert.ok((await page.locator('#subpage').innerText()).includes('не подтверждено'));await page.locator('#back').click();
  await page.locator('[data-group="muscles"]').click();assert.equal(await page.locator('[data-sub]').count(),2);await page.locator('#back').click();
  for(const [group,presets] of Object.entries(cases)){
   await page.locator(`[data-group="${group}"]`).click();await ready(page);assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
   for(const [preset,count] of Object.entries(presets)){await page.locator(`[data-preset="${preset}"]`).click();assert.equal(await page.evaluate(()=>window.__detail.counts().visible),count,`${group}/${preset}`);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
   await page.locator('#reset').click();assert.equal(await page.evaluate(()=>window.__detail.counts().visible),Object.values(presets)[0]);await page.screenshot({path:path.join(shots,`${group}-${width}-${theme}.png`)});
   if(group==='ear'){assert.equal(await page.locator('#view option[value="ant"]').innerText(),'Осевой вид 1');assert.equal(await page.locator('#cutPlane option[value="axial"]').innerText(),'Плоскость 3');}
   await page.locator('.back').click();await page.locator('[data-group="ear"]').waitFor();
  }
  // Actual cross-frame muscle/variant navigation, including stale layer state.
  await page.goto(`${base}/local.html#head`);await page.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden);
  await page.evaluate(()=>{window.__atlas.state.peel=3;window.__atlas.select('frontal');});await page.locator('#bHeadDetail').click();
  let frame=page.frameLocator('#headDetailFrame');await frame.locator('[data-group="muscles"]').click();await frame.locator('[data-sub="mastication"]').click();await page.waitForFunction(()=>!document.querySelector('#headDetailDialog').open);assert.equal(await page.evaluate(()=>window.__atlas.state.subs.head),'mastication');assert.equal(await page.evaluate(()=>window.__atlas.state.peel),0);
  await page.locator('#bHeadDetail').click();frame=page.frameLocator('#headDetailFrame');await frame.locator('[data-group="variants"]').click();const id=await frame.locator('[data-pin]').first().getAttribute('data-pin');await frame.locator('[data-pin]').first().click();await page.waitForFunction(()=>!document.querySelector('#headDetailDialog').open);assert.equal(await page.evaluate(()=>window.__atlas.state.pin),id);
  assert.deepEqual(errors,[]);report.cases.push({width,theme,status:'passed',groups:8,presets:18,variants:14,embedded_muscle_and_variant_navigation:true});console.log(`${width} ${theme}: study groups passed`);await ctx.close();
 }
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}finally{if(!process.argv.includes('--previews-only'))await fs.writeFile(path.join(root,'verify/ui-skull-study-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
