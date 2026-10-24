"""Screen cycles for a clear centre ray; this is NOT anatomical proof."""
import json,sys
from pathlib import Path
import numpy as np,trimesh
def intersects(triangles,origin,direction):
 # Moller-Trumbore, all source triangles. Bounded small candidate set, no rtree dependency.
 a=triangles[:,0];e1=triangles[:,1]-a;e2=triangles[:,2]-a
 h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);valid=abs(det)>1e-12
 inv=np.zeros_like(det);inv[valid]=1/det[valid];s=origin-a
 u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=inv*(q@direction)
 t=inv*np.einsum('ij,ij->i',e2,q)
 return bool(np.any(valid&(u>=0)&(v>=0)&(u+v<=1)&(t>0)))
run=Path(sys.argv[1]);rows=json.loads((run/'head-glb-source.json').read_text(encoding='utf8'))['rows']
cycles=json.loads((run/'candidate-cycles.json').read_text(encoding='utf8'));out=[]
for r in rows:
 v=np.array(r['positions']).reshape(-1,3);f=np.array(r['indices']).reshape(-1,3);m=trimesh.Trimesh(v,f,process=False)
 candidates=[c for c in cycles if c['bone']==r['bone']]
 origins=np.array([c['center'] for c in candidates]);directions=np.array([c['view'] for c in candidates],float);directions/=np.linalg.norm(directions,axis=1)[:,None]
 hits=[intersects(m.triangles,o+d,-d) for o,d in zip(origins,directions)]
 for c,hit in zip(candidates,hits):
  if hit:continue
  p=v[np.array(c['edges'])[:,0]];d=np.array(c['view'],float);d/=np.linalg.norm(d)
  area=abs(np.sum(np.cross(p-p[0],np.roll(p,-1,axis=0)-p[0]),axis=0)@d)/2
  if area<.000002:continue
  c['projectedAreaMm2']=area*1e6;out.append(c)
with (run/'clear-centre-candidates.json').open('x',encoding='utf8') as file:json.dump(out,file)
for c in out:print(c['id'],len(c['edges']),np.round(c['center'],4).tolist(),round(c['projectedAreaMm2'],1))
