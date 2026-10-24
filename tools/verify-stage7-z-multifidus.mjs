// Diagnostic admission evidence; no production writes and no deformation.
import fs from 'node:fs/promises';
import {BufferGeometry,BufferAttribute,Vector3,Matrix4,Ray,DoubleSide} from 'three';
import {MeshBVH} from 'three-mesh-bvh';
import {scan} from './audit-self-intersections.mjs';
const run=process.argv[2];if(!run)throw Error('Evidence directory required');
const z=JSON.parse(await fs.readFile(run+'/z-target-arrays-v2.json'));
const a=JSON.parse(await fs.readFile(run+'/atlas-multifidus-context.json'));
const transforms=JSON.parse(await fs.readFile(run+'/z-multifidus-registration.json'));
function tree(r){const g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(r.vertices.flat()),3));g.setIndex(new BufferAttribute(new Uint32Array(r.faces.flat()),1));g.computeBoundingBox();return {g,b:new MeshBVH(g,{indirect:true,verbose:false})};}
const bones=a.filter(r=>r.name.startsWith('b|')).map(r=>({...r,...tree(r)}));
const dirs=[new Vector3(1,.37,.13),new Vector3(.19,1,.43),new Vector3(.31,.17,1)].map(v=>v.normalize());
const summary=[];
for(const fit of transforms)for(const [side,suffix]of [['right','r'],['left','l']]){
 const source=z.find(r=>r.name===`Multifidus thoracis muscle.${suffix}`),M=new Matrix4().set(...fit.matrix_source_blender_to_atlas_three.flat());
 const vertices=source.vertices.map(p=>new Vector3(...p).applyMatrix4(M).toArray());
 const faces=source.faces.map(f=>source.determinant<0?[f[0],f[2],f[1]]:f.slice());
 const self=fit.kind==='rigid'?scan(new Float64Array(vertices.flat()),new Uint32Array(faces.flat()),20000):{inherited:'Rigid source shape; positive uniform scale cannot create self intersections.'};
 const overlaps=[];
 for(const target of bones){
  let inside=0,ambiguous=0,max=0;const affected=[];
  for(let s=0;s<600;s++){
   const i=Math.floor(s*vertices.length/600),v=new Vector3(...vertices[i]);
   if(!target.g.boundingBox.containsPoint(v))continue;
   const votes=dirs.map(d=>{const h=target.b.raycast(new Ray(v,d),DoubleSide,1e-8).map(h=>h.distance).sort((a,b)=>a-b);return h.filter((x,j)=>!j||x-h[j-1]>1e-7).length%2;});
   if(votes.some(x=>x!==votes[0]))ambiguous++;
   if(votes.filter(Boolean).length>=2){inside++;const depth=target.b.closestPointToPoint(v).distance;max=Math.max(max,depth);affected.push({vertex:i,depthMM:depth*1000});}
  }
  if(inside||ambiguous)overlaps.push({bone:target.name,inside,ambiguous,samples:600,maxSampleDepthMM:max*1000,deepest:affected.sort((a,b)=>b.depthMM-a.depthMM).slice(0,8)});
 }
 const result={side,fit:fit.kind,source:source.name,triangles:faces.length,self,sampledBoneOverlap:overlaps,
   limitations:'600 deterministic surface vertices and three-ray parity per bone; not volume fraction or continuous penetration bound. Topographic approval is separate.'};
 await fs.writeFile(run+`/node-z-multifidus-${fit.kind}-${side}.json`,JSON.stringify(result,null,2),{flag:'wx'});
 summary.push({side,fit:fit.kind,self:self.counts??self,sampledBoneOverlap:overlaps.map(({deepest,...r})=>r)});
}
await fs.writeFile(run+'/node-z-multifidus-summary.json',JSON.stringify(summary,null,2),{flag:'wx'});
console.log(JSON.stringify(summary));
