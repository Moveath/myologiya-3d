import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),out=path.join(root,'shots/mobile');
await fs.mkdir(out,{recursive:true});
const probe=`window.__mobileQA=()=>({ratio:renderer.getPixelRatio(),camera:camera.position.toArray(),target:controls.target.toArray(),free:freeArea,inset,models:Object.keys(models),toneMapping:renderer.toneMapping,triangles:renderer.info.render.triangles,tween:!!tween});\n`;
const server=http.createServer(async(req,res)=>{const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(site+path.sep))return res.writeHead(403).end();try{let data=await fs.readFile(file);if(file.endsWith('local.html'))data=Buffer.from(data.toString().replace('window.__atlas =',probe+'window.__atlas ='));res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(data);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report=[];
try{
 for(const width of [360,390,1280])for(const theme of ['light','dark']){
  const mobile=width<900,context=await browser.newContext({viewport:{width,height:mobile?780:900},deviceScaleFactor:mobile?3:1,isMobile:mobile,hasTouch:mobile,colorScheme:theme,reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(90000);const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.goto(`http://127.0.0.1:${server.address().port}/local.html`);await page.waitForFunction(()=>window.__ready);
  if(width===360&&theme==='light'){
   const check=await page.evaluate(async()=>{
    const {AtlasOrbitControls}=await import('./atlas-controls.js'),{OrbitControls}=await import('./vendor/three/examples/jsm/controls/OrbitControls.js'),{PerspectiveCamera}=await import('./vendor/three/build/three.module.js');
    const run=C=>{const canvas=document.createElement('canvas'),camera=new PerspectiveCamera();camera.position.z=1;const control=new C(camera,canvas),mouse={pointerId:11,pointerType:'mouse',pageX:40,pageY:40},touch={pointerId:12,pointerType:'touch',pageX:80,pageY:80};let error=null;try{control._addPointer(mouse);control._addPointer(touch);control._onTouchStart(touch);control._onPointerUp(touch);}catch(e){error=e.message;}finally{control.dispose();}return error;};
    return {upstream:run(OrbitControls),adapter:run(AtlasOrbitControls)};
   });assert.ok(check.upstream?.includes('x'));assert.equal(check.adapter,null);
  }
  await page.evaluate(()=>__atlas.enterSection('head'));await page.waitForTimeout(700);
  if(mobile){
   assert.equal(await page.locator('#sheet').isVisible(),false);assert.equal(await page.locator('#displayControls').isVisible(),false);
   const q=await page.evaluate(()=>__mobileQA());assert.ok(q.free.h>780*.65);assert.equal(q.ratio,3);
   await page.screenshot({path:path.join(out,`${width}-${theme}-model.png`)});
   await page.locator('#mobileCard').click();assert.equal(await page.locator('#sheet').isVisible(),true);
   await page.screenshot({path:path.join(out,`${width}-${theme}-description.png`)});
   await page.locator('#closeMobileCard').click();assert.equal(await page.locator('#sheet').isVisible(),false);
   assert.deepEqual((await page.evaluate(()=>__mobileQA())).camera,q.camera);
   await page.locator('#bOptions').click();assert.equal(await page.locator('#displayControls').isVisible(),true);
  }
  await page.locator('[data-peel="3"]').click();
  await page.locator('#bBoneColors').click();assert.equal(await page.evaluate(()=>__atlas.state.boneColors),false);
  await page.locator('#renderQualityChoice').selectOption('detail');
  if(mobile){await page.screenshot({path:path.join(out,`${width}-${theme}-options.png`)});await page.locator('#closeOptions').click();}
  await page.waitForTimeout(500);assert.equal(await page.evaluate(()=>__mobileQA().ratio),mobile?3:1);
  await page.screenshot({path:path.join(out,`${width}-${theme}-bone.png`)});
  if(mobile){
   await page.locator('#mobileSub').selectOption('neurocranium');
   assert.equal(await page.evaluate(()=>__atlas.state.subs.head),'neurocranium');
   await page.locator('#bOptions').click();await page.locator('#bHeadCut').click();
   await page.locator('#headCutAxis').selectOption('x');
   await page.locator('#headCutPosition').fill('40');
   await page.locator('#closeOptions').click();
   assert.equal(await page.evaluate(()=>__atlas.state.headCut.active),true);
   await page.locator('#bList').click();await page.locator('#q').fill('лобная кость');await page.locator('#dlist [data-id="frontal"]').first().click();
   assert.equal(await page.locator('#sheet').isVisible(),true);assert.equal(await page.evaluate(()=>__atlas.state.sel),'frontal');
   await page.waitForTimeout(700);const before=await page.evaluate(()=>__mobileQA());
   await page.locator('#closeMobileCard').click();assert.equal(await page.evaluate(()=>__atlas.state.sel),'frontal');
   assert.deepEqual((await page.evaluate(()=>__mobileQA())).camera,before.camera);
   await page.locator('#mobileCard').click();await page.keyboard.press('Escape');assert.equal(await page.locator('#sheet').isVisible(),false);
   await page.locator('#bOptions').click();await page.locator('#renderQualityChoice').selectOption('battery');await page.locator('#closeOptions').click();
   await page.waitForTimeout(300);assert.equal(await page.evaluate(()=>__mobileQA().ratio),1.5);
   await page.locator('#bOptions').click();await page.locator('#renderQualityChoice').selectOption('auto');await page.locator('#bQuiz').click();
   assert.equal(await page.evaluate(()=>__atlas.state.mode),'quiz');assert.equal(await page.locator('#sheet').isVisible(),true);
   await page.locator('#closeMobileCard').click();await page.locator('#mobileCard').click();assert.equal(await page.locator('#sheet').isVisible(),true);
   await page.locator('#closeMobileCard').click();
   await page.evaluate(()=>__atlas.enterSection('trunk'));assert.equal(await page.locator('#sheet').isVisible(),false);
   await page.locator('#mobileSub').selectOption('spine');await page.locator('#bOptions').click();await page.locator('[data-peel="3"]').click();
   await page.locator('#bContext').click();await page.locator('#closeOptions').click();
   await page.locator('#mobileFit').click();await page.waitForTimeout(700);await page.screenshot({path:path.join(out,`${width}-${theme}-thorax.png`)});
   for(const [section,id] of [['neck','atlas'],['arm','humerus'],['leg','lumbar_1']]){
    await page.evaluate(s=>__atlas.enterSection(s),section);assert.equal(await page.locator('#sheet').isVisible(),false);
    await page.locator('#bOptions').click();const old=await page.evaluate(()=>__atlas.state.boneColors);
    await page.locator('#bBoneColors').click();assert.equal(await page.evaluate(()=>__atlas.state.boneColors),!old);
    await page.locator('#closeOptions').click();await page.evaluate(b=>__atlas.goTo(b),id);
    assert.equal(await page.locator('#sheet').isVisible(),true);await page.locator('#bIso').click();assert.equal(await page.locator('#sheet').isVisible(),false);
    assert.equal(await page.evaluate(()=>__atlas.state.isolate),id);await page.locator('#mobileFit').click();assert.equal(await page.evaluate(()=>__atlas.state.isolate),null);
   }
   await page.setViewportSize({width:780,height:360});await page.waitForTimeout(400);
   await page.locator('#bOptions').click();await page.locator('#renderQualityChoice').selectOption('detail');await page.locator('#closeOptions').click();
   await page.locator('#mobileCard').click();await page.locator('#closeMobileCard').click();
   await page.screenshot({path:path.join(out,`${width}-${theme}-landscape.png`)});
   await page.setViewportSize({width:1280,height:900});await page.waitForTimeout(400);
   assert.equal(await page.locator('#sheet').isVisible(),true);assert.equal(await page.locator('#displayControls').isVisible(),true);
   assert.equal(await page.locator('#bQuiz').evaluate(e=>e.parentElement.className),'bar');
  }
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);assert.deepEqual(errors,[]);
  report.push({width,theme,status:'passed',mobilePanels:mobile,errors});console.log(JSON.stringify(report.at(-1)));await context.close();
 }
}finally{await browser.close();server.close();await fs.writeFile(path.join(root,'verify/mobile-layout.json'),JSON.stringify(report,null,2)+'\n');}
