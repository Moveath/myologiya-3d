// Independent read-only review of the root agent's new channel viewer.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from '../tools/node_modules/playwright/index.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),out=path.join(root,'build_head/muscle_completion');
const server=http.createServer(async(req,res)=>{const p=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!p.startsWith(site+path.sep)){res.writeHead(403).end();return;}try{res.setHeader('Content-Type',p.endsWith('.js')?'text/javascript':p.endsWith('.html')?'text/html; charset=utf-8':p.endsWith('.json')?'application/json':'application/octet-stream');res.end(await fs.readFile(p));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const base='http://127.0.0.1:'+server.address().port,report={cases:[],errors:[]};let browser;
try{
 browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 for(const width of [390,1280])for(const theme of ['light','dark']){
  const page=await browser.newPage({viewport:{width,height:860},colorScheme:theme});
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.goto(base+'/skull-detail.html?mode=channels&entry=local&from=study&theme='+theme);
  await page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:120000});
  const c={width,theme,loadError:await page.evaluate(()=>window.__detail.state.error)};
  await page.locator('[data-channel="facial_canal_wall"]').click();
  await page.waitForFunction(()=>document.querySelector('#scanPanel canvas').dataset.loaded==='true');
  c.initial=await page.evaluate(()=>({counts:window.__detail.counts(),canvasLoaded:document.querySelector('#scanPanel canvas').dataset.loaded,back:document.querySelector('.back').href,overflow:document.documentElement.scrollWidth>innerWidth}));
  await page.locator('#channelContext').check();
  await page.locator('#onlyPart').click();
  c.contextAfterIsolate=await page.evaluate(()=>({checked:document.querySelector('#channelContext').checked,only:window.__detail.state.only,visible:window.__detail.counts().visible,contextInHidden:window.__detail.state.hidden.has('temporal_context')}));
  await page.locator('[data-expand]').click();
  c.expanded=await page.evaluate(()=>({expanded:document.body.classList.contains('scan-expanded'),viewerDisplay:getComputedStyle(document.querySelector('.viewer')).display,panelHeight:document.querySelector('.panel').clientHeight,canvasWidth:document.querySelector('#scanPanel canvas').clientWidth}));
  await page.screenshot({path:path.join(out,`channel-ui-${width}-${theme}-expanded.png`)});
  await page.locator('[data-expand]').click();
  await page.evaluate(()=>window.__detail.reset());
  c.reset=await page.evaluate(()=>({expanded:document.body.classList.contains('scan-expanded'),scanHidden:document.querySelector('#scanPanel').hidden,selected:window.__detail.state.selected}));
  if(width===1280&&theme==='light'){
   await page.locator('[data-channel="facial_canal_wall"]').click();
   await page.waitForFunction(()=>document.querySelector('#scanPanel canvas').dataset.loaded==='true');
   const old=await page.locator('#scanPanel canvas').evaluate(c=>c.toDataURL());
   await page.route('**/skull-channel-carotid-slices-*.png',r=>r.abort());
   await page.evaluate(()=>window.__detail.selectPart('carotid_canal_wall',true));
   await page.waitForFunction(()=>document.querySelector('#scanPanel canvas').dataset.loaded==='false');
   c.failedNewSeries={oldCanvasRetained:old===await page.locator('#scanPanel canvas').evaluate(c=>c.toDataURL()),selection:await page.locator('#selection h2').innerText(),status:await page.locator('[data-status]').innerText()};
   await page.screenshot({path:path.join(out,'channel-ui-failed-other-series.png')});
  }
  report.cases.push(c);await page.close();
 }
}finally{if(browser)await browser.close();await new Promise(r=>server.close(r));await fs.writeFile(path.join(out,'channel-ui-review.json'),JSON.stringify(report,null,2));}
console.log(JSON.stringify(report));
