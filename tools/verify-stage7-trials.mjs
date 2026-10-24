import fs from 'node:fs/promises';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {BufferGeometry,BufferAttribute,Matrix4,Box3,Line3} from 'three';
import {MeshBVH} from 'three-mesh-bvh';
import {scan,pairKind} from './audit-self-intersections.mjs';
const run=process.argv[2], rows=JSON.parse(await fs.readFile(run+'/context-arrays.json'));
globalThis.ProgressEvent??=class{constructor(type,init){Object.assign(this,init);}};
const write=(name,obj)=>fs.writeFile(run+'/'+name,JSON.stringify(obj,null,2),{flag:'wx'});
function tree(v,f){const g=new BufferGeometry().setAttribute('position',new BufferAttribute(new Float64Array(v),3));g.setIndex(new BufferAttribute(new Uint32Array(f),1));g.computeBoundingBox();return {g,b:new MeshBVH(g,{indirect:true,verbose:false})};}
const candidates=[];
for(const fma of ['FMA45856','FMA45857','FMA71309','FMA71442','FMA71443']){
 const bytes=await fs.readFile('build_stage7/source_trials/'+fma+'.glb');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');let g;gltf.scene.traverse(m=>{if(m.isMesh)g=m.geometry;});
 const v=Float64Array.from(g.attributes.position.array),f=Uint32Array.from(g.index.array),self=scan(v,f,12000);
 await write('self-'+fma+'.json',self);candidates.push({fma,...tree(v,f)});console.log(fma,self.complete,self.counts);
}
const context=rows.filter(x=>!x.name.startsWith('m|omohyoid')).map(x=>({...x,...tree(x.positions,x.indices)}));
const pairs=[];
for(const a of candidates)for(const b of [...context,...candidates]){
 if(b===a||(b.fma&&b.fma<=a.fma))continue;
 if(!a.g.boundingBox.intersectsBox(b.g.boundingBox))continue;
 const row={a:a.fma,b:b.fma||b.name,complete:true,crossing:0,coplanar:0,maxIntersectionLineM:0};const start=Date.now(),line=new Line3();
 a.b.bvhcast(b.b,new Matrix4(),{intersectsTriangles(t,u){if(Date.now()-start>10000){row.complete=false;return true;}const kind=pairKind(t,u);if(kind==='crossing'){row.crossing++;t.intersectsTriangle(u,line);row.maxIntersectionLineM=Math.max(row.maxIntersectionLineM,line.distance());}if(kind==='coplanarOverlap')row.coplanar++;return false;}});
 pairs.push(row);
}
await write('candidate-pairs.json',pairs);console.log(JSON.stringify(pairs.filter(x=>x.crossing||x.coplanar)));
