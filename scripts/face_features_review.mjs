// Local-only geometry inspection and landmark picking. No user browser profile.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from '../tools/node_modules/playwright/index.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const queue = path.resolve(root, process.env.ATLAS_REVIEW_QUEUE || 'build_head/face_features/jobs');
if (!queue.startsWith(root + path.sep)) throw new Error('Review output must stay inside this project');
const port = Number(process.env.ATLAS_REVIEW_PORT || 8777);
await fs.mkdir(queue, {recursive: true});
const server = http.createServer(async (req, res) => {
  const file = path.resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (!file.startsWith(root + path.sep)) {res.writeHead(403).end(); return;}
  try {
    const data = await fs.readFile(file);
    res.setHeader('Content-Type', file.endsWith('.html') ? 'text/html; charset=utf-8' : file.endsWith('.js') || file.endsWith('.mjs') ? 'text/javascript' : 'application/octet-stream');
    res.end(data);
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(port, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined, args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const page = await browser.newPage({viewport: {width: 800, height: 800}});
page.on('pageerror', e => console.error(e));
await page.route('https://cdn.jsdelivr.net/npm/**', route => {
  const part = route.request().url().split('/npm/')[1].replace('three@0.170.0/', 'three/');
  return route.fulfill({path: path.join(root, 'tools/node_modules', part), contentType: 'text/javascript'});
});
await page.goto('http://127.0.0.1:' + port + '/build_head/face_features/inspect.html' + (process.env.ATLAS_REVIEW_MODEL ? '?f=' + encodeURIComponent(process.env.ATLAS_REVIEW_MODEL) : ''));
await page.waitForFunction(() => window.__ready === true, {timeout: 180000});
console.log('Head geometry ready; jobs: qhead/*.job');
while (true) {
  const files = await fs.readdir(queue);
  if (files.includes('_STOP')) break;
  for (const filename of files.filter(x => x.endsWith('.job'))) {
    const full = path.join(queue, filename);
    const code = await fs.readFile(full, 'utf8');
    try {
      const result = await page.evaluate(code);
      await page.screenshot({path: full.replace(/\.job$/, '.png')});
      await fs.writeFile(full.replace(/\.job$/, '.out'), JSON.stringify(result));
      console.log('Completed', filename);
    } catch(e) {
      await fs.writeFile(full.replace(/\.job$/, '.out'), JSON.stringify({error: String(e)}));
    }
    await fs.unlink(full);
  }
  await new Promise(resolve => setTimeout(resolve, 100));
}
await browser.close();
server.close();
