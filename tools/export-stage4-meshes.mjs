// Read exact hosted GLBs with pinned r170; only audit cache files are written.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3,REVISION} from 'three';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const cache=path.join(root,'.venv/geometry-audit-cache');
await fs.mkdir(cache,{recursive:true});
globalThis.ProgressEvent??=class {constructor(type,init){Object.assign(this,{type},init)}};
const plan=await fs.readFile(path.join(root,'ANATOMY_REPAIR_PLAN.md'),'utf8');
const section=plan.split('## Приложение G.')[1].split('## Приложение H.')[0];
const names=[...section.matchAll(/\| `([^`]+(?:\.txt|\.glb))` \|/g)].map(m=>m[1]);
if(names.length!==23)throw Error('Expected the 23 registered packages');
const index=[];
for(const filename of names){
 const source=await fs.readFile(path.join(root,'site',filename));
 const buffer=filename.endsWith('.txt')?Buffer.from(source.toString('utf8'),'base64'):source;
 const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
 // Node has no DOM image decoder. Geometry uses the original buffer; browser
 // checks separately cover materials/images, which are outside this export.
 loader.register(()=>({name:'AUDIT_GEOMETRY_ONLY',loadTexture:()=>Promise.resolve(null)}));
 const gltf=await loader.parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'');
 gltf.scene.updateMatrixWorld(true);const meshes=[];
 gltf.scene.traverse(mesh=>{if(mesh.isMesh)meshes.push(mesh)});
 const meta={source:filename,sha256:crypto.createHash('sha256').update(source).digest('hex'),three:REVISION,imagesSkipped:true,meshes:[]};
 for(let j=0;j<meshes.length;j++){
  const mesh=meshes[j],pos=mesh.geometry.getAttribute('position'),normal=mesh.geometry.getAttribute('normal'),idx=mesh.geometry.index;
  let owner=mesh;while(owner&&!/^[mboc]\|/.test(owner.name))owner=owner.parent;
  const prefix=filename+'.'+j;const vertices=new Float64Array(pos.count*3),normals=new Float64Array(normal?pos.count*3:0),faces=new Uint32Array(idx?.count??pos.count);
  for(let i=0;i<pos.count;i++){vertices.set([pos.getX(i),pos.getY(i),pos.getZ(i)],3*i);if(normal)normals.set([normal.getX(i),normal.getY(i),normal.getZ(i)],3*i)}
  for(let i=0;i<faces.length;i++)faces[i]=idx?idx.getX(i):i;
  for(const [ext,data] of [['v',vertices],['n',normals],['f',faces]])await fs.writeFile(path.join(cache,prefix+'.'+ext),Buffer.from(data.buffer));
  meta.meshes.push({id:j,name:mesh.name,owner:owner?.name??null,vertices:pos.count,faces:faces.length/3,normalCount:normal?.count??0,positionType:pos.array.constructor.name,normalized:pos.normalized,matrix:mesh.matrixWorld.toArray(),determinant:mesh.matrixWorld.determinant(),prefix});
 }
 await fs.writeFile(path.join(cache,filename+'.json'),JSON.stringify(meta));index.push({file:filename,meshes:meshes.length,sha256:meta.sha256});
 console.log(filename,meshes.length,'decoded');
}
await fs.writeFile(path.join(cache,'index.json'),JSON.stringify(index));

