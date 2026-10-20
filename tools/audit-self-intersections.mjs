// Diagnostic only: exhaustive BVH traversal per mesh, not anatomical acceptance.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {BufferGeometry,BufferAttribute,Matrix4,Line3,Vector3} from 'three';
import {MeshBVH,ExtendedTriangle} from 'three-mesh-bvh';

const EPS = 1e-10; // after centering and scaling each mesh to unit maximum extent
const line = new Line3(), normal = new Vector3(), otherNormal = new Vector3();
function overlapArea(a,b,n) {
  const axis = Math.abs(n.x)>Math.abs(n.y) ? (Math.abs(n.x)>Math.abs(n.z)?0:2) : (Math.abs(n.y)>Math.abs(n.z)?1:2);
  const project = v => axis===0 ? [v.y,v.z] : axis===1 ? [v.x,v.z] : [v.x,v.y];
  const orient = (p,q,r) => (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);
  let poly = [a.a,a.b,a.c].map(project);
  const clip = [b.a,b.b,b.c].map(project), sign = Math.sign(orient(...clip));
  for (let i=0;i<3 && poly.length;i++) {
    const p=clip[i],q=clip[(i+1)%3],next=[];
    for (let j=0;j<poly.length;j++) {
      const s=poly[j],t=poly[(j+1)%poly.length],ds=sign*orient(p,q,s),dt=sign*orient(p,q,t);
      if (ds>=0) next.push(s);
      if ((ds<0)!==(dt<0)) {const u=ds/(ds-dt);next.push([s[0]+u*(t[0]-s[0]),s[1]+u*(t[1]-s[1])]);}
    }
    poly=next;
  }
  let area=0;
  for(let i=1;i+1<poly.length;i++) area+=Math.abs(orient(poly[0],poly[i],poly[i+1]))/2;
  return area;
}

export function pairKind(a,b) {
  a.getNormal(normal); b.getNormal(otherNormal);
  if (normal.lengthSq()===0 || otherNormal.lengthSq()===0) return 'degenerate';
  if (!a.intersectsTriangle(b,line,true)) return 'none';
  const av=[a.a,a.b,a.c],bv=[b.a,b.b,b.c];
  const shared=av.filter(p=>bv.some(q=>p.equals(q)));
  if (shared.length===3) return 'duplicate';
  // The library uses this angular tolerance too; near-parallel cases remain diagnostic.
  if (Math.abs(normal.dot(otherNormal))>1-1e-10)
    return overlapArea(a,b,normal)>EPS*EPS ? 'coplanarOverlap' : 'contact';
  if (shared.length===2) return 'adjacent';
  return line.distance()>EPS ? 'crossing' : 'contact';
}

export function scan(v,f,limitMs=60000) {
  const start=Date.now(),positions=v.slice();
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<positions.length;i++) {const j=i%3;min[j]=Math.min(min[j],positions[i]);max[j]=Math.max(max[j],positions[i]);}
  const extent=Math.max(...max.map((x,j)=>x-min[j]));
  if (!(extent>0)) return {complete:false,reason:'zero extent'};
  for(let i=0;i<positions.length;i++){const j=i%3;positions[i]=(positions[i]-(min[j]+max[j])/2)/extent;}
  const geometry=new BufferGeometry();
  geometry.setAttribute('position',new BufferAttribute(positions,3));geometry.setIndex(new BufferAttribute(f.slice(),1));
  const bvh=new MeshBVH(geometry,{indirect:true,maxLeafTris:8,verbose:false});
  const counts={candidatePairs:0,degenerate:0,duplicate:0,coplanarOverlap:0,crossing:0,contact:0,adjacent:0};
  const examples=[];let timedOut=false;
  bvh.bvhcast(bvh,new Matrix4(),{intersectsTriangles(a,b,x,y){
    // 0.8.3 supplies BVH offsets here, even in indirect mode. Resolve once.
    const i=bvh.resolveTriangleIndex(x),j=bvh.resolveTriangleIndex(y);
    if(i>=j)return false;
    counts.candidatePairs++;
    if(counts.candidatePairs%8192===0 && Date.now()-start>limitMs){timedOut=true;return true;}
    const kind=pairKind(a,b);
    if(kind!=='none')counts[kind]++;
    if(['crossing','coplanarOverlap','duplicate'].includes(kind)&&examples.length<30)examples.push({i,j,kind});
    return false;
  }});
  geometry.dispose();
  return {complete:!timedOut,reason:timedOut?'time budget exceeded':null,triangles:f.length/3,
    durationMs:Date.now()-start,extent,counts,examples};
}

if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
  const cache=path.join(root,'.venv/geometry-audit-cache');
  const output=path.resolve(process.argv[2]??'research/stage4-closure-2026-10-16/self-intersections.json');
  // Optional FILE MESH_ID MILLISECONDS repeat only an unfinished mesh.
  const filterFile=process.argv[3], filterMesh=process.argv[4]===undefined?null:Number(process.argv[4]);
  const limitMs=Number(process.argv[5]??60000);
  const all=JSON.parse(await fs.readFile(path.join(cache,'index.json'),'utf8')).filter(x=>!filterFile||x.file===filterFile);
  const results=[];
  const existing=new Map();
  const report=()=>({limitMs,method:'three-mesh-bvh 0.8.3 indirect self-bvhcast, ExtendedTriangle narrow phase; centered unit extent; EPS=1e-10. Coplanar overlap uses 2D clipping. Exact duplicate/edge-contact separated. No cross-object test, no exact arithmetic certification. Degenerate faces cannot be certified. Explicit incomplete flag.',results});
  for(const item of all){
    const meta=JSON.parse(await fs.readFile(path.join(cache,item.file+'.json'),'utf8'));
    for(const mesh of meta.meshes){
      if(filterMesh!==null&&mesh.id!==filterMesh)continue;
      const vb=await fs.readFile(path.join(cache,mesh.prefix+'.v')),fb=await fs.readFile(path.join(cache,mesh.prefix+'.f'));
      const crypto=await import('node:crypto');
      const hash=crypto.createHash('sha256').update(vb).update(fb).digest('hex');
      let result=existing.get(hash),reuse=!!result;
      if(!result){result=scan(new Float64Array(vb.buffer.slice(vb.byteOffset,vb.byteOffset+vb.byteLength)),new Uint32Array(fb.buffer.slice(fb.byteOffset,fb.byteOffset+fb.byteLength)),limitMs);existing.set(hash,result);}
      results.push({file:item.file,sha256:item.sha256,mesh:mesh.id,owner:mesh.owner,geometryHash:hash,reused:reuse,...result});
    }
    await fs.writeFile(output,JSON.stringify(report(),null,2)+'\n');
    console.log(item.file,meta.meshes.length,'meshes complete');
  }
  console.log(JSON.stringify({meshes:results.length,unique:existing.size,incomplete:results.filter(r=>!r.complete).length}));
}
