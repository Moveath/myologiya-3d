import {chromium} from '../tools/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';import path from 'node:path';
const b=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe')});
const p=await b.newPage({viewport:{width:1024,height:1024}});
for(const name of ['Maxilla','Palatine']){const a=await fs.readFile('research/cache/face/'+name+'_Medial_background.svg'),c=await fs.readFile('research/cache/face/'+name+'_Medial_markup.svg');await p.setContent(`<style>img{position:absolute;inset:0;width:1024px}body{background:white}</style><img src="data:image/svg+xml;base64,${a.toString('base64')}"><img src="data:image/svg+xml;base64,${c.toString('base64')}">`);await p.screenshot({path:'research/cache/face/'+name+'_reference.png'});}await b.close();
