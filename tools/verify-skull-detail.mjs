// Local-only regression and screenshots for the independent skull model viewer.
// Run from the repository root: node tools/verify-skull-detail.mjs
// Optional: ATLAS_CHROMIUM points to an installed Chromium executable.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const site=path.join(root,'site'), output=path.join(root,'shots/head-detail');
const reportPath=path.join(root,'verify/ui-skull-detail-report.json');
await fs.mkdir(output,{recursive:true});
const server=http.createServer(async(request,response)=>{
  const filename=path.resolve(site,'.'+decodeURIComponent(new URL(request.url,'http://localhost').pathname));
  if(!filename.startsWith(site+path.sep)){response.writeHead(403).end();return;}
  try{
    response.setHeader('Content-Type',filename.endsWith('.html')?'text/html; charset=utf-8':filename.endsWith('.js')?'text/javascript':filename.endsWith('.json')?'application/json':'application/octet-stream');
    response.end(await fs.readFile(filename));
  }catch{response.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={generated_at:new Date().toISOString(),status:'running',test_command:'node tools/verify-skull-detail.mjs',cases:[],limitations:[
  'Проверка интерфейса и загрузки не подтверждает анатомическую точность геометрии.',
  'Время измерено на локальном сервере в headless Chromium с программным WebGL; это не скорость загрузки по интернету и не тест реального телефона.',
  'Латеральность микро-КТ независимо не подтверждена; боковые виды имеют нейтральные названия.'
]};
try{
  for(const width of [390,1280])for(const theme of ['light','dark']){
    const height=width===390?844:860;
    const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1,colorScheme:theme,reducedMotion:'reduce'});
    const page=await context.newPage(),errors=[],screenshots=[];
    page.on('pageerror',error=>errors.push(String(error)));
    await page.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
    await page.route('https://fonts.googleapis.com/**',route=>route.fulfill({body:'',contentType:'text/css'}));
    const shot=async(name)=>{screenshots.push(name);await page.screenshot({path:path.join(output,name),timeout:120000});};
    const ready=()=>page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:120000});
    await page.goto(`${base}/skull-detail.html?theme=${theme}`);
    assert.equal(await page.locator('.back').getAttribute('href'),'./#head');
    await ready();
    assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
    assert.deepEqual(await page.evaluate(()=>window.__detail.counts()),{parts:30,bones:22,cavities:8,visible:22});
    await shot(`detail-${width}-${theme}-bones.png`);
    await page.locator('#showCavities').check();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),30);
    assert.equal(await page.evaluate(()=>window.__detail.state.translucent),true);
    await shot(`detail-${width}-${theme}-cavities.png`);
    await page.evaluate(()=>window.__detail.setCut('sagittal',.5));
    await page.locator('#view').selectOption('right');
    await shot(`detail-${width}-${theme}-cut.png`);
    await page.evaluate(()=>window.__detail.selectPart('frontal_sinus',true));
    assert.ok((await page.locator('#selection').innerText()).includes('Лобная'));
    await page.locator('#onlyPart').click();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),1);
    await page.locator('#reset').click();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),22);
    await page.locator('#view').selectOption('inf');
    await shot(`detail-${width}-${theme}-inferior.png`);

    // The unavailable transfer must expose retry and remain recoverable.
    await page.route('**/skull-microct.glb',route=>route.abort());
    await page.locator('[data-mode="microct"]').click();
    await page.waitForFunction(()=>!!window.__detail.state.error);
    assert.ok(await page.locator('#retry').isVisible());
    await page.locator('[data-mode="z"]').click();
    await ready();
    assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
    await page.unroute('**/skull-microct.glb');

    const start=Date.now();
    await page.locator('[data-mode="microct"]').click();
    await ready();
    assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
    assert.equal(await page.evaluate(()=>window.__detail.state.mode),'microct');
    assert.equal(await page.locator('#view option[value="right"]').textContent(),'Боковой вид 1');
    assert.equal(await page.locator('#view option[value="left"]').textContent(),'Боковой вид 2');
    assert.equal(await page.locator('#cutPlane option[value="sagittal"]').textContent(),'Сагиттальная — боковой срез');
    await page.locator('#view').selectOption('ant');
    await shot(`microct-${width}-${theme}-front.png`);
    const microctLoadAndScreenshotMs=Date.now()-start;
    await page.evaluate(()=>window.__detail.setCut('sagittal',.5));
    await page.locator('#view').selectOption('right');
    await shot(`microct-${width}-${theme}-sagittal.png`);
    await page.evaluate(()=>window.__detail.setCut('coronal',.5,true));
    await page.locator('#view').selectOption('ant');
    await shot(`microct-${width}-${theme}-coronal.png`);
    await page.evaluate(()=>window.__detail.setCut('axial',.6));
    await page.locator('#view').selectOption('sup');
    await shot(`microct-${width}-${theme}-axial.png`);
    await page.locator('#reset').click();
    assert.equal(await page.evaluate(()=>window.__detail.state.clip),'off');
    await page.locator('[data-mode="z"]').click();
    await ready();
    assert.equal(await page.locator('#view option[value="right"]').textContent(),'Справа');
    assert.equal(await page.evaluate(()=>window.__detail.counts().bones),22);
    assert.deepEqual(errors,[]);
    report.cases.push({width,height,theme,status:'passed',z_bones:22,z_cavities:8,z_visibility_selection_isolation_reset:true,z_clipping:true,microct_load:true,microct_clipping:['sagittal','coronal','axial'],microct_reverse_cut:true,microct_neutral_lateral_labels:true,load_failure_recovery:true,microct_load_and_front_screenshot_ms:microctLoadAndScreenshotMs,page_errors:errors,screenshots});
    console.log(`${width} ${theme}: passed; micro-CT load + screenshot ${microctLoadAndScreenshotMs} ms`);
    await context.close();
  }
  // The local launcher's wrapper must survive the round trip through the detail page.
  const navigationContext=await browser.newContext({viewport:{width:390,height:844}});
  const navigationPage=await navigationContext.newPage();
  await navigationPage.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
  await navigationPage.route('https://fonts.googleapis.com/**',route=>route.fulfill({body:'',contentType:'text/css'}));
  await navigationPage.goto(`${base}/local.html#head`);
  await navigationPage.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden);
  await navigationPage.locator('#bHeadDetail').click();
  await navigationPage.waitForFunction(()=>!!window.__detail);
  assert.equal(await navigationPage.locator('.back').getAttribute('href'),'local.html#head');
  await navigationPage.locator('.back').click();
  await navigationPage.waitForURL(`${base}/local.html#head`);
  await navigationPage.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden);
  report.local_navigation_round_trip='passed';
  await navigationContext.close();
  report.status='passed';
}catch(error){report.status='failed';report.error=String(error?.stack||error);throw error;}
finally{
  await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n');
  await browser.close();server.close();
}
