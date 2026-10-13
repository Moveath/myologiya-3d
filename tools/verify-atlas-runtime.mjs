// Exercise the shipped application under actual network and graphics failures.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site');
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
 for(const file of ['local.html','skull-detail.html?mode=z&entry=local']){
  const context=await browser.newContext({viewport:{width:390,height:844}});
  await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
  const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(String(error)));
  await page.goto(base+'/'+file);await page.waitForFunction(()=>window.__ready===true);
  if(file.startsWith('local'))await page.evaluate(()=>window.__atlas.enterSection('head'));
  else await page.waitForFunction(()=>window.__detail.state.ready);
  assert.equal(await page.locator('#runtimeFailure').count(),0);assert.deepEqual(errors,[]);
  report.cases.push({file,test:'all_external_requests_blocked',status:'passed'});
  await page.evaluate(()=>{const gl=document.querySelector('#stage').getContext('webgl2');window.testLoss=gl.getExtension('WEBGL_lose_context');if(!window.testLoss)throw Error('Context-loss extension unavailable');window.testLoss.loseContext();});
  await page.waitForFunction(()=>window.__atlasRuntime.reason==='context');assert.ok(await page.locator('#runtimeFailure button').isVisible());
  await page.evaluate(()=>window.testLoss.restoreContext());await page.waitForFunction(()=>window.__atlasRuntime.reason===null);
  assert.equal(await page.locator('#runtimeFailure').count(),0);assert.deepEqual(errors,[]);
  report.cases.push({file,test:'webgl_context_loss_and_restore',status:'passed'});
  await context.close();
  const failed=await browser.newContext({viewport:{width:390,height:844}}),p=await failed.newPage();
  await p.route('**/vendor/three/build/three.module.js',route=>route.abort());
  await p.goto(base+'/'+file);await p.waitForFunction(()=>window.__atlasRuntime?.reason==='module');
  assert.ok(await p.locator('#runtimeFailure button').isVisible());assert.ok(await p.locator('#runtimeFailure a').isVisible());
  report.cases.push({file,test:'renderer_module_unavailable',status:'passed'});await failed.close();
  const unavailable=await browser.newContext({viewport:{width:390,height:844}}),q=await unavailable.newPage();
  await q.addInitScript(()=>{const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return /webgl/i.test(type)?null:get.call(this,type,...args);};});
  await q.goto(base+'/'+file);await q.waitForFunction(()=>window.__atlasRuntime?.reason==='webgl');
  assert.ok(await q.locator('#runtimeFailure button').isVisible());assert.ok(await q.locator('#runtimeFailure a').isVisible());
  report.cases.push({file,test:'webgl_unavailable',status:'passed'});await unavailable.close();
 }
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{await fs.writeFile(path.join(root,'verify/ui-atlas-runtime-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
console.log(JSON.stringify(report));
