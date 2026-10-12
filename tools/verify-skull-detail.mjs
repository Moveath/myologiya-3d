// Local-only regression for independent skull models and the embedded viewer.
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
  const zMetadata=JSON.parse(await fs.readFile(path.join(site,'skull-z-detail.json'),'utf8'));
  const earMetadata=JSON.parse(await fs.readFile(path.join(site,'skull-openear.json'),'utf8'));
  const testedMarkers=['mandible_mylohyoid_groove_right','mandible_mylohyoid_groove_left'];
  for(const id of testedMarkers)assert.ok(zMetadata.markers?.some(marker=>marker.id===id),`Missing reviewed Z marker ${id}`);
  assert.equal(earMetadata.structures.length,13,'OpenEar must expose all thirteen authored structures');
  const stapes=earMetadata.structures.find(part=>/stapes/i.test(part.id));
  const earContext=earMetadata.structures.find(part=>part.context);
  assert.ok(stapes,'OpenEar stapes metadata must be present');
  assert.ok(earContext,'OpenEar must identify the surrounding specimen as context');
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

    // These markers belong to the independent Z mesh. Their prescribed views
    // and clipping must expose the actual pin, not just change selected state.
    for(const id of testedMarkers){
      const marker=zMetadata.markers.find(marker=>marker.id===id);
      await page.evaluate(()=>window.__detail.selectPart('mandible',true));
      await page.locator(`[data-marker="${id}"]`).click();
      await page.waitForFunction(()=>!document.querySelector('#detailPin').hidden);
      assert.equal(await page.evaluate(()=>window.__detail.state.marker),id);
      assert.equal(await page.evaluate(()=>window.__detail.state.only),'mandible');
      assert.equal(await page.evaluate(()=>window.__detail.state.clip),marker.cut.plane);
      assert.equal(await page.evaluate(()=>window.__detail.state.reverse),marker.cut.reverse);
      assert.equal(await page.locator('#view').inputValue(),marker.view);
      assert.ok((await page.locator('#markerSelection').innerText()).includes('A02.1.15.031'));
      assert.ok(await page.locator('#markerSelection a').count()>=2);
      const contained=await page.evaluate(()=>{
        const pin=document.querySelector('#detailPin').getBoundingClientRect(),canvas=document.querySelector('#stage').getBoundingClientRect();
        return pin.width>0&&pin.height>0&&pin.left>=canvas.left&&pin.right<=canvas.right&&pin.top>=canvas.top&&pin.bottom<=canvas.bottom;
      });
      assert.ok(contained,`${id} must be visibly contained in the model canvas`);
      await shot(`detail-${width}-${theme}-${id}.png`);
      // A cut that keeps the opposite half must hide this marker as well.
      await page.evaluate(()=>window.__detail.setCut('sagittal',.5,!window.__detail.state.reverse));
      await page.waitForFunction(()=>document.querySelector('#detailPin').hidden);
      await page.locator('#reset').click();
      assert.equal(await page.evaluate(()=>window.__detail.state.marker),null);
      assert.ok(await page.locator('#markerSelection').isHidden());
      // Hiding the selected bone must also remove its active marker and card,
      // whether the user uses the card action or the composition checkbox.
      for(const control of ['button','checkbox']){
        await page.evaluate(()=>window.__detail.selectPart('mandible',true));
        await page.locator(`[data-marker="${id}"]`).click();
        await page.waitForFunction(()=>!document.querySelector('#detailPin').hidden);
        if(control==='button')await page.locator('#hidePart').click();
        else{
          if(await page.locator('#partsDetails').getAttribute('open')===null)await page.locator('#partsDetails summary').click();
          await page.locator('[data-visible="mandible"]').uncheck();
        }
        assert.equal(await page.evaluate(()=>window.__detail.state.marker),null);
        await page.waitForFunction(()=>document.querySelector('#detailPin').hidden);
        assert.ok(await page.locator('#detailPin').isHidden());
        assert.ok(await page.locator('#markerSelection').isHidden());
        await page.locator('#reset').click();
      }
    }

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

    // OpenEar is a separately registered specimen. Exercise controls through
    // their actual UI, including the bone block around the small ossicles.
    await page.locator('[data-mode="openear"]').click();
    await ready();
    assert.equal(await page.evaluate(()=>window.__detail.state.error),null);
    assert.equal(await page.evaluate(()=>window.__detail.state.mode),'openear');
    assert.equal(await page.evaluate(()=>window.__detail.counts().parts),13);
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),13);
    assert.ok(await page.locator('#earTranslucent').isChecked());
    assert.equal(await page.evaluate(()=>window.__detail.state.translucent),true);
    assert.ok(await page.locator('#zSwitches').isHidden());
    await shot(`openear-${width}-${theme}-context.png`);
    await page.locator('#earTranslucent').uncheck();
    assert.equal(await page.evaluate(()=>window.__detail.state.translucent),false);
    await page.locator('#earTranslucent').check();
    if(await page.locator('#partsDetails').getAttribute('open')===null)await page.locator('#partsDetails summary').click();
    assert.equal(await page.locator('[data-part]').count(),13);
    await page.locator(`[data-visible="${earContext.id}"]`).uncheck();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),12);
    await page.locator(`[data-visible="${earContext.id}"]`).check();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),13);
    await page.locator(`[data-part="${stapes.id}"]`).click();
    assert.equal(await page.evaluate(()=>window.__detail.state.selected),stapes.id);
    assert.ok((await page.locator('#selection').innerText()).includes(stapes.ru));
    await page.locator('#onlyPart').click();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),1);
    await shot(`openear-${width}-${theme}-stapes.png`);
    await page.locator('#reset').click();
    assert.equal(await page.evaluate(()=>window.__detail.counts().visible),13);
    assert.equal(await page.evaluate(()=>window.__detail.state.selected),null);
    assert.equal(await page.evaluate(()=>window.__detail.state.translucent),true);
    await page.locator('#cutPlane').selectOption('coronal');
    await page.locator('#reverseCut').check();
    assert.equal(await page.evaluate(()=>window.__detail.state.clip),'coronal');
    assert.equal(await page.evaluate(()=>window.__detail.state.reverse),true);
    await shot(`openear-${width}-${theme}-cut.png`);
    await page.locator('#reset').click();
    assert.equal(await page.evaluate(()=>window.__detail.state.clip),'off');
    assert.equal(await page.evaluate(()=>window.__detail.state.reverse),false);
    assert.ok(await page.locator('#detailPin').isHidden());
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Viewer must fit the viewport without horizontal scrolling');

    // Opening details must preserve the parent atlas document, selection and
    // URL. The child back action closes the dialog rather than navigating it.
    await page.goto(`${base}/local.html#head`);
    await page.waitForFunction(()=>window.__atlas?.state.sec==='head'&&document.querySelector('#veil').hidden);
    await page.evaluate(()=>{window.__embeddedRegressionToken='parent-remains-loaded';window.__atlas.select('frontal');});
    const atlasUrl=page.url(),atlasSelection=await page.evaluate(()=>window.__atlas.state.sel);
    await page.locator('#bHeadDetail').click();
    await page.waitForFunction(()=>document.querySelector('#headDetailDialog').open);
    const child=await page.locator('#headDetailFrame').elementHandle().then(handle=>handle.contentFrame());
    assert.ok(child,'Detail iframe must have its own browsing context');
    await child.waitForFunction(()=>window.__detail?.state.ready||window.__detail?.state.error,{},{timeout:120000});
    assert.equal(await child.evaluate(()=>window.__detail.state.error),null);
    assert.equal(new URL(child.url()).searchParams.get('embed'),'1');
    assert.equal(page.url(),atlasUrl);
    assert.equal(await page.evaluate(()=>window.__embeddedRegressionToken),'parent-remains-loaded');
    await shot(`embedded-${width}-${theme}-detail.png`);
    await child.locator('.back').click();
    await page.waitForFunction(()=>!document.querySelector('#headDetailDialog').open&&document.querySelector('#headDetailFrame').getAttribute('src')==='about:blank');
    assert.equal(page.url(),atlasUrl);
    assert.equal(await page.evaluate(()=>window.__atlas.state.sel),atlasSelection);
    assert.equal(await page.evaluate(()=>window.__embeddedRegressionToken),'parent-remains-loaded');

    // Even if the entire child document fails before its JavaScript starts,
    // the parent's persistent close button must remain reachable and work.
    const failedChild='**/skull-detail.html?*';
    await page.route(failedChild,route=>route.fulfill({status:503,contentType:'text/html; charset=utf-8',body:'<!doctype html><meta charset="utf-8"><p>Модель временно недоступна</p>'}));
    await page.locator('#bHeadDetail').click();
    await page.frameLocator('#headDetailFrame').getByText('Модель временно недоступна').waitFor();
    assert.ok(await page.locator('#closeHeadDetail').isVisible());
    await shot(`embedded-${width}-${theme}-failed-child.png`);
    await page.locator('#closeHeadDetail').click();
    await page.waitForFunction(()=>!document.querySelector('#headDetailDialog').open);
    assert.equal(page.url(),atlasUrl);
    assert.equal(await page.evaluate(()=>window.__embeddedRegressionToken),'parent-remains-loaded');
    assert.equal(await page.evaluate(()=>window.__atlas.state.sel),atlasSelection);
    await page.unroute(failedChild);
    assert.deepEqual(errors,[]);
    report.cases.push({width,height,theme,status:'passed',z_bones:22,z_cavities:8,z_visibility_selection_isolation_reset:true,z_clipping:true,z_markers:testedMarkers,z_markers_visible_and_clipped:true,microct_load:true,microct_clipping:['sagittal','coronal','axial'],microct_reverse_cut:true,microct_neutral_lateral_labels:true,openear_parts:13,openear_stapes_selection_isolation_reset:true,openear_context_visibility_transparency:true,openear_clipping:true,embedded_parent_navigation_preserved:true,embedded_child_back_closes:true,embedded_parent_close_after_child_failure:true,load_failure_recovery:true,microct_load_and_front_screenshot_ms:microctLoadAndScreenshotMs,page_errors:errors,screenshots});
    console.log(`${width} ${theme}: passed; micro-CT load + screenshot ${microctLoadAndScreenshotMs} ms`);
    await context.close();
  }
  report.local_navigation_round_trip='embedded dialog preserves the atlas document and selection in all four layouts';
  report.status='passed';
}catch(error){report.status='failed';report.error=String(error?.stack||error);throw error;}
finally{
  await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n');
  await browser.close();server.close();
}
