// New comparisons only; unchanged, byte-equivalent triangle inputs reuse prior evidence.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import * as THREE from 'three';
import {MeshBVH} from 'three-mesh-bvh';
import {pairKind, scan} from './audit-self-intersections.mjs';
const run=path.resolve(process.argv[2]);
const read=async f=>JSON.parse(await fs.readFile(f,'utf8'));
const arrays=await read(path.join(run,'comparison-arrays.json'));
const meta=await read(path.join(run,'comparison-metadata.json'));
const write=(file,obj)=>fs.writeFile(path.join(run,file),JSON.stringify(obj,null,2),{flag:'wx'});
const digest=a=>crypto.createHash('sha256').update(JSON.stringify(a.vertices)).update(JSON.stringify(a.faces)).digest('hex');
const hashes=Object.fromEntries(Object.entries(arrays).map(([k,a])=>[k,digest(a)]));
const cache=new Map(),reuseDirs=[
 'stage6-mirror-upper-v2-2026-10-20T12-11-27-299Z-T0jfz0',
 'stage6-mirror-lower-v2-2026-10-20T12-11-27-305Z-5rXqo2',
 'stage6-mirror-toe5-repair-2026-10-20T12-20-59-021Z-ZBXbnc',
 'stage6-left-metatarsals-2026-10-20T11-37-52-033Z-JqSVPJ',
 'stage6-left-tarsals-2026-10-20T11-22-52-873Z-6rEIlo'];
const pairHash=(a,b)=>[a,b].sort().join(':');
for(const name of reuseDirs){
 const dir=path.join('research/evidence-runs',name),a=await read(path.join(dir,'mesh-arrays.json'));
 for(const p of (await read(path.join(dir,'joint-intersections.json'))).cross)
  if(p.complete)cache.set(pairHash(digest(a[p.a]),digest(a[p.b])),{...p,evidence:path.join(dir,'joint-intersections.json')});
}
const bvh=new Map();
function tree(k){
 if(!bvh.has(k)){
  const a=arrays[k],g=new THREE.BufferGeometry().setAttribute('position',new THREE.BufferAttribute(new Float64Array(a.vertices),3));
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(a.faces),1));
  bvh.set(k,new MeshBVH(g,{indirect:true,verbose:false}));
 }
 return bvh.get(k);
}
const cross=[],ids=Object.keys(arrays);
let reused=0,computed=0,disjoint=0;
for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++){
 const a=ids[i],b=ids[j],ma=meta[a],mb=meta[b];
 if(ma.region!==mb.region||ma.owner===mb.owner||(a.startsWith('live__')&&b.startsWith('live__')))continue;
 const h=pairHash(hashes[a],hashes[b]);
 let row={a,b,complete:true,counts:{}};
 if(cache.has(h)){const old=cache.get(h);row={...row,counts:old.counts,reusedFrom:old.evidence};reused++;}
 else if([0,1,2].some(k=>ma.bounds[1][k]<mb.bounds[0][k]||mb.bounds[1][k]<ma.bounds[0][k])){
  row.aabbDisjoint=true;disjoint++;
 }else{
  const start=Date.now(),x=tree(a),y=tree(b);row.examples=[];
  x.bvhcast(y,new THREE.Matrix4(),{intersectsTriangles(t,u,ti,tj){
   if(Date.now()-start>15000){row.complete=false;return true;}
   const kind=pairKind(t,u);
   if(kind!=='none')row.counts[kind]=(row.counts[kind]||0)+1;
   if(['crossing','coplanarOverlap'].includes(kind)&&row.examples.length<8)
    row.examples.push({a:x.resolveTriangleIndex(ti),b:y.resolveTriangleIndex(tj),kind});
   return false;
  }});
  row.durationMs=Date.now()-start;computed++;
  await write(`pair-${a}-${b}.json`,row);
 }
 cross.push(row);
}
// Only five authored-left toe sources are newly subject to self-intersection acceptance.
for(const bone of ['toe_prox_1_left','toe_dist_1_left','toe_prox_5_left','toe_mid_5_left','toe_dist_5_left']){
 const a=arrays['native__'+bone];
 await write(bone+'-native-self.json',scan(new Float64Array(a.vertices),new Uint32Array(a.faces),15000));
}
await write('comparison-pairs.json',{cross,hashes,reused,computed,disjoint,
 scope:'Exact triangle reuse only. New comparisons preserve all positions; no fit/deformation or anatomical acceptance.'});
console.log(JSON.stringify({reused,computed,disjoint,incomplete:cross.filter(p=>!p.complete).length,
 crossing:cross.filter(p=>p.counts.crossing||p.counts.coplanarOverlap).length}));
