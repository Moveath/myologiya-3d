"""Check that surface/projection anchors actually lie on their assigned mesh.

This detects displaced points, wrong model frames and failed ray casts. It does
not verify the anatomical name or turn a projection into observed morphology.
"""
from pathlib import Path
import base64
import io
import json
import sys
import numpy as np
import trimesh
from geometry_distance import SurfaceQuery

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root/'scripts'))
from head_localization import positions

source = root/'build_head/head_hi.glb'
if source.exists():
    scene = trimesh.load(source, force='scene')
else:
    scene = trimesh.load(io.BytesIO(base64.b64decode((root/'site/head-q-glb.txt').read_bytes())),
                         file_type='glb', force='scene')
meshes = {}
parents = scene.graph.transforms.parents
for node in scene.graph.nodes_geometry:
    label = node
    while label and not label.startswith('b|'):
        label = parents.get(label)
    if not label:
        continue
    transform, geometry = scene.graph[node]
    mesh = scene.geometry[geometry].copy()
    mesh.apply_transform(transform)
    meshes[label.split('|')[1]] = mesh

rows = positions()
results = []
for bone, mesh in meshes.items():
    entries = [(code, row) for (b, code), row in rows.items()
               if b == bone and row['localization'] != 'internal']
    if not entries:
        continue
    query = SurfaceQuery(mesh)
    # Small batches keep the memory use bounded for full-resolution bones.
    for start in range(0, len(entries), 8):
        batch = entries[start:start+8]
        closest, distances, triangles = query.closest([row['p'] for _, row in batch])
        for (code, row), distance in zip(batch, distances):
            results.append({'bone':bone,'code':code,'localization':row['localization'],
                            'distance_mm':round(float(distance), 4)})
            assert distance < .3, (bone, code, 'Anchor is not on its bone (mm)', distance)

expected = {key for key, row in rows.items() if row['localization'] != 'internal'}
checked = {(r['bone'], r['code']) for r in results}
assert checked == expected, ('Some anchors were not checked', expected - checked, checked - expected)
report = {'check':'Distance to assigned BodyParts3D mesh, tolerance 0.3 mm',
          'query_units':'millimetres, rebased in-memory copy; source and pin coordinates unchanged',
          'note':'Geometric validation only; names, projections and source independence require anatomical review.',
          'checked':len(results),'maximum_distance_mm':max(r['distance_mm'] for r in results),
          'records':results}
(root/'verify/head-position-geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Head mesh anchors passed:', len(results), 'maximum distance', report['maximum_distance_mm'], 'mm')
