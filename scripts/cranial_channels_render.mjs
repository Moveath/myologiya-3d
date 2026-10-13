// Focused validation of the real Halle channel dataset; no production UI edits.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {chromium} from '../tools/node_modules/playwright/index.mjs';
const root=process.cwd(),out=path.join(root,'build_head/cranial_channels/ui');await fs.mkdir(out,{recursive:true});
const server=http.createServer(async(req,res)=>{const p=path.resolve(root,'site','.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));try{if(!p.startsWith(path.join(root,'site')+path.sep))throw Error('path');res.setHeader('Content-Type',p.endsWith('.html')?'text/html; charset=utf-8':p.endsWith('.js')?'text/javascript':p.endsWith('.json')?'application/json':'application/octet-stream');res.end(await fs.readFile(p));}catch{res.writeHead(404).end();}});await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={generated_at:new Date().toISOString(),cases:[],anatomicalProof:false};
try{
for(const width of [390,1280])for(const theme of ['light','dark']){
 const page=await browser.newPage({viewport:{width,height:width===390?844:860},colorScheme:theme});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.route('https://cdn.jsdelivr.net/npm/**',r=>r.fulfill({path:path.join(root,'tools/node_modules',r.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 await page.goto(`http://127.0.0.1:${server.address().port}/skull-detail.html?mode=cranial_channels&part=halle_hypoglossal&theme=${theme}`);
 await page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:180000});assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
 assert.equal(await page.evaluate(()=>window.__detail.state.selected),'halle_hypoglossal');assert.equal(await page.locator('#channelDataset').inputValue(),'cranial_channels');
 assert.equal(await page.evaluate(()=>window.__detail.counts().visible),1);assert.ok((await page.locator('#selection').innerText()).includes('A02.1.04.016'));
 assert.ok(await page.locator('#selection a[href]').count()>=2);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.screenshot({path:path.join(out,`${width}-${theme}-intracranial.png`),timeout:120000});
 await page.evaluate(()=>window.__detail.frame({d:[-12,0,7],up:[0,1,0]},'halle_hypoglossal'));await page.screenshot({path:path.join(out,`${width}-${theme}-extracranial.png`),timeout:120000});
 await page.locator('#scanPanel').scrollIntoViewIfNeeded();await page.waitForFunction(()=>document.querySelector('#scanPanel canvas')?.dataset.loaded==='true');
 await page.screenshot({path:path.join(out,`${width}-${theme}-ct.png`),timeout:120000});
 await page.locator('#channelContext').check();assert.equal(await page.evaluate(()=>window.__detail.counts().visible),2);await page.evaluate(()=>window.__detail.frame('inf'));
 await page.screenshot({path:path.join(out,`${width}-${theme}-context.png`),timeout:120000});
 assert.deepEqual(errors,[]);report.cases.push({width,theme,status:'passed',errors});await page.close();console.log(width,theme,'passed');
}
report.status='passed';
}catch(e){report.status='failed';report.error=String(e);throw e;}finally{await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2));await browser.close();server.close();}
