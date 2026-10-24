// Read-only extraction of the actual r170/Meshopt assets, including world transforms.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3, REVISION} from 'three';
const run=path.resolve(process.argv[2]);
if(REVISION!=='170')throw Error('r170 required');
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,{type},init);}};
const arrays={},assets=[];
for(const file of ['arm-glb.txt','arm-extra-glb.txt','leg-glb.txt','leg-extra-glb.txt']){
 const source=await fs.readFile('site/'+file),bytes=Buffer.from(source.toString(),'base64');
 const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
 loader.register(()=>({name:'MIRROR_SCREEN',loadTexture:()=>Promise.resolve(null)}));
 const scene=(await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')).scene;
 scene.updateMatrixWorld(true);
 scene.traverse(mesh=>{
  if(!mesh.isMesh)return;let owner=mesh;
  while(owner&&!owner.name.startsWith('b|'))owner=owner.parent;
  if(!owner)return;
  const id=owner.name.slice(2),key=file+':'+id;
  const row=arrays[key]??={id,file,vertices:[],faces:[],determinants:[]};
  const p=mesh.geometry.attributes.position,index=mesh.geometry.index,v=new Vector3(),offset=row.vertices.length/3;
  row.determinants.push(mesh.matrixWorld.determinant());
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);row.vertices.push(...v.toArray());}
  for(let i=0;i<(index?.count??p.count);i+=3){
   const face=[0,1,2].map(j=>offset+(index?index.getX(i+j):i+j));
   // Flatten a negative world determinant without leaving inverted winding.
   if(mesh.matrixWorld.determinant()<0)[face[1],face[2]]=[face[2],face[1]];
   row.faces.push(...face);
  }
 });
 assets.push({file:'site/'+file,sha256:createHash('sha256').update(source).digest('hex'),bytes:source.length});
}
await fs.writeFile(path.join(run,'right-source-arrays.json'),JSON.stringify(arrays),{flag:'wx'});
await fs.writeFile(path.join(run,'right-source-assets.json'),JSON.stringify(assets,null,2),{flag:'wx'});
console.log(JSON.stringify({assets:assets.length,owners:Object.values(arrays).map(r=>({file:r.file,id:r.id,triangles:r.faces.length/3}))}));
