// Left limb muscles (CAT-MUSCLE-BILATERAL): real r170/meshopt loading, parts, sides, search, isolation,
// canvas picking with BVH/native ray agreement and card limits in the actual atlas. New evidence run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'stage7-left-limb-muscles-ui');
const provenance = JSON.parse(await fs.readFile(path.join(site, 'models/bodyparts3d-3.0/left-limb-muscles/provenance.json'), 'utf8'));
const triangles = Object.fromEntries(provenance.files.map(f => [f.id, f.parts.reduce((n, p) => n + p.triangles, 0)]));
const REGIONS = {
  arm: {probe: 'deltoid_left', part: 'acrom', ids: provenance.files.filter(f => f.region === 'arm').map(f => f.id)},
  leg: {probe: 'gluteus_maximus_left', part: null, ids: provenance.files.filter(f => f.region === 'leg').map(f => f.id)},
};
const PROBE = `window.__muscleCheck={visible:()=>[...structs.values()].filter(s=>s.kind==='m'&&s.meshes.some(m=>m.visible)).map(s=>s.id),
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
await new Promise(resolve => server.listen(8792, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const report = [];
try {
  for (const [width, theme] of [[1280, 'light'], [390, 'dark']]) for (const [region, {probe, part, ids}] of Object.entries(REGIONS)) {
    const context = await browser.newContext({viewport: {width, height: width === 390 ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: 'reduce'});
    const page = await context.newPage(), errors = [], checks = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (['error', 'warning'].includes(m.type()) && /мышц|muscle|GLTF|Meshopt/i.test(m.text()) || m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(10000);
    const check = (ok, label) => {assert.ok(ok, `${width}/${region}: ${label}`); checks.push(label);};
    const close = async () => {if (await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();};
    const side = async s => {await close(); if (width === 390 && !await page.locator(`[data-side-view="${s}"]`).isVisible()) await page.locator('#bOptions').click();
      await page.locator(`[data-side-view="${s}"]`).click(); if (await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();};
    const card = async () => {if (width === 390) {if (await page.locator('#app').getAttribute('data-card-open') !== 'true') await page.locator('#mobileCard').click();}
      else if (await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent() === 'Подробнее') await page.locator('#bMore').click();};
    const visible = () => page.evaluate(() => __muscleCheck.visible());
    const started = Date.now();
    await page.goto(`http://127.0.0.1:8792/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    await page.evaluate(async r => {await __atlas.enterSection(r); __atlas.setSub('all');}, region);
    const loadMs = Date.now() - started;
    const loaded = await page.evaluate(ids => __atlas.inspect().structures.filter(s => ids.includes(s.id)), ids);
    check(loaded.length === ids.length && loaded.every(s => s.kind === 'm' && s.side === 'left' && s.bvh), `All ${ids.length} left muscles loaded with BVH`);
    check(loaded.every(s => s.triangles === triangles[s.id]), 'Loaded triangle counts equal published GLB');
    for (const id of ids) {
      await page.evaluate(async id => {await __atlas.goTo(id);}, id);
      check(await page.evaluate(() => __atlas.state.sel) === id, 'Card selection ' + id);
    }
    // goTo opens each muscle's own subsection and layer; reselect the probe so it is on screen again.
    await page.evaluate(() => __atlas.setSub('all'));
    await page.evaluate(([id, p]) => __atlas.select(id, p, true), [probe, part]);
    check(await page.evaluate(() => [__atlas.state.sel, __atlas.state.selPart ?? ''].join('|')) === probe + '|' + (part ?? ''), 'Muscle/part selection');
    const right = probe.replace('_left', '');
    for (const s of ['both', 'right', 'left']) {
      await side(s); const v = await visible();
      check(s === 'both' ? v.includes(probe) && v.includes(right) : s === 'left' ? v.includes(probe) && !v.includes(right) : !v.includes(probe) && v.includes(right), 'Side ' + s);
    }
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${region}-left-side.png`)});
    await side('both');
    await page.locator('#bList').click(); await page.locator('#q').fill(await page.evaluate(id => ATLAS.muscles[id].ru, probe));
    await page.locator(`#dlist [data-id="${probe}"]`).first().click();
    check(await page.evaluate(() => __atlas.state.sel) === probe, 'Search and selection');
    await card();
    const text = await page.locator('body').innerText();
    check(text.includes('слева') && text.includes('парной правой мышцы'), 'Card states side and copied paired text');
    await page.locator('#bIso').click(); check(JSON.stringify(await visible()) === JSON.stringify([probe]), 'Isolation');
    await close(); await page.waitForTimeout(600);
    const point = await page.evaluate(id => __muscleCheck.clickPoint(id), probe); check(!!point, 'Ray point');
    const rays = await page.evaluate(p => __muscleCheck.compare(p), point);
    check(rays.bvh > 0 && rays.rays.some(r => r.hits > 0), 'BVH/native ray agreement');
    await page.mouse.click(point.x, point.y); check(await page.evaluate(() => __atlas.state.sel) === probe, 'Canvas selection');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${region}-isolated.png`)});
    await card(); await page.locator('#bIso').click(); await close();
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS/model errors: ' + errors.join(' | '));
    report.push({width, theme, region, status: 'passed', checks: checks.length, muscles: ids.length, sectionLoadMs: loadMs, durationMs: Date.now() - started});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Desktop/mobile emulation with SwiftShader; not a physical phone or GPU benchmark.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
