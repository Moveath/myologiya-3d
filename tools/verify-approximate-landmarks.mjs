// Approximate landmarks added by LOG-20261026-02: craniometric suture junctions (pins-craniometric.js) and the
// locally refined left transfers (pins-left-transfer.js). Real clicks in the atlas at 1280 light and 390 dark:
// dashed approximate marker, card note, point on the loaded published mesh, records without a junction stay
// without a marker. New evidence run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'approximate-landmarks-ui');
const CASES = [
  {section: 'head', bone: 'frontal', pin: 'shared_skull_016', marker: true},
  {section: 'head', bone: 'occipital', pin: 'shared_skull_017', marker: true},
  {section: 'head', bone: 'temporal_right', pin: 'shared_skull_020_right', marker: true},
  {section: 'head', bone: 'temporal_left', pin: 'shared_skull_020_left', marker: true},
  {section: 'head', bone: 'frontal', pin: 'shared_skull_019_right', marker: false},
  {section: 'head', bone: 'frontal', pin: 'shared_skull_015', marker: false},
  {section: 'leg', bone: 'femur_left', pin: 'context_femur_left_A02_5_04_009', marker: true},
  {section: 'leg', bone: 'tibia_left', pin: 'context_tibia_left_A02_5_06_023', marker: true},
  {section: 'leg', bone: 'hip_bone_left', pin: 'context_hip_bone_left_A02_5_01_307', marker: true},
];
const PROBE = `window.__approxCheck={distance(id){scene.updateMatrixWorld(true);const p=pinById[id],point=new THREE.Vector3(...p.p),triangle=new THREE.Triangle(),closest=new THREE.Vector3();let best=Infinity;for(const mesh of structs.get(p.b).meshes){const g=mesh.geometry,pos=g.attributes.position,idx=g.index;for(let i=0;i<(idx?idx.count:pos.count);i+=3){for(const [j,v] of [triangle.a,triangle.b,triangle.c].entries())v.fromBufferAttribute(pos,idx?idx.getX(i+j):i+j).applyMatrix4(mesh.matrixWorld);triangle.closestPointToPoint(point,closest);best=Math.min(best,point.distanceTo(closest));}}return best*1000;}};
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
    const page = await context.newPage(), errors = [], checks = [], distances = {};
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(15000);
    const check = (ok, label) => {assert.ok(ok, `${width}: ${label}`); checks.push(label);};
    const openCard = async () => {
      if (await page.locator('#mobileCard').isVisible() && await page.locator('#app').getAttribute('data-card-open') !== 'true') await page.locator('#mobileCard').click();
      if (await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent() === 'Подробнее') await page.locator('#bMore').click();
    };
    await page.goto(`http://127.0.0.1:8798/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    for (const c of CASES) {
      await page.evaluate(async ({section, bone}) => {__atlas.activatePin(null); await __atlas.enterSection(section); await __atlas.goTo(bone);}, c);
      await openCard(page);
      const chip = page.locator(`#sheet [data-pinid="${c.pin}"]`);
      check(await chip.count() === 1, `Chip on ${c.bone}: ${c.pin}`);
      await chip.first().scrollIntoViewIfNeeded(); await chip.first().click(); await openCard(page);
      check(await page.evaluate(() => __atlas.state.pin) === c.pin, 'Pin activated ' + c.pin);
      const marker = page.locator(`.pin[data-pinid="${c.pin}"]`);
      check(await marker.count() === (c.marker ? 1 : 0), `Marker ${c.marker ? 'shown' : 'absent'}: ${c.pin}`);
      if (c.marker) {
        check(await marker.getAttribute('data-anchor') === 'approximate', 'Dashed approximate marker ' + c.pin);
        const box = await page.locator('.pinbox').textContent();
        check(box.includes('Ориентировочное положение'), 'Card states approximate position ' + c.pin);
        distances[c.pin] = await page.evaluate(id => __approxCheck.distance(id), c.pin);
        check(distances[c.pin] < 0.05, `Point on the loaded mesh of ${c.bone} (${distances[c.pin].toFixed(4)} mm)`);
      }
      if (c.pin === 'shared_skull_017') {
        if (width === 390 && await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();
        await page.evaluate(() => __atlas.setView?.('post'));
        await page.waitForTimeout(400);
        await page.screenshot({path: path.join(run.dir, `${width}-${theme}-lambda.png`)});
      }
      if (c.pin === 'shared_skull_020_right' || c.pin === 'context_femur_left_A02_5_04_009') {
        if (width === 390 && await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();
        await page.waitForTimeout(400);
        await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${c.pin}.png`)});
      }
    }
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS errors: ' + errors.join(' | '));
    report.push({width, theme, status: 'passed', checks: checks.length, distancesMM: distances});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Chromium/SwiftShader emulation; not a physical phone. Positions are educational approximations, not anatomist-accepted.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
