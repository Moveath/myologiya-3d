// Abdominal muscles (ABD-MUSCLES) in the real atlas: r170/meshopt loading into the trunk section, the abdomen
// subsection, layers, sides, isolation, canvas picking with BVH/native ray agreement, cards, catalogue, search
// and quiz at 1280 light and 390 dark. New evidence run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'abdomen-muscles-ui');
const provenance = JSON.parse(await fs.readFile(path.join(site, 'models/bodyparts3d-3.0/abdomen-muscles/provenance.json'), 'utf8'));
const triangles = Object.fromEntries(provenance.files.map(f => [f.id, f.triangles]));
const ids = Object.keys(triangles);
const of = base => ids.filter(id => id.startsWith('abdomen_' + base));
const PROBE = `window.__abdCheck={visible:()=>[...structs.values()].filter(s=>s.kind==='m'&&s.meshes.some(m=>m.visible)).map(s=>s.id),
clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=8)for(let x=15;x<r.width-inset.right-15;x+=8){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},
compare(target){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[],rect=canvas.getBoundingClientRect(),samples=[[(target.x-rect.left)/rect.width*2-1,-(target.y-rect.top)/rect.height*2+1],...[-.5,0,.5].flatMap(x=>[-.5,0,.5].map(y=>[x,y]))];for(const [x,y] of samples){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex}));};ray.firstHitOnly=false;const fast=cast();try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();if(fast.length!==slow.length)throw Error('Ray count mismatch');for(let i=0;i<fast.length;i++)if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray face mismatch');}finally{meshes.forEach((m,i)=>m.raycast=functions[i]);}results.push({x,y,hits:fast.length});}ray.firstHitOnly=!headCutActive();return {rays:results,bvh:meshes.filter(m=>!!m.geometry.boundsTree).length};}};
`;
const server = http.createServer(async (req, res) => {
  const file = path.resolve(site, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (!file.startsWith(site + path.sep)) {res.writeHead(403).end(); return;}
  try {
    let body = await fs.readFile(file);
    if (file.endsWith('local.html')) body = body.toString().replace('window.__atlas =', PROBE + 'window.__atlas =');
    res.setHeader('Content-Type', file.endsWith('.html') ? 'text/html; charset=utf-8' : file.endsWith('.js') ? 'text/javascript' : 'application/octet-stream');
    res.end(body);
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(8797, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const report = [];
try {
  for (const [width, theme] of [[1280, 'light'], [390, 'dark']]) {
    const context = await browser.newContext({viewport: {width, height: width === 390 ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: 'reduce'});
    const page = await context.newPage(), errors = [], checks = [], assets = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    page.on('request', r => {if (/\.(glb|txt)$/.test(new URL(r.url()).pathname)) assets.push(new URL(r.url()).pathname);});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(10000);
    const check = (ok, label) => {assert.ok(ok, `${width}/${theme}: ${label}`); checks.push(label);};
    const close = async () => {if (await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();};
    const option = async selector => {await close(); if (!await page.locator(selector).isVisible()) await page.locator('#bOptions').click();
      await page.locator(selector).click(); if (await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();};
    const card = async () => {if (width === 390) {if (await page.locator('#app').getAttribute('data-card-open') !== 'true') await page.locator('#mobileCard').click();}
      else if (await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent() === 'Подробнее') await page.locator('#bMore').click();};
    const visible = () => page.evaluate(() => __abdCheck.visible());
    const started = Date.now();
    await page.goto(`http://127.0.0.1:8797/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    check(assets.length === 0, 'Home does not preload models');
    check((await page.locator('.seccard[data-sec="trunk"]').innerText()).includes('Грудь и живот'), 'Home card names the chest and abdomen');
    await page.locator('.seccard[data-sec="trunk"]').click();
    await page.waitForFunction(() => window.__atlas.state.sec === 'trunk' && document.querySelector('#veil').hidden, null, {timeout: 60000});
    const loadMs = Date.now() - started;
    check(assets.every(u => u.includes('/thorax-') || u.includes('/abdomen-muscles/')) && ids.every(id => assets.some(u => u.endsWith(`/${id}.glb`))),
      'Trunk loads its GLB and the 12 abdominal models only');
    const loaded = await page.evaluate(ids => __atlas.inspect().structures.filter(s => ids.includes(s.id)), ids);
    check(loaded.length === 12 && loaded.every(s => s.kind === 'm' && s.bvh && s.triangles === triangles[s.id]), 'All 12 muscles loaded with BVH and published triangle counts');
    check(loaded.every(s => s.side === (s.id.endsWith('_left') ? 'left' : 'right')), 'Sides from the cards');

    await page.evaluate(() => __atlas.setSub('abdomen'));
    check(await page.locator('[data-sub="abdomen"]').getAttribute('aria-pressed') === 'true' || await page.locator('#mobileSub').inputValue() === 'abdomen', 'Abdomen subsection selected');
    let v = await visible();
    check(v.length === 12 && ids.every(id => v.includes(id)), 'Subsection shows exactly the 12 abdominal muscles');
    await page.waitForTimeout(400);
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-abdomen-overview.png`)});
    await option('[data-peel="1"]'); v = await visible();
    check(of('obliquus_externus').every(id => !v.includes(id)) && of('obliquus_internus').every(id => v.includes(id)), 'Layer −1 removes the external obliques');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-abdomen-peel1.png`)});
    await option('[data-peel="2"]'); v = await visible();
    check(of('obliquus_internus').every(id => !v.includes(id)) && ['transversus', 'rectus', 'pyramidalis', 'quadratus'].every(b => of(b).every(id => v.includes(id))),
      'Layer −2 shows the transversus, rectus, pyramidalis and quadratus lumborum');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-abdomen-peel2.png`)});
    await option('[data-peel="0"]');

    for (const id of ids) {
      await page.evaluate(async id => {await __atlas.goTo(id);}, id);
      check(await page.evaluate(() => __atlas.state.sel) === id && (await visible()).includes(id), 'Card selection and visibility ' + id);
      check(!(await page.locator('#sheet').textContent()).includes('undefined') && await page.locator('[data-field="o"] .field-sources').count() === 1, 'Card fields ' + id);
    }
    await page.evaluate(() => __atlas.goTo('abdomen_rectus_abdominis_right'));
    check(await page.evaluate(() => __atlas.state.peel) === 2, 'Rectus opens below both obliques');
    await card();
    const text = await page.locator('#sheet').textContent();
    const missing = ['m. rectus abdominis', 'Сухожильные перемычки', 'Влагалище прямой мышцы живота', 'отдельный небольшой фрагмент', 'Мечевидный отросток'].filter(s => !text.includes(s));
    check(!missing.length, 'Rectus card: Latin, features, model limits, insertion; missing: ' + missing.join(', '));
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-rectus-card.png`)});
    await close();

    await page.evaluate(() => {__atlas.setSub('abdomen');});
    await option('[data-peel="0"]');
    for (const s of ['right', 'left', 'both']) {
      await option(`[data-side-view="${s}"]`); v = await visible();
      check(s === 'both' ? v.length === 12 : v.length === 6 && v.every(id => id.endsWith('_' + s)), 'Side ' + s);
    }
    const probe = 'abdomen_obliquus_externus_abdominis_right';
    await page.evaluate(id => __atlas.select(id, null, true), probe);
    await card(); await page.locator('#bIso').click();
    check(JSON.stringify(await visible()) === JSON.stringify([probe]), 'Isolation');
    await close(); await page.waitForTimeout(600);
    const point = await page.evaluate(id => __abdCheck.clickPoint(id), probe); check(!!point, 'Ray point on the external oblique');
    const rays = await page.evaluate(p => __abdCheck.compare(p), point);
    check(rays.bvh > 0 && rays.rays.some(r => r.hits > 0), 'BVH/native ray agreement');
    await page.mouse.click(point.x, point.y); check(await page.evaluate(() => __atlas.state.sel) === probe, 'Canvas selection');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-isolated.png`)});
    await card(); await page.locator('#bIso').click(); await close();

    await page.locator('#bList').click();
    check(await page.locator('[data-group="abdomen-anterolateral"] .item-row').count() === 5 && await page.locator('[data-group="abdomen-posterior"] .item-row').count() === 1,
      'Catalogue: five anterolateral rows and the quadratus lumborum');
    check((await page.locator('[data-group="abdomen-anterolateral"] .missing').textContent()).includes('поднимающая яичко'), 'Cremaster gap stays visible');
    await page.locator('#q').fill('косая мышца живота');
    check(await page.locator('#dlist [data-id="abdomen_obliquus_internus_abdominis_left"]').count() > 0, 'Search finds the oblique muscles');
    await page.locator('#dlist [data-id="abdomen_obliquus_internus_abdominis_left"]').first().click();
    check(await page.evaluate(() => __atlas.state.sel) === 'abdomen_obliquus_internus_abdominis_left', 'Search result opens the left internal oblique');
    if (await page.locator('#bCloseList').isVisible()) await page.locator('#bCloseList').click();
    const quiz = async () => {
      await close();
      if (!await page.locator('#bQuiz').isVisible()) {  // 390 px: the quiz button lives in the ☰ menu
        await page.locator('#bOptions').click();
        await page.locator('#bQuiz').waitFor({state: 'visible'});
      }
      await page.locator('#bQuiz').click();
      if (await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();
    };
    await quiz();
    await page.locator('[data-scope="abdomen"]').click();
    check(await page.evaluate(() => __atlas.state.quiz.options.length >= 2 && __atlas.state.quiz.target?.startsWith('abdomen_')), 'Quiz over the abdominal muscles');
    await quiz();
    check(await page.evaluate(() => __atlas.state.mode) === 'study', 'Quiz closes');
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS/model errors: ' + errors.join(' | '));
    report.push({width, theme, status: 'passed', checks: checks.length, sectionLoadMs: loadMs, durationMs: Date.now() - started});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Desktop/mobile emulation with SwiftShader; not a physical phone or GPU benchmark.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
