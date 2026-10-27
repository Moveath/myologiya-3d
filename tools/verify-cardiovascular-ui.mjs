// Cardiovascular expansion (LOG-20261026-03) in the real atlas at 1280 light and 390 dark: all admitted models load
// per section with BVH, face masks match their files and appear only when chosen, a second click on the selected
// heart chooses the chamber under the cursor, isolation/search/side/opacity work, bones and muscles become faint
// context for a selected vessel, five systems work together, cards without geometry stay honest. New evidence run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'cardiovascular-ui');
const box = {window: {ATLAS: {}}}; box.window.window = box.window; vm.createContext(box);
vm.runInContext(await fs.readFile(path.join(site, 'data-cardiovascular.js'), 'utf8'), box);
const CARDS = box.window.ATLAS.structures, GROUPS = Object.fromEntries(box.window.ATLAS.structureGroups.map(g => [g.id, g.sec]));
const admitted = sec => Object.entries(CARDS).filter(([, c]) => !c.noModel && GROUPS[c.g] === sec).map(([id]) => id);
const masks = Object.fromEntries(await Promise.all(Object.entries(CARDS).filter(([, c]) => c.modelKind === 'face-mask')
  .map(async ([id, c]) => [id, JSON.parse(await fs.readFile(path.join(site, c.modelFile), 'utf8')).faceCount])));
