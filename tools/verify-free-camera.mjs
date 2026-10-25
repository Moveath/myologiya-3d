// Free camera: toggle, on-screen buttons, keyboard, look/strafe/pinch gestures, wheel, picking while
// flying, exit back to orbit without a jump, Escape/home exit and layout at 1280/390 in both themes.
// Real Chromium + r170 with SwiftShader; evidence goes to a new run only.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'free-camera-ui');
const PROBE = `window.__flyCheck={clickPoint(id){const r=canvas.getBoundingClientRect();for(let y=inset.top+25;y<r.height-inset.bottom-15;y+=8)for(let x=15;x<r.width-inset.right-15;x+=8){if(document.elementFromPoint(r.left+x,r.top+y)!==canvas)continue;const hit=hitAt(r.left+x,r.top+y);if(hit?.sid===id)return {x:r.left+x,y:r.top+y};}return null;}};
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
await new Promise(resolve => server.listen(8793, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const sub = (a, b) => a.map((v, i) => v - b[i]);
const len = v => Math.hypot(...v);
const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);
const unit = v => v.map(x => x / len(v));
const dirOf = v => unit(sub(v.target, v.position));
const angle = (a, b) => Math.acos(Math.min(1, Math.max(-1, dot(a, b)))) * 180 / Math.PI;
const report = [];
try {
  for (const [width, theme, region] of [[1280, 'light', 'arm'], [390, 'dark', 'head']]) {
    const mobile = width === 390;
    const context = await browser.newContext({viewport: {width, height: mobile ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme,
      reducedMotion: 'reduce', hasTouch: mobile});
    const page = await context.newPage(), errors = [], checks = [];
    const cdp = mobile ? await context.newCDPSession(page) : null;
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(8000);
    const check = (ok, label) => {assert.ok(ok, `${width}/${region}: ${label}`); checks.push(label);};
    const view = () => page.evaluate(() => __atlas.view());
    // wait, in rendered frames, until the glide after a release has stopped (SwiftShader frames are slow)
    const settle = async () => assert.ok(await page.evaluate(async () => {
      const frame = () => new Promise(resolve => requestAnimationFrame(() => resolve()));
      for (let i = 0; i < 600 && __atlas.view().moving; i++) await frame();
      await frame(); await frame();
      return !__atlas.view().moving;
    }), `${width}: camera did not settle`);
    const touch = async (type, points) => cdp.send('Input.dispatchTouchEvent', {type, touchPoints: points.map(([x, y], id) => ({x, y, id}))});
    // finger or mouse drag in steps, so pointermove events stream like a real gesture
    const drag = async (from, delta, {button = 'left', fingers = 1, pinch = 0} = {}) => {
      // a pinch spreads both fingers symmetrically, so their centre follows only the drag
      const pts = t => Array.from({length: fingers}, (_, i) => [from[0] + delta[0] * t + (fingers > 1 ? (i ? 60 + pinch * t / 2 : -pinch * t / 2) : 0), from[1] + delta[1] * t]);
      if (mobile) {
        await touch('touchStart', pts(0));
        for (let i = 1; i <= 8; i++) await touch('touchMove', pts(i / 8));
        await touch('touchEnd', []);
      } else {
        await page.mouse.move(...from); await page.mouse.down({button});
        for (let i = 1; i <= 8; i++) await page.mouse.move(from[0] + delta[0] * i / 8, from[1] + delta[1] * i / 8);
        await page.mouse.up({button});
      }
      await settle();
    };
    const holdButton = async (name, ms) => {
      const box = await page.locator(`#flyPad [data-fly="${name}"]`).boundingBox(), at = [box.x + box.width / 2, box.y + box.height / 2];
      if (mobile) {await touch('touchStart', [at]); await page.waitForTimeout(ms); await touch('touchEnd', []);}
      else {await page.mouse.move(...at); await page.mouse.down(); await page.waitForTimeout(ms); await page.mouse.up();}
      await settle();
    };
    const toggle = async () => {
      if (mobile) await page.locator('#bOptions').click();
      await page.locator('#bFly').click();
    };
    const started = Date.now();
    await page.goto(`http://127.0.0.1:8793/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});
    await page.evaluate(async r => {await __atlas.enterSection(r); __atlas.setSub('all');}, region);
    await settle();
    check((await view()).orbit && !(await view()).fly && await page.locator('#flyPad').isHidden(), 'Orbit camera by default; pad hidden');

    await toggle();
    let v = await view();
    check(v.fly && !v.orbit && await page.locator('#bFly').getAttribute('aria-pressed') === 'true' && await page.locator('#flyPad').isVisible(), 'Toggle enables free camera and pad');
    if (mobile) check(await page.locator('#app').getAttribute('data-options-open') === 'false', 'Mobile options panel closes on toggle');
    const pad = await page.locator('#flyPad').boundingBox(), blocker = await page.locator(mobile ? '#mobileCard' : '#sheet').boundingBox();
    check(!blocker || pad.y + pad.height <= blocker.y || pad.x + pad.width <= blocker.x, 'Pad does not cover the card');
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');

    for (const [name, sign] of [['up', 1], ['down', -1]]) {
      const a = await view(); await holdButton(name, 600); const b = await view();
      const dp = sub(b.position, a.position), dt = sub(b.target, a.target);
      check(sign * dp[1] > 1e-3 && Math.abs(dp[0]) < 1e-6 && Math.abs(dp[2]) < 1e-6 && len(sub(dp, dt)) < 1e-7,
        `Button ${name} moves camera and target vertically (${dp.map(x => x.toExponential(2))}; target diff ${len(sub(dp, dt)).toExponential(1)})`);
    }
    {
      const a = await view(); await holdButton('forward', 600); const b = await view(), dp = sub(b.position, a.position);
      check(len(dp) > 1e-3 && dot(unit(dp), dirOf(a)) > 0.999 && angle(dirOf(a), dirOf(b)) < 1e-3,
        `Button forward moves along the view (${len(dp).toFixed(4)} m, cos ${dot(unit(dp), dirOf(a)).toFixed(5)}, turn ${angle(dirOf(a), dirOf(b)).toExponential(2)}°)`);
    }
    if (!mobile) {
      const a = await view(); await page.keyboard.down('KeyD'); await page.waitForTimeout(600); await page.keyboard.up('KeyD'); await settle();
      const b = await view(), dp = sub(b.position, a.position), d = dirOf(a), right = unit([-d[2], 0, d[0]]);
      check(len(dp) > 1e-3 && dot(unit(dp), right) > 0.999, `Key D strafes right in the horizontal plane (${len(dp).toFixed(4)} m, cos ${dot(unit(dp), right).toFixed(5)})`);
      const c = await view(); await page.keyboard.down('KeyE'); await page.waitForTimeout(600); await page.keyboard.up('KeyE'); await settle();
      check((await view()).position[1] - c.position[1] > 1e-3, 'Key E moves up');
      await page.locator('#q').evaluate(el => el.closest('#drawer').hidden = false);
      await page.locator('#q').focus(); const e = await view();
      await page.keyboard.down('KeyW'); await page.waitForTimeout(300); await page.keyboard.up('KeyW'); await page.waitForTimeout(500);
      check(len(sub((await view()).position, e.position)) < 1e-9 && await page.locator('#q').inputValue() === 'w', 'Typing in search does not fly');
      await page.locator('#q').fill(''); await page.evaluate(() => {document.getElementById('drawer').hidden = true; document.activeElement.blur();});
      const w = await view(); await page.mouse.move(640, 450); await page.mouse.wheel(0, -300); await settle();
      const dw = sub((await view()).position, w.position);
      check(len(dw) > 1e-3 && dot(unit(dw), dirOf(w)) > 0.999, 'Wheel moves forward along the view');
    }
    const free = mobile ? [195, 330] : [420, 420];
    {
      const a = await view(); await drag(free, [120, 0]); const b = await view();
      check(len(sub(b.position, a.position)) < 1e-9 && angle(dirOf(a), dirOf(b)) > 5 && Math.abs(dirOf(a)[1] - dirOf(b)[1]) < 1e-6, 'Horizontal drag looks around in place');
    }
    {
      const a = await view(); await drag(free, [0, -80], {button: 'right', fingers: mobile ? 2 : 1}); const b = await view();
      check(b.position[1] - a.position[1] < -1e-3 && angle(dirOf(a), dirOf(b)) < 1e-3, (mobile ? 'Two-finger' : 'Right-button') + ' drag up moves the camera down, view kept');
    }
    if (mobile) {
      const a = await view(); await drag([150, 330], [0, 0], {fingers: 2, pinch: 120}); const b = await view(), dp = sub(b.position, a.position);
      check(len(dp) > 1e-3 && dot(unit(dp), dirOf(a)) > 0.99, 'Pinch out moves forward');
    }

    const id = region === 'arm' ? 'humerus' : 'masseter_right';
    await page.evaluate(async id => {await __atlas.goTo(id); __atlas.select(null);}, id); await settle();
    check((await view()).fly, 'Framing a structure keeps the free camera');
    if (mobile && await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();
    const point = await page.evaluate(id => __flyCheck.clickPoint(id), id); check(!!point, 'Ray point while flying');
    if (mobile) await page.touchscreen.tap(point.x, point.y); else await page.mouse.click(point.x, point.y);
    check(await page.evaluate(() => __atlas.state.sel) === id, 'Tap/click still selects while flying');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-${region}-fly.png`)});
    if (!mobile) {
      await page.locator('#sheet #bIso').focus(); const a = await view();
      await page.keyboard.down('ArrowDown'); await page.waitForTimeout(300); await page.keyboard.up('ArrowDown'); await settle();
      check(len(sub((await view()).position, a.position)) < 1e-9, 'Arrow keys inside the card stay with the card');
      await page.keyboard.down('KeyW'); await page.waitForTimeout(400); await page.keyboard.up('KeyW'); await settle();
      check(len(sub((await view()).position, a.position)) > 1e-3, 'Letter keys fly while the card has focus');
    }

    if (mobile && await page.locator('#app').getAttribute('data-card-open') === 'true') await page.locator('#closeMobileCard').click();
    const before = await view(); await page.locator('#bFlyExit').click(); const after = await view();
    check(after.orbit && !after.fly && await page.locator('#flyPad').isHidden() && await page.locator('#bFly').getAttribute('aria-pressed') === 'false', 'Exit restores orbit camera');
    check(len(sub(after.position, before.position)) < 1e-6 && angle(dirOf(before), dirOf(after)) < 0.05, 'Exit keeps the view without a jump');
    {
      const a = await view(); await drag(free, [100, 0]); const b = await view();
      check(len(sub(b.position, a.position)) > 1e-3 && Math.abs(len(sub(b.position, b.target)) - len(sub(a.position, a.target))) < 1e-4, 'Orbit drag works again around the new centre');
    }
    await page.evaluate(() => {__atlas.select(null); __atlas.setFly(true);});
    await page.keyboard.press('Escape');
    check(!(await view()).fly, 'Escape leaves the free camera when nothing is selected');
    await page.evaluate(() => {__atlas.setFly(true); __atlas.showHome();});
    check(!(await view()).fly && (await view()).orbit, 'Home screen leaves the free camera');
    check(!errors.length, 'No JS errors: ' + errors.join(' | '));
    report.push({width, theme, region, status: 'passed', checks: checks.length, durationMs: Date.now() - started});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Desktop mouse/keyboard and mobile CDP touch emulation with SwiftShader; not a physical phone or GPU benchmark.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
