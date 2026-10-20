// Anatomical evidence contracts and the actual compressed publication geometry.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {MeshBVH} from 'three-mesh-bvh';
import {createEvidenceRun} from './evidence-run.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const box={window:{}};vm.createContext(box);
for(const name of ['data.js','data-leg.js','data-head.js','data-neck.js','data-thorax.js','pins.js','pins-leg.js','pins-head.js','pins-neck.js','pins-thorax.js'])
  vm.runInContext(await fs.readFile(path.join(root,'site',name),'utf8'),box,{filename:name});
const A=box.window.ATLAS;
const muscles=Object.entries(A.muscles).filter(([,m])=>m.g.startsWith('thorax_'));
const bones=Object.entries(A.bones).filter(([,b])=>b.g.startsWith('thorax_'));
const soft=Object.entries(A.bones).filter(([,b])=>b.g==='b_soft_thorax');
assert.equal(muscles.length,43);assert.equal(bones.length,37);assert.equal(soft.length,2);
assert.equal(muscles.filter(([,m])=>m.noModel).length,3);
assert.equal(new Set(A.pins.map(p=>p.id)).size,A.pins.length);
const terminology=JSON.parse(await fs.readFile(path.join(root,'verify/ifaa-thorax-muscles.json'),'utf8')).terms;
const normal=s=>s.toLowerCase().replace(/^\(|\)$/g,'').replace(/^m\.\s*/,'musculus ').replace(/^mm\.\s*/,'musculi ').replace(/^lig\.\s*/,'ligamentum ').split(';')[0].trim();
let fieldChecks=0,nomenclatureChecks=0;const unresolved=[];
function evidence(refs,key){assert.ok(new Set((refs||[]).map(r=>r.url.split('#')[0])).size>=2,key+' two sources');assert.ok(refs.every(r=>r.locator&&/^https:\/\//.test(r.url)),key+' locators');fieldChecks++;}
function term(d,key){
  assert.ok(terminology[d.code],key+' IFAA code');
  let raw=normal(terminology[d.code].lat);
  if(d.code==='A04.3.02.212'){
    assert.equal(raw,'musculi rotator thoracis');
    raw='musculi rotatores thoracis'; // printed TA98 / Kolesnikov 2003, documented source exception
  }
  assert.equal(normal(d.lat),raw,key+' TA98');nomenclatureChecks++;
}
for(const [id,m] of muscles){
  for(const [part,d] of [['',m],...Object.entries(m.parts||{})]){
    if(d.code)term(d,id+':'+part);else assert.ok((d.x+' '+m.note).toLowerCase().includes('описательное'),id+':'+part+' descriptive title');
    for(const field of ['o','i','a','n','s','x']){
      if(!d[field]&&(part||field==='x'))continue;
      assert.equal(typeof d[field],'string',id+':'+part+':'+field);
      if(d.fieldStatus?.[field]==='unconfirmed'){unresolved.push({id,part,field});continue;}
      evidence(d.fieldRefs?.[field],id+':'+part+':'+field);
    }
  }
  for(const feature of m.features||[]){term(feature,id+':'+feature.code);evidence(feature.refs,id+':'+feature.code);}
  if(m.noModel)assert.ok(m.contextTargets.every(id=>A.bones[id]),id+' actual context links');
}
for(const t of A.thoraxWholeTerms)evidence(t.refs,t.c);
await MeshoptDecoder.ready;
const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
const buffer=Buffer.from(await fs.readFile(path.join(root,'site/thorax-glb.txt'),'utf8'),'base64');
const gltf=await loader.parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'');
gltf.scene.updateMatrixWorld(true);
const dataIds=[...muscles,...bones,...soft].map(([id])=>id),structures=new Map();
gltf.scene.traverse(mesh=>{
  if(!mesh.isMesh)return;
  let node=mesh;while(node&&!/^[mboc]\|/.test(node.name))node=node.parent;
  assert.ok(node,mesh.name);
  const [kind,id,part]=node.name.split('|');if(kind==='c')return;
  assert.ok(dataIds.includes(id),'Uncatalogued geometry '+id);
  if(part&&kind==='m')assert.ok(A.muscles[id].parts[part],id+':'+part);
  if(!structures.has(id))structures.set(id,[]);
  structures.get(id).push({mesh,part,kind});
});
assert.equal(structures.size,79);
assert.equal(structures.get('sternum').length,3,'All three original sternal components registered');
for(const [id,m] of muscles){
  assert.equal(structures.has(id),!m.noModel,id+' noModel');
  for(const [part,d] of Object.entries(m.parts||{}))assert.equal(!d.noModel,(structures.get(id)||[]).some(s=>s.part===part),id+':'+part);
}
const pins=A.pins.filter(p=>p.id.startsWith('thorax_')),distances=[];
for(const pin of pins){
  if(pin.anatomyVerification==='incomplete'){
    assert.equal(pin.evidenceScope,'nomenclature_and_body_region_only');
    assert.equal(pin.p,null,'Unresolved topography cannot get a fabricated marker');
    unresolved.push({id:pin.id,field:'topography'});
  }else evidence(pin.refs,pin.id);
  if(!pin.p){assert.ok(pin.modelNote,pin.id+' explanation');continue;}
  let distance=Infinity;
  for(const {mesh} of structures.get(pin.b)){
    mesh.geometry.boundsTree??=new MeshBVH(mesh.geometry,{indirect:true});
    const point=mesh.worldToLocal(new THREE.Vector3(...pin.p));
    const hit=mesh.geometry.boundsTree.closestPointToPoint(point);
    distance=Math.min(distance,mesh.localToWorld(hit.point.clone()).distanceTo(new THREE.Vector3(...pin.p)));
  }
  assert.ok(distance<=0.0003,`${pin.id} ${(distance*1000).toFixed(4)}mm`);
  distances.push({id:pin.id,distanceMm:distance*1000});
}
assert.ok(distances.length>0);
const report={status:'passed',bones:bones.length,muscles:muscles.length,structures:structures.size,
  sourceFieldChecks:fieldChecks,nomenclatureChecks,unresolvedFields:unresolved,terms:pins.length,located:distances.length,
  maximumSurfaceDistanceMm:Math.max(...distances.map(d=>d.distanceMm)),distances,
  limitation:'Mesh correspondence only; no independent anatomical acceptance or complete-feature geometry claim.'};
const run=await createEvidenceRun(root,'thorax-data');await run.write('thorax-data-geometry.json',report);
console.log(JSON.stringify({...report,distances:undefined,evidence:run.dir}));
