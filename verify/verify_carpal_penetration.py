"""Addressed numerical penetration samples; no physiological acceptance threshold."""
import json,pathlib,sys,numpy as np,trimesh
r=pathlib.Path(sys.argv[1]);name=sys.argv[2]
a=json.loads((r/'mesh-arrays.json').read_text());m={k:trimesh.Trimesh(np.array(v['vertices']).reshape(-1,3),np.array(v['faces']).reshape(-1,3),process=False) for k,v in a.items()}
pairs=[(p['a'],p['b']) for p in json.loads((r/'joint-intersections.json').read_text())['cross'] if p['counts'].get('crossing') or p['counts'].get('coplanarOverlap')]
results=[]
for p,q in pairs:
 for x,y in [(p,q),(q,p)]:
  pts=np.concatenate([m[x].vertices,m[x].triangles_center]);t=m[y].triangles;inside=[]
  for i in range(0,len(pts),32):
   v=t[None,:,:,:]-pts[i:i+32,None,None,:];u,w,z=v[:,:,0],v[:,:,1],v[:,:,2];lu,lw,lz=[np.linalg.norm(s,axis=2) for s in (u,w,z)]
   n=np.einsum('ijk,ijk->ij',u,np.cross(w,z));d=lu*lw*lz+np.einsum('ijk,ijk->ij',u,w)*lz+np.einsum('ijk,ijk->ij',w,z)*lu+np.einsum('ijk,ijk->ij',z,u)*lw
   winding=np.sum(2*np.arctan2(n,d),axis=1)/(4*np.pi);inside.extend((i+np.where(abs(winding)>.5)[0]).tolist())
  d=[]
  for chunk in np.array_split(pts[inside],max(1,len(inside)//20)):
   if len(chunk):d.extend(trimesh.proximity.closest_point_naive(m[y],chunk)[1].tolist())
  results.append(dict(a=x,b=y,testedVerticesAndFaceCentres=len(pts),insideSamples=len(inside),maxSamplePenetrationMM=max(d,default=0)*1000,affectedSourceFaces=[int(i-len(m[x].vertices)) for i in inside if i>=len(m[x].vertices)]))
with (r/name).open('x') as f:json.dump(dict(rows=results,method='Solid-angle winding for all vertices and triangle centres; nearest triangle distance. Sampled penetration, not exact maximum or biological threshold.'),f,indent=2)
print(json.dumps([{k:v for k,v in r.items() if k!='affectedSourceFaces'} for r in results]))
