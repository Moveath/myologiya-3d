// Classify prior intersection flags by authored connected component and material.
// Diagnostic counts/locations are not clinical penetration tolerances.
import fs from 'node:fs/promises';
import {BufferGeometry,BufferAttribute,Vector3,Matrix4,Ray,DoubleSide} from 'three';
import {MeshBVH} from 'three-mesh-bvh';
import {pairKind} from './audit-self-intersections.mjs';
const run=process.argv[2];if(!run)throw Error('Evidence directory required');
const rows=JSON.parse(await fs.readFile(run+'/z-target-arrays-v2.json'));
const maps=JSON.parse(await fs.readFile(run+'/z-multifidus-components-map.json'));
const transforms=JSON.parse(await fs.readFile(run+'/z-multifidus-registration.json'));
const atlas=JSON.parse(await fs.readFile(run+'/atlas-multifidus-context.json'));
const dirs=[new Vector3(1,.37,.13),new Vector3(.19,1,.43),new Vector3(.31,.17,1)].map(v=>v.normalize());
function mesh(vertices,faces){const g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(vertices.flat()),3));g.setIndex(new BufferAttribute(new Uint32Array(faces.flat()),1));g.computeBoundingBox();return {g,b:new MeshBVH(g,{indirect:true,verbose:false})};}
const results=[];
for(const [side,suffix]of [['right','r'],['left','l']]){
 const row=rows.find(x=>x.name===`Multifidus thoracis muscle.${suffix}`),map=maps.find(x=>x.name===row.name);
 const center=row.vertices.reduce((a,v)=>a.map((x,k)=>x+v[k]/row.vertices.length),[0,0,0]);
 const extent=Math.max(...[0,1,2].map(k=>Math.max(...row.vertices.map(v=>v[k]))-Math.min(...row.vertices.map(v=>v[k]))));
 const normalized=row.vertices.map(v=>v.map((x,k)=>(x-center[k])/extent));
 const whole=mesh(normalized,row.faces),counts={withinComponent:{crossing:0,duplicate:0,coplanarOverlap:0},betweenComponents:{crossing:0,duplicate:0,coplanarOverlap:0}},pairs={};
 const faceFlags=new Set(),deadline=Date.now()+20000;let complete=true;
 whole.b.bvhcast(whole.b,new Matrix4(),{intersectsTriangles(a,b,i,j){
  if(Date.now()>deadline){complete=false;return true;}
  const fi=whole.b.resolveTriangleIndex(i),fj=whole.b.resolveTriangleIndex(j);if(fi>=fj)return false;
  const kind=pairKind(a,b);if(!['crossing','duplicate','coplanarOverlap'].includes(kind))return false;
  const ci=map.faceComponent[fi],cj=map.faceComponent[fj],key=ci===cj?'withinComponent':'betweenComponents';
  counts[key][kind]++;faceFlags.add(fi);faceFlags.add(fj);
  const pairKey=[ci,cj].sort((a,b)=>a-b).join(':');pairs[pairKey]??={components:[ci,cj],crossing:0,duplicate:0,coplanarOverlap:0,examples:[]};pairs[pairKey][kind]++;
  if(pairs[pairKey].examples.length<6)pairs[pairKey].examples.push({faces:[fi,fj],kind,materials:[row.materials[row.triangle_materials[fi]],row.materials[row.triangle_materials[fj]]]});
  return false;
 }});
 const boneLocations=[];
 // Extend the existing diagnostic, do not repeat the successful ray classification.
 for(const fit of transforms){
  const prior=JSON.parse(await fs.readFile(run+`/node-z-multifidus-${fit.kind}-${side}.json`));
  const M=new Matrix4().set(...fit.matrix_source_blender_to_atlas_three.flat());
  const vertices=row.vertices.map(p=>new Vector3(...p).applyMatrix4(M).toArray());
  for(const overlap of prior.sampledBoneOverlap)for(const point of overlap.deepest){
   const incident=[];for(let fi=0;fi<row.faces.length;fi++)if(row.faces[fi].includes(point.vertex))incident.push(fi);
   const componentIds=[...new Set(incident.map(fi=>map.faceComponent[fi]))];
   const p=vertices[point.vertex],regions=componentIds.map(ci=>{
    const ids=[...new Set(map.components[ci].faceIds.flatMap(fi=>row.faces[fi]))];
    const ys=ids.map(i=>vertices[i][1]),lo=Math.min(...ys),hi=Math.max(...ys);
    return {component:ci,relativeCranioCaudalPosition:(p[1]-lo)/(hi-lo),heightMM:(hi-lo)*1000};
   });
   const materials=[...new Set(incident.map(fi=>row.materials[row.triangle_materials[fi]]))];
   boneLocations.push({fit:fit.kind,bone:overlap.bone,vertex:point.vertex,depthMM:point.depthMM,
      sourceMaterials:materials,componentLocations:regions,point:p,
      caveat:'Component height extrema and material labels are source diagnostics, not confirmed origin/insertion or named bone surface.'});
  }
 }
 const result={side,source:row.name,complete,components:map.components.length,counts,
    byComponentPair:Object.values(pairs),flaggedFaceCount:faceFlags.size,boneLocations,
    interpretation:'Within-component crossings cannot be explained solely by overlap between distinct soft-tissue bundles. Source tendon material and component extrema do not independently identify a validated attachment area.'};
 await fs.writeFile(run+`/z-multifidus-contact-classification-${side}.json`,JSON.stringify(result,null,2),{flag:'wx'});
 results.push({side,complete,counts,flaggedFaceCount:faceFlags.size,
   within:Object.values(pairs).filter(x=>x.components[0]===x.components[1]).map(({examples,...r})=>r),
   boneSamples:boneLocations.length,tendonOnlySamples:boneLocations.filter(x=>x.sourceMaterials.length===1&&x.sourceMaterials[0]==='Tendon').length,
   muscleMaterialSamples:boneLocations.filter(x=>x.sourceMaterials.includes('External rotation')).length});
}
await fs.writeFile(run+'/z-multifidus-contact-classification-summary.json',JSON.stringify(results,null,2),{flag:'wx'});console.log(JSON.stringify(results));
