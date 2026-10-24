// Bounded deterministic surface samples, not a continuous penetration maximum.
import fs from 'node:fs/promises';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {BufferGeometry,BufferAttribute,Vector3,Ray,DoubleSide} from 'three';
import {MeshBVH} from 'three-mesh-bvh';
const run=process.argv[2],rows=JSON.parse(await fs.readFile(run+'/context-arrays.json'));
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
function tree(g){return new MeshBVH(g,{indirect:true,verbose:false});}
const context=rows.filter(r=>!r.name.startsWith('m|omohyoid')).map(r=>{const g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(r.positions),3));g.setIndex(new BufferAttribute(new Uint32Array(r.indices),1));return {...r,b:tree(g)};});
const results=[];
for(const fma of ['FMA45856','FMA45857','FMA71309','FMA71442','FMA71443']){
 const bytes=await fs.readFile('build_stage7/source_trials/'+fma+'.glb');const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');let g;gltf.scene.traverse(m=>{if(m.isMesh)g=m.geometry;});
 const p=g.attributes.position,v=new Vector3(),dirs=[new Vector3(1,.37,.13).normalize(),new Vector3(.19,1,.43).normalize(),new Vector3(.31,.17,1).normalize()];
 for(const target of context.filter(r=>r.file===(fma.startsWith('FMA45')?'leg':'neck')||fma==='FMA45857'&&r.file==='leg-extra')){
  let inside=0,ambiguous=0,max=0;const affected=[];
  for(let s=0;s<600;s++){
   const i=Math.floor(s*p.count/600);v.fromBufferAttribute(p,i);const votes=dirs.map(d=>{const h=target.b.raycast(new Ray(v,d),DoubleSide,1e-8).map(h=>h.distance).sort((a,b)=>a-b);return h.filter((x,j)=>j===0||x-h[j-1]>1e-7).length%2;});
   if(votes.some(x=>x!==votes[0]))ambiguous++;
   if(votes.filter(Boolean).length>=2){inside++;const near=target.b.closestPointToPoint(v);max=Math.max(max,near.distance);affected.push(v.toArray());}
  }
  if(inside)results.push({fma,target:target.name,samples:600,inside,ambiguous,maxSampleDepthMM:max*1000,affectedBounds:[0,1,2].map(k=>[Math.min(...affected.map(x=>x[k])),Math.max(...affected.map(x=>x[k]))])});
 }
}
await fs.writeFile(run+'/sampled-depth.json',JSON.stringify({method:'600 evenly indexed vertices per source; majority of three ray parities. Surface sample only; not volume fraction, continuous maximum or anatomical acceptance.',results},null,2),{flag:'wx'});
console.log(JSON.stringify(results));
