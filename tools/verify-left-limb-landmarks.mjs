// Approximate left limb landmarks (scripts/make_left_limb_landmarks.py) in the real atlas:
// markers on the left side only, explicit "ориентировочно" labels, muscle links, "Кости мышцы",
// unchanged right records, desktop/mobile and both themes. New evidence run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'left-limb-landmarks-ui');
const source = await fs.readFile(path.join(site, 'pins-left-transfer.js'), 'utf8');
const patches = JSON.parse(source.match(/const patches=(.*?);\r?\n/s)[1]);
const accepted = Object.entries(patches).filter(([, p]) => p.anchorStatus === 'contralateral_transfer').map(([id]) => id);
const PROBE = `window.__lm={markers:()=>pinEls.map(e=>({id:e.pin.id,anchor:e.el.dataset.anchor||'',x:e.pin.p[0]})),
approx:()=>A.pins.filter(p=>p.anchorStatus==='contralateral_transfer').map(p=>({id:p.id,b:p.b,x:p.p?.[0],n:!!p.n})),
right:()=>A.pins.filter(p=>p.p&&!p.b.endsWith('_left')&&p.anchorStatus!=='contralateral_transfer').length,
related:()=>visibilityPolicy().related};\n`;
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
const CASES = {
  arm: {muscle: 'deltoid_left', right: 'deltoid', bone: 'humerus_left', bones: ['clavicle_left', 'scapula_left', 'humerus_left']},
  leg: {muscle: 'semimembranosus_left', right: 'semimembranosus', bone: 'tibia_left', bones: ['hip_bone_left', 'tibia_left']},
};
const report = [];
try {
  for (const [width, theme] of [[1280, 'light'], [390, 'dark']]) for (const [sec, c] of Object.entries(CASES)) {
    const context = await browser.newContext({viewport: {width, height: width === 390 ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: 'reduce'});
    const page = await context.newPage(), errors = [], checks = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(15000);
    const check = (ok, label) => {assert.ok(ok, `${width}/${sec}: ${label}`); checks.push(label);};
    const card = async () => {if (width === 390 && await page.locator('#app').getAttribute('data-card-open') !== 'true') await page.locator('#mobileCard').click();
      else if (width > 390 && await page.locator('#bMore').isVisible() && await page.locator('#bMore').textContent() === 'Подробнее') await page.locator('#bMore').click();};
    await page.goto(`http://127.0.0.1:8797/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    await page.evaluate(async s => {await __atlas.enterSection(s); __atlas.setSub('all');}, sec);
    const approx = await page.evaluate(() => __lm.approx());
    check(approx.length === accepted.length && approx.every(p => p.x > 0 && p.n && p.b.endsWith('_left')), `All ${accepted.length} approximate points are left-side with normals`);
    // Left muscle: chips, markers and the approximate note.
    await page.evaluate(async id => {await __atlas.goTo(id);}, c.muscle);
    await card();
    const text = (await page.locator('body').innerText()).toLowerCase();
    check(text.includes('ориентиры прикреплений на костях') && text.includes('ориентировочно'), 'Left muscle lists its attachment chips as approximate');
    await page.waitForTimeout(400);
    const markers = await page.evaluate(() => __lm.markers());
    check(markers.length > 0 && markers.every(m => m.x > 0), 'Left muscle markers are on the left side');
    check(markers.some(m => m.anchor === 'approximate'), 'Approximate markers carry data-anchor');
    const pinId = markers.find(m => m.anchor === 'approximate').id;
    await page.locator(`.chip[data-pinid="${pinId}"]`).first().click();
    await card();
    const pinText = (await page.locator('body').innerText()).toLowerCase();
    check(pinText.includes('ориентировочное положение') && pinText.includes('перенесена с проверенного правого ориентира'), 'Landmark card states the transfer and its limit');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${sec}-left-muscle-pin.png`)});
    // "Кости мышцы": left bones from the new links.
    await page.evaluate(async id => {__atlas.state.pin = null; await __atlas.goTo(id);}, c.muscle);
    if (!await page.evaluate(() => __atlas.state.muscleBones)) {
      if (await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();
      if (width === 390 && !await page.locator('#bMuscleBones').isVisible()) await page.locator('#bOptions').click();
      await page.locator('#bMuscleBones').click();
      if (await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();
    }
    const related = await page.evaluate(() => __lm.related());
    check(c.bones.every(b => related.includes(b)) && related.every(b => b.endsWith('_left') || /^(lumbar|sacrum|coccyx)/.test(b)), '"Кости мышцы" shows left bones: ' + related.join(','));
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${sec}-muscle-bones.png`)});
    await page.evaluate(() => {document.querySelector('#bMuscleBones')?.click();});
    // Right muscle unchanged: no approximate markers.
    await page.evaluate(async id => {__atlas.state.pin = null; await __atlas.goTo(id);}, c.right);
    await page.waitForTimeout(300);
    const rightMarkers = await page.evaluate(() => __lm.markers());
    check(rightMarkers.length > 0 && rightMarkers.every(m => m.x < 0 && !m.anchor), 'Right muscle markers unchanged');
    // Left bone card.
    await page.evaluate(async id => {__atlas.state.pin = null; await __atlas.goTo(id);}, c.bone);
    await card();
    check((await page.locator('body').innerText()).toLowerCase().includes('ориентировочно'), 'Left bone card counts approximate points');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${sec}-left-bone.png`)});
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS errors: ' + errors.join(' | '));
    report.push({width, theme, sec, status: 'passed', checks, rightPositionedRecords: await page.evaluate(() => __lm.right())});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {accepted: accepted.length, report, scope: 'Chromium/SwiftShader emulation; not a physical phone.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), cases: report.length, checks: report.reduce((n, r) => n + r.checks.length, 0)}));
