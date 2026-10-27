// Textbook catalogue UI (CAT-STRUCTURE-TEXTBOOK): home tiles, region focus over the home screen, pair rows
// with side buttons, one row for muscles modelled in several sections, hyoid in the facial skull,
// placeholder groups, filters, "by group" bone colours and legend, Escape. 1280 light / 390 dark.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {createEvidenceRun} from './evidence-run.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site');
const run = await createEvidenceRun(root, 'catalogue-ui');
const PROBE = `window.__catalogueCheck={color:id=>structs.get(id)?.meshes[0]?.material.color.getHexString()};
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
await new Promise(resolve => server.listen(8795, '127.0.0.1', resolve));
const browser = await chromium.launch({headless: true, executablePath: process.env.ATLAS_CHROMIUM || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const report = [];
try {
  for (const [width, theme] of [[1280, 'light'], [390, 'dark']]) {
    const mobile = width === 390;
    const context = await browser.newContext({viewport: {width, height: mobile ? 844 : 900}, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: 'reduce'});
    const page = await context.newPage(), errors = [], checks = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => {if (m.type() === 'error' && !m.text().includes('net::ERR_FAILED')) errors.push(m.text());});
    await page.route('https://fonts.googleapis.com/**', r => r.fulfill({body: '', contentType: 'text/css'}));
    page.setDefaultTimeout(10000);
    const check = (ok, label) => {assert.ok(ok, `${width}: ${label}`); checks.push(label);};
    const state = () => page.evaluate(() => ({sec: __atlas.state.sec, sel: __atlas.state.sel}));
    const closeCard = async () => {if (mobile && await page.locator('#closeMobileCard').isVisible()) await page.locator('#closeMobileCard').click();};
    const listType = async t => page.locator(`[data-list-type="${t}"]`).click();
    const ids = () => page.locator('#dlist [data-id]').evaluateAll(xs => xs.map(x => x.dataset.id));
    const started = Date.now();
    await page.goto(`http://127.0.0.1:8795/local.html?theme=${theme}`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => window.__ready === true, null, {timeout: 60000});

    const tiles = await page.locator('#homeCatalogue [data-catalogue]').evaluateAll(xs => xs.map(x => [x.dataset.catalogue, x.classList.contains('soon')]));
    // ABD-MUSCLES (LOG-20261027-01): the abdomen tile has models now, so no textbook region is a placeholder.
    check(tiles.length === 13 && !tiles.some(([, soon]) => soon), 'Home shows 13 textbook regions, none of them a placeholder');
    await page.locator('#homeCatalogue').scrollIntoViewIfNeeded();
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-home-catalogue.png`)});
    await page.locator('[data-catalogue="upper-limb-bones"]').click();
    check(await page.locator('#drawer').isVisible() && await page.locator('#home').isVisible(), 'Region tile opens the catalogue over the home screen');
    check(await page.locator('#cat-upper-limb-bones').isVisible() && await page.locator('[data-list-type="bones"]').getAttribute('aria-pressed') === 'true', 'Region heading in view, bones filter on');
    check(await page.locator('[data-group="humerus"]').evaluate(d => d.open) && !(await page.locator('[data-group="neurocranium"]').evaluate(d => d.open)), 'Only the chosen region is expanded');
    const box = await page.locator('#drawer').boundingBox();
    check(await page.evaluate(([x, y]) => !!document.elementFromPoint(x, y)?.closest('#drawer'), [box.x + box.width / 2, box.y + box.height / 2]), 'Catalogue is on top of the home screen');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-region.png`)});
    await page.keyboard.press('Escape');
    check(await page.locator('#drawer').isHidden() && await page.locator('#home').isVisible(), 'Escape closes the catalogue back to the home screen');

    await page.locator('[data-catalogue="upper-limb-bones"]').click();
    await page.locator('[data-group="humerus"] .item[data-id="humerus"]').click();
    await page.waitForFunction(() => __atlas.state.sec === 'arm' && __atlas.state.sel === 'humerus');
    check(await page.locator('#home').isHidden() && await page.locator('#drawer').isHidden(), 'Choosing a row enters its section and selects it');
    await closeCard();

    await page.locator('#bList').click();
    check(await page.locator('#cat-upper-limb-bones').evaluate(h => {const a = h.getBoundingClientRect(), b = h.closest('#dlist').getBoundingClientRect(); return a.top >= b.top - 1 && a.top < b.top + 40;}),
      'List opens at the region of the open section');
    check((await page.locator('#sheet .kicker').first().innerText()).trim().toLowerCase() === 'кости верхней конечности', 'Card label follows the textbook catalogue');
    check(await page.locator('[data-group="hand-bones"]').evaluate(d => d.open) && (await page.locator('[data-group="hand-bones"] h3').allInnerTexts()).map(t => t.toLowerCase()).join('|') === 'кости запястья|пястные кости|фаланги пальцев|сесамовидные кости', 'Groups of the open section expanded; hand bones split by textbook parts');
    check(await page.locator('[data-group="forearm-bones"] .item-row').count() === 2 && await page.locator('[data-group="humerus"] .item-row').count() === 1, 'Humerus and forearm bones are separate groups, one row per pair');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-arm-list.png`)});
    await page.locator('#dlist .side[data-id="radius_left"]').click();
    await page.waitForFunction(() => __atlas.state.sel === 'radius_left');
    check(true, 'Side button opens the left bone'); await closeCard();

    await page.locator('#bList').click(); await listType('muscles'); await page.locator('#q').fill('трапец');
    const rows = await page.locator('#dlist .item-row .item b').allInnerTexts();
    check(rows.filter(t => /^Трапециевидная мышца$/i.test(t)).length === 1, 'Trapezius is listed once (was five records)');
    check(await page.locator('#dlist .item-alt [data-id="neck_trapezius_right"]').count() === 1 && await page.locator('#dlist .item-alt [data-id="trapezius"]').count() === 1, 'Its neck and arm models are offered as links');
    const muscleIds = await ids();
    check(muscleIds.length > 0 && await page.evaluate(xs => xs.every(id => !!ATLAS.muscles[id]), muscleIds), 'Muscles filter lists only muscles');
    await page.locator('#dlist .item-alt [data-id="trapezius"]').click();
    await page.waitForFunction(() => __atlas.state.sel === 'trapezius' && __atlas.state.sec === 'arm');
    check(true, 'Arm model of the trapezius opens from its link'); await closeCard();

    await page.locator('#bList').click(); await listType('bones'); await page.locator('#q').fill('подъязычн');
    check(await page.locator('[data-group="viscerocranium"] .item-row .item[data-id="hyoid"]').count() === 1, 'Hyoid is found in the facial skull group');
    const boneIds = await ids();
    check(boneIds.length > 0 && await page.evaluate(xs => xs.every(id => !!ATLAS.bones[id]), boneIds), 'Bones filter lists only bones');
    await page.locator('#q').fill(''); await listType('muscles');
    check((await page.locator('[data-group="abdomen-anterolateral"] .missing').textContent()).includes('поднимающая яичко') && (await page.locator('[data-group="abdomen-anterolateral"] summary small').textContent()) === '5' && (await page.locator('[data-group="abdomen-posterior"] summary small').textContent()) === '1', 'Abdomen groups list 5 + 1 muscles and name the cremaster gap');
    check(await page.locator('[data-group="perineum-other"] .missing').count() === 1 && await page.locator('[data-group="back-deep"] .missing').count() === 1, 'Perineum and back placeholders are shown');
    await listType('all');
    check(await page.locator('#dlist .item-row').count() === 307, 'Browsing all lists 307 rows for 579 bone and muscle records');
    await page.locator('#q').fill('ключица');
    check(await page.locator('#dlist .item-row').count() === 1, 'Search returns one row for a paired bone');
    await page.locator('#q').fill(''); await page.locator('#bCloseList').click();

    const color = id => page.evaluate(id => __catalogueCheck.color(id), id);
    const perBone = [await color('radius'), await color('ulna')];
    if (mobile) await page.locator('#bOptions').click();
    await page.locator('#bBoneGroups').click();
    if (mobile && await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();
    const grouped = {radius: await color('radius'), ulna: await color('ulna'), humerus: await color('humerus'), scaphoid: await color('scaphoid'), lunate: await color('lunate')};
    check(perBone[0] !== perBone[1] && grouped.radius === grouped.ulna && grouped.radius !== grouped.humerus && grouped.scaphoid === grouped.lunate && grouped.scaphoid !== grouped.radius,
      'By-group colours: forearm bones share a colour, carpals share another');
    if (mobile) await page.locator('#bOptions').click();
    await page.locator('#bBoneLegend').click();
    check(await page.locator('#boneLegend [data-bone-group="forearm-bones"] [data-color-bone]').count() === 2 && await page.locator('#boneLegend [data-bone-group="carpus"]').count() === 1, 'Legend lists catalogue groups with their bones');
    await page.screenshot({path: path.join(run.dir, `${width}-${theme}-group-colours.png`)});
    await page.locator('#bCloseBoneLegend').click();
    check(await page.evaluate(() => JSON.parse(localStorage.getItem('myo3d')).boneColorGroups) === true, 'Choice is remembered');
    if (mobile) await page.locator('#bOptions').click();
    await page.locator('#bBoneGroups').click();
    if (mobile && await page.locator('#closeOptions').isVisible()) await page.locator('#closeOptions').click();
    check(await color('radius') === perBone[0] && await color('ulna') === perBone[1], 'Switching back restores per-bone colours');
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No horizontal overflow');
    check(!errors.length, 'No JS errors: ' + errors.join(' | '));
    report.push({width, theme, status: 'passed', checks: checks.length, durationMs: Date.now() - started});
    await context.close();
  }
} finally {
  await browser.close(); server.close();
  await run.write('ui-report.json', {report, scope: 'Desktop and mobile emulation with SwiftShader; not a physical phone. Catalogue placement, not anatomical acceptance of models.'});
}
console.log(JSON.stringify({run: path.relative(root, run.dir), report}));
