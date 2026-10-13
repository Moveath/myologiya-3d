// Targeted inspection of unchanged, previously acquired open source skulls.
// Camera framing boxes are not landmark coordinates or anatomical evidence.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {chromium} from '../tools/node_modules/playwright/index.mjs';
const root=path.resolve(import.meta.dirname,'..');
const out=path.join(root,'build_head/cranial_extent/other-orbits');
await fs.mkdir(out,{recursive:true});
const source='research/cache/new-skull/review.glb';
const nodes={
 '01_male-cranial_maxilla':[[.195,1.748,-.17],[.30,1.808,-.095]],
 '02_female-cranial_maxilla':[[.185,1.600,-.19],[.285,1.670,-.125]],
 'nih-002448':[[-.06,-.020,.020],[.06,.058,.098]]
};
const views={anterior:{d:[0,0,1],up:[0,1,0]},inferior_anterior:{d:[0,-.5,1],up:[0,1,0]},xminus_oblique:{d:[-.32,-.45,1],up:[0,1,0]},xplus_oblique:{d:[.32,-.45,1],up:[0,1,0]}};
const hash=async file=>crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
const report={script:'scripts/cranial_features_variant_check.mjs',source,sourceSha256:await hash(path.join(root,source)),target:'A02.1.03.024',geometryEdits:false,records:[]};
const browser=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'),args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:800,height:800}});
 await page.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
 await page.goto('http://127.0.0.1:8797/build_head/pintool.html?f=../'+source);
 await page.waitForFunction(()=>window.__ready===true,{timeout:180000});
 for(const [node,zoomBox] of Object.entries(nodes))for(const [name,camera] of Object.entries(views)){
  await page.evaluate(({node,camera,zoomBox,name})=>{window.show(node,camera,node+' / orbit region / '+name,zoomBox);},{node,camera,zoomBox,name});
  const filename=node+'-'+name+'.png';await page.screenshot({path:path.join(out,filename)});
  report.records.push({node,camera,zoomBox,name,screenshot:'build_head/cranial_extent/other-orbits/'+filename,screenshotSha256:await hash(path.join(out,filename))});
 }
 await fs.writeFile(path.join(out,'views.json'),JSON.stringify(report,null,2)+'\n');
 console.log(report.records.length,'source views saved');
}finally{await browser.close();}
