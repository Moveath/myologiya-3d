// Lighting inputs of every registered mesh (BONES-MUSCLES-AUDIT): the shared lit materials need a
// normal attribute; register() derives it in memory for glTF files saved without NORMAL.
// Real atlas in Chromium/SwiftShader; isolated screenshots of every model whose file lacks NORMAL.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'mesh-normals');
// Published supplemental GLBs whose primitives have no NORMAL (read from the glTF JSON chunk only).
const sourceWithoutNormals = [];
for (const dir of await fs.readdir(path.join(site, 'models/bodyparts3d-3.0'))) {
  for (const name of (await fs.readdir(path.join(site, 'models/bodyparts3d-3.0', dir))).filter(n => n.endsWith('.glb'))) {
    const b = await fs.readFile(path.join(site, 'models/bodyparts3d-3.0', dir, name));
    const json = JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)).toString());
    if (json.meshes.some(m => m.primitives.some(p => !('NORMAL' in p.attributes)))) sourceWithoutNormals.push(name.slice(0, -4));
  }
}
const PROBE = `window.__normals=()=>[...structs.values()].flatMap(s=>s.meshes.map(m=>({id:s.id,kind:s.kind,normal:!!m.geometry.attributes.normal,flat:!!m.userData.mat.flatShading})));\n`;
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
await new Promise(resolve => server.listen(8796, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const report = [];
try {
  const page = await browser.newPage({viewport: {width: 1280, height: 900}, deviceScaleFactor: 1});
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
  page.setDefaultTimeout(60000);
  await page.goto('http://127.0.0.1:8796/local.html', {waitUntil: 'domcontentloaded'});
  await page.waitForFunction(() => window.__ready === true);
  for (const sec of ['head', 'neck', 'trunk', 'arm', 'leg']) {
    await page.evaluate(async s => {await __atlas.enterSection(s); __atlas.setSub('all');}, sec);
    const meshes = await page.evaluate(() => __normals());
    const missing = meshes.filter(m => !m.normal);
    const unlit = missing.filter(m => !m.flat);
    const shots = [...new Set([...missing.map(m => m.id), ...meshes.map(m => m.id).filter(id => sourceWithoutNormals.includes(id))])];
    for (const id of shots) {
      await page.evaluate(async id => {await __atlas.goTo(id);}, id);
      if (await page.locator('#bIso').isVisible()) await page.locator('#bIso').click();
      await page.waitForTimeout(800);
      await page.screenshot({path: path.join(run.dir, `${sec}-${id}.png`)});
      if (await page.locator('#bIso').isVisible()) await page.locator('#bIso').click();
    }
    report.push({sec, meshes: meshes.length, screenshots: shots, withoutNormals: [...new Set(missing.map(m => m.id))], withoutNormalsOrFlat: [...new Set(unlit.map(m => m.id))]});
  }
  assert.deepEqual(errors, []);
} finally {
  await browser.close(); server.close();
  await run.write('normals-report.json', {sourceWithoutNormals, report, scope: 'Chromium/SwiftShader; lighting inputs and screenshots, not GPU colour accuracy.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
assert.ok(report.every(r => !r.withoutNormals.length), 'Every registered mesh needs a normal attribute');
