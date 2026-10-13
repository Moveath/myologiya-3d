// Reproducible complete-bone views; no points, segmentation or inferred geometry.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {chromium} from '../tools/node_modules/playwright/index.mjs';
const root=path.resolve(import.meta.dirname,'..');
const out=path.join(root,'build_head/face_features');
const bones=['maxilla_right','maxilla_left','mandible','zygomatic_right','zygomatic_left','palatine_right','palatine_left','lacrimal_right','lacrimal_left','nasal_right','nasal_left','inferior_concha_right','inferior_concha_left','vomer'];
const views={ant:{d:[0,0,1],up:[0,1,0]},post:{d:[0,0,-1],up:[0,1,0]},right:{d:[-1,0,0],up:[0,1,0]},left:{d:[1,0,0],up:[0,1,0]},sup:{d:[0,1,0],up:[0,0,-1]},inf:{d:[0,-1,0],up:[0,0,1]},oblique_front:{d:[1,.4,1],up:[0,1,0]},oblique_back:{d:[-1,.4,-1],up:[0,1,0]}};
const server=http.createServer(async(req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}try{res.setHeader('Content-Type',/\.html$/.test(file)?'text/html; charset=utf-8':/\.m?js$/.test(file)?'text/javascript':'application/octet-stream');res.end(await fs.readFile(file));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(8788,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'),args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:800,height:800}});
page.on('pageerror',e=>{throw e;});
await page.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
const report={date:'2026-10-13',script:'scripts/face_features_extent_render.mjs',sources:{},records:[]};
try{
for(const [source,file]of Object.entries({bp:'build_head/head_hi.glb',z:'site/skull-z-detail.glb'})){
 report.sources[source]={file,sha256:crypto.createHash('sha256').update(await fs.readFile(path.join(root,file))).digest('hex')};
 await page.goto('http://127.0.0.1:8788/build_head/face_features/inspect.html?f=/'+file);
 await page.waitForFunction(()=>window.__ready===true,{timeout:180000});
 for(const bone of bones){
  const box=await page.evaluate(b=>window.bbox(b),bone);
  for(const [name,view]of Object.entries(views)){
   await page.evaluate(({bone,view,label})=>{window.show(bone,view,label);const c=document.getElementById('ov').getContext('2d');c.clearRect(0,0,800,800);c.fillStyle='#fff';c.font='bold 18px sans-serif';c.fillText(label,15,28);window._renderer.render(window._scene,window._cam);},{bone,view,label:source+' / '+bone+' / '+name});
   const filename=`extent_${source}_${bone}_${name}.png`;await page.screenshot({path:path.join(out,filename)});
   report.records.push({source,bone,view:name,camera:view,bounds:box,image:'build_head/face_features/'+filename,sha256:crypto.createHash('sha256').update(await fs.readFile(path.join(out,filename))).digest('hex')});
  }
  console.log(source,bone);
 }
 // Isolate an existing half only for visibility. The cut face is artificial and
 // is never a boundary of an anatomical feature or an exported new surface.
 for(const side of ['right','left']){
  const sign=side==='right'?-1:1;
  const box=await page.evaluate(()=>window.bbox('mandible'));
  const zoomBox=structuredClone(box);if(sign<0)zoomBox[1][0]=0;else zoomBox[0][0]=0;
  for(const [suffix,dy,dz]of [['medial_front',.15,.45],['medial_back',.15,-.35]]){
   const view={d:[-sign,dy,dz],up:[0,1,0]},name=side+'_'+suffix;
   await page.evaluate(({view,sign,zoomBox,label})=>{window._renderer.clippingPlanes=[new window.THREE.Plane(new window.THREE.Vector3(sign,0,0),0)];window.show('mandible',view,label,zoomBox);const c=document.getElementById('ov').getContext('2d');c.clearRect(0,0,800,800);c.fillStyle='#fff';c.font='bold 18px sans-serif';c.fillText(label,15,28);window._renderer.render(window._scene,window._cam);},{view,sign,zoomBox,label:source+' / mandible / '+name+' / visual cut x=0'});
   const filename=`extent_${source}_mandible_${name}.png`;await page.screenshot({path:path.join(out,filename)});
   report.records.push({source,bone:'mandible',view:name,camera:view,clipping:{normal:[sign,0,0],constant:0,artificialBoundary:true},bounds:zoomBox,image:'build_head/face_features/'+filename,sha256:crypto.createHash('sha256').update(await fs.readFile(path.join(out,filename))).digest('hex')});
  }
 }
}
await fs.writeFile(path.join(out,'extent-views.json'),JSON.stringify(report,null,2)+'\n');
}finally{await browser.close();server.close();}
