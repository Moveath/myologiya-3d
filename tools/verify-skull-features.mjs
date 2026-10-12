// Independent local regression: published variant examples and native landmarks.
// This checks navigation/rendering/source disclosure, not anatomical correctness.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const site=path.join(root,'site'),shots=path.join(root,'shots/head-features');
await fs.mkdir(shots,{recursive:true});
const read=async name=>JSON.parse(await fs.readFile(path.join(site,name),'utf8'));
const [native,catalogue,examples,variants]=await Promise.all([
  read('skull-native-features.json'),read('skull-feature-catalogue.json'),
  read('skull-variant-examples.json'),read('skull-study-variants.json')]);
assert.equal(variants.length,14);
assert.equal(examples.examples.length,12);
assert.equal(new Set(examples.examples.map(row=>row.image)).size,12);
const markerRows=Object.entries(native.markers).flatMap(([mode,rows])=>rows.map(marker=>({...marker,mode})));
assert.equal(new Set(markerRows.map(marker=>marker.id)).size,markerRows.length,'Native ids must be globally unique');
for(const marker of markerRows){
  assert.ok(marker.refs.length>=2,`${marker.id}: two anatomical references required`);
  assert.ok(marker.refs.every(ref=>ref.locator&&ref.url),`${marker.id}: source locators required`);
  assert.ok(catalogue.features.some(feature=>feature.c===marker.c&&feature.views.some(view=>view.id===marker.id)),`${marker.id}: catalogue entry required`);
}
for(const example of examples.examples){
  await fs.access(path.join(site,example.image));
  assert.ok(example.license?.url&&example.author&&example.locator&&example.anatomyRefs?.length>=2,`${example.id}: attribution and references required`);
}

