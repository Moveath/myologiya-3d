// Bounded GLB/raycast/BVH checks for test derivatives; does not admit anatomy.
import fs from 'node:fs/promises';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
import {Mesh,MeshBasicMaterial,DoubleSide,Vector3,Raycaster,Triangle} from 'three';
const run=process.argv[2];if(!run)throw Error('Unique evidence directory required');
const checks=[],results=[];
function check(value,label){if(!value)throw Error(label);checks.push(label);}
for(const side of ['right','left']){
 const path=`build_stage7/z_multifidus_trials_v1/thorax_multifidus_${side}-thoracic-test.glb`;
 const bytes=await fs.readFile(path),gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
 gltf.scene.updateMatrixWorld(true);const meshes=[];gltf.scene.traverse(o=>{if(o.isMesh)meshes.push(o);});
 check(meshes.length===1,`${side}: exactly one trial mesh`);const m=meshes[0],g=m.geometry;
 check(m.name===`m|thorax_multifidus_${side}|thoracic`,`${side}: stable part owner`);
 check(g.index.count===3902*3,`${side}: source triangle count preserved`);
 check([...g.attributes.position.array].every(Number.isFinite),`${side}: finite positions`);
 g.computeBoundingBox();check(side==='right'?g.boundingBox.max.x<0:g.boundingBox.min.x>0,`${side}: actual geometric side`);
 const before=Array.from(g.index.array);g.boundsTree=new MeshBVH(g,{indirect:true,verbose:false});
 check(before.every((x,i)=>x===g.index.array[i]),`${side}: indirect BVH preserves indices`);
 const native=new Mesh(g,new MeshBasicMaterial({side:DoubleSide})),bvh=new Mesh(g,native.material);bvh.raycast=acceleratedRaycast;
 native.updateMatrixWorld(true);bvh.updateMatrixWorld(true);
 const v=[new Vector3(),new Vector3(),new Vector3()],normal=new Vector3(),center=new Vector3(),rays=[];
 for(let n=0;n<12;n++){
  const fi=Math.floor((n+.25)*3902/12),tri=new Triangle(...v.map((p,i)=>p.fromBufferAttribute(g.attributes.position,g.index.getX(fi*3+i))));
  tri.getNormal(normal);tri.getMidpoint(center);const ray=new Raycaster(center.clone().addScaledVector(normal,.015),normal.clone().negate(),0,.1);ray.firstHitOnly=true;
  const a=ray.intersectObject(native),b=ray.intersectObject(bvh);
  check(a.length&&b.length&&a[0].faceIndex===b[0].faceIndex&&Math.abs(a[0].distance-b[0].distance)<1e-7,`${side}: native/BVH ray ${n+1}`);
  rays.push({faceIndex:a[0].faceIndex,distance:a[0].distance});
 }
 results.push({side,file:path,triangles:g.index.count/3,vertices:g.attributes.position.count,rays,status:'technical_trial_only'});
}
await fs.writeFile(run+'/node-z-multifidus-glb.json',JSON.stringify({passed:checks.length,checks,results},null,2),{flag:'wx'});
console.log(JSON.stringify({passed:checks.length,models:results.map(({rays,...r})=>r)}));
