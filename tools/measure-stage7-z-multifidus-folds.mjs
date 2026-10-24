// Measure the already-recorded within-bundle examples; no full scan repeated.
import fs from 'node:fs/promises';
import {Vector3,Line3} from 'three';
import {ExtendedTriangle} from 'three-mesh-bvh';
const run=process.argv[2];if(!run)throw Error('Evidence directory required');
const rows=JSON.parse(await fs.readFile(run+'/z-target-arrays-v2.json'));
const reports=[];
for(const [side,suffix]of [['right','r'],['left','l']]){
 const source=rows.find(x=>x.name===`Multifidus thoracis muscle.${suffix}`);
 const prior=JSON.parse(await fs.readFile(run+`/z-multifidus-contact-classification-${side}.json`));
 const details=[];
 for(const pair of prior.byComponentPair.filter(x=>x.components[0]===x.components[1]))for(const e of pair.examples){
  const triangles=e.faces.map(fi=>new ExtendedTriangle(...source.faces[fi].map(vi=>new Vector3(...source.vertices[vi]))));
  triangles.forEach(t=>t.needsUpdate=true);const line=new Line3(),intersects=triangles[0].intersectsTriangle(triangles[1],line,true);
  const n0=triangles[0].getNormal(new Vector3()),n1=triangles[1].getNormal(new Vector3());
  details.push({component:pair.components[0],faces:e.faces,intersects,
      segmentLengthMM:line.distance()*1000,normalDot:n0.dot(n1),
      sharedVertexIds:source.faces[e.faces[0]].filter(v=>source.faces[e.faces[1]].includes(v)),
      sourceIntersection:intersects?[line.start.toArray(),line.end.toArray()]:null});
 }
 reports.push({side,withinCrossingPairs:prior.counts.withinComponent.crossing,recordedExamplesMeasured:details.length,
     details,note:'Length is the triangle-intersection segment, not tissue penetration or defect severity. The example cap records 11 of 12 flagged pairs.'});
}
await fs.writeFile(run+'/z-multifidus-fold-measurements.json',JSON.stringify(reports,null,2),{flag:'wx'});
console.log(JSON.stringify(reports.map(({details,...r})=>({...r,minSegmentMM:Math.min(...details.map(x=>x.segmentLengthMM)),maxSegmentMM:Math.max(...details.map(x=>x.segmentLengthMM)),samples:details.map(x=>({component:x.component,lengthMM:x.segmentLengthMM,normalDot:x.normalDot,shared:x.sharedVertexIds.length}))}))));