const server=http.createServer(async(req,res)=>{
  const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
  try{
    const ext=path.extname(file),types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.jpg':'image/jpeg','.png':'image/png'};
    res.setHeader('Content-Type',types[ext]||'application/octet-stream');
    res.end(await fs.readFile(file));
  }catch{res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created_at:new Date().toISOString(),status:'running',command:'node tools/verify-skull-features.mjs',native_markers:markerRows.length,catalogue_terms:catalogue.features.length,cases:[],limitations:['UI/source-display checks do not establish anatomical completeness.','Screenshots render actual source models; software WebGL timing does not measure real mobile performance.']};
const ready=page=>page.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:180000});
try{
 for(const width of [390,1280])for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width,height:width===390?844:860},deviceScaleFactor:1,colorScheme:theme,reducedMotion:'reduce'});
  await context.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
  await context.route('https://fonts.googleapis.com/**',route=>route.fulfill({body:'',contentType:'text/css'}));
  const page=await context.newPage(),errors=[],assetErrors=[],markersTested=[],saved=[];
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('response',response=>{if(response.url().startsWith(base)&&response.status()>=400&&!response.url().endsWith('/favicon.ico'))assetErrors.push(`${response.status()} ${response.url()}`);});
  const shot=async name=>{const file=`${width}-${theme}-${name}.png`;await page.screenshot({path:path.join(shots,file),timeout:120000});saved.push(file);};
  const noOverflow=async label=>assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${width}/${theme}: horizontal overflow in ${label}`);
  await page.goto(`${base}/skull-study.html?theme=${theme}&entry=local`);
  await page.locator('[data-group="variants"]').click();
  await page.locator('#variants .variant').first().waitFor();
  assert.equal(await page.locator('#variants .variant').count(),14);
  assert.equal(await page.locator('#variants .example img').count(),14);
  const loadedImages=[];
  for(let i=0;i<14;i++){
    const article=page.locator('#variants .variant').nth(i),img=article.locator('.example img');
    await img.scrollIntoViewIfNeeded();
    try{await img.evaluate(image=>image.decode());}
    catch(error){throw new Error(`Variant ${i+1}, ${await img.getAttribute('src')}: image decoding failed`,{cause:error});}
    const result=await img.evaluate(image=>({src:image.getAttribute('src'),width:image.naturalWidth,height:image.naturalHeight}));
    assert.ok(result.width>0&&result.height>0,`Variant image ${i} must be decoded`);loadedImages.push(result.src);
    const links=await article.locator('a').evaluateAll(nodes=>nodes.map(node=>node.href));
    const example=examples.examples.find(item=>item.image===result.src);
    assert.ok(links.includes(example.url)&&links.includes(example.license.url),`Variant ${i}: publication and license links must be shown`);
    for(const ref of example.anatomyRefs)assert.ok(links.includes(ref.url),`Variant ${i}: missing source ${ref.title}`);
    await noOverflow(`variant ${i}`);
    if(i===0||i===7||i===13)await shot(`variant-${i+1}`);
  }
  assert.equal(new Set(loadedImages).size,12);
  assert.ok((await page.locator('#subpage').innerText()).includes('не подтверждают наличие варианта'));
  await page.locator('#back').click();
  await page.locator('#features').click();
  await page.locator('#featureSearch').waitFor();
  await page.waitForFunction(()=>document.querySelectorAll('#featureResults > .variant').length>0);
  assert.equal(await page.locator('#featureResults > .variant').count(),catalogue.features.length);
  await noOverflow('feature catalogue');
  await shot('catalogue');
  for(const code of [...new Set(markerRows.map(marker=>marker.c))]){
    await page.locator('#featureSearch').fill(code);
    const expected=catalogue.features.filter(row=>row.c.includes(code));
    assert.equal(await page.locator('#featureResults > .variant').count(),expected.length,`Code search ${code}`);
    const expectedLinks=expected.reduce((count,row)=>count+row.views.length,0);
    assert.equal(await page.locator('[data-native-marker]').count(),expectedLinks,`Native links for ${code}`);
  }
  await page.locator('#featureSearch').fill('нет-такого-термина');
  assert.equal(await page.locator('#featureResults > .variant').count(),0);
  assert.ok((await page.locator('#featureResults').innerText()).includes('не доказательство отсутствия'));
  const first=markerRows[0];
  await page.locator('#featureSearch').fill(first.c);
  const link=page.locator(`[data-native-marker="${first.id}"]`);
  const target=new URL(await link.getAttribute('href'),base);
  assert.equal(target.searchParams.get('entry'),'local');
  assert.equal(target.searchParams.get('theme'),theme);
  assert.equal(target.searchParams.get('mode'),first.mode);
  await link.click();await ready(page);
  assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
  assert.equal(await page.evaluate(()=>window.__detail.state.marker),first.id);
  await page.locator('.back').click();
  await page.locator('#featureSearch').waitFor();
  await page.waitForFunction(code=>document.querySelector('#featureSearch')?.value===code,first.c);
  assert.equal(await page.locator('#featureSearch').inputValue(),first.c,'Return from a native view must restore its catalogue code');
  const restoredURL=new URL(page.url());
  assert.equal(restoredURL.searchParams.get('entry'),'local');
  assert.equal(restoredURL.searchParams.get('theme'),theme);
  await page.locator(`[data-native-marker="${first.id}"]`).click();await ready(page);
  // Every native marker is exercised in every viewport and theme, including
  // the detailed cavity surfaces and the independently scanned specimens.
  for(const [mode,markers] of Object.entries(native.markers)){
    if(!markers.length)continue;
    if(await page.evaluate(()=>window.__detail.state.mode)!==mode){await page.evaluate(mode=>window.__detail.setMode(mode),mode);await ready(page);}
    assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
    for(let i=0;i<markers.length;i++){
      const marker=markers[i];
      assert.equal(await page.evaluate(id=>window.__detail.selectMarker(id),marker.id),true,`${marker.id}: selection must succeed`);
      try{await page.waitForFunction(()=>!document.querySelector('#detailPin').hidden,{},{timeout:30000});}
      catch(error){await shot(`FAILED-${marker.id}`);throw new Error(`${width}/${theme}: native marker ${marker.id} is hidden after its saved view was applied`,{cause:error});}
      assert.equal(await page.evaluate(()=>window.__detail.state.marker),marker.id);
      assert.equal(await page.evaluate(()=>window.__detail.state.selected),marker.b);
      assert.equal(await page.evaluate(()=>window.__detail.state.only),marker.b);
      assert.equal(await page.evaluate(()=>window.__detail.counts().visible),1);
      assert.equal(await page.evaluate(()=>window.__detail.state.translucent),false,`${marker.id}: an isolated landmark must show its source surface opaquely`);
      if(typeof marker.view==='object'){
        assert.equal(await page.locator('#view').inputValue(),'marker',`${marker.id}: custom view must not retain an unrelated anatomical direction label`);
        assert.equal(await page.locator('#view option:checked').innerText(),'Ракурс ориентира');
      }
      assert.ok(await page.evaluate(()=>{
        const marker=document.querySelector('#markerSelection').getBoundingClientRect(),panel=document.querySelector('#panel').getBoundingClientRect();
        return marker.top>=panel.top&&marker.top<panel.bottom&&document.querySelector('#panel').scrollTop===0;
      }),`${marker.id}: the selected landmark card must start in the visible part of the panel`);
      const text=await page.locator('#markerSelection').innerText();
      for(const expected of [marker.ru,marker.lat,marker.c])assert.ok(text.includes(expected),`${marker.id}: card must include ${expected}`);
      const links=await page.locator('#markerSelection a').evaluateAll(nodes=>nodes.map(node=>node.href));
      for(const ref of marker.refs)assert.ok(links.includes(ref.url),`${marker.id}: anatomical source must be displayed`);
      assert.ok(await page.evaluate(()=>{
        const pin=document.querySelector('#detailPin').getBoundingClientRect(),stage=document.querySelector('#stage').getBoundingClientRect();
        return pin.width>0&&pin.height>0&&pin.left>=stage.left&&pin.right<=stage.right&&pin.top>=stage.top&&pin.bottom<=stage.bottom;
      }),`${marker.id}: visible marker must fit inside the actual canvas`);
      await noOverflow(marker.id);
      if(theme==='light'||i===0||i===markers.length-1)await shot(marker.id);
      markersTested.push({id:marker.id,mode,part:marker.b,pin_visible:true});
    }
  }
  assert.deepEqual(errors,[]);assert.deepEqual(assetErrors,[]);
  report.cases.push({width,theme,status:'passed',variant_cards:14,unique_loaded_images:12,catalogue_terms:catalogue.features.length,markers:markersTested,screenshots:saved,console_errors:errors,asset_errors:assetErrors});
  console.log(`${width} ${theme}: ${markersTested.length} native markers, 14 cards/12 examples passed`);
  await context.close();
 }
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{await fs.writeFile(path.join(root,'verify/ui-skull-features-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();server.close();}
