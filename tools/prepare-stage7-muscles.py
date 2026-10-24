"""Non-destructive source inspection and trial export; no anatomical admission."""
import hashlib,json,pathlib,sys
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
ROOT=pathlib.Path(__file__).resolve().parents[1]
run=pathlib.Path(sys.argv[1]);out=ROOT/'build_stage7/source_trials';out.mkdir(parents=True,exist_ok=True)
R=np.array([[1,0,0],[0,0,1],[0,-1,0]])
ids=['FMA45856','FMA45857','FMA71309','FMA71442','FMA71443']
def stats(m):
 edges=m.edges_unique;graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(m.vertices),)*2)
 count,labels=connected_components(graph,directed=False)
 components=[]
 for label in range(count):
  v=m.vertices[labels==label];components.append(dict(vertices=len(v),bounds=v.min(0).tolist()+v.max(0).tolist()))
 return dict(vertices=len(m.vertices),triangles=len(m.faces),bounds=m.bounds.tolist(),watertight=bool(m.is_watertight),winding=bool(m.is_winding_consistent),volume=float(m.volume),degenerate=int((m.area_faces<1e-16).sum()),duplicateFaces=len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),components=components)
results=[]
for fma in ids:
 source=ROOT/'research/cache/stage7-sources'/f'{fma}.obj';sha=hashlib.sha256(source.read_bytes()).hexdigest()
 m=trimesh.load(source,force='mesh',process=False);m.vertices=m.vertices@R.T/1000
 result=dict(fma=fma,sha256=sha,metrics=stats(m))
 target=out/f'{fma}.glb'
 scene=trimesh.Scene();scene.add_geometry(m,node_name=fma,geom_name=fma)
 with target.open('xb')as f:f.write(scene.export(file_type='glb'))
 back=trimesh.load(target,force='mesh',process=False)
 result['roundtrip']={'trianglesEqual':len(m.faces)==len(back.faces),'facesEqual':bool(np.array_equal(m.faces,back.faces)),'maxVertexErrorM':float(np.max(np.abs(m.vertices-back.vertices))),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 assert result['roundtrip']['facesEqual'] and result['roundtrip']['maxVertexErrorM']<1e-6
 assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
 results.append(result)
 print(fma,{k:v for k,v in result['metrics'].items() if k!='components'},'components',len(result['metrics']['components']))
with(run/'candidate-geometry.json').open('x',encoding='utf8')as f:json.dump(results,f,indent=2)
