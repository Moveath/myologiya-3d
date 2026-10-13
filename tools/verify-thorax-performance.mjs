// Accuracy and interaction checks for the accelerator. No production debug hooks.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),site=path.join(root,'site');
const counters=`let perfFrames=0;const originalRender=renderer.render.bind(renderer);renderer.render=(...args)=>{perfFrames++;return originalRender(...args);};`;
const mainProbe=`window.__perfCheck={info:()=>({frames:perfFrames,ratio:renderer.getPixelRatio(),distance:camera.position.distanceTo(controls.target),triangles:renderer.info.render.triangles,models:Object.keys(models),pins:pinEls.length}),async compare(){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const meshes=pickables,functions=meshes.map(m=>m.raycast),results=[];for(const clip of [false]){state.headCut.active=clip;updateHeadCut();scene.updateMatrixWorld(true);for(const x of [-.5,0,.5])for(const y of [-.5,0,.5]){const cast=()=>{ray.setFromCamera(new THREE.Vector2(x,y),camera);return ray.intersectObjects(meshes,false).filter(h=>!pointClipped(h.point)).map(h=>({id:h.object.userData.sid,d:h.distance,face:h.faceIndex,p:h.point.toArray()}));};ray.firstHitOnly=false;const fast=cast();meshes.forEach(m=>m.raycast=THREE.Mesh.prototype.raycast);const slow=cast();meshes.forEach((m,i)=>m.raycast=functions[i]);if(fast.length!==slow.length)throw Error('Intersection count mismatch');for(let i=0;i<fast.length;i++){if(fast[i].id!==slow[i].id||Math.abs(fast[i].d-slow[i].d)>1e-7||fast[i].face!==slow[i].face)throw Error('Ray/face mismatch');}if(!clip){ray.firstHitOnly=true;const first=cast()[0];if(!!first!==!!slow[0]||first&&(first.id!==slow[0].id||Math.abs(first.d-slow[0].d)>1e-7))throw Error('Nearest hit mismatch');}results.push({clip,x,y,hits:fast.length});}}state.headCut.active=false;updateHeadCut();return results;}};\n`;
const detailProbe=`window.__perfCheck={info:()=>({frames:perfFrames,ratio:renderer.getPixelRatio(),triangles:renderer.info.render.triangles,bvh:active?[...active.parts.values()].flatMap(p=>p.meshes).filter(m=>m.geometry.boundsTree).length:0})};\n`;
const geometryAudit=`
export async function prepareRaycasts(root){
 const arrays=[];root.traverse(o=>{if(o.isMesh){for(const a of Object.values(o.geometry.attributes))arrays.push(a.array||a.data.array);if(o.geometry.index)arrays.push(o.geometry.index.array);}});
 const digest=async a=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(a.buffer,a.byteOffset,a.byteLength)))).join(',');
 const before=await Promise.all(arrays.map(digest));await prepareForTest(root);const after=await Promise.all(arrays.map(digest));
 if(before.some((hash,i)=>hash!==after[i]))throw Error('Geometry buffer changed');window.__geometryAudit=(window.__geometryAudit||0)+arrays.length;
}
`;
const server=http.createServer(async(req,res)=>{const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(site+path.sep))return res.writeHead(403).end();try{let data=await fs.readFile(file);const name=path.basename(file);if(name==='atlas-performance.js')data=Buffer.from(data.toString().replace('export async function prepareRaycasts(root)','async function prepareForTest(root)')+geometryAudit);if(['local.html','skull-detail.html'].includes(name)){let s=data.toString();s=s.replace('const renderQuality',counters+'\nconst renderQuality');const hook=name==='local.html'?'window.__atlas =':'window.__detail=';s=s.replace(hook,(name==='local.html'?mainProbe:detailProbe)+hook);data=Buffer.from(s);}if(name==='skull-education-model.js')data=Buffer.from(data.toString().replace(' const renderQuality',counters+`window.__educationPerf=()=>({frames:perfFrames,ratio:renderer.getPixelRatio()});\n const renderQuality`));res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(data);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={status:'running',method:'Software Chromium regression checks; no physical-device FPS claim.',cases:[],errors:[]};
const context=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
const page=await context.newPage();page.setDefaultTimeout(120000);page.on('pageerror',e=>report.errors.push(String(e)));await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:''}));
async function steady(fn=()=>__perfCheck.info()){let last;for(let n=0;n<80;n++){const value=await page.evaluate(fn);if(last?.frames===value.frames)return value;last=value;await page.waitForTimeout(150);}throw Error('Renderer did not settle');}
async function zoom(){const stage=page.locator('#stage'),box=await stage.boundingBox();await page.mouse.move(box.x+box.width*.4,box.y+box.height*.45);const ratios=[];for(let n=0;n<8;n++){await page.mouse.wheel(0,-36);await page.waitForTimeout(40);ratios.push((await page.evaluate(()=>__perfCheck.info())).ratio);}assert.ok(ratios.some(r=>r<=1.25));const final=await steady();assert.equal(final.ratio,3);return {movingRatios:ratios,settled:final};}
try{
 await page.goto(base+'/local.html');await page.waitForFunction(()=>window.__ready);
 await page.evaluate(()=>__atlas.enterSection('trunk'));await page.locator('#bOptions').click();await page.locator('[data-peel="3"]').click();await page.locator('#closeOptions').click();await steady();
 assert.deepEqual((await page.evaluate(()=>__perfCheck.info())).models,['trunk']);
 report.cases.push({name:'whole-thorax zoom',...await zoom()});
 await page.evaluate(()=>__atlas.goTo('rib_7_left'));await page.locator('#closeMobileCard').click();await steady();
 report.cases.push({name:'thorax ray equivalence',rays:await page.evaluate(()=>__perfCheck.compare()),unchangedBuffers:await page.evaluate(()=>__geometryAudit)});
 assert.deepEqual(report.errors,[]);report.status='passed';
}finally{await browser.close();server.close();await fs.writeFile(path.join(root,'verify/performance-thorax.json'),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify(report));
