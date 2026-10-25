// Four MCP-I sesamoids from the Visible Human Male CT (scripts/publish_vhp_sesamoids.py) in the real atlas:
// loading with BVH, published triangle counts, sides, card attribution, isolation, canvas picking with
// BVH/native ray agreement, desktop/mobile and both themes. New evidence run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'vhp-sesamoids-ui');
const provenance = JSON.parse(await fs.readFile(path.join(site, 'models/vhp-male/thumb-sesamoids/provenance.json'), 'utf8'));
const triangles = Object.fromEntries(provenance.files.map(f => [f.id, f.triangles]));
const IDS = Object.keys(triangles);
const PROBE = `window.__ses={visible:()=>[...structs.values()].filter(s=>s.meshes.some(m=>m.visible)).map(s=>s.id),
clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=4)for(let x=15;x<r.width-inset.right-15;x+=4){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},
compare(t){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,fns=meshes.map(m=>m.raycast),rect=canvas.getBoundingClientRect();const x=(t.x-rect.left)/rect.width*2-1,y=-(t.y-rect.top)/rect.height*2+1;const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>[h.object.userData.sid,h.faceIndex,h.distance]);};ray.firstHitOnly=false;const fast=cast();let slow;try{meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);slow=cast();}finally{meshes.forEach((m,i)=>m.raycast=fns[i]);}ray.firstHitOnly=!headCutActive();return {same:fast.length===slow.length&&fast.every((h,i)=>h[0]===slow[i][0]&&h[1]===slow[i][1]&&Math.abs(h[2]-slow[i][2])<1e-7),hits:fast.length};}};
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
await new Promise(resolve => server.listen(8798, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const report = [];
try {
  for (const [width, theme] of [[1280, 'light'], [390, 'dark']]) {
    const context = await browser.newContext({viewport: {width, height: width === 390 ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: 'reduce'});
    const page = await context.newPage(), errors = [], checks = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(15000);
    const check = (ok, label) => {assert.ok(ok, `${width}: ${label}`); checks.push(label);};
    const close = async () => {if (await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();};
    const card = async () => {if (width === 390) {if (await page.locator('#app').getAttribute('data-card-open') !== 'true') await page.locator('#mobileCard').click();}
      else if (await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent() === 'Подробнее') await page.locator('#bMore').click();};
    const side = async s => {await close(); if (width === 390 && !await page.locator(`[data-side-view="${s}"]`).isVisible()) await page.locator('#bOptions').click();
      await page.locator(`[data-side-view="${s}"]`).click(); if (await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();};
    await page.goto(`http://127.0.0.1:8798/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    await page.evaluate(async () => {await __atlas.enterSection('arm'); __atlas.setSub('hand');});
    const loaded = await page.evaluate(ids => __atlas.inspect().structures.filter(s => ids.includes(s.id)), IDS);
    check(loaded.length === 4 && loaded.every(s => s.kind === 'b' && s.bvh && s.side === (s.id.endsWith('_left') ? 'left' : 'right')), 'Four sesamoids loaded as sided bones with BVH');
    check(loaded.every(s => s.triangles === triangles[s.id]), 'Loaded triangles equal published GLB');
    for (const id of IDS) {
      await page.evaluate(async id => {await __atlas.goTo(id);}, id);
      check(await page.evaluate(() => __atlas.state.sel) === id, 'Card selection ' + id);
    }
    await card();
    const text = await page.locator('body').innerText();
    check(text.includes('Visible Human') && text.includes('Courtesy of the U.S. National Library of Medicine') && !text.includes('Именованной и анатомически подтверждённой модели нет'),
      'Card states the CT source, NLM attribution and no stale "no model" note');
    check(text.includes('реконструкция по КТ другого тела (Visible Human)') && !text.includes('доступны как карточки без 3D'), 'Section coverage note reflects loaded sesamoids');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-card.png`)});
    await close();
    await page.evaluate(async () => {__atlas.setSub('hand'); await __atlas.goTo('sesamoid_mcp1_radial_right');});
    for (const s of ['right', 'left', 'both']) {
      await side(s); const v = await page.evaluate(() => __ses.visible());
      check(s === 'right' ? v.includes('sesamoid_mcp1_radial_right') && !v.includes('sesamoid_mcp1_radial_left')
        : s === 'left' ? !v.includes('sesamoid_mcp1_radial_right') && v.includes('sesamoid_mcp1_radial_left')
        : v.includes('sesamoid_mcp1_radial_right') && v.includes('sesamoid_mcp1_radial_left'), 'Side filter ' + s);
    }
    await page.evaluate(async () => {await __atlas.goTo('sesamoid_mcp1_ulnar_left');});
    await card(); await page.locator('#bIso').click(); await close(); await page.waitForTimeout(700);
    const visible = await page.evaluate(() => __ses.visible());
    check(visible.includes('sesamoid_mcp1_ulnar_left') && !visible.includes('sesamoid_mcp1_ulnar_right'), 'Isolation keeps the selected sesamoid');
    const point = await page.evaluate(() => __ses.clickPoint('sesamoid_mcp1_ulnar_left'));
    check(!!point, 'Ray point on the isolated sesamoid');
    const rays = await page.evaluate(p => __ses.compare(p), point);
    check(rays.same && rays.hits > 0, 'BVH and native rays agree');
    // Deselecting can reframe the view; recompute the target on the settled frame before a real click.
    await page.evaluate(() => __atlas.select(null));
    await page.waitForTimeout(900);
    const settled = await page.evaluate(() => __ses.clickPoint('sesamoid_mcp1_ulnar_left'));
    check(!!settled, 'Ray point after deselection');
    await page.mouse.click(settled.x, settled.y);
    check(await page.evaluate(() => __atlas.state.sel) === 'sesamoid_mcp1_ulnar_left', 'Canvas click selects the sesamoid');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-isolated.png`)});
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS errors: ' + errors.join(' | '));
    report.push({width, theme, status: 'passed', checks});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Chromium/SwiftShader emulation; not a physical phone.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), checks: report.reduce((n, r) => n + r.checks.length, 0)}));
