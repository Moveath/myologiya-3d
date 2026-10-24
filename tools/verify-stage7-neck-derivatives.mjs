// Targeted read-only checks; no global atlas geometry audit.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {BufferGeometry,BufferAttribute,Vector3,Ray,DoubleSide,Mesh,MeshBasicMaterial,Raycaster} from 'three';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
const run=process.argv[2],previous='research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT';
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const filter=process.argv[3]||'';
const records=JSON.parse(await fs.readFile(run+'/derivatives.json')).filter(r=>r.id.includes(filter));
const rows=JSON.parse(await fs.readFile(previous+'/context-arrays.json')).filter(r=>r.file==='neck'&&r.name.startsWith('b|'));
const context=rows.map(r=>{const g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(r.positions),3));g.setIndex(new BufferAttribute(new Uint32Array(r.indices),1));g.computeBoundingBox();return {...r,g,b:new MeshBVH(g,{indirect:true,verbose:false})};});
const results=[],checks=[];const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
for(const rec of records){
 const bytes=await fs.readFile(rec.file);check(crypto.createHash('sha256').update(bytes).digest('hex')===rec.sha256,rec.id+' hash');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');const meshes=[];gltf.scene.traverse(m=>{if(m.isMesh)meshes.push(m);});check(meshes.length===1,rec.id+' one owner');
 const g=meshes[0].geometry,p=g.attributes.position,n=g.attributes.normal;
 check(g.index.count/3===rec.triangles,rec.id+' triangle count');
 check([...n.array].every(Number.isFinite),rec.id+' finite normals');
 const nv=new Vector3();check(Array.from({length:n.count},(_,i)=>Math.abs(nv.fromBufferAttribute(n,i).length()-1)).every(e=>e<1e-6),rec.id+' unit normals');
 const index=g.index.array.slice(),positions=p.array.slice();g.boundsTree=new MeshBVH(g,{indirect:true,verbose:false});
 check(index.every((v,i)=>v===g.index.array[i])&&positions.every((v,i)=>v===p.array[i]),rec.id+' BVH preserves arrays');
 g.computeBoundingBox();g.computeBoundingSphere();const center=g.boundingSphere.center,radius=g.boundingSphere.radius;
 const mesh=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));mesh.updateMatrixWorld(true);
 let hits=0;for(const fraction of [.2,.4,.6,.8]){
  // Aim at an actual face; the bounding-sphere centre can be between bundles.
  const fi=Math.floor(fraction*rec.triangles)*3;
  const a=new Vector3().fromBufferAttribute(p,g.index.getX(fi)),b=new Vector3().fromBufferAttribute(p,g.index.getX(fi+1)),c=new Vector3().fromBufferAttribute(p,g.index.getX(fi+2));
  const target=a.clone().add(b).add(c).multiplyScalar(1/3),dir=b.clone().sub(a).cross(c.clone().sub(a)).normalize();
  const ray=new Raycaster(target.clone().addScaledVector(dir,radius*3),dir.clone().negate());
  mesh.raycast=Mesh.prototype.raycast;const native=ray.intersectObject(mesh);mesh.raycast=acceleratedRaycast;const fast=ray.intersectObject(mesh);
  check(native.length===fast.length&&native.every(h=>fast.some(f=>Math.abs(h.distance-f.distance)<1e-8&&h.faceIndex===f.faceIndex)),rec.id+' BVH ray '+fraction);hits+=fast.length;
 }
 check(hits>0,rec.id+' real ray hits');
 const sample=[];
 if(rec.id.startsWith('interspinales'))for(const target of context){
  if(!g.boundingBox.intersectsBox(target.g.boundingBox))continue;
  let inside=0,ambiguous=0,max=0;const dirs=[new Vector3(1,.37,.13).normalize(),new Vector3(.19,1,.43).normalize(),new Vector3(.31,.17,1).normalize()];
  const start=Date.now();for(let s=0;s<600;s++){
   check(Date.now()-start<8000,rec.id+' bounded depth');
   const v=new Vector3().fromBufferAttribute(p,Math.floor(s*p.count/600));
   const votes=dirs.map(d=>{const h=target.b.raycast(new Ray(v,d),DoubleSide,1e-8).map(h=>h.distance).sort((a,b)=>a-b);return h.filter((x,j)=>j===0||x-h[j-1]>1e-7).length%2;});
   if(votes.some(x=>x!==votes[0]))ambiguous++;
   if(votes.filter(Boolean).length>=2){inside++;max=Math.max(max,target.b.closestPointToPoint(v).distance);}
  }
  if(inside||ambiguous)sample.push({target:target.name,inside,ambiguous,samples:600,maxSampleDepthMM:max*1000});
 }
 results.push({id:rec.id,triangles:rec.triangles,hits,sampledBoneOverlap:sample});
 // Evidence is saved after each model, including a failed later batch.
 await fs.writeFile(run+'/node-'+rec.id+'.json',JSON.stringify(results.at(-1),null,2),{flag:'wx'});
}
const unique=[...new Set(checks)];await fs.writeFile(run+'/node-derivatives'+(filter?'-'+filter:'')+'.json',JSON.stringify({passed:unique.length,checks:unique,results,note:'Three-ray majority / 600 vertices is a surface sample; not an exact penetration bound or anatomical acceptance.'},null,2),{flag:'wx'});
console.log(JSON.stringify({passed:unique.length,results}));
