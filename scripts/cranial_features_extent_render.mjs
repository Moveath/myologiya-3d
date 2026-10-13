// Whole-bone inspection of actual source meshes. No inferred anatomy or edits.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {chromium} from '../tools/node_modules/playwright/index.mjs';
const root=path.resolve(import.meta.dirname,'..');
const out=path.join(root,'build_head/cranial_extent');await fs.mkdir(out,{recursive:true});
const halle=process.argv.includes('--halle');
const bones=halle?['specimen']:['frontal','occipital','sphenoid','ethmoid','parietal_right','parietal_left'];
const views={ant:{d:[0,0,1],up:[0,1,0]},post:{d:[0,0,-1],up:[0,1,0]},right:{d:[-1,0,0],up:[0,1,0]},left:{d:[1,0,0],up:[0,1,0]},sup:{d:[0,1,0],up:[0,0,-1]},inf:{d:[0,-1,0],up:[0,0,1]},oblique_front:{d:[-1,.4,1],up:[0,1,0]},oblique_back:{d:[1,.4,-1],up:[0,1,0]}};
if(halle){views.xminus=views.right;views.xplus=views.left;delete views.right;delete views.left;views.internal_base={d:[0,1,0],up:[0,0,-1],cut:{normal:[0,-1,0],constant:.105},zoomBox:[[.022,.022,.035],[.126,.105,.182]]};views.internal_base_oblique={d:[0,1,1],up:[0,1,0],cut:{normal:[0,-1,0],constant:.105},zoomBox:[[.022,.022,.035],[.126,.105,.182]]};}
const server=http.createServer(async(req,res)=>{const f=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!f.startsWith(root+path.sep)){res.writeHead(403).end();return;}try{res.setHeader('Content-Type',/\.html$/.test(f)?'text/html; charset=utf-8':/\.m?js$/.test(f)?'text/javascript':'application/octet-stream');res.end(await fs.readFile(f));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(8794,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'),args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:800,height:800}});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.route('https://cdn.jsdelivr.net/npm/**',route=>route.fulfill({path:path.join(root,'tools/node_modules',route.request().url().split('/npm/')[1].replace('three@0.170.0/','three/')),contentType:'text/javascript'}));
const hash=p=>fs.readFile(p).then(b=>crypto.createHash('sha256').update(b).digest('hex'));
const report={script:'scripts/cranial_features_extent_render.mjs',sources:{},records:[]};
try{
for(const [source,file] of Object.entries(halle?{halle:'site/skull-microct.glb'}:{bp:'build_head/head_hi.glb',z:'site/skull-z-detail.glb'})){
 report.sources[source]={file,sha256:await hash(path.join(root,file))};
 await page.goto('http://127.0.0.1:8794/build_head/cranial_features/pintool.html?f=/'+file);
 await page.waitForFunction(()=>window.__ready===true,{timeout:180000});
 for(const bone of bones)for(const [name,camera] of Object.entries(views)){
  const observation=await page.evaluate(({bone,camera,label})=>{window.clip(camera.cut?.normal||null,camera.cut?.constant||0);window.show([bone],camera,label,camera.zoomBox);const c=document.getElementById('ov').getContext('2d');c.clearRect(0,0,800,800);c.fillStyle='#fff';c.font='bold 18px sans-serif';c.fillText(label,15,28);const b=new window.THREE.Box3().setFromObject(window.__meshes[bone]);return {bounds:[b.min.toArray(),b.max.toArray()]};},{bone,camera,label:source+' / '+bone+' / '+name});
  const filename=`${source}_${bone}_${name}.png`;await page.screenshot({path:path.join(out,filename)});
  report.records.push({source,bone,view:name,camera,image:'build_head/cranial_extent/'+filename,sha256:await hash(path.join(out,filename)),...observation});
 }
 console.log(source,report.records.length,'views');
}
if(errors.length)throw new Error(errors.join('\n'));
await fs.writeFile(path.join(out,halle?'halle-views.json':'views.json'),JSON.stringify(report,null,2)+'\n');
}finally{await browser.close();server.close();}
