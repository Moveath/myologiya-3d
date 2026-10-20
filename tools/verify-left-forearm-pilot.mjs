// Small, bounded trial only; never edits the catalogue or any model.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshBVH, acceleratedRaycast} from 'three-mesh-bvh';
import {scan,pairKind} from './audit-self-intersections.mjs';
import {inspectGeometry} from './geometry-export-check.mjs';
const dir=path.resolve(process.argv[2]);
const arrays=JSON.parse(await fs.readFile(path.join(dir,'mesh-arrays.json'),'utf8'));
const write=(name,data)=>fs.writeFile(path.join(dir,name),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
assert.equal(THREE.REVISION,'170');
const self=[];
for(const id of ['radius_left','ulna_left']){
 const a=arrays[id],result=scan(new Float64Array(a.vertices),new Uint32Array(a.faces),15000);
 self.push({id,...result});
 await write(id+'-self-intersections.json',self.at(-1));
}
const cross=[];
for(const [a,b] of [['radius_left','ulna_left'],['radius_left','existing_humerus_left'],
 ['ulna_left','existing_humerus_left'],['radius_left','scaphoid_left'],['radius_left','lunate_left']]){
 const start=Date.now();
 const make=id=>{
  const g=new THREE.BufferGeometry().setAttribute('position',new THREE.BufferAttribute(new Float64Array(arrays[id].vertices),3));
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(arrays[id].faces),1));
  return new MeshBVH(g,{indirect:true,verbose:false});
 };
 const x=make(a),y=make(b),counts={},examples=[];let complete=true;
 x.bvhcast(y,new THREE.Matrix4(),{intersectsTriangles(t,u,i,j){
  if(Date.now()-start>15000){complete=false;return true;}
  const kind=pairKind(t,u);
  if(kind!=='none')counts[kind]=(counts[kind]||0)+1;
  if(['crossing','coplanarOverlap'].includes(kind)&&examples.length<12)
   examples.push({a:x.resolveTriangleIndex(i),b:y.resolveTriangleIndex(j),kind});
  return false;
 }});
 cross.push({a,b,complete,counts,examples,durationMs:Date.now()-start});
 x.geometry.dispose();y.geometry.dispose();
}
await write('joint-intersections.json',{cross,limitation:'Floating point triangle intersections, not proof of anatomical contact/cartilage or clinical alignment.'});
const exports=[];
for(const id of ['radius_left','ulna_left']){
 const file='build_stage6/left_forearm_v1/'+id+'.glb',summary=await inspectGeometry(file);
 const m=summary.meshes[0];
 assert.equal(m.owner,'b|'+id);assert.equal(summary.meshes.length,1);
 assert.equal(m.invalidNormals+m.invalidPositions+m.zeroFaces,0);assert.ok(m.determinant>0);
 const bytes=await fs.readFile(file),scene=(await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')).scene;
 scene.updateMatrixWorld(true);
 let mesh;scene.traverse(o=>{if(o.isMesh)mesh=o;});
 const g=mesh.geometry,index=g.index.array.slice(),position=g.attributes.position.array.slice();
 g.boundsTree=new MeshBVH(g,{indirect:true,verbose:false});
 assert.deepEqual(g.index.array,index);assert.deepEqual(g.attributes.position.array,position);
 const box=new THREE.Box3().setFromObject(mesh),center=box.getCenter(new THREE.Vector3()),radius=box.getSize(new THREE.Vector3()).length();
 let compared=0,hits=0;
 for(let i=0;i<18;i++){
  const origin=center.clone().add(new THREE.Vector3(Math.cos(i)*radius,Math.sin(i)*radius,radius));
  const ray=new THREE.Raycaster(origin,center.clone().sub(origin).normalize());
  const original=[],fast=[];
  THREE.Mesh.prototype.raycast.call(mesh,ray,original);
  acceleratedRaycast.call(mesh,ray,fast);
  original.sort((a,b)=>a.distance-b.distance);fast.sort((a,b)=>a.distance-b.distance);
  assert.equal(original.length,fast.length);
  if(original.length){hits++;assert.equal(original[0].faceIndex,fast[0].faceIndex);assert.ok(Math.abs(original[0].distance-fast[0].distance)<1e-7);}
  compared++;
 }
 assert.ok(hits>0);
 exports.push({...summary,raysCompared:compared,raysWithHits:hits,indicesAndVerticesPreserved:true});
}
await write('three-bvh.json',{status:'passed',exports});
console.log(JSON.stringify({exports:exports.map(x=>({file:x.file,faces:x.meshes[0].faces,rays:x.raysCompared})),
 self:self.map(x=>({id:x.id,complete:x.complete,counts:x.counts})),cross}));
