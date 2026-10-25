// Reproducible section cost in one Chromium/SwiftShader environment (PERF-001): bytes fetched,
// section load time, registered triangles, JS heap, three.js memory and frame intervals while orbiting.
// The arm/leg sections are also measured without data-left-limb-muscles.js to isolate the cost of the
// 88 left muscles. CPU rasterisation: relative numbers only, not phone or GPU FPS.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'section-load-cost');
const PROBE = `window.__cost={mem:()=>({heap:performance.memory?.usedJSHeapSize??null,geometries:renderer.info.memory.geometries,triangles:[...structs.values()].reduce((n,s)=>n+s.meshes.reduce((k,m)=>k+(m.geometry.index?.count||m.geometry.attributes.position.count)/3,0),0),meshes:pickables.length}),
async orbit(){tween=null;const d=camera.position.clone().sub(controls.target),axis=new THREE.Vector3(0,1,0),f=[];let prev=performance.now();for(let i=0;i<60;i++){await new Promise(requestAnimationFrame);const now=performance.now();f.push(now-prev);prev=now;camera.position.copy(controls.target).add(d.clone().applyAxisAngle(axis,i*0.03));controls.update();requestRender();}f.shift();f.sort((a,b)=>a-b);return {medianMs:+f[f.length>>1].toFixed(1),p95Ms:+f[Math.floor(f.length*0.95)].toFixed(1)};}};\n`;
const server = http.createServer(async (req, res) => {
  const file = path.resolve(site, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (!file.startsWith(site + path.sep)) {res.writeHead(403).end(); return;}
  try {
    let body = await fs.readFile(file);
    if (file.endsWith('local.html')) body = Buffer.from(body.toString().replace('window.__atlas =', PROBE + 'window.__atlas ='));
    res.setHeader('Content-Type', file.endsWith('.html') ? 'text/html; charset=utf-8' : file.endsWith('.js') ? 'text/javascript' : 'application/octet-stream');
    res.end(body);
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(8801, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-precise-memory-info']});
const rows = [];
try {
  for (const [sec, withoutLeft] of [['head', false], ['neck', false], ['trunk', false], ['arm', false], ['arm', true], ['leg', false], ['leg', true]]) {
    const page = await browser.newPage({viewport: {width: 1280, height: 860}, deviceScaleFactor: 1});
    page.setDefaultTimeout(120000);
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    if (withoutLeft) await page.route(/data-left-limb-muscles\.js/, r => r.fulfill({body: '', contentType: 'text/javascript'}));
    let bytes = 0;
    page.on('response', async r => {try {bytes += (await r.body()).length;} catch {}});
    await page.goto('http://127.0.0.1:8801/local.html', {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => window.__ready === true);
    await page.waitForTimeout(300);
    const before = bytes, base = await page.evaluate(() => __cost.mem());
    const t0 = Date.now();
    await page.evaluate(async s => {await __atlas.enterSection(s); __atlas.setSub('all');}, sec);
    const loadMs = Date.now() - t0;
    await page.waitForTimeout(800);
    const after = await page.evaluate(() => __cost.mem());
    const frames = await page.evaluate(() => __cost.orbit());
    rows.push({sec, withoutLeftMuscles: withoutLeft, sectionBytes: bytes - before, loadMs, triangles: after.triangles, meshes: after.meshes,
      heapMB: after.heap && +(after.heap / 1048576).toFixed(1), heapDeltaMB: after.heap && +((after.heap - base.heap) / 1048576).toFixed(1),
      geometries: after.geometries, frames});
    console.log(JSON.stringify(rows.at(-1)));
    await page.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('section-cost.json', {rows, scope: 'Chromium headless shell, SwiftShader CPU rasteriser, 1280x860, DPR 1; relative cost only, not device FPS.'});
}
