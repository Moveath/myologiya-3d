// Exact world-space arrays from the current atlas for bounded Blender review.
import fs from 'node:fs/promises';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {Vector3} from 'three';
const run=process.argv[2];globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const targets={neck:['b|','m|omohyoid'],leg:['b|hip_bone','b|sacrum','m|levator_ani','m|coccygeus','m|obturator_internus'], 'leg-extra':['b|hip_bone_left','b|coccyx']};
const rows=[];
for(const [file,names]of Object.entries(targets)){
 const bytes=Buffer.from(await fs.readFile('site/'+file+'-glb.txt','utf8'),'base64');
 const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');gltf.scene.updateMatrixWorld(true);
 gltf.scene.traverse(m=>{if(!m.isMesh)return;let n=m;while(n&&!/^[mboc]\|/.test(n.name))n=n.parent;if(!n||!names.some(x=>n.name.startsWith(x)))return;
 const p=m.geometry.attributes.position,idx=m.geometry.index,v=new Vector3(),positions=[],indices=[];
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);positions.push(...v.toArray());}
 for(let i=0;i<(idx?.count??p.count);i++)indices.push(idx?idx.getX(i):i);
 rows.push({file,name:n.name,positions,indices});
 });
}
await fs.writeFile(run+'/context-arrays.json',JSON.stringify(rows),{flag:'wx'});console.log(rows.map(x=>({name:x.name,triangles:x.indices.length/3})));
