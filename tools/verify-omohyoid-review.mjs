import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {BufferGeometry,BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Vector3,Raycaster} from 'three';
import {MeshBVH,acceleratedRaycast} from 'three-mesh-bvh';
const run=process.argv[2],checks=[],data=JSON.parse(await fs.readFile(run+'/blender-review-arrays.json'));
const check=(v,n)=>{assert.ok(v,n);checks.push(n);};
check(crypto.createHash('sha256').update(await fs.readFile(data.source)).digest('hex')===data.sha256,'Current neck GLB matches diagnostic context');
const box={window:{}};vm.createContext(box);
for(const f of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','data-muscle-recovery','data-neck-recovery'])vm.runInContext(await fs.readFile('site/'+f+'.js','utf8'),box);
const A=box.window.ATLAS;
for(const id of ['omohyoid_right','omohyoid_left']){
 const rows=data.rows.filter(r=>r.name==='m|'+id+'|');check(rows.length===1,'One whole muscle mesh '+id);
 check(['superior','inferior'].every(k=>A.muscles[id].parts[k].noModel),'Both unadmitted parts remain noModel '+id);
 const row=rows[0],g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float32Array(row.positions),3));g.setIndex(row.indices);
 const before=Array.from(g.index.array);g.computeVertexNormals();g.boundsTree=new MeshBVH(g,{indirect:true});
 check(JSON.stringify(before)===JSON.stringify(Array.from(g.index.array)),'Face order retained '+id);
 const m=new Mesh(g,new MeshBasicMaterial({side:DoubleSide}));m.updateMatrixWorld();
 for(let i=0;i<8;i++){
  const f=i*431%(g.index.count/3),p=new Vector3(),n=new Vector3();
  for(let k=0;k<3;k++){const ix=g.index.getX(f*3+k);p.add(new Vector3().fromBufferAttribute(g.attributes.position,ix));n.add(new Vector3().fromBufferAttribute(g.attributes.normal,ix));}
  p.multiplyScalar(1/3);n.normalize();const ray=new Raycaster(p.clone().addScaledVector(n,.02),n.negate()),a=[],b=[];
  Mesh.prototype.raycast.call(m,ray,a);acceleratedRaycast.call(m,ray,b);a.sort((x,y)=>x.distance-y.distance);b.sort((x,y)=>x.distance-y.distance);
  check(a.length>0&&a.length===b.length&&Math.abs(a[0].distance-b[0].distance)<1e-7&&a[0].faceIndex===b[0].faceIndex,'Native/BVH '+id+' ray '+i);
 }
}
const inventory={muscles:Object.keys(A.muscles).length,muscleNoModel:Object.values(A.muscles).filter(x=>x.noModel).length,partsNoModel:Object.values(A.muscles).flatMap(m=>Object.values(m.parts||{})).filter(x=>x.noModel).length,boneNoModel:Object.values(A.bones).filter(x=>x.noModel).length};
check(inventory.muscleNoModel===14&&inventory.partsNoModel===21&&inventory.boneNoModel===20,'All noModel counts retained');
await fs.writeFile(run+'/node-review.json',JSON.stringify({status:'passed',checks,inventory,anatomicalMasks:0},null,2),{flag:'wx'});
console.log(JSON.stringify({checks:checks.length,inventory}));
