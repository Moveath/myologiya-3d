// Decode the exact hosted assets; do not substitute an intermediate mesh.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3} from 'three';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'build_head/geometry_check');await fs.mkdir(output,{recursive:true});
globalThis.ProgressEvent??=class {constructor(type,init){this.type=type;Object.assign(this,init);}};
for(const filename of ['head-glb.txt','head-q-glb.txt']){
 const buffer=Buffer.from(await fs.readFile(path.join(root,'site',filename),'utf8'),'base64');
 const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
 const gltf=await loader.parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'');
 gltf.scene.updateMatrixWorld(true);const rows={};
 gltf.scene.traverse(mesh=>{
  if(!mesh.isMesh)return;let parent=mesh;while(parent&&!parent.name.startsWith('b|'))parent=parent.parent;if(!parent)return;
  const id=parent.name.split('|')[1],positions=mesh.geometry.getAttribute('position'),indices=mesh.geometry.getIndex(),v=new Vector3();
  const row=rows[id]??={vertices:[],faces:[]},offset=row.vertices.length/3;
  for(let i=0;i<positions.count;i++){v.fromBufferAttribute(positions,i).applyMatrix4(mesh.matrixWorld);row.vertices.push(...v.toArray());}
  for(let i=0;i<(indices?.count??positions.count);i++)row.faces.push(offset+(indices?indices.getX(i):i));
 });
 await fs.writeFile(path.join(output,filename.replace('.txt','.json')),JSON.stringify(rows));
 console.log(filename,Object.keys(rows).length,'decoded bones');
}
