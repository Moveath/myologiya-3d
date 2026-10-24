import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {BufferGeometry,BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Vector3,Raycaster,Matrix4} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
import {scan,pairKind} from './audit-self-intersections.mjs';
const [build,run]=process.argv.slice(2),checks=[];
const check=(v,n)=>{assert.ok(v,n);checks.push(n);};
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const bytes=await fs.readFile(build+'/palmaris_brevis-trial.glb');
const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
gltf.scene.updateMatrixWorld(true);const ms=[];gltf.scene.traverse(m=>{if(m.isMesh)ms.push(m)});
check(ms.length===1,'Exactly one trial mesh, no foreign scene objects');
const m=ms[0];check(m.name==='m|palmaris_brevis|','Stable owner ID without Blender suffix');
const g=m.geometry.clone().applyMatrix4(m.matrixWorld),before=Array.from(g.index.array);g.boundsTree=new MeshBVH(g,{indirect:true});
check(JSON.stringify(before)===JSON.stringify(Array.from(g.index.array)),'Indirect BVH preserves indices');
check(g.index.count===3296*3,'3296 triangles loaded by r170');
check(Array.from(g.attributes.normal.array).every(Number.isFinite),'Finite exported normals');
const self=scan(g.attributes.position.array,g.index.array,15000);
check(self.complete,'Bounded self-intersection scan completed');
check(!self.counts.crossing&&!self.counts.coplanarOverlap&&!self.counts.duplicate,'No self crossings/overlaps/duplicate faces');
const trial=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));trial.updateMatrixWorld();const rays=[];
for(let i=0;i<24;i++){
 const f=i*101%3296,p=new Vector3(),normal=new Vector3();
 for(let k=0;k<3;k++){const ix=g.index.getX(f*3+k);p.add(new Vector3().fromBufferAttribute(g.attributes.position,ix));normal.add(new Vector3().fromBufferAttribute(g.attributes.normal,ix));}p.multiplyScalar(1/3);normal.normalize();
 const ray=new Raycaster(p.clone().addScaledVector(normal,.03),normal.clone().negate()),a=[],b=[];
 Mesh.prototype.raycast.call(trial,ray,a);acceleratedRaycast.call(trial,ray,b);a.sort((x,y)=>x.distance-y.distance);b.sort((x,y)=>x.distance-y.distance);
 check(a.length&&a.length===b.length&&Math.abs(a[0].distance-b[0].distance)<1e-7&&a[0].faceIndex===b[0].faceIndex,'Native/BVH ray '+i);rays.push({face:f,hits:a.length});
}
const rows=JSON.parse(await fs.readFile(run+'/hand-context.json')),contacts=[];
for(const row of rows){
 const context=new BufferGeometry();context.setAttribute('position',new BufferAttribute(new Float32Array(row.positions),3));context.setIndex(row.indices);context.boundsTree=new MeshBVH(context,{indirect:true});
 let crossing=0,overlap=0,pairs=0;const examples=[];
 g.boundsTree.bvhcast(context.boundsTree,new Matrix4(),{intersectsTriangles(a,b,ia,ib){const k=pairKind(a,b);pairs++;if(k==='crossing')crossing++;if(k==='coplanarOverlap')overlap++;if((k==='crossing'||k==='coplanarOverlap')&&examples.length<4)examples.push({trialFace:g.boundsTree.resolveTriangleIndex(ia),contextFace:context.boundsTree.resolveTriangleIndex(ib),kind:k});return false;}});
 contacts.push({id:row.id,name:row.name,pairs,crossing,overlap,examples});context.dispose();
}
const box={window:{}};vm.createContext(box);for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','data-muscle-recovery','data-neck-recovery'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=box.window.ATLAS;check(A.muscles.palmaris_brevis.noModel,'Production noModel retained');
check(!Object.values(A.supplementalMuscles).flat().includes('palmaris_brevis'),'Prototype excluded from production whitelist');
const inventory={muscles:Object.keys(A.muscles).length,muscleNoModel:Object.values(A.muscles).filter(x=>x.noModel).length,partsNoModel:Object.values(A.muscles).flatMap(m=>Object.values(m.parts||{})).filter(x=>x.noModel).length,boneNoModel:Object.values(A.bones).filter(x=>x.noModel).length};
check(inventory.muscleNoModel===14&&inventory.partsNoModel===21&&inventory.boneNoModel===20,'All existing blockers retained');
await fs.writeFile(run+'/node-prototype.json',JSON.stringify({status:'passed',checks,self,rays,contacts,inventory,anatomicalAdmission:false},null,2),{flag:'wx'});
console.log(JSON.stringify({checks:checks.length,self:self.counts,contacts:contacts.filter(c=>c.crossing||c.overlap),inventory}));
