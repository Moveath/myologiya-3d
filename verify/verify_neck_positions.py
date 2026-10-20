"""Check every reviewed neck anchor against source AND publication meshes.

This checks the coordinate frame and mesh distance; it does not independently
validate anatomical naming, whole-feature geometry or source independence.
"""
from pathlib import Path
import base64
import io
import json
import argparse
import sys
import numpy as np
import trimesh
from geometry_distance import SurfaceQuery

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from evidence_output import write_report
parser=argparse.ArgumentParser()
parser.add_argument('--report', help='New JSON path within an allocated evidence run')
args=parser.parse_args()
rows=json.loads((ROOT/'pins_neck/ta.json').read_text(encoding='utf8'))
assert len({(r['bone'],r['code']) for r in rows})==len(rows)

def meshes_of(scene):
    meshes={}
    parents=scene.graph.transforms.parents
    for node in scene.graph.nodes_geometry:
        label=node
        while label and not label.startswith('b|'):
            label=parents.get(label)
        if not label:
            continue
        transform,geometry=scene.graph[node]
        mesh=scene.geometry[geometry].copy()
        mesh.apply_transform(transform)
        meshes[label.split('|')[1]]=mesh
    return meshes

sources={
 'source':trimesh.load(ROOT/'build_neck/neck_hi.glb',force='scene'),
 'published_fallback':trimesh.load(io.BytesIO(base64.b64decode((ROOT/'site/neck-q-glb.txt').read_bytes())),file_type='glb',force='scene'),
}
results=[]
for name,scene in sources.items():
    meshes=meshes_of(scene)
    queries={bone:SurfaceQuery(mesh) for bone,mesh in meshes.items()}
    for row in rows:
        bone,code=row['bone'],row['code']
        assert row['localization']=='surface'
        assert len(row['refs'])>=2
        assert all(ref.get('locator') for ref in row['refs'])
        assert row['evidence'].get('uv') and row['evidence'].get('sourceSha256')
        for i, point in enumerate([row]+row.get('secondaryMarkers',[])):
            closest,distance,triangle=queries[bone].closest([point['p']])
            mm=float(distance[0])
            assert mm < .3, (name,bone,code,i,mm)
            assert abs(np.linalg.norm(point['n'])-1)<.003,(bone,code,'normal')
            results.append(dict(model=name,bone=bone,code=code,secondary=i>0,distance_mm=round(mm,5)))
report=dict(check='Assigned bone surface, source and published mesh; tolerance 0.3 mm',
            queryUnits='millimetres, rebased in-memory copy; coordinates unchanged',
            anatomicalExpertAcceptance=False,wholeFeatureGeometryVerified=False,
            primaryMarkers=len(rows),secondaryMarkers=sum(len(r.get('secondaryMarkers',[])) for r in rows),
            maximumDistanceMm=max(r['distance_mm'] for r in results),records=results)
target=write_report(report,'neck-position-geometry','neck-position-geometry.json',args.report)
print('Evidence:',target)
print('Neck anchor positions passed:',len(results),'checks; max',report['maximumDistanceMm'],'mm')
