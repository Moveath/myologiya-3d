"""Validate source-edge annotations; no anatomical acceptance is inferred."""
import json,sys
from pathlib import Path
from collections import Counter
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1];run=ROOT/sys.argv[1]
rows=json.loads((run/'head-glb-source.json').read_text(encoding='utf8'))['rows']
data=json.loads((ROOT/'scripts/skull_region_expansion_annotations.json').read_text(encoding='utf8'))
result=[]
for r in data['regions']:
 s=next(x for x in rows if x['bone']==r['bone']);v=np.array(s['positions']).reshape(-1,3);f=np.array(s['indices']).reshape(-1,3)
 m=trimesh.Trimesh(v,f,process=False);allowed={tuple(e) for e in m.edges_unique}
 edges=[tuple(sorted(e)) for e in r['edges']];counts=Counter(i for e in edges for i in e)
 assert len(set(edges))==len(edges) and all(e in allowed for e in edges)
 assert set(counts.values())=={2},'Not a closed simple cycle'
 seen={edges[0][0]}
 while True:
  previous=len(seen)
  for a,b in edges:
   if a in seen or b in seen:seen.update([a,b])
  if len(seen)==previous:break
 assert len(seen)==len(counts),'Disconnected contour'
 if r.get('side'):assert all(v[i,0]<0 if r['side']=='right' else v[i,0]>0 for i in seen),'Wrong anatomical side'
 result.append(dict(id=r['id'],status=r['status'],edges=len(edges),sourceEdges=True,singleClosedCycle=True,side=r.get('side'),anatomicalAcceptance='projection only' if r['status'].startswith('reviewed') else 'NOT admitted'))
with (run/'annotation-validation.json').open('x',encoding='utf8') as file:json.dump(result,file,ensure_ascii=False,indent=2)
print('Validated',len(result),'source-edge cycles; admitted',sum(x['status'].startswith('reviewed') for x in result))
