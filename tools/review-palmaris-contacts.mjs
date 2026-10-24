// Measure contact distribution on the existing, unchanged trial GLB.
// Open context surfaces prohibit interpreting parity as a reliable tissue volume.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {BufferGeometry,BufferAttribute,Matrix4,Vector3,Line3,Ray,DoubleSide,Mesh,MeshBasicMaterial,Raycaster} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
import {pairKind} from './audit-self-intersections.mjs';
const [build,run]=process.argv.slice(2),checks=[],start=Date.now();
const check=(v,n)=>{assert.ok(v,n);checks.push(n);};
const deadline=()=>{if(Date.now()-start>45000)throw Error('Contact review exceeded 45 seconds');};
const write=(n,v)=>fs.writeFile(run+'/'+n,JSON.stringify(v,null,2),{flag:'wx'});
globalThis.ProgressEvent??=class{constructor(t,i){Object.assign(this,i);}};
const spec=JSON.parse(await fs.readFile(build+'/recipe.json'));
const context=JSON.parse(await fs.readFile(spec.source_context));
const bytes=await fs.readFile(build+'/palmaris_brevis-trial.glb');
const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
gltf.scene.updateMatrixWorld(true);const meshes=[];gltf.scene.traverse(m=>{if(m.isMesh)meshes.push(m)});
check(meshes.length===1,'One saved PB mesh');
const g=meshes[0].geometry.clone().applyMatrix4(meshes[0].matrixWorld),before=Array.from(g.index.array);
g.boundsTree=new MeshBVH(g,{indirect:true});
check(JSON.stringify(before)===JSON.stringify(Array.from(g.index.array)),'Indirect BVH keeps source face order');
const p=g.attributes.position,origin=new Vector3(...spec.frame.origin_m),basis=spec.frame.basis_columns;
const local=v=>{const d=v.clone().sub(origin).multiplyScalar(1000);return [0,1,2].map(i=>d.x*basis[0][i]+d.y*basis[1][i]+d.z*basis[2][i]);};
const dirs=[new Vector3(1,.37,.13).normalize(),new Vector3(.19,1,.43).normalize(),new Vector3(.31,.17,1).normalize()];
const contacts=[];
for(const row of context.filter(r=>spec.support_ids.includes(r.id))){
 const target=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(row.positions),3));target.setIndex(row.indices);
 const bvh=new MeshBVH(target,{indirect:true}),faces=new Set(),segments=[],counts={crossing:0,coplanarOverlap:0,contact:0};
 const line=new Line3();
 g.boundsTree.bvhcast(bvh,new Matrix4(),{intersectsTriangles(a,b,ia,ib){
  deadline();const kind=pairKind(a,b);if(kind in counts)counts[kind]++;
  if(kind==='crossing'||kind==='coplanarOverlap'){
   faces.add(g.boundsTree.resolveTriangleIndex(ia));
   if(kind==='crossing'&&a.intersectsTriangle(b,line,true))segments.push([line.start.toArray(),line.end.toArray()]);
  }return false;
 }});
 const samples=[];
 for(let i=0;i<p.count+g.index.count/3;i++){
  deadline();let v=new Vector3();
  if(i<p.count)v.fromBufferAttribute(p,i);
  else for(let k=0;k<3;k++)v.add(new Vector3().fromBufferAttribute(p,g.index.getX((i-p.count)*3+k))).multiplyScalar(k===2?1/3:1);
  const votes=dirs.map(d=>{const hits=bvh.raycast(new Ray(v,d),DoubleSide,1e-8).map(h=>h.distance).sort((a,b)=>a-b);return hits.filter((x,j)=>j===0||x-hits[j-1]>1e-7).length%2;});
  if(votes.some(Boolean)){
   const near=bvh.closestPointToPoint(v);samples.push({kind:i<p.count?'vertex':'face_centroid',index:i<p.count?i:i-p.count,votes,nearestSurfaceMM:near.distance*1000,position:v.toArray(),localMM:local(v)});
  }
 }
 const unanimous=samples.filter(s=>s.votes.every(Boolean));
 const rowResult={id:row.id,counts,crossingFaces:[...faces],segments,
   parityDiagnostic:{sampleCount:p.count+g.index.count/3,unanimousOdd:unanimous.length,disagreement:samples.length-unanimous.length,
    maxUnanimousNearestSurfaceMM:Math.max(0,...unanimous.map(s=>s.nearestSurfaceMM)),
    examples:unanimous.sort((a,b)=>b.nearestSurfaceMM-a.nearestSurfaceMM).slice(0,8),
    limitation:'Context meshes are open. Odd parity and nearest distances are diagnostics, not validated inside classifications or penetration maxima.'}};
 contacts.push(rowResult);await write('contacts-'+row.id+'.json',rowResult);
 check(true,'Bounded contact/parity review: '+row.id);target.dispose();
}
// Addressed regression: original r170 raycaster and indirect BVH agree.
const mesh=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));mesh.updateMatrixWorld();
for(let i=0;i<8;i++){
 const f=i*379%3296,a=new Vector3(),normal=new Vector3();
 for(let k=0;k<3;k++){const ix=g.index.getX(f*3+k);a.add(new Vector3().fromBufferAttribute(p,ix));normal.add(new Vector3().fromBufferAttribute(g.attributes.normal,ix));}
 a.multiplyScalar(1/3);normal.normalize();const ray=new Raycaster(a.clone().addScaledVector(normal,.03),normal.negate()),native=[],fast=[];
 Mesh.prototype.raycast.call(mesh,ray,native);acceleratedRaycast.call(mesh,ray,fast);native.sort((a,b)=>a.distance-b.distance);fast.sort((a,b)=>a.distance-b.distance);
 check(native.length>0&&native.length===fast.length&&Math.abs(native[0].distance-fast[0].distance)<1e-7&&native[0].faceIndex===fast[0].faceIndex,'Native/BVH addressed ray '+i);
}
await write('contact-review.json',{status:'passed',checks,elapsedMS:Date.now()-start,anatomicalAdmission:false,
 source:build+'/palmaris_brevis-trial.glb',geometry:{positions:Array.from(p.array),indices:before},contacts});
console.log(JSON.stringify({checks:checks.length,elapsedMS:Date.now()-start,contacts:contacts.map(r=>({id:r.id,counts:r.counts,faces:r.crossingFaces.length,parity:r.parityDiagnostic}))}));
