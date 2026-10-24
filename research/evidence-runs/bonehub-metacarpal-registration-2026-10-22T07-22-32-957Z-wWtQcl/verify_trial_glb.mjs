import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as T from '../../../tools/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../../../tools/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {MeshBVH} from '../../../tools/node_modules/three-mesh-bvh/src/index.js';
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const run=path.dirname(fileURLToPath(import.meta.url)),checks=[];
function check(ok,name,details){checks.push({name,pass:!!ok,details});if(!ok)throw Error(name);}
for(const owner of ['metacarpal_1_left','metacarpal_3_left']){
 const bytes=await fs.readFile(path.join(run,owner+'-rigid-trial-v2.glb'));
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
 const meshes=[];gltf.scene.traverse(o=>{if(o.isMesh)meshes.push(o)});
 check(meshes.length===1,owner+' one mesh');const mesh=meshes[0],g=mesh.geometry;
 const ref=JSON.parse(await fs.readFile(path.join(run,owner+'-registered-arrays.json'),'utf8'));
 check(mesh.name==='b|'+owner,owner+' stable name',mesh.name);
 check(g.index.count===ref.faces.length,owner+' triangle count',g.index.count/3);
 check(g.index.array.every((x,i)=>x===ref.faces[i]),owner+' triangle indexing unchanged');
 const positions=g.attributes.position.array;let error=0;for(let i=0;i<positions.length;i++)error=Math.max(error,Math.abs(positions[i]-ref.vertices[i]));
 check(error<1e-7,owner+' float32 position tolerance',error);
 check(g.attributes.normal.array.every(Number.isFinite),owner+' finite normals');
 const before=Array.from(g.index.array);const bvh=new MeshBVH(g,{indirect:true,verbose:false});
 check(g.index.array.every((x,i)=>x===before[i]),owner+' BVH index preservation');
 g.computeBoundingSphere();mesh.material=new T.MeshBasicMaterial({side:T.DoubleSide});mesh.updateMatrixWorld(true);
 const c=g.boundingSphere.center,r=g.boundingSphere.radius;let hits=0;
 for(let i=0;i<12;i++){
  const d=new T.Vector3(Math.cos(i*2.399),Math.sin(i*2.399),((i+.5)/12)*2-1).normalize();
  const start=c.clone().addScaledVector(d,r*3),dir=c.clone().sub(start).normalize();
  const native=new T.Raycaster(start,dir).intersectObject(mesh)[0];const fast=bvh.raycastFirst(new T.Ray(start,dir),T.DoubleSide);
  check(!!native===!!fast,owner+' ray '+i+' hit parity');
  if(native){hits++;check(Math.abs(native.distance-fast.distance)<1e-8&&native.faceIndex===fast.faceIndex,owner+' ray '+i+' face/distance equality');}
 }
 check(hits>=8,owner+' enough actual ray hits',hits);
}
await fs.writeFile(path.join(run,'trial-glb-node-checks.json'),JSON.stringify({status:'passed',checks,claim:'Technical test-only GLB checks; no anatomical admission or production integration.'},null,2),{flag:'wx'});
console.log(JSON.stringify({status:'passed',checks:checks.length}));