const PROBE = `window.__cvCheck={
 structs:()=>[...structs.values()].map(s=>({id:s.id,kind:s.kind,system:s.data?.system||null,v:visState(s),seg:s.data?.segmentOf||null,
   tri:s.meshes.reduce((n,m)=>n+(m.geometry.index?m.geometry.index.count/3:0),0),bvh:s.meshes.every(m=>!!m.geometry.boundsTree)})),
 errors:()=>[...systemErrors.entries()],
 segmentPoint(parent){const r=canvas.getBoundingClientRect();for(let y=inset.top+30;y<r.height-inset.bottom-20;y+=9)for(let x=20;x<r.width-inset.right-20;x+=9){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const u=hitAt(r.left+x,r.top+y);if(u?.sid===parent){const seg=segmentAt(parent,lastHitFace);if(seg)return {x:r.left+x,y:r.top+y,seg};}}return null;},
 clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+30;y<r.height-inset.bottom-20;y+=8)for(let x=20;x<r.width-inset.right-20;x+=8){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;if(hitAt(r.left+x,r.top+y)?.sid===id)return {x:r.left+x,y:r.top+y};}return null;},
 rays(id){scene.updateMatrixWorld(true);const meshes=structs.get(id).meshes,out=[];for(const mesh of meshes){const g=mesh.geometry,pos=g.attributes.position,idx=g.index;for(const k of [.2,.5,.8]){const f=Math.floor(idx.count/3*k);const t=[0,1,2].map(i=>new THREE.Vector3().fromBufferAttribute(pos,idx.getX(f*3+i)).applyMatrix4(mesh.matrixWorld));const n=t[1].clone().sub(t[0]).cross(t[2].clone().sub(t[0])).normalize();const c=t[0].clone().add(t[1]).add(t[2]).multiplyScalar(1/3);const caster=new THREE.Raycaster(c.clone().addScaledVector(n,.02),n.clone().negate());const a=[],b=[];THREE.Mesh.prototype.raycast.call(mesh,caster,a);mesh.raycast(caster,b);a.sort((p,q)=>p.distance-q.distance);b.sort((p,q)=>p.distance-q.distance);out.push(a.length===b.length&&a.length>0&&Math.abs(a[0].distance-b[0].distance)<1e-7&&a.some(h=>h.faceIndex===b[0].faceIndex));}}return out;}};
`;
const server = http.createServer(async (req, res) => {
  const file = path.resolve(site, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (!file.startsWith(site + path.sep)) {res.writeHead(403).end(); return;}
  try {
    let body = await fs.readFile(file);
    if (file.endsWith('local.html')) body = body.toString().replace('window.__atlas =', PROBE + 'window.__atlas =');
    res.setHeader('Content-Type', file.endsWith('.html') ? 'text/html; charset=utf-8' : file.endsWith('.js') ? 'text/javascript' : file.endsWith('.json') ? 'application/json' : 'application/octet-stream');
    res.end(body);
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(8801, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const report = [];
try {
  for (const [width, theme] of [[1280, 'light'], [390, 'dark']]) {
    const context = await browser.newContext({viewport: {width, height: width === 390 ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: 'reduce'});
    const page = await context.newPage(), errors = [], checks = [], timings = {};
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED') || /Cardiovascular|mask/i.test(m.text()) && m.type() === 'warning') errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(20000);
    const check = (ok, label) => {assert.ok(ok, `${width}: ${label}`); checks.push(label);};
    const structs = () => page.evaluate(() => __cvCheck.structs());
    const closeCard = async () => {if (await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();};
    const openCard = async () => {if (width === 390 && await page.locator('#app').getAttribute('data-card-open') !== 'true') await page.locator('#mobileCard').click();};
    const sel = () => page.evaluate(() => __atlas.state.sel);
    await page.goto(`http://127.0.0.1:8801/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    // Every section: all five systems together, every admitted model loaded with BVH, no load errors.
    for (const sec of ['trunk', 'neck', 'arm', 'leg']) {
      const started = Date.now();
      await page.evaluate(async s => {await __atlas.enterSection(s); for (const k of ['bones', 'muscles', 'heart', 'arteries', 'veins']) await __atlas.setSystem(k, true);}, sec);
      await page.waitForFunction(ids => ids.every(id => __cvCheck.structs().some(s => s.id === id)) || __cvCheck.errors().length, admitted(sec), {timeout: 60000});
      timings[sec] = Date.now() - started;
      const all = await structs(), loaded = all.filter(s => s.kind === 's');
      check(!(await page.evaluate(() => __cvCheck.errors())).length, `${sec}: no model errors`);
      check(admitted(sec).every(id => loaded.some(s => s.id === id)), `${sec}: all ${admitted(sec).length} admitted structures loaded`);
      check(loaded.every(s => s.bvh), `${sec}: BVH on every structure`);
      for (const system of ['bones', 'muscles', 'heart', 'arteries', 'veins'].filter(k => sec === 'trunk' || k !== 'heart'))
        check(all.some(s => (s.system || (['m', 'o'].includes(s.kind) ? 'muscles' : s.kind === 'b' ? 'bones' : null)) === system && s.v === 2), `${sec}: ${system} visible together`);
      for (const s of loaded.filter(s => s.seg)) check(s.tri === masks[s.id] && s.v === 0, `${sec}: mask ${s.id} = ${masks[s.id]} faces, hidden until chosen`);
    }
    // Heart: chamber chip, faint context, isolation of a mask, second click chooses the chamber under the cursor.
    await page.evaluate(async () => {await __atlas.enterSection('trunk'); await __atlas.goTo('cv_heart');});
    await openCard();
    check(await sel() === 'cv_heart', 'Heart selected');
    check((await structs()).filter(s => ['b', 'm'].includes(s.kind)).every(s => s.v !== 2), 'Bones and muscles faint while a heart structure is selected');
    await page.locator('#sheet [data-structure-link="cv_ventricle_left"]').click();
    check(await sel() === 'cv_ventricle_left', 'Chamber chosen from the heart card');
    check((await structs()).find(s => s.id === 'cv_ventricle_left').v === 2, 'Chosen chamber mask shown');
    await openCard();
    check((await page.locator('#sheet').innerText()).includes('выделенная списком её граней'), 'Mask card states its provenance');
    await page.locator('#bIso').click();
    const iso = (await structs()).filter(s => s.v === 2).map(s => s.id);
    check(JSON.stringify(iso) === '["cv_ventricle_left"]', 'Isolated mask only');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-left-ventricle-isolated.png`)});
    await openCard(); await page.locator('#bIso').click();
    await page.evaluate(() => __atlas.goTo('cv_heart')); await closeCard(); await page.waitForTimeout(600);
    const point = await page.evaluate(() => __cvCheck.segmentPoint('cv_heart'));
    check(!!point, 'Canvas point on a masked part of the heart');
    await page.mouse.click(point.x, point.y);
    check(await sel() === point.seg, `Second click on the selected heart chooses ${point.seg}`);
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-heart-part-click.png`)});
    // New BodyParts3D heart parts, opacity and native/BVH ray agreement.
    for (const id of ['cv_papillary_rv_septal', 'cv_v_cardiac_great', 'cv_a_coronary_posterior_interventricular']) {
      await page.evaluate(id => __atlas.goTo(id), id);
      check(await sel() === id, 'Selected ' + id);
      check((await page.evaluate(id => __cvCheck.rays(id), id)).every(Boolean), 'BVH/native rays ' + id);
    }
    await openCard();
    await page.locator('#structureOpacity').fill('40');
    check(await page.evaluate(() => __atlas.state.opacity.cv_a_coronary_posterior_interventricular) === 0.4, 'Opacity of a vessel');
    // Search by Russian name reaches a mask card.
    await closeCard(); await page.locator('#bList').click(); await page.locator('#q').fill('правое предсердие');
    await page.locator('#dlist [data-id="cv_atrium_right"]').first().click();
    check(await sel() === 'cv_atrium_right', 'Search selects the right atrium');
    // Z-Anatomy limb vessels: side filter, canvas click, provenance.
    await page.evaluate(async () => {await __atlas.enterSection('arm'); __atlas.setSub('all');});
    await page.evaluate(() => __atlas.goTo('cv_a_brachial_right'));
    await openCard();
    check((await page.locator('#sheet').innerText()).includes('Z-Anatomy'), 'Z-Anatomy provenance on the brachial artery card');
    check((await page.evaluate(() => __cvCheck.rays('cv_a_brachial_right'))).every(Boolean), 'BVH/native rays brachial artery');
    await page.evaluate(() => __atlas.setSide('left'));
    const left = await structs();
    check(left.find(s => s.id === 'cv_a_brachial_right').v === 0 && left.find(s => s.id === 'cv_a_brachial_left').v === 2, 'Side filter hides the right brachial artery');
    await page.evaluate(() => __atlas.setSide('both'));
    await page.evaluate(() => {__atlas.select(null); __atlas.goTo('cv_a_radial_left');}); await closeCard(); await page.waitForTimeout(500);
    await page.evaluate(() => __atlas.select(null)); await page.waitForTimeout(300);
    const radial = await page.evaluate(() => __cvCheck.clickPoint('cv_a_radial_left'));
    if (radial) {await page.mouse.click(radial.x, radial.y); check(await sel() === 'cv_a_radial_left', 'Canvas click selects the left radial artery');}
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-arm-vessels.png`)});
    await page.evaluate(async () => {await __atlas.enterSection('leg'); __atlas.setSub('all'); await __atlas.goTo('cv_a_femoral_left');});
    check(await sel() === 'cv_a_femoral_left', 'Femoral artery selected in the leg section');
    check(await page.locator('#tip').isHidden(), 'Hover label of the previous section cleared');
    await closeCard(); await page.waitForTimeout(500);
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-leg-vessels.png`)});
    // Cards without geometry stay explicit.
    await page.evaluate(async () => {await __atlas.enterSection('trunk'); await __atlas.goTo('cv_v_portal');});
    await openCard();
    check((await page.locator('#sheet').innerText()).includes('Отдельная принятая геометрия отсутствует'), 'Portal vein card states missing geometry');
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS/model errors: ' + errors.join(' | '));
    report.push({width, theme, status: 'passed', checks: checks.length, sectionLoadMs: timings, secondClickPart: point.seg});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Chromium/SwiftShader emulation; not a physical phone or GPU benchmark. Educational models, not anatomical acceptance.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
