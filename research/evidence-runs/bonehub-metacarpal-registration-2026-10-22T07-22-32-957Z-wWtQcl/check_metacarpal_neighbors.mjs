// Bounded new-candidate comparisons only. No neighbour-dependent fitting.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as THREE from '../../../tools/node_modules/three/build/three.module.js';
import {MeshBVH} from '../../../tools/node_modules/three-mesh-bvh/src/index.js';
import {pairKind,scan} from '../../../tools/audit-self-intersections.mjs';
const run=path.dirname(fileURLToPath(import.meta.url));
const old=path.resolve(run,'../stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj');
const arrays=JSON.parse(await fs.readFile(path.join(old,'comparison-arrays.json'),'utf8'));
const meta=JSON.parse(await fs.readFile(path.join(old,'comparison-metadata.json'),'utf8'));
const owner=process.argv[2];if(!['metacarpal_1_left','metacarpal_3_left'].includes(owner))throw Error('owner');
const a=JSON.parse(await fs.readFile(path.join(run,owner+'-registered-arrays.json'),'utf8'));
const write=(name,data)=>fs.writeFile(path.join(run,name),JSON.stringify(data,null,2),{flag:'wx'});
function create(a){const g=new THREE.BufferGeometry().setAttribute('position',new THREE.BufferAttribute(new Float64Array(a.vertices),3));g.setIndex(new THREE.BufferAttribute(new Uint32Array(a.faces),1));g.computeBoundingBox();return {g,b:new MeshBVH(g,{indirect:true,verbose:false})};}
const candidate=create(a),target=create(arrays['native__'+owner]);
const dirs=[new THREE.Vector3(1,.371,.137).normalize(),new THREE.Vector3(.193,1,.431).normalize(),new THREE.Vector3(.313,.173,1).normalize()];
function surfaceSamples(g){const p=g.attributes.position,idx=g.index;const points=[];for(let i=0;i<p.count;i++)points.push(new THREE.Vector3().fromBufferAttribute(p,i));for(let i=0;i<idx.count;i+=3){const x=new THREE.Vector3().fromBufferAttribute(p,idx.getX(i));x.add(new THREE.Vector3().fromBufferAttribute(p,idx.getX(i+1))).add(new THREE.Vector3().fromBufferAttribute(p,idx.getX(i+2))).multiplyScalar(1/3);points.push(x);}return points;}
function depth(source,dest){const begin=Date.now(),points=surfaceSamples(source.g);let tested=0,inside=0,ambiguous=0;const values=[];for(const p of points){if(Date.now()-begin>25000)return {complete:false,reason:'25second direction budget',tested,totalSamples:points.length};tested++;const votes=dirs.map(d=>{const h=dest.b.raycast(new THREE.Ray(p,d),THREE.DoubleSide,1e-8).map(x=>x.distance).sort((x,y)=>x-y);return h.filter((x,i)=>!i||x-h[i-1]>1e-7).length%2;});if(votes.some(x=>x!==votes[0]))ambiguous++;if(votes.filter(Boolean).length>=2){inside++;const n=dest.b.closestPointToPoint(p);values.push({mm:n.distance*1000,position:p.toArray()});}}values.sort((x,y)=>y.mm-x.mm);return {complete:true,tested,insideSamples:inside,ambiguous,maxSampleDepthMM:values[0]?.mm||0,deepest:values.slice(0,12),elapsedMs:Date.now()-begin};}
const sourceHashes={};
const distances=[];
for(const [name,src,dst] of [['candidate-to-target',candidate,target],['target-to-candidate',target,candidate]]){
 const begin=Date.now(),d=[];for(const p of surfaceSamples(src.g)){if(Date.now()-begin>15000)throw Error('surface distance time budget');d.push(dst.b.closestPointToPoint(p).distance*1000);}d.sort((x,y)=>x-y);distances.push({direction:name,samples:d.length,medianMM:d[Math.floor(d.length*.5)],p95MM:d[Math.floor(d.length*.95)],maxSampleDistanceMM:d.at(-1),rmsMM:Math.sqrt(d.reduce((s,x)=>s+x*x,0)/d.length)});
}
await write(owner+'-surface-distances.json',distances);
const candidates=Object.keys(arrays).filter(k=>k.startsWith('live__')&&meta[k].region===meta['native__'+owner].region);
const results=[];
for(const k of candidates){
 const n=create(arrays[k]);if(!candidate.g.boundingBox.intersectsBox(n.g.boundingBox)){results.push({neighbor:k,aabbDisjoint:true,complete:true});continue;}
 const row={neighbor:k,complete:true,counts:{},examples:[]};const start=Date.now();
 candidate.b.bvhcast(n.b,new THREE.Matrix4(),{intersectsTriangles(t,u,ti,tj){if(Date.now()-start>10000){row.complete=false;return true;}const kind=pairKind(t,u);if(kind!=='none')row.counts[kind]=(row.counts[kind]||0)+1;if(['crossing','coplanarOverlap'].includes(kind)&&row.examples.length<5)row.examples.push({candidateFace:candidate.b.resolveTriangleIndex(ti),neighborFace:n.b.resolveTriangleIndex(tj),kind});return false;}});
 if(row.counts.crossing||row.counts.coplanarOverlap){row.candidateIntoNeighbor=depth(candidate,n);row.neighborIntoCandidate=depth(n,candidate);}
 results.push(row);await write(owner+'-neighbor-'+k+'.json',row);
 console.log(owner,k,row.counts,'depthMM',row.candidateIntoNeighbor?.maxSampleDepthMM,row.neighborIntoCandidate?.maxSampleDepthMM);
}
const self=scan(new Float64Array(a.vertices),new Uint32Array(a.faces),15000);await write(owner+'-self.json',self);
await write(owner+'-neighbors-summary.json',{owner,workingNeighbors:candidates.length,results,selfComplete:self.complete,method:'Candidate registered to original bone shape only; all current working regional neighbours checked with indirect BVH. Depth sampled at all vertices and triangle centres, parity majority in three directions + exact closest triangle distance. Not continuous depth maximum, anatomical masks or a clinical admissibility threshold.',admitted:false});
