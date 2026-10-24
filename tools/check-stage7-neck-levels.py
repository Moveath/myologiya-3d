"""Diagnostic endpoint proximity, explicitly not anatomical attachment proof."""
import json,pathlib,sys
import numpy as np
import trimesh
run=pathlib.Path(sys.argv[1]);R=np.array([[1,0,0],[0,0,1],[0,-1,0]])
m=trimesh.load('research/cache/stage7-sources/FMA71309.obj',force='mesh',process=False)
v,inv=np.unique(m.vertices,axis=0,return_inverse=True);m=trimesh.Trimesh(v@R.T/1000,inv[m.faces],process=False)
bones={r['name']:trimesh.Trimesh(np.array(r['positions']).reshape(-1,3),np.array(r['indices']).reshape(-1,3),process=False) for r in json.loads((run/'context-arrays.json').read_text())if r['file']=='neck'and r['name'].startswith('b|')and 'hyoid'not in r['name']}
rows=[]
for c in sorted(m.split(only_watertight=False),key=lambda c:-c.bounds[1,1]):
 row={'bounds':c.bounds.tolist(),'triangles':len(c.faces),'ends':{}}
 for end in ['upper','lower']:
  q=c.vertices[np.argsort(c.vertices[:,1])[-8:]if end=='upper'else np.argsort(c.vertices[:,1])[:8]]
  distances=sorted((float(np.median(trimesh.proximity.closest_point_naive(b,q)[1]))*1000,k)for k,b in bones.items())
  row['ends'][end]=[{'bone':k,'medianDistanceMM':d}for d,k in distances[:2]]
 rows.append(row)
with(run/'neck-endpoint-diagnostics.json').open('x',encoding='utf8')as f:json.dump({'rows':rows,'limitation':'Endpoint-to-surface proximity is not proof of insertion; no levels or pins assigned automatically.'},f,indent=2)
print(json.dumps(rows[:2]))
