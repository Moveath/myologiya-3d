// Addressed comparison: one new reflected group against two unchanged baselines.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {BufferGeometry,BufferAttribute,Vector3,Ray,DoubleSide,Mesh,MeshBasicMaterial,Raycaster,Matrix4} from 'three';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
const run=process.argv[2], rec=JSON.parse(await fs.readFile(run+'/mirror-preparation.json'));
const previous='research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT';
globalThis.ProgressEvent??=class {constructor(type,init){Object.assign(this,init);}};
const context=JSON.parse(await fs.readFile(previous+'/context-arrays.json')).filter(r=>r.file==='neck'&&r.name.startsWith('b|')).map(r=>{
 const g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(r.positions),3));g.setIndex(new BufferAttribute(new Uint32Array(r.indices),1));g.computeBoundingBox();return {...r,g,b:new MeshBVH(g,{indirect:true,verbose:false})};
});
const files=rec.candidates ?? [{id:'admitted-right',file:rec.sourceFile,sha:rec.sourceSHA256},{id:'original-left-trial',file:rec.originalLeftTestFile,sha:rec.originalLeftTestSHA256},{id:'mirrored-left-trial',file:rec.file,sha:rec.sha256}];
const results=[],checks=[]; const check=(v,n)=>{if(!v)throw Error(n);checks.push(n);};
const dirs=[new Vector3(1,.37,.13).normalize(),new Vector3(.19,1,.43).normalize(),new Vector3(.31,.17,1).normalize()];
for(const row of files){
 const raw=await fs.readFile(row.file);check(crypto.createHash('sha256').update(raw).digest('hex')===row.sha,row.id+' source hash');
 const gltf=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.length),'');const meshes=[];gltf.scene.traverse(m=>{if(m.isMesh)meshes.push(m);});check(meshes.length===1,row.id+' one mesh');
 const mesh=meshes[0],g=mesh.geometry,p=g.attributes.position,idx=g.index,oldIndices=idx.array.slice();g.computeBoundingBox();g.boundsTree=new MeshBVH(g,{indirect:true,verbose:false});check(oldIndices.every((x,i)=>x===idx.array[i]),row.id+' stable indices');
 const pts=Array.from({length:p.count},(_,i)=>new Vector3().fromBufferAttribute(p,i));
 for(let i=0;i<idx.count;i+=3)pts.push(new Vector3().fromBufferAttribute(p,idx.getX(i)).add(new Vector3().fromBufferAttribute(p,idx.getX(i+1))).add(new Vector3().fromBufferAttribute(p,idx.getX(i+2))).multiplyScalar(1/3));
 const intersections=[];
 for(const target of context){
  if(!g.boundingBox.intersectsBox(target.g.boundingBox))continue;
  const start=Date.now(),affected=[],ambiguous=[];
  for(let i=0;i<pts.length;i++){
   if(Date.now()-start>20000)throw Error(row.id+' '+target.name+' 20 second budget exceeded');
   const point=pts[i],votes=dirs.map(d=>{const hits=target.b.raycast(new Ray(point,d),DoubleSide,1e-8).map(h=>h.distance).sort((a,b)=>a-b);return hits.filter((x,j)=>j===0||x-hits[j-1]>1e-7).length%2;});
   if(votes.some(x=>x!==votes[0]))ambiguous.push(i);
   if(votes.filter(Boolean).length>=2){const depth=target.b.closestPointToPoint(point).distance*1000;affected.push({sample:i,kind:i<p.count?'vertex':'faceCentroid',depthMM:depth,point:point.toArray()});}
  }
  if(affected.length||ambiguous.length){affected.sort((a,b)=>b.depthMM-a.depthMM);intersections.push({target:target.name,totalSamples:pts.length,insideSamples:affected.length,ambiguousSamples:ambiguous.length,maxSampleDepthMM:affected[0]?.depthMM??0,greaterThan01mm:affected.filter(x=>x.depthMM>.1).length,greaterThan05mm:affected.filter(x=>x.depthMM>.5).length,greaterThan1mm:affected.filter(x=>x.depthMM>1).length,worst:affected.slice(0,10),affectedBounds:affected.length?[0,1,2].map(k=>[Math.min(...affected.map(x=>x.point[k])),Math.max(...affected.map(x=>x.point[k]))]):null});}
 }
 const rays=[];mesh.material=new MeshBasicMaterial({side:DoubleSide});mesh.updateMatrixWorld(true);g.computeBoundingSphere();
 for(const f of [.13,.31,.57,.79,.91]){const aidx=Math.floor(f*idx.count/3)*3,a=new Vector3().fromBufferAttribute(p,idx.getX(aidx)),b=new Vector3().fromBufferAttribute(p,idx.getX(aidx+1)),c=new Vector3().fromBufferAttribute(p,idx.getX(aidx+2));const target=a.clone().add(b).add(c).multiplyScalar(1/3),normal=b.clone().sub(a).cross(c.clone().sub(a)).normalize();const ray=new Raycaster(target.clone().addScaledVector(normal,.1),normal.clone().negate());mesh.raycast=Mesh.prototype.raycast;const native=ray.intersectObject(mesh);mesh.raycast=acceleratedRaycast;const fast=ray.intersectObject(mesh);check(native.length>0&&native.length===fast.length&&native.every(h=>fast.some(x=>x.faceIndex===h.faceIndex&&Math.abs(x.distance-h.distance)<1e-8)),row.id+' ray '+f);rays.push(fast.length);}
 const result={id:row.id,file:row.file,vertices:p.count,triangles:idx.count/3,totalSamples:pts.length,bounds:g.boundingBox,intersections,rays};results.push(result);
 await fs.writeFile(run+'/'+row.id+'-checks.json',JSON.stringify(result,null,2),{flag:'wx'});
 console.log(JSON.stringify({id:row.id,intersections:intersections.map(r=>({target:r.target,inside:r.insideSamples,max:r.maxSampleDepthMM,above1:r.greaterThan1mm})),rays}));
}
await fs.writeFile(run+'/node-comparison.json',JSON.stringify({passed:checks.length,checks,method:'Every mesh vertex and face centroid; majority of three ray parities; nearest triangle distance. Includes ambiguous votes and depth bands for description, not universal medical thresholds. Sample maxima are not a continuous penetration or volume bound. No global mesh audit.',results},null,2),{flag:'wx'});
