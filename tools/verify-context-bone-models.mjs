// Check the actual meshopt and fallback supplements against unquantized GLBs.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {MeshBVH} from 'three-mesh-bvh';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
await MeshoptDecoder.ready;
const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
const provenance=JSON.parse(await fs.readFile(path.join(root,'research/context-bone-provenance.json'),'utf8'));
async function load(buffer){
  const scene=(await loader.parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'')).scene;
  scene.updateMatrixWorld(true);
  const meshes=new Map();
  scene.traverse(mesh=>{
    if(!mesh.isMesh)return;
    let node=mesh;while(node&&!node.name.startsWith('b|'))node=node.parent;
    assert.ok(node,'Named bone ancestor');
    const id=node.name.split('|')[1];assert.ok(!meshes.has(id),'One mesh per bone: '+id);
    // gltfpack uses integer POSITION attributes plus node scale/translation.
    // Convert to floats before applying the world transform; mutating a cloned
    // integer attribute would quantize/clamp the metre-space results again.
    const geometry=new THREE.BufferGeometry();
    const sourcePosition=mesh.geometry.attributes.position,positions=new Float32Array(sourcePosition.count*3);
    for(let i=0;i<sourcePosition.count;i++){
      positions[i*3]=sourcePosition.getX(i);positions[i*3+1]=sourcePosition.getY(i);positions[i*3+2]=sourcePosition.getZ(i);
    }
    geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
    if(mesh.geometry.index)geometry.setIndex(mesh.geometry.index.clone());
    geometry.applyMatrix4(mesh.matrixWorld);
    geometry.boundsTree=new MeshBVH(geometry,{indirect:true});
    meshes.set(id,geometry);
  });return meshes;
}
function count(g){return(g.index?.count||g.attributes.position.count)/3;}
function distance(a,b){
  const position=a.attributes.position,p=new THREE.Vector3();let max=0;
  for(let i=0;i<position.count;i++){
    p.fromBufferAttribute(position,i);
    max=Math.max(max,b.boundsTree.closestPointToPoint(p).distance);
  }return max*1000;
}
const records=[];
for(const section of ['arm','leg']){
  const high=await load(await fs.readFile(path.join(root,`build_context_bones/${section}_extra_hi.glb`)));
  const expected=Object.entries(provenance.bones).filter(([,b])=>b.ownerSection===section).map(([id])=>id).sort();
  assert.deepEqual([...high.keys()].sort(),expected);
  for(const suffix of ['','-q']){
    const asset=`${section}-extra${suffix}-glb.txt`;
    const packed=await load(Buffer.from(await fs.readFile(path.join(root,'site',asset),'utf8'),'base64'));
    assert.deepEqual([...packed.keys()].sort(),expected);
    for(const id of expected){
      const a=high.get(id),b=packed.get(id);
      assert.equal(count(a),provenance.bones[id].sourceTriangles,id+' source triangles');
      assert.equal(count(a),count(b),id+' packed triangles');
      const sourceToPackedMm=distance(a,b),packedToSourceMm=distance(b,a);
      assert.ok(Math.max(sourceToPackedMm,packedToSourceMm)<.1,`${id} quantization distance ${sourceToPackedMm} / ${packedToSourceMm} mm`);
      if(id.endsWith('_left')){b.computeBoundingBox();assert.ok(b.boundingBox.min.x>0,id+' original left side');}
      records.push({asset,id,triangles:count(b),sourceToPackedMm,packedToSourceMm});
    }
  }
}
const report={status:'passed',bones:9,assets:4,checks:records.length,
  sampledVertices:'All vertices of both source and packed meshes; bidirectional distance to triangle surfaces',
  anatomicalLandmarksVerified:false,geometryCompleteClaim:false,
  maximumDistanceMm:Math.max(...records.flatMap(r=>[r.sourceToPackedMm,r.packedToSourceMm])),records};
await fs.writeFile(path.join(root,'verify/context-bone-models.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,bones:report.bones,checks:report.checks,maximumDistanceMm:report.maximumDistanceMm}));
