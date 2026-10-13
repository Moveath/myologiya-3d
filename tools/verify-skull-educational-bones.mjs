// Render all independent bone diagrams in the actual shared educational viewer.
// This is a visual/software check, never independent anatomical acceptance.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base=process.env.ATLAS_REVIEW_URL||'http://127.0.0.1:8811';
const bone=JSON.parse(await fs.readFile(path.join(root,'site/skull-educational-bones.json'),'utf8'));
const unified=JSON.parse(await fs.readFile(path.join(root,'site/skull-education.json'),'utf8'));
const out=path.join(root,'shots/skull-educational-bones');await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const cases=[],errors=[];
try{
for(const width of [1280,390])for(const theme of ['light','dark']){
 const page=await browser.newPage({viewport:{width,height:900},colorScheme:theme,deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(base+'/skull-education.html?category=variants&theme='+theme);
 await page.waitForFunction(()=>window.__education);
 for(const model of bone.models){
  const entry=unified.entries.find(r=>r.models?.some(m=>m.id===model.id));assert.ok(entry,model.id);
  await page.evaluate(id=>window.__education.select(id),entry.id);
  const index=entry.models.findIndex(m=>m.id===model.id);
  if(index)await page.selectOption('#modelChoice',String(index));
  await page.waitForFunction(({id,node})=>window.__education.selected.id===id&&window.__education.viewer?.ready&&window.__education.viewer.visibleNames().includes(node),{id:entry.id,node:model.nodeNames[0]},{timeout:30000});
  await page.locator('#viewport').scrollIntoViewIfNeeded();
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const nodes=await page.evaluate(()=>window.__education.viewer.visibleNames());
  assert.deepEqual([...nodes].sort(),[...model.nodeNames].sort(),model.id+': isolated diagram nodes');
  assert.equal(await page.locator('#labelLegend li').count(),model.labels.length);
  const visibleLabels=await page.locator('.modelLabel:not([hidden])').count();
  assert.equal(visibleLabels,model.labels.length,model.id+': labels must fit initial view');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),model.id+': overflow');
  const file=`${width}-${theme}-${model.id}.png`;
  await page.locator('#viewport').screenshot({path:path.join(out,file)});
  cases.push({width,theme,id:model.id,entry:entry.id,nodes:nodes.length,labels:visibleLabels,screenshot:'shots/skull-educational-bones/'+file});
 }
 await page.close();
}
assert.deepEqual(errors,[]);
await fs.writeFile(path.join(root,'verify/ui-skull-educational-bones-report.json'),JSON.stringify({status:'passed',models:bone.models.length,cases,errors,limitations:['Software browser render check; not physical mobile hardware or independent anatomical validation.']},null,2)+'\n');
console.log(JSON.stringify({models:bone.models.length,cases:cases.length,errors}));
}finally{await browser.close();}
