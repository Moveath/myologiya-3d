// Real UI actions and renderer state: group visibility, palettes, supplemental bones.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site'),out=path.join(root,'shots/navigation');
await fs.mkdir(out,{recursive:true});
const probe=`window.__navSnapshot=()=>({models:Object.keys(models),bones:[...structs.values()].filter(s=>s.kind==='b').map(s=>({id:s.id,v:visState(s),color:s.meshes[0].userData.mat.color.getHexString()})),context:[...structs.values()].filter(s=>s.kind==='c').flatMap(s=>s.meshes.map(m=>({name:(()=>{let n=m;while(n&&!n.name.startsWith('c|'))n=n.parent;return n?.name;})(),visible:m.visible}))),meshes:[...structs.values()].flatMap(s=>s.meshes.map(m=>({id:s.id,kind:s.kind,v:visState(s),visible:m.visible}))) });\n`;
const server=http.createServer(async(req,res)=>{
 const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
 if(!file.startsWith(site+path.sep))return res.writeHead(403).end();
 try{let data=await fs.readFile(file);if(file.endsWith('local.html'))data=Buffer.from(data.toString().replace('window.__atlas =',probe+'window.__atlas ='));res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(data);}catch{res.writeHead(404).end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report=[];
try{
 for(const width of [390,1280])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:width===390?844:900},colorScheme:theme,reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(90000);const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  await page.goto(`http://127.0.0.1:${server.address().port}/local.html`);await page.waitForFunction(()=>window.__ready);
  assert.deepEqual(await page.evaluate(()=>__navSnapshot().models),[]);
  for(const sec of ['trunk','neck','head','arm','leg']){
   assert.equal(await page.evaluate(s=>__atlas.enterSection(s),sec),true);
   await page.locator('[data-peel="3"]').click();
   const before=await page.evaluate(()=>__navSnapshot().bones);
   assert.ok(before.every(b=>b.color!=='e9dfc5'));
   await page.locator('#bBoneColors').click();
   assert.equal(await page.evaluate(()=>__atlas.state.boneColors),false);
   assert.ok((await page.evaluate(()=>__navSnapshot().bones)).every(b=>b.color==='e9dfc5'));
   await page.locator('#bBoneColors').click();
   assert.equal(await page.evaluate(()=>__atlas.state.boneColors),true);
   await page.locator('#bBoneLegend').click();
   assert.equal(await page.locator('[data-color-bone]').count(),before.length);
   await page.locator('#bCloseBoneLegend').click();
  }
  await page.evaluate(()=>__atlas.enterSection('trunk'));
  await page.waitForFunction(()=>!document.querySelector('#subScrollBar').hidden);
  await page.locator('#subScroll').focus();await page.keyboard.press('End');
  await page.waitForFunction(()=>{const e=document.querySelector('#subs');return e.scrollLeft>=e.scrollWidth-e.clientWidth-2;});
  await page.locator('[data-sub="deepback"]').click();
  assert.equal(await page.evaluate(()=>__atlas.state.subs.trunk),'deepback');
  await page.evaluate(()=>__atlas.setSub('spine'));
  await page.locator('#bContext').click();
  let snap=await page.evaluate(()=>__navSnapshot());
  assert.equal(snap.bones.filter(b=>b.v===2).length,12);
  assert.equal(snap.meshes.filter(m=>m.visible&&m.kind==='c').length,0);
  assert.equal(snap.meshes.filter(m=>m.v===1).length,0);
  assert.equal(await page.evaluate(()=>__atlas.state.isolate),null);
  await page.screenshot({path:path.join(out,`${width}-${theme}-spine.png`)});
  await page.locator('#bContext').click();
  assert.ok((await page.evaluate(()=>__navSnapshot())).meshes.some(m=>m.visible&&m.kind==='c'));
  await page.evaluate(()=>__atlas.setSub('sternum'));
  await page.locator('#bContext').click();
  assert.deepEqual((await page.evaluate(()=>__navSnapshot().bones.filter(b=>b.v===2).map(b=>b.id))),['sternum']);
  await page.locator('#bContext').click();
  for(const sec of ['arm','leg']){
   await page.evaluate(s=>__atlas.enterSection(s),sec);
   const owners=await page.evaluate(s=>Object.entries(ATLAS.contextBoneSources).filter(([,v])=>v.sec===s),sec);
   for(const [id,source] of owners){
    await page.evaluate(b=>__atlas.goTo(b),id);
    assert.equal(await page.evaluate(()=>__atlas.state.sel),id);
    const snapshot=await page.evaluate(()=>__navSnapshot());
    assert.ok(snapshot.bones.some(b=>b.id===id&&b.v===2));
    assert.ok(!snapshot.context.some(c=>c.name==='c|'+source.sourceId),'Old context duplicate removed');
    assert.equal(await page.evaluate(b=>ATLAS.pins.filter(p=>p.b===b&&p.p).length,id),0);
    assert.ok(!(await page.locator('#sheet').innerText()).includes('undefined'));
   }
  }
  await page.evaluate(()=>{__atlas.select(null);__atlas.setSub('lumbar');});
  await page.locator('#bContext').click();
  assert.deepEqual((await page.evaluate(()=>__navSnapshot().bones.filter(b=>b.v===2).map(b=>b.id))).sort(),['lumbar_1','lumbar_2','lumbar_3','lumbar_4','lumbar_5']);
  await page.screenshot({path:path.join(out,`${width}-${theme}-lumbar.png`)});
  await page.locator('#bHeadDetail').click();await page.locator('[data-list-type="bones"]').click();
  const listIds=await page.locator('#dlist [data-id]').evaluateAll(xs=>xs.map(x=>x.dataset.id));
  assert.ok(await page.evaluate(ids=>ids.every(id=>!!ATLAS.bones[id]),listIds));
  await page.locator('#q').fill('копчик');
  await page.locator('#dlist [data-pinjump="coc_os_coccygis"]').click();
  assert.equal(await page.evaluate(()=>__atlas.state.pin),'coc_os_coccygis');
  await page.locator('#bHeadDetail').click();await page.locator('#q').fill('');
  await page.locator('[data-list-type="muscles"]').click();
  const muscleIds=await page.locator('#dlist [data-id]').evaluateAll(xs=>xs.map(x=>x.dataset.id));
  assert.ok(muscleIds.length>0&&await page.evaluate(ids=>ids.every(id=>!!ATLAS.muscles[id]),muscleIds));
  await page.screenshot({path:path.join(out,`${width}-${theme}-groups.png`)});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  assert.deepEqual(errors,[]);
  report.push({width,theme,sections:5,bonesAdded:9,groupVisibility:true,scrollKeyboard:true,filters:true,errors,status:'passed'});
  console.log(JSON.stringify(report.at(-1)));await context.close();
 }
}finally{await browser.close();server.close();await fs.writeFile(path.join(root,'verify/navigation-ui.json'),JSON.stringify(report,null,2)+'\n');}
