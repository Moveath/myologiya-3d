// Functional and visual regression checks with a clean, local-only browser profile.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, process.argv[2] || 'site');
const out = path.join(root, 'shots/head');
await fs.mkdir(out, {recursive:true});
const server = http.createServer(async (req,res) => {
  const file = path.resolve(site, '.' + decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if (!file.startsWith(site + path.sep)) {res.writeHead(403).end();return;}
  try {res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(await fs.readFile(file));}
  catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(8776,'127.0.0.1',resolve));
const browser = await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM || undefined,
  args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report = [];
try {
  for (const width of [390,1280]) for (const theme of ['light','dark']) {
    const context = await browser.newContext({viewport:{width,height:width===390?844:860},deviceScaleFactor:1,colorScheme:theme,reducedMotion:'reduce'});
    const page = await context.newPage();
    const errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    page.on('console',message=>{if(message.type()==='error'&&!message.text().includes('net::ERR_FAILED'))errors.push(message.text());});
    await page.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
    // Remove external font/network timing from layout regression screenshots.
    await page.route('https://fonts.googleapis.com/**',route=>route.fulfill({body:'',contentType:'text/css'}));
    await page.goto('http://127.0.0.1:8776/'+(process.argv[3]||'local.html'));
    await page.waitForFunction(()=>window.__ready===true);
    await page.screenshot({path:path.join(out,`${width}-${theme}-home.png`)});
    await page.locator('.seccard[data-sec="head"]').click();
    await page.waitForFunction(()=>document.querySelector('#secTitle').textContent==='Голова');
    await page.waitForFunction(()=>window.__atlas.state.sec==='head' && document.querySelector('#veil').hidden);
    await page.screenshot({path:path.join(out,`${width}-${theme}-muscles.png`)});
    await page.locator('[data-peel="3"]').click();
    await page.evaluate(()=>window.__atlas.goTo('frontal'));
    await page.waitForFunction(()=>document.querySelector('#sheet .name')?.textContent==='Лобная кость');
    if(await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent()==='Подробнее') await page.locator('#bMore').click();
    await page.locator('#bIso').click();
    await page.screenshot({path:path.join(out,`${width}-${theme}-bone.png`)});
    const pin = await page.evaluate(()=>ATLAS.pins.find(p=>p.b==='frontal'&&p.p)?.id);
    assert.ok(pin);
    await page.evaluate(id=>window.__atlas.activatePin(id,true),pin);
    await page.waitForFunction(id=>window.__atlas.state.pin===id,pin);
    assert.ok(await page.locator('.pinbox').isVisible());
    const noPoint = await page.evaluate(()=>ATLAS.pins.find(p=>p.b==='frontal'&&!p.p)?.id);
    if(noPoint){await page.evaluate(id=>window.__atlas.activatePin(id,true),noPoint);const details=await page.locator('.pinbox').innerText();assert.ok(details.toLowerCase().includes('без 3d-точки'),JSON.stringify({noPoint,details,errors}));}
    await page.evaluate(()=>window.__atlas.goTo('masseter_right'));
    await page.locator('[data-part="deep"]').click();
    assert.equal(await page.evaluate(()=>window.__atlas.state.selPart),'deep');
    await page.screenshot({path:path.join(out,`${width}-${theme}-parts.png`)});
    await page.evaluate(()=>window.__atlas.goTo('orbicularis_oculi_left','deep'));
    assert.ok(!(await page.locator('#sheet').textContent()).includes('undefined'));
    assert.ok((await page.locator('#sheet').textContent()).includes('не выделена отдельной геометрией'));
    await page.evaluate(()=>window.__atlas.goTo('auricularis_anterior_right'));
    assert.ok((await page.locator('#sheet').textContent()).includes('нет отдельной 3D-модели'));
    await page.locator('#bList').click();
    await page.locator('#q').fill('mandibula');
    assert.ok((await page.locator('#drawer').innerText()).includes('Нижняя челюсть'));
    await page.locator('#q').fill('нижняя челюсть');
    assert.ok((await page.locator('#drawer').innerText()).includes('mandibula'));
    await page.locator('#bCloseList').click();
    await page.locator('#bQuiz').click();
    assert.equal(await page.evaluate(()=>window.__atlas.state.mode),'quiz');
    assert.ok(await page.evaluate(()=>window.__atlas.state.quiz.options.length>=2));
    assert.equal(await page.locator('[data-scope="neurocranium"]').count(),0);
    await page.locator('[data-scope="mastication"]').click();
    assert.equal(await page.evaluate(()=>window.__atlas.state.quiz.scope),'mastication');
    assert.ok(await page.evaluate(()=>window.__atlas.state.quiz.options.length>=2));
    await page.screenshot({path:path.join(out,`${width}-${theme}-quiz.png`)});
    await page.locator('#bQuiz').click();
    const overflow = await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
    assert.equal(overflow,false,'Horizontal page overflow');
    for(const sec of ['arm','leg']){assert.equal(await page.evaluate(id=>window.__atlas.enterSection(id),sec),true);}
    assert.deepEqual(errors,[]);
    report.push({width,theme,errors,overflow,status:'passed'});
    await context.close();
    console.log('Passed',width,theme);
  }
  const fallbackContext=await browser.newContext({viewport:{width:1280,height:860}});
  const fallbackPage=await fallbackContext.newPage();
  const fallbackErrors=[];
  fallbackPage.on('pageerror',e=>fallbackErrors.push(String(e)));
  await fallbackPage.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
  await fallbackPage.route('https://fonts.googleapis.com/**',route=>route.fulfill({body:'',contentType:'text/css'}));
  await fallbackPage.route('**/head-glb.txt',route=>route.fulfill({status:503,body:'Test: use fallback'}));
  let fallbackFetched=false;
  fallbackPage.on('response',r=>{if(r.url().endsWith('/head-q-glb.txt')&&r.ok())fallbackFetched=true;});
  await fallbackPage.goto('http://127.0.0.1:8776/'+(process.argv[3]||'local.html'));
  await fallbackPage.waitForFunction(()=>window.__ready===true);
  assert.equal(await fallbackPage.evaluate(()=>window.__atlas.enterSection('head')),true);
  assert.ok(fallbackFetched);
  assert.deepEqual(fallbackErrors,[]);
  await fallbackContext.close();
  report.push({scenario:'Fallback GLB after primary model unavailable',status:'passed'});
  await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2));
} finally {await browser.close();server.close();}
