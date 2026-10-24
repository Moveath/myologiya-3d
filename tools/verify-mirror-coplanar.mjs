// Regression fixtures for shared-edge roundoff, without tolerating real overlaps.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {Vector3} from 'three';
import {ExtendedTriangle} from 'three-mesh-bvh';
import {pairKind,scan} from './audit-self-intersections.mjs';
const run=path.resolve(process.argv[2]),arrays=JSON.parse(await fs.readFile(path.join(run,'mesh-arrays.json'),'utf8'));
const triangle=points=>new ExtendedTriangle(...points.map(p=>new Vector3(...p)));
const fixtures=[
 ['adjacent',[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[0,0,0],[0,-1,0]]],
 ['coplanarOverlap',[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[1,0,0],[.2,.5,0]]],
 ['coplanarOverlap',[[0,0,0],[1,0,0],[0,1,0]],[[.1,.1,0],[.8,.1,0],[.1,.8,0]]],
 ['crossing',[[0,0,0],[1,0,0],[0,1,0]],[[.2,.2,-1],[.2,.2,1],[.7,.2,0]]],
 ['duplicate',[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[1,0,0],[0,1,0]]]
];
for(const [expected,a,b] of fixtures)assert.equal(pairKind(triangle(a),triangle(b)),expected);
const reviewed=[];
for(const id of ['toe_prox_3_left','toe_prox_4_left']){
 const a=arrays[id],prior=JSON.parse(await fs.readFile(path.join(run,id+'-self-intersections.json'),'utf8'));
 for(const ex of prior.examples){
  const t=i=>triangle(a.faces.slice(i*3,i*3+3).map(j=>a.vertices.slice(j*3,j*3+3)));
  assert.equal(pairKind(t(ex.i),t(ex.j)),'adjacent',id);
 }
 const result=scan(new Float64Array(a.vertices),new Uint32Array(a.faces),15000);
 assert.ok(result.complete);assert.equal(result.counts.crossing+result.counts.coplanarOverlap,0);
 await fs.writeFile(path.join(run,id+'-self-reviewed.json'),JSON.stringify({id,...result},null,2),{flag:'wx'});
 reviewed.push({id,previousFalseCandidates:prior.examples});
}
await fs.writeFile(path.join(run,'coplanar-regression.json'),JSON.stringify({status:'passed',fixtures:fixtures.length,reviewed,
 scope:'Only exact shared-edge opposite-half-plane cases reclassified; no mesh or thresholds changed'},null,2),{flag:'wx'});
console.log(JSON.stringify({status:'passed',fixtures:fixtures.length,realMeshes:reviewed.length}));
