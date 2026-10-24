// Execute the actual atlas frameBox function; verify projected corners at camera poles.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import * as THREE from 'three';
// Load the pure production helper without resolving browser import-map dependencies in Node.
const controlsSource=await fs.readFile('site/atlas-controls.js','utf8');
const {framingBasis}=await import('data:text/javascript,'+encodeURIComponent(controlsSource.slice(controlsSource.indexOf('export function framingBasis'))));
const html=await fs.readFile('site/index.html','utf8');
const source=html.slice(html.indexOf('function frameBox('),html.indexOf('// how much context to keep'));
const checks=[];
for(const width of [1280,390])for(const xyz of [[0,-1,0],[0,1,0],[0,0,1],[1,0,0],[1,.3,-1],[0,-1,1e-10]]) {
 const camera=new THREE.PerspectiveCamera(35,width/900,.001,10), target=new THREE.Vector3();
 const controls={target,maxDistance:10,update(){camera.lookAt(this.target);camera.updateMatrixWorld(true);}};
 const dir=new THREE.Vector3(...xyz).normalize(),box=new THREE.Box3(new THREE.Vector3(-.06,-.04,-.05),new THREE.Vector3(.06,.04,.05));
 const create=Function('THREE','framingBasis','camera','controls','freeArea',`let tween=null,occDirty=false;const reduceMotion=false,requestRender=()=>{};${source};return frameBox;`);
 const fit=create(THREE,framingBasis,camera,controls,{w:width,h:900,W:width,H:900});
 fit(box,dir,true,.08);
 const basis=framingBasis(dir);assert.ok(Math.abs(basis.right.dot(dir))<1e-8&&Math.abs(basis.up.dot(dir))<1e-8);
 assert.ok(Math.abs(basis.right.length()-1)<1e-8&&Math.abs(basis.up.length()-1)<1e-8);
 for(let i=0;i<8;i++){
  const p=new THREE.Vector3(i&1?box.max.x:box.min.x,i&2?box.max.y:box.min.y,i&4?box.max.z:box.min.z).project(camera);
  assert.ok(Math.abs(p.x)<=1&&Math.abs(p.y)<=1&&p.z<1,`${width} ${xyz}: corner outside frame`);
 }
 checks.push({width,direction:xyz,distance:camera.position.length(),projectedCorners:8});
}
await fs.writeFile(path.join(process.argv[2],'node-framing.json'),JSON.stringify({passed:checks.length,checks},null,2),{flag:'wx'});
console.log(JSON.stringify({passed:checks.length}));
