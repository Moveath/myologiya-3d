// Real Chromium touch input through CDP; mobile emulation, not a physical phone test.
// A read-only camera getter is injected into the served HTML for assertions.
// No application files, controls, gesture handlers, or camera state are changed.
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const site=path.join(root,'site'),shots=path.join(root,'shots/atlas-touch');
await fs.mkdir(shots,{recursive:true});
const sha=data=>crypto.createHash('sha256').update(data).digest('hex');
const sourceHashes={};
const probe=`window.__touchProbe=()=>({position:camera.position.toArray(),target:controls.target.toArray(),distance:camera.position.distanceTo(controls.target),zoom:camera.zoom,triangles:renderer.info.render.triangles,drawCalls:renderer.info.render.calls,contextLost:renderer.getContext().isContextLost()});\n`;
const server=http.createServer(async(req,res)=>{
 const file=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
 if(!file.startsWith(site+path.sep)){res.writeHead(403).end();return;}
 try{
  let data=await fs.readFile(file);
  if(['local.html','skull-detail.html'].includes(path.basename(file))){
   sourceHashes[path.basename(file)]=sha(data);
   const text=data.toString('utf8'),hook=path.basename(file)==='local.html'?'window.__atlas =':'window.__detail=';
   assert.equal(text.split(hook).length,2,'Read-only probe hook must occur once');
   data=Buffer.from(text.replace(hook,probe+hook));
  }
  res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.js')?'text/javascript':'application/octet-stream');res.end(data);
 }catch(error){res.writeHead(404).end(String(error));}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,executablePath:process.env.ATLAS_CHROMIUM||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const report={created_at:new Date().toISOString(),status:'running',method:'Chromium CDP Input.dispatchTouchEvent with hasTouch/isMobile; read-only camera instrumentation; no synthetic DOM events',limitation:'Mobile browser emulation at 390 × 844 CSS pixels, not a physical phone or Safari test.',sourceHashes,cases:[]};
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
const direction=s=>{const v=s.position.map((x,i)=>x-s.target[i]),n=Math.hypot(...v);return v.map(x=>x/n);};
async function snapshot(page){
 return page.evaluate(()=>({
  ...window.__touchProbe(),scroll:[scrollX,scrollY],viewportScale:visualViewport.scale,
  input:window.__touchInput,main:window.__atlas?{sec:__atlas.state.sec,selected:__atlas.state.sel}:null,
  detail:window.__detail?{mode:__detail.state.mode,selected:__detail.state.selected,ready:__detail.state.ready,visible:__detail.visibleIds()}:null,
  runtimeFailure:window.__atlasRuntime?.reason||null
 }));
}
async function settle(page){
 let previous=await snapshot(page),stable=0;
 for(let i=0;i<180;i++){
  await page.waitForTimeout(100);const current=await snapshot(page);
  stable=distance(previous.position,current.position)<5e-6&&distance(previous.target,current.target)<5e-6?stable+1:0;
  if(stable>=3)return current;previous=current;
 }
 throw Error('Camera did not settle after the gesture');
}
function healthy(state){
 assert.equal(state.contextLost,false);assert.equal(state.runtimeFailure,null);
 assert.ok(state.triangles>0&&state.drawCalls>0,'Model is still rendered');
 assert.ok(state.position.every(Number.isFinite)&&state.target.every(Number.isFinite));
 if(state.main)assert.equal(state.main.sec,'head');
 if(state.detail){assert.equal(state.detail.ready,true);assert.equal(state.detail.selected,'mandible');assert.ok(state.detail.visible.length>0);}
}
async function shot(page,name){
 const png=await page.screenshot({path:path.join(shots,name+'.png')});return {file:'shots/atlas-touch/'+name+'.png',sha256:sha(png)};
}
async function gesture(cdp,frames){
 const points=frame=>frame.map((p,i)=>({x:p[0],y:p[1],id:i+1,radiusX:3,radiusY:3,force:1}));
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:points(frames[0])});
 for(const frame of frames.slice(1)){
  await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:points(frame)});
  await new Promise(resolve=>setTimeout(resolve,25));
 }
 await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
}
try{
 for(const theme of ['light','dark'])for(const kind of ['main','detail']){
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1,colorScheme:theme,reducedMotion:'reduce'});
  await context.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
  const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(String(error)));
  await page.addInitScript(()=>{
   window.__touchInput={trustedTouchPointers:0,touchMoves:0,contextLost:0};
   for(const type of ['pointerdown','pointermove'])document.addEventListener(type,event=>{
    if(event.isTrusted&&event.pointerType==='touch'){if(type==='pointerdown')__touchInput.trustedTouchPointers++;else __touchInput.touchMoves++;}
   },{capture:true,passive:true});
   document.addEventListener('webglcontextlost',()=>__touchInput.contextLost++,{capture:true});
  });
  await page.goto(`${base}/${kind==='main'?'local.html':'skull-detail.html?mode=z&part=mandible&entry=local&theme='+theme}`);
  await page.waitForFunction(()=>window.__ready&&window.__touchProbe);
  if(kind==='main')assert.equal(await page.evaluate(()=>window.__atlas.enterSection('head')),true);
  else await page.waitForFunction(()=>window.__detail?.state.ready&&window.__detail.state.selected==='mandible');
  const initial=await settle(page);healthy(initial);
  assert.ok(await page.evaluate(()=>navigator.maxTouchPoints>0));
  const point=await page.evaluate(()=>{
   const canvas=document.querySelector('#stage'),r=canvas.getBoundingClientRect(),x=r.x+r.width/2;
   const rows=[];
   for(let y=Math.max(r.top+35,35);y<Math.min(r.bottom-35,innerHeight-35);y+=10){
    if([-90,-60,-30,0,30,60,90].every(dx=>[-15,0,15].every(dy=>document.elementFromPoint(x+dx,y+dy)===canvas)))rows.push({x,y});
   }
   rows.sort((a,b)=>Math.abs(a.y-(r.y+r.height/2))-Math.abs(b.y-(r.y+r.height/2)));
   return rows[0]||null;
  });
  assert.ok(point,'Enough exposed canvas for the one- and two-finger gestures');
  const name=`${kind}-390-${theme}`,images=[await shot(page,name+'-before')],cdp=await context.newCDPSession(page);
  const rotationFrames=Array.from({length:13},(_,i)=>[[point.x-50+i*100/12,point.y-10+i*20/12]]);
  await gesture(cdp,rotationFrames);const rotated=await settle(page);healthy(rotated);
  const rotationDelta=distance(direction(initial),direction(rotated));assert.ok(rotationDelta>.08,'One finger rotates the camera');
  assert.ok(Math.abs(rotated.distance/initial.distance-1)<.02,'One-finger rotation preserves the zoom distance');
  assert.deepEqual(rotated.scroll,initial.scroll);assert.equal(rotated.viewportScale,initial.viewportScale);
  images.push(await shot(page,name+'-rotated'));
  const pinchFrames=Array.from({length:13},(_,i)=>{const radius=28+i*42/12;return [[point.x-radius,point.y],[point.x+radius,point.y]];});
  await gesture(cdp,pinchFrames);const pinched=await settle(page);healthy(pinched);
  const zoomRatio=pinched.distance/rotated.distance;assert.ok(zoomRatio<.85,'Spreading two fingers zooms into the 3D scene');
  assert.deepEqual(pinched.scroll,initial.scroll);assert.equal(pinched.viewportScale,initial.viewportScale);
  assert.ok(pinched.input.trustedTouchPointers>=3&&pinched.input.touchMoves>=12,'Chromium delivered trusted touch pointers');
  assert.equal(pinched.input.contextLost,0);assert.deepEqual(errors,[]);
  if(pinched.detail)assert.deepEqual(pinched.detail.visible,initial.detail.visible);
  images.push(await shot(page,name+'-pinched'));
  assert.equal(new Set(images.map(image=>image.sha256)).size,3,'The rendered image changes after each gesture');
  report.cases.push({kind,theme,width:390,status:'passed',point,rotationDelta,zoomRatio,initial,rotated,pinched,images,errors});
  await context.close();
 }
 report.status='passed';
}catch(error){report.status='failed';report.error=String(error.stack||error);throw error;}
finally{
 await fs.writeFile(path.join(root,'verify/ui-atlas-touch-report.json'),JSON.stringify(report,null,2)+'\n');
 await browser.close();server.close();
}
console.log(JSON.stringify({status:report.status,cases:report.cases.map(({kind,theme,status,rotationDelta,zoomRatio})=>({kind,theme,status,rotationDelta,zoomRatio})),report:'verify/ui-atlas-touch-report.json'}));
