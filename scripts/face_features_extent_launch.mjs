// Diagnostic launch check: serves unchanged viewer behavior plus a read-only probe.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {chromium} from '../tools/node_modules/playwright/index.mjs';
const root=path.resolve(import.meta.dirname,'..'),out=path.join(root,'build_head/face_features');
const server=http.createServer(async(req,res)=>{let p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));try{let data=await fs.readFile(p);if(p.endsWith('skull-detail.html'))data=Buffer.from(data.toString().replace('window.__detail={','window.__faceProbe=()=>({bounds:[active.bounds.min.toArray(),active.bounds.max.toArray()],plane:{normal:clipPlane.normal.toArray(),constant:clipPlane.constant},camera:{position:camera.position.toArray(),up:camera.up.toArray()},only:state.only});window.__detail={'));res.setHeader('Content-Type',p.endsWith('.html')?'text/html; charset=utf-8':p.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(data);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(8798,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'),args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1280,height:900}});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
try{
await page.goto('http://127.0.0.1:8798/site/skull-detail.html?mode=z&part=mandible');
await page.waitForFunction(()=>window.__detail?.state.ready,{timeout:180000});
const initial=await page.evaluate(()=>window.__faceProbe());const cutValue=-initial.bounds[0][0]/(initial.bounds[1][0]-initial.bounds[0][0]);const records=[];
for(const reverse of [true,false]){
 await page.evaluate(({reverse,cutValue})=>{const a=window.__detail;a.state.only='mandible';a.state.colors=false;a.selectPart('mandible',true);a.setCut('sagittal',cutValue,reverse);a.frame({d:[reverse?1:-1,.15,.45],up:[0,1,0]},'mandible');},{reverse,cutValue});
 await page.waitForTimeout(500);
 const r=await page.evaluate(()=>window.__faceProbe());r.side=reverse?'right':'left';
 r.screenshot='build_head/face_features/extent_launch_mandible_'+r.side+'.png';
 await page.screenshot({path:path.join(root,r.screenshot)});
 r.screenshotSha256=crypto.createHash('sha256').update(await fs.readFile(path.join(root,r.screenshot))).digest('hex');
 r.cutMatchesReview=Math.abs(r.plane.constant)<1e-10 && r.plane.normal[0]===(reverse?-1:1);
 if(!r.cutMatchesReview)throw Error('Cut mismatch '+JSON.stringify(r));
 records.push(r);
}
const report={modelFile:'site/skull-z-detail.glb',modelSha256:crypto.createHash('sha256').update(await fs.readFile(path.join(root,'site/skull-z-detail.glb'))).digest('hex'),cutValue,initialBounds:initial.bounds,defaultHalfPlaneX:(initial.bounds[0][0]+initial.bounds[1][0])/2,file:'site/skull-detail.html',sha256:crypto.createHash('sha256').update(await fs.readFile(path.join(root,'site/skull-detail.html'))).digest('hex'),url:'skull-detail.html?mode=z&part=mandible',probe:'Read-only bounds/plane/camera accessor injected into served source; no functional viewer behavior changed.',reviewPlane:'x=0; normal [-1,0,0] for right, [1,0,0] for left',records,errors};
await fs.writeFile(path.join(out,'extent-launch-check.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await browser.close();server.close();}
