// Verify source contracts and distances on the actual compressed public model.
// Distance to a surface is not an independent proof of an anatomical name.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {MeshBVH} from 'three-mesh-bvh';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const box={window:{}};vm.createContext(box);
for(const name of ['data.js','data-leg.js','data-head.js','data-neck.js','pins.js','pins-leg.js','pins-head.js','pins-neck.js'])
  vm.runInContext(await fs.readFile(path.join(root,'site',name),'utf8'),box,{filename:name});
const A=box.window.ATLAS;
const muscles=Object.entries(A.muscles).filter(([,m])=>m.g.startsWith('neck_'));
const bones=Object.entries(A.bones).filter(([,b])=>b.g.startsWith('neck_'));
assert.equal(muscles.length,62);assert.equal(bones.length,8);
const dataIds=[...muscles,...bones].map(([id])=>id);
assert.equal(new Set(A.pins.map(p=>p.id)).size,A.pins.length);
let fieldChecks=0;
const unresolved=[];
const terminology=JSON.parse(await fs.readFile(path.join(root,'verify/ifaa-neck-muscles.json'),'utf8')).terms;
const normalizeTerm=s=>s.toLowerCase().replace(/^m\.\s*/,'musculus ').split(';')[0].trim();
let nomenclatureChecks=0;
for(const [id,m] of muscles){
  for(const [part,d] of [['',m],...Object.entries(m.parts||{})]){
    if(d.code){
      assert.ok(terminology[d.code],`${id}:${part} has an IFAA code`);
      assert.equal(normalizeTerm(d.lat),normalizeTerm(terminology[d.code].lat),`${id}:${part} TA98`);
      nomenclatureChecks++;
    }else assert.ok(part && d.x?.includes('Описательное'),`${id}:${part} has explicitly descriptive terminology`);
    for(const field of ['o','i','a','n','s']){
      if(part&&!d[field])continue;
      assert.equal(typeof d[field],'string',`${id}:${part}:${field}`);
      const refs=d.fieldRefs?.[field]||[];
      if(d.fieldStatus?.[field]==='unconfirmed'){
        unresolved.push({id,part,field});continue;
      }
      assert.ok(new Set(refs.map(r=>r.url.split('#')[0])).size>=2,`${id}:${part}:${field} requires two sources`);
      assert.ok(refs.every(r=>r.locator&&/^https:\/\//.test(r.url)),`${id}:${part}:${field} locators`);
      fieldChecks++;
    }
  }
}
await MeshoptDecoder.ready;
const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
const buffer=Buffer.from(await fs.readFile(path.join(root,'site/neck-glb.txt'),'utf8'),'base64');
const gltf=await loader.parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'');
gltf.scene.updateMatrixWorld(true);
const structures=new Map();
gltf.scene.traverse(mesh=>{
  if(!mesh.isMesh)return;
  let node=mesh;while(node&&!/^[mboc]\|/.test(node.name))node=node.parent;
  assert.ok(node,mesh.name);
  const [kind,id,part]=node.name.split('|');
  if(kind==='c')return;
  assert.ok(dataIds.includes(id),'Uncatalogued geometry '+id);
  if(part)assert.ok(A.muscles[id].parts[part],`${id}:${part}`);
  if(!structures.has(id))structures.set(id,[]);
  structures.get(id).push({mesh,part,kind});
});
assert.equal(structures.size,dataIds.length);
for(const [id,m] of muscles)for(const [part,d] of Object.entries(m.parts||{})){
  const exists=structures.get(id).some(s=>s.part===part);
  assert.equal(!d.noModel,exists,`${id}:${part} noModel reflects actual named mesh`);
}
const pins=A.pins.filter(p=>p.id.startsWith('neck_'));
const distances=[];
for(const pin of pins){
  assert.ok(new Set(pin.refs.map(r=>r.url.split('#')[0])).size>=2,pin.id);
  assert.ok(pin.refs.every(r=>r.locator),pin.id);
  if(!pin.p){assert.ok(pin.modelNote.includes('не проверено'));continue;}
  const original=structures.get(pin.b);
  let distance=Infinity;
  for(const {mesh} of original){
    mesh.geometry.boundsTree??=new MeshBVH(mesh.geometry,{indirect:true});
    const point=new THREE.Vector3(...pin.p);
    mesh.worldToLocal(point);
    const hit=mesh.geometry.boundsTree.closestPointToPoint(point);
    const world=mesh.localToWorld(hit.point.clone());
    distance=Math.min(distance,world.distanceTo(new THREE.Vector3(...pin.p)));
  }
  assert.ok(distance<=0.0003,`${pin.id} ${(distance*1000).toFixed(4)}mm`);
  distances.push({id:pin.id,distanceMm:distance*1000});
}
assert.ok(distances.length>0);
const report={status:'passed',bones:bones.length,muscles:muscles.length,structures:structures.size,
  sourceFieldChecks:fieldChecks,nomenclatureChecks,unresolvedFields:unresolved,terms:pins.length,located:distances.length,
  maximumSurfaceDistanceMm:Math.max(...distances.map(d=>d.distanceMm)),distances,
  limitation:'Distance validates mesh correspondence only, not anatomical identity or completeness.'};
const {createEvidenceRun}=await import('./evidence-run.mjs');
const evidence=await createEvidenceRun(root,'neck-data-geometry');
await evidence.write('neck-data-geometry.json',report);
console.log('Evidence:',evidence.dir);
console.log(JSON.stringify({...report,distances:undefined}));
