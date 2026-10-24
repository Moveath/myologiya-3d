"""Compare endpoint gaps without equating closest surface to attachment proof."""
import json
import pathlib
import sys
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

run = pathlib.Path(sys.argv[1])
rec = json.loads((run / 'mirror-preparation.json').read_text())
previous = pathlib.Path('research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT')
rows = json.loads((previous / 'context-arrays.json').read_text())
bones = {r['name']: trimesh.Trimesh(np.array(r['positions']).reshape(-1,3),np.array(r['indices']).reshape(-1,3),process=False) for r in rows if r['file']=='neck' and r['name'].startswith('b|') and 'hyoid' not in r['name']}
results = []
cases = [(c['id'],c['file']) for c in rec['candidates']] if rec.get('candidates') else [('admitted-right',rec['sourceFile']),('original-left-trial',rec['originalLeftTestFile']),('mirrored-left-trial',rec['file'])]
for label,path in cases:
    m=trimesh.load(path,force='mesh',process=False)
    edges=m.edges_unique
    graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(m.vertices),)*2)
    count,labels=connected_components(graph,directed=False)
    components=sorted([m.vertices[labels==i] for i in range(count)],key=lambda v:-v[:,1].max())
    result=dict(id=label,components=[])
    for i,v in enumerate(components):
        ends={}
        for end in ['upper','lower']:
            points=v[np.argsort(v[:,1])[-8:] if end=='upper' else np.argsort(v[:,1])[:8]]
            distances=[]
            for name,bone in bones.items():
                near,d,_=trimesh.proximity.closest_point_naive(bone,points)
                distances.append(dict(bone=name,minDistanceMM=float(d.min()*1000),medianDistanceMM=float(np.median(d)*1000),maxDistanceMM=float(d.max()*1000),meanEndpoint=points.mean(0).tolist(),meanClosest=near.mean(0).tolist()))
            ends[end]=sorted(distances,key=lambda d:d['medianDistanceMM'])[:2]
        result['components'].append(dict(provisionalLevel=f'C{i+2}-C{i+3}',bounds=[v.min(0).tolist(),v.max(0).tolist()],ends=ends))
    results.append(result)
with (run/'endpoint-comparison.json').open('x',encoding='utf8') as f:
    json.dump(dict(method='Eight highest/lowest Y vertices per connected component, exact nearest triangle on current unchanged neck bone meshes. Diagnostic proximity only, not confirmation of anatomical insertion or accuracy of caps.',results=results),f,indent=2)
print(json.dumps([dict(id=r['id'],levels=[dict(level=c['provisionalLevel'],upper=c['ends']['upper'][0],lower=c['ends']['lower'][0]) for c in r['components']]) for r in results]))
