import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),out=path.join(root,'shots/mobile-detail');
await fs.mkdir(out,{recursive:true});
const probe=`window.__detailQA=()=>({camera:camera.position.toArray(),target:controls.target.toArray()});\n`;
const server=http.createServer(async(req,res)=>{const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(site+path.sep))return res.writeHead(403).end();try{let data=await fs.readFile(file);if(file.endsWith('skull-detail.html'))data=Buffer.from(data.toString().replace('window.__detail={',probe+'window.__detail={'));res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(data);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report=[];
try{
 for(const width of [360,390])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:760},deviceScaleFactor:1,isMobile:true,hasTouch:true,colorScheme:theme});
  const page=await context.newPage(),errors=[];page.setDefaultTimeout(120000);page.on('pageerror',e=>errors.push(String(e)));
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const base=`http://127.0.0.1:${server.address().port}`;
  const ready=async()=>{await page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error);assert.equal(await page.evaluate(()=>__detail.state.error),null);await page.waitForTimeout(300);};
  await page.goto(`${base}/skull-detail.html?region=whole&theme=${theme}`);await ready();
  assert.equal(await page.locator('#panel').isVisible(),false);
  assert.ok((await page.locator('#stage').boundingBox()).height>760*.7);
  assert.equal(await page.locator('#detailChoice').inputValue(),'all');
  await page.screenshot({path:path.join(out,`${width}-${theme}-model.png`)});
  await page.locator('#detailChoice').selectOption('brain');assert.equal(await page.evaluate(()=>__detail.state.preset),'brain');
  await page.evaluate(()=>__detail.selectPart('frontal',true));await page.waitForTimeout(700);
  const camera=await page.evaluate(()=>__detailQA());
  await page.locator('#detailDock').click();assert.ok(await page.locator('#panel').isVisible());
  assert.equal(await page.locator('#panel').getAttribute('aria-modal'),'true');
  assert.equal(await page.locator('#detailClose').evaluate(e=>e===document.activeElement),true);
  await page.screenshot({path:path.join(out,`${width}-${theme}-panel.png`)});
  await page.locator('#modelDetails summary').click();await page.locator('#modelInfo').scrollIntoViewIfNeeded();
  assert.ok(await page.locator('#detailClose').isVisible());await page.locator('#detailClose').click();
  assert.equal(await page.locator('#panel').isVisible(),false);assert.equal(await page.evaluate(()=>__detail.state.selected),'frontal');
  assert.deepEqual(await page.evaluate(()=>__detailQA()),camera);
  await page.locator('#detailMenu').click();await page.keyboard.press('Escape');assert.equal(await page.locator('#panel').isVisible(),false);
  await page.locator('#detailDock').click();await page.locator('#onlyPart').click();assert.equal(await page.locator('#panel').isVisible(),false);assert.equal(await page.evaluate(()=>__detail.counts().visible),1);
  await page.locator('#detailMenu').click();await page.locator('#reset').click();assert.equal(await page.locator('#detailChoice').inputValue(),'all');
  await page.setViewportSize({width:780,height:360});assert.equal(await page.locator('#panel').isVisible(),false);assert.ok((await page.locator('#stage').boundingBox()).height>180);
  await page.setViewportSize({width:1280,height:860});await page.locator('.view-tools #view').waitFor();assert.ok(await page.locator('#panel').isVisible());assert.ok(await page.locator('.top #themeButton').isVisible());
  await page.setViewportSize({width,height:760});assert.equal(await page.locator('#panel').isVisible(),false);
  if(width===390){
   await page.goto(`${base}/skull-detail.html?mode=openear&theme=${theme}`);await ready();
   assert.equal(await page.locator('#panel').isVisible(),false);await page.locator('#detailDock').click();assert.ok(await page.locator('#earSwitches').isVisible());await page.locator('#detailClose').click();
   await page.locator('#detailChoice').selectOption('microct');await ready();assert.equal(await page.locator('#panel').isVisible(),false);
   await page.locator('#detailMenu').click();await page.locator('#cutPlane').selectOption('sagittal');assert.equal(await page.evaluate(()=>__detail.state.clip),'sagittal');await page.locator('#detailClose').click();
   await page.locator('#detailChoice').selectOption('channels');await ready();
   await page.locator('#detailDock').click();await page.locator('[data-channel]').first().click();await page.locator('#scanPanel canvas[data-loaded="true"]').waitFor();
   await page.locator('#scanPanel [data-expand]').click();assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('scan-expanded')),true);
   await page.locator('#detailClose').click();assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('scan-expanded')),false);assert.ok(await page.locator('#stage').isVisible());
  }
  if(width===390&&theme==='dark'){
   await page.goto(`${base}/local.html#head`);await page.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden);
   await page.locator('#bOptions').click();await page.locator('#bHeadDetail').click();
   const child=page.frameLocator('#headDetailFrame');await child.locator('[data-group="whole"]').click();await page.waitForFunction(()=>document.querySelector('#headDetailFrame').contentWindow.__detail?.state.ready);
   assert.equal(await child.locator('#panel').isVisible(),false);await child.locator('#detailDock').click();assert.ok(await child.locator('#panel').isVisible());
   await page.keyboard.press('Escape');assert.equal(await child.locator('#panel').isVisible(),false);assert.equal(await page.locator('#headDetailDialog').evaluate(e=>e.open),true);
   await child.locator('#detailMenu').click();await child.locator('#detailClose').click();await page.screenshot({path:path.join(out,'390-dark-embedded.png')});
   await page.locator('#closeHeadDetail').click();assert.equal(await page.locator('#headDetailDialog').evaluate(e=>e.open),false);
  }
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);assert.deepEqual(errors,[]);
  report.push({width,theme,status:'passed',selectionAndCameraPreserved:true,landscapeAndDesktop:true,sourceModes:width===390?['z','openear','microct','channels']:['z']});
  await context.close();
 }
}finally{await fs.writeFile(path.join(root,'verify/ui-skull-detail-mobile.json'),JSON.stringify(report,null,2)+'\n');await browser.close();await new Promise(r=>server.close(r));}
console.log(JSON.stringify(report));
