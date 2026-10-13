// Mobile panel interactions are covered by verify-mobile-layout.mjs and the USB device check.
// Neck integration: real source structures, lazy loading, navigation and responsive cards.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const site=path.join(root,'site'), out=path.join(root,'shots/neck');
await fs.mkdir(out,{recursive:true});
const server=http.createServer(async(req,res)=>{
  const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
  try{res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(await fs.readFile(file));}
  catch{res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report=[];
try{
  for(const width of [1280]) for(const theme of ['light','dark']){
    const context=await browser.newContext({viewport:{width,height:width===390?844:900},colorScheme:theme,reducedMotion:'reduce',deviceScaleFactor:1});
    const page=await context.newPage();page.setDefaultTimeout(120000);
    const errors=[],assets=[];
    page.on('pageerror',e=>errors.push(String(e)));
    page.on('request',r=>{if(/-glb\.txt/.test(r.url()))assets.push(r.url());});
    await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
    await page.goto(origin+'/local.html',{waitUntil:'domcontentloaded',timeout:120000});
    await page.waitForFunction(()=>window.__ready===true);
    assert.equal(assets.length,0,'Home must not preload models');
    await page.locator('.seccard[data-sec="neck"]').click();
    await page.waitForFunction(()=>window.__atlas.state.sec==='neck'&&document.querySelector('#veil').hidden);
    const counts=await page.evaluate(()=>({
      muscles:Object.values(ATLAS.muscles).filter(m=>m.g.startsWith('neck_')).length,
      bones:Object.values(ATLAS.bones).filter(b=>b.g.startsWith('neck_')).length,
      terms:ATLAS.pins.filter(p=>p.id.startsWith('neck_')).length,
      located:ATLAS.pins.filter(p=>p.id.startsWith('neck_')&&p.p).length,
    }));
    assert.equal(counts.muscles,62);assert.equal(counts.bones,8);assert.ok(counts.terms>80);assert.ok(counts.located>0);
    assert.equal(assets.filter(u=>!u.includes('/neck-')).length,0,'Only requested section loads');
    await page.screenshot({path:path.join(out,`${width}-${theme}-overview.png`)});
    for(const sub of ['cervical','superficial','hyoid','deep','posterior','girdle']){
      await page.evaluate(s=>window.__atlas.setSub(s),sub);
      assert.equal(await page.locator(`[data-sub="${sub}"]`).getAttribute('aria-pressed'),'true');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    }
    await page.evaluate(()=>window.__atlas.setSub('cervical'));
    await page.locator('[data-peel="3"]').click();
    await page.screenshot({path:path.join(out,`${width}-${theme}-bones.png`)});
    await page.locator('#bBoneLegend').click();
    assert.equal(await page.locator('[data-color-bone]').count(),8);
    await page.locator('[data-color-bone="atlas"]').click();
    assert.equal(await page.evaluate(()=>window.__atlas.state.sel),'atlas');
    if(await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent()==='Подробнее')await page.locator('#bMore').click();
    await page.locator('#bIso').click();
    const pin=await page.evaluate(()=>ATLAS.pins.find(p=>p.b==='atlas'&&p.p)?.id);
    assert.ok(pin);
    await page.evaluate(id=>window.__atlas.activatePin(id,true),pin);
    assert.ok(await page.locator('.pinbox').isVisible());
    assert.ok(!(await page.locator('#sheet').textContent()).includes('undefined'));
    await page.locator('#bBoneXray').click();
    assert.equal(await page.evaluate(()=>window.__atlas.state.xrayBone),'atlas');
    await page.screenshot({path:path.join(out,`${width}-${theme}-atlas.png`)});
    for(const [id,part] of [['digastric_right','anterior'],['digastric_left','posterior'],['longus_colli_right','superior_oblique'],['longus_colli_left','inferior_oblique'],['neck_trapezius_right','descending']]){
      await page.evaluate(([id,part])=>window.__atlas.goTo(id,part),[id,part]);
      assert.equal(await page.evaluate(()=>window.__atlas.state.selPart),part);
      assert.ok(!(await page.locator('#sheet').textContent()).includes('undefined'));
      assert.equal(await page.locator('[data-field="o"] .field-sources').count(),1);
    }
    await page.evaluate(()=>window.__atlas.goTo('sternocleidomastoid_left'));
    await page.screenshot({path:path.join(out,`${width}-${theme}-muscle.png`)});
    await page.locator('#bList').click();
    await page.locator('#q').fill('longus colli');
    assert.equal(await page.locator('#dlist [data-id="longus_colli_right"]').count()>0,true);
    await page.locator('#bCloseList').click();
    await page.evaluate(()=>window.__atlas.setSub('all'));
    await page.locator('[data-peel="0"]').click();
    await page.locator('#bQuiz').click();
    assert.equal(await page.locator('[data-scope="cervical"]').count(),0,'No bone-only muscle quiz');
    for(const scope of ['superficial','hyoid','deep','posterior','girdle']){
      await page.locator(`[data-scope="${scope}"]`).click();
      assert.ok(await page.evaluate(()=>window.__atlas.state.quiz.options.length>=2));
    }
    await page.screenshot({path:path.join(out,`${width}-${theme}-quiz.png`)});
    assert.equal(await page.locator('#bBoneColors').getAttribute('aria-pressed'),'false');
    await page.locator('#bQuiz').click();
    for(const sec of ['head','arm','leg','neck']){
      assert.equal(await page.evaluate(s=>window.__atlas.enterSection(s),sec),true);
      assert.equal(await page.locator('#bBoneColors').isVisible(),true);
    }
    assert.deepEqual(errors,[]);
    report.push({width,theme,...counts,status:'passed'});
    await context.close();
  }
}finally{await browser.close();server.close();}
await fs.writeFile(path.join(root,'verify/ui-neck-report.json'),JSON.stringify({status:'passed',cases:report,limitation:'Desktop headless Chromium/SwiftShader; not a physical-phone performance measurement.'},null,2)+'\n');
console.log(JSON.stringify(report));
